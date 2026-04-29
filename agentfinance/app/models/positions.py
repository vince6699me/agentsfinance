"""
AgentFinance v5 - Position Model

Represents open positions in portfolios.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Position(Base):
    """
    Position model representing open positions in a portfolio.
    
    Attributes:
        id: Primary key
        portfolio_id: Foreign key to portfolios table
        symbol: Trading symbol (e.g., "EURUSD", "XAUUSD")
        quantity: Position size/units
        entry_price: Entry price
        current_price: Current market price
        pnl: Unrealized P&L
        created_at: Timestamp when position was opened
    """
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)  # Unrealized P&L
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    
    def __repr__(self):
        return f"<Position(id={self.id}, symbol='{self.symbol}', quantity={self.quantity}, pnl={self.pnl})>"
    
    def to_dict(self):
        """Convert position to dictionary."""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "pnl": self.pnl,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def calculate_pnl(self, current_price: float = None) -> float:
        """
        Calculate unrealized P&L.
        
        Args:
            current_price: Current market price (uses current_price if not provided)
            
        Returns:
            float: Unrealized P&L
        """
        price = current_price or self.current_price
        if price:
            return (price - self.entry_price) * self.quantity
        return None