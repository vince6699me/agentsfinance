"""
Department base classes and registry for AgentFinance v5 Analysis Team.

Philosophy-based departments following modular, functional design patterns
from code-quality standards. Each department is a pluggable module with
clear responsibilities and explicit interfaces.

Department Structure:
1. Fundamental Analysis (Agents 01-04) - Macro, Forex, Commodities, Equity
2. Technical Analysis (Agents 05-07) - Price Action, Indicators, Trend
3. Sentiment Analysis (Agents 08-10) - COT, Market, News NLP
4. Intermarket Analysis (Agents 11-13) - Bond-Equity, Commodity-FX, Correlations
5. Quantitative/Systematic (Agents 14-17) - Statistical, Volume, Algo, Optimiser
6. SMC/ICT Analysis (Agents 18-21) - Order Blocks, Structure, Liquidity, Sessions
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# ============================================================================
# Enums and Constants
# ============================================================================


class DepartmentId(Enum):
    """Department identification enum."""
    FUNDAMENTAL = 1
    TECHNICAL = 2
    SENTIMENT = 3
    INTERMARKET = 4
    QUANTITATIVE = 5
    SMC_ICT = 6


class AnalysisResultStatus(Enum):
    """Status of an analysis result."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class AgentResult:
    """Result from a single agent analysis."""
    agent_id: str
    agent_name: str
    department_id: int
    status: AnalysisResultStatus
    signals: list[dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DepartmentResult:
    """Aggregated result from a department."""
    department_id: DepartmentId
    department_name: str
    status: AnalysisResultStatus
    agent_results: list[AgentResult] = field(default_factory=list)
    combined_signals: list[dict[str, Any]] = field(default_factory=list)
    confluence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# Base Department Class
# ============================================================================


class BaseDepartment(ABC):
    """
    Base class for all analysis departments.
    
    Following the modular design principle: single responsibility per module.
    Each department has clear interfaces and can be tested in isolation.
    """
    
    def __init__(self, department_id: DepartmentId, department_name: str):
        self.department_id = department_id
        self.department_name = department_name
        self.agents: list[dict[str, str]] = []
    
    @abstractmethod
    async def analyze(
        self,
        instrument: str,
        sector: str,
        timeframe: str,
        data: dict[str, Any],
    ) -> DepartmentResult:
        """
        Run department analysis on instrument.
        
        Args:
            instrument: Trading instrument symbol
            sector: Market sector (forex, commodities, stocks, indices, crypto)
            timeframe: Analysis timeframe (M15, H1, H4, D1, etc.)
            data: Market data for analysis
            
        Returns:
            DepartmentResult with agent analyses and signals
        """
        pass
    
    @abstractmethod
    def get_agents(self) -> list[dict[str, str]]:
        """Return list of agents in this department."""
        pass
    
    def register_agent(self, agent_id: str, agent_name: str, role: str) -> None:
        """Register an agent to this department."""
        self.agents.append({
            "id": agent_id,
            "name": agent_name,
            "role": role,
        })


# ============================================================================
# Department Registry
# ============================================================================


class DepartmentRegistry:
    """
    Registry for all analysis departments.
    
    Singleton pattern to maintain single source of truth for departments.
    """
    
    _instance: Optional["DepartmentRegistry"] = None
    _departments: dict[DepartmentId, BaseDepartment] = {}
    
    def __new__(cls) -> "DepartmentRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._departments = {}
        return cls._instance
    
    def register(self, department: BaseDepartment) -> None:
        """Register a department."""
        self._departments[department.department_id] = department
    
    def get(self, department_id: DepartmentId) -> Optional[BaseDepartment]:
        """Get a department by ID."""
        return self._departments.get(department_id)
    
    def get_all(self) -> dict[DepartmentId, BaseDepartment]:
        """Get all registered departments."""
        return self._departments.copy()
    
    def get_all_results(
        self,
        instrument: str,
        sector: str,
        timeframe: str,
        data: dict[str, Any],
    ) -> list[DepartmentResult]:
        """Run all departments and return results."""
        results = []
        for department in self._departments.values():
            # Note: In production, use asyncio.gather for parallel execution
            result = department.analyze(instrument, sector, timeframe, data)
            results.append(result)
        return results


# Helper function to get department registry
def get_registry() -> DepartmentRegistry:
    """Get the department registry instance."""
    return DepartmentRegistry()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "DepartmentId",
    "AnalysisResultStatus",
    "AgentResult",
    "DepartmentResult",
    "BaseDepartment",
    "DepartmentRegistry",
    "get_registry",
]