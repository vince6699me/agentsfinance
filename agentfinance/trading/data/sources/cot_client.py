"""
CFTC Commitment of Traders (COT) Data Client
==============================================
Fetch CFTC Commitment of Traders reports.

Weekly report released every Friday at 15:30 EST.
Covers futures positioning by:
- Commercial hedgers (smart money)
- Large speculators (large funds)
- Small speculators (retail)
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from scipy.stats import percentileofscore

from .retry_session import RetrySession

logger = logging.getLogger(__name__)


class CotClient:
    """CFTC Commitment of Traders report client."""

    COT_URL = "https://www.cftc.gov/dea/futures/deahistfo.txt"

    # Currency futures codes for COT
    SYMBOL_MAP = {
        # FX futures
        "EURUSD": "099741",  # Euro FX
        "GBPUSD": "096742",  # British Pound
        "JPYUSD": "097741",  # Japanese Yen
        "AUDUSD": "232741",  # Australian Dollar
        "CADUSD": "090741",  # Canadian Dollar
        "CHFUSD": "092741",  # Swiss Franc
        "NZDUSD": "112741",  # New Zealand Dollar
        # Metals
        "XAUUSD": "088691",  # Gold
        "XAGUSD": "084691",  # Silver
        # Indices
        "SPX": "13874+",  # S&P 500
        "NDX": "20974+",  # Nasdaq-100
        # Energy
        "WTI": "067651",  # Crude Oil
        "NATGAS": "023651",  # Natural Gas
    }

    def __init__(
        self,
        request_timeout: int = 60,
        max_retries: int = 3,
    ):
        self.session = RetrySession(
            request_timeout=request_timeout, max_retries=max_retries
        )
        self._cache: Dict[str, pd.DataFrame] = {}

    def fetch_cot_report(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch and parse the CFTC COT legacy report.
        Returns DataFrame with commercial and speculative positioning.

        If symbol is None, fetches all currency/metals reports.
        """
        cache_key = symbol or "all"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            response = self.session.get(self.COT_URL)
            response.encoding = "utf-8"
            text = response.text
            df = self._parse_cot_text(text)
            self._cache[cache_key] = df
            return df
        except Exception as e:
            logger.error(f"COT fetch failed: {e}")
            return pd.DataFrame()

    def _parse_cot_text(self, text: str) -> pd.DataFrame:
        """Parse the COT legacy report text file."""
        lines = text.strip().split("\n")
        records = []
        current_code = None
        current_name = None

        for line in lines:
            if line.startswith("#") or not line.strip():
                continue

            if line.startswith("001"):
                parts = line.split()
                if len(parts) >= 3:
                    current_code = parts[1]
                    current_name = " ".join(parts[2:])
                continue

            if len(line) > 100 and current_code:
                try:
                    date = line[9:17].strip()
                    if not date:
                        continue
                    cols = line.split()
                    if len(cols) < 20:
                        continue
                    record = {
                        "date": self._parse_date(date),
                        "code": current_code,
                        "name": current_name,
                    }
                    try:
                        record["commercial_long"] = (
                            int(cols[-12]) if len(cols) > 12 else 0
                        )
                        record["commercial_short"] = (
                            int(cols[-11]) if len(cols) > 11 else 0
                        )
                        record["large_spec_long"] = (
                            int(cols[-10]) if len(cols) > 10 else 0
                        )
                        record["large_spec_short"] = (
                            int(cols[-9]) if len(cols) > 9 else 0
                        )
                        record["small_spec_long"] = (
                            int(cols[-8]) if len(cols) > 8 else 0
                        )
                        record["small_spec_short"] = (
                            int(cols[-7]) if len(cols) > 7 else 0
                        )
                    except (ValueError, IndexError):
                        pass
                    if "commercial_long" in record:
                        records.append(record)
                except Exception:
                    continue

        df = pd.DataFrame(records)
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
            df = df.dropna(subset=["date"]).sort_values("date")
        return df

    def _parse_date(self, date_str: str) -> str:
        """Parse COT date format."""
        try:
            return datetime.strptime(date_str.strip(), "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return ""

    def get_symbol_cot(self, symbol: str) -> pd.DataFrame:
        """Get COT data for a specific symbol."""
        df = self.fetch_cot_report(symbol)
        if df.empty:
            return df
        code = self.SYMBOL_MAP.get(symbol)
        if code:
            df = df[df["code"] == code]
        return df

    def analyze_cot_extremes(
        self,
        symbol: str,
        lookback_weeks: int = 52,
    ) -> Dict:
        """
        Analyze COT positioning for extremes.
        Returns percentile rank and directional signal.
        """
        df = self.get_symbol_cot(symbol)
        if df.empty:
            return {"error": "No COT data available", "signal": "UNKNOWN"}

        df = df.tail(lookback_weeks)
        if len(df) < 4:
            return {"error": "Insufficient data", "signal": "UNKNOWN"}

        df = df.copy()
        df["net_commercial"] = df["commercial_long"] - df["commercial_short"]
        df["net_large_spec"] = df["large_spec_long"] - df["large_spec_short"]

        latest = df.iloc[-1]
        net_comm = latest["net_commercial"]
        net_large = latest["net_large_spec"]

        pct = percentileofscore(df["net_commercial"].dropna(), net_comm)

        if pct >= 80:
            signal = "BULLISH"
        elif pct <= 20:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        return {
            "symbol": symbol,
            "date": latest["date"].strftime("%Y-%m-%d")
            if pd.notna(latest["date"])
            else "N/A",
            "commercial_long": int(latest["commercial_long"]),
            "commercial_short": int(latest["commercial_short"]),
            "net_commercial": int(net_comm),
            "large_spec_net": int(net_large),
            "percentile_rank": round(pct, 1),
            "signal": signal,
            "extreme": pct >= 90 or pct <= 10,
            "net_commercial_pct": round(
                net_comm
                / (latest["commercial_long"] + latest["commercial_short"] + 1)
                * 100,
                1,
            ),
        }

    def get_all_cot_signals(self) -> Dict[str, Dict]:
        """Get COT signals for all tracked symbols."""
        signals = {}
        for symbol in self.SYMBOL_MAP.keys():
            try:
                signals[symbol] = self.analyze_cot_extremes(symbol)
            except Exception as e:
                signals[symbol] = {"error": str(e), "signal": "ERROR"}
        return signals
