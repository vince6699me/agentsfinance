"""
AgentFinance v5 - Sector Scanner

Per-sector scanning logic for all 5 market sectors.
Each sector has dedicated scanning methods and instruments.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional

from app.core.logging import get_logger
from app.scanner.models import (
    Sector,
    OpportunityType,
    ConfidenceScore,
    Opportunity,
    SectorScanResult,
    ScannerConfig,
)


logger = get_logger(__name__)


# Instrument definitions per sector
SECTOR_INSTRUMENTS: dict[Sector, list[str]] = {
    Sector.FOREX: [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "USDCAD", "NZDUSD",
        "EURGBP", "EURJPY", "GBPJPY",
        "EURCHF", "EURAUD", "EURNZD",
        "GBPAUD", "GBPCAD", "GBPNZD",
        "AUDJPY", "CADJPY", "NZDJPY",
        "AUDCAD", "AUDCHF", "AUDNZD",
        "CADCHF", "USDSGD", "USDHKD",
        "USDZAR", "USDMXN", "USDNOK", "USDSEK",
    ],
    Sector.COMMODITIES: [
        "XAUUSD",  # Gold
        "XTIUSD",  # Oil/Black Gold
    ],
    Sector.STOCKS: [
        # Top US equities - sample of 30 for initial implementation
        "SPY", "QQQ", "IWM",  # ETFs
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA",  # Top Tech
        "TSLA", "AMD", "INTC", "NFLX", "PYPL",
        "JPM", "BAC", "WFC", "GS", "MS",
        "JNJ", "PFE", "UNH", "ABBV", "MRK",
        "XOM", "CVX", "COP",
        "WMT", "COST", "HD", "DIS", "NKE",
    ],
    Sector.INDICES: [
        "US500",   # SP500
        "US100",   # NAS100
        "DE40",    # DAX
        "UK100",   # FTSE
        "JP225",   # Nikkei
    ],
    Sector.CRYPTO: [
        "BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD",
        "XRPUSD", "ADAUSD", "DOGEUSD", "DOTUSD",
        "MATICUSD", "AVAXUSD", "LINKUSD", "ATOMUSD",
        "UNIUSD", "LTCUSD", "ETCUSD", "XLMUSD",
        "ALGOUSD", "VETUSD", "ICPUSD", "FILUSD",
        "AAVEUSD", "GRTUSD", "SANDUSD", "MANAUSD",
        "AXSUSD", "THETAUSD", "ENJUSD", "GALAUSD",
        "CHZUSD", "BATUSD",
    ],
}


class SectorScanner:
    """
    Per-sector scanning logic.

    Responsible for scanning individual market sectors and identifying
    trading opportunities based on technical analysis and structure.
    """

    def __init__(self, config: Optional[ScannerConfig] = None):
        """
        Initialize sector scanner.

        Args:
            config: Scanner configuration
        """
        self.config = config or ScannerConfig()
        self._sector_cache: dict[Sector, list[Opportunity]] = {}
        self._last_scan: dict[Sector, datetime] = {}

    async def scan_sector(self, sector: Sector) -> SectorScanResult:
        """
        Scan a single sector for opportunities.

        Args:
            sector: Sector to scan

        Returns:
            SectorScanResult with ranked opportunities
        """
        start_time = time.perf_counter()
        logger.info(f"Starting scan for sector: {sector.value}")

        try:
            # Get instruments for sector
            instruments = SECTOR_INSTRUMENTS.get(sector, [])

            # Scan each instrument concurrently
            tasks = [self._scan_instrument(sector, symbol) for symbol in instruments]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter valid opportunities and sort by confidence
            opportunities = [
                r for r in results
                if isinstance(r, Opportunity) and r.confidence.overall >= self.config.min_confidence
            ]

            # Sort by confidence (highest first)
            opportunities.sort(
                key=lambda x: x.confidence.overall, reverse=True
            )

            # Limit to max opportunities per sector
            opportunities = opportunities[: self.config.max_opportunities_per_sector]

            scan_duration = (time.perf_counter() - start_time) * 1000

            result = SectorScanResult(
                sector=sector,
                opportunities=opportunities,
                total_instruments=len(instruments),
                scan_duration_ms=scan_duration,
                timestamp=datetime.utcnow(),
                metadata=self._get_sector_metadata(sector, opportunities),
            )

            # Update cache
            self._sector_cache[sector] = opportunities
            self._last_scan[sector] = datetime.utcnow()

            logger.info(
                f"Scan complete for {sector.value}: "
                f"{len(opportunities)} opportunities in {scan_duration:.1f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Error scanning sector {sector.value}: {e}")
            return SectorScanResult(
                sector=sector,
                opportunities=[],
                total_instruments=len(SECTOR_INSTRUMENTS.get(sector, [])),
                scan_duration_ms=(time.perf_counter() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)},
            )

    async def _scan_instrument(
        self, sector: Sector, symbol: str
    ) -> Opportunity | None:
        """
        Scan a single instrument for opportunities.

        This is a simplified implementation. In production, this would
        connect to actual market data and run full technical analysis.

        Args:
            sector: Market sector
            symbol: Trading symbol

        Returns:
            Opportunity if found, None otherwise
        """
        try:
            # Simulate market data fetching and analysis
            # In production: fetch OHLCV, run technical indicators, check kill zones
            await asyncio.sleep(0.01)  # Simulate async I/O

            # Generate demo opportunity based on symbol hash for consistency
            # This ensures same symbol always produces similar confidence
            base_confidence = 50 + (hash(symbol) % 40)
            entry_price = self._get_demo_price(symbol)
            spread = self._get_demo_spread(sector)

            # Only return opportunity if confidence meets threshold
            if base_confidence < self.config.min_confidence:
                return None

            # Determine opportunity type based on sector
            opp_type = self._get_opportunity_type(symbol, sector)

            # Calculate entry, SL, TP based on direction
            direction = "buy" if base_confidence > 70 else "sell"
            pip_value = 0.0001 if sector != Sector.COMMODITIES or symbol == "XAUUSD" else 1.0

            if direction == "buy":
                entry = entry_price + spread
                sl = entry - (30 * pip_value)
                tp = entry + (70 * pip_value)
            else:
                entry = entry_price - spread
                sl = entry + (30 * pip_value)
                tp = entry - (70 * pip_value)

            # Calculate R:R
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            rr = reward / risk if risk > 0 else 0

            confidence = ConfidenceScore(
                overall=base_confidence,
                confluence=min(100, base_confidence + 5),
                momentum=min(100, base_confidence - 10),
                structure=min(100, base_confidence + 8),
                regime=min(100, base_confidence - 5),
            )

            return Opportunity(
                symbol=symbol,
                sector=sector,
                direction=direction,
                entry_price=round(entry, 5),
                stop_loss=round(sl, 5),
                take_profit=round(tp, 5),
                risk_reward=round(rr, 2),
                opportunity_type=opp_type,
                confidence=confidence,
                key_levels=self._get_key_levels(symbol, direction, entry),
                indicators=self._get_demo_indicators(symbol),
                timestamp=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(minutes=30),
            )

        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return None

    def _get_demo_price(self, symbol: str) -> float:
        """Get demo price for symbol."""
        prices = {
            "EURUSD": 1.0850, "GBPUSD": 1.2650, "USDJPY": 157.50,
            "USDCHF": 0.9020, "AUDUSD": 0.6520, "USDCAD": 1.3650,
            "NZDUSD": 0.6020,
            "EURGBP": 0.8580, "EURJPY": 170.80, "GBPJPY": 199.20,
            "EURCHF": 0.9790, "EURAUD": 1.6620, "EURNZD": 1.7820,
            "GBPAUD": 1.9380, "GBPCAD": 1.7260, "GBPNZD": 2.0780,
            "AUDJPY": 102.70, "CADJPY": 115.40, "NZDJPY": 94.80,
            "AUDCAD": 0.8890, "AUDCHF": 0.5880, "AUDNZD": 1.0830,
            "CADCHF": 0.6610, "USDSGD": 1.3450, "USDHKD": 7.8120,
            "USDZAR": 18.50, "USDMXN": 17.20, "USDNOK": 11.00,
            "USDSEK": 10.80,
            "XAUUSD": 2345.50, "XTIUSD": 83.20,
            "BTCUSD": 67450.00, "ETHUSD": 3450.00,
        }
        return prices.get(symbol, 100.0)

    def _get_demo_spread(self, sector: Sector) -> float:
        """Get typical spread for sector."""
        spreads = {
            Sector.FOREX: 0.00015,  # 1.5 pips
            Sector.COMMODITIES: 0.50 if sector == "XAUUSD" else 0.05,
            Sector.STOCKS: 0.01,
            Sector.INDICES: 0.50,
            Sector.CRYPTO: 0.50,
        }
        return spreads.get(sector, 0.01)

    def _get_opportunity_type(self, symbol: str, sector: Sector) -> OpportunityType:
        """Determine opportunity type based on symbol."""
        # Simplified classification based on hash for consistency
        h = hash(symbol)
        types = [
            OpportunityType.FVG,
            OpportunityType.BREAKOUT,
            OpportunityType.ORDER_BLOCK,
            OpportunityType.KILL_ZONE,
            OpportunityType.TREND_CONTINUATION,
        ]
        return types[h % len(types)]

    def _get_key_levels(self, symbol: str, direction: str, entry: float) -> dict:
        """Get key price levels for opportunity."""
        levels = {
            "entry": round(entry, 5),
            "resistance": round(entry * 1.005, 5) if direction == "buy" else round(entry * 0.995, 5),
            "support": round(entry * 0.995, 5) if direction == "buy" else round(entry * 1.005, 5),
        }
        return levels

    def _get_demo_indicators(self, symbol: str) -> dict:
        """Get demo technical indicators."""
        base = 50 + (hash(symbol) % 40)
        return {
            "rsi": round(min(100, base + 10), 1),
            "macd_signal": round(base * 0.001, 5),
            "adx": round(min(50, base - 20), 1),
            "ema_20": round(50 + (hash(symbol + "ema") % 10), 2),
            "ema_50": round(50 + (hash(symbol + "ema") % 10), 2),
        }

    def _get_sector_metadata(
        self, sector: Sector, opportunities: list[Opportunity]
    ) -> dict:
        """Get sector-specific metadata."""
        metadata = {
            "sector_name": sector.value.capitalize(),
            "opportunities_found": len(opportunities),
        }

        if sector == Sector.FOREX:
            metadata["active_pairs"] = len(opportunities)
            metadata["currency_strength"] = {
                "USD": "strong", "EUR": "neutral", "GBP": "weak"
            }
        elif sector == Sector.COMMODITIES:
            metadata["gold_trend"] = "up" if opportunities else "neutral"
            metadata["oil_trend"] = "neutral"
        elif sector == Sector.CRYPTO:
            metadata["market_sentiment"] = "bullish"
            metadata["fear_greed_index"] = 65

        return metadata

    def get_cached_opportunities(
        self, sector: Sector, max_age_seconds: int = 60
    ) -> list[Opportunity]:
        """
        Get cached opportunities for a sector if fresh enough.

        Args:
            sector: Sector to get cached opportunities
            max_age_seconds: Maximum age of cached data

        Returns:
            List of cached opportunities or empty list if stale
        """
        cached = self._sector_cache.get(sector, [])
        last_scan = self._last_scan.get(sector)

        if last_scan:
            age = (datetime.utcnow() - last_scan).total_seconds()
            if age <= max_age_seconds:
                return cached

        return []