"""
Polygon.io Equity & Crypto Data Client
=======================================
Fetch US equities, indices, and crypto OHLCV data from Polygon.io REST API.

Coverage:
- US equities (AAPL, MSFT, etc.)
- Indices (SPY, QQQ, DIA)
- Forex (when available)
- Crypto (BTC/USD)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd

from .retry_session import RetrySession

logger = logging.getLogger(__name__)


class PolygonClient:
    """Polygon.io REST API client for equities and crypto data."""

    BASE_URL = "https://api.polygon.io/v2"

    def __init__(
        self,
        api_key: str,
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.session = RetrySession(
            request_timeout=request_timeout, max_retries=max_retries
        )
        self.headers = {"Authorization": f"Bearer {api_key}"}

    # ── OHLCV ──────────────────────────────────────────────────────────────────

    def fetch_ohlcv(
        self,
        symbol: str,
        timespan: str = "hour",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 5000,
    ) -> pd.DataFrame:
        """
        Fetch aggregated OHLCV bars from Polygon.

        Args:
            symbol: Ticker symbol (e.g., "AAPL", "SPY", "BTCUSD")
            timespan: second, minute, hour, day, week, month, quarter, year
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Max results (up to 50000)
        """
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if to_date is None:
            to_date = datetime.now().strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/aggs/ticker/{symbol}/range/1/{timespan}/{from_date}/{to_date}"
        params = {"adjusted": "true", "sort": "asc", "limit": limit}

        response = self.session.get(url, headers=self.headers, params=params)
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return pd.DataFrame()

        records = []
        for bar in data["results"]:
            records.append(
                {
                    "time": pd.to_datetime(bar["t"], unit="ms"),
                    "open": bar["o"],
                    "high": bar["h"],
                    "low": bar["l"],
                    "close": bar["c"],
                    "volume": bar["v"],
                    "vwap": bar.get("vwap", bar["c"]),
                }
            )

        return pd.DataFrame(records).set_index("time").sort_index()

    def fetch_daily(
        self,
        symbol: str,
        days: int = 365,
    ) -> pd.DataFrame:
        """Fetch daily OHLCV for the last N days."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.fetch_ohlcv(symbol, "day", from_date, to_date)

    # ── Ticker Details ─────────────────────────────────────────────────────────

    def get_ticker_details(self, symbol: str) -> Dict:
        """Get ticker metadata."""
        url = f"{self.BASE_URL}/reference/ticker/{symbol}"
        response = self.session.get(
            url, headers=self.headers, params={"type": "stocks"}
        )
        return response.json().get("results", {})

    def get_daily_open_close(self, symbol: str, date: Optional[str] = None) -> Dict:
        """Get daily open/close for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/aggs/ticker/{symbol}/prev"
        response = self.session.get(url, headers=self.headers)
        return response.json().get("results", {})

    # ── Market Status ──────────────────────────────────────────────────────────

    def get_market_status(self) -> Dict:
        """Check if US markets are open/closed."""
        url = f"{self.BASE_URL}/marketcd/usa/now"
        response = self.session.get(url, headers=self.headers)
        return response.json()

    # ── Snapshot ────────────────────────────────────────────────────────────────

    def get_snapshot(self, symbol: str) -> Dict:
        """Get real-time snapshot for a ticker."""
        url = f"{self.BASE_URL}/snapshot/locale/us/markets/stocks/tickers/{symbol}"
        response = self.session.get(url, headers=self.headers)
        return response.json()
