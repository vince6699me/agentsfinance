"""
Trade Signals Team - Bull/Bear/Neutral Debate Mechanism

Team 4: Trade Signals (Debate Mechanism)
- Bull Analyst argues LONG case
- Bear Analyst argues SHORT case
- Neutral/Risk Analyst stress-tests both cases
- Fund Manager produces final decision with confidence score

Debate Rules:
- Minimum confluence: 3 of 6 departments must provide supporting signals
- Confidence threshold: >= 65/100 for entry; >= 80/100 for full position
- Checklist gate: Pre-trade checklist must score >= 7/9 before debate
- Expired signals: Signals past confidence half-life not debated
- Debate transcript logged to database
"""

from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON


class DecisionDirection(str, Enum):
    """Trade direction enum."""
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"


class DebateRole(str, Enum):
    """Debate participant roles."""
    BULL_ANALYST = "bull_analyst"
    BEAR_ANALYST = "bear_analyst"
    NEUTRAL_ANALYST = "neutral_analyst"
    FUND_MANAGER = "fund_manager"


class ChecklistResult(Base):
    """Pre-trade checklist validator result."""
    __tablename__ = "checklist_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, nullable=False)
    total_score = Column(Float, nullable=False)  # 0-9
    passed = Column(Integer, nullable=False)  # 1=yes, 0=no
    
    # Individual checklist items (0 or 1)
    kill_zone = Column(Integer, default=0)
    structure_confirmed = Column(Integer, default=0)
    ote_within_zone = Column(Integer, default=0)
    ob_quality = Column(Integer, default=0)
    liquidity_pool = Column(Integer, default=0)
    adr_consumption = Column(Integer, default=0)
    news_proximity = Column(Integer, default=0)
    spread_check = Column(Integer, default=0)
    regime_alignment = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChecklistResult signal_id={self.signal_id} score={self.total_score}/9 passed={self.passed}>"


@dataclass
class AnalysisSignal:
    """Represents a signal from one of the 6 analysis departments."""
    department_id: int
    department_name: str
    agent_id: str
    direction: str  # "buy", "sell", "neutral"
    confidence: float  # 0-100
    supporting_factors: list[str] = field(default_factory=list)
    key_levels: dict[str, float] = field(default_factory=dict)
    strategy_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "department_id": self.department_id,
            "department_name": self.department_name,
            "agent_id": self.agent_id,
            "direction": self.direction,
            "confidence": self.confidence,
            "supporting_factors": self.supporting_factors,
            "key_levels": self.key_levels,
            "strategy_id": self.strategy_id,
            "created_at": self.created_at.isoformat(),
        }
    
    def is_supporting(self, direction: str) -> bool:
        """Check if signal supports the given direction."""
        return self.direction.lower() == direction.lower() and self.confidence >= 50


@dataclass
class BullCase:
    """Bull Analyst's LONG argument."""
    role: str = "bull_analyst"
    arguments: list[str] = field(default_factory=list)
    supporting_departments: list[int] = field(default_factory=list)
    confluence_count: int = 0
    upside_target: float = 0.0
    risk_reward: float = 0.0
    key_support_factors: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "arguments": self.arguments,
            "supporting_departments": self.supporting_departments,
            "confluence_count": self.confluence_count,
            "upside_target": self.upside_target,
            "risk_reward": self.risk_reward,
            "key_support_factors": self.key_support_factors,
        }


@dataclass
class BearCase:
    """Bear Analyst's SHORT argument."""
    role: str = "bear_analyst"
    arguments: list[str] = field(default_factory=list)
    counter_arguments: list[str] = field(default_factory=list)
    manipulation_risks: list[str] = field(default_factory=list)
    htf_structure_concerns: list[str] = field(default_factory=list)
    downside_target: float = 0.0
    risk_reward: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "arguments": self.arguments,
            "counter_arguments": self.counter_arguments,
            "manipulation_risks": self.manipulation_risks,
            "htf_structure_concerns": self.htf_structure_concerns,
            "downside_target": self.downside_target,
            "risk_reward": self.risk_reward,
        }


@dataclass
class NeutralCase:
    """Neutral/Risk Analyst's stress test."""
    role: str = "neutral_analyst"
    risk_assessment: dict[str, Any] = field(default_factory=dict)
    spread_analysis: dict[str, float] = field(default_factory=dict)
    correlation_check: dict[str, float] = field(default_factory=list)
    news_proximity: dict[str, Any] = field(default_factory=dict)
    checklist_score: float = 0.0
    risk_flags: list[str] = field(default_factory=list)
    position_adjustment: str = ""  # "reduce_50", "full_size", "skip"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "risk_assessment": self.risk_assessment,
            "spread_analysis": self.spread_analysis,
            "correlation_check": self.correlation_check,
            "news_proximity": self.news_proximity,
            "checklist_score": self.checklist_score,
            "risk_flags": self.risk_flags,
            "position_adjustment": self.position_adjustment,
        }


@dataclass
class FundManagerDecision:
    """Fund Manager's final decision."""
    role: str = "fund_manager"
    decision: str = "NO_TRADE"  # LONG, SHORT, NO_TRADE
    confidence: int = 0  # 0-100
    position_size_multiplier: float = 0.0  # 0.0 to 1.0
    rationale: str = ""
    key_decision_factors: list[str] = field(default_factory=list)
    risk_adjustments: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "decision": self.decision,
            "confidence": self.confidence,
            "position_size_multiplier": self.position_size_multiplier,
            "rationale": self.rationale,
            "key_decision_factors": self.key_decision_factors,
            "risk_adjustments": self.risk_adjustments,
        }
    
    def is_approved(self) -> bool:
        """Check if trade is approved (not NO_TRADE)."""
        return self.decision != "NO_TRADE"
    
    def is_full_position(self) -> bool:
        """Check if eligible for full position size."""
        return self.confidence >= 80
    
    def is_entry_eligible(self) -> bool:
        """Check if eligible for any entry."""
        return self.confidence >= 65 and self.decision != "NO_TRADE"


# ============================================================================
# Database Models
# ============================================================================

class DebateTranscript(Base):
    """Full debate transcript stored in database."""
    __tablename__ = "debate_transcripts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, nullable=False)
    
    # Sector and instrument
    sector = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)
    
    # Bull case
    bull_arguments = Column(JSON, default=list)
    bull_confluence = Column(Integer, default=0)
    bull_score = Column(Float, default=0.0)
    
    # Bear case
    bear_arguments = Column(JSON, default=list)
    bear_counter_arguments = Column(JSON, default=list)
    bear_score = Column(Float, default=0.0)
    
    # Neutral case
    neutral_checklist_score = Column(Float, default=0.0)
    neutral_risk_flags = Column(JSON, default=list)
    neutral_position_adjustment = Column(String(20), default="")
    
    # Fund Manager decision
    fund_manager_decision = Column(String(20), default="NO_TRADE")
    fund_manager_confidence = Column(Integer, default=0)
    fund_manager_rationale = Column(Text, default="")
    position_size_multiplier = Column(Float, default=0.0)
    
    # Metadata
    debate_duration_ms = Column(Integer, default=0)
    confluence_requirement_met = Column(Integer, default=0)  # 1=yes, 0=no
    confidence_threshold_met = Column(Integer, default=0)  # 1=yes, 0=no
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "sector": self.sector,
            "symbol": self.symbol,
            "bull_case": {
                "arguments": self.bull_arguments,
                "confluence": self.bull_confluence,
                "score": self.bull_score,
            },
            "bear_case": {
                "arguments": self.bear_arguments,
                "counter_arguments": self.bear_counter_arguments,
                "score": self.bear_score,
            },
            "neutral_case": {
                "checklist_score": self.neutral_checklist_score,
                "risk_flags": self.neutral_risk_flags,
                "position_adjustment": self.neutral_position_adjustment,
            },
            "fund_manager": {
                "decision": self.fund_manager_decision,
                "confidence": self.fund_manager_confidence,
                "rationale": self.fund_manager_rationale,
                "position_size_multiplier": self.position_size_multiplier,
            },
            "confluence_requirement_met": bool(self.confluence_requirement_met),
            "confidence_threshold_met": bool(self.confidence_threshold_met),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<DebateTranscript signal_id={self.signal_id} decision={self.fund_manager_decision} conf={self.fund_manager_confidence}>"


# ============================================================================
# Debate Rules Constants
# ============================================================================

DEPARTMENT_NAMES = {
    1: "Fundamental Analysis",
    2: "Technical Analysis",
    3: "Sentiment Analysis",
    4: "Intermarket Analysis",
    5: "Quantitative/Systematic",
    6: "SMC/ICT Analysis",
}


# Minimum confluence requirement (hard rule)
MIN_CONFLUENCE_DEPARTMENTS = 3  # 3 of 6 departments must support

# Confidence thresholds
CONFIDENCE_THRESHOLD_ENTRY = 65  # Minimum for entry
CONFIDENCE_THRESHOLD_FULL = 80  # Minimum for full position

# Checklist threshold
CHECKLIST_THRESHOLD = 7  # Minimum 7/9 to start debate

# Half-life in minutes by strategy tier
CONFIDENCE_HALF_LIFE = {
    "scalp": 15,
    "short_term": 60,
    "swing": 240,
    "position": 1440,
}


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_confluence(signals: list[AnalysisSignal], direction: str) -> int:
    """Calculate number of departments supporting a direction."""
    count = 0
    for signal in signals:
        if signal.is_supporting(direction):
            count += 1
    return count


def check_confluence_met(signals: list[AnalysisSignal], direction: str) -> bool:
    """Check if minimum confluence requirement is met."""
    return calculate_confluence(signals, direction) >= MIN_CONFLUENCE_DEPARTMENTS


def calculate_average_confidence(signals: list[AnalysisSignal], direction: str) -> float:
    """Calculate average confidence for supporting signals."""
    supporting = [s for s in signals if s.is_supporting(direction)]
    if not supporting:
        return 0.0
    return sum(s.confidence for s in supporting) / len(supporting)


def is_signal_expired(signal_created_at: datetime, strategy_tier: str = "scalp") -> bool:
    """Check if signal is past its confidence half-life."""
    half_life_minutes = CONFIDENCE_HALF_LIFE.get(strategy_tier, 15)
    age_minutes = (datetime.utcnow() - signal_created_at).total_seconds() / 60
    return age_minutes > half_life_minutes * 2  # 2 half-lives = expired


def assess_position_size(confidence: int) -> float:
    """Determine position size multiplier based on confidence."""
    if confidence >= 80:
        return 1.0  # Full position
    elif confidence >= 70:
        return 0.75  # 75% size
    elif confidence >= 65:
        return 0.5  # 50% size
    else:
        return 0.0  # No trade