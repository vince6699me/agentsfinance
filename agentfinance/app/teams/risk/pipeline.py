"""
AgentFinance v5 - 7-Gate Risk Pipeline

Main risk pipeline that applies all 7 gates to every trade approved by Team 4.
Each gate is checked sequentially with proper failure actions defined.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GateName(Enum):
    """Enum for the 7 risk gates."""
    GATE_1_HALT = "system_halt"
    GATE_2_DAILY_LOSS = "daily_loss_limit"
    GATE_3_WEEKLY_LOSS = "weekly_loss_limit"
    GATE_4_NEWS_WINDOW = "news_window"
    GATE_5_SPREAD = "spread_check"
    GATE_6_CORRELATION = "correlation_check"
    GATE_7_CONFIDENCE = "minimum_confidence"


class GateAction(Enum):
    """Action to take when a gate fails."""
    BLOCK = "block"
    REDUCE_SIZE = "reduce_size"
    PAPER_ONLY = "paper_only"
    STOP_DAY = "stop_day"
    STOP_WEEK = "stop_week"
    RETRY_LATER = "retry_later"
    ALERT_ONLY = "alert_only"


@dataclass
class GateResult:
    """Result of a single gate check."""
    gate_name: GateName
    passed: bool
    message: str
    action: Optional[GateAction] = None
    reduction_factor: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskCheckResult:
    """Complete result of the 7-gate risk pipeline."""
    signal_id: int
    symbol: str
    direction: str
    confidence: float
    all_gates_passed: bool
    gate_results: List[GateResult]
    final_action: GateAction
    position_size_multiplier: float = 1.0
    blocked_reason: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "confidence": self.confidence,
            "all_gates_passed": self.all_gates_passed,
            "gate_results": [
                {
                    "gate": g.gate_name.value,
                    "passed": g.passed,
                    "message": g.message,
                    "action": g.action.value if g.action else None,
                    "reduction_factor": g.reduction_factor,
                }
                for g in self.gate_results
            ],
            "final_action": self.final_action.value,
            "position_size_multiplier": self.position_size_multiplier,
            "blocked_reason": self.blocked_reason,
            "checked_at": self.checked_at.isoformat(),
        }


class RiskPipeline:
    """
    7-gate risk pipeline for trade validation.
    
    Applies all 7 gates in sequence:
    1. System Halt - Check if kill switch is active or system in paper mode
    2. Daily Loss Limit - Check if daily P&L dropped below -5%
    3. Weekly Loss Limit - Check if weekly P&L dropped below -10%
    4. News Window - Check for high-impact news within 30 minutes
    5. Spread Check - Check if spread > 2x historical average
    6. Correlation Check - Check if new position increases correlation > 0.7
    7. Minimum Confidence - Check if confidence >= 65
    """

    def __init__(self):
        """Initialize the risk pipeline with all gate checkers."""
        from app.teams.risk.gates import (
            Gate1Halt,
            Gate2DailyLoss,
            Gate3WeeklyLoss,
            Gate4NewsWindow,
            Gate5Spread,
            Gate6Correlation,
            Gate7Confidence,
        )
        
        self.gates = [
            Gate1Halt(),
            Gate2DailyLoss(),
            Gate3WeeklyLoss(),
            Gate4NewsWindow(),
            Gate5Spread(),
            Gate6Correlation(),
            Gate7Confidence(),
        ]
        
        # Track daily/weekly state
        self._daily_loss_triggered = False
        self._weekly_loss_triggered = False
        self._last_daily_reset = datetime.utcnow().date()
        self._last_weekly_reset = datetime.utcnow().date()
        
        logger.info("RiskPipeline initialized with 7 gates")

    def check_all_gates(
        self,
        signal_id: int,
        symbol: str,
        direction: str,
        confidence: float,
        strategy_tier: str = "short-term",
        portfolio_id: int = 1,
    ) -> RiskCheckResult:
        """
        Run all 7 gates on a trade signal.
        
        Args:
            signal_id: ID of the signal to check
            symbol: Trading symbol (e.g., "EURUSD")
            direction: Trade direction ("buy" or "sell")
            confidence: Fund Manager confidence score (0-100)
            strategy_tier: Strategy tier ("scalp", "short-term", "swing", "position")
            portfolio_id: Portfolio ID to check limits against
            
        Returns:
            RiskCheckResult with all gate results and final action
        """
        logger.info(f"Running 7-gate risk pipeline for signal {signal_id}: {symbol} {direction} conf={confidence}")
        
        gate_results: List[GateResult] = []
        position_multiplier = 1.0
        blocked_reason = None
        
        # Check if daily/weekly reset is needed
        self._check_time_based_resets()
        
        # Run each gate in sequence
        for gate in self.gates:
            result = gate.check(
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                strategy_tier=strategy_tier,
                portfolio_id=portfolio_id,
                previous_results=gate_results,
            )
            gate_results.append(result)
            
            # Update state for daily/weekly limits
            if result.gate_name == GateName.GATE_2_DAILY_LOSS and not result.passed:
                self._daily_loss_triggered = True
            if result.gate_name == GateName.GATE_3_WEEKLY_LOSS and not result.passed:
                self._weekly_loss_triggered = True
            
            # Handle reduction factors
            if result.reduction_factor < 1.0:
                position_multiplier *= result.reduction_factor
            
            # If gate is blocked, stop checking further gates
            if result.action == GateAction.BLOCK:
                blocked_reason = f"Gate {result.gate_name.value}: {result.message}"
                break
            elif result.action == GateAction.STOP_DAY:
                blocked_reason = f"Daily loss limit hit: {result.message}"
                break
            elif result.action == GateAction.STOP_WEEK:
                blocked_reason = f"Weekly loss limit hit: {result.message}"
                break
        
        # Determine final action
        all_passed = all(g.passed for g in gate_results)
        
        if blocked_reason:
            final_action = GateAction.BLOCK
        elif self._daily_loss_triggered:
            final_action = GateAction.STOP_DAY
        elif self._weekly_loss_triggered:
            final_action = GateAction.STOP_WEEK
        elif position_multiplier < 1.0:
            final_action = GateAction.REDUCE_SIZE
        else:
            final_action = GateAction.BLOCK if not all_passed else GateAction.BLOCK
        
        # Override: if all gates passed, allow the trade
        if all_passed:
            final_action = GateAction.BLOCK  # Will be handled by caller based on this result
        
        result = RiskCheckResult(
            signal_id=signal_id,
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            all_gates_passed=all_passed,
            gate_results=gate_results,
            final_action=final_action,
            position_size_multiplier=position_multiplier,
            blocked_reason=blocked_reason,
        )
        
        logger.info(f"Risk pipeline complete for signal {signal_id}: passed={all_passed}, multiplier={position_multiplier}")
        
        return result

    def _check_time_based_resets(self):
        """Reset daily/weekly flags based on time."""
        now = datetime.utcnow()
        today = now.date()
        
        # Reset daily at midnight
        if today > self._last_daily_reset:
            self._daily_loss_triggered = False
            self._last_daily_reset = today
            logger.info("Daily loss limit reset")
        
        # Reset weekly on Monday
        if today.weekday() == 0 and today > self._last_weekly_reset:
            self._weekly_loss_triggered = False
            self._last_weekly_reset = today
            logger.info("Weekly loss limit reset")

    def is_trading_allowed(self) -> bool:
        """Check if trading is currently allowed (not halted, not daily/weekly limit hit)."""
        if self._daily_loss_triggered:
            logger.warning("Trading blocked: Daily loss limit triggered")
            return False
        if self._weekly_loss_triggered:
            logger.warning("Trading blocked: Weekly loss limit triggered")
            return False
        return True

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status for monitoring."""
        return {
            "daily_loss_triggered": self._daily_loss_triggered,
            "weekly_loss_triggered": self._weekly_loss_triggered,
            "trading_allowed": self.is_trading_allowed(),
            "last_daily_reset": self._last_daily_reset.isoformat(),
            "last_weekly_reset": self._last_weekly_reset.isoformat(),
        }

    def reset_daily_limit(self):
        """Manually reset daily loss limit (for testing or manual override)."""
        self._daily_loss_triggered = False
        logger.info("Daily loss limit manually reset")

    def reset_weekly_limit(self):
        """Manually reset weekly loss limit (for testing or manual override)."""
        self._weekly_loss_triggered = False
        logger.info("Weekly loss limit manually reset")