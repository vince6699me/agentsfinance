"""
ICT Strategy 06: Sell-Side Redistribution Swing.

Trade the 75-100 pip bearish swing after a second-stage distribution forms
on the 4H chart. The strategy exploits the market maker sell-side dynamic.

Key Rules:
- Bearish breaker block entry rules
- 4-tier TP structure
- Crash vs controlled decline rule
- 75-100 pip target

See: /home/greywolf/agentsfinance/smc-ict/ICT-06-Sell-Side-Redistribution-Swing.md
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    OBQualityRank,
)


@dataclass
class SellSideConfig:
    """Configuration for Sell-Side Redistribution Swing."""
    # Targets (4-tier TP structure)
    tp1_pips: float = 75.0      # 1R - minimum target
    tp2_pips: float = 100.0     # 1.5-2R - discount terminal
    tp3_pips: float = 150.0     # 3R - parabolic extension
    tp4_pips: Optional[float] = None  # Discount terminal + 30
    
    # Scale-out percentages
    tp1_percent: float = 0.25   # Move to breakeven
    tp2_percent: float = 0.30   # Lock profit
    tp3_percent: float = 0.25   # Trailing stop
    tp4_percent: float = 0.20   # Final exit
    
    # Stop loss
    min_stop_pips: float = 25.0
    max_stop_pips: float = 50.0
    
    # Entry offset
    entry_offset_pips: float = 5.0
    
    # Timeframes
    htf_timeframe: str = "4H"      # Second-stage distribution
    bias_timeframe: str = "D"       # Weekly dealing range
    entry_timeframe: str = "1H"     # First-stage line
    confirmation_timeframe: str = "15M"  # Sell-side sweep
    
    # Risk percent (swing tier = 2%)
    risk_percent: float = 0.02
    
    # Range period (20 days)
    range_days: int = 20
    
    # Discount zone (lower 30% of range)
    discount_zone_percent: float = 0.30
    
    # Discount extension (below range low)
    discount_extension_pips: float = 30.0
    
    # Crash detection
    crash_candle_limit: int = 2  # If TP3 reached in 2 candles = crash


class SellSideRedistributionSwing(ICTBaseStrategy):
    """
    Sell-Side Redistribution Swing Strategy.
    
    Trade setup:
    1. Define 20-day dealing range on Daily chart
    2. Identify first-stage redistribution at Range High
    3. Wait for sell-side liquidity sweep below Range Low
    4. Enter short at first-stage line after retrace
    5. Target 75-100 pips (TP1/TP2)
    
    Key rules:
    - Only bearish direction (sell-side)
    - First-stage line is entry trigger
    - Crash vs controlled decline distinction
    - Breaker block as alternate entry
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[SellSideConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or SellSideConfig()
        self.BASE_RISK_PERCENT = self.config.risk_percent
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Sell-Side setup.
        
        Required market_data keys:
        - candles_daily: Daily candles for range
        - candles_4h: 4H candles for structure
        - candles_1h: 1H candles for entry
        - candles_15m: 15M candles for sweep confirmation
        
        Optional:
        - range_high: Pre-calculated range high
        - range_low: Pre-calculated range low
        - first_stage_line: First-stage redistribution line
        - sell_side_sweep: Confirmed sweep status
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Get candles
        candles_daily = market_data.get("candles_daily", [])
        candles_1h = market_data.get("candles_1h", [])
        candles_15m = market_data.get("candles_15m", [])
        
        if len(candles_daily) < self.config.range_days or len(candles_1h) < 10:
            return None
        
        # R1: Calculate 20-day dealing range
        range_high = market_data.get("range_high")
        range_low = market_data.get("range_low")
        
        if range_high is None or range_low is None:
            range_high, range_low = self._calculate_range(candles_daily)
        
        if range_high is None or range_low is None:
            return None
        
        # Check range width (INV3: narrow range < 50 pips = skip)
        range_width = range_high - range_low
        if range_width < 50:
            return None
        
        # R2: Identify first-stage redistribution
        first_stage_line = market_data.get("first_stage_line")
        if first_stage_line is None:
            first_stage_line = self._identify_first_stage(candles_daily, range_high)
        
        if first_stage_line is None:
            return None
        
        # R5: Check for sell-side liquidity sweep
        sweep_confirmed = market_data.get("sell_side_sweep", False)
        
        if not sweep_confirmed and candles_15m:
            sweep_confirmed = self._check_sweep(
                candles_15m, range_low, Direction.SHORT
            )
        
        if not sweep_confirmed:
            # Check for breaker block as alternate
            breaker = self.detect_breaker_block(candles_1h, Direction.SHORT)
            if breaker is None:
                return None
            # Use breaker for entry
            entry_price = breaker.low - self.config.entry_offset_pips
            stop_price = breaker.high + 10
        else:
            # R6: Confirm retrace reaches first-stage line
            retrace_confirmed = market_data.get("retrace_confirmed", False)
            
            if not retrace_confirmed:
                # Check if price retrace reaches first-stage line
                recent_prices = [c["close"] for c in candles_1h[-10:]]
                if Direction.SHORT == Direction.SHORT:
                    if max(recent_prices) < first_stage_line - 5:
                        return None  # Retrace didn't reach
            else:
                # R8: Entry at first-stage line - 5 pips
                entry_price = first_stage_line - self.config.entry_offset_pips
                stop_price = first_stage_line + self.config.min_stop_pips
        
        # Validate stop distance
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            return None
        if stop_pips > self.config.max_stop_pips:
            return None
        
        # R11: Calculate targets (4-tier)
        tp1_price = entry_price - self.config.tp1_pips
        tp2_price = entry_price - self.config.tp2_pips
        tp3_price = entry_price - self.config.tp3_pips
        tp4_price = range_low - self.config.discount_extension_pips
        
        # Position sizing
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-06-Sell-Side-Redistribution",
            direction=Direction.SHORT,  # Always short
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            take_profit_3=tp3_price,
            take_profit_4=tp4_price,
            session_high=range_high,
            session_low=range_low,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=sweep_confirmed,
            retrace_confirmed=retrace_confirmed,
            position_size=position_size,
            risk_amount=self.account_equity * self.config.risk_percent,
            risk_pips=stop_pips,
            tp1_pips=self.config.tp1_pips,
            tp2_pips=self.config.tp2_pips,
            tp3_pips=self.config.tp3_pips,
            tp1_percent=self.config.tp1_percent,
            tp2_percent=self.config.tp2_percent,
            tp3_percent=self.config.tp3_percent,
            tp4_percent=self.config.tp4_percent,
        )
        
        # Validate setup
        is_valid, reason = self.validate_setup(setup)
        if not is_valid:
            return None
        
        return setup
    
    def validate_setup(self, setup: TradeSetup) -> tuple[bool, str]:
        """
        Validate setup against all Sell-Side rules.
        
        Rules:
        - INV3: Range >= 50 pips
        - INV4: Stop <= 50 pips
        - R13: Crash detection enabled
        """
        # Check range width
        if setup.session_high and setup.session_low:
            range_width = setup.session_high - setup.session_low
            if range_width < 50:
                return False, f"Range {range_width:.1f} pips < 50 (narrow range)"
        
        # Check stop distance
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        if setup.risk_pips > self.config.max_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips > {self.config.max_stop_pips} pips"
        
        return True, "Setup valid"
    
    def _calculate_range(
        self,
        candles: list
    ) -> tuple[float, float]:
        """
        Calculate 20-day dealing range.
        
        Returns:
            (range_high, range_low) tuple
        """
        if len(candles) < self.config.range_days:
            return None, None
        
        recent = candles[-self.config.range_days:]
        
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        
        return max(highs), min(lows)
    
    def _identify_first_stage(
        self,
        candles: list,
        range_high: float
    ) -> Optional[float]:
        """
        Identify first-stage redistribution line.
        
        Look for double-top failure at Range High.
        
        Returns:
            First-stage line price or None
        """
        if len(candles) < 10:
            return None
        
        # Look for rallies that approach or exceed range high
        for i in range(len(candles) - 5, len(candles) - 15, -1):
            if candles[i]["high"] >= range_high - 10:
                # Found a rally to range high
                # Check for second rally that also fails
                for j in range(i + 3, min(i + 10, len(candles))):
                    if candles[j]["high"] >= range_high - 10:
                        # Double top - return the lower high
                        return min(candles[i]["high"], candles[j]["high"])
        
        # Default to 80% of range high
        return range_high * 0.80
    
    def _check_sweep(
        self,
        candles: list,
        level: float,
        direction: Direction
    ) -> bool:
        """
        Check if sell-side sweep is confirmed.
        
        Requirements:
        - Price closes below range low
        - Sweep candle body >= 60%
        - Following candle does not immediately reclaim
        
        Returns:
            True if sweep confirmed
        """
        if len(candles) < 3:
            return False
        
        # Look for close below level
        for i in range(len(candles) - 3):
            if candles[i]["close"] < level:
                # Check body >= 60%
                if not self._has_strong_body(candles[i], direction, 0.60):
                    continue
                
                # Check subsequent candles don't reclaim
                for j in range(i + 1, min(i + 3, len(candles))):
                    if candles[j]["close"] > level:
                        return False
                
                return True
        
        return False
    
    def evaluate_breaker_entry(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[TradeSetup]:
        """
        Evaluate bearish breaker block as alternate entry.
        
        Bearish Breaker:
        - Was a bearish order block
        - Price broke above it (failed)
        - Price now returning from above
        - Expect further downside
        
        Returns:
            TradeSetup if breaker found, None otherwise
        """
        breaker = self.detect_breaker_block(candles, Direction.SHORT)
        
        if breaker is None:
            return None
        
        # Calculate entry (sell limit at breaker bottom - 5 pips)
        entry = breaker.low - self.config.entry_offset_pips
        stop = breaker.high + 10  # Above breaker high + 10
        
        stop_pips = abs(entry - stop)
        
        if stop_pips < self.config.min_stop_pips or stop_pips > self.config.max_stop_pips:
            return None
        
        # Calculate targets
        tp1 = entry - self.config.tp1_pips
        tp2 = entry - self.config.tp2_pips
        
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        return TradeSetup(
            strategy="ICT-06-Sell-Side-Breaker",
            direction=Direction.SHORT,
            entry=entry,
            stop_loss=stop,
            take_profit_1=tp1,
            take_profit_2=tp2,
            ob_zone=breaker,
            ob_quality_rank=breaker.quality_rank,
            timeframe=self.config.entry_timeframe,
            position_size=position_size,
            risk_amount=self.account_equity * self.config.risk_percent,
            risk_pips=stop_pips,
            tp1_pips=self.config.tp1_pips,
            tp2_pips=self.config.tp2_pips,
        )
    
    def detect_crash_decline(
        self,
        candles: list,
        entry: float,
        tp3_price: float
    ) -> bool:
        """
        Detect crash-type decline.
        
        Crash: TP3 reached by 2nd 1H candle (extremely fast drop)
        Controlled: gradual decline with retrace between drops
        
        Returns:
            True if crash detected (should exit immediately)
        """
        if len(candles) < 3:
            return False
        
        # Check if price reached TP3 very quickly
        for i in range(min(3, len(candles))):
            if candles[i]["close"] <= tp3_price:
                return True
        
        return False
    
    def check_stop_adjustment(
        self,
        setup: TradeSetup,
        current_price: float,
        direction: Direction,
        candles_since_entry: int = 0
    ) -> tuple[str, float]:
        """
        Check stop adjustment with crash detection.
        
        Returns:
            (action, new_stop) tuple
        """
        entry = setup.entry
        current_stop = setup.stop_loss
        
        # Calculate pips from entry
        pips_from_entry = entry - current_price
        
        # 40 pips profit: move to breakeven
        if pips_from_entry >= 40:
            return ("breakeven", entry)
        
        # 60 pips profit: move to +15
        if pips_from_entry >= 60:
            return ("profit_stop", entry - 15)
        
        # At range low: close 30% (TP2)
        if setup.session_low and current_price <= setup.session_low:
            return ("partial_close", current_stop)
        
        # At discount terminal: close all
        if setup.take_profit_4 and current_price <= setup.take_profit_4:
            return ("full_close", current_stop)
        
        return ("maintain", current_stop)


# Factory function for strategy creation
def create_sell_side_strategy(
    account_equity: float = 10000.0,
    config: Optional[SellSideConfig] = None
) -> SellSideRedistributionSwing:
    """
    Create Sell-Side Redistribution Swing strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        SellSideRedistributionSwing instance
    """
    return SellSideRedistributionSwing(account_equity, config)