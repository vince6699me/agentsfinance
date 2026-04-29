"""
Custom exception classes for AgentFinance v5.

Following clean code principles:
- Explicit error types for different failure modes
- Meaningful error messages
- Proper inheritance hierarchy for error handling
"""

from typing import Optional, Any, Dict


class AgentFinanceException(Exception):
    """
    Base exception for all AgentFinance errors.

    Following the modular design principle: base class defines common interface.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# Data Layer Exceptions
# ============================================================================

class DatabaseError(AgentFinanceException):
    """Raised when database operations fail."""
    pass


class RecordNotFoundError(AgentFinanceException):
    """Raised when a requested database record is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found",
            details={"resource": resource, "identifier": str(identifier)}
        )


class ValidationError(AgentFinanceException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None,
                 errors: Optional[list] = None):
        super().__init__(
            message=message,
            details={
                "field": field,
                "errors": errors or []
            }
        )


# ============================================================================
# Business Logic Exceptions
# ============================================================================

class TradingError(AgentFinanceException):
    """Base exception for trading-related errors."""
    pass


class InsufficientBalanceError(TradingError):
    """Raised when account balance is insufficient for a trade."""

    def __init__(self, required: float, available: float, currency: str = "USD"):
        super().__init__(
            message=f"Insufficient balance: required {required}, available {available} {currency}",
            details={"required": required, "available": available, "currency": currency}
        )


class InvalidTradeParametersError(TradingError):
    """Raised when trade parameters are invalid."""

    def __init__(self, message: str, params: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=params or {}
        )


class RiskLimitExceededError(TradingError):
    """Raised when a trade would exceed risk limits."""

    def __init__(self, limit_type: str, current_value: float, limit_value: float):
        super().__init__(
            message=f"Risk limit exceeded: {limit_type}",
            details={
                "limit_type": limit_type,
                "current_value": current_value,
                "limit_value": limit_value
            }
        )


class PositionNotFoundError(TradingError):
    """Raised when a position cannot be found."""

    def __init__(self, position_id: str):
        super().__init__(
            message=f"Position not found: {position_id}",
            details={"position_id": position_id}
        )


# ============================================================================
# Scanner & Analysis Exceptions
# ============================================================================

class ScannerError(AgentFinanceException):
    """Base exception for scanner-related errors."""
    pass


class ScanTimeoutError(ScannerError):
    """Raised when a sector scan times out."""

    def __init__(self, sector: str, timeout_seconds: int):
        super().__init__(
            message=f"Scan timeout for sector: {sector}",
            details={"sector": sector, "timeout_seconds": timeout_seconds}
        )


class AnalysisError(AgentFinanceException):
    """Base exception for analysis-related errors."""
    pass


class LLMError(AnalysisError):
    """Raised when LLM operations fail."""

    def __init__(self, message: str, model: Optional[str] = None):
        super().__init__(
            message=f"LLM error: {message}",
            details={"model": model}
        )


# ============================================================================
# External API Exceptions
# ============================================================================

class ExternalAPIError(AgentFinanceException):
    """Base exception for external API errors."""
    pass


class APIConnectionError(ExternalAPIError):
    """Raised when connection to external API fails."""

    def __init__(self, service: str, reason: Optional[str] = None):
        super().__init__(
            message=f"Failed to connect to {service}",
            details={"service": service, "reason": reason}
        )


class APIRateLimitError(ExternalAPIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, service: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {service}",
            details={"service": service, "retry_after": retry_after}
        )


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigurationError(AgentFinanceException):
    """Raised when configuration is invalid or missing."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str):
        super().__init__(
            message=f"Missing required configuration: {config_key}",
            details={"config_key": config_key}
        )


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================

class AuthenticationError(AgentFinanceException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AgentFinanceException):
    """Raised when authorization fails."""
    pass