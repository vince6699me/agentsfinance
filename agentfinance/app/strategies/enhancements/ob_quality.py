"""
Order Block Quality Ranking Module

Implements ICT v2 Order Block Quality Ranking (1-5 scale):
- Rank 1: OB at discount/premium with CHoCH (highest)
- Rank 2: OB with FVG above/below (high)
- Rank 3: OB with liquidity nearby (medium)
- Rank 4: Standard OB at structure level (medium)
- Rank 5: OB without confluence (low - skip)
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


class OBQualityRank(IntEnum):
    """Order Block Quality Ranking (1 = highest quality)"""
    RANK_1_HIGHEST = 1  # OB at discount/premium with CHoCH
    RANK_2_HIGH = 2     # OB with FVG above/below
    RANK_3_MEDIUM = 3   # OB with liquidity nearby
    RANK_4_MEDIUM = 4   # Standard OB at structure level
    RANK_5_LOW = 5      # OB without confluence (skip)


@dataclass
class OrderBlock:
    """Represents an Order Block with quality metrics"""
    id: str
    direction: str  # "bullish" or "bearish"
    zone_high: float
    zone_low: float
    timeframe: str
    created_at: datetime
    
    # Quality factors
    has_choch: bool = False
    has_fvg: bool = False
    has_liquidity_nearby: bool = False
    is_at_discount_premium: bool = False
    
    # Calculated rank
    quality_rank: Optional[OBQualityRank] = None


@dataclass
class QualityAnalysis:
    """Analysis result for Order Block quality"""
    order_block: OrderBlock
    rank: OBQualityRank
    confidence: float  # 0.0 to 1.0
    recommendation: str
    skip: bool


class OrderBlockQuality:
    """
    Order Block Quality Ranking System
    
    Ranks order blocks by institutional conviction:
    - Rank 1-2: High probability, suitable for entry
    - Rank 3-4: Medium probability, use with caution
    - Rank 5: Low probability, skip
    """
    
    # Minimum confidence thresholds
    MIN_CONFIDENCE_RANK_1 = 0.90
    MIN_CONFIDENCE_RANK_2 = 0.75
    MIN_CONFIDENCE_RANK_3 = 0.60
    MIN_CONFIDENCE_RANK_4 = 0.45
    
    @staticmethod
    def analyze_ob(
        order_block: OrderBlock,
        current_price: float,
        market_structure: Dict[str, Any]
    ) -> QualityAnalysis:
        """
        Analyze an Order Block and assign quality rank.
        
        Args:
            order_block: The Order Block to analyze
            current_price: Current market price
            market_structure: Dict containing structure info (trend, BOS, etc.)
            
        Returns:
            QualityAnalysis with rank and recommendation
        """
        # Determine if OB is at discount (bullish) or premium (bearish)
        is_discount = order_block.direction == "bullish" and current_price < order_block.zone_low
        is_premium = order_block.direction == "bearish" and current_price > order_block.zone_high
        is_at_discount_premium = is_discount or is_premium
        
        # Calculate rank based on confluence factors
        rank, confidence = OrderBlockQuality._calculate_rank(
            has_choch=order_block.has_choch,
            has_fvg=order_block.has_fvg,
            has_liquidity_nearby=order_block.has_liquidity_nearby,
            is_at_discount_premium=is_at_discount_premium
        )
        
        # Generate recommendation
        recommendation = OrderBlockQuality._get_recommendation(rank)
        skip = rank == OBQualityRank.RANK_5
        
        return QualityAnalysis(
            order_block=order_block,
            rank=rank,
            confidence=confidence,
            recommendation=recommendation,
            skip=skip
        )
    
    @staticmethod
    def _calculate_rank(
        has_choch: bool,
        has_fvg: bool,
        has_liquidity_nearby: bool,
        is_at_discount_premium: bool
    ) -> tuple[OBQualityRank, float]:
        """
        Calculate the quality rank based on confluence factors.
        
        Returns:
            Tuple of (rank, confidence)
        """
        # Rank 1: OB at discount/premium with CHoCH (highest)
        if is_at_discount_premium and has_choch:
            return (OBQualityRank.RANK_1_HIGHEST, 0.95)
        
        # Rank 2: OB with FVG above/below (high)
        if has_fvg and (has_choch or is_at_discount_premium):
            return (OBQualityRank.RANK_2_HIGH, 0.80)
        
        # Rank 3: OB with liquidity nearby (medium)
        if has_liquidity_nearby and (has_fvg or has_choch):
            return (OBQualityRank.RANK_3_MEDIUM, 0.65)
        
        # Rank 4: Standard OB at structure level (medium)
        if has_choch or has_fvg:
            return (OBQualityRank.RANK_4_MEDIUM, 0.50)
        
        # Rank 5: OB without confluence (low - skip)
        return (OBQualityRank.RANK_5_LOW, 0.30)
    
    @staticmethod
    def _get_recommendation(rank: OBQualityRank) -> str:
        """Get recommendation text for the rank."""
        recommendations = {
            OBQualityRank.RANK_1_HIGHEST: "Highest probability entry - full position size",
            OBQualityRank.RANK_2_HIGH: "High probability entry - consider full position",
            OBQualityRank.RANK_3_MEDIUM: "Medium probability - reduce position size",
            OBQualityRank.RANK_4_MEDIUM: "Lower probability - use minimal size or skip",
            OBQualityRank.RANK_5_LOW: "Low probability - skip this setup"
        }
        return recommendations.get(rank, "Unknown rank")
    
    @staticmethod
    def filter_qualified_obs(
        order_blocks: List[OrderBlock],
        current_price: float,
        market_structure: Dict[str, Any],
        min_rank: OBQualityRank = OBQualityRank.RANK_3_MEDIUM
    ) -> List[QualityAnalysis]:
        """
        Filter order blocks by minimum quality rank.
        
        Args:
            order_blocks: List of Order Blocks to filter
            current_price: Current market price
            market_structure: Market structure information
            min_rank: Minimum acceptable rank (default: Rank 3)
            
        Returns:
            List of QualityAnalysis for qualified OBs
        """
        qualified = []
        for ob in order_blocks:
            analysis = OrderBlockQuality.analyze_ob(ob, current_price, market_structure)
            if analysis.rank <= min_rank:
                qualified.append(analysis)
        
        # Sort by rank (highest quality first)
        qualified.sort(key=lambda x: x.rank)
        return qualified
    
    @staticmethod
    def get_position_size_multiplier(rank: OBQualityRank) -> float:
        """
        Get position size multiplier based on OB quality rank.
        
        Args:
            rank: The OB quality rank
            
        Returns:
            Position size multiplier (0.0 to 1.0)
        """
        multipliers = {
            OBQualityRank.RANK_1_HIGHEST: 1.0,
            OBQualityRank.RANK_2_HIGH: 0.85,
            OBQualityRank.RANK_3_MEDIUM: 0.60,
            OBQualityRank.RANK_4_MEDIUM: 0.40,
            OBQualityRank.RANK_5_LOW: 0.0  # Skip
        }
        return multipliers.get(rank, 0.0)