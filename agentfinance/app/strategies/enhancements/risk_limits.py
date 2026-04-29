"""
Daily/Weekly Loss Limits Module

Implements ICT v2 risk management limits:
- Daily: 5% of account → stop trading for the day
- Weekly: 10% of account → skip next week
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, date
from collections import defaultdict


class LossLimitType(IntEnum):
    """Types of loss limits"""
    DAILY = 1
    WEEKLY = 2


class LimitStatus(IntEnum):
    """Status of loss limit"""
    ACTIVE = 1      # Trading allowed
    WARNING = 2    # Approaching limit
    TRIGGERED = 3  # Limit hit - stop trading
    RESET = 4      # New period started


@dataclass
class LossLimit:
    """Individual loss limit configuration"""
    limit_type: LossLimitType
    percentage: float  # e.g., 5.0 for 5%
    absolute_amount: float  # Dollar amount
    current_loss: float = 0.0
    status: LimitStatus = LimitStatus.ACTIVE
    
    # Period tracking
    period_start: date = field(default_factory=date.today)
    period_end: Optional[date] = None
    
    # Trade history
    trade_count: int = 0
    winning_trades: int = 0
    losing_trades: int = 0


@dataclass
class RiskLimits:
    """
    Daily and Weekly Loss Limits Manager
    
    Implements ICT v2 risk management:
    - Daily loss limit: 5% of account → stop for the day
    - Weekly loss limit: 10% of account → skip next week
    """
    
    # Default limits
    DEFAULT_DAILY_LIMIT = 5.0  # 5%
    DEFAULT_WEEKLY_LIMIT = 10.0  # 10%
    
    # Warning threshold (percentage of limit reached)
    WARNING_THRESHOLD = 0.80  # 80% of limit
    
    account_balance: float
    daily_limit_pct: float = DEFAULT_DAILY_LIMIT
    weekly_limit_pct: float = DEFAULT_WEEKLY_LIMIT
    
    # Limit tracking
    daily_limit: Optional[LossLimit] = None
    weekly_limit: Optional[LossLimit] = None
    
    # Historical tracking
    daily_history: Dict[date, float] = field(default_factory=dict)
    weekly_history: Dict[date, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize limits after creation"""
        self._initialize_limits()
    
    def _initialize_limits(self):
        """Initialize daily and weekly limits"""
        daily_amount = self.account_balance * (self.daily_limit_pct / 100)
        self.daily_limit = LossLimit(
            limit_type=LossLimitType.DAILY,
            percentage=self.daily_limit_pct,
            absolute_amount=daily_amount
        )
        
        weekly_amount = self.account_balance * (self.weekly_limit_pct / 100)
        self.weekly_limit = LossLimit(
            limit_type=LossLimitType.WEEKLY,
            percentage=self.weekly_limit_pct,
            absolute_amount=weekly_amount
        )
    
    def update_balance(self, new_balance: float) -> None:
        """Update account balance and recalculate limits"""
        self.account_balance = new_balance
        self._initialize_limits()
    
    def record_trade(self, pnl: float) -> Dict[str, Any]:
        """
        Record a trade and check limits.
        
        Args:
            pnl: Profit/Loss of the trade (positive = win, negative = loss)
            
        Returns:
            Dict with limit status and actions
        """
        today = date.today()
        
        # Update daily limit
        self.daily_limit.current_loss += pnl
        self.daily_limit.trade_count += 1
        if pnl > 0:
            self.daily_limit.winning_trades += 1
        else:
            self.daily_limit.losing_trades += 1
        
        # Update weekly limit
        self.weekly_limit.current_loss += pnl
        self.weekly_limit.trade_count += 1
        
        # Record in history
        self.daily_history[today] = self.daily_limit.current_loss
        
        # Check limits
        daily_status = self._check_limit(self.daily_limit)
        weekly_status = self._check_limit(self.weekly_limit)
        
        return {
            "daily_status": daily_status,
            "weekly_status": weekly_status,
            "can_trade": daily_status != LimitStatus.TRIGGERED and weekly_status != LimitStatus.TRIGGERED,
            "daily_loss": self.daily_limit.current_loss,
            "daily_limit": self.daily_limit.absolute_amount,
            "weekly_loss": self.weekly_limit.current_loss,
            "weekly_limit": self.weekly_limit.absolute_amount,
            "warning_message": self._get_warning_message(daily_status, weekly_status)
        }
    
    def _check_limit(self, limit: LossLimit) -> LimitStatus:
        """Check if limit is active, warning, or triggered"""
        if limit.current_loss <= 0:
            return LimitStatus.ACTIVE
        
        loss_percentage = (abs(limit.current_loss) / limit.absolute_amount) * 100
        
        if loss_percentage >= 100:
            return LimitStatus.TRIGGERED
        elif loss_percentage >= (self.WARNING_THRESHOLD * 100):
            return LimitStatus.WARNING
        else:
            return LimitStatus.ACTIVE
    
    def _get_warning_message(
        self,
        daily_status: LimitStatus,
        weekly_status: LimitStatus
    ) -> Optional[str]:
        """Generate warning message based on status"""
        if daily_status == LimitStatus.TRIGGERED:
            return f"DAILY LIMIT TRIGGERED: {self.daily_limit_pct}% loss reached. Stop trading for the day."
        elif weekly_status == LimitStatus.TRIGGERED:
            return f"WEEKLY LIMIT TRIGGERED: {self.weekly_limit_pct}% loss reached. Skip trading next week."
        elif daily_status == LimitStatus.WARNING:
            daily_pct = (abs(self.daily_limit.current_loss) / self.daily_limit.absolute_amount) * 100
            return f"Daily limit warning: {daily_pct:.1f}% of {self.daily_limit_pct}% reached"
        elif weekly_status == LimitStatus.WARNING:
            weekly_pct = (abs(self.weekly_limit.current_loss) / self.weekly_limit.absolute_amount) * 100
            return f"Weekly limit warning: {weekly_pct:.1f}% of {self.weekly_limit_pct}% reached"
        return None
    
    def can_trade(self) -> tuple[bool, Optional[str]]:
        """
        Check if trading is allowed.
        
        Returns:
            Tuple of (can_trade, reason_if_not)
        """
        daily_status = self._check_limit(self.daily_limit)
        weekly_status = self._check_limit(self.weekly_limit)
        
        if daily_status == LimitStatus.TRIGGERED:
            return (False, "Daily loss limit triggered - stop trading for the day")
        if weekly_status == LimitStatus.TRIGGERED:
            return (False, "Weekly loss limit triggered - skip next week")
        
        return (True, None)
    
    def reset_daily(self) -> None:
        """Reset daily limit for new day"""
        self.daily_limit = LossLimit(
            limit_type=LossLimitType.DAILY,
            percentage=self.daily_limit_pct,
            absolute_amount=self.account_balance * (self.daily_limit_pct / 100),
            period_start=date.today()
        )
    
    def reset_weekly(self) -> None:
        """Reset weekly limit for new week"""
        self.weekly_limit = LossLimit(
            limit_type=LossLimitType.WEEKLY,
            percentage=self.weekly_limit_pct,
            absolute_amount=self.account_balance * (self.weekly_limit_pct / 100)
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all limits"""
        daily_status = self._check_limit(self.daily_limit)
        weekly_status = self._check_limit(self.weekly_limit)
        
        return {
            "account_balance": self.account_balance,
            "daily_limit": {
                "percentage": self.daily_limit_pct,
                "absolute": self.daily_limit.absolute_amount,
                "current_loss": self.daily_limit.current_loss,
                "status": daily_status.name,
                "trades": self.daily_limit.trade_count,
                "wins": self.daily_limit.winning_trades,
                "losses": self.daily_limit.losing_trades
            },
            "weekly_limit": {
                "percentage": self.weekly_limit_pct,
                "absolute": self.weekly_limit.absolute_amount,
                "current_loss": self.weekly_limit.current_loss,
                "status": weekly_status.name,
                "trades": self.weekly_limit.trade_count
            },
            "can_trade": daily_status != LimitStatus.TRIGGERED and weekly_status != LimitStatus.TRIGGERED
        }
    
    def get_remaining_risk(self) -> Dict[str, float]:
        """Get remaining risk capacity"""
        daily_remaining = max(0, self.daily_limit.absolute_amount - abs(self.daily_limit.current_loss))
        weekly_remaining = max(0, self.weekly_limit.absolute_amount - abs(self.weekly_limit.current_loss))
        
        return {
            "daily_remaining_pct": (daily_remaining / self.daily_limit.absolute_amount) * 100 if self.daily_limit.absolute_amount > 0 else 0,
            "daily_remaining_amount": daily_remaining,
            "weekly_remaining_pct": (weekly_remaining / self.weekly_limit.absolute_amount) * 100 if self.weekly_limit.absolute_amount > 0 else 0,
            "weekly_remaining_amount": weekly_remaining
        }
    
    @staticmethod
    def create_default(account_balance: float) -> 'RiskLimits':
        """Create RiskLimits with default settings"""
        return RiskLimits(
            account_balance=account_balance,
            daily_limit_pct=RiskLimits.DEFAULT_DAILY_LIMIT,
            weekly_limit_pct=RiskLimits.DEFAULT_WEEKLY_LIMIT
        )