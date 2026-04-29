"""
Trade Signals Team - Debate Transcript Logging

Logs debate transcripts to database and provides query functions.
Stores complete debate for audit and dashboard visibility.
"""

from datetime import datetime
from typing import Any, Optional, List
from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session, init_engine
from app.teams.signals.models import DebateTranscript


# ============================================================================
# Transcript Storage
# ============================================================================

def save_transcript(
    transcript_data: dict[str, Any],
    session: Optional[Session] = None,
) -> DebateTranscript:
    """
    Save debate transcript to database.
    
    Args:
        transcript_data: Dictionary with transcript fields
        session: Optional database session (creates one if not provided)
        
    Returns:
        Saved DebateTranscript object
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        transcript = DebateTranscript(**transcript_data)
        session.add(transcript)
        session.commit()
        session.refresh(transcript)
        
        if close_session:
            session.close()
        
        return transcript
    except Exception as e:
        session.rollback()
        if close_session:
            session.close()
        raise e


def save_transcripts_batch(
    transcripts: List[dict[str, Any]],
) -> List[DebateTranscript]:
    """
    Save multiple transcripts in batch.
    
    Args:
        transcripts: List of transcript dictionaries
        
    Returns:
        List of saved DebateTranscript objects
    """
    init_engine()
    with get_session() as session:
        saved = []
        for data in transcripts:
            transcript = DebateTranscript(**data)
            session.add(transcript)
            saved.append(transcript)
        
        session.commit()
        
        # Refresh all
        for transcript in saved:
            session.refresh(transcript)
        
        return saved


# ============================================================================
# Transcript Retrieval
# ============================================================================

def get_transcript_by_signal(
    signal_id: int,
    session: Optional[Session] = None,
) -> Optional[DebateTranscript]:
    """
    Get transcript for a specific signal.
    
    Args:
        signal_id: Signal ID
        session: Optional database session
        
    Returns:
        DebateTranscript or None if not found
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        result = session.execute(
            select(DebateTranscript)
            .where(DebateTranscript.signal_id == signal_id)
            .order_by(DebateTranscript.created_at.desc())
            .limit(1)
        )
        transcript = result.scalar_one_or_none()
        
        if close_session:
            session.close()
        
        return transcript
    except Exception as e:
        if close_session:
            session.close()
        raise e


def get_transcripts(
    limit: int = 20,
    offset: int = 0,
    sector: Optional[str] = None,
    decision: Optional[str] = None,
    session: Optional[Session] = None,
) -> List[DebateTranscript]:
    """
    Get debate transcripts with filters.
    
    Args:
        limit: Maximum transcripts to return
        offset: Offset for pagination
        sector: Filter by sector
        decision: Filter by decision (LONG/SHORT/NO_TRADE)
        session: Optional database session
        
    Returns:
        List of DebateTranscript objects
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        query = select(DebateTranscript)
        
        if sector:
            query = query.where(DebateTranscript.sector == sector)
        
        if decision:
            query = query.where(DebateTranscript.fund_manager_decision == decision)
        
        query = query.order_by(DebateTranscript.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = session.execute(query)
        transcripts = list(result.scalars().all())
        
        if close_session:
            session.close()
        
        return transcripts
    except Exception as e:
        if close_session:
            session.close()
        raise e


def get_recent_decisions(
    days: int = 7,
    limit: int = 50,
    session: Optional[Session] = None,
) -> List[dict[str, Any]]:
    """
    Get recent Fund Manager decisions.
    
    Args:
        days: Number of days to look back
        limit: Maximum results
        session: Optional database session
        
    Returns:
        List of decision dictionaries
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        # Calculate date threshold
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(DebateTranscript)
            .where(DebateTranscript.created_at >= threshold)
            .order_by(DebateTranscript.created_at.desc())
            .limit(limit)
        )
        
        result = session.execute(query)
        transcripts = list(result.scalars().all())
        
        if close_session:
            session.close()
        
        return [t.to_dict() for t in transcripts]
    except Exception as e:
        if close_session:
            session.close()
        raise e


