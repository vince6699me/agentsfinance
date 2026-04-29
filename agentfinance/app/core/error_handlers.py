"""
Global error handlers for AgentFinance v5.

Following security patterns:
- Don't expose internal error details to users
- Log full errors internally
- Return safe, generic messages to clients
"""

import traceback
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.core.exceptions import AgentFinanceException


# Logger for error handlers
logger = get_logger(__name__)


async def agent_finance_exception_handler(
    request: Request,
    exc: AgentFinanceException
) -> JSONResponse:
    """
    Handle AgentFinance custom exceptions.

    Following security patterns: return safe error messages to clients,
    log full details internally.
    """
    # Log full error details
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_type": exc.__class__.__name__,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
        },
        exc_info=True
    )

    # Return safe response to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions.

    Following the modular design principle: focused handler for HTTP errors.
    """
    # Log the error
    logger.warning(
        f"HTTP error: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )

    # Return appropriate response based on status code
    if exc.status_code == 404:
        content = {
            "error": "NotFound",
            "message": "The requested resource was not found.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    elif exc.status_code == 401:
        content = {
            "error": "Unauthorized",
            "message": "Authentication is required to access this resource.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    elif exc.status_code == 403:
        content = {
            "error": "Forbidden",
            "message": "You don't have permission to access this resource.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    elif exc.status_code >= 500:
        content = {
            "error": "ServerError",
            "message": "An unexpected server error occurred.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    else:
        content = {
            "error": "HTTPError",
            "message": exc.detail,
            "request_id": request.headers.get("X-Request-ID"),
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.

    Following the modular design principle: focused handler for validation errors.
    """
    # Log validation errors (not as errors, but as warnings)
    logger.warning(
        "Request validation failed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )

    # Return detailed validation errors to help client debugging
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "errors": exc.errors(),
            "request_id": request.headers.get("X-Request-ID"),
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle any unhandled exceptions.

    Following security patterns: never expose internal error details to users.
    Log full traceback internally, return generic message to client.
    """
    # Log full exception with traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )

    # Return safe generic response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.headers.get("X-Request-ID"),
        }
    )


def register_error_handlers(app) -> None:
    """
    Register all error handlers with the FastAPI application.

    Following the declarative approach: describe what to register, not how.
    """
    from fastapi import FastAPI

    # Import exceptions to ensure they're available
    from app.core import exceptions  # noqa: F401

    # Register handlers in order of specificity
    app.add_exception_handler(AgentFinanceException, agent_finance_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)