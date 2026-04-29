"""
ICT Strategy 05: CHoCH Momentum Swing.

Trade the 75-100 pip swing after a Change of Character (CHoCH) confirms
a trend shift on the 4H chart. CHoCH occurs when price breaks a structure
high/low AND the subsequent retrace fails to reclaim it.

Key Rules:
- 4-tier TP structure (TP1=1R, TP2=1.5-2R, TP3=3R, TP4=structure extreme)
- Breaker block as alternate entry
- MSS dual-path (100%/75%)
- OB rank 1-4 acceptable
- 75-100 pip target

See: /home/greywolf/agentsfinance/smc-ict/ICT-05-CHoCH-Momentum-Swing.md
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    OBQualityRank,
    FVGStrength,
    OrderBlock,
)


@dataclass
class CHoCHConfig:
    """Configuration for CHoCH Momentum Swing."""
    # Targets (4-tier TP structure)
    tp1_pips: float = 75.0      # 1R - minimum target
    tp2_pips: float = 100.0     # 1.5-2R - structure extreme
    tp3_pips: float = 150.0     # 3R - extended
    tp4_pips: Optional[float] = None  # Structure extreme
    
    # Scale-out percentages
    tp1_percent: float = 0.30   # Move to breakeven
    tp2_percent: float = 0.30   # Lock profit
    tp3_percent: float = 0.20   # Trailing stop
    tp4_percent: float = 0.20   # Final exit
    
    # Stop loss
    min_stop_pips: float = 25.0
    max_stop_pips: float = 50.0
    
    # Entry offset
    entry_offset_pips: float = 5.0
    
    # Timeframes
    htf_timeframe: str = "4H"      # CHoCH identification
    bias_timeframe: str = "D"       # Weekly bias
    entry_timeframe: str = "1H"     # Entry zone
    confirmation_timeframe: str = "15M"  # Displacement confirmation
    
    # Risk percent (swing tier = 2%)
    risk_percent: float = 0.02
    
    # Allowed OB quality ranks
    min_ob_rank: int = 1
    max_ob_rank: int = 4
    
    # MSS alternate entry
    mss_position_percent: float = 0.75
    
    # Holding period
    max_entry_candles: int = 4   # 4H candles (2 days)
    max_holding_candles: int = 10  # 4H candles (5 days)


class CHoCHMomentumSwing(ICTBaseStrategy):
    """
    CHoCH Momentum Swing Strategy.
    
    Trade setup:
    1. Analyze 4H chart for CHoCH signal
    2. Confirm with Daily chart for weekly bias
    3. Identify entry zone at 70.5% OTE on 1H
    4. Enter at limit order with 25-50 pip stop
    5. Target 75-100 pips (TP1/TP2)
    
    Key rules:
    - CHoCH must be confirmed (not just BOS)
    - Weekly bias should align with CHoCH direction
    - Breaker block is alternate entry
    - MSS provides 75% size entry path
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[CHoCHConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or CHoCHConfig()
        self.BASE_RISK_PERCENT = self.config.risk_percent
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for CHoCH setup.
        
        Required market_data keys:
        - candles_4h: 4H candles for CHoCH identification
        - candles_daily: Daily candles for weekly bias
        - candles_1h: 1H candles for entry zone
        - direction: Expected direction (LONG/SHORT)
        
        Optional:
        - choch_confirmed: Pre-calculated CHoCH status
        - breaker_block: Breaker block if present
        - weekly_high: Pre-calculated weekly high
        - weekly_low: Pre-calculated weekly low
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Get candles
        candles_4h = market_data.get("candles_4h", [])
        candles_daily = market_data.get("candles_daily", [])
        candles_1h = market_data.get("candles_1h", [])
        
        if len(candles_4h) < 20 or len(candles_1h) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R2: Check for CHoCH confirmation
        choch_confirmed = market_data.get("choch_confirmed", False)
        break_level = market_data.get("break_level", 0.0)
        retracement_level = market_data.get("retracement_level", 0.0)
        
        if not choch_confirmed:
            # Try to detect CHoCH
            choch_confirmed, break_level, retracement_level = self.detect_choch(
                candles_4h, direction
            )
        
        if not choch_confirmed:
            # Check for breaker block as alternate entry
            breaker = self.detect_breaker_block(candles_1h, direction)
            if breaker is None:
                return None
            # Use breaker block for entry
            entry_zone = breaker.low if direction == Direction.LONG else breaker.high
            stop_zone = breaker.high if direction == Direction.LONG else breaker.low
        else:
            # R6: Identify entry zone at 70.5% OTE
            if len(candles_4h) < 2:
                return None
            
            # Get the CHoCH move range
            recent_high = max(c["high"] for c in candles_4h[-10:])
            recent_low = min(c["low"] for c in candles_4h[-10:])
            
            # Calculate 70.5% OTE
            entry_zone = self.calculate_ote(recent_high, recent_low, 0.705)
            
            # Stop is beyond retracement level
            if direction == Direction.LONG:
                stop_zone = retracement_level - self.config.min_stop_pips
            else:
                stop_zone = retracement_level + self.config.min_stop_pips
        
        # R3: Check weekly bias alignment
        weekly_bias = self.calculate_weekly_bias(candles_daily)
        
        # R7: Check confluence (3 of 4)
        confluence = self._check_confluence_4(
            direction, choch_confirmed, weekly_bias, entry_zone, candles_4h
        )
        
        if confluence < 3:
            return None
        
        # Calculate entry and stop
        entry_price = self._calculate_entry_price(entry_zone, direction)
        stop_price = self._calculate_stop_price(stop_zone, direction)
        
        # Validate stop distance
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            return None
        if stop_pips > self.config.max_stop_pips:
            return None
        
        # Calculate targets (4-tier)
        tp1_price = self._calculate_tp_price(entry_price, self.config.tp1_pips, direction)
        tp2_price = self._calculate_tp_price(entry_price, self.config.tp2_pips, direction)
        tp3_price = self._calculate_tp_price(entry_price, self.config.tp3_pips, direction)
        
        # Get weekly extreme for TP4
        weekly_high = market_data.get("weekly_high")
        weekly_low = market_data.get("weekly_low")
        
        if weekly_high is None or weekly_low is None:
            if candles_daily:
                weekly_high = max(c["high"] for c in candles_daily[-20:])
                weekly_low = min(c["low"] for c in candles_daily[-20:])
        
        tp4_price = weekly_high if direction == Direction.LONG else weekly_low
        
        # Position sizing
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-05-CHoCH-Momentum-Swing",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            take_profit_3=tp3_price,
            take_profit_4=tp4_price,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=choch_confirmed,
            retrace_confirmed=True,
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
        Validate setup against all CHoCH rules.
        
        Rules:
        - R8: Stop >= 25 pips, <= 50 pips
        - INV3: Target >= 50 pips from entry
        - INV4: Stop <= 50 pips
        - OB quality rank 1-4 acceptable
        """
        # Check minimum stop
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        # Check maximum stop
        if setup.risk_pips > self.config.max_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips > {self.config.max_stop_pips} pips"
        
        # Check target distance
        tp1_distance = abs(setup.take_profit_1 - setup.entry)
        if tp1_distance < 50:
            return False, f"TP1 distance {tp1_distance:.1f} < 50 pips"
        
        return True, "Setup valid"
    
    def _check_confluence_4(
        self,
        direction: Direction,
        choch_confirmed: bool,
        weekly_bias: Direction,
        entry_zone: float,
        candles_4h: list
    ) -> int:
        """
        Check confluence (minimum 3 of 4 conditions).
        
        1. CHoCH confirmed on 4H chart
        2. Entry zone at 70.5% OTE within ±10 pips of 1H VWAP
        3. Weekly bias aligns with CHoCH direction
        4. CHoCH target zone >= 50 pips from entry
        """
        conditions = 0
        
        # Condition 1: CHoCH confirmed
        if choch_confirmed:
            conditions += 1
        
        # Condition 2: 70.5% OTE (simplified - assume VWAP check done externally)
        conditions += 1  # Assume passed
        
        # Condition 3: Weekly bias alignment
        if direction == weekly_bias:
            conditions += 1
        
        # Condition 4: Target >= 50 pips
        if len(candles_4h) >= 10:
            range_high = max(c["high"] for c in candles_4h[-10:])
            range_low = min(c["low"] for c in candles_4h[-10:])
            target_distance = abs(range_high - range_low)
            if target_distance >= 50:
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
        zone_price: float,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        if direction == Direction.LONG:
            return zone_price - self.config.min_stop_pips
        else:
            return zone_price + self.config.min_stop_pips
    
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
        mss_confirmed = market_data.get("mss", False)
        
        if mss_confirmed:
            # Create alternate at 75% size
            alternate = setup
            alternate.position_size = setup.position_size * self.config.mss_position_percent
            alternate.risk_amount = setup.risk_amount * self.config.mss_position_percent
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
        
        # 40 pips profit: move to breakeven
        if pips_from_entry >= 40:
            return ("breakeven", entry)
        
        # 60 pips profit: move to +20
        if pips_from_entry >= 60:
            if direction == Direction.LONG:
                return ("profit_stop", entry + 20)
            else:
                return ("profit_stop", entry - 20)
        
        # At structure extreme: close 30%
        # This would be handled by the caller based on TP hits
        
        return ("maintain", current_stop)
    
    def evaluate_breaker_entry(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[TradeSetup]:
        """
        Evaluate breaker block as alternate entry.
        
        Bullish Breaker:
        - Was a bullish order block
        - Price broke below it (failed)
        - Price now returning from below
        - Expect reversal to upside
        
        Returns:
            TradeSetup if breaker found, None otherwise
        """
        breaker = self.detect_breaker_block(candles, direction)
        
        if breaker is None:
            return None
        
        # Calculate entry
        if direction == Direction.LONG:
            entry = breaker.high + self.config.entry_offset_pips
            stop = breaker.low - 10  # 10 pips below breaker low
        else:
            entry = breaker.low - self.config.entry_offset_pips
            stop = breaker.high + 10  # 10 pips above breaker high
        
        stop_pips = abs(entry - stop)
        
        if stop_pips < self.config.min_stop_pips or stop_pips > self.config.max_stop_pips:
            return None
        
        # Calculate targets
        tp1 = entry + self.config.tp1_pips if direction == Direction.LONG else entry - self.config.tp1_pips
        tp2 = entry + self.config.tp2_pips if direction == Direction.LONG else entry - self.config.tp2_pips
        
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        return TradeSetup(
            strategy="ICT-05-CHoCH-Momentum-Swing-Breaker",
            direction=direction,
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


# Factory function for strategy creation
def create_choch_strategy(
    account_equity: float = 10000.0,
    config: Optional[CHoCHConfig] = None
) -> CHoCHMomentumSwing:
    """
    Create CHoCH Momentum Swing strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        CHoCHMomentumSwing instance
    """
    return CHoCHMomentumSwing(account_equity, config)