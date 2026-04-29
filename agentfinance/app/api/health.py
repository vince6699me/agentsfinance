"""
Health check endpoints for AgentFinance v5.

Following REST API design: appropriate HTTP methods, standard status codes.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Standardized health response model."""

    status: str
    timestamp: str
    version: str
    paper_mode: bool


class DetailedHealthResponse(HealthResponse):
    """Extended health response with system details."""

    database: str
    debug: bool
    components: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns: Health status with basic system information
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        paper_mode=settings.paper_mode,
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check with system component status.

    Returns: Comprehensive health status including all system components
    """
    # Check database connection
    db_status = "connected"  # Placeholder - implement actual DB check

    # Check components
    components = {
        "database": db_status,
        "logging": "active",
        "api": "ready",
    }

    return DetailedHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        paper_mode=settings.paper_mode,
        database=settings.database_url.split("://")[0],
        debug=settings.debug,
        components=components,
    )


@router.get("/ping")
async def ping() -> dict[str, Any]:
    """
    Simple ping endpoint for load balancers and monitoring.

    Minimal response for quick health checks.
    """
    return {
        "data": {"message": "pong"},
        "meta": {"timestamp": datetime.utcnow().isoformat()},
    }