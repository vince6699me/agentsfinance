"""
Base Agent Class and Configuration

Defines the core agent interface used by all 21 agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class MarketSector(Enum):
    """Market sectors covered by agents."""
    FOREX = "forex"
    COMMODITIES = "commodities"
    STOCKS = "stocks"
    INDICES = "indices"
    CRYPTO = "crypto"


class StrategyTier(Enum):
    """Strategy tier classification."""
    SCALP = "scalp"           # 15 min half-life
    SHORT_TERM = "short_term"   # 60 min half-life
    SWING = "swing"            # 4 hour half-life
    POSITION = "position"      # 24 hour half-life


@dataclass
class AgentConfig:
    """Configuration for an agent instance."""
    agent_id: str
    role: str
    department: str
    sector: MarketSector = None
    enabled: bool = True
    timeout_seconds: int = 300
    max_retries: int = 3
    model: str = "llama3.1:8b"
    temperature: float = 0.7
    tools: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result returned by agent execution."""
    agent_id: str
    status: AgentStatus
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    signal: Optional[str] = None  # LONG, SHORT, NO_TRADE
    analysis: dict[str, Any] = field(default_factory=dict)
    confluence: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentStatus.COMPLETED and self.signal != "NO_TRADE"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "signal": self.signal,
            "analysis": self.analysis,
            "confluence": self.confluence,
            "warnings": self.warnings,
            "errors": self.errors,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


@dataclass
class MarketData:
    """Market data context for agent analysis."""
    symbol: str
    sector: MarketSector
    timeframe: str = "H1"
    ohlcv: dict[str, float] = field(default_factory=dict)
    news: list[dict[str, Any]] = field(default_factory=list)
    macro_data: dict[str, Any] = field(default_factory=dict)
    sentiment: float = 0.0
    regime: str = "UNKNOWN"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_prompt_context(self) -> str:
        """Format market data for LLM prompt."""
        context = f"""
Symbol: {self.symbol}
Sector: {self.sector.value}
Timeframe: {self.timeframe}
Regime: {self.regime}
Sentiment: {self.sentiment:.2f}

OHLCV:
- Open: {self.ohlcv.get('open', 'N/A')}
- High: {self.ohlcv.get('high', 'N/A')}
- Low: {self.ohlcv.get('low', 'N/A')}
- Close: {self.ohlcv.get('close', 'N/A')}
- Volume: {self.ohlcv.get('volume', 'N/A')}

Recent News ({len(self.news)} items):
"""
        for i, item in enumerate(self.news[:5]):
            context += f"\n{i+1}. {item.get('headline', 'N/A')}"

        if self.macro_data:
            context += "\n\nMacro Data:"
            for key, value in self.macro_data.items():
                context += f"\n- {key}: {value}"

        return context


class BaseAgent(ABC):
    """
    Base class for all 21 agents.
    
    Each agent implements analyze() to produce market analysis.
    The framework handles execution, retries, and result formatting.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._system_prompt = ""
        self._execution_count = 0

    @property
    def agent_id(self) -> str:
        return self.config.agent_id

    @property
    def role(self) -> str:
        return self.config.role

    @property
    def department(self) -> str:
        return self.config.department

    @property
    def system_prompt(self) -> str:
        """Get the agent's system prompt."""
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        """Set the agent's system prompt."""
        self._system_prompt = value

    @abstractmethod
    def analyze(self, market_data: MarketData) -> AgentResult:
        """
        Run agent analysis on market data.
        
        Args:
            market_data: Current market context
            
        Returns:
            AgentResult with analysis findings and signal
        """
        pass

    def get_tools(self) -> list[str]:
        """Get list of tools available to this agent."""
        return self.config.tools

    def is_enabled(self) -> bool:
        """Check if agent is enabled for execution."""
        return self.config.enabled

    def execute(self, market_data: MarketData) -> AgentResult:
        """
        Execute agent with error handling and retries.
        
        This method wraps analyze() with:
        - Error handling
        - Retry logic
        - Timing measurement
        """
        import time
        start_time = time.monotonic()
        self._execution_count += 1

        result = None
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                result = self.analyze(market_data)
                if result.status != AgentStatus.FAILED:
                    break
            except Exception as e:
                last_error = str(e)
                if result is None:
                    result = AgentResult(
                        agent_id=self.agent_id,
                        status=AgentStatus.FAILED,
                    )
                result.errors.append(f"Attempt {attempt + 1}: {e}")

        execution_time_ms = int((time.monotonic() - start_time) * 1000)

        if result is None:
            result = AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                errors=[last_error or "Unknown error"],
            )

        result.execution_time_ms = execution_time_ms
        result.metadata["execution_count"] = self._execution_count

        return result


# Agent factory function type
AgentFactory = lambda config: BaseAgent