"""
Trade Signals Team - Bull/Bear/Neutral/Fund Manager Roles

Each role implements the debate logic for their perspective:
- Bull Analyst: Argues LONG case with supporting analysis
- Bear Analyst: Argues SHORT case, challenges Bull
- Neutral/Risk Analyst: Stress-tests both cases
- Fund Manager: Synthesizes all cases for final decision
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
    DEPARTMENT_NAMES,
    MIN_CONFLUENCE_DEPARTMENTS,
    CONFIDENCE_THRESHOLD_ENTRY,
    CONFIDENCE_THRESHOLD_FULL,
)


# ============================================================================
# Bull Analyst Role
# ============================================================================

class BullAnalyst:
    """
    Bull Analyst - Argues the LONG/buy case.
    
    Responsibilities:
    - Cite supporting analysis from all 6 departments
    - Identify strongest confluence factors
    - Project upside target with probability
    """
    
    def __init__(self):
        self.role = "bull_analyst"
    
    def analyze(
        self,
        signals: list[AnalysisSignal],
        current_price: float,
        key_levels: dict[str, float],
    ) -> BullCase:
        """
        Analyze signals and build bull case.
        
        Args:
            signals: List of signals from all 6 departments
            current_price: Current market price
            key_levels: Key support/resistance levels
            
        Returns:
            BullCase with LONG arguments
        """
        bull_case = BullCase()
        
        # Find supporting signals
        for signal in signals:
            if signal.is_supporting("buy"):
                bull_case.supporting_departments.append(signal.department_id)
                
                # Add supporting factors
                for factor in signal.supporting_factors:
                    if factor not in bull_case.key_support_factors:
                        bull_case.key_support_factors.append(factor)
                
                # Add department to arguments
                dept_name = DEPARTMENT_NAMES.get(signal.department_id, f"Dept {signal.department_id}")
                bull_case.arguments.append(
                    f"{dept_name}: {signal.direction.upper()} with {signal.confidence:.0f}% confidence"
                )
        
        # Calculate confluence
        bull_case.confluence_count = len(set(bull_case.supporting_departments))
        
        # Project upside target
        if key_levels.get("take_profit"):
            bull_case.upside_target = key_levels["take_profit"]
        elif key_levels.get("resistance"):
            bull_case.upside_target = key_levels["resistance"]
        else:
            # Default: 2% upside for scalp
            bull_case.upside_target = current_price * 1.02
        
        # Calculate risk/reward
        if key_levels.get("stop_loss") and current_price > 0:
            risk = current_price - key_levels["stop_loss"]
            reward = bull_case.upside_target - current_price
            if risk > 0:
                bull_case.risk_reward = reward / risk
        
        # Build summary arguments
        if bull_case.confluence_count >= MIN_CONFLUENCE_DEPARTMENTS:
            bull_case.arguments.append(
                f"MINIMUM CONFLUENCE MET: {bull_case.confluence_count}/{MIN_CONFLUENCE_DEPARTMENTS} departments support LONG"
            )
        else:
            bull_case.arguments.append(
                f"CONFLUENCE WARNING: Only {bull_case.confluence_count}/{MIN_CONFLUENCE_DEPARTMENTS} departments support LONG"
            )
        
        return bull_case


# ============================================================================
# Bear Analyst Role
# ============================================================================

class BearAnalyst:
    """
    Bear Analyst - Argues the SHORT/sell case.
    
    Responsibilities:
    - Challenge the Bull case
    - Identify counter-signals
    - Stress-test setup against opposing HTF structure
    - Flag manipulation risk
    """
    
    def __init__(self):
        self.role = "bear_analyst"
    
    def analyze(
        self,
        signals: list[AnalysisSignal],
        current_price: float,
        key_levels: dict[str, float],
        bull_case: Optional[BullCase] = None,
    ) -> BearCase:
        """
        Analyze signals and build bear case.
        
        Args:
            signals: List of signals from all 6 departments
            current_price: Current market price
            key_levels: Key support/resistance levels
            bull_case: The bull case to counter
            
        Returns:
            BearCase with SHORT arguments
        """
        bear_case = BearCase()
        
        # Find counter-signals (sell signals or weak buy signals)
        for signal in signals:
            if signal.direction.lower() == "sell":
                # Add counter argument
                dept_name = DEPARTMENT_NAMES.get(signal.department_id, f"Dept {signal.department_id}")
                bear_case.arguments.append(
                    f"{dept_name}: SHORT signal with {signal.confidence:.0f}% confidence"
                )
            elif signal.direction.lower() == "neutral" or signal.confidence < 50:
                # Add as counter consideration
                bear_case.counter_arguments.append(
                    f"{DEPARTMENT_NAMES.get(signal.department_id)}: NEUTRAL or low confidence"
                )
        
        # Check for manipulation risks
        bear_case.manipulation_risks = self._assess_manipulation_risk(
            signals, key_levels
        )
        
        # Check HTF structure concerns
        bear_case.htf_structure_concerns = self._assess_htf_structure(key_levels)
        
        # Project downside target
        if key_levels.get("support"):
            bear_case.downside_target = key_levels["support"]
        elif key_levels.get("stop_loss"):
            bear_case.downside_target = key_levels["stop_loss"]
        else:
            # Default: 1.5% downside
            bear_case.downside_target = current_price * 0.985
        
        # Calculate risk/reward
        if key_levels.get("stop_loss") and current_price > 0:
            risk = key_levels["stop_loss"] - current_price
            reward = current_price - bear_case.downside_target
            if risk > 0:
                bear_case.risk_reward = reward / risk
        
        # If bull case exists, counter their arguments
        if bull_case and bull_case.arguments:
            bear_case.counter_arguments.append(
                f"Bull case confluence: {bull_case.confluence_count} departments"
            )
        
        return bear_case
    
    def _assess_manipulation_risk(
        self,
        signals: list[AnalysisSignal],
        key_levels: dict[str, float],
    ) -> list[str]:
        """Assess potential manipulation risks."""
        risks = []
        
        # Check for liquidity grab patterns
        if key_levels.get("liquidity_sweep"):
            risks.append("Potential liquidity sweep - false breakout risk")
        
        # Check for tight stops near round numbers
        if key_levels.get("stop_loss"):
            stop = key_levels["stop_loss"]
            if stop % 100 < 5 or stop % 100 > 95:
                risks.append("Stop near round number - susceptibility to stop hunting")
        
        # Check for low volume signals
        low_volume_count = sum(1 for s in signals if getattr(s, 'volume', 0) < 1000)
        if low_volume_count > len(signals) // 2:
            risks.append("Multiple low-volume signals - manipulation risk elevated")
        
        return risks
    
    def _assess_htf_structure(self, key_levels: dict[str, float]) -> list[str]:
        """Check HTF (higher timeframe) structure concerns."""
        concerns = []
        
        # Check for opposing HTF trend
        if key_levels.get("htf_trend") == "bearish":
            concerns.append("HTF structure bearish - counter-trend trade risk")
        
        # Check for weak HTF structure
        if key_levels.get("htf_strength", 0) < 60:
            concerns.append(f"HTF structure weak (strength: {key_levels.get('htf_strength')})")
        
        return concerns


# ============================================================================
# Neutral/Risk Analyst Role
# ============================================================================

class NeutralAnalyst:
    """
    Neutral/Risk Analyst - Stress-tests both cases.
    
    Responsibilities:
    - Evaluate overall risk
    - Check spread, correlation, news proximity
    - Apply Checklist Validator scores
    - Recommend position adjustment
    """
    
    def __init__(self):
        self.role = "neutral_analyst"
    
    def analyze(
        self,
        signals: list[AnalysisSignal],
        current_spread: float,
        historical_spread: float,
        portfolio_correlation: float = 0.0,
        news_events: list[dict[str, Any]] = None,
        checklist_score: float = 9.0,
    ) -> NeutralCase:
        """
        Analyze risk factors and build neutral assessment.
        
        Args:
            signals: List of signals from all departments
            current_spread: Current bid-ask spread
            historical_spread: Average historical spread
            portfolio_correlation: Current portfolio correlation
            news_events: Upcoming high-impact news events
            checklist_score: Pre-trade checklist score (0-9)
            
        Returns:
            NeutralCase with risk assessment
        """
        neutral_case = NeutralCase()
        
        # Store checklist score
        neutral_case.checklist_score = checklist_score
        
        # Spread analysis
        neutral_case.spread_analysis = {
            "current": current_spread,
            "historical": historical_spread,
            "ratio": current_spread / historical_spread if historical_spread > 0 else 1.0,
        }
        
        # Correlation check
        neutral_case.correlation_check = {
            "current": portfolio_correlation,
            "threshold": 0.7,
            "action_required": portfolio_correlation > 0.7,
        }
        
        # News proximity check
        news_proximity = self._check_news_proximity(news_events or [])
        neutral_case.news_proximity = news_proximity
        
        # Build risk assessment
        neutral_case.risk_assessment = {
            "spread_risk": current_spread > historical_spread * 2,
            "correlation_risk": portfolio_correlation > 0.7,
            "news_risk": news_proximity.get("high_impact_within_30min", False),
            "checklist_passed": checklist_score >= 7.0,
        }
        
        # Identify risk flags
        neutral_case.risk_flags = []
        
        if current_spread > historical_spread * 2:
            neutral_case.risk_flags.append("SPREAD: >2x historical average")
        
        if portfolio_correlation > 0.7:
            neutral_case.risk_flags.append(f"CORRELATION: {portfolio_correlation:.2f} > 0.70 threshold")
        
        if news_proximity.get("high_impact_within_30min"):
            neutral_case.risk_flags.append(f"NEWS: {news_proximity.get('event_name')} within 30 min")
        
        if checklist_score < 7.0:
            neutral_case.risk_flags.append(f"CHECKLIST: {checklist_score:.0f}/9 below threshold")
        
        # Determine position adjustment
        neutral_case.position_adjustment = self._calculate_position_adjustment(
            neutral_case.risk_flags,
            checklist_score,
            portfolio_correlation,
        )
        
        return neutral_case
    
    def _check_news_proximity(self, news_events: list[dict[str, Any]]) -> dict[str, Any]:
        """Check for high-impact news events near current time."""
        if not news_events:
            return {"high_impact_within_30min": False, "events": []}
        
        now = datetime.utcnow()
        high_impact_events = []
        
        for event in news_events:
            if event.get("impact") == "high":
                event_time = event.get("event_time", now)
                minutes_until = (event_time - now).total_seconds() / 60
                
                if minutes_until <= 30 and minutes_until >= -30:
                    high_impact_events.append({
                        "name": event.get("name"),
                        "minutes_until": minutes_until,
                    })
        
        return {
            "high_impact_within_30min": len(high_impact_events) > 0,
            "events": high_impact_events,
        }
    
    def _calculate_position_adjustment(
        self,
        risk_flags: list[str],
        checklist_score: float,
        correlation: float,
    ) -> str:
        """Calculate position size adjustment based on risk factors."""
        # Count serious risk flags
        serious_flags = [
            f for f in risk_flags
            if "CHECKLIST" not in f and "NEWS" not in f
        ]
        
        if len(serious_flags) >= 2:
            return "skip"
        
        if checklist_score < 7.0:
            return "skip"
        
        if correlation > 0.85:
            return "skip"
        
        if correlation > 0.7:
            return "reduce_50"
        
        if len(risk_flags) >= 1:
            return "reduce_25"
        
        return "full_size"


# ============================================================================
# Fund Manager Role
# ============================================================================

class FundManager:
    """
    Fund Manager - Final decision maker.
    
    Responsibilities:
    - Synthesize all three cases
    - Produce final LONG/SHORT/NO TRADE decision
    - Set confidence score (0-100)
    - Set position parameters
    """
    
    def __init__(self):
        self.role = "fund_manager"
    
    def decide(
        self,
        bull_case: BullCase,
        bear_case: BearCase,
        neutral_case: NeutralCase,
        signals: list[AnalysisSignal],
    ) -> FundManagerDecision:
        """
        Synthesize all cases and produce final decision.
        
        Args:
            bull_case: Bull analyst's argument
            bear_case: Bear analyst's argument
            neutral_case: Neutral analyst's risk assessment
            signals: All department signals
            
        Returns:
            FundManagerDecision with final trade decision
        """
        decision = FundManagerDecision()
        
        # Calculate supporting counts
        bull_support = bull_case.confluence_count
        bear_depts = set()
        
        for signal in signals:
            if signal.direction.lower() == "sell":
                bear_depts.add(signal.department_id)
        
        bear_support = len(bear_depts)
        
        # Check if neutral says skip
        if neutral_case.position_adjustment == "skip":
            decision.decision = "NO_TRADE"
            decision.confidence = 0
            decision.rationale = f"NEUTRAL RISK: {', '.join(neutral_case.risk_flags)}"
            decision.key_decision_factors = neutral_case.risk_flags
            return decision
        
        # Determine direction based on confluence
        if bull_support >= MIN_CONFLUENCE_DEPARTMENTS and bull_support > bear_support:
            # Bull has stronger case
            decision.decision = "LONG"
            decision.confidence = self._calculate_confidence(
                bull_case,
                neutral_case,
                signals,
            )
        elif bear_support >= MIN_CONFLUENCE_DEPARTMENTS and bear_support > bull_support:
            # Bear has stronger case
            decision.decision = "SHORT"
            decision.confidence = self._calculate_confidence(
                bear_case,
                neutral_case,
                signals,
            )
        else:
            # No clear winner - check if either side meets minimum
            if bull_support >= MIN_CONFLUENCE_DEPARTMENTS:
                decision.decision = "LONG"
                decision.confidence = self._calculate_confidence(
                    bull_case,
                    neutral_case,
                    signals,
                )
            elif bear_support >= MIN_CONFLUENCE_DEPARTMENTS:
                decision.decision = "SHORT"
                decision.confidence = self._calculate_confidence(
                    bull_case,
                    neutral_case,
                    signals,
                )
            else:
                # No trade - insufficient confluence
                decision.decision = "NO_TRADE"
                decision.confidence = max(bull_support, bear_support) * 10  # Scale 0-60
                decision.rationale = f"INSUFFICIENT CONFLUENCE: Bull={bull_support}, Bear={bear_support}, Required={MIN_CONFLUENCE_DEPARTMENTS}"
        
        # Set position size multiplier
        if decision.confidence >= CONFIDENCE_THRESHOLD_FULL:
            decision.position_size_multiplier = 1.0
        elif decision.confidence >= CONFIDENCE_THRESHOLD_ENTRY:
            # Apply neutral adjustments
            adj = neutral_case.position_adjustment
            if adj == "reduce_50":
                decision.position_size_multiplier = 0.5
            elif adj == "reduce_25":
                decision.position_size_multiplier = 0.75
            else:
                decision.position_size_multiplier = 0.75
        else:
            decision.position_size_multiplier = 0.0
        
        # Build rationale
        decision.rationale = self._build_rationale(
            decision.decision,
            decision.confidence,
            bull_case,
            bear_case,
            neutral_case,
            bull_support,
            bear_support,
        )
        
        # Key decision factors
        decision.key_decision_factors = [
            f"Bull confluence: {bull_support}/6 departments",
            f"Bear confluence: {bear_support}/6 departments",
            f"Checklist: {neutral_case.checklist_score:.0f}/9",
            f"Position adjustment: {neutral_case.position_adjustment}",
        ]
        
        # Risk adjustments from neutral
        for flag in neutral_case.risk_flags:
            if flag not in decision.risk_adjustments:
                decision.risk_adjustments.append(flag)
        
        return decision
    
    def _calculate_confidence(
        self,
        case: BullCase | BearCase,
        neutral_case: NeutralCase,
        signals: list[AnalysisSignal],
    ) -> int:
        """Calculate confidence score (0-100)."""
        # Base confidence from case
        base_conf = 50
        
        # Add confluence bonus
        if isinstance(case, BullCase):
            base_conf += case.confluence_count * 8  # Max +48
        else:
            # Bear case - use counter-argument count
            base_conf += len(case.arguments) * 5
        
        # Add risk/reward bonus
        if case.risk_reward >= 2.0:
            base_conf += 15
        elif case.risk_reward >= 1.5:
            base_conf += 10
        elif case.risk_reward >= 1.0:
            base_conf += 5
        
        # Apply neutral checklist penalty
        if neutral_case.checklist_score < 9.0:
            base_conf -= (9.0 - neutral_case.checklist_score) * 5
        
        # Apply risk flag penalty
        base_conf -= len(neutral_case.risk_flags) * 5
        
        return max(0, min(100, int(base_conf)))
    
    def _build_rationale(
        self,
        decision: str,
        confidence: int,
        bull_case: BullCase,
        bear_case: BearCase,
        neutral_case: NeutralCase,
        bull_support: int,
        bear_support: int,
    ) -> str:
        """Build decision rationale string."""
        parts = []
        
        if decision == "LONG":
            parts.append(f"LONG approved based on {bull_support}/6 department confluence")
        elif decision == "SHORT":
            parts.append(f"SHORT approved based on {bear_support}/6 department confluence")
        else:
            return f"NO TRADE: Insufficient confluence (Bull: {bull_support}, Bear: {bear_support})"
        
        parts.append(f"Confidence: {confidence}/100")
        
        if neutral_case.checklist_score > 0:
            parts.append(f"Checklist: {neutral_case.checklist_score:.0f}/9")
        
        if neutral_case.risk_flags:
            parts.append(f"Risk flags: {len(neutral_case.risk_flags)}")
        
        if confidence >= CONFIDENCE_THRESHOLD_FULL:
            parts.append("Full position size approved")
        elif confidence >= CONFIDENCE_THRESHOLD_ENTRY:
            parts.append("Reduced position size")
        
        return "; ".join(parts)