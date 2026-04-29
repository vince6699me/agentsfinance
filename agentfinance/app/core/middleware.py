"""
Request/Response logging middleware for AgentFinance v5.

Following clean code principles: modular, focused, declarative.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger, log_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Following the modular design principle: single responsibility -
    this middleware only handles request/response logging.
    """

    def __init__(self, app: ASGIApp, log_body: bool = False):
        """
        Initialize middleware.

        Args:
            app: ASGI application
            log_body: Whether to log request/response bodies (default: False for security)
        """
        super().__init__(app)
        self.logger = get_logger(__name__)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Following the functional approach: pure function - same request
        produces same log output, no side effects on the application state.
        """
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]

        # Start timing
        start_time = time.perf_counter()

        # Log request start
        self.logger.debug(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception before re-raising
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                },
                exc_info=True
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log request completion with structured data
        log_request(
            logger=self.logger,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            extra={
                "request_id": request_id,
                "client_ip": request.client.host if request.client else None,
            }
        )

        # Add request ID to response headers for tracing
        response.headers["X-Request-ID"] = request_id

        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for catching and logging unhandled errors.

    Following the security patterns: don't expose internal error details to users.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Catch unhandled errors and log them safely."""
        try:
            return await call_next(request)
        except Exception as e:
            # Log full error details internally
            self.logger.error(
                f"Unhandled error: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(e).__name__,
                    # Don't include stack trace in extra - use exc_info
                },
                exc_info=True
            )

            # Re-raise to let error handlers process the response
            raise