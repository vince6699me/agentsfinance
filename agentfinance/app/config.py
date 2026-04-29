"""
Configuration module for AgentFinance v5.

Uses environment variables for all settings following the modular design principle
of explicit dependencies - configuration is injected, not hardcoded.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Following clean code principles: meaningful names, type hints,
    and validation at boundaries.
    """

    # Application
    app_name: str = Field(default="AgentFinance v5", description="Application name")
    app_version: str = Field(default="5.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./agentfinance.db",
        description="SQLAlchemy database connection URL"
    )

    # API Keys (will be loaded from environment)
    oanda_api_key: Optional[str] = Field(default=None, description="OANDA API key")
    oanda_account_id: Optional[str] = Field(default=None, description="OANDA account ID")
    bybit_api_key: Optional[str] = Field(default=None, description="Bybit API key")
    bybit_api_secret: Optional[str] = Field(default=None, description="Bybit API secret")
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token")
    finnhub_api_key: Optional[str] = Field(default=None, description="Finnhub API key")

    # LLM Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama LLM server base URL"
    )
    ollama_model: str = Field(default="llama3.1:8b", description="Default Ollama model")

    # Trading Configuration
    paper_mode: bool = Field(default=True, description="Paper trading mode flag")
    max_concurrent_trades: int = Field(default=3, description="Maximum concurrent trades")
    daily_loss_limit: float = Field(default=0.05, description="Daily loss limit (5%)")
    weekly_loss_limit: float = Field(default=0.10, description="Weekly loss limit (10%)")

    # Risk Management
    min_confidence_threshold: int = Field(default=65, description="Minimum confidence for trade")
    high_confidence_threshold: int = Field(default=80, description="High confidence threshold")

    # Scanner Configuration
    scan_interval_minutes: int = Field(default=5, description="Scanner interval in minutes")
    sector_scan_timeout: int = Field(default=30, description="Sector scan timeout in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Following the functional principle: same input = same output.
    This function is idempotent and returns a singleton.
    """
    return Settings()


# Global settings instance for import convenience
settings = get_settings()