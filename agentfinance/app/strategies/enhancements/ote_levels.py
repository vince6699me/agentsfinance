"""
Fibonacci OTE Levels Module

Implements ICT v2 Fibonacci Optimal Trade Entry (OTE) levels:
- Primary: 70.5% (ICT's core OTE level)
- Secondary: 61.8%
- Tertiary: 78.6%
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, Tuple
import math


class OTELevel(IntEnum):
    """Fibonacci OTE Levels"""
    PRIMARY = 705    # 70.5% - ICT's core OTE level
    SECONDARY = 618  # 61.8% - Standard Fibonacci
    TERTIARY = 786   # 78.6% - Extended Fib


@dataclass
class OTECalculation:
    """Result of OTE calculation"""
    swing_high: float
    swing_low: float
    level: OTELevel
    ote_price: float
    fib_percentage: float
    is_valid: bool
    invalid_reason: Optional[str] = None


@dataclass
class EntryZone:
    """Entry zone with multiple OTE levels"""
    primary_entry: float      # 70.5%
    secondary_entry: float    # 61.8%
    tertiary_entry: float     # 78.6%
    zone_width: float         # Range between tertiary and primary
    recommended_entry: float  # Best entry based on market conditions


class OTELevels:
    """
    Fibonacci OTE Calculator
    
    Calculates Optimal Trade Entry levels using ICT's specific Fibonacci levels:
    - 70.5% (0.705) is ICT's core OTE - mathematically distinct from 62%
    - 61.8% (0.618) standard Fibonacci retracement
    - 78.6% (0.786) extended Fibonacci level
    """
    
    # OTE percentages as floats
    PRIMARY_PERCENTAGE = 0.705
    SECONDARY_PERCENTAGE = 0.618
    TERTIARY_PERCENTAGE = 0.786
    
    # Valid swing minimum (prevent noise)
    MIN_SWING_SIZE = 50  # pips
    
    @staticmethod
    def calculate_ote(
        swing_high: float,
        swing_low: float,
        direction: str,
        level: OTELevel = OTELevel.PRIMARY
    ) -> OTECalculation:
        """
        Calculate OTE price for a given swing.
        
        Args:
            swing_high: High of the swing
            swing_low: Low of the swing
            direction: "bullish" or "bearish"
            level: OTE level to calculate (default: PRIMARY 70.5%)
            
        Returns:
            OTECalculation with OTE price and details
        """
        # Validate swing
        swing_size = abs(swing_high - swing_low)
        if swing_size < OTELevels.MIN_SWING_SIZE:
            return OTECalculation(
                swing_high=swing_high,
                swing_low=swing_low,
                level=level,
                ote_price=0.0,
                fib_percentage=0.0,
                is_valid=False,
                invalid_reason=f"Swing too small: {swing_size:.1f} pips (min: {OTELevels.MIN_SWING_SIZE})"
            )
        
        if swing_high <= swing_low:
            return OTECalculation(
                swing_high=swing_high,
                swing_low=swing_low,
                level=level,
                ote_price=0.0,
                fib_percentage=0.0,
                is_valid=False,
                invalid_reason="Invalid swing: high must be greater than low"
            )
        
        # Calculate OTE based on direction
        fib_percentage = OTELevels._get_fib_percentage(level)
        
        if direction == "bullish":
            # For bullish: OTE = swing_low + (swing_size * fib_percentage)
            ote_price = swing_low + (swing_size * fib_percentage)
        else:
            # For bearish: OTE = swing_high - (swing_size * fib_percentage)
            ote_price = swing_high - (swing_size * fib_percentage)
        
        return OTECalculation(
            swing_high=swing_high,
            swing_low=swing_low,
            level=level,
            ote_price=ote_price,
            fib_percentage=fib_percentage * 100,
            is_valid=True
        )
    
    @staticmethod
    def calculate_all_levels(
        swing_high: float,
        swing_low: float,
        direction: str
    ) -> EntryZone:
        """
        Calculate all three OTE levels for a swing.
        
        Args:
            swing_high: High of the swing
            swing_low: Low of the swing
            direction: "bullish" or "bearish"
            
        Returns:
            EntryZone with all OTE levels
        """
        primary = OTELevels.calculate_ote(
            swing_high, swing_low, direction, OTELevel.PRIMARY
        )
        secondary = OTELevels.calculate_ote(
            swing_high, swing_low, direction, OTELevel.SECONDARY
        )
        tertiary = OTELevels.calculate_ote(
            swing_high, swing_low, direction, OTELevel.TERTIARY
        )
        
        # Calculate zone width
        if direction == "bullish":
            zone_width = tertiary.ote_price - primary.ote_price
        else:
            zone_width = primary.ote_price - tertiary.ote_price
        
        # Determine recommended entry (70.5% is ICT's core)
        recommended = primary.ote_price
        
        return EntryZone(
            primary_entry=primary.ote_price,
            secondary_entry=secondary.ote_price,
            tertiary_entry=tertiary.ote_price,
            zone_width=zone_width,
            recommended_entry=recommended
        )
    
    @staticmethod
    def get_entry_at_ote(
        current_price: float,
        entry_zone: EntryZone,
        direction: str,
        tolerance_pips: float = 10.0
    ) -> Tuple[bool, str]:
        """
        Check if current price is at OTE entry zone.
        
        Args:
            current_price: Current market price
            entry_zone: Calculated entry zone
            direction: "bullish" or "bearish"
            tolerance_pips: Acceptable deviation in pips
            
        Returns:
            Tuple of (is_at_ote, entry_recommendation)
        """
        if direction == "bullish":
            # For bullish, price should be below entry and approaching
            if current_price <= entry_zone.primary_entry:
                # Check if within tolerance
                distance = entry_zone.primary_entry - current_price
                if distance <= tolerance_pips:
                    return (True, f"At primary OTE 70.5%: {entry_zone.primary_entry:.5f}")
                elif current_price <= entry_zone.tertiary_entry:
                    return (True, f"At extended zone: {current_price:.5f}")
            return (False, f"Price {current_price:.5f} above OTE zone")
        else:
            # For bearish, price should be above entry and approaching
            if current_price >= entry_zone.primary_entry:
                distance = current_price - entry_zone.primary_entry
                if distance <= tolerance_pips:
                    return (True, f"At primary OTE 70.5%: {entry_zone.primary_entry:.5f}")
                elif current_price >= entry_zone.tertiary_entry:
                    return (True, f"At extended zone: {current_price:.5f}")
            return (False, f"Price {current_price:.5f} below OTE zone")
    
    @staticmethod
    def _get_fib_percentage(level: OTELevel) -> float:
        """Get Fibonacci percentage for OTE level."""
        percentages = {
            OTELevel.PRIMARY: OTELevels.PRIMARY_PERCENTAGE,    # 0.705
            OTELevel.SECONDARY: OTELevels.SECONDARY_PERCENTAGE,  # 0.618
            OTELevel.TERTIARY: OTELevels.TERTIARY_PERCENTAGE    # 0.786
        }
        return percentages.get(level, OTELevels.PRIMARY_PERCENTAGE)
    
    @staticmethod
    def is_valid_swing(swing_high: float, swing_low: float) -> bool:
        """
        Validate if swing is large enough for OTE calculation.
        
        Args:
            swing_high: Swing high price
            swing_low: Swing low price
            
        Returns:
            True if swing is valid
        """
        if swing_high <= swing_low:
            return False
        swing_size = abs(swing_high - swing_low)
        return swing_size >= OTELevels.MIN_SWING_SIZE
    
    @staticmethod
    def get_ote_description(level: OTELevel) -> str:
        """Get description of OTE level."""
        descriptions = {
            OTELevel.PRIMARY: "70.5% - ICT's core OTE level (0.618 + 0.087)",
            OTELevel.SECONDARY: "61.8% - Standard Fibonacci retracement",
            OTELevel.TERTIARY: "78.6% - Extended Fibonacci level"
        }
        return descriptions.get(level, "Unknown OTE level")