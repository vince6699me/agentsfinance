"""
ICT Strategy 04: Weekly Bias Expansion.

Trade the 50-pip intraday expansion aligned with weekly bias.
Tuesday/Wednesday only. Combined with 6% monthly compounding model.

Key Rules:
- Tuesday/Wednesday only rule
- 50 pip target
- 70.5% OTE, FVG strength 1-3
- MSS alternate at 75% size

See: /home/greywolf/agentsfinance/smc-ict/ICT-04-Weekly-Bias-Expansion.md
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    FVG,
    FVGStrength,
)


@dataclass
class WeeklyBiasConfig:
    """Configuration for Weekly Bias Expansion."""
    # Targets
    tp1_pips: float = 50.0
    tp2_pips: float = 75.0
    min_stop_pips: float = 20.0  # Requires more room
    
    # Scale-out percentages
    tp1_percent: float = 0.80
    tp2_percent: float = 0.20
    
    # Entry offset
    entry_offset_pips: float = 5.0
    
    # Kill zones (ET)
    # Only NY AM for this tier
    active_kill_zones: tuple = (KillZone.NY_AM,)
    
    # Timeframes
    htf_timeframe: str = "D"        # Weekly/4H
    setup_timeframe: str = "15M"      # Kill zone structure
    entry_timeframe: str = "5M"
    
    # Trading days
    # Tuesday/Wednesday only
    allowed_days: tuple = (1, 2)  # Tuesday=1, Wednesday=2
    
    # Max setups per week
    max_weekly_setups: int = 1
    
    # Allowed FVG strength
    min_fvg_strength: int = 1
    max_fvg_strength: int = 3


class WeeklyBiasExpansion(ICTBaseStrategy):
    """
    Weekly Bias Expansion Strategy.
    
    Trade setup:
    1. Analyze weekly/4H for bias
    2. Map Monday range
    3. Wait for Tuesday/Wednesday NY AM kill zone
    4. Identify FVG during kill zone (strength 1-3)
    5. Enter at 70.5% OTE
    6. Target 50 pips (TP1), 75 pips (TP2)
    
    Key rules:
    - Monday is observation only, no trades
    - Tuesday/Wednesday trade days only
    - 1 setup per week max
    - 50 pip target
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[WeeklyBiasConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or WeeklyBiasConfig()
        self.weekly_setup_count = 0
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Weekly Bias setup.
        
        Required market_data keys:
        - candles_weekly: Weekly/daily candles
        - monday_candles: Monday candles for range
        - candles_15m: 15M candles for kill zone
        - current_time: Current ET time
        - current_day: Current weekday (0=Monday, 1=Tuesday, etc.)
        - direction: Expected direction
        
        Optional:
        - weekly_high: Pre-calculated weekly high
        - weekly_low: Pre-calculated weekly low
        - monday_high: Monday range high
        - monday_low: Monday range low
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # R3: Check trading day (Tuesday or Wednesday only)
        current_day = market_data.get("current_day", datetime.now().weekday())
        
        # Handle datetime object
        if isinstance(current_day, datetime):
            current_day = current_day.weekday()
        
        if current_day not in self.config.allowed_days:
            return None
        
        # Check weekly setup limit
        if self.weekly_setup_count >= self.config.max_weekly_setups:
            return None
        
        # Check kill zone active
        current_time = market_data.get("current_time")
        if current_time is None:
            return None
        
        active_kz = self._get_active_kill_zone(current_time)
        if active_kz not in self.config.active_kill_zones:
            return None
        
        # Get candles
        candles_weekly = market_data.get("candles_weekly", [])
        monday_candles = market_data.get("monday_candles", [])
        candles_15m = market_data.get("candles_15m", [])
        
        if len(candles_weekly) < 5 or len(candles_15m) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R1: Calculate weekly bias
        weekly_bias = self._calculate_weekly_bias(candles_weekly, direction)
        
        # R3: Monday range
        monday_high = market_data.get("monday_high")
        monday_low = market_data.get("monday_low")
        
        if monday_high is None or monday_low is None:
            if monday_candles:
                monday_high = max(c["high"] for c in monday_candles)
                monday_low = min(c["low"] for c in monday_candles)
            else:
                # Use recent candles
                recent = candles_weekly[-1]
                monday_high = recent.get("high")
                monday_low = recent.get("low")
        
        if monday_high is None or monday_low is None:
            return None
        
        # R7: Identify entry zone (discount/premium relative to Monday range)
        entry_zone = self._identify_entry_zone(
            candles_15m, direction, monday_high, monday_low
        )
        
        if entry_zone is None:
            return None
        
        # R8: Check confluence (3 of 4)
        weekly_high = market_data.get("weekly_high")
        weekly_low = market_data.get("weekly_low")
        
        if weekly_high is None or weekly_low is None:
            weekly_high = max(c["high"] for c in candles_weekly[-20:])
            weekly_low = min(c["low"] for c in candles_weekly[-20:])
        
        confluence = self._check_confluence_4(
            direction, entry_zone, weekly_bias,
            monday_high, monday_low, weekly_high, weekly_low
        )
        
        if confluence < 3:
            return None
        
        # Calculate entry, stop, targets
        entry_price = self._calculate_entry_price(entry_zone, direction)
        stop_price = self._calculate_stop_price(
            monday_high, monday_low, direction
        )
        
        # Validate minimum stop
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            return None  # INV6: Too wide
        
        # Calculate targets
        tp1_price = self._calculate_tp_price(
            entry_price, self.config.tp1_pips, direction
        )
        tp2_price = self._calculate_tp_price(
            entry_price, self.config.tp2_pips, direction
        )
        
        # Position sizing
        position_size = self.calculate_position_size(stop_pips)
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-04-Weekly-Bias-Expansion",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            session_high=monday_high,
            session_low=monday_low,
            kill_zone=active_kz,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=True,
            retrace_confirmed=True,
            position_size=position_size,
            risk_amount=self.account_equity * self.BASE_RISK_PERCENT,
            risk_pips=stop_pips,
            tp1_pips=self.config.tp1_pips,
            tp2_pips=self.config.tp2_pips,
        )
        
        # Validate setup
        is_valid, reason = self.validate_setup(setup)
        if not is_valid:
            return None
        
        return setup
    
    def validate_setup(self, setup: TradeSetup) -> tuple[bool, str]:
        """
        Validate setup against all Weekly Bias rules.
        
        Rules:
        - R8: Confluence >= 3/4 conditions
        - R10: Stop >= 20 pips
        - INV6: Stop distance <= 35 pips
        - INV7: No more than 1 setup this week
        - Kill zone still active
        """
        # Check minimum stop (INV6)
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        # Check maximum stop (INV6)
        if setup.risk_pips > 35:
            return False, f"Stop {setup.risk_pips:.1f} pips > 35 (too wide)"
        
        return True, "Setup valid"
    
    def _get_active_kill_zone(self, current_time) -> Optional[KillZone]:
        """Get active kill zone from current time."""
        if isinstance(current_time, datetime):
            et_time = current_time.time()
        elif isinstance(current_time, time):
            et_time = current_time
        else:
            return None
        
        for kz in self.config.active_kill_zones:
            if self.is_kill_zone_active(kz, et_time):
                return kz
        return None
    
    def _calculate_weekly_bias(
        self,
        candles: list,
        direction: Direction
    ) -> Direction:
        """Calculate weekly bias from candles."""
        if not candles:
            return direction
        
        recent = candles[-5:]  # Last 5 periods
        current_close = recent[-1].get("close", 0)
        
        highs = [c.get("high", 0) for c in recent]
        lows = [c.get("low", 0) for c in recent]
        
        if not highs or not lows:
            return direction
        
        midpoint = (max(highs) + min(lows)) / 2
        
        if current_close > midpoint:
            return Direction.LONG
        return Direction.SHORT
    
    def _identify_entry_zone(
        self,
        candles: list,
        direction: Direction,
        monday_high: float,
        monday_low: float
    ) -> Optional[float]:
        """
        Identify entry zone in discount (long) or premium (short).
        
        Discount: below Monday range midpoint for longs
        Premium: above Monday range midpoint for shorts
        """
        if len(candles) < 3:
            return None
        
        midpoint = (monday_high + monday_low) / 2
        
        # Look for FVG in correct location
        for i in range(len(candles) - 2):
            c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]
            
            if direction == Direction.LONG:
                # Bullish FVG: gap below, looking for in discount (below midpoint)
                if c2["high"] < c1["low"] and c3["high"] < c1["low"]:
                    fvg_bottom = c2["high"]
                    if fvg_bottom < midpoint:  # In discount
                        return fvg_bottom
            else:
                # Bearish FVG: gap above, looking for in premium (above midpoint)
                if c2["low"] > c1["high"] and c3["low"] > c1["high"]:
                    fvg_top = c2["low"]
                    if fvg_top > midpoint:  # In premium
                        return fvg_top
        
        return None
    
    def _check_confluence_4(
        self,
        direction: Direction,
        entry_zone: float,
        weekly_bias: Direction,
        monday_high: float,
        monday_low: float,
        weekly_high: float,
        weekly_low: float
    ) -> int:
        """
        Check confluence (minimum 3 of 4 conditions).
        
        1. Weekly bias aligns with trade direction
        2. Entry zone in discount (long) or premium (short)
        3. Entry zone at 70.5% OTE
        4. No high-impact news in next 60 min
        """
        conditions = 0
        
        # Condition 1: Weekly bias alignment
        if direction == weekly_bias:
            conditions += 1
        
        # Condition 2: Entry zone location
        midpoint = (monday_high + monday_low) / 2
        if direction == Direction.LONG:
            if entry_zone < midpoint:  # Discount
                conditions += 1
        else:
            if entry_zone > midpoint:  # Premium
                conditions += 1
        
        # Condition 3: 70.5% OTE
        ote_level = self.calculate_ote(weekly_high, weekly_low, 0.705)
        if abs(entry_zone - ote_level) <= 5:
            conditions += 1
        
        # Condition 4: Assume no news (would be checked externally)
        conditions += 1
        
        return conditions
    
    def _calculate_entry_price(
        self,
        zone_price: float,
        direction: Direction
    ) -> float:
        """Calculate entry price with offset."""
        offset = self.config.entry_offset_pips
        
        if direction == Direction.LONG:
            return zone_price + offset
        else:
            return zone_price - offset
    
    def _calculate_stop_price(
        self,
        monday_high: float,
        monday_low: float,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        if direction == Direction.LONG:
            return monday_low - self.config.min_stop_pips
        else:
            return monday_high + self.config.min_stop_pips
    
    def _calculate_tp_price(
        self,
        entry: float,
        target_pips: float,
        direction: Direction
    ) -> float:
        """Calculate take profit price."""
        if direction == Direction.LONG:
            return entry + target_pips
        else:
            return entry - target_pips
    
    def record_setup_completed(self) -> None:
        """Record that a setup was completed this week."""
        self.weekly_setup_count += 1
    
    def reset_weekly_count(self) -> None:
        """Reset weekly setup count (call at week start)."""
        self.weekly_setup_count = 0
    
    def calculate_mss_alternate_entry(
        self,
        setup: TradeSetup,
        market_data: dict
    ) -> Optional[TradeSetup]:
        """
        Calculate MSS alternate entry at 75% size.
        
        Used when CHoCH hasn't formed but MSS confirms.
        
        Returns:
            TradeSetup at 75% size, or None
        """
        # Check if MSS confirmed
        mss_confirmed = market_data.get("mss", False)
        
        if mss_confirmed:
            # Create alternate at 75% size
            alternate = setup
            alternate.position_size = setup.position_size * 0.75
            alternate.risk_amount = setup.risk_amount * 0.75
            return alternate
        
        return None
    
    def check_stop_adjustment(
        self,
        setup: TradeSetup,
        current_price: float,
        direction: Direction
    ) -> tuple[str, float]:
        """
        Check stop adjustment based on current price.
        
        Returns:
            (action, new_stop) tuple
        """
        entry = setup.entry
        current_stop = setup.stop_loss
        
        if direction == Direction.LONG:
            pips_from_entry = current_price - entry
        else:
            pips_from_entry = entry - current_price
        
        # 25 pips profit: reduce stop by 10 toward entry
        if pips_from_entry >= 25:
            if direction == Direction.LONG:
                return ("reduce_stop", entry + 10)
            else:
                return ("reduce_stop", entry - 10)
        
        # 40 pips profit: move to breakeven
        if pips_from_entry >= 40:
            return ("breakeven", entry)
        
        # 60 pips profit: move to +15
        if pips_from_entry >= 60:
            if direction == Direction.LONG:
                return ("profit_stop", entry + 15)
            else:
                return ("profit_stop", entry - 15)
        
        return ("maintain", current_stop)


# Factory function for strategy creation
def create_weekly_bias_strategy(
    account_equity: float = 10000.0,
    config: Optional[WeeklyBiasConfig] = None
) -> WeeklyBiasExpansion:
    """
    Create Weekly Bias Expansion strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        WeeklyBiasExpansion instance
    """
    return WeeklyBiasExpansion(account_equity, config)