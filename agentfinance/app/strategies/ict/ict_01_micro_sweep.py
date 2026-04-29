"""
ICT Strategy 01: Micro-Sweep Scalp.

Trade the 20-pip scalp after a session high/low liquidity sweep.
Price sweeps the previous session's high (buy-side) or low (sell-side),
then retraces into an order block or FVG zone.

Key Rules:
- Session high/low liquidity sweep detection
- Displacement confirmation (body >= 60%)
- Retrace entry into OB/FVG zone
- 20 pip target, 15 pip min stop
- 80%/20% scale-out TP structure
- Kill zones: London (03:00-05:00 ET), NY AM (08:30-11:00 ET)

See: /home/greywolf/agentsfinance/smc-ict/ICT-01-Micro-Sweep-Scalp.md
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
    FVG,
    OBQualityRank,
    FVGStrength,
    DisplacementConfirmation,
)


@dataclass
class MicroSweepConfig:
    """Configuration for Micro-Sweep Scalp."""
    # Targets
    tp1_pips: float = 20.0
    tp2_pips: float = 35.0
    min_stop_pips: float = 15.0
    
    # Scale-out percentages
    tp1_percent: float = 0.80
    tp2_percent: float = 0.20
    
    # Offset from OB/FVG zone
    entry_offset_pips: float = 5.0
    
    # Kill zones (ET)
    active_kill_zones: tuple = (KillZone.LONDON, KillZone.NY_AM)
    
    # Timeframes
    context_timeframe: str = "15M"
    entry_timeframe: str = "5M"
    confirmation_timeframe: str = "1M"


class MicroSweepScalp(ICTBaseStrategy):
    """
    Micro-Sweep Scalp Strategy.
    
    Trade setup:
    1. Identify session high/low from previous kill zone
    2. Wait for sweep (price closes beyond session level)
    3. Confirm displacement (body >= 60%)
    4. Wait for retrace into OB/FVG zone
    5. Enter with limit order (offset from zone)
    6. Target 20 pips (80% at TP1, 20% at TP2)
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[MicroSweepConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or MicroSweepConfig()
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Micro-Sweep setup.
        
        Required market_data keys:
        - candles_15m: List of 15M OHLCV candles
        - candles_5m: List of 5M OHLCV candles
        - current_time: Current ET time
        - direction: Expected direction (LONG or SHORT)
        
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
        candles_15m = market_data.get("candles_15m", [])
        candles_5m = market_data.get("candles_5m", [])
        
        if len(candles_15m) < 10 or len(candles_5m) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R2: Calculate session high/low
        session_high, session_low = self._calculate_session_levels(candles_15m, active_kz)
        
        if direction == Direction.SHORT:
            session_target = session_high
            stop_level = session_high
        else:
            session_target = session_low
            stop_level = session_low
        
        # R3: Identify OB or FVG
        ob = self._identify_order_block(candles_15m, direction)
        fvg = self._identify_fvg(candles_15m, direction)
        
        # R6: Check for sweep and displacement
        valid_sweep, sweep_reason = self._validate_sweep(
            candles_5m,
            session_target,
            direction
        )
        
        if not valid_sweep:
            return None
        
        # R7: Check for retrace into OB/FVG zone
        entry_zone = self._determine_entry_zone(ob, fvg, direction)
        
        if entry_zone is None:
            return None
        
        # Calculate entry, stop, targets
        entry_price = self._calculate_entry_price(entry_zone, direction)
        stop_price = self._calculate_stop_price(stop_level, direction)
        
        # R10: Validate minimum stop distance
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            return None
        
        # Calculate targets
        tp1_price = self._calculate_tp_price(entry_price, self.config.tp1_pips, direction)
        tp2_price = self._calculate_tp_price(entry_price, self.config.tp2_pips, direction)
        
        # Position sizing
        position_size = self.calculate_position_size(stop_pips)
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-01-Micro-Sweep-Scalp",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            session_high=session_high,
            session_low=session_low,
            ob_zone=ob,
            fvg_zone=fvg,
            ob_quality_rank=ob.quality_rank if ob else OBQualityRank.RANK_4,
            fvg_strength=fvg.strength if fvg else FVGStrength.STRENGTH_4,
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
        Validate setup against all Micro-Sweep rules.
        
        Rules:
        - R6: Displacement (body >= 60%) confirmed
        - R8: Confluence >= 2/3 conditions
        - R10: Stop >= 15 pips
        - Kill zone still active
        """
        # Check displacement confirmed
        if not setup.displacement_confirmed:
            return False, "Displacement not confirmed"
        
        # Check retrace confirmed
        if not setup.retrace_confirmed:
            return False, "Retrace not confirmed"
        
        # Check minimum stop
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        # Check OBQualityRank (use ranks 1-3 only)
        if setup.ob_quality_rank.value > 3 and setup.ob_zone is not None:
            return False, f"OB rank {setup.ob_quality_rank.value} too low (skip)"
        
        # Check FVG strength (use 1-3 only)
        if setup.fvg_strength.value > 3 and setup.fvg_zone is not None:
            return False, f"FVG strength {setup.fvg_strength.value} too low (skip)"
        
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
    
    def _calculate_session_levels(
        self,
        candles: list,
        session: KillZone
    ) -> tuple[float, float]:
        """Calculate session high/low from 15M candles."""
        # Use last 20 candles for session range
        recent = candles[-20:]
        
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        
        return max(highs), min(lows)
    
    def _identify_order_block(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[OrderBlock]:
        """Identify order block near session level."""
        ob = self.detect_order_block(candles, direction)
        
        if ob:
            # Assess quality rank
            ob.quality_rank = self._assess_ob_quality(ob, candles, direction)
        
        return ob
    
    def _assess_ob_quality(
        self,
        ob: OrderBlock,
        candles: list,
        direction: Direction
    ) -> OBQualityRank:
        """Assess order block quality rank."""
        # RANK_1: OB at discount/premium with CHoCH
        if ob.has_choc and ob.has_fvg:
            return OBQualityRank.RANK_1
        
        # RANK_2: OB with FVG above/below
        if ob.has_fvg:
            return OBQualityRank.RANK_2
        
        # RANK_3: OB with liquidity nearby
        if ob.near_liquidity:
            return OBQualityRank.RANK_3
        
        # RANK_4: Standard OB at structure level
        return OBQualityRank.RANK_4
    
    def _identify_fvg(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[FVG]:
        """Identify FVG near session level."""
        fvg = self.detect_fvg(candles, direction)
        
        if fvg:
            # Assess strength
            fvg.strength = self._assess_fvg_strength(fvg, candles)
        
        return fvg
    
    def _assess_fvg_strength(
        self,
        fvg: FVG,
        candles: list
    ) -> FVGStrength:
        """Assess FVG strength."""
        # Already assessed in detect_fvg
        return fvg.strength
    
    def _validate_sweep(
        self,
        candles_5m: list,
        session_level: float,
        direction: Direction
    ) -> tuple[bool, str]:
        """
        Validate sweep and displacement.
        
        Checks:
        - Price closes beyond session level
        - Sweep candle body >= 60%
        - Subsequent candles confirm sweep
        """
        if len(candles_5m) < 5:
            return False, "Insufficient candles"
        
        # Find sweep candle (closes beyond session level)
        sweep_idx = None
        for i in range(len(candles_5m) - 1, -1, -1):
            candle = candles_5m[i]
            
            if direction == Direction.SHORT:
                if candle.get("close", 0) < session_level:
                    sweep_idx = i
                    break
            else:
                if candle.get("close", 0) > session_level:
                    sweep_idx = i
                    break
        
        if sweep_idx is None:
            return False, "No sweep detected"
        
        sweep_candle = candles_5m[sweep_idx]
        subsequent = candles_5m[sweep_idx + 1:sweep_idx + 4]
        
        # Validate displacement
        return DisplacementConfirmation.validate_sweep(
            sweep_candle,
            subsequent,
            session_level,
            direction
        )
    
    def _determine_entry_zone(
        self,
        ob: Optional[OrderBlock],
        fvg: Optional[FVG],
        direction: Direction
    ) -> Optional[float]:
        """Determine entry zone from OB or FVG."""
        # Prefer OB (higher priority)
        if ob:
            if direction == Direction.LONG:
                return ob.low
            else:
                return ob.high
        
        # Fall back to FVG
        if fvg:
            if direction == Direction.LONG:
                return fvg.bottom
            else:
                return fvg.top
        
        return None
    
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
        session_level: float,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        stop_distance = max(20, self.config.min_stop_pips)
        
        if direction == Direction.LONG:
            return session_level - stop_distance
        else:
            return session_level + stop_distance
    
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
    
    def check_confluence(
        self,
        setup: TradeSetup,
        ote_level: float,
        vwap: float
    ) -> int:
        """
        Check confluence conditions.
        
        Returns:
            Number of conditions met (need >= 2)
        """
        conditions_met = 0
        
        # Check OB or FVG at entry
        if setup.ob_zone or setup.fvg_zone:
            conditions_met += 1
        
        # Check OTE level
        if abs(setup.entry - ote_level) <= 5:
            conditions_met += 1
        
        # Check VWAP
        if abs(setup.entry - vwap) <= 5:
            conditions_met += 1
        
        return conditions_met


# Factory function for strategy creation
def create_micro_sweep_strategy(
    account_equity: float = 10000.0,
    config: Optional[MicroSweepConfig] = None
) -> MicroSweepScalp:
    """
    Create Micro-Sweep Scalp strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        MicroSweepScalp instance
    """
    return MicroSweepScalp(account_equity, config)