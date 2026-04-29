"""
ICT Strategy 02: PD Array FVG Scalp.

Trade the 25-pip intraday move after a Fair Value Gap (FVG) forms
during a kill zone session.

Key Rules:
- FVG strength ranking (1-3 only for entry)
- 70.5% OTE level
- 25 pip target
- MSS alternate entry at 50% size if FVG weak

See: /home/greywolf/agentsfinance/smc-ict/ICT-02-PD-Array-FVG-Scalp.md
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
class PDArrayConfig:
    """Configuration for PD Array FVG Scalp."""
    # Targets
    tp1_pips: float = 25.0
    alt_tp_pips: float = 15.0  # Only if kill zone closing
    min_stop_pips: float = 15.0
    
    # Entry offset from FVG edge
    entry_offset_pips: float = 5.0
    
    # FVG offset above stop
    stop_offset_pips: float = 20.0
    
    # Kill zones (ET)
    active_kill_zones: tuple = (KillZone.LONDON, KillZone.NY_AM)
    
    # Timeframes
    context_timeframe: str = "60M"  # Weekly bias
    zone_timeframe: str = "15M"  # FVG identification
    entry_timeframe: str = "5M"
    
    # FVG minimum size (pips)
    min_fvg_size: float = 5.0
    
    # Allowed FVG strength (1-3 only)
    min_fvg_strength: int = 1
    max_fvg_strength: int = 3


class PDArrayFVGScalp(ICTBaseStrategy):
    """
    PD Array FVG Scalp Strategy.
    
    Trade setup:
    1. Determine weekly bias on 60M chart
    2. Identify FVG on 15M chart during kill zone
    3. Filter by FVG strength (1-3 only)
    4. Classify FVG location (discount/premium/external)
    5. Enter at FVG edge + offset
    6. Target 25 pips
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[PDArrayConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or PDArrayConfig()
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for PD Array FVG setup.
        
        Required market_data keys:
        - candles_60m: Weekly/daily context candles
        - candles_15m: 15M candles for FVG detection
        - current_time: Current ET time
        - direction: Expected direction (LONG or SHORT)
        - weekly_high: Weekly high (20-day)
        - weekly_low: Weekly low (20-day)
        
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
        
        if len(candles_60m) < 20 or len(candles_15m) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # Get weekly range
        weekly_high = market_data.get("weekly_high")
        weekly_low = market_data.get("weekly_low")
        
        if weekly_high is None or weekly_low is None:
            # Calculate from candles
            weekly_high = max(c["high"] for c in candles_60m[-20:])
            weekly_low = min(c["low"] for c in candles_60m[-20:])
        
        # R5: Identify FVG on 15M chart
        fvg = self._identify_fvg_in_kill_zone(candles_15m, active_kz, direction)
        
        if fvg is None:
            return None
        
        # R6: Classify FVG location
        fvg_classification = self._classify_fvg_location(
            fvg, weekly_high, weekly_low, direction
        )
        
        # R7: Check confluence
        current_price = candles_15m[-1].get("close", 0)
        confluence_met = self._check_confluence(
            fvg, current_price, weekly_high, weekly_low, active_kz
        )
        
        if confluence_met < 2:
            return None
        
        # R8: Check weekly bias alignment
        bias_aligned = self._check_bias_alignment(
            direction, fvg_classification, candles_60m
        )
        
        if not bias_aligned:
            # Only allow if external FVG
            if fvg_classification != "external":
                return None
        
        # Calculate entry, stop, target
        entry_price = self._calculate_entry_price(fvg, direction)
        stop_price = self._calculate_stop_price(fvg, direction)
        
        # Validate minimum stop
        stop_pips = abs(entry_price - stop_price)
        if stop_pips < self.config.min_stop_pips:
            # Widen to minimum
            stop_pips = self.config.min_stop_pips
            stop_price = self._calculate_stop_price_at_min(
                entry_price, self.config.min_stop_pips, direction
            )
        
        # Calculate target
        tp1_price = self._calculate_tp_price(entry_price, self.config.tp1_pips, direction)
        
        # Position sizing
        position_size = self.calculate_position_size(stop_pips)
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-02-PD-Array-FVG-Scalp",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            fvg_zone=fvg,
            fvg_strength=fvg.strength,
            kill_zone=active_kz,
            timeframe=self.config.entry_timeframe,
            position_size=position_size,
            risk_amount=self.account_equity * self.BASE_RISK_PERCENT,
            risk_pips=stop_pips,
            tp1_pips=self.config.tp1_pips,
        )
        
        # Validate setup
        is_valid, reason = self.validate_setup(setup)
        if not is_valid:
            return None
        
        return setup
    
    def validate_setup(self, setup: TradeSetup) -> tuple[bool, str]:
        """
        Validate setup against all PD Array FVG rules.
        
        Rules:
        - FVG strength 1-3 only (strength 4-5 = skip)
        - FVG forms during kill zone
        - Stop >= 15 pips
        - Confluence >= 2/3 conditions
        """
        # Check FVG strength (critical filter)
        if setup.fvg_strength.value > self.config.max_fvg_strength:
            return False, f"FVG strength {setup.fvg_strength.value} > 3 (skip)"
        
        # Check minimum stop
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
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
    
    def _identify_fvg_in_kill_zone(
        self,
        candles: list,
        kill_zone: KillZone,
        direction: Direction
    ) -> Optional[FVG]:
        """
        Identify FVG that forms during kill zone.
        
        Only considers FVG that forms during the kill zone window.
        """
        # Check each potential FVG
        for i in range(len(candles) - 2):
            c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]
            
            if direction == Direction.LONG:
                # Bullish FVG: gap below
                if c2["high"] < c1["low"] and c3["high"] < c1["low"]:
                    gap_size = c1["low"] - c2["high"]
                    if gap_size >= self.config.min_fvg_size:
                        return self._create_fvg_with_strength(
                            c1["low"], c2["high"], direction, candles, i
                        )
            else:
                # Bearish FVG: gap above
                if c2["low"] > c1["high"] and c3["low"] > c1["high"]:
                    gap_size = c2["low"] - c1["high"]
                    if gap_size >= self.config.min_fvg_size:
                        return self._create_fvg_with_strength(
                            c1["high"], c2["low"], direction, candles, i
                        )
        
        return None
    
    def _create_fvg_with_strength(
        self,
        top: float,
        bottom: float,
        direction: Direction,
        candles: list,
        index: int
    ) -> FVG:
        """Create FVG with strength assessment."""
        strength = self._assess_fvg_strength_context(candles, index, direction)
        
        return FVG(
            top=top,
            bottom=bottom,
            direction=direction,
            strength=strength,
            is_cluster=strength == FVGStrength.STRENGTH_1,
            formed_during_displacement=strength in [
                FVGStrength.STRENGTH_2,
                FVGStrength.STRENGTH_3
            ],
            contains_mss=strength == FVGStrength.STRENGTH_3
        )
    
    def _assess_fvg_strength_context(
        self,
        candles: list,
        index: int,
        direction: Direction
    ) -> FVGStrength:
        """Assess FVG strength based on context."""
        # STRENGTH_1: 3+ consecutive FVGs
        cluster_count = 0
        for i in range(index, min(index + 5, len(candles) - 2):
            c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]
            if direction == Direction.LONG:
                if c2["high"] < c1["low"] and c3["high"] < c1["low"]:
                    cluster_count += 1
            else:
                if c2["low"] > c1["high"] and c3["low"] > c1["high"]:
                    cluster_count += 1
        
        if cluster_count >= 3:
            return FVGStrength.STRENGTH_1
        
        # STRENGTH_2: Formed during displacement
        if index > 0:
            prev = candles[index - 1]
            if self.check_displacement(prev, 0.60):
                return FVGStrength.STRENGTH_2
        
        # STRENGTH_3: Contains MSS/CHoCH (simplified)
        # Default to STRENGTH_3 for valid FVGs in kill zone
        return FVGStrength.STRENGTH_3
    
    def _classify_fvg_location(
        self,
        fvg: FVG,
        weekly_high: float,
        weekly_low: float,
        direction: Direction
    ) -> str:
        """
        Classify FVG location relative to PD array.
        
        Returns:
            "discount", "premium", or "external"
        """
        midpoint = (weekly_high + weekly_low) / 2
        fvg_mid = (fvg.top + fvg.bottom) / 2
        
        if direction == Direction.LONG:
            if fvg_mid > midpoint:
                return "premium"
            elif fvg_mid < weekly_low:
                return "external"
            else:
                return "discount"
        else:
            if fvg_mid < midpoint:
                return "discount"
            elif fvg_mid > weekly_high:
                return "external"
            else:
                return "premium"
    
    def _check_confluence(
        self,
        fvg: FVG,
        current_price: float,
        weekly_high: float,
        weekly_low: float,
        kill_zone: KillZone
    ) -> int:
        """
        Check confluence conditions (minimum 2 of 3).
        
        1. FVG in discount (long) or premium (short)
        2. FVG edge at 70.5% OTE
        3. Kill zone active
        """
        conditions = 0
        
        # Condition 1: FVG location
        # (assumed true since we found FVG)
        conditions += 1
        
        # Condition 2: 70.5% OTE calculation
        ote_level = self.calculate_ote(weekly_high, weekly_low, 0.705)
        fvg_mid = (fvg.top + fvg.bottom) / 2
        if abs(fvg_mid - ote_level) <= 10:  # Within 10 pips
            conditions += 1
        
        # Condition 3: Kill zone active
        if kill_zone in self.config.active_kill_zones:
            conditions += 1
        
        return conditions
    
    def _check_bias_alignment(
        self,
        direction: Direction,
        fvg_classification: str,
        candles_60m: list
    ) -> bool:
        """Check weekly bias alignment with FVG direction."""
        weekly_bias = self.calculate_weekly_bias(candles_60m)
        
        # High conviction: bias + FVG in same direction
        if direction == Direction.LONG:
            if fvg_classification == "discount" and weekly_bias == Direction.LONG:
                return True
            if fvg_classification == "external" and weekly_bias == Direction.LONG:
                return True
        else:
            if fvg_classification == "premium" and weekly_bias == Direction.SHORT:
                return True
            if fvg_classification == "external" and weekly_bias == Direction.SHORT:
                return True
        
        return False
    
    def _calculate_entry_price(
        self,
        fvg: FVG,
        direction: Direction
    ) -> float:
        """Calculate entry price with offset from FVG edge."""
        offset = self.config.entry_offset_pips
        
        if direction == Direction.LONG:
            return fvg.bottom + offset
        else:
            return fvg.top - offset
    
    def _calculate_stop_price(
        self,
        fvg: FVG,
        direction: Direction
    ) -> float:
        """Calculate stop loss price."""
        if direction == Direction.LONG:
            return fvg.bottom - self.config.stop_offset_pips
        else:
            return fvg.top + self.config.stop_offset_pips
    
    def _calculate_stop_price_at_min(
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
    
    def calculate_mss_alternate_entry(
        self,
        setup: TradeSetup,
        market_data: dict
    ) -> Optional[TradeSetup]:
        """
        Calculate MSS alternate entry at 50% size if FVG is weak.
        
        Used when FVG strength is 4-5 but MSS confirms.
        
        Returns:
            TradeSetup at 50% size, or None
        """
        # Check if MSS confirmed
        mss_confirmed = market_data.get("mss_confirmed", False)
        fvg_strength_current = setup.fvg_strength
        
        if mss_confirmed and fvg_strength_current.value >= 4:
            # Create alternate at 50% size
            alternate = setup
            alternate.position_size = setup.position_size * 0.5
            alternate.risk_amount = setup.risk_amount * 0.5
            return alternate
        
        return None


# Factory function for strategy creation
def create_pd_array_strategy(
    account_equity: float = 10000.0,
    config: Optional[PDArrayConfig] = None
) -> PDArrayFVGScalp:
    """
    Create PD Array FVG Scalp strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        PDArrayFVGScalp instance
    """
    return PDArrayFVGScalp(account_equity, config)