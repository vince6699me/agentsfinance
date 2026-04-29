"""
AgentFinance v5 - Gate 4: News Window Check

Gate 4: News Window
Check: Is high-impact news within 30 minutes?
Action on Fail: Block scalp/short-term entries; allow position entries with larger stop
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.teams.risk.pipeline import GateName, GateResult, GateAction

logger = logging.getLogger(__name__)


# High-impact news events that should block trading
HIGH_IMPACT_EVENTS = [
    "NFP", "Non-Farm Payrolls",
    "FOMC", "Federal Reserve",
    "ECB", "European Central Bank",
    "BOJ", "Bank of Japan",
    "BOE", "Bank of England",
    "CPI", "Consumer Price Index",
    "GDP", "Gross Domestic Product",
    "PCE", "Personal Consumption Expenditures",
    "Unemployment",
    "Interest Rate",
    "Press Conference",
]


class Gate4NewsWindow:
    """
    Gate 4: News Window Check
    
    Checks if high-impact news is expected within 30 minutes.
    - Block scalp/short-term entries during news window
    - Allow swing/position entries with larger stop loss
    """

    def __init__(self):
        self.gate_name = GateName.GATE_4_NEWS_WINDOW
        self.news_window_minutes = 30  # Block trades within 30 min of news

    def check(
        self,
        signal_id: int,
        symbol: str,
        direction: str,
        confidence: float,
        strategy_tier: str,
        portfolio_id: int,
        previous_results: List[GateResult],
    ) -> GateResult:
        """
        Check if news window is active for the symbol.
        
        Args:
            signal_id: ID of the signal
            symbol: Trading symbol
            direction: Trade direction
            confidence: Confidence score
            strategy_tier: Strategy tier ("scalp", "short-term", "swing", "position")
            portfolio_id: Portfolio ID
            previous_results: Results from previous gates
            
        Returns:
            GateResult with pass/fail and action
        """
        logger.debug(f"Gate 4: Checking news window for signal {signal_id}, tier: {strategy_tier}")
        
        # Check for upcoming high-impact news
        news_event = self._check_upcoming_news(symbol)
        
        if news_event is None:
            logger.info(f"Gate 4: No high-impact news in window for {symbol}")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message="No high-impact news in trading window",
                action=None,
                metadata={"news_event": None},
            )
        
        # News event found within window
        time_until_news = news_event["minutes_until"]
        
        logger.warning(f"Gate 4: High-impact news approaching: {news_event['event']} in {time_until_news} min")
        
        # Determine action based on strategy tier
        if strategy_tier in ["scalp", "short-term"]:
            # Block scalp and short-term trades
            logger.warning(f"Gate 4: Blocking {strategy_tier} trade due to news window")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"High-impact news ({news_event['event']}) in {time_until_news} min - {strategy_tier} trades blocked",
                action=GateAction.BLOCK,
                metadata={
                    "news_event": news_event["event"],
                    "minutes_until": time_until_news,
                    "strategy_tier": strategy_tier,
                },
            )
        else:
            # Allow swing/position with larger stop
            logger.info(f"Gate 4: Allowing {strategy_tier} trade with larger stop due to news")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"High-impact news ({news_event['event']}) in {time_until_news} min - {strategy_tier} allowed with larger stop",
                action=None,
                reduction_factor=0.7,  # Reduce position size by 30%
                metadata={
                    "news_event": news_event["event"],
                    "minutes_until": time_until_news,
                    "strategy_tier": strategy_tier,
                    "larger_stop_required": True,
                    "position_reduced": True,
                },
            )

    def _check_upcoming_news(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Check for upcoming high-impact news.
        
        In production, this would query a news/calendar service.
        For now, returns None (no news blocking).
        """
        # Simulated: In production, query economic calendar
        # Check if any high-impact news for the symbol's currency(ies) within 30 min
        
        # For demo purposes, return None (no news)
        # In production, integrate with economic calendar API
        return None

    def is_news_active(self, symbol: str) -> bool:
        """
        Check if news window is currently active.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            bool: True if high-impact news within 30 minutes
        """
        news = self._check_upcoming_news(symbol)
        return news is not None

    def get_next_news_event(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the next scheduled news event for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with event details or None
        """
        return self._check_upcoming_news(symbol)