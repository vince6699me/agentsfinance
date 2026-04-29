"""
AgentFinance v5 - Scanner API Endpoints

Team 2: Live Markets Scanner API

Endpoints:
- GET /api/v1/scanner/sector/{sector} - Scan a single sector
- GET /api/v1/scanner/sectors - Scan all five sectors in parallel
- GET /api/v1/scanner/opportunities/{sector} - Top opportunities for a sector
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.scanner.models import (
    Sector,
    Opportunity,
    SectorScanResult,
    ScanResult,
    ScannerConfig,
    ConfidenceScore,
)
from app.scanner.scanner_service import ScannerService, get_scanner_service


router = APIRouter(prefix="/scanner", tags=["Scanner"])


# --- Pydantic Response Models ---

class ScannerSectorResponse(BaseModel):
    """Response model for single sector scan."""

    data: SectorScanResult
    meta: dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "sector": "forex",
                    "opportunities": [],
                    "total_instruments": 28,
                    "scan_duration_ms": 125.5,
                    "timestamp": "2026-04-29T10:30:00Z",
                    "metadata": {"active_kill_zones": ["london", "ny"]},
                },
                "meta": {
                    "timestamp": "2026-04-29T10:30:00Z",
                    "request_id": "abc-123",
                },
            }
        }


class ScannerSectorsResponse(BaseModel):
    """Response model for all sectors scan."""

    data: ScanResult
    meta: dict[str, Any]


class ScannerOpportunitiesResponse(BaseModel):
    """Response model for sector opportunities."""

    data: list[Opportunity]
    meta: dict[str, Any]


class SectorInfoResponse(BaseModel):
    """Response model for sector information."""

    data: list[dict]
    meta: dict[str, Any]


class ScannerConfigResponse(BaseModel):
    """Response model for scanner configuration."""

    data: ScannerConfig
    meta: dict[str, Any]


# --- Service Instance ---

def _get_service() -> ScannerService:
    """Get or create scanner service instance."""
    return get_scanner_service()


# --- Endpoints ---


@router.get(
    "/sectors",
    response_model=ScannerSectorsResponse,
    summary="Scan all sectors",
    description="Scan all five market sectors in parallel and return aggregated opportunities.",
)
async def scan_all_sectors(
    min_confidence: float = Query(
        default=60.0, ge=0, le=100,
        description="Minimum confidence threshold"
    ),
) -> ScannerSectorsResponse:
    """
    Scan all five sectors in parallel.

    Returns:
        Aggregated scan result with all sector results and top opportunities
    """
    service = _get_service()

    # Update config for this request
    service.config.min_confidence = min_confidence

    result = await service.scan_all_sectors()

    return ScannerSectorsResponse(
        data=result,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "sectors_scanned": len(result.sectors),
            "total_opportunities": result.total_opportunities,
            "scan_duration_ms": result.scan_duration_ms,
        },
    )


@router.get(
    "/sector/{sector}",
    response_model=ScannerSectorResponse,
    summary="Scan single sector",
    description="Scan a specific market sector and return ranked opportunities with confidence scores.",
)
async def scan_sector(sector: Sector) -> ScannerSectorResponse:
    """
    Scan a single sector for opportunities.

    Args:
        sector: Market sector to scan (forex, commodities, stocks, indices, crypto)

    Returns:
        Sector scan result with ranked opportunities
    """
    service = _get_service()
    result = await service.scan_sector(sector)

    return ScannerSectorResponse(
        data=result,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "sector": sector.value,
            "opportunities_found": len(result.opportunities),
        },
    )


@router.get(
    "/opportunities/{sector}",
    response_model=ScannerOpportunitiesResponse,
    summary="Get sector opportunities",
    description="Return top-5 current opportunities for a sector with confidence scores.",
)
async def get_opportunities(
    sector: Sector,
    limit: int = Query(default=5, ge=1, le=20, description="Number of opportunities to return"),
) -> ScannerOpportunitiesResponse:
    """
    Get top opportunities for a specific sector.

    Args:
        sector: Market sector to get opportunities for
        limit: Number of opportunities to return (1-20)

    Returns:
        List of top opportunities with confidence scores
    """
    service = _get_service()
    opportunities = await service.get_sector_opportunities(sector, limit)

    if not opportunities:
        # Return empty list with info
        return ScannerOpportunitiesResponse(
            data=[],
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "sector": sector.value,
                "opportunities_found": 0,
                "message": "No opportunities meeting minimum confidence threshold",
            },
        )

    return ScannerOpportunitiesResponse(
        data=opportunities,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "sector": sector.value,
            "opportunities_found": len(opportunities),
        },
    )


@router.get(
    "/sectors/info",
    response_model=SectorInfoResponse,
    summary="Get sector information",
    description="Get metadata about all supported market sectors.",
)
async def get_sectors_info() -> SectorInfoResponse:
    """
    Get information about all supported sectors.

    Returns:
        List of sector information including instruments and execution venues
    """
    service = _get_service()
    sectors = service.get_supported_sectors()

    return SectorInfoResponse(
        data=sectors,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "total_sectors": len(sectors),
        },
    )


@router.get(
    "/config",
    response_model=ScannerConfigResponse,
    summary="Get scanner configuration",
    description="Get current scanner configuration including thresholds.",
)
async def get_scanner_config() -> ScannerConfigResponse:
    """
    Get current scanner configuration.

    Returns:
        Scanner configuration
    """
    service = _get_service()

    return ScannerConfigResponse(
        data=service.config,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get(
    "/cache",
    response_model=ScannerSectorsResponse,
    summary="Get cached scan result",
    description="Get cached full scan result if available and fresh.",
)
async def get_cached_scan(
    max_age: int = Query(default=30, ge=0, le=300, description="Max cache age in seconds"),
) -> ScannerSectorsResponse:
    """
    Get cached scan result if fresh enough.

    Args:
        max_age: Maximum age of cached data in seconds

    Returns:
        Cached scan result or 404 if stale
    """
    service = _get_service()
    cached = service.get_cached_scan(max_age)

    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CACHE_NOT_FOUND",
                    "message": "No cached scan result available or cache is stale",
                    "details": {
                        "max_age_seconds": max_age,
                        "suggestion": "Call /scanner/sectors endpoint to perform fresh scan",
                    },
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    return ScannerSectorsResponse(
        data=cached,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "cached": True,
            "cache_age_seconds": (
                (datetime.utcnow() - cached.timestamp).total_seconds()
                if cached.timestamp
                else None
            ),
        },
    )


@router.get(
    "/opportunities",
    response_model=ScannerOpportunitiesResponse,
    summary="Get top opportunities across all sectors",
    description="Get top opportunities from all sectors combined.",
)
async def get_all_opportunities(
    limit: int = Query(default=10, ge=1, le=50, description="Number of opportunities to return"),
    sector: Sector | None = Query(default=None, description="Filter by sector"),
) -> ScannerOpportunitiesResponse:
    """
    Get top opportunities across all sectors.

    Args:
        limit: Number of opportunities to return (1-50)
        sector: Optional sector filter

    Returns:
        List of top opportunities from all sectors
    """
    service = _get_service()

    if sector:
        opportunities = await service.get_sector_opportunities(sector, limit)
    else:
        # Get from full scan
        result = await service.scan_all_sectors()
        opportunities = result.top_opportunities[:limit]

    return ScannerOpportunitiesResponse(
        data=opportunities,
        meta={
            "timestamp": datetime.utcnow().isoformat(),
            "opportunities_found": len(opportunities),
            "sector_filter": sector.value if sector else "all",
        },
    )