"""
AgentFinance v5 - Gate 3: Weekly Loss Limit

Gate 3: Weekly Loss Limit
Check: Has weekly P&L dropped below -10% of account?
Action on Fail: Skip next week; trigger manual review alert
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.teams.risk.pipeline import GateName, GateResult, GateAction
from app.config import get_settings
from app.models.portfolios import Portfolio
from app.models.trades import Trade

logger = logging.getLogger(__name__)
settings = get_settings()


class Gate3WeeklyLoss:
    """
    Gate 3: Weekly Loss Limit
    
    Checks if the weekly P&L has dropped below -10% of account balance.
    If triggered, skips next week and triggers manual review alert.
    """

    def __init__(self):
        self.gate_name = GateName.GATE_3_WEEKLY_LOSS
        self.weekly_loss_limit = settings.weekly_loss_limit  # Default 10%

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
        Check if weekly loss limit has been breached.
        
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
        logger.debug(f"Gate 3: Checking weekly loss limit for signal {signal_id}")
        
        # Get start of current week (Monday)
        now = datetime.utcnow()
        days_since_monday = now.weekday()
        week_start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Get portfolio balance
        portfolio_balance = self._get_portfolio_balance(portfolio_id)
        
        # Calculate weekly P&L
        weekly_pnl = self._calculate_weekly_pnl(portfolio_id, week_start)
        
        # Calculate loss percentage
        if portfolio_balance > 0:
            loss_percentage = abs(weekly_pnl) / portfolio_balance
        else:
            loss_percentage = 0
        
        logger.info(f"Gate 3: Weekly P&L: {weekly_pnl:.2f} ({loss_percentage*100:.2f}% of {portfolio_balance})")
        
        # Check if loss exceeds limit
        if weekly_pnl < 0 and loss_percentage >= self.weekly_loss_limit:
            logger.warning(f"Gate 3: WEEKLY LOSS LIMIT BREACHED - {loss_percentage*100:.2f}% loss")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Weekly loss limit breached: {loss_percentage*100:.2f}% (limit: {self.weekly_loss_limit*100}%)",
                action=GateAction.STOP_WEEK,
                metadata={
                    "weekly_pnl": weekly_pnl,
                    "loss_percentage": loss_percentage,
                    "limit": self.weekly_loss_limit,
                    "alert_triggered": True,
                    "manual_review_required": True,
                },
            )
        
        # Check if approaching limit (80% of limit)
        if weekly_pnl < 0 and loss_percentage >= self.weekly_loss_limit * 0.8:
            logger.info(f"Gate 3: Approaching weekly loss limit: {loss_percentage*100:.2f}%")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"Approaching weekly limit: {loss_percentage*100:.2f}% (limit: {self.weekly_loss_limit*100}%)",
                action=GateAction.ALERT_ONLY,
                metadata={
                    "weekly_pnl": weekly_pnl,
                    "loss_percentage": loss_percentage,
                    "warning": True,
                },
            )
        
        logger.info(f"Gate 3: Weekly loss check passed - P&L: {weekly_pnl:.2f}")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Weekly loss within limits: {weekly_pnl:.2f} ({loss_percentage*100:.2f}%)",
            action=None,
            metadata={"weekly_pnl": weekly_pnl, "loss_percentage": loss_percentage},
        )

    def _get_portfolio_balance(self, portfolio_id: int) -> float:
        """Get portfolio balance (simulated for now)."""
        # Default account balance: $100,000
        return 100000.0

    def _calculate_weekly_pnl(self, portfolio_id: int, since: datetime) -> float:
        """
        Calculate weekly P&L from closed trades.
        
        In production, this would query the Trade model.
        """
        # Simulated: In production, query Trade model
        return 0.0

    async def check_async(
        self,
        signal_id: int,
        symbol: str,
        direction: str,
        confidence: float,
        strategy_tier: str,
        portfolio_id: int,
        db: AsyncSession,
    ) -> GateResult:
        """
        Async version that queries actual database.
        
        Args:
            signal_id: ID of the signal
            symbol: Trading symbol
            direction: Trade direction
            confidence: Confidence score
            strategy_tier: Strategy tier
            portfolio_id: Portfolio ID
            db: Database session
            
        Returns:
            GateResult with pass/fail and action
        """
        logger.debug(f"Gate 3 (async): Checking weekly loss limit for signal {signal_id}")
        
        # Get start of current week (Monday)
        now = datetime.utcnow()
        days_since_monday = now.weekday()
        week_start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Get portfolio
        result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            logger.warning(f"Portfolio {portfolio_id} not found, using default balance")
            portfolio_balance = 100000.0
        else:
            portfolio_balance = portfolio.balance
        
        # Get week's closed trades P&L
        result = await db.execute(
            select(func.sum(Trade.pnl)).where(
                Trade.portfolio_id == portfolio_id,
                Trade.closed_at >= week_start,
                Trade.status == "closed",
            )
        )
        weekly_pnl = result.scalar() or 0.0
        
        # Calculate loss percentage
        if portfolio_balance > 0:
            loss_percentage = abs(weekly_pnl) / portfolio_balance
        else:
            loss_percentage = 0
        
        logger.info(f"Gate 3 (async): Weekly P&L: {weekly_pnl:.2f} ({loss_percentage*100:.2f}%)")
        
        if weekly_pnl < 0 and loss_percentage >= self.weekly_loss_limit:
            logger.warning(f"Gate 3: WEEKLY LOSS LIMIT BREACHED")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Weekly loss limit breached: {loss_percentage*100:.2f}%",
                action=GateAction.STOP_WEEK,
                metadata={
                    "weekly_pnl": weekly_pnl,
                    "loss_percentage": loss_percentage,
                    "manual_review_required": True,
                },
            )
        
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Weekly loss within limits: {weekly_pnl:.2f}",
            action=None,
            metadata={"weekly_pnl": weekly_pnl},
        )