# ============================================================================
# Statistics
# ============================================================================

def get_debate_statistics(
    days: int = 30,
    session: Optional[Session] = None,
) -> dict[str, Any]:
    """
    Get debate statistics for a period.
    
    Args:
        days: Number of days to analyze
        session: Optional database session
        
    Returns:
        Statistics dictionary
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(DebateTranscript)
            .where(DebateTranscript.created_at >= threshold)
        )
        
        result = session.execute(query)
        transcripts = list(result.scalars().all())
        
        if close_session:
            session.close()
        
        # Calculate statistics
        total = len(transcripts)
        long_count = sum(1 for t in transcripts if t.fund_manager_decision == "LONG")
        short_count = sum(1 for t in transcripts if t.fund_manager_decision == "SHORT")
        no_trade_count = sum(1 for t in transcripts if t.fund_manager_decision == "NO_TRADE")
        
        avg_confidence = (
            sum(t.fund_manager_confidence for t in transcripts) / total
            if total > 0 else 0
        )
        
        avg_duration = (
            sum(t.debate_duration_ms for t in transcripts) / total
            if total > 0 else 0
        )
        
        confluence_met = sum(1 for t in transcripts if t.confluence_requirement_met)
        
        return {
            "period_days": days,
            "total_debates": total,
            "long_count": long_count,
            "short_count": short_count,
            "no_trade_count": no_trade_count,
            "approval_rate": (long_count + short_count) / total if total > 0 else 0,
            "average_confidence": avg_confidence,
            "average_duration_ms": avg_duration,
            "confluence_met_pct": confluence_met / total if total > 0 else 0,
        }
    except Exception as e:
        if close_session:
            session.close()
        raise e


# ============================================================================
# Utility Functions
# ============================================================================

def transcript_to_dict(transcript: DebateTranscript) -> dict[str, Any]:
    """
    Convert transcript to dictionary with all nested data.
    
    Args:
        transcript: DebateTranscript object
        
    Returns:
        Full dictionary representation
    """
    return {
        "id": transcript.id,
        "signal_id": transcript.signal_id,
        "sector": transcript.sector,
        "symbol": transcript.symbol,
        "bull_case": {
            "arguments": transcript.bull_arguments,
            "confluence": transcript.bull_confluence,
            "score": transcript.bull_score,
        },
        "bear_case": {
            "arguments": transcript.bear_arguments,
            "counter_arguments": transcript.bear_counter_arguments,
            "score": transcript.bear_score,
        },
        "neutral_case": {
            "checklist_score": transcript.neutral_checklist_score,
            "risk_flags": transcript.neutral_risk_flags,
            "position_adjustment": transcript.neutral_position_adjustment,
        },
        "fund_manager": {
            "decision": transcript.fund_manager_decision,
            "confidence": transcript.fund_manager_confidence,
            "rationale": transcript.fund_manager_rationale,
            "position_size_multiplier": transcript.position_size_multiplier,
        },
        "validation": {
            "confluence_met": bool(transcript.confluence_requirement_met),
            "confidence_met": bool(transcript.confidence_threshold_met),
        },
        "metadata": {
            "duration_ms": transcript.debate_duration_ms,
            "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
        },
    }


def get_signal_history(
    symbol: str,
    days: int = 30,
    session: Optional[Session] = None,
) -> List[dict[str, Any]]:
    """
    Get debate history for a specific symbol.
    
    Args:
        symbol: Trading symbol
        days: Number of days to look back
        session: Optional database session
        
    Returns:
        List of historical debates
    """
    close_session = False
    if session is None:
        session = get_session().__enter__()
        close_session = True
    
    try:
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(DebateTranscript)
            .where(DebateTranscript.symbol == symbol)
            .where(DebateTranscript.created_at >= threshold)
            .order_by(DebateTranscript.created_at.desc())
        )
        
        result = session.execute(query)
        transcripts = list(result.scalars().all())
        
        if close_session:
            session.close()
        
        return [transcript_to_dict(t) for t in transcripts]
    except Exception as e:
        if close_session:
            session.close()
        raise e