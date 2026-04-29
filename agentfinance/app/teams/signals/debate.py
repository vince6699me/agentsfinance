"""
Trade Signals Team - Debate Orchestrator

Orchestrates the full Bull/Bear/Neutral debate:
1. Validates pre-trade checklist (must score >= 7/9)
2. Checks signal hasn't expired (half-life check)
3. Runs Bull Analyst argument
4. Runs Bear Analyst argument
5. Runs Neutral/Risk Analyst stress test
6. Fund Manager produces final decision
7. Logs debate transcript to database
"""

from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field

from app.teams.signals.models import (
    AnalysisSignal,
    BullCase,
    BearCase,
    NeutralCase,
    FundManagerDecision,
    DebateTranscript,
    MIN_CONFLUENCE_DEPARTMENTS,
    CONFIDENCE_THRESHOLD_ENTRY,
    CHECKLIST_THRESHOLD,
    DEPARTMENT_NAMES,
    is_signal_expired,
)
from app.teams.signals.roles import (
    BullAnalyst,
    BearAnalyst,
    NeutralAnalyst,
    FundManager,
)


@dataclass
class DebateConfig:
    """Configuration for debate execution."""
    # Required thresholds
    min_confluence: int = MIN_CONFLUENCE_DEPARTMENTS
    min_checklist_score: float = CHECKLIST_THRESHOLD
    confidence_entry: int = CONFIDENCE_THRESHOLD_ENTRY
    
    # Risk parameters
    max_spread_ratio: float = 2.0
    max_correlation: float = 0.7
    
    # Half-life configuration (minutes by tier)
    half_life_tier: str = "scalp"


@dataclass
class DebateRequest:
    """Request to initiate a debate."""
    signal_id: int
    symbol: str
    sector: str
    current_price: float
    signals: list[AnalysisSignal] = field(default_factory=list)
    key_levels: dict[str, float] = field(default_factory=dict)
    checklist_score: float = 9.0
    current_spread: float = 0.0
    historical_spread: float = 0.0
    portfolio_correlation: float = 0.0
    news_events: list[dict[str, Any]] = field(default_factory=list)
    strategy_tier: str = "scalp"
    signal_created_at: Optional[datetime] = field(default_factory=datetime.utcnow)


@dataclass
class DebateResult:
    """Result of a completed debate."""
    signal_id: int
    symbol: str
    sector: str
    
    # Individual cases
    bull_case: BullCase = field(default_factory=BullCase)
    bear_case: BearCase = field(default_factory=BearCase)
    neutral_case: NeutralCase = field(default_factory=NeutralCase)
    fund_manager_decision: FundManagerDecision = field(default_factory=FundManagerDecision)
    
    # Validation results
    checklist_passed: bool = False
    signal_not_expired: bool = False
    confluence_met: bool = False
    confidence_threshold_met: bool = False
    
    # Debate metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    
    # Error if debate failed
    error: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "sector": self.sector,
            "bull_case": self.bull_case.to_dict(),
            "bear_case": self.bear_case.to_dict(),
            "neutral_case": self.neutral_case.to_dict(),
            "fund_manager_decision": self.fund_manager_decision.to_dict(),
            "validation": {
                "checklist_passed": self.checklist_passed,
                "signal_not_expired": self.signal_not_expired,
                "confluence_met": self.confluence_met,
                "confidence_threshold_met": self.confidence_threshold_met,
            },
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }
    
    def is_approved(self) -> bool:
        """Check if trade is approved."""
        return (
            self.checklist_passed and
            self.signal_not_expired and
            self.confluence_met and
            self.confidence_threshold_met and
            self.fund_manager_decision.is_approved()
        )


# ============================================================================
# Debate Orchestrator
# ============================================================================

