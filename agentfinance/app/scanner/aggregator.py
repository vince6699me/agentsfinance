"""
AgentFinance v5 - Scanner Aggregator

Multi-sector aggregation logic for parallel scanning and result merging.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

from app.core.logging import get_logger
from app.scanner.models import (
    Sector,
    Opportunity,
    ScanResult,
    SectorScanResult,
    ScannerConfig,
)
from app.scanner.sector_scanner import SectorScanner


logger = get_logger(__name__)


class ScannerAggregator:
    """
    Aggregates scan results across all sectors.

    Handles parallel scanning, result merging, and cross-sector ranking.
    """

    def __init__(self, config: Optional[ScannerConfig] = None):
        """
        Initialize scanner aggregator.

        Args:
            config: Scanner configuration
        """
        self.config = config or ScannerConfig()
        self._sector_scanner = SectorScanner(config)
        self._last_full_scan: Optional[datetime] = None
        self._cached_result: Optional[ScanResult] = None

    async def scan_all_sectors(self) -> ScanResult:
        """
        Scan all five sectors in parallel.

        Returns:
            Aggregated scan result with ranked opportunities
        """
        start_time = time.perf_counter()
        logger.info("Starting full sector scan (all 5 sectors in parallel)")

        try:
            # Scan all sectors concurrently
            sectors = list(Sector)
            tasks = [self._sector_scanner.scan_sector(sector) for sector in sectors]
            sector_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Build sector results dict
            sector_scan_results: dict[Sector, SectorScanResult] = {}
            all_opportunities: list[Opportunity] = []

            for sector, result in zip(sectors, sector_results):
                if isinstance(result, SectorScanResult):
                    sector_scan_results[sector] = result
                    all_opportunities.extend(result.opportunities)

            # Sort all opportunities by confidence
            all_opportunities.sort(
                key=lambda x: x.confidence.overall, reverse=True
            )

            # Get top 10 overall
            top_opportunities = all_opportunities[:10]

            total_opportunities = len(all_opportunities)
            scan_duration = (time.perf_counter() - start_time) * 1000

            # Build metadata
            metadata = self._build_metadata(sector_scan_results)

            result = ScanResult(
                sectors=sector_scan_results,
                total_opportunities=total_opportunities,
                top_opportunities=top_opportunities,
                scan_duration_ms=scan_duration,
                timestamp=datetime.utcnow(),
                metadata=metadata,
            )

            # Cache result
            self._last_full_scan = datetime.utcnow()
            self._cached_result = result

            logger.info(
                f"Full scan complete: {total_opportunities} total opportunities "
                f"in {scan_duration:.1f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Error in full sector scan: {e}")
            return ScanResult(
                sectors={},
                total_opportunities=0,
                top_opportunities=[],
                scan_duration_ms=(time.perf_counter() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)},
            )

    async def scan_sector(self, sector: Sector) -> SectorScanResult:
        """
        Scan a single sector.

        Args:
            sector: Sector to scan

        Returns:
            Scan result for the sector
        """
        return await self._sector_scanner.scan_sector(sector)

    def get_top_opportunities(
        self, sector: Sector, count: int = 5
    ) -> list[Opportunity]:
        """
        Get top opportunities for a sector from cache.

        Args:
            sector: Sector to get opportunities for
            count: Number of opportunities to return

        Returns:
            Top opportunities for the sector
        """
        cached = self._sector_scanner.get_cached_opportunities(sector)
        return cached[:count]

    def get_cached_result(self, max_age_seconds: int = 30) -> Optional[ScanResult]:
        """
        Get cached full scan result if fresh enough.

        Args:
            max_age_seconds: Maximum age of cached data

        Returns:
            Cached ScanResult or None if stale
        """
        if not self._cached_result or not self._last_full_scan:
            return None

        age = (datetime.utcnow() - self._last_full_scan).total_seconds()
        if age <= max_age_seconds:
            return self._cached_result

        return None

    def _build_metadata(
        self, sector_results: dict[Sector, SectorScanResult]
    ) -> dict:
        """Build cross-sector metadata."""
        metadata = {
            "sectors_scanned": len(sector_results),
            "scan_type": "full",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Add sector summaries
        sector_summaries = {}
        for sector, result in sector_results.items():
            sector_summaries[sector.value] = {
                "opportunities": len(result.opportunities),
                "instruments": result.total_instruments,
                "duration_ms": round(result.scan_duration_ms, 1),
            }

        metadata["sectors"] = sector_summaries

        # Add market overview
        all_confs = [
            opp.confidence.overall
            for result in sector_results.values()
            for opp in result.opportunities
        ]
        if all_confs:
            metadata["market_overview"] = {
                "avg_confidence": round(sum(all_confs) / len(all_confs), 1),
                "max_confidence": max(all_confs),
                "opportunities_by_confidence": {
                    "high": len([c for c in all_confs if c >= 75]),
                    "medium": len([c for c in all_confs if 60 <= c < 75]),
                    "low": len([c for c in all_confs if c < 60]),
                },
            }

        return metadata


def create_aggregator(config: Optional[ScannerConfig] = None) -> ScannerAggregator:
    """
    Factory function to create scanner aggregator.

    Args:
        config: Scanner configuration

    Returns:
        Configured ScannerAggregator instance
    """
    return ScannerAggregator(config)