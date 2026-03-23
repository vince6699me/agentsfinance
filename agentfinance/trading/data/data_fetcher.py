"""
AgentFinance v3 - Market Data Fetcher
======================================
Thin orchestrator delegating to specialized source modules.

Sources:
- OANDA (forex OHLCV, real-time prices)
- Polygon.io (equities, indices, crypto)
- FRED (macroeconomic data)
- CFTC COT (institutional positioning)
- TradingEconomics (comprehensive macro)
- NewsAPI (financial news)

Source modules are in trading/data/sources/:
  - oanda_client.py
  - polygon_client.py
  - fred_client.py
  - cot_client.py
  - trading_econs_client.py
  - retry_session.py (shared HTTP client)
"""

import logging
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────


class DataConfig:
    """Configuration for all data sources."""

    def __init__(
        self,
        oanda_api_key: str = "",
        oanda_account_id: str = "",
        oanda_environment: str = "practice",
        polygon_api_key: str = "",
        fred_api_key: str = "",
        trading_economics_key: str = "",
        news_api_key: str = "",
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.oanda_api_key = oanda_api_key
        self.oanda_account_id = oanda_account_id
        self.oanda_environment = oanda_environment
        self.polygon_api_key = polygon_api_key
        self.fred_api_key = fred_api_key
        self.trading_economics_key = trading_economics_key
        self.news_api_key = news_api_key
        self.request_timeout = request_timeout
        self.max_retries = max_retries


# ─────────────────────────────────────────────
# Market Data Aggregator
# ─────────────────────────────────────────────


class MarketDataAggregator:
    """
    Unified market data interface combining all sources.
    Single entry point for the trading engine.

    Clients are lazily instantiated — only created when first accessed.
    This avoids importing heavy dependencies (requests, pandas, etc.)
    until they are actually needed.
    """

    def __init__(self, config: DataConfig = None):
        if config is None:
            import os

            config = DataConfig(
                oanda_api_key=os.getenv("OANDA_API_KEY", ""),
                oanda_account_id=os.getenv("OANDA_ACCOUNT_ID", ""),
                oanda_environment=os.getenv("OANDA_ENV", "practice"),
                polygon_api_key=os.getenv("POLYGON_API_KEY", ""),
                fred_api_key=os.getenv("FRED_API_KEY", ""),
                trading_economics_key=os.getenv("TRADING_ECONOMICS_KEY", ""),
                news_api_key=os.getenv("NEWS_API_KEY", ""),
            )

        self.config = config

        # Lazy clients — instantiated on first property access
        self._oanda = None
        self._polygon = None
        self._fred = None
        self._cot = None
        self._trading_econs = None
        self._news = None

    # ── Property-based lazy clients ───────────────────────────────────────────

    @property
    def oanda(self):
        if self._oanda is None:
            if not self.config.oanda_api_key:
                logger.warning("OANDA API key not configured")
                return None
            from .sources.oanda_client import OandaClient

            self._oanda = OandaClient(
                api_key=self.config.oanda_api_key,
                account_id=self.config.oanda_account_id,
                environment=self.config.oanda_environment,
            )
        return self._oanda

    @property
    def polygon(self):
        if self._polygon is None:
            if not self.config.polygon_api_key:
                logger.warning("Polygon API key not configured")
                return None
            from .sources.polygon_client import PolygonClient

            self._polygon = PolygonClient(api_key=self.config.polygon_api_key)
        return self._polygon

    @property
    def fred(self):
        if self._fred is None:
            if not self.config.fred_api_key:
                logger.warning("FRED API key not configured")
                return None
            from .sources.fred_client import FredClient

            self._fred = FredClient(api_key=self.config.fred_api_key)
        return self._fred

    @property
    def cot(self):
        if self._cot is None:
            from .sources.cot_client import CotClient

            self._cot = CotClient()
        return self._cot

    @property
    def trading_economics(self):
        if self._trading_econs is None:
            if not self.config.trading_economics_key:
                logger.warning("TradingEconomics API key not configured")
                return None
            from .sources.trading_econs_client import TradingEconsClient

            self._trading_econs = TradingEconsClient(
                api_key=self.config.trading_economics_key
            )
        return self._trading_econs

    @property
    def news(self):
        if self._news is None:
            if not self.config.news_api_key:
                logger.warning("NewsAPI key not configured")
                return None
            from .sources.trading_econs_client import NewsClient

            self._news = NewsClient(api_key=self.config.news_api_key)
        return self._news

    # ── Convenience methods ─────────────────────────────────────────────────────

    def get_forex_data(
        self,
        symbol: str,
        timeframe: str = "H1",
        count: int = 500,
    ) -> pd.DataFrame:
        """Get OHLCV data for forex pair (via OANDA)."""
        if self.oanda is None:
            return pd.DataFrame()
        return self.oanda.fetch_ohlcv(symbol, timeframe, count)

    def get_equity_data(
        self,
        symbol: str,
        days: int = 365,
    ) -> pd.DataFrame:
        """Get daily OHLCV for equity/index (via Polygon)."""
        if self.polygon is None:
            return pd.DataFrame()
        return self.polygon.fetch_daily(symbol, days)

    def get_macro_snapshot(self) -> Dict:
        """Get comprehensive macro regime snapshot (via FRED)."""
        if self.fred is None:
            return {"error": "FRED not configured"}
        return self.fred.get_macro_snapshot()

    def get_cot_signals(self, symbols: List[str] = None) -> Dict[str, Dict]:
        """Get COT signals for specified symbols."""
        if symbols is None:
            from .sources.cot_client import CotClient

            symbols = list(CotClient.SYMBOL_MAP.keys())
        return {s: self.cot.analyze_cot_extremes(s) for s in symbols}

    def get_trading_signals(
        self,
        forex_pairs: List[str],
    ) -> List[Dict]:
        """
        Generate composite trading signals combining:
        - Current price action (OANDA)
        - COT positioning (CFTC)
        - Macro regime (FRED)
        """
        signals = []
        macro = self.get_macro_snapshot()

        for pair in forex_pairs:
            if self.oanda:
                price_data = self.oanda.get_current_prices([pair])
                price = price_data.get(pair, {})
            else:
                price = {}

            cot = self.cot.analyze_cot_extremes(pair)

            signals.append(
                {
                    "symbol": pair,
                    "bid": price.get("bid"),
                    "ask": price.get("ask"),
                    "spread_pips": price.get("spread_pips"),
                    "cot_signal": cot.get("signal", "N/A"),
                    "cot_percentile": cot.get("percentile_rank"),
                    "cot_extreme": cot.get("extreme", False),
                    "macro": {
                        "vix": macro.get("vix", {}).get("current"),
                        "dxy": macro.get("dxy", {}).get("current"),
                        "yield_curve": macro.get("2y10y_spread", {}).get("current"),
                    },
                }
            )

        return signals


# ─────────────────────────────────────────────
# Re-exports for backward compatibility
# ─────────────────────────────────────────────

from .sources.retry_session import RetrySession
from .sources.oanda_client import OandaClient
from .sources.polygon_client import PolygonClient
from .sources.fred_client import FredClient
from .sources.cot_client import CotClient
from .sources.trading_econs_client import (
    TradingEconsClient,
    NewsClient,
)

__all__ = [
    "DataConfig",
    "MarketDataAggregator",
    "RetrySession",
    "OandaClient",
    "PolygonClient",
    "FredClient",
    "CotClient",
    "TradingEconsClient",
    "NewsClient",
]


# ─────────────────────────────────────────────
# Usage Example
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agg = MarketDataAggregator()

    print("=== AgentFinance Data Fetcher ===")
    print(
        f"OANDA:  {'✓' if agg.oanda else '✗'} "
        f"(key: {'✓' if agg.config.oanda_api_key else '✗'})"
    )
    print(
        f"Polygon: {'✓' if agg.polygon else '✗'} "
        f"(key: {'✓' if agg.config.polygon_api_key else '✗'})"
    )
    print(
        f"FRED:    {'✓' if agg.fred else '✗'} "
        f"(key: {'✓' if agg.config.fred_api_key else '✗'})"
    )
    print(f"CFTC:    ✓ (public data)")
    print(
        f"T.Econ:  {'✓' if agg.trading_economics else '✗'} "
        f"(key: {'✓' if agg.config.trading_economics_key else '✗'})"
    )
    print(
        f"News:    {'✓' if agg.news else '✗'} "
        f"(key: {'✓' if agg.config.news_api_key else '✗'})"
    )

    # Example: Get COT signals
    if agg.cot:
        print("\n=== COT Signals ===")
        for sym, sig in list(
            agg.get_cot_signals(["EURUSD", "GBPUSD", "XAUUSD"]).items()
        ):
            print(
                f"  {sym}: {sig.get('signal', 'N/A')} "
                f"(pct: {sig.get('percentile_rank', 'N/A')}%)"
            )
