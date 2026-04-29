"""
FastAPI application entry point for AgentFinance v5.

Modular design with separate routers for each team following REST API design principles.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.database import init_db, close_db
from app.api.health import router as health_router
from app.api.teams_routes import router as teams_router
from app.api.scanner import router as scanner_router
from app.api.signals import router as signals_router
from app.api.risk import router as risk_router


# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown tasks following the clean code principle
    of explicit resource management.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Paper mode: {settings.paper_mode}")
    logger.info(f"Debug: {settings.debug}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    await close_db()
    logger.info("Shutting down AgentFinance v5")


def create_app() -> FastAPI:
    """
    Factory function to create FastAPI application.

    Following modular design: each component has a single responsibility.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        AgentFinance v5 - Autonomous Multi-Team AI Trading System

        ## Teams
        * News & Market Data - Collect news + market data per sector
        * Live Markets Scanner - Scan all 5 sectors for opportunities
        * Analysis - 6 philosophy-based departments (21 agents)
        * Trade Signals - Bull/Bear/Neutral debate → Fund Manager decision
        * Risk & Portfolio - Position sizing, drawdown limits, 7-gate pipeline
        * Live Traders - Sector-specific execution (cTrader + Bybit)
        * Backtesting - Automated strategy testing
        * Analytics - Performance tracking, A/B tests, meta-evaluation

        ## Market Coverage
        * Forex (28+ pairs)
        * Commodities (Gold/Oil)
        * Stocks (Top 100 US)
        * Indices (SP500, NAS100, DAX, etc.)
        * Crypto (BTC, ETH, top-30 alts)
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(teams_router, prefix="/api/v1/teams", tags=["Teams"])
    app.include_router(scanner_router, prefix="/api/v1", tags=["Scanner"])
    app.include_router(signals_router, prefix="/api/v1/signals", tags=["Signals"])
    app.include_router(risk_router, prefix="/api/v1/risk", tags=["Risk"])

    return app


# Create application instance
app = create_app()


@app.get("/")
async def root() -> dict:
    """
    Root endpoint returning application info.

    Following REST API design: resource-based URLs, consistent response format.
    """
    return {
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "paper_mode": settings.paper_mode,
        },
        "meta": {
            "documentation": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )