"""
HTTP Client with Retry Logic
============================
Reusable session factory with automatic retry and backoff for all data sources.
"""

import logging
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class RetrySession:
    """HTTP session with automatic retry and backoff."""

    def __init__(
        self,
        request_timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
    ):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.timeout = request_timeout

    def get(
        self,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """Perform a GET request with retry and timeout."""
        response = self.session.get(
            url, headers=headers, params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response

    def post(
        self,
        url: str,
        headers: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[bytes] = None,
    ) -> requests.Response:
        """Perform a POST request with retry and timeout."""
        response = self.session.post(
            url, headers=headers, json=json, data=data, timeout=self.timeout
        )
        response.raise_for_status()
        return response
