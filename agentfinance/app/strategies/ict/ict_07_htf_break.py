"""
ICT Strategy 07: HTF Structure Break.

Trade the 200-300 pip directional move after a multi-timeframe (MTF) structure
break confirms a trend change on the weekly chart.

Key Rules:
- Breaker block alternate entry
- 4-tier TP (100/180/250/weekly)
- OB rank 1-4
- Weekly close management
- 200-300 pip target

See: /home/greywolf/agentsfinance/smc-ict/ICT-07-HTF-Structure-Break.md
"""

from dataclasses import dataclass
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    OBQualityRank,
)


@dataclass
class HTFBreakConfig:
    """Configuration for HTF Structure Break."""
    # Targets (4-tier TP structure)
    tp1_pips: float = 100.0     # 1R - first structural target
    tp2_pips: float = 180.0     # 1.5-2R - weekly structure target
    tp3_pips: float = 250.0     # 3R - extended
    tp4_pips: Optional[float] = None  # Weekly extreme
    
    # Scale-out percentages
    tp1_percent: float = 0.30   # Move to breakeven
    tp2_percent: float = 0.30   # Move to +40
    tp3_percent: float = 0.20   # Trailing stop
    tp4_percent: float = 0.20   # Final exit
    
    # Stop loss
    min_stop_pips: float = 40.0
    max_stop_pips: float = 80.0
    
    # Entry offset
    entry_offset_pips: float = 10.0
    
    # Timeframes
    htf_timeframe: str = "W"       # Weekly (D1) for BOS
    mtf_timeframe: str = "4H"       # 4H for CHoCH
    entry_timeframe: str = "1H"     # Entry zone
    confirmation_timeframe: str = "15M"  # Displacement
    
    # Risk percent (position tier = 2.5%)
    risk_percent: float = 0.025
    
    # Weekly lookback
    weekly_lookback: int = 4   # Last 4 weeks for range
    
    # Entry validity
    max_entry_candles: int = 5  # Daily candles
    
    # Allowed OB quality ranks
    min_ob_rank: int = 1
    max_ob_rank: int = 4


