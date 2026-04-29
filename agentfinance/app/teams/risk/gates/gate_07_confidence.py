"""
AgentFinance v5 - Gate 7: Minimum Confidence Check

Gate 7: Minimum Confidence
Check: Is Fund Manager confidence score >= 65?
Action on Fail: Block if < 65; reduce 30% if 65-75; full if >= 75
"""

from typing import Dict, Any, List, Optional
import logging

from app.teams.risk.pipeline import GateName, GateResult, GateAction
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Gate7Confidence:
    """
    Gate 7: Minimum Confidence Check
    
    Validates the Fund Manager confidence score:
    - Block if confidence < 65
    - Reduce position by 30% if confidence 65-75
    - Full position size if confidence >= 75
    """

    def __init__(self):
        self.gate_name = GateName.GATE_7_CONFIDENCE
        self.min_confidence = settings.min_confidence_threshold  # Default 65
        self.high_confidence = settings.high_confidence_threshold  # Default 80
        self.reduce_threshold = 65
        self.full_size_threshold = 75

    def check(
        self,
        signal_id: int,
        symbol: str,
        direction: str,
        confidence: float,
        strategy_tier: str,
        portfolio_id: int,
        previous_results: List[GateResult],
    ) -> GateResult:
        """
        Check if confidence meets minimum threshold.
        
        Args:
            signal_id: ID of the signal
            symbol: Trading symbol
            direction: Trade direction
            confidence: Fund Manager confidence score (0-100)
            strategy_tier: Strategy tier
            portfolio_id: Portfolio ID
            previous_results: Results from previous gates
            
        Returns:
            GateResult with pass/fail and action
        """
        logger.debug(f"Gate 7: Checking confidence for signal {signal_id}: {confidence}")
        
        # Validate confidence is in valid range
        if confidence < 0 or confidence > 100:
            logger.error(f"Gate 7: Invalid confidence score: {confidence}")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Invalid confidence score: {confidence} (must be 0-100)",
                action=GateAction.BLOCK,
                metadata={"confidence": confidence},
            )
        
        # Check confidence thresholds
        if confidence < self.reduce_threshold:
            logger.warning(f"Gate 7: CONFIDENCE TOO LOW - {confidence} < {self.reduce_threshold}")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Confidence too low: {confidence} (minimum: {self.reduce_threshold})",
                action=GateAction.BLOCK,
                metadata={
                    "confidence": confidence,
                    "threshold": self.reduce_threshold,
                    "action": "blocked",
                },
            )
        
        if confidence < self.full_size_threshold:
            # Confidence between reduce_threshold and full_size_threshold
            logger.info(f"Gate 7: Reduced confidence - applying 30% reduction")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"Confidence acceptable but reduced: {confidence} (position reduced 30%)",
                action=None,
                reduction_factor=0.7,  # 30% reduction
                metadata={
                    "confidence": confidence,
                    "full_size_threshold": self.full_size_threshold,
                    "position_reduced": True,
                    "reduction_percentage": 30,
                },
            )
        
        # Confidence >= full_size_threshold - full position
        logger.info(f"Gate 7: High confidence - full position size: {confidence}")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"High confidence: {confidence} - full position size",
            action=None,
            metadata={
                "confidence": confidence,
                "full_size_threshold": self.full_size_threshold,
                "position_reduced": False,
            },
        )

    def get_confidence_level(self, confidence: float) -> str:
        """
        Get confidence level description.
        
        Args:
            confidence: Confidence score
            
        Returns:
            str: Confidence level ("low", "medium", "high")
        """
        if confidence < self.reduce_threshold:
            return "low"
        elif confidence < self.full_size_threshold:
            return "medium"
        else:
            return "high"

    def calculate_position_multiplier(self, confidence: float) -> float:
        """
        Calculate position size multiplier based on confidence.
        
        Args:
            confidence: Confidence score
            
        Returns:
            float: Position multiplier (0.0 to 1.0)
        """
        if confidence < self.reduce_threshold:
            return 0.0  # Blocked
        elif confidence < self.full_size_threshold:
            return 0.7  # 30% reduction
        else:
            return 1.0  # Full size