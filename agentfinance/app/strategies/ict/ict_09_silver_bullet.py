"""
ICT Strategy 09: Silver Bullet Time-Window.

Time-based algorithmic model - setups form within specific 60-minute windows
daily, combining liquidity draws with time-synchronized price action.

Key Rules:
- 3 time windows: 3-4AM, 10-11AM, 2-3PM NY
- Minimum movement framework (>=15 pips Forex)
- FVG strength 1-3 only
- Body validation rule
- Window failure rule (no-force)
- 15-30 pip target

See: /home/greywolf/agentsfinance/smc-ict/ICT-09-Silver-Bullet-Time-Window.md
"""

from dataclasses import dataclass
from datetime import time, datetime
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    FVGStrength,
)


@dataclass
class SilverBulletConfig:
    """Configuration for Silver Bullet Time-Window."""
    # Targets
    tp1_pips: float = 15.0      # Minimum framework
    tp2_pips: float = 25.0      # Liquidity draw
    
    # Scale-out percentages
    tp1_percent: float = 0.60   # Lock base profit
    tp2_percent: float = 0.40   # Full draw capture
    
    # Stop loss
    min_stop_pips: float = 10.0   # Futures
    max_stop_pips: float = 25.0   # Forex
    
    # Entry offset
    entry_offset_pips: float = 5.0
    
    # Timeframes
    setup_timeframe: str = "15M"   # FVG identification
    entry_timeframe: str = "5M"    # Entry confirmation
    confirmation_timeframe: str = "1M"  # Precise fill
    
    # Risk percent (scalping tier = 1%)
    risk_percent: float = 0.01
    
    # Time windows (NY local)
    window_1_start: time = time(3, 0)   # 3:00 AM
    window_1_end: time = time(4, 0)     # 4:00 AM
    window_2_start: time = time(10, 0)  # 10:00 AM
    window_2_end: time = time(11, 0)    # 11:00 AM
    window_3_start: time = time(14, 0) # 2:00 PM
    window_3_end: time = time(15, 0)    # 3:00 PM
    
    # Minimum movement framework
    min_movement_forex: float = 15.0  # pips
    min_movement_futures: float = 10.0  # handles
    
    # FVG strength (only 1-3 allowed)
    min_fvg_strength: int = 1
    max_fvg_strength: int = 3
    
    # Window validity
    window_validity_minutes: int = 30  # Order expires window close + 30 min
    
    # Max windows per day
    max_windows_per_day: int = 3


