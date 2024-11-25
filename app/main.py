from fastapi import FastAPI
import dotenv
import logging
import os

app = FastAPI()

# Load environment variables from .env file
dotenv.load_dotenv()

# Access the variables
api_key = os.getenv("API_KEY")
debug_mode = os.getenv("DEBUG_MODE")

print(f"API Key: {api_key}")
print(f"Debug Mode: {debug_mode}")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/crypto/{crypto_name}")
async def gecko():
    headers = {"Authorization": f"Bearer {api_key}"}


app = app
