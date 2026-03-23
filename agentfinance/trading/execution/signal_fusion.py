#!/usr/bin/env python3
"""
AgentFinance v3 — Signal Fusion Layer
======================================
Cross-agent confluence engine that combines signals from all 5 strategy agents
(22-26) into a single weighted confidence score before execution.

Flow:
    Agent 22 (SMC)     ─┐
    Agent 23 (Technical) ├─► signal_fusion.py ─► risk_manager.py ─► cTrader
    Agent 24 (Macro)    ├─► FusedSignal
    Agent 25 (Sentiment)─┤
    Agent 26 (News)     ─┘

Usage:
    from trading.execution.signal_fusion import SignalFusion, FusedSignal

    fusion = SignalFusion()
    result = fusion.fuse(symbol="EURUSD", timeframe="H1")

    if result.approved and result.confidence >= 0.65:
        risk_manager.check_risk(
            symbol=result.symbol,
            direction=result.direction,
            ...
        )
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("signal_fusion")

# ============================================================================
# WEIGHTS — tuned for FX intraday trading
# ============================================================================
# SMC is primary driver (40%) — our core edge
# Technical confirms the setup (25%) — momentum alignment
# Macro sets the regime direction (20%) — sector winds
# Sentiment provides edge confirmation (10%) — positioning clues
# News can block or boost (5%) — event risk only

AGENT_WEIGHTS = {
    22: 0.40,  # SMC Strategy
    23: 0.25,  # Technical Analysis
    24: 0.20,  # Fundamental/Macro
    25: 0.10,  # Sentiment
    26: 0.05,  # News Intelligence
}

# Minimum individual agent scores to count as "agreeing"
MIN_SCORE_THRESHOLD = 0.50


# ============================================================================
# DATA CLASSES
# ============================================================================


class Direction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class Regime(Enum):
    TRENDING = "TRENDING"  # ADX > 25 — breakout trades
    RANGING = "RANGING"  # ADX < 20 — mean reversion only
    TRANSITIONING = "TRANSITIONING"  # 20 <= ADX <= 25 — reduce size


@dataclass
class AgentSignal:
    """Signal output from a single agent."""

    agent_id: int
    direction: Direction
    score: float  # 0.0 - 1.0 confidence
    reasoning: str  # Short human-readable rationale
    metadata: Dict[str, Any]  # Agent-specific details
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_valid(self) -> bool:
        return self.score >= MIN_SCORE_THRESHOLD and self.direction != Direction.NEUTRAL


@dataclass
class VetoReason:
    """Reason why a signal was vetoed."""

    agent_id: int
    reason: str
    severity: str  # "hard" = block trade, "soft" = reduce confidence


@dataclass
class FusedSignal:
    """
    Final fused signal combining all agent inputs.

    composite_confidence: weighted average of all agent scores
    direction: consensus direction (BUY/SELL/NEUTRAL)
    components_agreeing: how many agents support the direction
    components_conflicting: how many agents oppose
    vetoes: hard veto reasons (trade blocked if any)
    warnings: soft veto reasons (reduce confidence)
    regime: detected market regime
    recommended_size: position size multiplier based on confluence
    """

    symbol: str
    timeframe: str
    direction: Direction
    composite_confidence: float
    smc_score: float
    technical_score: float
    macro_score: float
    sentiment_score: float
    news_score: float
    components_agreeing: int
    components_conflicting: int
    vetoes: List[VetoReason] = field(default_factory=list)
    warnings: List[VetoReason] = field(default_factory=list)
    regime: Regime = Regime.TRANSITIONING
    recommended_size: float = 1.0  # Multiplier: 0.0-1.0
    entry_zone: Optional[Dict] = None  # {min, max, ideal}
    stop_loss_pips: Optional[float] = None
    take_profit_pips: float = 0.0
    risk_reward_ratio: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def approved(self) -> bool:
        """True if the signal passes all veto checks and has minimum confidence."""
        if self.direction == Direction.NEUTRAL:
            return False
        if any(v.severity == "hard" for v in self.vetoes):
            return False
        if self.composite_confidence < 0.55:
            return False
        return True

    @property
    def veto_summary(self) -> str:
        if not self.vetoes:
            return "No vetoes"
        return "; ".join(f"[Agent-{v.agent_id}] {v.reason}" for v in self.vetoes)


# ============================================================================
# SIGNAL FUSION ENGINE
# ============================================================================


class SignalFusion:
    """
    Combines signals from all 5 strategy agents into a single FusedSignal.

    Pipeline:
        1. Fetch regime (ADX + ATR + BB width)
        2. Run all 5 agents in parallel
        3. Apply veto rules (hard + soft)
        4. Calculate weighted composite score
        5. Determine consensus direction
        6. Calculate recommended position size
    """

    def __init__(self, min_confidence: float = 0.55):
        self.min_confidence = min_confidence
        self._agent_cache: Dict[int, AgentSignal] = {}
        self._last_fetch: Optional[datetime] = None

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def fuse(self, symbol: str, timeframe: str = "H1") -> FusedSignal:
        """
        Main entry point — fetch and fuse all agent signals for a symbol.

        Args:
            symbol: Trading pair (e.g. "EURUSD")
            timeframe: Chart timeframe (e.g. "H1", "M15")

        Returns:
            FusedSignal with composite confidence, direction, and vetoes
        """
        logger.info(f"Fusing signals for {symbol} {timeframe}")

        # Step 1: Detect market regime (must do before running agents)
        regime = self._detect_regime(symbol, timeframe)
        logger.info(f"  Regime: {regime.value}")

        # Step 2: Run all agents
        smc_sig = self._run_agent_22_smc(symbol, timeframe, regime)
        tech_sig = self._run_agent_23_technical(symbol, timeframe)
        macro_sig = self._run_agent_24_macro(symbol, timeframe)
        sent_sig = self._run_agent_25_sentiment(symbol)
        news_sig = self._run_agent_26_news(symbol)

        agents = {
            22: smc_sig,
            23: tech_sig,
            24: macro_sig,
            25: sent_sig,
            26: news_sig,
        }

        # Step 3: Apply veto rules
        vetoes, warnings = self._check_vetoes(agents, regime)

        # Step 4: Count agreeing/conflicting agents
        agreeing, conflicting = self._count_direction_alignment(agents)

        # Step 5: Calculate composite score
        composite = self._calculate_composite(agents)

        # Step 6: Consensus direction
        direction = self._determine_direction(agents)

        # Step 7: Position size multiplier
        size_mult = self._calculate_size_multiplier(
            composite, agreeing, regime, vetoes, warnings
        )

        # Step 8: Build entry zone from SMC signal
        entry_zone = self._build_entry_zone(smc_sig, tech_sig)

        # Step 9: Build FusedSignal
        return FusedSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            composite_confidence=composite,
            smc_score=smc_sig.score if smc_sig else 0.0,
            technical_score=tech_sig.score if tech_sig else 0.0,
            macro_score=macro_sig.score if macro_sig else 0.0,
            sentiment_score=sent_sig.score if sent_sig else 0.0,
            news_score=news_sig.score if news_sig else 0.0,
            components_agreeing=agreeing,
            components_conflicting=conflicting,
            vetoes=vetoes,
            warnings=warnings,
            regime=regime,
            recommended_size=size_mult,
            entry_zone=entry_zone,
            metadata={
                "smc_reasoning": smc_sig.reasoning if smc_sig else "",
                "tech_reasoning": tech_sig.reasoning if tech_sig else "",
                "macro_reasoning": macro_sig.reasoning if macro_sig else "",
                "sentiment_reasoning": sent_sig.reasoning if sent_sig else "",
                "news_reasoning": news_sig.reasoning if news_sig else "",
            },
        )

    def fuse_quick(self, symbol: str, timeframe: str = "H1") -> FusedSignal:
        """
        Quick fusion — SMC only + regime check.
        Use when you need a fast decision without full agent analysis.
        """
        logger.info(f"Quick fuse for {symbol} {timeframe} (SMC + regime only)")

        regime = self._detect_regime(symbol, timeframe)
        smc_sig = self._run_agent_22_smc(symbol, timeframe, regime)
        macro_sig = self._run_agent_24_macro(symbol, timeframe)

        # Hard veto: macro regime conflicts with SMC direction
        vetoes: List[VetoReason] = []
        if macro_sig and smc_sig:
            if regime == Regime.RANGING and smc_sig.direction != Direction.NEUTRAL:
                # In ranging markets, only allow FVG (mean reversion) setups
                if "FVG" not in smc_sig.metadata.get("setup_types", []):
                    vetoes.append(
                        VetoReason(
                            agent_id=24,
                            reason="Ranging market + non-FVG SMC setup",
                            severity="hard",
                        )
                    )

        agreeing = 1 if smc_sig and smc_sig.is_valid() else 0
        composite = smc_sig.score * 0.7 + (macro_sig.score * 0.3 if macro_sig else 0)

        return FusedSignal(
            symbol=symbol,
            timeframe=timeframe,
            direction=smc_sig.direction if smc_sig else Direction.NEUTRAL,
            composite_confidence=composite,
            smc_score=smc_sig.score if smc_sig else 0.0,
            technical_score=0.0,
            macro_score=macro_sig.score if macro_sig else 0.0,
            sentiment_score=0.0,
            news_score=0.0,
            components_agreeing=agreeing,
            components_conflicting=0,
            vetoes=vetoes,
            regime=regime,
            recommended_size=composite * 0.7 if composite > 0 else 0.0,
        )

    # --------------------------------------------------------------------------
    # Regime Detection
    # --------------------------------------------------------------------------

    def _detect_regime(self, symbol: str, timeframe: str) -> Regime:
        """
        Detect market regime using ADX, ATR ratio, and Bollinger Band width.
        Must run before SMC analysis — SMC behaves very differently in ranging
        vs trending conditions.
        """
        try:
            from trading.engines.technical_engine import TechnicalEngine
            import pandas as pd

            engine = TechnicalEngine()
            data = engine.get_ohlcv(symbol, timeframe, count=100)

            if data is None or len(data) < 20:
                return Regime.TRANSITIONING

            close = data["close"]
            high = data["high"]
            low = data["low"]

            # ADX
            adx = engine.adx(data, period=14)
            adx_current = float(adx.iloc[-1]) if len(adx) > 0 else 25.0

            # ATR ratio (volatility)
            atr = engine.atr(data, period=14)
            atr_current = float(atr.iloc[-1]) if len(atr) > 0 else 0
            atr_ratio = (
                atr_current / float(close.iloc[-1])
                if float(close.iloc[-1]) > 0
                else 0.007
            )

            # Bollinger Band width (range vs volatility)
            sma = close.rolling(20).mean()
            std = close.rolling(20).std()
            bb_upper = sma + (2 * std)
            bb_lower = sma - (2 * std)
            bb_width = (
                float((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / float(close.iloc[-1]))
                if len(sma) > 0
                else 0.02
            )

            logger.debug(
                f"  Regime check: ADX={adx_current:.1f}, "
                f"ATR_ratio={atr_ratio:.4f}, BB_width={bb_width:.4f}"
            )

            if adx_current > 25 and atr_ratio > 0.007:
                return Regime.TRENDING
            elif adx_current < 20 and bb_width < 0.015:
                return Regime.RANGING
            else:
                return Regime.TRANSITIONING

        except ImportError:
            logger.warning("TechnicalEngine not available — using TRANSITIONING regime")
            return Regime.TRANSITIONING
        except Exception as e:
            logger.error(f"Regime detection failed: {e}")
            return Regime.TRANSITIONING

    # --------------------------------------------------------------------------
    # Agent Runners
    # --------------------------------------------------------------------------

    def _run_agent_22_smc(
        self, symbol: str, timeframe: str, regime: Regime
    ) -> Optional[AgentSignal]:
        """
        Agent 22 — SMC Strategy Engine.
        Primary signal source. Handles 40% weight.
        """
        try:
            from trading.engines.smc_engine import SMCEngine

            engine = SMCEngine()
            data = engine.get_data(symbol, timeframe)
            setups = engine.identify_setups(data)

            if not setups:
                return AgentSignal(
                    agent_id=22,
                    direction=Direction.NEUTRAL,
                    score=0.0,
                    reasoning="No SMC setups found",
                    metadata={"setup_types": []},
                )

            # Score based on setup quality and regime fit
            best = max(setups, key=lambda s: s.get("confidence", 0))
            score = best.get("confidence", 0.0)
            direction_str = best.get("direction", "NEUTRAL")
            direction = (
                Direction.BUY
                if direction_str == "BUY"
                else Direction.SELL
                if direction_str == "SELL"
                else Direction.NEUTRAL
            )

            # In RANGING markets, penalize non-FVG setups
            if regime == Regime.RANGING:
                setup_type = best.get("setup_type", "")
                if setup_type not in ("FVG", "MTS"):
                    score *= 0.5
                    reasoning = (
                        f"SMC setup found but penalised in ranging: {setup_type}"
                    )
                else:
                    reasoning = f"FVG/MTS in ranging — mean reversion trade"
            else:
                reasoning = f"SMC {best.get('setup_type', 'N/A')} setup: {direction_str} with {score:.0%} confidence"

            return AgentSignal(
                agent_id=22,
                direction=direction,
                score=score,
                reasoning=reasoning,
                metadata={
                    "setup_type": best.get("setup_type", ""),
                    "setup_types": [s.get("setup_type", "") for s in setups],
                    "entry_zone": best.get("entry_zone", {}),
                    "sl": best.get("stop_loss", 0),
                    "tp": best.get("take_profit", 0),
                },
            )

        except ImportError:
            logger.warning("SMCEngine not available for Agent 22")
            return None
        except Exception as e:
            logger.error(f"Agent 22 SMC analysis failed: {e}")
            return None

    def _run_agent_23_technical(
        self, symbol: str, timeframe: str
    ) -> Optional[AgentSignal]:
        """
        Agent 23 — Technical Analysis.
        Confirms SMC signal with momentum indicators. Weight: 25%.
        """
        try:
            from trading.engines.technical_engine import TechnicalEngine

            engine = TechnicalEngine()
            data = engine.get_ohlcv(symbol, timeframe, count=100)
            if data is None:
                return None

            scores = {}

            # Trend alignment (EMA crossover)
            ema_9 = engine.ema(data["close"], 9)
            ema_21 = engine.ema(data["close"], 21)
            if len(ema_9) >= 2 and len(ema_21) >= 2:
                if float(ema_9.iloc[-1]) > float(ema_21.iloc[-1]):
                    scores["bullish_trend"] = 0.7
                    direction = Direction.BUY
                else:
                    scores["bearish_trend"] = 0.7
                    direction = Direction.SELL

            # RSI confirmation
            rsi = engine.rsi(data["close"], 14)
            if len(rsi) >= 1:
                rsi_val = float(rsi.iloc[-1])
                if rsi_val < 30:
                    scores["rsi_oversold"] = 0.8
                elif rsi_val > 70:
                    scores["rsi_overbought"] = 0.8

            # MACD confirmation
            macd, signal_line, histogram = engine.macd(data["close"])
            if len(macd) >= 1:
                if float(macd.iloc[-1]) > float(signal_line.iloc[-1]):
                    scores["macd_bullish"] = 0.6
                else:
                    scores["macd_bearish"] = 0.6

            # Average score
            if not scores:
                avg_score = 0.3
                direction = Direction.NEUTRAL
                reasoning = "No technical signals"
            else:
                avg_score = sum(scores.values()) / len(scores)
                reasoning = f"Technical: {', '.join(scores.keys())}"

            return AgentSignal(
                agent_id=23,
                direction=direction,
                score=min(avg_score, 1.0),
                reasoning=reasoning,
                metadata={"indicator_scores": scores},
            )

        except ImportError:
            return None
        except Exception as e:
            logger.error(f"Agent 23 technical analysis failed: {e}")
            return None

    def _run_agent_24_macro(self, symbol: str, timeframe: str) -> Optional[AgentSignal]:
        """
        Agent 24 — Fundamental/Macro Analysis.
        Provides regime bias from economic data. Weight: 20%.
        """
        try:
            from trading.data.data_fetcher import DataFetcher

            fetcher = DataFetcher()
            macro = fetcher.get_macro_brief(symbol)

            if not macro:
                return AgentSignal(
                    agent_id=24,
                    direction=Direction.NEUTRAL,
                    score=0.3,
                    reasoning="No macro data available",
                    metadata={"regime": "UNKNOWN"},
                )

            regime_bias = macro.get("regime_bias", "NEUTRAL")
            score = macro.get("confidence", 0.5)
            direction = (
                Direction.BUY
                if regime_bias == "BULLISH"
                else Direction.SELL
                if regime_bias == "BEARISH"
                else Direction.NEUTRAL
            )

            return AgentSignal(
                agent_id=24,
                direction=direction,
                score=score,
                reasoning=f"Macro: {regime_bias} ({macro.get('key_events', 'no events')})",
                metadata=macro,
            )

        except ImportError:
            return None
        except Exception as e:
            logger.error(f"Agent 24 macro analysis failed: {e}")
            return None

    def _run_agent_25_sentiment(self, symbol: str) -> Optional[AgentSignal]:
        """
        Agent 25 — Sentiment Intelligence.
        FX positioning and retail sentiment. Weight: 10%.
        """
        try:
            # Try to import the sentiment agent
            sys.path.insert(
                0,
                os.path.join(
                    os.path.dirname(__file__), "..", "..", "agents", "trading"
                ),
            )
            from sentiment_intelligence import SentimentIntelligence

            agent = SentimentIntelligence()
            report = agent.get_composite(symbol)

            if not report:
                return AgentSignal(
                    agent_id=25,
                    direction=Direction.NEUTRAL,
                    score=0.3,
                    reasoning="No sentiment data",
                    metadata={},
                )

            direction_str = report.get("overall_bias", "NEUTRAL")
            direction = (
                Direction.BUY
                if direction_str == "BULLISH"
                else Direction.SELL
                if direction_str == "BEARISH"
                else Direction.NEUTRAL
            )

            return AgentSignal(
                agent_id=25,
                direction=direction,
                score=report.get("confidence", 0.5),
                reasoning=f"Sentiment: {report.get('description', 'mixed')}",
                metadata=report,
            )

        except (ImportError, TypeError):
            # sentiment_intelligence module not available — return neutral
            return AgentSignal(
                agent_id=25,
                direction=Direction.NEUTRAL,
                score=0.3,
                reasoning="Sentiment agent not available",
                metadata={},
            )
        except Exception as e:
            logger.error(f"Agent 25 sentiment analysis failed: {e}")
            return None

    def _run_agent_26_news(self, symbol: str) -> Optional[AgentSignal]:
        """
        Agent 26 — News Intelligence.
        Event risk and high-impact news. Weight: 5%.
        Can issue hard vetoes.
        """
        try:
            from news_intelligence import NewsIntelligence

            agent = NewsIntelligence()
            report = agent.get_event_risk(symbol)

            if not report:
                return AgentSignal(
                    agent_id=26,
                    direction=Direction.NEUTRAL,
                    score=0.3,
                    reasoning="No news events",
                    metadata={"high_impact_imminent": False},
                )

            # News is mostly a veto mechanism, not a directional signal
            if report.get("high_impact_imminent", False):
                # High-impact news = soft veto, reduce confidence significantly
                return AgentSignal(
                    agent_id=26,
                    direction=Direction.NEUTRAL,
                    score=0.2,
                    reasoning=f"⚠ HIGH IMPACT: {report.get('event', 'N/A')} at {report.get('time', 'N/A')}",
                    metadata={**report, "severity": "soft_veto"},
                )

            direction_str = report.get("bias", "NEUTRAL")
            direction = (
                Direction.BUY
                if direction_str == "BULLISH"
                else Direction.SELL
                if direction_str == "BEARISH"
                else Direction.NEUTRAL
            )

            return AgentSignal(
                agent_id=26,
                direction=direction,
                score=report.get("score", 0.4),
                reasoning=f"News: {report.get('summary', 'no significant news')}",
                metadata=report,
            )

        except (ImportError, TypeError):
            return AgentSignal(
                agent_id=26,
                direction=Direction.NEUTRAL,
                score=0.3,
                reasoning="News agent not available",
                metadata={"high_impact_imminent": False},
            )
        except Exception as e:
            logger.error(f"Agent 26 news analysis failed: {e}")
            return None

    # --------------------------------------------------------------------------
    # Fusion Logic
    # --------------------------------------------------------------------------

    def _check_vetoes(
        self, agents: Dict[int, AgentSignal], regime: Regime
    ) -> tuple[List[VetoReason], List[VetoReason]]:
        """
        Apply hard and soft veto rules.
        Hard veto = trade is blocked entirely.
        Soft veto = confidence penalty but not blocked.
        """
        vetoes: List[VetoReason] = []
        warnings: List[VetoReason] = []

        # News veto (Agent 26) — high impact event imminent
        news = agents.get(26)
        if news and news.metadata.get("high_impact_imminent", False):
            event = news.metadata.get("event", "unknown")
            vetoes.append(
                VetoReason(
                    agent_id=26,
                    reason=f"High-impact news event: {event}",
                    severity="hard",
                )
            )

        # Macro regime + SMC direction conflict
        macro = agents.get(24)
        smc = agents.get(22)
        if macro and smc:
            if regime == Regime.RANGING and smc.direction != Direction.NEUTRAL:
                setup_type = smc.metadata.get("setup_type", "")
                if setup_type not in ("FVG", "MTS"):
                    vetoes.append(
                        VetoReason(
                            agent_id=24,
                            reason=f"Stagflation/ranging regime + non-FVG SMC setup",
                            severity="hard",
                        )
                    )
            elif regime.value == "STAGFLATION" and smc.direction == Direction.BUY:
                vetoes.append(
                    VetoReason(
                        agent_id=24,
                        reason="Stagflation macro regime blocks long positions",
                        severity="hard",
                    )
                )

        # Stale data veto — if all agents returned 0.0 scores
        valid_signals = sum(1 for a in agents.values() if a and a.score > 0.1)
        if valid_signals < 2:
            warnings.append(
                VetoReason(
                    agent_id=0,
                    reason=f"Only {valid_signals} agent(s) returned valid signals",
                    severity="soft",
                )
            )

        return vetoes, warnings

    def _count_direction_alignment(
        self, agents: Dict[int, Optional[AgentSignal]]
    ) -> tuple[int, int]:
        """Count agents agreeing vs conflicting with SMC direction."""
        smc = agents.get(22)
        if not smc or smc.direction == Direction.NEUTRAL:
            return 0, 0

        smc_dir = smc.direction
        agreeing = 0
        conflicting = 0

        for agent_id, sig in agents.items():
            if agent_id == 22 or not sig:
                continue
            if sig.direction == smc_dir and sig.score >= MIN_SCORE_THRESHOLD:
                agreeing += 1
            elif sig.direction != Direction.NEUTRAL and sig.direction != smc_dir:
                if sig.score >= MIN_SCORE_THRESHOLD:
                    conflicting += 1

        return agreeing, conflicting

    def _calculate_composite(self, agents: Dict[int, Optional[AgentSignal]]) -> float:
        """Weighted average of all agent scores."""
        total_weight = 0.0
        weighted_sum = 0.0

        for agent_id, weight in AGENT_WEIGHTS.items():
            sig = agents.get(agent_id)
            if sig:
                weighted_sum += sig.score * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return min(weighted_sum / total_weight, 1.0)

    def _determine_direction(
        self, agents: Dict[int, Optional[AgentSignal]]
    ) -> Direction:
        """Determine consensus direction from weighted agent votes."""
        buy_weight = 0.0
        sell_weight = 0.0

        for agent_id, weight in AGENT_WEIGHTS.items():
            sig = agents.get(agent_id)
            if sig:
                if sig.direction == Direction.BUY:
                    buy_weight += weight * sig.score
                elif sig.direction == Direction.SELL:
                    sell_weight += weight * sig.score

        if abs(buy_weight - sell_weight) < 0.1:
            return Direction.NEUTRAL
        return Direction.BUY if buy_weight > sell_weight else Direction.SELL

    def _calculate_size_multiplier(
        self,
        composite: float,
        agreeing: int,
        regime: Regime,
        vetoes: List[VetoReason],
        warnings: List[VetoReason],
    ) -> float:
        """
        Calculate position size multiplier (0.0 - 1.0) based on:
        - Composite confidence
        - Number of agreeing agents
        - Market regime
        - Active vetoes/warnings
        """
        if not vetoes:
            size = composite
        else:
            size = composite * 0.3  # Hard vetoes cut size to 30%

        # Regime adjustment
        if regime == Regime.RANGING:
            size *= 0.5
        elif regime == Regime.TRANSITIONING:
            size *= 0.75

        # Agreement bonus
        if agreeing >= 3:
            size = min(size * 1.2, 1.0)
        elif agreeing == 2:
            size = min(size * 1.0, 1.0)
        elif agreeing == 1:
            size *= 0.7

        # Warning penalty
        size *= max(1.0 - (len(warnings) * 0.1), 0.3)

        return max(0.0, min(size, 1.0))

    def _build_entry_zone(
        self,
        smc_sig: Optional[AgentSignal],
        tech_sig: Optional[AgentSignal],
    ) -> Optional[Dict]:
        """Build entry zone from SMC + technical data."""
        if not smc_sig or not smc_sig.metadata:
            return None

        zone = smc_sig.metadata.get("entry_zone", {})
        if zone:
            return zone

        # Fallback: build from SMC data
        return {"source": "smc", "confidence": smc_sig.score}


# ============================================================================
# CLI
# ============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Signal Fusion Layer")
    parser.add_argument("symbol", help="Symbol (e.g. EURUSD)")
    parser.add_argument(
        "--timeframe",
        "-tf",
        default="H1",
        help="Timeframe (default: H1)",
    )
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick mode (SMC + regime only)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    )

    fusion = SignalFusion()
    if args.quick:
        result = fusion.fuse_quick(args.symbol, args.timeframe)
    else:
        result = fusion.fuse(args.symbol, args.timeframe)

    print(f"\n{'═' * 60}")
    print(f"  Signal Fusion — {result.symbol} {result.timeframe}")
    print(f"{'═' * 60}")
    print(f"  Direction:        {result.direction.value}")
    print(f"  Regime:           {result.regime.value}")
    print(f"  Composite Score: {result.composite_confidence:.0%}")
    print(
        f"  Agenting:         {result.components_agreeing} agree, {result.components_conflicting} conflict"
    )
    print(f"  SMC Score:        {result.smc_score:.0%}")
    print(f"  Tech Score:       {result.technical_score:.0%}")
    print(f"  Macro Score:      {result.macro_score:.0%}")
    print(f"  Sentiment Score:  {result.sentiment_score:.0%}")
    print(f"  News Score:       {result.news_score:.0%}")
    print(f"  Position Size:    {result.recommended_size:.0%}")
    print(f"  Status:           {'✓ APPROVED' if result.approved else '✗ BLOCKED'}")
    if result.vetoes:
        print(f"  Vetoes:          {result.veto_summary}")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
