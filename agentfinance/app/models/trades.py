"""
AgentFinance v5 - Trade Model

Represents executed trades in the system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Trade(Base):
    """
    Trade model representing executed trades.
    
    Attributes:
        id: Primary key
        signal_id: Foreign key to signals table
        direction: Trade direction (buy, sell)
        entry_price: Entry price
        exit_price: Exit price (null if still open)
        stop_loss: Stop loss price
        take_profit: Take profit price
        status: Trade status (pending, open, closed, cancelled)
        pnl: Profit/Loss in currency
        created_at: Timestamp when trade was created
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    direction = Column(String(10), nullable=False)  # buy, sell
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, open, closed, cancelled
    pnl = Column(Float, nullable=True)  # Profit/Loss
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    signal = relationship("Signal", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, direction='{self.direction}', status='{self.status}', pnl={self.pnl})>"
    
    def to_dict(self):
        """Convert trade to dictionary."""
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "status": self.status,
            "pnl": self.pnl,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def calculate_pnl(self):
        """Calculate P&L based on entry/exit prices and direction."""
        if self.entry_price and self.exit_price:
            if self.direction == "buy":
                return self.exit_price - self.entry_price
            else:
                return self.entry_price - self.exit_price
        return None