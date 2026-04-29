"""
Logging setup for AgentFinance v5.

Following clean code principles: explicit configuration, dependency injection,
structured logging, and security patterns (no sensitive data in logs).

Enhanced from subtask_01 with:
- Structured logging with JSON support
- Log file rotation
- Context-aware logging
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional, Any, Dict
from logging.handlers import RotatingFileHandler
from datetime import datetime

from app.config import settings


class StructuredLogFormatter(logging.Formatter):
    """
    JSON-structured log formatter for machine-readable logs.

    Following the modular design principle: focused component for structured output.
    """

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for structured logging."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (context)
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in ("msg", "args", "exc_info", "exc_text",
                              "levelname", "levelno", "pathname", "filename",
                              "module", "lineno", "funcName", "created",
                              "msecs", "relativeCreated", "thread", "threadName",
                              "processName", "process", "message", "name",
                              "stack_info"):
                    if not key.startswith("_"):
                        log_data[key] = value

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored formatter for console output during development.

    Following the functional approach: pure function for colorizing output.
    """

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Add color codes to log level names."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> None:
    """
    Configure application-wide logging with structured output and rotation.

    Sets up console and file handlers with appropriate formatters.
    Should be called once at application startup.

    Following security patterns: no sensitive data in logs.
    """
    # Determine log directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    console_formatter = ColoredConsoleFormatter(
        fmt=settings.log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_formatter = StructuredLogFormatter(include_extra=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    # Following security patterns: logs in dedicated directory
    file_handler = RotatingFileHandler(
        filename=log_dir / "agentfinance.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    root_logger.addHandler(file_handler)

    # Error-specific log file (for easier debugging)
    error_handler = RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Following the modular design principle: each module gets its own logger.

    Args:
        name: Module name (typically __name__ from the calling module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Dynamically change log level.

    Useful for runtime debugging or monitoring.

    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    level_upper = level.upper()

    if level_upper not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of: {valid_levels}")

    logging.getLogger().setLevel(getattr(logging, level_upper))


def log_request(logger: logging.Logger, method: str, path: str,
                status_code: int, duration_ms: float,
                extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Log HTTP request with structured data.

    Following the declarative approach: describe what to log, not how.

    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        extra: Additional context to log
    """
    log_data = {
        "type": "request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

    if extra:
        log_data.update(extra)

    # Choose log level based on status code
    if status_code >= 500:
        logger.error("Request failed", extra=log_data)
    elif status_code >= 400:
        logger.warning("Request error", extra=log_data)
    else:
        logger.info("Request completed", extra=log_data)


def log_security_event(logger: logging.Logger, event_type: str,
                       details: Dict[str, Any], severity: str = "INFO") -> None:
    """
    Log security-related events.

    Following security patterns: track security events without exposing sensitive data.

    Args:
        logger: Logger instance
        event_type: Type of security event (auth_failure, invalid_input, etc.)
        details: Event details (sanitized - no passwords/tokens)
        severity: Event severity (DEBUG, INFO, WARNING, ERROR)
    """
    # Sanitize details - remove any potentially sensitive fields
    safe_details = {
        k: v for k, v in details.items()
        if k.lower() not in ("password", "token", "secret", "key", "api_key")
    }

    log_data = {
        "type": "security",
        "event": event_type,
        **safe_details,
    }

    log_func = getattr(logger, severity.lower(), logger.info)
    log_func(f"Security event: {event_type}", extra=log_data)