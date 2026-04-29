"""
4-Tier Take Profit Structure Module

Implements ICT v2 4-tier TP structure:
- TP1: 1R - Break even
- TP2: 1.5R-2R - Partial exit 50%
- TP3: 3R - Trailing stop activated
- TP4: Structure extreme - Full exit
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class TPTier(IntEnum):
    """Take Profit Tiers"""
    TP1 = 1  # 1R - Break even
    TP2 = 2  # 1.5R-2R - Partial exit 50%
    TP3 = 3  # 3R - Trailing stop activated
    TP4 = 4  # Structure extreme - Full exit


@dataclass
class TPTarget:
    """Individual Take Profit Target"""
    tier: TPTier
    r_multiple: float
    price: float
    position_percentage: float  # % of position to close
    is_active: bool = True
    is_hit: bool = False


@dataclass
class TPStructure:
    """
    4-Tier Take Profit Structure
    
    Manages multiple take profit levels with position sizing:
    - TP1 (1R): Move stop to break even
    - TP2 (1.5R-2R): Close 50% of position
    - TP3 (3R): Activate trailing stop, close remaining
    - TP4 (Structure extreme): Final exit
    """
    
    entry_price: float
    stop_loss: float
    direction: str  # "bullish" or "bearish"
    
    # Calculated targets
    tp1: Optional[TPTarget] = None
    tp2: Optional[TPTarget] = None
    tp3: Optional[TPTarget] = None
    tp4: Optional[TPTarget] = None
    
    # Risk calculation
    risk_amount: float = 0.0
    risk_pips: float = 0.0
    
    @staticmethod
    def create(
        entry_price: float,
        stop_loss: float,
        direction: str,
        position_size: float = 1.0
    ) -> 'TPStructure':
        """
        Create a new TP structure.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            direction: "bullish" or "bearish"
            position_size: Position size multiplier (default 1.0)
            
        Returns:
            TPStructure with all TP levels calculated
        """
        tp = TPStructure(
            entry_price=entry_price,
            stop_loss=stop_loss,
            direction=direction
        )
        
        # Calculate risk in pips and amount
        tp.risk_pips = abs(entry_price - stop_loss)
        
        # Calculate TP levels based on direction
        if direction == "bullish":
            # Bullish: TPs are above entry
            tp.tp1 = TPTarget(
                tier=TPTier.TP1,
                r_multiple=1.0,
                price=entry_price,  # Break even
                position_percentage=0  # Just move SL to BE
            )
            tp.tp2 = TPTarget(
                tier=TPTier.TP2,
                r_multiple=1.75,  # Average of 1.5-2R
                price=entry_price + (tp.risk_pips * 1.75),
                position_percentage=50  # Close 50%
            )
            tp.tp3 = TPTarget(
                tier=TPTier.TP3,
                r_multiple=3.0,
                price=entry_price + (tp.risk_pips * 3.0),
                position_percentage=30  # Close 30% more
            )
            tp.tp4 = TPTarget(
                tier=TPTier.TP4,
                r_multiple=5.0,  # Will be adjusted to structure extreme
                price=entry_price + (tp.risk_pips * 5.0),
                position_percentage=20  # Final 20%
            )
        else:
            # Bearish: TPs are below entry
            tp.tp1 = TPTarget(
                tier=TPTier.TP1,
                r_multiple=1.0,
                price=entry_price,  # Break even
                position_percentage=0
            )
            tp.tp2 = TPTarget(
                tier=TPTier.TP2,
                r_multiple=1.75,
                price=entry_price - (tp.risk_pips * 1.75),
                position_percentage=50
            )
            tp.tp3 = TPTarget(
                tier=TPTier.TP3,
                r_multiple=3.0,
                price=entry_price - (tp.risk_pips * 3.0),
                position_percentage=30
            )
            tp.tp4 = TPTarget(
                tier=TPTier.TP4,
                r_multiple=5.0,
                price=entry_price - (tp.risk_pips * 5.0),
                position_percentage=20
            )
        
        return tp
    
    def update_tp4_to_structure_extreme(
        self,
        structure_extreme: float,
        min_r: float = 4.0,
        max_r: float = 8.0
    ) -> None:
        """
        Update TP4 to structure extreme with R constraints.
        
        Args:
            structure_extreme: Price of structure extreme (high/low)
            min_r: Minimum R multiple (default 4R)
            max_r: Maximum R multiple (default 8R)
        """
        if self.direction == "bullish":
            # For bullish, structure extreme should be above entry
            potential_r = (structure_extreme - self.entry_price) / self.risk_pips
            # Constrain to min/max R
            constrained_r = max(min_r, min(max_r, potential_r))
            self.tp4 = TPTarget(
                tier=TPTier.TP4,
                r_multiple=constrained_r,
                price=structure_extreme,
                position_percentage=20
            )
        else:
            # For bearish, structure extreme should be below entry
            potential_r = (self.entry_price - structure_extreme) / self.risk_pips
            constrained_r = max(min_r, min(max_r, potential_r))
            self.tp4 = TPTarget(
                tier=TPTier.TP4,
                r_multiple=constrained_r,
                price=structure_extreme,
                position_percentage=20
            )
    
    def check_tp_hit(self, current_price: float) -> List[TPTarget]:
        """
        Check which TP levels have been hit.
        
        Args:
            current_price: Current market price
            
        Returns:
            List of TP targets that have been hit
        """
        hit_targets = []
        
        targets = [self.tp1, self.tp2, self.tp3, self.tp4]
        
        for target in targets:
            if target and target.is_active and not target.is_hit:
                if self.direction == "bullish":
                    if current_price >= target.price:
                        target.is_hit = True
                        hit_targets.append(target)
                else:
                    if current_price <= target.price:
                        target.is_hit = True
                        hit_targets.append(target)
        
        return hit_targets
    
    def get_active_tps(self) -> List[TPTarget]:
        """Get list of active (not hit) TP targets."""
        active = []
        for target in [self.tp1, self.tp2, self.tp3, self.tp4]:
            if target and target.is_active and not target.is_hit:
                active.append(target)
        return active
    
    def get_trailing_stop_price(self, current_price: float) -> Optional[float]:
        """
        Calculate trailing stop price after TP3 is hit.
        
        Args:
            current_price: Current market price
            
        Returns:
            Trailing stop price or None if TP3 not hit
        """
        if self.tp3 and self.tp3.is_hit:
            # Trail by 50% of distance from entry to TP3
            if self.direction == "bullish":
                trail_distance = (self.tp3.price - self.entry_price) * 0.5
                return current_price - trail_distance
            else:
                trail_distance = (self.entry_price - self.tp3.price) * 0.5
                return current_price + trail_distance
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of TP structure."""
        return {
            "entry": self.entry_price,
            "stop_loss": self.stop_loss,
            "risk_pips": self.risk_pips,
            "tp1": {
                "tier": "TP1",
                "r_multiple": self.tp1.r_multiple if self.tp1 else None,
                "price": self.tp1.price if self.tp1 else None,
                "action": "Move SL to break even"
            },
            "tp2": {
                "tier": "TP2",
                "r_multiple": self.tp2.r_multiple if self.tp2 else None,
                "price": self.tp2.price if self.tp2 else None,
                "action": "Close 50% position"
            },
            "tp3": {
                "tier": "TP3",
                "r_multiple": self.tp3.r_multiple if self.tp3 else None,
                "price": self.tp3.price if self.tp3 else None,
                "action": "Activate trailing, close 30%"
            },
            "tp4": {
                "tier": "TP4",
                "r_multiple": self.tp4.r_multiple if self.tp4 else None,
                "price": self.tp4.price if self.tp4 else None,
                "action": "Full exit at structure extreme"
            }
        }
    
    def calculate_position_exit(
        self,
        current_price: float,
        original_position: float
    ) -> Dict[str, float]:
        """
        Calculate remaining position after TP hits.
        
        Args:
            current_price: Current market price
            original_position: Original position size
            
        Returns:
            Dict with remaining position and closed amounts
        """
        closed_amount = 0.0
        remaining = original_position
        
        for target in [self.tp2, self.tp3, self.tp4]:
            if target and target.is_hit:
                closed_amount += original_position * (target.position_percentage / 100)
        
        remaining = original_position - closed_amount
        
        return {
            "original": original_position,
            "closed": closed_amount,
            "remaining": remaining,
            "closed_percentage": (closed_amount / original_position) * 100 if original_position > 0 else 0
        }