class DebateOrchestrator:
    """
    Orchestrates the Bull/Bear/Neutral debate mechanism.
    
    Flow:
    1. Validate pre-trade checklist (>= 7/9 required)
    2. Check signal hasn't expired
    3. Run Bull Analyst
    4. Run Bear Analyst
    5. Run Neutral Analyst
    6. Run Fund Manager decision
    7. Log transcript to database
    """
    
    def __init__(self, config: DebateConfig = None):
        self.config = config or DebateConfig()
        self.bull_analyst = BullAnalyst()
        self.bear_analyst = BearAnalyst()
        self.neutral_analyst = NeutralAnalyst()
        self.fund_manager = FundManager()
    
    async def run_debate(self, request: DebateRequest) -> DebateResult:
        """
        Run full debate for a signal.
        
        Args:
            request: Debate request with all required data
            
        Returns:
            DebateResult with all cases and final decision
        """
        result = DebateResult(
            signal_id=request.signal_id,
            symbol=request.symbol,
            sector=request.sector,
            started_at=datetime.utcnow(),
        )
        
        try:
            # ===== Step 1: Validate Checklist =====
            result.checklist_passed = request.checklist_score >= self.config.min_checklist_score
            
            if not result.checklist_passed:
                result.error = f"CHECKLIST FAILED: {request.checklist_score:.0f}/9 (required: {self.config.min_checklist_score}/9)"
                result.fund_manager_decision = FundManagerDecision(
                    decision="NO_TRADE",
                    confidence=0,
                    rationale=result.error,
                )
                return result
            
            # ===== Step 2: Check Signal Expiration =====
            if request.signal_created_at:
                result.signal_not_expired = not is_signal_expired(
                    request.signal_created_at,
                    request.strategy_tier,
                )
            else:
                result.signal_not_expired = True
            
            if not result.signal_not_expired:
                result.error = "SIGNAL EXPIRED: Past confidence half-life"
                result.fund_manager_decision = FundManagerDecision(
                    decision="NO_TRADE",
                    confidence=0,
                    rationale=result.error,
                )
                return result
            
            # ===== Step 3: Run Bull Analyst =====
            result.bull_case = self.bull_analyst.analyze(
                request.signals,
                request.current_price,
                request.key_levels,
            )
            
            # ===== Step 4: Run Bear Analyst =====
            result.bear_case = self.bear_analyst.analyze(
                request.signals,
                request.current_price,
                request.key_levels,
                result.bull_case,
            )
            
            # ===== Step 5: Run Neutral Analyst =====
            result.neutral_case = self.neutral_analyst.analyze(
                request.signals,
                request.current_spread,
                request.historical_spread,
                request.portfolio_correlation,
                request.news_events,
                request.checklist_score,
            )
            
            # ===== Step 6: Run Fund Manager =====
            result.fund_manager_decision = self.fund_manager.decide(
                result.bull_case,
                result.bear_case,
                result.neutral_case,
                request.signals,
            )
            
            # ===== Step 7: Validate Results =====
            # Check confluence
            bull_confluence = result.bull_case.confluence_count
            result.confluence_met = bull_confluence >= self.config.min_confluence
            
            # Check confidence threshold
            result.confidence_threshold_met = (
                result.fund_manager_decision.confidence >= self.config.confidence_entry
            )
            
            # ===== Complete =====
            result.completed_at = datetime.utcnow()
            result.duration_ms = int(
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
            
        except Exception as e:
            result.error = f"DEBATE ERROR: {str(e)}"
            result.fund_manager_decision = FundManagerDecision(
                decision="NO_TRADE",
                confidence=0,
                rationale=f"Error: {str(e)}",
            )
            result.completed_at = datetime.utcnow()
            result.duration_ms = int(
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
        
        return result
    
    def create_transcript(
        self,
        request: DebateRequest,
        result: DebateResult,
    ) -> dict[str, Any]:
        """
        Create transcript dictionary for storage.
        
        Args:
            request: Original debate request
            result: Debate result
            
        Returns:
            Dictionary ready for database storage
        """
        return {
            "signal_id": request.signal_id,
            "sector": request.sector,
            "symbol": request.symbol,
            "bull_arguments": result.bull_case.arguments,
            "bull_confluence": result.bull_case.confluence_count,
            "bull_score": result.bull_case.risk_reward,
            "bear_arguments": result.bear_case.arguments,
            "bear_counter_arguments": result.bear_case.counter_arguments,
            "bear_score": result.bear_case.risk_reward,
            "neutral_checklist_score": result.neutral_case.checklist_score,
            "neutral_risk_flags": result.neutral_case.risk_flags,
            "neutral_position_adjustment": result.neutral_case.position_adjustment,
            "fund_manager_decision": result.fund_manager_decision.decision,
            "fund_manager_confidence": result.fund_manager_decision.confidence,
            "fund_manager_rationale": result.fund_manager_decision.rationale,
            "position_size_multiplier": result.fund_manager_decision.position_size_multiplier,
            "debate_duration_ms": result.duration_ms,
            "confluence_requirement_met": 1 if result.confluence_met else 0,
            "confidence_threshold_met": 1 if result.confidence_threshold_met else 0,
        }


# ============================================================================
# Simplified API Functions
# ============================================================================

async def run_debate(
    signal_id: int,
    symbol: str,
    sector: str,
    current_price: float,
    signals: list[AnalysisSignal],
    key_levels: dict[str, float] = None,
    checklist_score: float = 9.0,
    current_spread: float = 0.0,
    historical_spread: float = 0.0,
    portfolio_correlation: float = 0.0,
    news_events: list[dict[str, Any]] = None,
    strategy_tier: str = "scalp",
) -> DebateResult:
    """
    Convenience function to run a debate.
    
    Args:
        signal_id: ID of the signal to debate
        symbol: Trading symbol (e.g., "EURUSD")
        sector: Market sector
        current_price: Current market price
        signals: Signals from all 6 departments
        key_levels: Key price levels
        checklist_score: Pre-trade checklist score (0-9)
        current_spread: Current bid-ask spread
        historical_spread: Average historical spread
        portfolio_correlation: Current portfolio correlation
        news_events: Upcoming news events
        strategy_tier: Strategy tier (scalp/short_term/swing/position)
        
    Returns:
        DebateResult with all cases and final decision
    """
    request = DebateRequest(
        signal_id=signal_id,
        symbol=symbol,
        sector=sector,
        current_price=current_price,
        signals=signals,
        key_levels=key_levels or {},
        checklist_score=checklist_score,
        current_spread=current_spread,
        historical_spread=historical_spread,
        portfolio_correlation=portfolio_correlation,
        news_events=news_events or [],
        strategy_tier=strategy_tier,
    )
    
    orchestrator = DebateOrchestrator()
    return await orchestrator.run_debate(request)


def create_sample_signals() -> list[AnalysisSignal]:
    """
    Create sample signals for testing purposes.
    
    Returns:
        List of sample AnalysisSignal objects
    """
    return [
        AnalysisSignal(
            department_id=1,
            department_name="Fundamental Analysis",
            agent_id="T3-D1-A1",
            direction="buy",
            confidence=75.0,
            supporting_factors=["Positive GDP growth", "CB hawkish stance"],
            key_levels={"resistance": 1.0950, "support": 1.0850},
        ),
        AnalysisSignal(
            department_id=2,
            department_name="Technical Analysis",
            agent_id="T3-D2-A1",
            direction="buy",
            confidence=80.0,
            supporting_factors=["Bullish divergence", "EMA crossover"],
            key_levels={"resistance": 1.0950, "support": 1.0850},
        ),
        AnalysisSignal(
            department_id=3,
            department_name="Sentiment Analysis",
            agent_id="T3-D3-A1",
            direction="buy",
            confidence=65.0,
            supporting_factors=["COT commercial long", "VIX declining"],
            key_levels={},
        ),
        AnalysisSignal(
            department_id=4,
            department_name="Intermarket Analysis",
            agent_id="T3-D4-A1",
            direction="neutral",
            confidence=50.0,
            supporting_factors=[],
            key_levels={},
        ),
        AnalysisSignal(
            department_id=5,
            department_name="Quantitative/Systematic",
            agent_id="T3-D5-A1",
            direction="buy",
            confidence=70.0,
            supporting_factors=["Mean reversion signal", "Volume confirmation"],
            key_levels={"stop_loss": 1.0820},
        ),
        AnalysisSignal(
            department_id=6,
            department_name="SMC/ICT Analysis",
            agent_id="T3-D6-A1",
            direction="buy",
            confidence=85.0,
            supporting_factors=["Order block detected", "FVG present", "Kill zone active"],
            key_levels={
                "order_block": 1.0870,
                "fte": 1.0900,
                "stop_loss": 1.0820,
                "take_profit": 1.0980,
            },
        ),
    ]


def create_sample_request(
    signal_id: int = 1,
    symbol: str = "EURUSD",
    sector: str = "forex",
) -> DebateRequest:
    """Create a sample debate request for testing."""
    return DebateRequest(
        signal_id=signal_id,
        symbol=symbol,
        sector=sector,
        current_price=1.0920,
        signals=create_sample_signals(),
        key_levels={
            "support": 1.0850,
            "resistance": 1.0950,
            "stop_loss": 1.0820,
            "take_profit": 1.0980,
        },
        checklist_score=8.0,
        current_spread=0.5,
        historical_spread=0.3,
        portfolio_correlation=0.45,
        news_events=[],
        strategy_tier="scalp",
    )