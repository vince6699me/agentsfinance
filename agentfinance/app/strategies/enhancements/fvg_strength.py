"""
FVG Strength Ranking Module

Implements ICT v2 FVG Strength Ranking (1-5 scale):
- Strength 1: 3+ consecutive FVGs (FVG cluster) - max conviction
- Strength 2: FVGs formed during displacement - high conviction
- Strength 3: FVGs containing market structure shift - high conviction
- Strength 4: FVGs at order blocks - medium-high
- Strength 5: FVGs at liquidity zones - medium (consider skip)
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


class FVGStrengthRank(IntEnum):
    """FVG Strength Ranking (1 = highest strength)"""
    STRENGTH_1_MAX = 1   # 3+ consecutive FVGs (FVG cluster)
    STRENGTH_2_HIGH = 2  # FVGs formed during displacement
    STRENGTH_3_HIGH = 3  # FVGs containing market structure shift
    STRENGTH_4_MEDIUM = 4  # FVGs at order blocks
    STRENGTH_5_MEDIUM = 5  # FVGs at liquidity zones


@dataclass
class FairValueGap:
    """Represents a Fair Value Gap"""
    id: str
    direction: str  # "bullish" or "bearish"
    zone_high: float
    zone_low: float
    timeframe: str
    created_at: datetime
    
    # Strength factors
    is_in_displacement: bool = False
    contains_structure_shift: bool = False
    is_in_cluster: bool = False
    is_near_order_block: bool = False
    is_near_liquidity: bool = False
    
    # Calculated strength
    strength_rank: Optional[FVGStrengthRank] = None


@dataclass
class FVGStrengthAnalysis:
    """Analysis result for FVG strength"""
    fvg: FairValueGap
    strength: FVGStrengthRank
    confidence: float  # 0.0 to 1.0
    conviction_level: str
    recommendation: str


class FVGStrength:
    """
    FVG Strength Ranking System
    
    Ranks FVGs by institutional conviction:
    - Strength 1-3: High conviction, suitable for entry
    - Strength 4: Medium-high, use with confirmation
    - Strength 5: Medium, consider skip
    """
    
    # Minimum confidence thresholds
    MIN_CONFIDENCE_STRENGTH_1 = 0.90
    MIN_CONFIDENCE_STRENGTH_2 = 0.80
    MIN_CONFIDENCE_STRENGTH_3 = 0.75
    MIN_CONFIDENCE_STRENGTH_4 = 0.60
    
    @staticmethod
    def analyze_fvg(
        fvg: FairValueGap,
        all_fvgs: List[FairValueGap] = None
    ) -> FVGStrengthAnalysis:
        """
        Analyze an FVG and assign strength rank.
        
        Args:
            fvg: The FVG to analyze
            all_fvgs: List of all FVGs for cluster detection
            
        Returns:
            FVGStrengthAnalysis with strength and recommendation
        """
        # Check for cluster (3+ consecutive FVGs)
        is_cluster = False
        if all_fvgs:
            is_cluster = FVGStrength._is_in_cluster(fvg, all_fvgs)
        
        # Calculate strength based on factors
        strength, confidence = FVGStrength._calculate_strength(
            is_in_displacement=fvg.is_in_displacement,
            contains_structure_shift=fvg.contains_structure_shift,
            is_in_cluster=is_cluster or fvg.is_in_cluster,
            is_near_order_block=fvg.is_near_order_block,
            is_near_liquidity=fvg.is_near_liquidity
        )
        
        # Get conviction level
        conviction = FVGStrength._get_conviction_level(strength)
        recommendation = FVGStrength._get_recommendation(strength)
        
        return FVGStrengthAnalysis(
            fvg=fvg,
            strength=strength,
            confidence=confidence,
            conviction_level=conviction,
            recommendation=recommendation
        )
    
    @staticmethod
    def _is_in_cluster(fvg: FairValueGap, all_fvgs: List[FairValueGap]) -> bool:
        """
        Check if FVG is part of a cluster (3+ consecutive FVGs).
        
        Args:
            fvg: The FVG to check
            all_fvgs: All FVGs to analyze
            
        Returns:
            True if FVG is in a cluster of 3+
        """
        # Filter FVGs in same direction and timeframe
        similar_fvgs = [
            f for f in all_fvgs
            if f.direction == fvg.direction
            and f.timeframe == fvg.timeframe
            and f.id != fvg.id
        ]
        
        if len(similar_fvgs) < 2:
            return False
        
        # Sort by creation time
        similar_fvgs.sort(key=lambda x: x.created_at)
        
        # Check for consecutive FVGs within reasonable distance
        cluster_count = 1
        for other_fvg in similar_fvgs:
            # Check if within 50 pips (approximate)
            distance = abs(fvg.zone_low - other_fvg.zone_low)
            if distance < 50:  # 50 pips threshold
                cluster_count += 1
                if cluster_count >= 3:
                    return True
        
        return False
    
    @staticmethod
    def _calculate_strength(
        is_in_displacement: bool,
        contains_structure_shift: bool,
        is_in_cluster: bool,
        is_near_order_block: bool,
        is_near_liquidity: bool
    ) -> tuple[FVGStrengthRank, float]:
        """
        Calculate the strength rank based on factors.
        
        Returns:
            Tuple of (strength, confidence)
        """
        # Strength 1: 3+ consecutive FVGs (FVG cluster) - max conviction
        if is_in_cluster:
            return (FVGStrengthRank.STRENGTH_1_MAX, 0.95)
        
        # Strength 2: FVGs formed during displacement - high conviction
        if is_in_displacement and contains_structure_shift:
            return (FVGStrengthRank.STRENGTH_2_HIGH, 0.85)
        
        # Strength 3: FVGs containing market structure shift - high conviction
        if contains_structure_shift:
            return (FVGStrengthRank.STRENGTH_3_HIGH, 0.80)
        
        # Strength 4: FVGs at order blocks - medium-high
        if is_near_order_block and (is_in_displacement or contains_structure_shift):
            return (FVGStrengthRank.STRENGTH_4_MEDIUM, 0.70)
        
        # Strength 5: FVGs at liquidity zones - medium (consider skip)
        if is_near_liquidity:
            return (FVGStrengthRank.STRENGTH_5_MEDIUM, 0.50)
        
        # Default: standard FVG without strong confluence
        return (FVGStrengthRank.STRENGTH_5_MEDIUM, 0.40)
    
    @staticmethod
    def _get_conviction_level(strength: FVGStrengthRank) -> str:
        """Get conviction level description for the strength."""
        levels = {
            FVGStrengthRank.STRENGTH_1_MAX: "Maximum Conviction",
            FVGStrengthRank.STRENGTH_2_HIGH: "High Conviction",
            FVGStrengthRank.STRENGTH_3_HIGH: "High Conviction",
            FVGStrengthRank.STRENGTH_4_MEDIUM: "Medium-High Conviction",
            FVGStrengthRank.STRENGTH_5_MEDIUM: "Medium Conviction"
        }
        return levels.get(strength, "Unknown")
    
    @staticmethod
    def _get_recommendation(strength: FVGStrengthRank) -> str:
        """Get recommendation text for the strength."""
        recommendations = {
            FVGStrengthRank.STRENGTH_1_MAX: "Maximum conviction - full position size",
            FVGStrengthRank.STRENGTH_2_HIGH: "High conviction - full position size",
            FVGStrengthRank.STRENGTH_3_HIGH: "High conviction - standard position size",
            FVGStrengthRank.STRENGTH_4_MEDIUM: "Medium-high - reduce position size",
            FVGStrengthRank.STRENGTH_5_MEDIUM: "Medium - consider skip or minimal size"
        }
        return recommendations.get(strength, "Unknown strength")
    
    @staticmethod
    def filter_qualified_fvgs(
        fvgs: List[FairValueGap],
        min_strength: FVGStrengthRank = FVGStrengthRank.STRENGTH_3_HIGH
    ) -> List[FVGStrengthAnalysis]:
        """
        Filter FVGs by minimum strength rank.
        
        Args:
            fvgs: List of FVGs to filter
            min_strength: Minimum acceptable strength (default: Strength 3)
            
        Returns:
            List of FVGStrengthAnalysis for qualified FVGs
        """
        qualified = []
        for fvg in fvgs:
            analysis = FVGStrength.analyze_fvg(fvg, fvgs)
            if analysis.strength <= min_strength:
                qualified.append(analysis)
        
        # Sort by strength (highest first)
        qualified.sort(key=lambda x: x.strength)
        return qualified
    
    @staticmethod
    def get_position_size_multiplier(strength: FVGStrengthRank) -> float:
        """
        Get position size multiplier based on FVG strength.
        
        Args:
            strength: The FVG strength rank
            
        Returns:
            Position size multiplier (0.0 to 1.0)
        """
        multipliers = {
            FVGStrengthRank.STRENGTH_1_MAX: 1.0,
            FVGStrengthRank.STRENGTH_2_HIGH: 1.0,
            FVGStrengthRank.STRENGTH_3_HIGH: 0.85,
            FVGStrengthRank.STRENGTH_4_MEDIUM: 0.60,
            FVGStrengthRank.STRENGTH_5_MEDIUM: 0.30
        }
        return multipliers.get(strength, 0.0)