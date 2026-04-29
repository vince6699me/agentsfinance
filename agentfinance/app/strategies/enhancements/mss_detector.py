"""
Market Structure Shift (MSS) Detector Module

Implements ICT v2 MSS distinction from CHoCH:
- MSS does NOT require prior BOS (distinct from CHoCH)
- Faster entries, shorter holds
- 75% position size vs CHoCH's 100%
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


class StructureType(IntEnum):
    """Market structure types"""
    MSS = 1       # Market Structure Shift - no prior BOS required
    CHoCH = 2     # Change of Character - requires prior BOS
    BOS = 3       # Break of Structure - momentum continuation
    CONSOLIDATION = 4  # No clear structure


@dataclass
class StructureSignal:
    """Detected market structure signal"""
    signal_type: StructureType
    direction: str  # "bullish" or "bearish"
    timestamp: datetime
    price_level: float
    
    # Context
    has_prior_bos: bool = False
    confidence: float = 0.0
    
    # For CHoCH specifically
    bos_price: Optional[float] = None
    bos_timestamp: Optional[datetime] = None
    
    # Entry recommendations
    recommended_position_size: float = 1.0
    expected_hold_time: str = ""  # "short", "medium", "long"


@dataclass
class LiquidityZone:
    """Liquidity zone for MSS detection"""
    zone_type: str  # "demand" or "supply"
    zone_high: float
    zone_low: float
    strength: float = 0.0  # 0.0 to 1.0


class MSSDetector:
    """
    Market Structure Shift Detector
    
    Distinguishes between MSS and CHoCH:
    - MSS: Does NOT require prior BOS, faster entries
    - CHoCH: Requires prior BOS, more confirmation
    
    Position sizing:
    - MSS: 75% of normal position (faster, shorter holds)
    - CHoCH: 100% of normal position (more confirmation)
    """
    
    # Position size multipliers
    MSS_POSITION_MULTIPLIER = 0.75
    CHOCH_POSITION_MULTIPLIER = 1.0
    
    # Confidence thresholds
    MSS_MIN_CONFIDENCE = 0.70
    CHOCH_MIN_CONFIDENCE = 0.75
    
    @staticmethod
    def detect_structure(
        price: float,
        liquidity_zones: List[LiquidityZone],
        prior_bos: Optional[Dict[str, Any]] = None,
        recent_structure: List[Dict[str, Any]] = None
    ) -> StructureSignal:
        """
        Detect market structure type (MSS vs CHoCH).
        
        Args:
            price: Current price
            liquidity_zones: List of liquidity zones
            prior_bos: Prior BOS information (if any)
            recent_structure: Recent price structure data
            
        Returns:
            StructureSignal with type and recommendations
        """
        # Check if price is at extreme (below demand or above supply)
        at_demand_extreme = False
        at_supply_extreme = False
        
        for zone in liquidity_zones:
            if zone.zone_type == "demand":
                if price <= zone.zone_low:
                    at_demand_extreme = True
            elif zone.zone_type == "supply":
                if price >= zone.zone_high:
                    at_supply_extreme = True
        
        # Determine if this is MSS or CHoCH
        if prior_bos is None or not prior_bos.get("occurred", False):
            # No prior BOS - this is MSS
            if at_demand_extreme:
                return MSSDetector._create_mss_signal(
                    direction="bullish",
                    price=price,
                    has_prior_bos=False
                )
            elif at_supply_extreme:
                return MSSDetector._create_mss_signal(
                    direction="bearish",
                    price=price,
                    has_prior_bos=False
                )
        else:
            # Has prior BOS - check for CHoCH
            if at_demand_extreme:
                return MSSDetector._create_choch_signal(
                    direction="bullish",
                    price=price,
                    prior_bos=prior_bos
                )
            elif at_supply_extreme:
                return MSSDetector._create_choch_signal(
                    direction="bearish",
                    price=price,
                    prior_bos=prior_bos
                )
        
        # No clear structure signal
        return StructureSignal(
            signal_type=StructureType.CONSOLIDATION,
            direction="neutral",
            timestamp=datetime.now(),
            price_level=price,
            confidence=0.0
        )
    
    @staticmethod
    def _create_mss_signal(
        direction: str,
        price: float,
        has_prior_bos: bool
    ) -> StructureSignal:
        """Create MSS signal"""
        confidence = 0.75 if direction == "bullish" else 0.75
        
        return StructureSignal(
            signal_type=StructureType.MSS,
            direction=direction,
            timestamp=datetime.now(),
            price_level=price,
            has_prior_bos=has_prior_bos,
            confidence=confidence,
            recommended_position_size=MSSDetector.MSS_POSITION_MULTIPLIER,
            expected_hold_time="short"  # MSS = faster, shorter holds
        )
    
    @staticmethod
    def _create_choch_signal(
        direction: str,
        price: float,
        prior_bos: Dict[str, Any]
    ) -> StructureSignal:
        """Create CHoCH signal"""
        confidence = 0.85 if direction == "bullish" else 0.85
        
        return StructureSignal(
            signal_type=StructureType.CHoCH,
            direction=direction,
            timestamp=datetime.now(),
            price_level=price,
            has_prior_bos=True,
            confidence=confidence,
            bos_price=prior_bos.get("price"),
            bos_timestamp=prior_bos.get("timestamp"),
            recommended_position_size=MSSDetector.CHOCH_POSITION_MULTIPLIER,
            expected_hold_time="medium"  # CHoCH = more confirmation, longer holds
        )
    
    @staticmethod
    def is_valid_mss(
        price: float,
        demand_zone: LiquidityZone,
        min_strength: float = 0.6
    ) -> bool:
        """
        Validate if MSS signal is strong enough.
        
        Args:
            price: Current price
            demand_zone: Demand zone to check against
            min_strength: Minimum zone strength (default 0.6)
            
        Returns:
            True if MSS is valid
        """
        if demand_zone.strength < min_strength:
            return False
        
        # Price must be at or below demand zone
        return price <= demand_zone.zone_low
    
    @staticmethod
    def is_valid_choch(
        price: float,
        supply_zone: LiquidityZone,
        prior_bos: Dict[str, Any],
        min_bos_distance_pips: float = 20.0
    ) -> bool:
        """
        Validate if CHoCH signal is strong enough.
        
        Args:
            price: Current price
            supply_zone: Supply zone to check against
            prior_bos: Prior BOS information
            min_bos_distance: Minimum distance from BOS (pips)
            
        Returns:
            True if CHoCH is valid
        """
        if not prior_bos.get("occurred", False):
            return False
        
        # Check BOS distance
        bos_price = prior_bos.get("price", 0)
        if bos_price > 0:
            distance = abs(price - bos_price)
            if distance < min_bos_distance_pips:
                return False
        
        # Price must be at or above supply zone
        return price >= supply_zone.zone_high
    
    @staticmethod
    def get_position_size(signal: StructureSignal) -> float:
        """
        Get recommended position size based on signal type.
        
        Args:
            signal: The structure signal
            
        Returns:
            Position size multiplier
        """
        if signal.signal_type == StructureType.MSS:
            return MSSDetector.MSS_POSITION_MULTIPLIER
        elif signal.signal_type == StructureType.CHoCH:
            return MSSDetector.CHOCH_POSITION_MULTIPLIER
        return 0.0
    
    @staticmethod
    def compare_signals(
        mss_signal: StructureSignal,
        choch_signal: StructureSignal
    ) -> Dict[str, Any]:
        """
        Compare MSS and CHoCH signals for decision making.
        
        Args:
            mss_signal: MSS signal
            choch_signal: CHoCH signal
            
        Returns:
            Dict with comparison and recommendation
        """
        if mss_signal.signal_type == StructureType.CONSOLIDATION and choch_signal.signal_type == StructureType.CONSOLIDATION:
            return {
                "recommendation": "no_entry",
                "reason": "No clear structure detected",
                "prefer_mss": False,
                "prefer_choch": False
            }
        
        # If both available, prefer higher confidence
        if mss_signal.signal_type != StructureType.CONSOLIDATION and choch_signal.signal_type != StructureType.CONSOLIDATION:
            if mss_signal.confidence >= choch_signal.confidence:
                return {
                    "recommendation": "mss",
                    "reason": "MSS has higher confidence",
                    "confidence": mss_signal.confidence,
                    "position_size": mss_signal.recommended_position_size,
                    "expected_hold": mss_signal.expected_hold_time
                }
            else:
                return {
                    "recommendation": "choch",
                    "reason": "CHoCH has higher confidence",
                    "confidence": choch_signal.confidence,
                    "position_size": choch_signal.recommended_position_size,
                    "expected_hold": choch_signal.expected_hold_time
                }
        
        # Only one signal available
        if mss_signal.signal_type != StructureType.CONSOLIDATION:
            return {
                "recommendation": "mss",
                "reason": "MSS signal only available",
                "confidence": mss_signal.confidence,
                "position_size": mss_signal.recommended_position_size,
                "expected_hold": mss_signal.expected_hold_time
            }
        
        if choch_signal.signal_type != StructureType.CONSOLIDATION:
            return {
                "recommendation": "choch",
                "reason": "CHoCH signal only available",
                "confidence": choch_signal.confidence,
                "position_size": choch_signal.recommended_position_size,
                "expected_hold": choch_signal.expected_hold_time
            }
        
        return {
            "recommendation": "no_entry",
            "reason": "No valid signals",
            "prefer_mss": False,
            "prefer_choch": False
        }
    
    @staticmethod
    def get_hold_time_description(signal: StructureSignal) -> str:
        """Get human-readable hold time description"""
        hold_times = {
            "short": "15 min - 2 hours",
            "medium": "2 - 8 hours", 
            "long": "8+ hours"
        }
        return hold_times.get(signal.expected_hold_time, "Unknown")