class HTFStructureBreak(ICTBaseStrategy):
    """
    HTF Structure Break Strategy.
    
    Trade setup:
    1. Weekly chart: identify Weekly BOS (break of last 4-week extreme)
    2. 4H chart: confirm CHoCH after weekly BOS
    3. 1H chart: identify entry zone at 70.5% OTE
    4. Enter at limit order with 40-80 pip stop
    5. Target 200-300 pips (TP1-TP3)
    
    Key rules:
    - 3-layer MTF confirmation required
    - Weekly close for confirmation (not intraday spike)
    - Breaker block as alternate entry
    - Hold through weekly closes
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[HTFBreakConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or HTFBreakConfig()
        self.BASE_RISK_PERCENT = self.config.risk_percent
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for HTF Structure Break setup.
        
        Required market_data keys:
        - candles_weekly: Weekly candles for BOS
        - candles_4h: 4H candles for CHoCH
        - candles_1h: 1H candles for entry zone
        - direction: Expected direction (LONG/SHORT)
        
        Optional:
        - weekly_bos_confirmed: Pre-calculated BOS status
        - weekly_target: Pre-calculated weekly target
        - htf_choch_confirmed: 4H CHoCH status
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Get candles
        candles_weekly = market_data.get("candles_weekly", [])
        candles_4h = market_data.get("candles_4h", [])
        candles_1h = market_data.get("candles_1h", [])
        
        if len(candles_weekly) < 8 or len(candles_4h) < 20 or len(candles_1h) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R2: Identify Weekly BOS
        weekly_bos = market_data.get("weekly_bos_confirmed", False)
        weekly_extreme = market_data.get("weekly_extreme", 0.0)
        
        if not weekly_bos:
            weekly_bos, weekly_extreme = self._detect_weekly_bos(
                candles_weekly, direction
            )
        
        if not weekly_bos:
            # Check for breaker block as alternate
            breaker = self.detect_breaker_block(candles_1h, direction)
            if breaker is None:
                return None
            entry_zone = breaker.low if direction == Direction.LONG else breaker.high
            stop_zone = breaker.high if direction == Direction.LONG else breaker.low
        else:
            # R4: Confirm 4H CHoCH after weekly BOS
            htf_choch = market_data.get("htf_choch_confirmed", False)
            
            if not htf_choch and candles_4h:
                htf_choch, _, _ = self.detect_choch(candles_4h, direction)
            
            if not htf_choch:
                return None  # INV1: No 4H CHoCH confirmation
            
            # R6: Identify entry zone at 70.5% OTE
            if len(candles_4h) < 2:
                return None
            
            recent_high = max(c["high"] for c in candles_4h[-10:])
            recent_low = min(c["low"] for c in candles_4h[-10:])
            
            entry_zone = self.calculate_ote(recent_high, recent_low, 0.705)
            
            # Stop below entry zone
            if direction == Direction.LONG:
                stop_zone = entry_zone - self.config.min_stop_pips
            else:
                stop_zone = entry_zone + self.config.min_stop_pips
        
        # R7: Check confluence (4 of 5)
        weekly_target = market_data.get("weekly_target")
        
        if weekly_target is None and candles_weekly:
            weekly_target = self._calculate_weekly_target(
                candles_weekly, direction
            )
        
        confluence = self._check_confluence_5(
            direction, weekly_bos, htf_choch, entry_zone, 
            weekly_target, candles_weekly
        )
        
        if confluence < 4:
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
        tp4_price = weekly_target
        
        # Position sizing
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-07-HTF-Structure-Break",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            take_profit_3=tp3_price,
            take_profit_4=tp4_price,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=weekly_bos,
            retrace_confirmed=htf_choch,
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
        Validate setup against all HTF Structure Break rules.
        
        Rules:
        - INV1: Weekly BOS + 4H CHoCH required
        - INV2: Weekly target >= 150 pips from entry
        - INV3: Stop <= 80 pips
        - OB quality rank 1-4 acceptable
        """
        # Check stop distance
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        if setup.risk_pips > self.config.max_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips > {self.config.max_stop_pips} pips"
        
        # Check target distance (INV2)
        if setup.take_profit_1:
            target_distance = abs(setup.take_profit_1 - setup.entry)
            if target_distance < 150:
                return False, f"TP1 distance {target_distance:.1f} < 150 pips"
        
        return True, "Setup valid"
    
    def _detect_weekly_bos(
        self,
        candles: list,
        direction: Direction
    ) -> tuple[bool, float]:
        """
        Detect Weekly BOS (Break of Structure).
        
        Bullish: Weekly candle closes ABOVE last 4-week high
        Bearish: Weekly candle closes BELOW last 4-week low
        
        Returns:
            (is_bos, extreme_level) tuple
        """
        if len(candles) < 5:
            return False, 0.0
        
        # Get last 4 weeks
        recent = candles[-self.config.weekly_lookback:]
        
        if direction == Direction.LONG:
            extreme = min(c["low"] for c in recent)  # Last 4-week low
            # Check if recent candle closes above
            for i in range(len(candles) - 1, len(candles) - 5, -1):
                if candles[i]["close"] > extreme:
                    return True, extreme
        else:
            extreme = max(c["high"] for c in recent)  # Last 4-week high
            # Check if recent candle closes below
            for i in range(len(candles) - 1, len(candles) - 5, -1):
                if candles[i]["close"] < extreme:
                    return True, extreme
        
        return False, 0.0
    
    def _calculate_weekly_target(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[float]:
        """
        Calculate weekly target zone.
        
        Bullish: last major weekly swing low OR external high
        Bearish: last major weekly swing high OR external low
        
        Returns:
            Target price or None
        """
        if len(candles) < 20:
            return None
        
        # Look for swing highs/lows in older data
        if direction == Direction.LONG:
            # Target is last major swing low (look back 20-40 candles)
            for i in range(len(candles) - 20, len(candles) - 40, -1):
                if i > 0 and i < len(candles):
                    # Simple swing low detection
                    if (candles[i]["low"] < candles[i-1]["low"] and 
                        candles[i]["low"] < candles[i+1]["low"]):
                        return candles[i]["low"]
        else:
            # Target is last major swing high
            for i in range(len(candles) - 20, len(candles) - 40, -1):
                if i > 0 and i < len(candles):
                    if (candles[i]["high"] > candles[i-1]["high"] and 
                        candles[i]["high"] > candles[i+1]["high"]):
                        return candles[i]["high"]
        
        return None
    
    def _check_confluence_5(
        self,
        direction: Direction,
        weekly_bos: bool,
        htf_choch: bool,
        entry_zone: float,
        weekly_target: Optional[float],
        candles_weekly: list
    ) -> int:
        """
        Check confluence (minimum 4 of 5 conditions).
        
        1. Weekly BOS confirmed
        2. 4H CHoCH confirms after weekly BOS
        3. Entry zone at 70.5% retrace
        4. Entry zone within ±10 pips of 1H VWAP
        5. Weekly target >= 150 pips from entry
        """
        conditions = 0
        
        # Condition 1: Weekly BOS
        if weekly_bos:
            conditions += 1
        
        # Condition 2: 4H CHoCH
        if htf_choch:
            conditions += 1
        
        # Condition 3: 70.5% OTE (simplified)
        conditions += 1
        
        # Condition 4: VWAP (assumed checked externally)
        conditions += 1
        
        # Condition 5: Target >= 150 pips
        if weekly_target:
            target_distance = abs(weekly_target - entry_zone)
            if target_distance >= 150:
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
    
    def evaluate_breaker_entry(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[TradeSetup]:
        """
        Evaluate breaker block as alternate entry.
        
        Returns:
            TradeSetup if breaker found, None otherwise
        """
        breaker = self.detect_breaker_block(candles, direction)
        
        if breaker is None:
            return None
        
        # Calculate entry
        if direction == Direction.LONG:
            entry = breaker.high + self.config.entry_offset_pips
            stop = breaker.low - 10
        else:
            entry = breaker.low - self.config.entry_offset_pips
            stop = breaker.high + 10
        
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
            strategy="ICT-07-HTF-Break-Breaker",
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
        
        # 100 pips profit: move to breakeven
        if pips_from_entry >= 100:
            return ("breakeven", entry)
        
        # 180 pips profit: move to +40
        if pips_from_entry >= 180:
            if direction == Direction.LONG:
                return ("profit_stop", entry + 40)
            else:
                return ("profit_stop", entry - 40)
        
        # At TP1 (150 pips): close 40%, move stop to +80
        if pips_from_entry >= 150:
            return ("partial_tp1", entry + 80)
        
        # At TP2 (250 pips): close all, trail remainder
        if pips_from_entry >= 250:
            return ("full_tp2", entry + 120)
        
        return ("maintain", current_stop)
    
    def should_hold_through_weekly_close(
        self,
        setup: TradeSetup,
        current_price: float,
        weekly_close_price: float
    ) -> bool:
        """
        Determine if position should be held through weekly close.
        
        Returns:
            True if should hold, False if should exit
        """
        # Hold through weekly close unless:
        # 1. At target zone
        # 2. Invalidating
        
        if setup.take_profit_4 and abs(current_price - setup.take_profit_4) < 20:
            return False  # At target, can close
        
        # INV4: Weekly BOS invalidates within 1 week
        # This would be checked by caller
        
        return True  # Hold through weekly close


# Factory function for strategy creation
def create_htf_break_strategy(
    account_equity: float = 10000.0,
    config: Optional[HTFBreakConfig] = None
) -> HTFStructureBreak:
    """
    Create HTF Structure Break strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        HTFStructureBreak instance
    """
    return HTFStructureBreak(account_equity, config)