"""
AgentFinance v5 - Database Connection Module

Provides SQLite database connection and session management using SQLAlchemy
with aiosqlite for async-compatible operations.

Usage:
    from app.database import get_db, init_db, engine, async_session
    
    # Initialize database on startup
    await init_db()
    
    # Get async session
    async with async_session() as session:
        result = await session.execute(select(Model))
"""

import os
import logging
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "agentfinance.db")

# SQLAlchemy engine and session (sync)
engine = None
SessionLocal = None

# Async engine and session
async_engine = None
async_session_maker = None

# Base class for models
Base = declarative_base()


def get_database_path() -> Path:
    """Get the absolute path to the database file."""
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def create_sync_engine():
    """
    Create synchronous SQLAlchemy engine with SQLite configuration.
    
    Uses StaticPool for SQLite to handle concurrent access properly.
    Enables foreign keys and WAL mode for better performance.
    """
    db_path = get_database_path()
    db_url = f"sqlite:///{db_path}"
    
    engine = create_engine(
        db_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
        poolclass=StaticPool,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )
    
    # Enable foreign keys and WAL mode
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
    
    return engine


def create_async_engine_config():
    """
    Create async SQLAlchemy engine with aiosqlite.
    
    Uses StaticPool for SQLite to handle concurrent access properly.
    """
    db_path = get_database_path()
    # Convert to async URL for aiosqlite
    db_url = f"sqlite+aiosqlite:///{db_path}"
    
    engine = create_async_engine(
        db_url,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        poolclass=StaticPool,
    )
    
    return engine


def init_engine():
    """Initialize the synchronous database engine and session factory."""
    global engine, SessionLocal
    
    if engine is None:
        engine = create_sync_engine()
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info(f"Sync database engine initialized: {get_database_path()}")
    
    return engine


def init_async_engine():
    """Initialize the async database engine and session maker."""
    global async_engine, async_session_maker
    
    if async_engine is None:
        async_engine = create_async_engine_config()
        async_session_maker = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info(f"Async database engine initialized: {get_database_path()}")
    
    return async_engine


async def init_db():
    """
    Initialize the database - create all tables.
    
    Should be called on application startup.
    """
    # Initialize both sync and async engines
    init_engine()
    init_async_engine()
    
    # Import models after engine initialization to avoid circular imports
    # Models import Base from this module, so we import them here
    from app.models import Agent, Strategy, Signal, Trade, Portfolio, Position
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database tables created successfully")
    return engine


async def close_db():
    """Close database connections on shutdown."""
    global engine, async_engine
    
    if engine:
        engine.dispose()
        engine = None
        logger.info("Sync database connections closed")
    
    if async_engine:
        await async_engine.dispose()
        async_engine = None
        logger.info("Async database connections closed")


# ============================================================================
# Synchronous Session Management
# ============================================================================

def get_session():
    """
    Get a synchronous database session context manager.
    
    Yields:
        Session: SQLAlchemy session
        
    Usage:
        with get_session() as session:
            session.query(Model).all()
    """
    init_engine()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ============================================================================
# Async Session Management
# ============================================================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session context manager.
    
    Yields:
        AsyncSession: SQLAlchemy async session
        
    Usage:
        async with get_async_session() as session:
            result = await session.execute(select(Model))
    """
    init_async_engine()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db():
    """
    Get async database session - alias for get_async_session.
    
    Usage:
        async for db in get_db():
            result = await db.execute(select(Model))
    """
    async for session in get_async_session():
        yield session


# ============================================================================
# Table Management
# ============================================================================

async def create_tables():
    """Create all database tables."""
    init_engine()
    # Import models to register them with Base
    from app.models import Agent, Strategy, Signal, Trade, Portfolio, Position
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created")


async def drop_tables():
    """Drop all database tables."""
    init_engine()
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


async def reset_db():
    """Reset database - drop and recreate all tables."""
    await drop_tables()
    await create_tables()
    logger.info("Database reset complete")


# ============================================================================
# Utility Functions
# ============================================================================

def get_db_path() -> str:
    """Get the database file path as a string."""
    return str(get_database_path())


# Export commonly used items
__all__ = [
    "engine",
    "SessionLocal",
    "async_engine",
    "async_session_maker",
    "Base",
    "init_engine",
    "init_async_engine",
    "init_db",
    "close_db",
    "get_db",
    "get_session",
    "get_async_session",
    "create_tables",
    "drop_tables",
    "reset_db",
    "get_db_path",
    "get_database_path",
]