"""
Agent Registry

Central registration system for all 21 agents.
Supports dynamic agent lookup, filtering, and execution scheduling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from app.agents.base import (
    AgentConfig,
    AgentFactory,
    AgentResult,
    AgentStatus,
    BaseAgent,
    MarketSector,
)


@dataclass
class AgentMetadata:
    """Metadata for a registered agent."""
    agent_id: str
    role: str
    department: str
    sector: Optional[MarketSector] = None
    strategy_tiers: list[str] = field(default_factory=list)
    strategies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0


class AgentRegistry:
    """
    Central registry for all 21 agents.
    
    Provides:
    - Agent registration and lookup
    - Department/sector filtering
    - Execution scheduling
    - Performance tracking
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}
        self._metadata: dict[str, AgentMetadata] = {}
        self._factories: dict[str, AgentFactory] = {}
        self._execution_order: list[str] = []
        self._initialized = False

    def register(
        self,
        agent_id: str,
        factory: AgentFactory,
        metadata: AgentMetadata,
    ) -> None:
        """
        Register an agent with its factory and metadata.
        
        Args:
            agent_id: Unique identifier (e.g., "01", "T1-A1")
            factory: Function that creates agent instance
            metadata: Agent metadata
        """
        self._factories[agent_id] = factory
        self._metadata[agent_id] = metadata
        if agent_id not in self._execution_order:
            self._execution_order.append(agent_id)

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get agent instance by ID.
        
        Creates instance if not already cached.
        """
        if agent_id not in self._agents:
            factory = self._factories.get(agent_id)
            if factory:
                config = AgentConfig(
                    agent_id=agent_id,
                    role=self._metadata[agent_id].role,
                    department=self._metadata[agent_id].department,
                    sector=self._metadata[agent_id].sector,
                )
                self._agents[agent_id] = factory(config)
        return self._agents.get(agent_id)

    def get_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent metadata by ID."""
        return self._metadata.get(agent_id)

    def list_by_department(self, department: str) -> list[AgentMetadata]:
        """List all agents in a department."""
        return [
            m for m in self._metadata.values()
            if m.department.lower() == department.lower()
        ]

    def list_by_sector(self, sector: MarketSector) -> list[AgentMetadata]:
        """List all agents for a sector."""
        return [
            m for m in self._metadata.values()
            if m.sector == sector
        ]

    def list_all(self) -> list[AgentMetadata]:
        """List all registered agents."""
        return list(self._metadata.values())

    def get_execution_order(self, department: Optional[str] = None) -> list[str]:
        """Get agent execution order, optionally filtered by department."""
        if department:
            dept_agents = [
                m.agent_id for m in self._metadata.values()
                if m.department.lower() == department.lower()
            ]
            return [a for a in self._execution_order if a in dept_agents]
        return self._execution_order.copy()

    def update_execution_stats(
        self,
        agent_id: str,
        result: AgentResult,
    ) -> None:
        """Update execution statistics for an agent."""
        if agent_id in self._metadata:
            meta = self._metadata[agent_id]
            meta.last_executed = result.timestamp
            meta.execution_count += 1

            if result.status == AgentStatus.COMPLETED:
                # Update rolling success rate
                prev_rate = meta.success_rate
                n = meta.execution_count
                success = 1 if result.signal != "NO_TRADE" else 0
                meta.success_rate = ((prev_rate * (n - 1)) + success) / n

    def is_initialized(self) -> bool:
        """Check if registry is initialized."""
        return self._initialized

    def set_initialized(self, value: bool) -> None:
        """Set initialization status."""
        self._initialized = value


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def register_agent(
    agent_id: str,
    factory: AgentFactory,
    metadata: AgentMetadata,
) -> None:
    """Register an agent in the global registry."""
    get_registry().register(agent_id, factory, metadata)


