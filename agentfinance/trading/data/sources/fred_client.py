"""
FRED Macroeconomic Data Client
==============================
Fetch macroeconomic data from the Federal Reserve Economic Data (FRED) API.

Key series tracked:
- Interest rates: FEDFUNDS, DFF (effective fed funds)
- Yield curve: DGS2, DGS5, DGS10 (treasury yields)
- Inflation: CPIAUCSL, PCEPI (CPI and PCE)
- Employment: PAYEMS, UNRATE (NFP, unemployment)
- GDP: GDPPOT, GDPC1 (potential and actual GDP)
- Consumer: Retail Sales, Consumer Confidence
- Risk: VIXCLS, TEDRATE (fear indicators)
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .retry_session import RetrySession

logger = logging.getLogger(__name__)


class FredClient:
    """FRED (Federal Reserve Economic Data) API client."""

    BASE_URL = "https://api.stlouisfed.org/fred"

    # Important series IDs
    SERIES_MAP = {
        # Interest rates
        "fed_funds": "FEDFUNDS",
        "sofr": "SOFR",
        "2y_yield": "DGS2",
        "5y_yield": "DGS5",
        "10y_yield": "DGS10",
        "30y_yield": "DGS30",
        "2y10y_spread": "T10Y2Y",
        "teds_spread": "TEDRATE",
        # Inflation
        "cpi_yoy": "CPIAUCSL",
        "core_cpi": "CPILFESL",
        "pce": "PCEPI",
        "breakeven_5y": "T5YIE",
        "breakeven_10y": "T10YIE",
        # Employment
        "nfp": "PAYEMS",
        "unemployment": "UNRATE",
        "job_openings": "JTSJOL",
        "initial_claims": "ICSA",
        # GDP & Growth
        "gdp": "GDPC1",
        "gdp_potential": "GDPPOT",
        "ism_mfg": "MANEMP",
        "ism_services": "NMI",
        # Consumer
        "retail_sales": "RSXFS",
        "consumer_confidence": "CONCCONSUMEMINWOMER",
        "consumer_sentiment": "UMCSENT",
        # Risk & Market
        "vix": "VIXCLS",
        "skew": "SKEW",
        "hy_spread": "BAMLC0A0HYC",
        "move_index": "TICKREX",
        # Dollar & Credit
        "dxy": "DTBEX",
        "credit_spread_ig": "BAMLC0A0CIBM",
        "credit_spread_hy": "BAMLC0A0HYC",
        # Housing
        "housing_starts": "HOUST",
        "mortgage_rate": "MORTGAGE30US",
    }

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

    def _fetch_series(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """Generic FRED series fetcher."""
        url = f"{self.BASE_URL}/series/observations/stream/file"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": limit,
        }
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end

        response = self.session.get(url, params=params)
        data = response.json()

        if "observations" not in data:
            return pd.DataFrame()

        records = [
            {
                "date": obs["date"],
                "value": float(obs["value"]) if obs["value"] != "." else np.nan,
            }
            for obs in data["observations"]
        ]
        df = pd.DataFrame(records).set_index("date")
        df.index = pd.to_datetime(df.index)
        return df.sort_index()

    def get_indicator(self, name: str, **kwargs) -> pd.DataFrame:
        """Get indicator by name from SERIES_MAP."""
        series_id = self.SERIES_MAP.get(name)
        if not series_id:
            raise ValueError(f"Unknown FRED indicator: {name}")
        return self._fetch_series(series_id, **kwargs)

    def get_latest(self, name: str) -> Optional[Dict]:
        """Get the latest value for an indicator."""
        df = self.get_indicator(name)
        if df.empty:
            return None
        latest = df.iloc[-1]
        return {
            "indicator": name,
            "series_id": self.SERIES_MAP[name],
            "date": latest.name.strftime("%Y-%m-%d"),
            "value": latest["value"],
        }

    def get_macro_snapshot(self) -> Dict:
        """Get snapshot of all key macro indicators for regime analysis."""
        snapshot = {}

        # Critical indicators for macro regime
        critical = [
            "fed_funds",
            "vix",
            "2y10y_spread",
            "unemployment",
            "cpi_yoy",
            "consumer_sentiment",
            "10y_yield",
            "gdp",
        ]

        for name in critical:
            try:
                df = self.get_indicator(name)
                if not df.empty:
                    snapshot[name] = {
                        "current": df.iloc[-1]["value"],
                        "previous": df.iloc[-2]["value"] if len(df) > 1 else None,
                        "date": df.index[-1].strftime("%Y-%m-%d"),
                    }
            except Exception as e:
                logger.warning(f"FRED {name} failed: {e}")
                snapshot[name] = {"current": None, "error": str(e)}

        return snapshot

    def get_yield_curve(self) -> pd.DataFrame:
        """Get current yield curve (2Y, 5Y, 10Y, 30Y)."""
        yields = {}
        for tenor in ["2y_yield", "5y_yield", "10y_yield", "30y_yield"]:
            df = self.get_indicator(tenor)
            if not df.empty:
                yields[tenor.replace("_yield", "")] = df.iloc[-1]["value"]

        return pd.DataFrame([yields]).T.rename(columns={0: "yield_pct"})

    def get_inflation_break_evens(self) -> Dict:
        """Get 5Y and 10Y breakeven inflation rates."""
        return {
            "breakeven_5y": self.get_latest("breakeven_5y"),
            "breakeven_10y": self.get_latest("breakeven_10y"),
        }

    # ── Calendar ───────────────────────────────────────────────────────────────

    def get_economic_calendar(
        self,
        days_ahead: int = 7,
    ) -> List[Dict]:
        """
        Parse FRED economic release calendar.
        Note: FRED doesn't have a dedicated calendar API.
        For production, use Forex Factory or tradingeconomics.com.
        """
        calendar = []
        today = datetime.now().date()

        # Common high-impact events with typical release dates
        # In production, replace with actual calendar API calls
        for i in range(days_ahead):
            date = today + timedelta(days=i)
            dow = date.weekday()

            # US high-impact releases by day of week
            if dow == 1:  # Tuesday
                calendar.append(
                    {
                        "date": date,
                        "event": "US Retail Sales",
                        "impact": "HIGH",
                        "typical_time": "08:30 EST",
                    }
                )
            elif dow == 2:  # Wednesday
                calendar.append(
                    {
                        "date": date,
                        "event": "US CPI",
                        "impact": "HIGH",
                        "typical_time": "08:30 EST",
                    }
                )
            elif dow == 3:  # Thursday
                calendar.append(
                    {
                        "date": date,
                        "event": "US Jobless Claims",
                        "impact": "MEDIUM",
                        "typical_time": "08:30 EST",
                    }
                )
            elif dow == 4:  # Friday
                calendar.append(
                    {
                        "date": date,
                        "event": "US NFP",
                        "impact": "HIGH",
                        "typical_time": "08:30 EST",
                    }
                )

        return calendar
