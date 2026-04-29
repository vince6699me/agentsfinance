"""
AgentFinance v5 - Agent Model

Represents AI agents in the trading system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Agent(Base):
    """
    Agent model representing AI trading agents.
    
    Attributes:
        id: Primary key
        name: Agent name (e.g., "T1-A1 — Macro Intelligence Agent")
        department: Department (e.g., "fundamental", "technical", "smc")
        role: Specific role within department
        status: Agent status (active, inactive, paused)
        created_at: Timestamp when agent was created
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    department = Column(String(50), nullable=False)
    role = Column(String(100), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    signals = relationship("Signal", back_populates="agent", lazy="dynamic")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', department='{self.department}')>"
    
    def to_dict(self):
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }