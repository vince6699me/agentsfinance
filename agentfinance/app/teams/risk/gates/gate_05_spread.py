"""
AgentFinance v5 - Gate 5: Spread Check

Gate 5: Spread Check
Check: Is current spread > 2x the historical average?
Action on Fail: Block entry; log spread spike; retry after 5 minutes
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.teams.risk.pipeline import GateName, GateResult, GateAction

logger = logging.getLogger(__name__)


# Typical spreads in pips for major pairs
TYPICAL_SPREADS = {
    "EURUSD": 1.0,
    "GBPUSD": 1.5,
    "USDJPY": 1.0,
    "USDCHF": 1.5,
    "AUDUSD": 1.5,
    "USDCAD": 1.5,
    "NZDUSD": 1.8,
    "XAUUSD": 30.0,  # Gold in points
    "XTIUSD": 40.0,  # Oil in points
}


class Gate5Spread:
    """
    Gate 5: Spread Check
    
    Checks if the current spread is abnormally high (> 2x historical average).
    If spread is too wide, block entry and log for retry.
    """

    def __init__(self):
        self.gate_name = GateName.GATE_5_SPREAD
        self.spread_multiplier_threshold = 2.0  # Block if > 2x average
        self.retry_after_minutes = 5

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
        Check if spread is within normal range.
        
        Args:
            signal_id: ID of the signal
            symbol: Trading symbol
            direction: Trade direction
            confidence: Confidence score
            strategy_tier: Strategy tier
            portfolio_id: Portfolio ID
            previous_results: Results from previous gates
            
        Returns:
            GateResult with pass/fail and action
        """
        logger.debug(f"Gate 5: Checking spread for signal {signal_id}, symbol: {symbol}")
        
        # Get current spread (would be from live data in production)
        current_spread = self._get_current_spread(symbol)
        
        # Get historical average spread
        avg_spread = self._get_historical_average_spread(symbol)
        
        if avg_spread is None or avg_spread == 0:
            logger.warning(f"Gate 5: No historical spread data for {symbol}, allowing trade")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message="No historical spread data available",
                action=None,
                metadata={"current_spread": current_spread, "avg_spread": None},
            )
        
        # Calculate spread ratio
        spread_ratio = current_spread / avg_spread if avg_spread > 0 else 1.0
        
        logger.info(f"Gate 5: {symbol} spread: {current_spread} (avg: {avg_spread}, ratio: {spread_ratio:.2f}x)")
        
        # Check if spread is too wide
        if spread_ratio > self.spread_multiplier_threshold:
            logger.warning(f"Gate 5: SPREAD SPIKE DETECTED for {symbol}: {spread_ratio:.2f}x average")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Spread spike: {current_spread} pips ({spread_ratio:.2f}x avg) - blocked, retry after {self.retry_after_minutes} min",
                action=GateAction.RETRY_LATER,
                metadata={
                    "current_spread": current_spread,
                    "avg_spread": avg_spread,
                    "spread_ratio": spread_ratio,
                    "retry_after_minutes": self.retry_after_minutes,
                    "spread_spike_logged": True,
                },
            )
        
        # Check if spread is elevated but not blocked
        if spread_ratio > 1.5:
            logger.info(f"Gate 5: Elevated spread for {symbol}: {spread_ratio:.2f}x")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"Elevated spread: {current_spread} pips ({spread_ratio:.2f}x avg)",
                action=None,
                reduction_factor=0.9,  # Slight position reduction
                metadata={
                    "current_spread": current_spread,
                    "avg_spread": avg_spread,
                    "spread_ratio": spread_ratio,
                    "warning": True,
                },
            )
        
        logger.info(f"Gate 5: Spread normal for {symbol}: {current_spread} pips")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Spread normal: {current_spread} pips",
            action=None,
            metadata={
                "current_spread": current_spread,
                "avg_spread": avg_spread,
                "spread_ratio": spread_ratio,
            },
        )

    def _get_current_spread(self, symbol: str) -> float:
        """
        Get current spread for symbol.
        
        In production, this would query live market data.
        """
        # Simulated: Return typical spread
        return TYPICAL_SPREADS.get(symbol, 2.0)

    def _get_historical_average_spread(self, symbol: str) -> Optional[float]:
        """
        Get historical average spread for symbol.
        
        In production, this would calculate from historical data.
        """
        # Simulated: Return typical spread as the "average"
        return TYPICAL_SPREADS.get(symbol, 2.0)

    def is_spread_elevated(self, symbol: str) -> bool:
        """
        Check if spread is currently elevated.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            bool: True if spread > 1.5x average
        """
        current = self._get_current_spread(symbol)
        avg = self._get_historical_average_spread(symbol)
        
        if avg and avg > 0:
            return (current / avg) > 1.5
        return False

    def get_spread_info(self, symbol: str) -> Dict[str, Any]:
        """Get current and average spread info for a symbol."""
        current = self._get_current_spread(symbol)
        avg = self._get_historical_average_spread(symbol)
        
        return {
            "symbol": symbol,
            "current_spread": current,
            "average_spread": avg,
            "spread_ratio": current / avg if avg and avg > 0 else 1.0,
            "is_elevated": self.is_spread_elevated(symbol),
        }