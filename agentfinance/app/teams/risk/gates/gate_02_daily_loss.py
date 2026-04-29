"""
AgentFinance v5 - Gate 2: Daily Loss Limit

Gate 2: Daily Loss Limit
Check: Has daily P&L dropped below -5% of account?
Action on Fail: Stop all trading for the day; alert via Telegram
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


class Gate2DailyLoss:
    """
    Gate 2: Daily Loss Limit
    
    Checks if the daily P&L has dropped below -5% of account balance.
    If triggered, stops all trading for the day and sends alert.
    """

    def __init__(self):
        self.gate_name = GateName.GATE_2_DAILY_LOSS
        self.daily_loss_limit = settings.daily_loss_limit  # Default 5%

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
        Check if daily loss limit has been breached.
        
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
        logger.debug(f"Gate 2: Checking daily loss limit for signal {signal_id}")
        
        # Get today's date range
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate daily P&L from trades
        # In a real implementation, this would query the database
        # For now, we'll simulate the check
        
        # Get portfolio balance (would be from DB in production)
        portfolio_balance = self._get_portfolio_balance(portfolio_id)
        
        # Calculate daily P&L (would be from Trade model in production)
        daily_pnl = self._calculate_daily_pnl(portfolio_id, today_start)
        
        # Calculate loss percentage
        if portfolio_balance > 0:
            loss_percentage = abs(daily_pnl) / portfolio_balance
        else:
            loss_percentage = 0
        
        logger.info(f"Gate 2: Daily P&L: {daily_pnl:.2f} ({loss_percentage*100:.2f}% of {portfolio_balance})")
        
        # Check if loss exceeds limit
        if daily_pnl < 0 and loss_percentage >= self.daily_loss_limit:
            logger.warning(f"Gate 2: DAILY LOSS LIMIT BREACHED - {loss_percentage*100:.2f}% loss")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Daily loss limit breached: {loss_percentage*100:.2f}% (limit: {self.daily_loss_limit*100}%)",
                action=GateAction.STOP_DAY,
                metadata={
                    "daily_pnl": daily_pnl,
                    "loss_percentage": loss_percentage,
                    "limit": self.daily_loss_limit,
                    "alert_triggered": True,
                },
            )
        
        # Check if approaching limit (80% of limit)
        if daily_pnl < 0 and loss_percentage >= self.daily_loss_limit * 0.8:
            logger.info(f"Gate 2: Approaching daily loss limit: {loss_percentage*100:.2f}%")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"Approaching daily limit: {loss_percentage*100:.2f}% (limit: {self.daily_loss_limit*100}%)",
                action=GateAction.ALERT_ONLY,
                metadata={
                    "daily_pnl": daily_pnl,
                    "loss_percentage": loss_percentage,
                    "warning": True,
                },
            )
        
        logger.info(f"Gate 2: Daily loss check passed - P&L: {daily_pnl:.2f}")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Daily loss within limits: {daily_pnl:.2f} ({loss_percentage*100:.2f}%)",
            action=None,
            metadata={"daily_pnl": daily_pnl, "loss_percentage": loss_percentage},
        )

    def _get_portfolio_balance(self, portfolio_id: int) -> float:
        """Get portfolio balance (simulated for now)."""
        # In production, this would query the Portfolio model
        # Default account balance: $100,000
        return 100000.0

    def _calculate_daily_pnl(self, portfolio_id: int, since: datetime) -> float:
        """
        Calculate daily P&L from closed trades.
        
        In production, this would query the Trade model:
        SELECT SUM(pnl) FROM trades 
        WHERE portfolio_id = ? AND closed_at >= ? AND status = 'closed'
        """
        # Simulated: In production, query Trade model
        # For now, return 0 (no losses today)
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
        logger.debug(f"Gate 2 (async): Checking daily loss limit for signal {signal_id}")
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
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
        
        # Get today's closed trades P&L
        result = await db.execute(
            select(func.sum(Trade.pnl)).where(
                Trade.portfolio_id == portfolio_id,
                Trade.closed_at >= today_start,
                Trade.status == "closed",
            )
        )
        daily_pnl = result.scalar() or 0.0
        
        # Calculate loss percentage
        if portfolio_balance > 0:
            loss_percentage = abs(daily_pnl) / portfolio_balance
        else:
            loss_percentage = 0
        
        logger.info(f"Gate 2 (async): Daily P&L: {daily_pnl:.2f} ({loss_percentage*100:.2f}%)")
        
        if daily_pnl < 0 and loss_percentage >= self.daily_loss_limit:
            logger.warning(f"Gate 2: DAILY LOSS LIMIT BREACHED")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Daily loss limit breached: {loss_percentage*100:.2f}%",
                action=GateAction.STOP_DAY,
                metadata={"daily_pnl": daily_pnl, "loss_percentage": loss_percentage},
            )
        
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Daily loss within limits: {daily_pnl:.2f}",
            action=None,
            metadata={"daily_pnl": daily_pnl},
        )