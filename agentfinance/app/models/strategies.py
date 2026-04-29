"""
AgentFinance v5 - Strategy Model

Represents trading strategies in the system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Strategy(Base):
    """
    Strategy model representing trading strategies.
    
    Attributes:
        id: Primary key
        strategy_id: Unique strategy identifier (e.g., "ICT-01", "STRAT_003")
        name: Strategy name (e.g., "Micro-Sweep Scalp")
        category: Strategy category (ict, technical, fundamental, sentiment, intermarket, quantitative)
        tier: Strategy tier (scalp, short-term, swing, position, structural, execution)
        sector: Market sector (forex, commodities, stocks, indices, crypto, all)
        department: Analysis department (fundamental, technical, sentiment, intermarket, quantitative, smc_ict)
        is_tactic: Whether this is an execution tactic (not a signal generator)
        description: Strategy description
        parameters: JSON configuration parameters
        status: Strategy status (active, inactive, testing)
        v2_enabled: Whether v2 enhancements are applied
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    tier = Column(String(20), nullable=True, index=True)
    sector = Column(String(50), nullable=True, index=True)
    department = Column(String(50), nullable=True)
    is_tactic = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    status = Column(String(20), default="active", nullable=False)
    v2_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    signals = relationship("Signal", back_populates="strategy", lazy="dynamic")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, strategy_id='{self.strategy_id}', name='{self.name}')>"
    
    def to_dict(self):
        """Convert strategy to dictionary."""
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "name": self.name,
            "category": self.category,
            "tier": self.tier,
            "sector": self.sector,
            "department": self.department,
            "is_tactic": self.is_tactic,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status,
            "v2_enabled": self.v2_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }