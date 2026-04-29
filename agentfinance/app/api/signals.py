"""
Signals API - Trade Signals Team Endpoints

API endpoints for Team 4: Trade Signals (Debate Mechanism)

Endpoints:
- POST /signals/debate - Initiate Bull/Bear/Neutral debate
- GET /signals/{signal_id} - Get signal with debate result
- GET /signals - List signals with debate history
- GET /signals/statistics - Get debate statistics
- POST /signals/checklist - Validate pre-trade checklist

Following REST API design principles with consistent response format.
"""

from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.teams.signals import (
    DebateOrchestrator,
    DebateRequest,
    DebateResult,
    AnalysisSignal,
    create_sample_signals,
    save_transcript,
    get_transcripts,
    get_transcript_by_signal,
    get_debate_statistics,
    get_signal_history,
    MIN_CONFLUENCE_DEPARTMENTS,
    CHECKLIST_THRESHOLD,
    CONFIDENCE_THRESHOLD_ENTRY,
    CONFIDENCE_THRESHOLD_FULL,
)


# Create router
router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class SignalInput(BaseModel):
    """Input for signal creation."""
    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    sector: str = Field(..., description="Market sector")
    direction: str = Field(..., description="Signal direction (buy/sell)")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    supporting_departments: list[int] = Field(default=[], description="Department IDs")
    key_levels: dict[str, float] = Field(default={}, description="Key price levels")
    checklist_score: float = Field(default=9.0, ge=0, le=9, description="Checklist score 0-9")
    current_spread: float = Field(default=0.0, description="Current bid-ask spread")
    historical_spread: float = Field(default=0.3, description="Historical average spread")
    portfolio_correlation: float = Field(default=0.0, description="Portfolio correlation")
    strategy_tier: str = Field(default="scalp", description="Strategy tier")


class DebateRequestInput(BaseModel):
    """Input for debate initiation."""
    signal_id: int = Field(..., description="Signal ID to debate")
    symbol: str = Field(..., description="Trading symbol")
    sector: str = Field(..., description="Market sector")
    current_price: float = Field(..., description="Current market price")
    checklist_score: float = Field(
        default=9.0,
        ge=0,
        le=9,
        description="Pre-trade checklist score"
    )
    current_spread: float = Field(default=0.0, description="Current spread")
    historical_spread: float = Field(default=0.3, description="Historical spread")
    portfolio_correlation: float = Field(default=0.0, description="Portfolio correlation")
    strategy_tier: str = Field(default="scalp", description="Strategy tier")
    
    # Signals from departments (if not provided, use sample for testing)
    signals: list[dict[str, Any]] = Field(
        default=[],
        description="Department signals"
    )
    key_levels: dict[str, float] = Field(
        default={},
        description="Key price levels"
    )


class DebateResponse(BaseModel):
    """Debate result response."""
    signal_id: int
    symbol: str
    decision: str
    confidence: int
    position_size_multiplier: float
    rationale: str
    bull_case: dict[str, Any]
    bear_case: dict[str, Any]
    neutral_case: dict[str, Any]
    validation: dict[str, Any]
    duration_ms: int


class ChecklistInput(BaseModel):
    """Pre-trade checklist input."""
    signal_id: int
    symbol: str
    sector: str
    
    # Checklist items (0=no, 1=yes)
    kill_zone: int = Field(default=0, ge=0, le=1)
    structure_confirmed: int = Field(default=0, ge=0, le=1)
    ote_within_zone: int = Field(default=0, ge=0, le=1)
    ob_quality: int = Field(default=0, ge=0, le=1)
    liquidity_pool: int = Field(default=0, ge=0, le=1)
    adr_consumption: int = Field(default=0, ge=0, le=1)
    news_proximity: int = Field(default=0, ge=0, le=1)
    spread_check: int = Field(default=0, ge=0, le=1)
    regime_alignment: int = Field(default=0, ge=0, le=1)


class ChecklistResponse(BaseModel):
    """Checklist result response."""
    signal_id: int
    total_score: float
    passed: bool
    items: dict[str, Any]


# ============================================================================
# Mock Database (in-memory for demo)
# ============================================================================

# In-memory signal storage
SIGNALS_db: dict[int, dict[str, Any]] = {}
SIGNAL_COUNTER = 1


# ============================================================================
# API Functions
# ============================================================================

def _create_signal_from_input(
    input_data: SignalInput,
    agent_id: str = "T3-D6-A1",
) -> AnalysisSignal:
    """Create AnalysisSignal from input."""
    return AnalysisSignal(
        department_id=6,
        department_name="SMC/ICT Analysis",
        agent_id=agent_id,
        direction=input_data.direction,
        confidence=input_data.confidence,
        supporting_factors=[],
        key_levels=input_data.key_levels,
    )


