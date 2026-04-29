"""
Core functionality package for AgentFinance v5.

Contains logging setup, middleware, exceptions, and error handlers.
"""

# Logging
from app.core.logging import (
    setup_logging,
    get_logger,
    set_log_level,
    log_request,
    log_security_event,
)

# Middleware
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorLoggingMiddleware,
)

# Exceptions
from app.core.exceptions import (
    AgentFinanceException,
    # Data layer
    DatabaseError,
    RecordNotFoundError,
    ValidationError,
    # Business logic
    TradingError,
    InsufficientBalanceError,
    InvalidTradeParametersError,
    RiskLimitExceededError,
    PositionNotFoundError,
    # Scanner & Analysis
    ScannerError,
    ScanTimeoutError,
    AnalysisError,
    LLMError,
    # External API
    ExternalAPIError,
    APIConnectionError,
    APIRateLimitError,
    # Configuration
    ConfigurationError,
    MissingConfigurationError,
    # Auth
    AuthenticationError,
    AuthorizationError,
)

# Error handlers
from app.core.error_handlers import register_error_handlers


__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "set_log_level",
    "log_request",
    "log_security_event",
    # Middleware
    "RequestLoggingMiddleware",
    "ErrorLoggingMiddleware",
    # Exceptions
    "AgentFinanceException",
    "DatabaseError",
    "RecordNotFoundError",
    "ValidationError",
    "TradingError",
    "InsufficientBalanceError",
    "InvalidTradeParametersError",
    "RiskLimitExceededError",
    "PositionNotFoundError",
    "ScannerError",
    "ScanTimeoutError",
    "AnalysisError",
    "LLMError",
    "ExternalAPIError",
    "APIConnectionError",
    "APIRateLimitError",
    "ConfigurationError",
    "MissingConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    # Error handlers
    "register_error_handlers",
]