from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import dotenv
import time
import logging
import os
import httpx
from sqlalchemy.orm import Session
from app.databases.db import SessionLocal
import app.crud as crud
from app.models.model import Transaction
from app.schemas.schemas import TransactionCreate, TransactionResponse
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize the app
app = FastAPI()

# init security
security = HTTPBasic()


# Custom Middleware for Request Logging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        logging.info(f"Incoming request: {request.method} {request.url}")
        logging.debug(f"Headers: {dict(request.headers)}")

        # Measure request processing time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response details
        logging.info(
            f"Completed response: {response.status_code} in {process_time:.2f}s"
        )
        return response


# Add middleware to the app
app.add_middleware(RequestLoggingMiddleware)

# Load .env file
dotenv.load_dotenv()

# .env variables
api_key = os.getenv("API_KEY")
debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
correct_username = os.getenv("TEST_USERNAME")
correct_password = os.getenv("TEST_PASSWORD")

# Log API key and Debug Mode
logging.debug(f"API Key: {api_key}")
logging.debug(f"Debug Mode: {debug_mode}")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Security
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    if (
        credentials.username != correct_username
        or credentials.password != correct_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Pydantic Schema
class CryptoPriceResponse(BaseModel):
    crypto_name: str
    price_usd: Optional[float] = None


# Endpoints
@app.get("/crypto/{crypto_name}", response_model=CryptoPriceResponse)
async def get_crypto_data(crypto_name: str, db: Session = Depends(get_db)):
    logging.info(f"Fetching data for cryptocurrency: {crypto_name}")

    # gecko url
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_name}&vs_currencies=usd"

    # headers = {"Authorization": f"Bearer {api_key}"}

    try:
        # Make the API request
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        # Raise exception if request failed
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()
        logging.debug(f"Response data: {data}")

        # Extract price
        price_usd = data.get(crypto_name, {}).get("usd", None)

        # Save the transaction to the database (optional example)
        if price_usd is not None:
            crud.create_transaction(db, crypto_name, 1.0, price_usd)

        return {"crypto_name": crypto_name, "price_usd": price_usd}

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error while fetching data for {crypto_name}: {e}")
        raise HTTPException(status_code=response.status_code, detail=str(e))

    except Exception as e:
        logging.error(f"Unexpected error while fetching data for {crypto_name}: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@app.get("/transactions/", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, skip, limit)
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction_by_id(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = crud.create_transaction(
        db, transaction.crypto_name, transaction.amount, transaction.price_usd
    )
    return db_transaction


@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    updated_transaction = crud.update_transaction(
        db,
        transaction_id,
        transaction.crypto_name,
        transaction.amount,
        transaction.price_usd,
    )
    if updated_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.delete_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": f"Transaction with ID {transaction_id} deleted successfully"}


@app.get("/protected")
def read_protected(username: str = Depends(get_current_username)):
    return {"message": "This is a protected route", "username": username}