def _parse_signals_input(
    signals_data: list[dict[str, Any]],
) -> list[AnalysisSignal]:
    """Parse signals from API input."""
    signals = []
    for i, s in enumerate(signals_data, 1):
        signals.append(AnalysisSignal(
            department_id=s.get("department_id", i),
            department_name=s.get("department_name", f"Department {i}"),
            agent_id=s.get("agent_id", f"T3-D{i}-A1"),
            direction=s.get("direction", "buy"),
            confidence=s.get("confidence", 70.0),
            supporting_factors=s.get("supporting_factors", []),
            key_levels=s.get("key_levels", {}),
        ))
    return signals


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/debate", response_model=DebateResponse, tags=["Signals"])
async def run_debate_endpoint(
    request: DebateRequestInput,
) -> DebateResponse:
    """
    Initiate and run Bull/Bear/Neutral debate.
    
    Runs full debate flow and returns decision.
    """
    # Get signals - use input or create sample
    if request.signals:
        signals = _parse_signals_input(request.signals)
    else:
        signals = create_sample_signals()
    
    # Create debate request
    debate_request = DebateRequest(
        signal_id=request.signal_id,
        symbol=request.symbol,
        sector=request.sector,
        current_price=request.current_price,
        signals=signals,
        key_levels=request.key_levels,
        checklist_score=request.checklist_score,
        current_spread=request.current_spread,
        historical_spread=request.historical_spread,
        portfolio_correlation=request.portfolio_correlation,
        strategy_tier=request.strategy_tier,
    )
    
    # Run debate
    orchestrator = DebateOrchestrator()
    result = await orchestrator.run_debate(debate_request)
    
    # Save transcript
    if result.completed_at and not result.error:
        transcript_data = orchestrator.create_transcript(debate_request, result)
        try:
            save_transcript(transcript_data)
        except Exception:
            pass  # Ignore save errors in demo
    
    # Build response
    return DebateResponse(
        signal_id=result.signal_id,
        symbol=result.symbol,
        decision=result.fund_manager_decision.decision,
        confidence=result.fund_manager_decision.confidence,
        position_size_multiplier=result.fund_manager_decision.position_size_multiplier,
        rationale=result.fund_manager_decision.rationale,
        bull_case=result.bull_case.to_dict(),
        bear_case=result.bear_case.to_dict(),
        neutral_case=result.neutral_case.to_dict(),
        validation={
            "checklist_passed": result.checklist_passed,
            "signal_not_expired": result.signal_not_expired,
            "confluence_met": result.confluence_met,
            "confidence_threshold_met": result.confidence_threshold_met,
        },
        duration_ms=result.duration_ms,
    )


@router.get("/{signal_id}", tags=["Signals"])
async def get_signal_endpoint(
    signal_id: int,
) -> dict[str, Any]:
    """Get signal with debate result by ID."""
    transcript = get_transcript_by_signal(signal_id)
    
    if transcript:
        return {
            "signal_id": signal_id,
            "transcript": transcript.to_dict(),
            "found": True,
        }
    
    return {
        "signal_id": signal_id,
        "transcript": None,
        "found": False,
    }


@router.get("", tags=["Signals"])
async def list_signals_endpoint(
    limit: int = 20,
    offset: int = 0,
    sector: Optional[str] = None,
    decision: Optional[str] = None,
) -> dict[str, Any]:
    """List signals with debate history."""
    transcripts = get_transcripts(
        limit=limit,
        offset=offset,
        sector=sector,
        decision=decision,
    )
    
    return {
        "count": len(transcripts),
        "signals": [t.to_dict() for t in transcripts],
    }


@router.get("/statistics", tags=["Signals"])
async def get_statistics_endpoint(
    days: int = 30,
) -> dict[str, Any]:
    """Get debate statistics."""
    stats = get_debate_statistics(days=days)
    
    return {
        "statistics": stats,
        "thresholds": {
            "min_confluence": MIN_CONFLUENCE_DEPARTMENTS,
            "checklist_threshold": CHECKLIST_THRESHOLD,
            "confidence_entry": CONFIDENCE_THRESHOLD_ENTRY,
            "confidence_full": CONFIDENCE_THRESHOLD_FULL,
        },
    }


@router.post("/checklist", response_model=ChecklistResponse, tags=["Signals"])
async def validate_checklist_endpoint(
    request: ChecklistInput,
) -> ChecklistResponse:
    """Validate pre-trade checklist."""
    # Calculate total score
    total = (
        request.kill_zone +
        request.structure_confirmed +
        request.ote_within_zone +
        request.ob_quality +
        request.liquidity_pool +
        request.adr_consumption +
        request.news_proximity +
        request.spread_check +
        request.regime_alignment
    )
    
    passed = total >= CHECKLIST_THRESHOLD
    
    return ChecklistResponse(
        signal_id=request.signal_id,
        total_score=float(total),
        passed=passed,
        items={
            "kill_zone": {"score": request.kill_zone, "label": "Kill zone active"},
            "structure_confirmed": {"score": request.structure_confirmed, "label": "Bull/Bear structure confirmed"},
            "ote_within_zone": {"score": request.ote_within_zone, "label": "OTE within zone"},
            "ob_quality": {"score": request.ob_quality, "label": "OB quality >= 3 or FVG >= 3"},
            "liquidity_pool": {"score": request.liquidity_pool, "label": "Liquidity pool identified"},
            "adr_consumption": {"score": request.adr_consumption, "label": "ADR consumption < 80%"},
            "news_proximity": {"score": request.news_proximity, "label": "No high-impact news within 30 min"},
            "spread_check": {"score": request.spread_check, "label": "Spread within normal range"},
            "regime_alignment": {"score": request.regime_alignment, "label": "Regime alignment confirmed"},
        },
    )


# ============================================================================
# Demo/Testing Functions
# ============================================================================

async def run_demo_debate(
    symbol: str = "EURUSD",
    sector: str = "forex",
) -> DebateResponse:
    """Run a demo debate with sample signals."""
    request = DebateRequestInput(
        signal_id=999,
        symbol=symbol,
        sector=sector,
        current_price=1.0920,
        checklist_score=8.0,
        strategy_tier="scalp",
    )
    return await run_debate_endpoint(request)


async def get_symbol_history(
    symbol: str,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Get debate history for a symbol."""
    return get_signal_history(symbol, days)