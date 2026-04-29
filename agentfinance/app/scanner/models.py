"""
AgentFinance v5 - Scanner Data Models

Pydantic models for scanner API responses and internal data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Sector(str, Enum):
    """Market sectors covered by the scanner."""

    FOREX = "forex"
    COMMODITIES = "commodities"
    STOCKS = "stocks"
    INDICES = "indices"
    CRYPTO = "crypto"


class OpportunityType(str, Enum):
    """Types of trading opportunities."""

    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    TREND_CONTINUATION = "trend_continuation"
    RANGE_BOUND = "range_bound"
    KILL_ZONE = "kill_zone"
    FVG = "fair_value_gap"
    ORDER_BLOCK = "order_block"
    LIQUIDITY_SWEEP = "liquidity_sweep"


class ConfidenceScore(BaseModel):
    """
    Confidence scoring for opportunities.

    Based on multi-factor analysis with regime-adaptive weighting.
    """

    overall: float = Field(..., ge=0, le=100, description="Overall confidence 0-100")
    confluence: float = Field(..., ge=0, le=100, description="Confluence factor score")
    momentum: float = Field(..., ge=0, le=100, description="Momentum indicator score")
    structure: float = Field(..., ge=0, le=100, description="Market structure score")
    regime: float = Field(..., ge=0, le=100, description="Regime alignment score")

    class Config:
        json_schema_extra = {
            "example": {
                "overall": 78.5,
                "confluence": 85.0,
                "momentum": 72.0,
                "structure": 80.0,
                "regime": 77.0,
            }
        }


class Opportunity(BaseModel):
    """
    A trading opportunity identified by the scanner.

    Contains all information needed for analysis pipeline.
    """

    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    sector: Sector = Field(..., description="Market sector")
    direction: str = Field(..., pattern="^(buy|sell)$", description="Trade direction")
    entry_price: float = Field(..., description="Suggested entry price")
    stop_loss: float = Field(..., description="Stop loss price")
    take_profit: float = Field(..., description="Take profit price")
    risk_reward: float = Field(..., ge=0, description="Risk/reward ratio")
    opportunity_type: OpportunityType = Field(..., description="Type of opportunity")
    confidence: ConfidenceScore = Field(..., description="Confidence scoring breakdown")
    key_levels: dict = Field(default_factory=dict, description="Key price levels")
    indicators: dict = Field(default_factory=dict, description="Technical indicators")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(..., description="Signal expiration time")
    instruments_count: Optional[int] = Field(None, description="For aggregated scans")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "EURUSD",
                "sector": "forex",
                "direction": "buy",
                "entry_price": 1.0850,
                "stop_loss": 1.0820,
                "take_profit": 1.0920,
                "risk_reward": 2.33,
                "opportunity_type": "fvg",
                "confidence": {
                    "overall": 78.5,
                    "confluence": 85.0,
                    "momentum": 72.0,
                    "structure": 80.0,
                    "regime": 77.0,
                },
                "key_levels": {
                    "resistance": 1.0900,
                    "support": 1.0820,
                    "ob_high": 1.0845,
                },
                "indicators": {
                    "rsi": 58.5,
                    "macd_histogram": 0.0012,
                    "adx": 25.0,
                },
                "timestamp": "2026-04-29T10:30:00Z",
                "valid_until": "2026-04-29T11:00:00Z",
            }
        }


class SectorScanResult(BaseModel):
    """
    Scan result for a single sector.
    """

    sector: Sector = Field(..., description="Sector that was scanned")
    opportunities: list[Opportunity] = Field(
        default_factory=list, description="Ranked opportunities"
    )
    total_instruments: int = Field(..., description="Total instruments scanned")
    scan_duration_ms: float = Field(..., description="Scan duration in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(
        default_factory=dict, description="Additional sector metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sector": "forex",
                "opportunities": [],
                "total_instruments": 28,
                "scan_duration_ms": 125.5,
                "timestamp": "2026-04-29T10:30:00Z",
                "metadata": {"active_kill_zones": ["london", "ny"]},
            }
        }


class ScanResult(BaseModel):
    """
    Aggregated scan result across all sectors.
    """

    sectors: dict[Sector, SectorScanResult] = Field(
        ..., description="Scan results per sector"
    )
    total_opportunities: int = Field(..., description="Total opportunities found")
    top_opportunities: list[Opportunity] = Field(
        ..., description="Top 10 ranked opportunities overall"
    )
    scan_duration_ms: float = Field(..., description="Total scan duration")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, description="Cross-sector metadata")


class ScannerConfig(BaseModel):
    """Configuration for scanner behavior."""

    min_confidence: float = Field(
        default=60.0, ge=0, le=100, description="Minimum confidence threshold"
    )
    max_opportunities_per_sector: int = Field(
        default=10, ge=1, description="Max opportunities per sector"
    )
    scan_timeout_seconds: float = Field(
        default=30.0, ge=1, description="Scan timeout per sector"
    )
    include_expired: bool = Field(
        default=False, description="Include expired opportunities"
    )
    regime_filter: Optional[str] = Field(
        None, description="Filter by regime (trending/ranging/transitioning)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "min_confidence": 65.0,
                "max_opportunities_per_sector": 10,
                "scan_timeout_seconds": 30.0,
                "include_expired": False,
                "regime_filter": None,
            }
        }