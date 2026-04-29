"""
AgentFinance v5 - Scanner Module

Team 2: Live Markets Scanner - Scans all 5 sectors for opportunities.

Market Coverage:
- Forex (28+ pairs)
- Commodities (Gold, Oil)
- Stocks (Top 100 US)
- Indices (SP500, NAS100, DAX, FTSE, Nikkei)
- Crypto (BTC, ETH, top-30 alts)
"""

from app.scanner.scanner_service import ScannerService
from app.scanner.sector_scanner import SectorScanner
from app.scanner.aggregator import ScannerAggregator
from app.scanner.models import (
    Sector,
    Opportunity,
    ScanResult,
    SectorScanResult,
    ConfidenceScore,
    ScannerConfig,
)

__all__ = [
    "ScannerService",
    "SectorScanner",
    "ScannerAggregator",
    "Sector",
    "Opportunity",
    "ScanResult",
    "SectorScanResult",
    "ConfidenceScore",
    "ScannerConfig",
]