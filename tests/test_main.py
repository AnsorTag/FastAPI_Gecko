import pytest
import httpx
from httpx import ASGITransport
from app.main import app


@pytest.mark.asyncio(loop_scope="function")
async def test_get_crypto_data(monkeypatch):
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            @staticmethod
            def json():
                return {"crypto_name": "bitcoin", "price_usd": 50000}

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    url = "/crypto/bitcoin"
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(url)

    assert response.status_code == 200
    assert response.json() == {"crypto_name": "bitcoin", "price_usd": 50000}


@pytest.mark.asyncio(loop_scope="function")
async def test_get_crypto_data_invalid(monkeypatch):
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 404

            @staticmethod
            def json():
                return {
                    "error": "Failed to fetch cryptocurrency data",
                    "details": "404 Client Error: Not Found for url",
                }

            def raise_for_status(self):
                raise httpx.HTTPStatusError(
                    "404 Client Error: Not Found for url", request=None, response=None
                )

        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    url = "/crypto/unknowncrypto"
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        response = await async_client.get(url)

    assert response.status_code == 404
    assert response.json() == {
        "error": "Failed to fetch cryptocurrency data",
        "details": "404 Client Error: Not Found for url",
    }