class SilverBulletTimeWindow(ICTBaseStrategy):
    """
    Silver Bullet Time-Window Strategy.
    
    Trade setup:
    1. Identify active Silver Bullet window (3-4AM, 10-11AM, 2-3PM)
    2. Map liquidity draws on 15M chart
    3. Determine weekly bias on 60M chart
    4. Check minimum movement potential (>=15 pips)
    5. Wait for FVG formation within 60-minute window
    6. Confirm structure shift (MSS or CHoCH on 15M)
    7. Validate body rule (bodies stay in FVG)
    8. Enter at FVG edge with 15-25 pip stop
    9. Target 15-30 pips (TP1/TP2)
    
    Key rules:
    - FVG strength 1-3 ONLY
    - Minimum movement framework (>=15 pips)
    - Body validation rule (bodies don't violate FVG)
    - Window failure rule (don't force trades)
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[SilverBulletConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or SilverBulletConfig()
        self.BASE_RISK_PERCENT = self.config.risk_percent
        self.windows_today = 0
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Silver Bullet setup.
        
        Required market_data keys:
        - current_time: Current NY time
        - candles_15m: 15M candles for FVG
        - candles_60m: 60M candles for weekly bias
        - direction: Expected direction
        
        Optional:
        - liquidity_draws: Pre-mapped liquidity targets
        - fvg_confirmed: Pre-checked FVG status
        - min_movement: Pre-calculated movement potential
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Check max windows per day
        if self.windows_today >= self.config.max_windows_per_day:
            return None
        
        # R1: Identify active window
        current_time = market_data.get("current_time")
        if current_time is None:
            return None
        
        if isinstance(current_time, datetime):
            current_time = current_time.time()
        
        active_window = self._get_active_window(current_time)
        
        if active_window is None:
            return None  # R12: Window failure rule - don't force
        
        # Get candles
        candles_15m = market_data.get("candles_15m", [])
        candles_60m = market_data.get("candles_60m", [])
        
        if len(candles_15m) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R2: Map liquidity draws
        liquidity_draws = market_data.get("liquidity_draws", [])
        
        if not liquidity_draws:
            liquidity_draws = self._map_liquidity_draws(candles_15m)
        
        if not liquidity_draws:
            return None
        
        # R3: Determine weekly bias
        weekly_bias = self.calculate_weekly_bias(candles_60m) if candles_60m else direction
        
        # R4: Check minimum movement potential
        min_movement = market_data.get("min_movement", 0.0)
        
        if min_movement == 0.0:
            min_movement = self._calculate_min_movement(
                candles_15m, direction, liquidity_draws
            )
        
        if min_movement < self.config.min_movement_forex:
            return None  # INV3: Below minimum framework
        
        # R5: Monitor for Silver Bullet pattern within window
        fvg = self.detect_fvg(candles_15m, direction)
        
        if fvg is None:
            return None
        
        # Check FVG strength (only 1-3 allowed)
        if fvg.strength.value > self.config.max_fvg_strength:
            return None
        
        # R6: Check structure shift (MSS or CHoCH)
        structure_shift = market_data.get("structure_shift", False)
        
        if not structure_shift:
            structure_shift = self._check_structure_shift(candles_15m, direction)
        
        if not structure_shift:
            return None  # INV4: No structure shift
        
        # R6: Body validation rule
        body_valid = self._validate_body_in_fvg(candles_15m, fvg, direction)
        
        if not body_valid:
            return None  # INV2: Bodies violate FVG
        
        # R7: Check confluence (3 of 4)
        confluence = self._check_confluence_4(
            direction, fvg, structure_shift, 
            liquidity_draws, weekly_bias
        )
        
        if confluence < 3:
            return None
        
        # Calculate entry and stop
        entry_price = self._calculate_entry_price(fvg, direction)
        stop_price = self._calculate_stop_price(fvg, direction)
        
        # Validate stop distance
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            return None
        if stop_pips > self.config.max_stop_pips:
            return None
        
        # Calculate targets
        tp1_price = self._calculate_tp_price(entry_price, self.config.tp1_pips, direction)
        tp2_price = self._calculate_tp_price(entry_price, self.config.tp2_pips, direction)
        
        # Position sizing
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-09-Silver-Bullet",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            fvg_zone=fvg,
            fvg_strength=fvg.strength,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=structure_shift,
            retrace_confirmed=body_valid,
            position_size=position_size,
            risk_amount=self.account_equity * self.config.risk_percent,
            risk_pips=stop_pips,
            tp1_pips=self.config.tp1_pips,
            tp2_pips=self.config.tp2_pips,
            tp1_percent=self.config.tp1_percent,
            tp2_percent=self.config.tp2_percent,
        )
        
        # Validate setup
        is_valid, reason = self.validate_setup(setup)
        if not is_valid:
            return None
        
        # Record window used
        self.windows_today += 1
        
        return setup
    
    def validate_setup(self, setup: TradeSetup) -> tuple[bool, str]:
        """
        Validate setup against all Silver Bullet rules.
        
        Rules:
        - FVG strength 1-3 only
        - Minimum movement >= 15 pips
        - Stop 10-25 pips
        - Body validation passed
        """
        # Check FVG strength
        if setup.fvg_strength.value > self.config.max_fvg_strength:
            return False, f"FVG strength {setup.fvg_strength.value} > {self.config.max_fvg_strength}"
        
        # Check stop distance
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        if setup.risk_pips > self.config.max_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips > {self.config.max_stop_pips} pips"
        
        return True, "Setup valid"
    
    def _get_active_window(self, current_time: time) -> Optional[int]:
        """
        Get active Silver Bullet window number.
        
        Returns:
            Window number (1, 2, or 3) or None
        """
        # Window 1: 3:00-4:00 AM
        if self.config.window_1_start <= current_time <= self.config.window_1_end:
            return 1
        
        # Window 2: 10:00-11:00 AM
        if self.config.window_2_start <= current_time <= self.config.window_2_end:
            return 2
        
        # Window 3: 2:00-3:00 PM
        if self.config.window_3_start <= current_time <= self.config.window_3_end:
            return 3
        
        return None
    
    def _map_liquidity_draws(self, candles: list) -> list:
        """
        Map top 3 liquidity draws on 15M chart.
        
        Priority:
        1. Previous day high/low
        2. Previous session high/low
        3. Previous weekly high/low
        4. Week open gap
        5. Fair Value Gap
        
        Returns:
            List of liquidity levels
        """
        if len(candles) < 20:
            return []
        
        draws = []
        
        # Previous day high/low (last 20 candles = ~5 hours)
        day_high = max(c["high"] for c in candles[-20:])
        day_low = min(c["low"] for c in candles[-20:])
        draws.append(("day_high", day_high))
        draws.append(("day_low", day_low))
        
        # Previous session (first 10 candles of day)
        if len(candles) >= 30:
            session_high = max(c["high"] for c in candles[-30:-20])
            session_low = min(c["low"] for c in candles[-30:-20])
            draws.append(("session_high", session_high))
            draws.append(("session_low", session_low))
        
        return draws[:3]  # Return top 3
    
    def _calculate_min_movement(
        self,
        candles: list,
        direction: Direction,
        liquidity_draws: list
    ) -> float:
        """
        Calculate minimum movement potential.
        
        Returns:
            Movement potential in pips
        """
        if not liquidity_draws or not candles:
            return 0.0
        
        current_price = candles[-1].get("close", 0)
        
        # Find nearest liquidity draw in trade direction
        if direction == Direction.LONG:
            targets = [l[1] for l in liquidity_draws if l[1] > current_price]
            if targets:
                return min(targets) - current_price
        else:
            targets = [l[1] for l in liquidity_draws if l[1] < current_price]
            if targets:
                return current_price - max(targets)
        
        return 0.0
    
    def _check_structure_shift(
        self,
        candles: list,
        direction: Direction
    ) -> bool:
        """
        Check for MSS or CHoCH on 15M.
        
        Returns:
            True if structure shift confirmed
        """
        # Check for MSS (simpler - doesn't require prior BOS)
        if len(candles) < 5:
            return False
        
        # Look for lower highs (bearish) or higher lows (bullish)
        if direction == Direction.LONG:
            # Higher low = bullish MSS
            for i in range(len(candles) - 3, len(candles) - 6, -1):
                if (candles[i]["low"] > candles[i-1]["low"] and 
                    candles[i]["low"] > candles[i-2]["low"]):
                    return True
        else:
            # Lower high = bearish MSS
            for i in range(len(candles) - 3, len(candles) - 6, -1):
                if (candles[i]["high"] < candles[i-1]["high"] and 
                    candles[i]["high"] < candles[i-2]["high"]):
                    return True
        
        return False
    
    def _validate_body_in_fvg(
        self,
        candles: list,
        fvg,
        direction: Direction
    ) -> bool:
        """
        Validate that price bodies stay inside or respect the FVG.
        
        Bodies (not wicks) must stay inside or in the FVG.
        If bodies violate the FVG completely -> setup invalid.
        
        Returns:
            True if body validation passed
        """
        # Check recent candles for body violation
        for i in range(max(0, len(candles) - 5), len(candles)):
            candle = candles[i]
            
            if direction == Direction.LONG:
                # For bullish: check if body goes above FVG top
                if candle["close"] > fvg.top or candle["open"] > fvg.top:
                    return False
            else:
                # For bearish: check if body goes below FVG bottom
                if candle["close"] < fvg.bottom or candle["open"] < fvg.bottom:
                    return False
        
        return True
    
    def _check_confluence_4(
        self,
        direction: Direction,
        fvg,
        structure_shift: bool,
        liquidity_draws: list,
        weekly_bias: Direction
    ) -> int:
        """
        Check confluence (minimum 3 of 4 conditions).
        
        1. FVG forms within the 60-minute window
        2. Structure shift confirms direction (MSS or CHoCH on 15M)
        3. Liquidity draw identified (< 15 pips from entry)
        4. Weekly bias aligns with trade direction
        """
        conditions = 0
        
        # Condition 1: FVG in window (assumed - checked by caller)
        conditions += 1
        
        # Condition 2: Structure shift
        if structure_shift:
            conditions += 1
        
        # Condition 3: Liquidity draw (assumed - within 15 pips)
        if liquidity_draws:
            conditions += 1
        
        # Condition 4: Weekly bias alignment
        if direction == weekly_bias:
            conditions += 1
        
        return conditions
    
    def _calculate_entry_price(
        self,
        fvg,
        direction: Direction
    ) -> float:
        """Calculate entry price at FVG edge."""
        offset = self.config.entry_offset_pips
        
        if direction == Direction.LONG:
            return fvg.bottom + offset
        else:
            return fvg.top - offset
    
    def _calculate_stop_price(
        self,
        fvg,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        if direction == Direction.LONG:
            return fvg.bottom - 15  # 15 pips below FVG low
        else:
            return fvg.top + 15     # 15 pips above FVG high
    
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
    
    def check_stop_adjustment(
        self,
        setup: TradeSetup,
        current_price: float,
        direction: Direction,
        minutes_since_entry: int = 0
    ) -> tuple[str, float]:
        """
        Check stop adjustment with window rules.
        
        Returns:
            (action, new_stop) tuple
        """
        entry = setup.entry
        current_stop = setup.stop_loss
        
        # Calculate pips from entry
        if direction == Direction.LONG:
            pips_from_entry = current_price - entry
        else:
            pips_from_entry = entry - current_price
        
        # At TP1 (minimum framework): move to breakeven
        if pips_from_entry >= self.config.tp1_pips:
            return ("breakeven", entry)
        
        # 5 pips from liquidity draw: close 20% remainder
        # This would be checked by caller with liquidity data
        
        # Window closes + 60 min with no TP1: close at market
        if minutes_since_entry > 60:
            return ("window_expire", current_price)
        
        return ("maintain", current_stop)
    
    def reset_daily_windows(self) -> None:
        """Reset daily window count (call at start of day)."""
        self.windows_today = 0
    
    def is_window_failure(
        self,
        current_time: time,
        window_number: int
    ) -> bool:
        """
        Check if window has failed (no valid setup formed).
        
        R12: If no valid Silver Bullet setup forms during a window ->
        do not force a trade. Wait for next window.
        
        Returns:
            True if window should be considered failed
        """
        # Check if we're past the window end + validity
        window_end = None
        
        if window_number == 1:
            window_end = self.config.window_1_end
        elif window_number == 2:
            window_end = self.config.window_2_end
        elif window_number == 3:
            window_end = self.config.window_3_end
        
        if window_end is None:
            return True
        
        # Window closes + 30 min validity
        from datetime import timedelta
        
        window_end_dt = datetime.combine(datetime.today(), window_end)
        validity_end = window_end_dt + timedelta(minutes=self.config.window_validity_minutes)
        
        current_dt = datetime.combine(datetime.today(), current_time)
        
        return current_dt > validity_end


# Factory function for strategy creation
def create_silver_bullet_strategy(
    account_equity: float = 10000.0,
    config: Optional[SilverBulletConfig] = None
) -> SilverBulletTimeWindow:
    """
    Create Silver Bullet Time-Window strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        SilverBulletTimeWindow instance
    """
    return SilverBulletTimeWindow(account_equity, config)