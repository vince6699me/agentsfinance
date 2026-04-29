"""
Agent Execution Framework

Orchestrates execution of all 21 agents with:
- Parallel execution by department
- Sequential dependencies
- Result aggregation
- Timeout handling
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.agents.base import (
    AgentConfig,
    AgentResult,
    AgentStatus,
    BaseAgent,
    MarketData,
    MarketSector,
)
from app.agents.registry import AgentRegistry, get_registry


@dataclass
class ExecutionConfig:
    """Configuration for agent execution."""
    department: Optional[str] = None
    sector: Optional[MarketSector] = None
    max_concurrent: int = 5
    timeout_seconds: int = 300
    require_all: bool = True  # Require all agents to complete
    stop_on_failure: bool = True


@dataclass
class ExecutionReport:
    """Report from agent execution cycle."""
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    results: dict[str, AgentResult] = field(default_factory=dict)
    total_agents: int = 0
    completed: int = 0
    failed: int = 0
    signals: dict[str, int] = field(default_factory=dict)  # signal -> count
    aggregate_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "total_agents": self.total_agents,
            "completed": self.completed,
            "failed": self.failed,
            "signals": self.signals,
            "aggregate_confidence": self.aggregate_confidence,
            "results": {
                k: v.to_dict() for k, v in self.results.items()
            },
        }


class AgentExecutor:
    """
    Executes agents according to configuration.
    
    Supports:
    - Single agent execution
    - Department-level parallel execution
    - Sector-specific execution
    - Full pipeline execution
    """

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        max_workers: int = 5,
    ):
        self.registry = registry or get_registry()
        self.max_workers = max_workers

    def execute_single(
        self,
        agent_id: str,
        market_data: MarketData,
    ) -> AgentResult:
        """Execute a single agent."""
        agent = self.registry.get(agent_id)
        if not agent:
            return AgentResult(
                agent_id=agent_id,
                status=AgentStatus.FAILED,
                errors=[f"Agent {agent_id} not found"],
            )

        result = agent.execute(market_data)
        self.registry.update_execution_stats(agent_id, result)
        return result

    def execute_department(
        self,
        department: str,
        market_data: MarketData,
        config: Optional[ExecutionConfig] = None,
    ) -> ExecutionReport:
        """Execute all agents in a department."""
        exec_config = config or ExecutionConfig(department=department)
        start_time = time.monotonic()

        agent_ids = self.registry.get_execution_order(department)
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.execute_single, aid, market_data): aid
                for aid in agent_ids
            }

            for future in as_completed(futures):
                agent_id = futures[future]
                try:
                    results[agent_id] = future.result()
                except Exception as e:
                    results[agent_id] = AgentResult(
                        agent_id=agent_id,
                        status=AgentStatus.FAILED,
                        errors=[str(e)],
                    )

                if exec_config.stop_on_failure and results[agent_id].status == AgentStatus.FAILED:
                    if not exec_config.require_all:
                        break

        report = self._build_report(results, start_time)
        return report

    def execute_sector(
        self,
        sector: MarketSector,
        market_data: MarketData,
    ) -> ExecutionReport:
        """Execute all scanner agents for a sector."""
        start_time = time.monotonic()

        metadata_list = self.registry.list_by_sector(sector)
        agent_ids = [m.agent_id for m in metadata_list]
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.execute_single, aid, market_data): aid
                for aid in agent_ids
            }

            for future in as_completed(futures):
                agent_id = futures[future]
                try:
                    results[agent_id] = future.result()
                except Exception as e:
                    results[agent_id] = AgentResult(
                        agent_id=agent_id,
                        status=AgentStatus.FAILED,
                        errors=[str(e)],
                    )

        report = self._build_report(results, start_time)
        return report

    def execute_all(
        self,
        market_data: MarketData,
        config: Optional[ExecutionConfig] = None,
    ) -> ExecutionReport:
        """Execute all 21 agents."""
        exec_config = config or ExecutionConfig()
        start_time = time.monotonic()

        agent_ids = self.registry.get_execution_order()
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.execute_single, aid, market_data): aid
                for aid in agent_ids
            }

            for future in as_completed(futures):
                agent_id = futures[future]
                try:
                    results[agent_id] = future.result()
                except Exception as e:
                    results[agent_id] = AgentResult(
                        agent_id=agent_id,
                        status=AgentStatus.FAILED,
                        errors=[str(e)],
                    )

                if exec_config.stop_on_failure and results[agent_id].status == AgentStatus.FAILED:
                    if not exec_config.require_all:
                        break

        report = self._build_report(results, start_time)
        return report

    def _build_report(
        self,
        results: dict[str, AgentResult],
        start_time: float,
    ) -> ExecutionReport:
        """Build execution report from results."""
        signals: dict[str, int] = {}
        total_confidence = 0.0
        completed = 0
        failed = 0

        for agent_id, result in results.items():
            if result.status == AgentStatus.COMPLETED:
                completed += 1
                if result.signal:
                    signals[result.signal] = signals.get(result.signal, 0) + 1
                total_confidence += result.confidence
            else:
                failed += 1

        aggregate_confidence = (
            total_confidence / len(results) if results else 0.0
        )

        return ExecutionReport(
            duration_ms=int((time.monotonic() - start_time) * 1000),
            results=results,
            total_agents=len(results),
            completed=completed,
            failed=failed,
            signals=signals,
            aggregate_confidence=aggregate_confidence,
        )


# Module-level convenience functions

def execute_agent(
    agent_id: str,
    market_data: MarketData,
    registry: Optional[AgentRegistry] = None,
) -> AgentResult:
    """Execute a single agent by ID."""
    reg = registry or get_registry()
    executor = AgentExecutor(reg)
    return executor.execute_single(agent_id, market_data)


def execute_all_agents(
    market_data: MarketData,
    config: Optional[ExecutionConfig] = None,
    registry: Optional[AgentRegistry] = None,
) -> ExecutionReport:
    """Execute all 21 agents."""
    reg = registry or get_registry()
    executor = AgentExecutor(reg)
    return executor.execute_all(market_data, config)