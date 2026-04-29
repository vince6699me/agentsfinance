"""
AgentFinance v5 - Portfolio Monitor

Tracks all open positions, calculates net delta per sector,
monitors correlation matrix, and triggers rebalancing alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class PositionInfo:
    """Information about an open position."""
    id: int
    symbol: str
    sector: str
    direction: str
    quantity: float
    entry_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    opened_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SectorExposure:
    """Sector exposure information."""
    sector: str
    total_long: float
    total_short: float
    net_delta: float
    position_count: int


class PortfolioMonitor:
    """
    Portfolio Monitor for tracking open positions and risk metrics.
    
    Responsibilities:
    - Track all open positions
    - Calculate net delta per sector
    - Monitor correlation matrix
    - Trigger rebalancing alerts
    """

    # Sector mapping for common symbols
    SECTOR_MAP = {
        # Forex
        "EURUSD": "forex",
        "GBPUSD": "forex",
        "USDJPY": "forex",
        "USDCHF": "forex",
        "AUDUSD": "forex",
        "USDCAD": "forex",
        "NZDUSD": "forex",
        "EURGBP": "forex",
        "EURJPY": "forex",
        "GBPJPY": "forex",
        # Commodities
        "XAUUSD": "commodities",
        "XAGUSD": "commodities",
        "XTIUSD": "commodities",
        "XBRUSD": "commodities",
        # Indices
        "SPX500": "indices",
        "NAS100": "indices",
        "DJI30": "indices",
        "DAX40": "indices",
        "FTSE100": "indices",
        "N225": "indices",
        # Stocks
        "AAPL": "stocks",
        "TSLA": "stocks",
        "MSFT": "stocks",
        "GOOGL": "stocks",
        "AMZN": "stocks",
        # Crypto
        "BTCUSD": "crypto",
        "ETHUSD": "crypto",
        "BNBUSD": "crypto",
        "SOLUSD": "crypto",
    }

    def __init__(self):
        self.max_concurrent_trades = settings.max_concurrent_trades

    def get_sector(self, symbol: str) -> str:
        """Get sector for a symbol."""
        return self.SECTOR_MAP.get(symbol, "unknown")

    def calculate_sector_exposure(
        self,
        positions: List[PositionInfo],
    ) -> List[SectorExposure]:
        """
        Calculate exposure per sector.
        
        Args:
            positions: List of open positions
            
        Returns:
            List of SectorExposure for each sector
        """
        sector_data: Dict[str, Dict[str, float]] = {}
        
        for pos in positions:
            sector = pos.sector
            
            if sector not in sector_data:
                sector_data[sector] = {
                    "long": 0.0,
                    "short": 0.0,
                    "count": 0,
                }
            
            if pos.direction == "buy":
                sector_data[sector]["long"] += pos.quantity
            else:
                sector_data[sector]["short"] += pos.quantity
            
            sector_data[sector]["count"] += 1
        
        exposures = []
        for sector, data in sector_data.items():
            exposures.append(
                SectorExposure(
                    sector=sector,
                    total_long=data["long"],
                    total_short=data["short"],
                    net_delta=data["long"] - data["short"],
                    position_count=data["count"],
                )
            )
        
        return exposures

    def check_concurrent_limit(self, positions: List[PositionInfo]) -> Dict[str, Any]:
        """
        Check if concurrent position limit is reached.
        
        Args:
            positions: List of open positions
            
        Returns:
            Dict with limit status
        """
        current_count = len(positions)
        limit = self.max_concurrent_trades
        
        return {
            "can_open": current_count < limit,
            "current_positions": current_count,
            "max_positions": limit,
            "remaining_slots": max(0, limit - current_count),
        }

    def calculate_portfolio_delta(self, positions: List[PositionInfo]) -> float:
        """
        Calculate total portfolio delta.
        
        Args:
            positions: List of open positions
            
        Returns:
            Net delta across all positions
        """
        delta = 0.0
        for pos in positions:
            if pos.direction == "buy":
                delta += pos.quantity
            else:
                delta -= pos.quantity
        return delta

    def get_correlation_alerts(
        self,
        new_symbol: str,
        positions: List[PositionInfo],
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Check if new position would create correlation issues.
        
        Args:
            new_symbol: Symbol for new position
            positions: Current open positions
            threshold: Correlation threshold
            
        Returns:
            List of correlation alerts
        """
        alerts = []
        
        # Correlation matrix (simplified)
        correlations = {
            ("EURUSD", "GBPUSD"): 0.85,
            ("EURUSD", "AUDUSD"): 0.65,
            ("EURUSD", "USDJPY"): -0.75,
            ("GBPUSD", "AUDUSD"): 0.70,
            ("XAUUSD", "XTIUSD"): 0.35,
        }
        
        for pos in positions:
            # Check both directions
            corr = correlations.get((new_symbol, pos.symbol)) or correlations.get((pos.symbol, new_symbol))
            
            if corr and abs(corr) > threshold:
                alerts.append({
                    "symbol": new_symbol,
                    "existing_symbol": pos.symbol,
                    "correlation": corr,
                    "threshold": threshold,
                    "action": "reduce" if abs(corr) < 0.85 else "block",
                })
        
        return alerts

    def calculate_margin_requirement(
        self,
        positions: List[PositionInfo],
        leverage: float = 20.0,
    ) -> Dict[str, float]:
        """
        Calculate margin requirement for open positions.
        
        Args:
            positions: List of open positions
            leverage: Account leverage
            
        Returns:
            Dict with margin info
        """
        total_notional = sum(pos.quantity * pos.entry_price for pos in positions)
        margin_required = total_notional / leverage if leverage > 0 else total_notional
        
        return {
            "total_notional": total_notional,
            "leverage": leverage,
            "margin_required": margin_required,
            "position_count": len(positions),
        }

    def get_rebalancing_alerts(
        self,
        positions: List[PositionInfo],
        max_sector_exposure: float = 0.4,
    ) -> List[Dict[str, Any]]:
        """
        Get alerts when sector exposure exceeds limits.
        
        Args:
            positions: List of open positions
            max_sector_exposure: Maximum % of portfolio in single sector
            
        Returns:
            List of rebalancing alerts
        """
        exposures = self.calculate_sector_exposure(positions)
        total_quantity = sum(p.quantity for p in positions)
        
        alerts = []
        
        for exp in exposures:
            if total_quantity > 0:
                exposure_pct = (exp.total_long + exp.total_short) / total_quantity
                
                if exposure_pct > max_sector_exposure:
                    alerts.append({
                        "sector": exp.sector,
                        "exposure_percentage": exposure_pct,
                        "max_allowed": max_sector_exposure,
                        "action": "rebalance",
                        "message": f"Sector {exp.sector} exposure {exposure_pct:.1%} exceeds limit {max_sector_exposure:.1%}",
                    })
        
        return alerts

    def get_portfolio_summary(self, positions: List[PositionInfo]) -> Dict[str, Any]:
        """
        Get complete portfolio summary.
        
        Args:
            positions: List of open positions
            
        Returns:
            Dict with portfolio metrics
        """
        total_pnl = sum(p.pnl or 0 for p in positions)
        total_quantity = sum(p.quantity for p in positions)
        
        return {
            "total_positions": len(positions),
            "total_quantity": total_quantity,
            "total_pnl": total_pnl,
            "sector_exposures": [
                {
                    "sector": e.sector,
                    "net_delta": e.net_delta,
                    "position_count": e.position_count,
                }
                for e in self.calculate_sector_exposure(positions)
            ],
            "concurrent_limit": self.check_concurrent_limit(positions),
            "portfolio_delta": self.calculate_portfolio_delta(positions),
        }