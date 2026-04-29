"""
Trade Signals Team (Team 4)

Bull/Bear/Neutral Debate Mechanism:

Roles:
- Bull Analyst: Argues LONG case
- Bear Analyst: Argues SHORT case
- Neutral/Risk Analyst: Stress-tests both cases
- Fund Manager: Produces final decision with confidence score

Debate Rules:
- Minimum confluence: 3 of 6 departments must provide supporting signals
- Confidence threshold: >= 65/100 for entry; >= 80/100 for full position
- Checklist gate: Pre-trade checklist must score >= 7/9 before debate
- Expired signals: Signals past confidence half-life not debated
- Debate transcript logged to database
"""

from app.teams.signals.models import (
    # Enums
    DecisionDirection,
    DebateRole,
    # Data classes
    AnalysisSignal,
    BullCase,
    BearCase,
    NeutralCase,
    FundManagerDecision,
    # Database models
    DebateTranscript,
    ChecklistResult,
    # Constants
    DEPARTMENT_NAMES,
    MIN_CONFLUENCE_DEPARTMENTS,
    CONFIDENCE_THRESHOLD_ENTRY,
    CONFIDENCE_THRESHOLD_FULL,
    CHECKLIST_THRESHOLD,
    CONFIDENCE_HALF_LIFE,
    # Helper functions
    calculate_confluence,
    check_confluence_met,
    calculate_average_confidence,
    is_signal_expired,
    assess_position_size,
)

from app.teams.signals.roles import (
    BullAnalyst,
    BearAnalyst,
    NeutralAnalyst,
    FundManager,
)

from app.teams.signals.debate import (
    DebateConfig,
    DebateRequest,
    DebateResult,
    DebateOrchestrator,
    run_debate,
    create_sample_signals,
    create_sample_request,
)

from app.teams.signals.transcript import (
    save_transcript,
    save_transcripts_batch,
    get_transcript_by_signal,
    get_transcripts,
    get_recent_decisions,
    get_debate_statistics,
    transcript_to_dict,
    get_signal_history,
)


__all__ = [
    # Enums
    "DecisionDirection",
    "DebateRole",
    # Data classes
    "AnalysisSignal",
    "BullCase",
    "BearCase",
    "NeutralCase",
    "FundManagerDecision",
    # Database models
    "DebateTranscript",
    "ChecklistResult",
    # Constants
    "DEPARTMENT_NAMES",
    "MIN_CONFLUENCE_DEPARTMENTS",
    "CONFIDENCE_THRESHOLD_ENTRY",
    "CONFIDENCE_THRESHOLD_FULL",
    "CHECKLIST_THRESHOLD",
    "CONFIDENCE_HALF_LIFE",
    # Helper functions
    "calculate_confluence",
    "check_confluence_met",
    "calculate_average_confidence",
    "is_signal_expired",
    "assess_position_size",
    # Roles
    "BullAnalyst",
    "BearAnalyst",
    "NeutralAnalyst",
    "FundManager",
    # Debate
    "DebateConfig",
    "DebateRequest",
    "DebateResult",
    "DebateOrchestrator",
    "run_debate",
    "create_sample_signals",
    "create_sample_request",
    # Transcript
    "save_transcript",
    "save_transcripts_batch",
    "get_transcript_by_signal",
    "get_transcripts",
    "get_recent_decisions",
    "get_debate_statistics",
    "transcript_to_dict",
    "get_signal_history",
]


# Team configuration
TEAM_ID = "T4"
TEAM_NAME = "Trade Signals"
TEAM_DESCRIPTION = "Bull/Bear/Neutral debate → Fund Manager decision"


# Default configuration
DEFAULT_CONFIG = DebateConfig()