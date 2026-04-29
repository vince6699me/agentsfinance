"""
AgentFinance v5 - Portfolio Model

Represents trading portfolios in the system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Portfolio(Base):
    """
    Portfolio model representing trading portfolios.
    
    Attributes:
        id: Primary key
        name: Portfolio name (e.g., "Main Account", "Demo Account")
        balance: Current balance
        equity: Current equity (balance + open P&L)
        created_at: Timestamp when portfolio was created
    """
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    balance = Column(Float, default=0.0, nullable=False)
    equity = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    positions = relationship("Position", back_populates="portfolio", lazy="dynamic")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', balance={self.balance})>"
    
    def to_dict(self):
        """Convert portfolio to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance,
            "equity": self.equity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def update_equity(self):
        """Update equity based on balance and open positions P&L."""
        open_pnl = sum(pos.pnl or 0 for pos in self.positions if pos.pnl is not None)
        self.equity = self.balance + open_pnl