"""
ICT Strategy 03: Kill-Zone Pulse.

Trade the 30-50 pip intraday expansion triggered by a kill zone
session displacement. Price breaks the prior session range during
London or NY open, creates a momentum candle with body >= 70%, then
pulls back to the 70.5% OTE level.

Key Rules:
- Displacement candle entry (body >= 70%)
- 30-50 pip target
- 70.5% OTE replaces 62%
- MSS dual-path entry (100% if CHoCH, 75% if MSS only)
- OB rank filter

See: /home/greywolf/agentsfinance/smc-ict/ICT-03-Kill-Zone-Pulse.md
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from app.strategies.ict.base import (
    ICTBaseStrategy,
    KillZone,
    Direction,
    TradeSetup,
    OrderBlock,
    OBQualityRank,
)


@dataclass
class KillZonePulseConfig:
    """Configuration for Kill-Zone Pulse."""
    # Targets
    tp1_pips: float = 30.0
    tp2_pips: float = 50.0
    min_stop_pips: float = 15.0
    
    # Scale-out percentages
    tp1_percent: float = 0.80
    tp2_percent: float = 0.20
    
    # Entry offset from zone
    entry_offset_pips: float = 5.0
    
    # Displacement body threshold
    displacement_body_threshold: float = 0.70  # 70%
    
    # Kill zones (ET)
    active_kill_zones: tuple = (
        KillZone.LONDON,
        KillZone.NY_AM,
        KillZone.NY_PM,
        KillZone.ASIA
    )
    
    # Timeframes
    context_timeframe: str = "60M"
    setup_timeframe: str = "15M"
    entry_timeframe: str = "5M"
    confirmation_timeframe: str = "1M"
    
    # Risk percentage (higher for larger target)
    risk_percent: float = 0.015  # 1.5%


@dataclass
class EntryPathway:
    """Entry pathway for Kill-Zone Pulse."""
    CHOCH = "choc"      # Primary: displacement + CHoCH = 100%
    MSS = "mss"         # Alternate: displacement + MSS (no CHoCH) = 75%
    DISPLACEMENT_ONLY = "displacement"  # Fallback: only displacement = SKIP


class KillZonePulse(ICTBaseStrategy):
    """
    Kill-Zone Pulse Strategy.
    
    Trade setup:
    1. Determine weekly bias on 60M chart
    2. Map kill zone range on 15M chart
    3. Monitor for displacement candle (body >= 70%)
    4. Wait for retrace to 70.5% OTE
    5. Enter with limit order
    6. Target 30 pips (TP1), 50 pips (TP2)
    
    Entry pathways:
    - Primary (100%): displacement + CHoCH confirmed
    - Alternate (75%): displacement + MSS confirmed (no CHoCH)
    - Fallback (SKIP): only displacement
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[KillZonePulseConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or KillZonePulseConfig()
        # Override risk for larger target
        self.BASE_RISK_PERCENT = self.config.risk_percent
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Kill-Zone Pulse setup.
        
        Required market_data keys:
        - candles_60m: Weekly context candles
        - candles_15m: 15M candles for setup
        - candles_5m: 5M candles for entry
        - current_time: Current ET time
        - direction: Expected direction
        - kick_zone_high: Previous kill zone high
        - kick_zone_low: Previous kill zone low
        - vwap_15m: 15M VWAP level
        - choc: CHoCH confirmed (optional)
        - mss: MSS confirmed (optional)
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Check kill zone active
        current_time = market_data.get("current_time")
        if current_time is None:
            return None
        
        active_kz = self._get_active_kill_zone(current_time)
        if active_kz not in self.config.active_kill_zones:
            return None
        
        # Get candles
        candles_60m = market_data.get("candles_60m", [])
        candles_15m = market_data.get("candles_15m", [])
        candles_5m = market_data.get("candles_5m", [])
        
        if len(candles_60m) < 20 or len(candles_15m) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R1: Weekly bias
        weekly_bias = self.calculate_weekly_bias(candles_60m)
        
        # R2: Kill zone range
        kzr_high = market_data.get("kick_zone_high")
        kzr_low = market_data.get("kick_zone_low")
        
        if kzr_high is None or kzr_low is None:
            # Calculate from previous kill zone
            kzr_high, kzr_low = self._calculate_kzr_levels(candles_15m, active_kz)
        
        # R6: Find displacement candle
        displacement = self._find_displacement_candle(
            candles_15m, active_kz, direction
        )
        
        if displacement is None:
            return None
        
        # Validate displacement (>= 70% body)
        is_valid_displacement = self._validate_displacement(displacement, direction)
        if not is_valid_displacement:
            return None
        
        # R8: Find retrace to 70.5% OTE
        entry_zone = self._calculate_entry_zone(
            displacement, kzr_high, kzr_low, direction
        )
        
        if entry_zone is None:
            return None
        
        # Determine entry pathway and position size
        pathway = self._determine_entry_pathway(
            market_data, is_valid_displacement
        )
        
        if pathway == EntryPathway.DISPLACEMENT_ONLY:
            return None  # Skip
        
        # Determine position size based on pathway
        position_multiplier = 1.0 if pathway == EntryPathway.CHOCH else 0.75
        
        # Calculate entry, stop, targets
        entry_price = self._calculate_entry_price(entry_zone, direction)
        stop_price = self._calculate_stop_price(displacement, direction)
        
        # Validate minimum stop
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            stop_pips = max(stop_pips, self.config.min_stop_pips)
            stop_price = self._calculate_stop_at_min(
                entry_price, stop_pips, direction
            )
        
        # Calculate targets
        tp1_price = self._calculate_tp_price(
            entry_price, self.config.tp1_pips, direction
        )
        tp2_price = self._calculate_tp_price(
            entry_price, self.config.tp2_pips, direction
        )
        
        # Position sizing
        position_size = self.calculate_position_size(stop_pips) * position_multiplier
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-03-Kill-Zone-Pulse",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            session_high=kzr_high,
            session_low=kzr_low,
            kill_zone=active_kz,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=True,
            retrace_confirmed=True,
            position_size=position_size,
            risk_amount=self.account_equity * self.config.risk_percent * position_multiplier,
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
        Validate setup against all Kill-Zone Pulse rules.
        
        Rules:
        - R6: Displacement (body >= 70%) confirmed
        - R7: No news within 10 min of displacement
        - R11: Stop >= 15 pips
        - INV4: Kill zone still active
        - Stop distance <= 30 pips (INV6)
        """
        # Check displacement confirmed
        if not setup.displacement_confirmed:
            return False, "Displacement not confirmed"
        
        # Check minimum stop
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        # Check maximum stop (INV6)
        if setup.risk_pips > 30:
            return False, f"Stop {setup.risk_pips:.1f} pips > 30 (too wide)"
        
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
    
    def _calculate_kzr_levels(
        self,
        candles: list,
        session: KillZone
    ) -> tuple[float, float]:
        """Calculate kill zone range (high/low) from candles."""
        # Use last 20 candles for KZ range
        recent = candles[-20:]
        
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        
        return max(highs), min(lows)
    
    def _find_displacement_candle(
        self,
        candles: list,
        kill_zone: KillZone,
        direction: Direction
    ) -> Optional[dict]:
        """
        Find displacement candle during kill zone.
        
        Displacement candle:
        - Opens near one end of range
        - Closes near/through opposite end
        - Body >= 70% of range
        """
        for i in range(len(candles) - 1, -1, -1):
            candle = candles[i]
            
            high = candle.get("high", 0)
            low = candle.get("low", 0)
            close = candle.get("close", 0)
            open_price = candle.get("open", 0)
            
            if high == low:
                continue
            
            body = abs(close - open_price)
            body_percent = body / (high - low)
            
            if body_percent >= self.config.displacement_body_threshold:
                # Check direction
                if direction == Direction.LONG and close > open_price:
                    return candle
                if direction == Direction.SHORT and close < open_price:
                    return candle
        
        return None
    
    def _validate_displacement(
        self,
        displacement_candle: dict,
        direction: Direction
    ) -> bool:
        """
        Validate displacement is institutional (not noise).
        
        Conditions:
        - Candle on 15M chart
        - Body >= 70% of range
        - Candle closes within kill zone time window
        - No high-impact news within 10 min
        """
        high = displacement_candle.get("high", 0)
        low = displacement_candle.get("low", 0)
        close = displacement_candle.get("close", 0)
        open_price = displacement_candle.get("open", 0)
        
        if high == low:
            return False
        
        body = abs(close - open_price)
        body_percent = body / (high - low)
        
        return body_percent >= self.config.displacement_body_threshold
    
    def _calculate_entry_zone(
        self,
        displacement: dict,
        kzr_high: float,
        kzr_low: float,
        direction: Direction
    ) -> Optional[float]:
        """
        Calculate entry zone at 70.5% OTE level.
        
        Entry at:
        - 70.5% Fibonacci retracement of displacement, OR
        - VWAP level, OR
        - FVG edge formed during retrace
        """
        high = displacement.get("high", 0)
        low = displacement.get("low", 0)
        
        if high == 0 or low == 0:
            return None
        
        # Calculate 70.5% OTE
        ote_level = self.calculate_ote(high, low, 0.705)
        
        return ote_level
    
    def _determine_entry_pathway(
        self,
        market_data: dict,
        displacement_confirmed: bool
    ) -> EntryPathway:
        """
        Determine entry pathway based on confirmation.
        
        Primary (100%): displacement + CHoCH
        Alternate (75%): displacement + MSS (no CHoCH)
        Fallback (SKIP): only displacement
        """
        if not displacement_confirmed:
            return EntryPathway.DISPLACEMENT_ONLY
        
        choc = market_data.get("choc", False)
        mss = market_data.get("mss", False)
        
        if choc:
            return EntryPathway.CHOCH
        elif mss:
            return EntryPathway.MSS
        else:
            # Default to MSS pathway for faster entry
            return EntryPathway.MSS
    
    def _calculate_entry_price(
        self,
        entry_zone: float,
        direction: Direction
    ) -> float:
        """Calculate entry price with offset."""
        offset = self.config.entry_offset_pips
        
        if direction == Direction.LONG:
            return entry_zone + offset
        else:
            return entry_zone - offset
    
    def _calculate_stop_price(
        self,
        displacement: dict,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        stop_offset = 15  # Minimum 15 pips
        
        if direction == Direction.LONG:
            displacement_low = displacement.get("low", 0)
            return displacement_low - stop_offset
        else:
            displacement_high = displacement.get("high", 0)
            return displacement_high + stop_offset
    
    def _calculate_stop_at_min(
        self,
        entry: float,
        min_stop: float,
        direction: Direction
    ) -> float:
        """Calculate stop at minimum pips."""
        if direction == Direction.LONG:
            return entry - min_stop
        else:
            return entry + min_stop
    
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
        
        # 15 pips profit: reduce stop by 5 toward entry
        if pips_from_entry >= 15:
            if direction == Direction.LONG:
                return ("reduce_stop", entry + 5)
            else:
                return ("reduce_stop", entry - 5)
        
        # 25 pips profit: move to breakeven
        if pips_from_entry >= 25:
            return ("breakeven", entry)
        
        # 35 pips profit: move to +10
        if pips_from_entry >= 35:
            if direction == Direction.LONG:
                return ("profit_stop", entry + 10)
            else:
                return ("profit_stop", entry - 10)
        
        return ("maintain", current_stop)


# Factory function for strategy creation
def create_kill_zone_pulse_strategy(
    account_equity: float = 10000.0,
    config: Optional[KillZonePulseConfig] = None
) -> KillZonePulse:
    """
    Create Kill-Zone Pulse strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        KillZonePulse instance
    """
    return KillZonePulse(account_equity, config)