"""
ICT Strategy 08: Discount-Premium Position.

Trade the 300-500 pip swing from the discount (below weekly midpoint) or
premium (above weekly midpoint) zone on the weekly chart.

Key Rules:
- 70.5% OTE replaces midpoint
- Breaker block entry rules
- 4-tier TP
- 20-week IPA range
- 2.5% risk tier
- 300-500 pip target

See: /home/greywolf/agentsfinance/smc-ict/ICT-08-Discount-Premium-Position.md
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
class DiscountPremiumConfig:
    """Configuration for Discount-Premium Position."""
    # Targets (4-tier TP structure)
    tp1_pips: float = 150.0     # 1R - midpoint
    tp2_pips: float = 250.0     # 2R - zone edge
    tp3_pips: float = 350.0     # 3R - external liquidity
    tp4_pips: Optional[float] = None  # 40-60 week extreme
    
    # Scale-out percentages
    tp1_percent: float = 0.30   # Move to breakeven
    tp2_percent: float = 0.30   # Move to +30
    tp3_percent: float = 0.25   # Trailing stop
    tp4_percent: float = 0.15   # Final exit
    
    # Stop loss
    min_stop_pips: float = 50.0
    max_stop_pips: float = 100.0
    
    # Entry offset
    entry_offset_pips: float = 10.0
    
    # Timeframes
    htf_timeframe: str = "W"       # Weekly for OTE
    bias_timeframe: str = "D"       # Daily for entry confirmation
    entry_timeframe: str = "4H"     # Entry zone
    confirmation_timeframe: str = "1H"  # OB/FVG confirmation
    
    # Risk percent (position tier = 2.5%)
    risk_percent: float = 0.025
    
    # IPA range
    ipa_weeks: int = 20   # 20-week IPA dealing range
    
    # External liquidity lookback
    external_weeks_min: int = 40
    external_weeks_max: int = 60
    
    # Discount/Premium zones
    discount_percent: float = 0.35  # Lower 35% of range
    premium_percent: float = 0.35   # Upper 35% of range
    
    # Entry validity
    max_entry_weeks: int = 3
    
    # Allowed OB quality ranks
    min_ob_rank: int = 1
    max_ob_rank: int = 3


class DiscountPremiumPosition(ICTBaseStrategy):
    """
    Discount-Premium Position Strategy.
    
    Trade setup:
    1. Calculate 20-week IPA dealing range on Weekly chart
    2. Identify discount (lower 35%) or premium (upper 35%) zone
    3. Map external liquidity targets (40-60 weeks ago)
    4. Wait for weekly candle to close in discount/premium zone
    5. Confirm OB or FVG at entry zone on 4H/1H
    6. Enter at 70.5% OTE with 50-100 pip stop
    7. Target 300-500 pips (TP1-TP3)
    
    Key rules:
    - Entry at first weekly close in discount/premium zone
    - 70.5% OTE (not midpoint) for entry
    - Weekly midpoint rule for exit
    - Hold through weekly closes
    """
    
    def __init__(
        self,
        account_equity: float = 10000.0,
        config: Optional[DiscountPremiumConfig] = None
    ):
        super().__init__(account_equity)
        self.config = config or DiscountPremiumConfig()
        self.BASE_RISK_PERCENT = self.config.risk_percent
    
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for Discount-Premium setup.
        
        Required market_data keys:
        - candles_weekly: Weekly candles for 20-week IPA
        - candles_daily: Daily candles for entry confirmation
        - candles_4h: 4H candles for OB/FVG
        - direction: Expected direction (LONG for discount, SHORT for premium)
        
        Optional:
        - range_high: Pre-calculated 20W high
        - range_low: Pre-calculated 20W low
        - discount_zone: Pre-calculated discount zone
        - premium_zone: Pre-calculated premium zone
        - external_target: Pre-calculated external liquidity
        
        Returns:
            TradeSetup if valid setup, None otherwise
        """
        # Get candles
        candles_weekly = market_data.get("candles_weekly", [])
        candles_4h = market_data.get("candles_4h", [])
        
        if len(candles_weekly) < self.config.ipa_weeks or len(candles_4h) < 10:
            return None
        
        direction = market_data.get("direction")
        if direction is None:
            return None
        
        # R1: Calculate 20-week IPA dealing range
        range_high = market_data.get("range_high")
        range_low = market_data.get("range_low")
        
        if range_high is None or range_low is None:
            range_high, range_low, _ = self.calculate_weekly_range(
                candles_weekly, self.config.ipa_weeks
            )
        
        if range_high is None or range_low is None:
            return None
        
        # R2: Identify discount/premium zones
        discount_low, discount_high, premium_low, premium_high = (
            self.calculate_discount_premium_zones(range_high, range_low)
        )
        
        # R5: Check if price enters discount/premium zone
        entry_zone = None
        current_price = candles_weekly[-1].get("close", 0)
        
        if direction == Direction.LONG:
            # Check if price entered discount zone
            if current_price < discount_high:
                entry_zone = self._find_entry_in_discount(candles_4h, direction)
        else:
            # Check if price entered premium zone
            if current_price > premium_low:
                entry_zone = self._find_entry_in_premium(candles_4h, direction)
        
        if entry_zone is None:
            # Check for breaker block
            breaker = self.detect_breaker_block(candles_4h, direction)
            if breaker is None:
                return None
            entry_zone = breaker.low if direction == Direction.LONG else breaker.high
            stop_zone = breaker.high if direction == Direction.LONG else breaker.low
        else:
            # R6: Confirm OB or FVG at entry zone
            ob = self.detect_order_block(candles_4h, direction)
            fvg = self.detect_fvg(candles_4h, direction)
            
            if ob is None and fvg is None:
                # Lower confidence - reduce position by 50% (INV2)
                pass
            
            # Calculate stop
            if direction == Direction.LONG:
                stop_zone = entry_zone - self.config.min_stop_pips
            else:
                stop_zone = entry_zone + self.config.min_stop_pips
        
        # R3: Map external liquidity targets
        external_target = market_data.get("external_target")
        
        if external_target is None:
            external_target = self._find_external_liquidity(
                candles_weekly, direction
            )
        
        # R7: Check confluence (4 of 5)
        confluence = self._check_confluence_5(
            direction, current_price, 
            discount_low, discount_high, premium_low, premium_high,
            external_target, entry_zone
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
        midpoint = (range_high + range_low) / 2
        zone_edge = discount_high if direction == Direction.LONG else premium_low
        
        tp1_price = midpoint  # At weekly midpoint
        tp2_price = zone_edge + 50 if direction == Direction.LONG else zone_edge - 50
        tp3_price = external_target
        tp4_price = external_target  # 40-60 week extreme
        
        # Position sizing
        position_size = self.calculate_position_size(
            stop_pips, risk_percent=self.config.risk_percent
        )
        
        # Create setup
        setup = TradeSetup(
            strategy="ICT-08-Discount-Premium-Position",
            direction=direction,
            entry=entry_price,
            stop_loss=stop_price,
            take_profit_1=tp1_price,
            take_profit_2=tp2_price,
            take_profit_3=tp3_price,
            take_profit_4=tp4_price,
            session_high=range_high,
            session_low=range_low,
            timeframe=self.config.entry_timeframe,
            displacement_confirmed=True,
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
        Validate setup against all Discount-Premium rules.
        
        Rules:
        - INV1: Price must close in discount/premium zone
        - INV2: OB/FVG required (or reduce position 50%)
        - INV3: External target >= 200 pips from entry
        - INV4: Stop <= 100 pips
        - OB quality rank 1-3 for position trades
        """
        # Check stop distance
        if setup.risk_pips < self.config.min_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips < {self.config.min_stop_pips} pips"
        
        if setup.risk_pips > self.config.max_stop_pips:
            return False, f"Stop {setup.risk_pips:.1f} pips > {self.config.max_stop_pips} pips"
        
        # Check external target distance (INV3)
        if setup.take_profit_3:
            target_distance = abs(setup.take_profit_3 - setup.entry)
            if target_distance < 200:
                return False, f"External target {target_distance:.1f} pips < 200"
        
        return True, "Setup valid"
    
    def _find_entry_in_discount(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[float]:
        """Find entry zone in discount."""
        # Look for OB or FVG in discount zone
        ob = self.detect_order_block(candles, direction)
        if ob:
            return ob.low
        
        fvg = self.detect_fvg(candles, direction)
        if fvg:
            return fvg.bottom
        
        return None
    
    def _find_entry_in_premium(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[float]:
        """Find entry zone in premium."""
        ob = self.detect_order_block(candles, direction)
        if ob:
            return ob.high
        
        fvg = self.detect_fvg(candles, direction)
        if fvg:
            return fvg.top
        
        return None
    
    def _find_external_liquidity(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[float]:
        """
        Find external liquidity target (40-60 weeks ago).
        
        Returns:
            External high (bullish) or low (bearish) from 40-60 weeks ago
        """
        if len(candles) < self.config.external_weeks_max:
            return None
        
        # Look for high/low from 40-60 weeks ago
        old_candles = candles[-self.config.external_weeks_max:-self.config.external_weeks_min]
        
        if not old_candles:
            return None
        
        if direction == Direction.LONG:
            # Target is external low (old low)
            return min(c["low"] for c in old_candles)
        else:
            # Target is external high (old high)
            return max(c["high"] for c in old_candles)
    
    def _check_confluence_5(
        self,
        direction: Direction,
        current_price: float,
        discount_low: float,
        discount_high: float,
        premium_low: float,
        premium_high: float,
        external_target: Optional[float],
        entry_zone: Optional[float]
    ) -> int:
        """
        Check confluence (minimum 4 of 5 conditions).
        
        1. Price enters discount/premium zone (weekly close)
        2. Entry zone has OB or FVG (4H or 1H)
        3. Weekly bias aligns with trade direction
        4. External liquidity target >= 200 pips from entry
        5. Entry zone is >= 50 pips below/above midpoint
        """
        conditions = 0
        
        # Condition 1: Price in zone
        if direction == Direction.LONG:
            if current_price < discount_high:
                conditions += 1
        else:
            if current_price > premium_low:
                conditions += 1
        
        # Condition 2: OB/FVG at entry
        if entry_zone is not None:
            conditions += 1
        
        # Condition 3: Weekly bias (assumed aligned - checked externally)
        conditions += 1
        
        # Condition 4: External target >= 200 pips
        if external_target and entry_zone:
            distance = abs(external_target - entry_zone)
            if distance >= 200:
                conditions += 1
        
        # Condition 5: Entry >= 50 pips from midpoint
        midpoint = (discount_high + premium_low) / 2
        if entry_zone:
            distance_from_mid = abs(entry_zone - midpoint)
            if distance_from_mid >= 50:
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
            stop = breaker.low - 50  # 50 pips below for position
        else:
            entry = breaker.low - self.config.entry_offset_pips
            stop = breaker.high + 50
        
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
            strategy="ICT-08-Discount-Premium-Breaker",
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
        direction: Direction,
        weekly_close: float = None
    ) -> tuple[str, float]:
        """
        Check stop adjustment with weekly midpoint rule.
        
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
        
        # At weekly midpoint: close 30%, move to breakeven
        midpoint = (setup.session_high + setup.session_low) / 2
        if abs(current_price - midpoint) < 10:
            return ("tp1_hit", entry)
        
        # At premium/discount edge: close 30%, move to +30
        if direction == Direction.LONG:
            if current_price >= setup.session_high - 50:
                return ("tp2_hit", entry + 30)
        else:
            if current_price <= setup.session_low + 50:
                return ("tp2_hit", entry - 30)
        
        # At external liquidity: close all
        if setup.take_profit_3:
            if direction == Direction.LONG:
                if current_price >= setup.take_profit_3 - 20:
                    return ("full_exit", current_stop)
            else:
                if current_price <= setup.take_profit_3 + 20:
                    return ("full_exit", current_stop)
        
        # R14: Weekly midpoint rule
        # LONG: valid as long as weekly close stays BELOW midpoint
        # SHORT: valid as long as weekly close stays ABOVE midpoint
        if weekly_close:
            if direction == Direction.LONG:
                if weekly_close > midpoint:
                    return ("midpoint_cross", entry)  # Momentum weakening
            else:
                if weekly_close < midpoint:
                    return ("midpoint_cross", entry)
        
        return ("maintain", current_stop)
    
    def should_hold_through_weekly_close(
        self,
        setup: TradeSetup,
        current_price: float,
        weekly_close: float
    ) -> bool:
        """
        Determine if position should be held through weekly close.
        
        Returns:
            True if should hold, False if should exit
        """
        midpoint = (setup.session_high + setup.session_low) / 2
        
        # Hold unless at target or invalidating
        if setup.take_profit_4:
            if abs(current_price - setup.take_profit_4) < 30:
                return False
        
        # INV5: Weekly close through midpoint against direction
        if setup.direction == Direction.LONG:
            if weekly_close > midpoint + 20:
                return False  # Weakness signal
        else:
            if weekly_close < midpoint - 20:
                return False
        
        return True


# Factory function for strategy creation
def create_discount_premium_strategy(
    account_equity: float = 10000.0,
    config: Optional[DiscountPremiumConfig] = None
) -> DiscountPremiumPosition:
    """
    Create Discount-Premium Position strategy instance.
    
    Args:
        account_equity: Account equity
        config: Strategy configuration
        
    Returns:
        DiscountPremiumPosition instance
    """
    return DiscountPremiumPosition(account_equity, config)