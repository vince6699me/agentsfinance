"""
TradingEconomics & News Data Client
====================================
Fetch comprehensive macroeconomic data and financial news.

TradingEconomics: 190 countries, all macroeconomic indicators.
News: Financial news via NewsAPI.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .retry_session import RetrySession

logger = logging.getLogger(__name__)


class TradingEconsClient:
    """TradingEconomics.com API client."""

    BASE_URL = "https://api.tradingeconomics.com"

    def __init__(
        self,
        api_key: str,
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.session = RetrySession(
            request_timeout=request_timeout, max_retries=max_retries
        )

    def get_indicator(self, country: str, indicator: str) -> Optional[Dict]:
        """Get latest value for a specific indicator."""
        url = f"{self.BASE_URL}/indicator"
        params = {
            "country": country,
            "indicator": indicator,
            "key": self.api_key,
        }
        response = self.session.get(url, params=params)
        data = response.json()
        if isinstance(data, list) and data:
            return data[0]
        return None

    def get_calendar(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        countries: str = "united states",
    ) -> List[Dict]:
        """Get economic calendar for date range."""
        url = f"{self.BASE_URL}/calendar"
        params = {
            "key": self.api_key,
            "countries": countries,
        }
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = self.session.get(url, params=params)
        return response.json()

    def get_macro_data(self, countries: Optional[List[str]] = None) -> Dict:
        """Get comprehensive macro data for countries."""
        if countries is None:
            countries = [
                "united states",
                "euro area",
                "united kingdom",
                "japan",
                "china",
            ]

        macro = {}
        for country in countries:
            url = f"{self.BASE_URL}/country/{country.replace(' ', '%20')}"
            response = self.session.get(url, params={"key": self.api_key})
            macro[country] = response.json()
        return macro


class NewsClient:
    """Financial news client via NewsAPI."""

    NEWS_API_URL = "https://newsapi.org/v2"

    def __init__(
        self,
        api_key: str,
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.session = RetrySession(
            request_timeout=request_timeout, max_retries=max_retries
        )

    def get_financial_news(
        self,
        query: str = "forex OR trading OR Federal Reserve",
        days_back: int = 1,
        page_size: int = 50,
    ) -> List[Dict]:
        """Fetch financial news articles."""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        params = {
            "q": query,
            "from": from_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
        }

        response = self.session.get(f"{self.NEWS_API_URL}/everything", params=params)
        data = response.json()

        articles = []
        for article in data.get("articles", []):
            articles.append(
                {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "content": article.get("content", "")[:500],
                }
            )
        return articles

    def get_market_headlines(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get market headlines, optionally filtered by symbol."""
        query = f"stock market {symbol}" if symbol else "stock market"
        return self.get_financial_news(query=query, days_back=1)
