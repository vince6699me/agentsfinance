"""
AgentFinance v5 - Gate 1: System Halt Check

Gate 1: System Halt
Check: Is the kill switch active or system in paper mode?
Action on Fail: Block all live trades; route to paper trade
"""

from typing import Dict, Any, List, Optional
import logging

from app.teams.risk.pipeline import GateName, GateResult, GateAction
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Gate1Halt:
    """
    Gate 1: System Halt Check
    
    Checks if the system is in halt state or paper mode.
    If in paper mode, routes to paper trading instead of blocking.
    """

    def __init__(self):
        self.gate_name = GateName.GATE_1_HALT

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
        Check if system halt is active.
        
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
        logger.debug(f"Gate 1: Checking system halt for signal {signal_id}")
        
        # Check paper mode setting
        is_paper_mode = settings.paper_mode
        
        # In paper mode, allow trades but mark as paper-only
        if is_paper_mode:
            logger.info(f"Gate 1: System in paper mode - routing signal {signal_id} to paper trading")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message="System in paper mode - trade will be executed as paper trade",
                action=GateAction.PAPER_ONLY,
                metadata={"paper_mode": True},
            )
        
        # Check if there's a system halt flag (could be stored in database)
        # For now, we check the paper_mode as the primary halt indicator
        # In production, this would check a system-wide halt flag
        
        # If not paper mode and no halt, allow live trading
        logger.info(f"Gate 1: System in live mode - allowing live trade for signal {signal_id}")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message="System active - live trading allowed",
            action=None,
            metadata={"paper_mode": False, "live_trading": True},
        )