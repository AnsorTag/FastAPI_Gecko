import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust the import path as per your project structure
import httpx

client = TestClient(app)  # For synchronous endpoints


# Test /yo endpoint
def test_read_root():
    response = client.get("/yo")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


# Test /crypto/{crypto_name} endpoint with mocked HTTP response
@pytest.mark.asyncio
async def test_get_crypto_data(monkeypatch):
    # Define a mock response for the HTTP request
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            @staticmethod
            def json():
                return {"bitcoin": {"usd": 50000}}

            @staticmethod
            async def aread():
                return '{"bitcoin": {"usd": 50000}}'

            def raise_for_status(self):
                pass

        return MockResponse()

    # Patch the httpx.AsyncClient.get method
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    # Call the endpoint
    url = "/crypto/bitcoin"
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(url)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"crypto_name": "bitcoin", "price_usd": 50000}


# Test /crypto/{crypto_name} with an invalid crypto name
@pytest.mark.asyncio
async def test_get_crypto_data_invalid(monkeypatch):
    # Mock a response for an invalid cryptocurrency
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 404

            @staticmethod
            def json():
                return {"error": "cryptocurrency not found"}

            def raise_for_status(self):
                raise httpx.HTTPStatusError(
                    "404 Client Error: Not Found for url", request=None, response=None
                )

        return MockResponse()

    # Patch the httpx.AsyncClient.get method
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    # Call the endpoint
    url = "/crypto/unknowncrypto"
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(url)

    # Assertions
    assert response.status_code == 404
    assert response.json() == {
        "error": "Failed to fetch cryptocurrency data",
        "details": "404 Client Error: Not Found for url",
    }
