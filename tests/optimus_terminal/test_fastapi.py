from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from optimus_terminal.fast_api.main import app  # Import your FastAPI app

client = TestClient(app)


def test_stock_news_polygon():
    payload = {"symbol": "AAPL", "order": "asc", "limit": "5"}

    response = client.post("/stock-news-polygon", json=payload)
    response_data = response.json()

    assert response.status_code == 200
    assert "results" in response_data
    assert isinstance(response_data["results"], list)

    if response_data["results"]:  # If there are results
        first_result = response_data["results"][0]
        assert "id" in first_result
        assert "publisher" in first_result
        assert "title" in first_result


def test_stock_price_api():
    with patch("optimus_terminal.fast_api.main.requests.get") as mock_requests_get:
        mock_requests_get.return_value.status_code = 200
        response = client.get("/stock-price/aapl?period=1d")
        response_data = response.json()

        assert response.status_code == 200

        assert "symbol" in response_data
        assert "entries" in response_data

        assert isinstance(response_data["symbol"], str)
        assert isinstance(response_data["entries"], list)

        for entry in response_data["entries"]:
            assert set(entry.keys()) == {
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            }
            assert isinstance(entry["date"], str)
            assert isinstance(entry["open"], (int, float))
            assert isinstance(entry["high"], (int, float))
            assert isinstance(entry["low"], (int, float))
            assert isinstance(entry["close"], (int, float))
            assert isinstance(entry["volume"], int)


def test_watchList_api():
    with patch("optimus_terminal.fast_api.main.requests.get") as mock_requests_get:
        mock_requests_get.return_value.status_code = 200
        response = client.get("/watchlist")

        assert response.status_code == 200
        response_data = response.json()

        for entry in response_data:
            assert set(entry.keys()) == {
                "ticker",
                "last",
                "change",
                "changePer",
                "volume",
                "avgVolume",
                "marketCapacity",
            }

            assert isinstance(entry["ticker"], str)
            assert isinstance(entry["last"], (int, float))
            assert entry["last"] > 0

            assert isinstance(entry["change"], (int, float))
            assert isinstance(entry["changePer"], (int, float))

            assert isinstance(entry["volume"], (int, float))
            assert entry["volume"] >= 0

            assert isinstance(entry["avgVolume"], (int, float))
            assert entry["avgVolume"] >= 0

            assert isinstance(entry["marketCapacity"], (int, float))
            assert entry["marketCapacity"] > 0
