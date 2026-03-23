"""
OANDA Forex Data Client
=======================
Fetch forex OHLCV data, real-time prices, account info, and order books
from the OANDA v20 REST API.

Supported instruments:
- Majors: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- Minors: EURGBP, EURJPY, GBPJPY, AUDJPY, CADJPY, NZDJPY, etc.
- Metals: XAUUSD, XAGUSD
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from .retry_session import RetrySession

logger = logging.getLogger(__name__)


class OandaClient:
    """OANDA v20 REST API client for forex data."""

    BASE_URLS = {
        "practice": "https://api-fxpractice.oanda.com",
        "live": "https://api-fxtrade.oanda.com",
    }

    TIMEFRAME_MAP = {
        "M5": "M5",
        "M15": "M15",
        "M30": "M30",
        "H1": "H1",
        "H4": "H4",
        "D": "D",
        "W": "W",
    }

    def __init__(
        self,
        api_key: str,
        account_id: str,
        environment: str = "practice",
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        self.session = RetrySession(
            request_timeout=request_timeout, max_retries=max_retries
        )
        self.base_url = self.BASE_URLS.get(environment, self.BASE_URLS["practice"])
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    # ── OHLCV Data ──────────────────────────────────────────────────────────────

    def fetch_ohlcv(
        self,
        instrument: str,
        timeframe: str = "H1",
        count: int = 500,
        since: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candles for a forex pair.

        Args:
            instrument: e.g. "EUR_USD" or "EURUSD"
            timeframe: M5, M15, M30, H1, H4, D, W
            count: Number of candles (max 5000 per request)
            since: Return candles since this datetime (UTC)
        """
        # Normalize instrument name
        if "_" not in instrument and "USD" in instrument:
            inst = instrument.replace("USD", "_USD")
        else:
            inst = instrument

        tf = self.TIMEFRAME_MAP.get(timeframe, "H1")
        params = {"granularity": tf, "count": min(count, 5000)}
        if since:
            params["from"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f"{self.base_url}/v3/instruments/{inst}/candles"
        response = self.session.get(url, headers=self.headers, params=params)
        data = response.json()

        if "candles" not in data or not data["candles"]:
            logger.warning(f"No OHLCV data returned for {instrument}")
            return pd.DataFrame()

        records = []
        for c in data["candles"]:
            rec = {
                "time": pd.to_datetime(c["time"]),
                "open": float(c["mid"]["o"]),
                "high": float(c["mid"]["h"]),
                "low": float(c["mid"]["l"]),
                "close": float(c["mid"]["c"]),
                "volume": int(c.get("volume", 0)),
            }
            records.append(rec)

        return pd.DataFrame(records).set_index("time").sort_index()

    def fetch_latest(
        self,
        instrument: str,
        timeframe: str = "H1",
    ) -> Optional[Dict]:
        """Get the most recent candle."""
        df = self.fetch_ohlcv(instrument, timeframe, count=1)
        if df.empty:
            return None
        return df.iloc[-1].to_dict()

    def fetch_multi_timeframe(
        self,
        instrument: str,
        timeframes: Optional[List[str]] = None,
        count: int = 200,
    ) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV across multiple timeframes efficiently."""
        if timeframes is None:
            timeframes = ["M15", "H1", "H4", "D"]

        results = {}
        for tf in timeframes:
            try:
                results[tf] = self.fetch_ohlcv(instrument, tf, count=count)
            except Exception as e:
                logger.error(f"Failed to fetch {instrument} {tf}: {e}")
                results[tf] = pd.DataFrame()

        return results

    # ── Pricing ─────────────────────────────────────────────────────────────────

    def get_current_prices(self, instruments: List[str]) -> Dict[str, Dict]:
        """Get real-time bid/ask for multiple instruments."""
        inst_list = [i.replace("_", "_") if "_" in i else i for i in instruments]
        params = {"instruments": ",".join(inst_list)}

        url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
        response = self.session.get(url, headers=self.headers, params=params)
        data = response.json()

        prices = {}
        for p in data.get("prices", []):
            inst = p["instrument"].replace("_", "")
            prices[inst] = {
                "bid": float(p["bids"][0]["price"]),
                "ask": float(p["asks"][0]["price"]),
                "mid": (float(p["bids"][0]["price"]) + float(p["asks"][0]["price"]))
                / 2,
                "spread_pips": self._calculate_spread(p),
                "tradeable": p.get("tradeable", False),
                "time": p["time"],
            }
        return prices

    def _calculate_spread(self, price_data: Dict) -> float:
        """Calculate spread in pips for forex pairs."""
        bid = float(price_data["bids"][0]["price"])
        ask = float(price_data["asks"][0]["price"])
        spread = ask - bid

        # Convert to pips (4th decimal for most pairs, 2nd for JPY pairs)
        instrument = price_data["instrument"]
        if "JPY" in instrument:
            return round(spread * 100, 1)
        return round(spread * 10000, 1)

    # ── Account ─────────────────────────────────────────────────────────────────

    def get_account_summary(self) -> Dict:
        """Get OANDA account summary."""
        url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
        response = self.session.get(url, headers=self.headers)
        data = response.json()["account"]

        return {
            "balance": float(data["balance"]),
            "nav": float(data["NAV"]),
            "unrealized_pl": float(data["unrealizedPL"]),
            "margin_used": float(data["marginUsed"]),
            "margin_available": float(data["marginAvailable"]),
            "open_trade_count": int(data["openTradeCount"]),
            "open_position_count": int(data["openPositionCount"]),
            "pending_order_count": int(data["pendingOrderCount"]),
            "pl": float(data["pl"]),
            "currency": data["currency"],
        }

    # ── Order Book ─────────────────────────────────────────────────────────────

    def get_order_book(self, instrument: str) -> Dict:
        """Get OANDA order book for liquidity analysis."""
        inst = instrument.replace("_", "_") if "_" in instrument else instrument
        url = f"{self.base_url}/v3/instruments/{inst}/orderBook"
        response = self.session.get(url, headers=self.headers)
        return response.json()

    # ── Positioning ──────────────────────────────────────────────────────────────

    def get_position_book(self, instrument: str) -> Dict:
        """Get retail positioning data (SSI-style)."""
        inst = instrument.replace("_", "_") if "_" in instrument else instrument
        url = f"{self.base_url}/v3/instruments/{inst}/positionBook"
        response = self.session.get(url, headers=self.headers)
        return response.json()
