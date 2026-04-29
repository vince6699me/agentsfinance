"""
AgentFinance v5 - Scanner Service

Main service orchestrating all scanner operations.
Provides high-level API for scanner endpoints.
"""

from typing import Optional

from app.core.logging import get_logger
from app.scanner.models import (
    Sector,
    Opportunity,
    SectorScanResult,
    ScanResult,
    ScannerConfig,
)
from app.scanner.aggregator import ScannerAggregator, create_aggregator


logger = get_logger(__name__)


class ScannerService:
    """
    Main scanner service for Team 2.

    Orchestrates scanning operations across all sectors and provides
    high-level API for scanner endpoints.
    """

    def __init__(self, config: Optional[ScannerConfig] = None):
        """
        Initialize scanner service.

        Args:
            config: Scanner configuration
        """
        self.config = config or ScannerConfig()
        self._aggregator = create_aggregator(self.config)

    async def scan_sector(self, sector: Sector) -> SectorScanResult:
        """
        Scan a single sector for opportunities.

        Args:
            sector: Sector to scan

        Returns:
            SectorScanResult with ranked opportunities
        """
        logger.info(f"ScannerService: Scanning sector {sector.value}")
        return await self._aggregator.scan_sector(sector)

    async def scan_all_sectors(self) -> ScanResult:
        """
        Scan all five sectors in parallel.

        Returns:
            Aggregated scan result across all sectors
        """
        logger.info("ScannerService: Scanning all 5 sectors in parallel")
        return await self._aggregator.scan_all_sectors()

    async def get_sector_opportunities(
        self, sector: Sector, limit: int = 5
    ) -> list[Opportunity]:
        """
        Get top opportunities for a sector.

        Args:
            sector: Sector to get opportunities for
            limit: Number of opportunities to return (default 5)

        Returns:
            Top opportunities for the sector
        """
        logger.info(f"ScannerService: Getting top {limit} opportunities for {sector.value}")

        # First scan to get fresh data
        result = await self._aggregator.scan_sector(sector)

        # Return top N opportunities
        opportunities = result.opportunities[:limit]

        # If we don't have enough, try to use cache
        if len(opportunities) < limit:
            cached = self._aggregator.get_top_opportunities(sector, limit)
            for opp in cached:
                if opp not in opportunities:
                    opportunities.append(opp)
                    if len(opportunities) >= limit:
                        break

        return opportunities[:limit]

    def get_cached_scan(self, max_age_seconds: int = 30) -> Optional[ScanResult]:
        """
        Get cached full scan result if available and fresh.

        Args:
            max_age_seconds: Maximum age of cached data

        Returns:
            Cached ScanResult or None if stale
        """
        return self._aggregator.get_cached_result(max_age_seconds)

    def get_supported_sectors(self) -> list[dict]:
        """
        Get list of supported sectors with metadata.

        Returns:
            List of sector information
        """
        sectors = [
            {
                "id": Sector.FOREX.value,
                "name": "Forex",
                "description": "28+ major, minor, and exotic currency pairs",
                "instruments_count": 28,
                "execution_venue": "cTrader",
            },
            {
                "id": Sector.COMMODITIES.value,
                "name": "Commodities",
                "description": "Gold (XAUUSD) and Oil (XTIUSD)",
                "instruments_count": 2,
                "execution_venue": "cTrader",
            },
            {
                "id": Sector.STOCKS.value,
                "name": "Stocks",
                "description": "Top 100 US equities",
                "instruments_count": 30,
                "execution_venue": "Bybit",
            },
            {
                "id": Sector.INDICES.value,
                "name": "Indices",
                "description": "SP500, NAS100, DAX, FTSE, Nikkei",
                "instruments_count": 5,
                "execution_venue": "cTrader / Bybit",
            },
            {
                "id": Sector.CRYPTO.value,
                "name": "Crypto",
                "description": "BTC, ETH, and top-30 altcoins",
                "instruments_count": 30,
                "execution_venue": "Bybit",
            },
        ]
        return sectors


# Global service instance
_service: Optional[ScannerService] = None


def get_scanner_service(config: Optional[ScannerConfig] = None) -> ScannerService:
    """
    Get or create the global scanner service instance.

    Args:
        config: Optional scanner configuration

    Returns:
        ScannerService instance
    """
    global _service
    if _service is None:
        _service = ScannerService(config)
    return _service