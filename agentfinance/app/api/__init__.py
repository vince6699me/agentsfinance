"""
API package for AgentFinance v5.

Contains routers for health checks and team endpoints.
"""

from app.api.health import router as health_router
from app.api.scanner import router as scanner_router
from app.api.signals import router as signals_router
from app.api.risk import router as risk_router
from app.api.teams_routes import router as teams_router

__all__ = ["health_router", "teams_router", "scanner_router", "signals_router", "risk_router"]