# Pre-defined agent roster from gen_v5.md
DEPARTMENT_AGENTS = {
    "News & Market Data": [
        {"agent_id": "T1-A1", "role": "Macro Intelligence Agent", "sector": None},
        {"agent_id": "T1-A2", "role": "News NLP Agent", "sector": None},
        {"agent_id": "T1-A3", "role": "Sector Data Collector", "sector": None},
        {"agent_id": "T1-A4", "role": "COT Report Agent", "sector": None},
    ],
    "Scanner": [
        {"agent_id": "T2-A1", "role": "Forex Scanner", "sector": MarketSector.FOREX},
        {"agent_id": "T2-A2", "role": "Commodities Scanner", "sector": MarketSector.COMMODITIES},
        {"agent_id": "T2-A3", "role": "Stocks Scanner", "sector": MarketSector.STOCKS},
        {"agent_id": "T2-A4", "role": "Indices Scanner", "sector": MarketSector.INDICES},
        {"agent_id": "T2-A5", "role": "Crypto Scanner", "sector": MarketSector.CRYPTO},
    ],
    "Fundamental": [
        {"agent_id": "01", "role": "Macro Economics", "sector": None},
        {"agent_id": "02", "role": "Forex Fundamentals", "sector": MarketSector.FOREX},
        {"agent_id": "03", "role": "Commodities Fundamentals", "sector": MarketSector.COMMODITIES},
        {"agent_id": "04", "role": "Equity Fundamentals", "sector": MarketSector.STOCKS},
    ],
    "Technical": [
        {"agent_id": "05", "role": "Price Action", "sector": None},
        {"agent_id": "06", "role": "Indicators", "sector": None},
        {"agent_id": "07", "role": "Trend Analysis", "sector": None},
    ],
    "Sentiment": [
        {"agent_id": "08", "role": "COT Sentiment", "sector": None},
        {"agent_id": "09", "role": "Market Sentiment", "sector": None},
        {"agent_id": "10", "role": "News NLP", "sector": None},
    ],
    "Intermarket": [
        {"agent_id": "11", "role": "Bond-Equity", "sector": None},
        {"agent_id": "12", "role": "Commodity-FX", "sector": None},
        {"agent_id": "13", "role": "Correlation Monitor", "sector": None},
    ],
    "Quantitative": [
        {"agent_id": "14", "role": "Statistical Modeller", "sector": None},
        {"agent_id": "15", "role": "Volume Analyst", "sector": None},
        {"agent_id": "16", "role": "Algorithmic Execution", "sector": None},
        {"agent_id": "17", "role": "Parameter Optimiser", "sector": None},
    ],
    "SMC/ICT": [
        {"agent_id": "18", "role": "Order Block & FVG", "sector": None},
        {"agent_id": "19", "role": "Market Structure", "sector": None},
        {"agent_id": "20", "role": "Liquidity Analyst", "sector": None},
        {"agent_id": "21", "role": "Session/Kill Zone", "sector": None},
    ],
}


def initialize_registry(
    registry: Optional[AgentRegistry] = None,
    agent_factories: Optional[dict[str, AgentFactory]] = None,
) -> AgentRegistry:
    """
    Initialize the registry with all 21 agents.
    
    Args:
        registry: Registry to initialize (uses global if None)
        agent_factories: Optional dict of custom agent factories
        
    Returns:
        Initialized registry
    """
    reg = registry or get_registry()
    factories = agent_factories or {}

    for department, agents in DEPARTMENT_AGENTS.items():
        for agent_info in agents:
            agent_id = agent_info["agent_id"]
            role = agent_info["role"]
            sector = agent_info.get("sector")

            # Use custom factory if available, otherwise use default
            factory = factories.get(agent_id, lambda config: BaseAgent(config))

            metadata = AgentMetadata(
                agent_id=agent_id,
                role=role,
                department=department,
                sector=sector,
            )

            reg.register(agent_id, factory, metadata)

    reg.set_initialized(True)
    return reg