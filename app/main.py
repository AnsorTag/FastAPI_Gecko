from fastapi import FastAPI
import dotenv
import logging
import os
import httpx

app = FastAPI()

# Load .env file
dotenv.load_dotenv()

# .env variables
api_key = os.getenv("API_KEY")
debug_mode = os.getenv("DEBUG_MODE")

print(f"API Key: {api_key}")
print(f"Debug Mode: {debug_mode}")


@app.get("/yo")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/crypto/{crypto_name}")
async def get_crypto_data(crypto_name: str):
    # gecko url
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_name}&vs_currencies=usd"

    # headers just in case
    headers = {
        "Authorization": f"Bearer {api_key}"  # Only if the API requires an API key in headers
    }

    try:
        # get request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        # raise exception
        response.raise_for_status()

        # Parse the JSON
        data = response.json()

        # Extract data
        return {
            "crypto_name": crypto_name,
            "price_usd": data.get(crypto_name, {}).get("usd", "N/A"),
        }

    except httpx.HTTPStatusError as e:
        # HTTP errors
        logging.error(f"HTTP error: {e}")
        return {"error": "Failed to fetch cryptocurrency data", "details": str(e)}
    except Exception as e:
        # other errors
        logging.error(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred", "details": str(e)}


app = app
