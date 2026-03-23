#!/usr/bin/env python3
"""
AgentFinance Kill Zones & COT Analysis Module
Session timing, COT report analysis, and special pattern detection.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# DATA CLASSES
# ============================================================================


class SessionType(Enum):
    ASIAN = "Asian"
    LONDON_OPEN = "London Open"
    LONDON = "London"
    NEW_YORK = "New York"
    LONDON_CLOSE = "London Close"
    NY_CLOSE = "NY Close"


class COTSignal(Enum):
    EXTREME_BULLISH = "EXTREME_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    EXTREME_BEARISH = "EXTREME_BEARISH"


@dataclass
class KillZone:
    """Active trading session information."""

    name: str
    session_type: SessionType
    start_est: str
    end_est: str
    pairs: List[str]
    description: str
    active: bool
    priority: str  # "HIGH", "MEDIUM", "LOW"
    volatility_expectation: str  # "LOW", "MEDIUM", "HIGH"


@dataclass
class COTAnalysis:
    """CFTC Commitment of Traders analysis result."""

    symbol: str
    report_date: datetime
    commercial_long: float
    commercial_short: float
    large_spec_long: float
    large_spec_short: float
    net_commercial: float
    net_large_spec: float
    commercial_percentile: float
    large_spec_percentile: float
    signal: COTSignal
    extreme: bool
    positioning_trend: str  # "INCREASING_LONG", "DECREASING_LONG", "INCREASING_SHORT", "DECREASING_SHORT"


@dataclass
class SentimentScore:
    """Composite sentiment from multiple sources."""

    symbol: str
    timestamp: datetime
    cot_weighted: float  # -1 to 1
    options_weighted: float
    news_weighted: float
    social_weighted: float
    retail_weighted: float
    composite: float  # -1 to 1
    interpretation: str  # "EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"


# ============================================================================
# KILL ZONES
# ============================================================================

# Session definitions in EST
SESSIONS = {
    SessionType.ASIAN: {
        "start": "21:00",  # Previous day
        "end": "04:00",
        "pairs": ["AUDJPY", "USDJPY", "AUDUSD", "NZDUSD"],
        "description": "Low volatility consolidation, range-bound",
        "priority": "LOW",
        "volatility": "LOW",
    },
    SessionType.LONDON_OPEN: {
        "start": "02:50",
        "end": "04:00",
        "pairs": ["GBPUSD", "EURGBP", "EURUSD", "GBPJPY"],
        "description": "High volatility spike, trend initiation",
        "priority": "HIGH",
        "volatility": "HIGH",
    },
    SessionType.LONDON: {
        "start": "03:00",
        "end": "12:00",
        "pairs": ["EURUSD", "GBPUSD", "EURJPY", "GBPJPY"],
        "description": "Continuous liquidity, kill zones at 03:00, 10:30",
        "priority": "HIGH",
        "volatility": "MEDIUM",
    },
    SessionType.NEW_YORK: {
        "start": "08:00",
        "end": "17:00",
        "pairs": ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"],
        "description": "High impact overlap 08:00-12:00, US session close",
        "priority": "HIGH",
        "volatility": "HIGH",
    },
    SessionType.LONDON_CLOSE: {
        "start": "10:30",
        "end": "11:00",
        "pairs": ["EURUSD", "GBPUSD"],
        "description": "Stop runs, liquidity sweeps, reversal zones",
        "priority": "HIGH",
        "volatility": "MEDIUM",
    },
    SessionType.NY_CLOSE: {
        "start": "16:00",
        "end": "17:00",
        "pairs": ["All majors"],
        "description": "Avoid trading - low liquidity, erratic price action",
        "priority": "LOW",
        "volatility": "LOW",
    },
}

# Trading pairs by session preference
SESSION_PAIRS = {
    "London Open": ["GBPUSD", "EURGBP", "EURUSD", "GBPJPY", "USDCHF"],
    "London": ["EURUSD", "GBPUSD", "EURJPY", "GBPJPY", "EURGBP", "USDCHF"],
    "New York AM": ["EURUSD", "GBPUSD", "USDCAD", "USDJPY", "AUDUSD"],
    "New York PM": ["EURUSD", "GBPUSD", "USDCAD"],
    "London Close": ["EURUSD", "GBPUSD"],
    "Asian": ["USDJPY", "AUDUSD", "NZDUSD", "AUDJPY"],
}


def get_est_time(utc_time: Optional[datetime] = None) -> datetime:
    """Convert UTC to EST/EDT."""
    if utc_time is None:
        utc_time = datetime.now(timezone.utc)

    # EST is UTC-5, EDT is UTC-4 (approx March-November)
    est_offset = -5 if (utc_time.month < 3 or utc_time.month > 11) else -4
    return utc_time + timedelta(hours=est_offset)


def get_active_sessions(utc_time: Optional[datetime] = None) -> List[KillZone]:
    """Get all currently active trading sessions."""
    est_time = get_est_time(utc_time)
    current_time_str = est_time.strftime("%H:%M")

    active_sessions = []

    for session_type, session_data in SESSIONS.items():
        start = session_data["start"]
        end = session_data["end"]

        # Handle overnight sessions
        if start > end:
            is_active = current_time_str >= start or current_time_str <= end
        else:
            is_active = start <= current_time_str <= end

        if is_active:
            active_sessions.append(
                KillZone(
                    name=session_data["description"],
                    session_type=session_type,
                    start_est=start,
                    end_est=end,
                    pairs=session_data["pairs"],
                    description=session_data["description"],
                    active=True,
                    priority=session_data["priority"],
                    volatility_expectation=session_data["volatility"],
                )
            )

    return active_sessions


def get_best_pairs_for_session(session: SessionType) -> List[str]:
    """Get the best pairs to trade during a specific session."""
    session_name = session.value

    # Map session types to pair lists
    pair_map = {
        "London Open": ["GBPUSD", "EURGBP", "EURUSD", "GBPJPY"],
        "London": ["EURUSD", "GBPUSD", "EURJPY", "GBPJPY", "EURGBP"],
        "New York": ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD"],
        "London Close": ["EURUSD", "GBPUSD"],
        "Asian": ["USDJPY", "AUDUSD", "NZDUSD"],
        "NY Close": [],
    }

    return pair_map.get(session_name, [])


def get_next_session_start(
    utc_time: Optional[datetime] = None,
) -> Tuple[SessionType, datetime, timedelta]:
    """Get the next session start time and countdown."""
    if utc_time is None:
        utc_time = datetime.now(timezone.utc)

    est_time = get_est_time(utc_time)
    current_time = est_time.time()

    # Check each session
    next_session = None
    next_start = None
    min_diff = timedelta(days=1)

    for session_type, session_data in SESSIONS.items():
        start_str = session_data["start"]
        start = datetime.strptime(start_str, "%H:%M").time()

        # Handle overnight
        if session_data["start"] > session_data["end"]:
            if current_time >= start:
                # Next day
                next_start_dt = datetime.combine(
                    est_time.date() + timedelta(days=1), start
                )
            else:
                # Same day
                next_start_dt = datetime.combine(est_time.date(), start)
        else:
            if current_time <= start:
                next_start_dt = datetime.combine(est_time.date(), start)
            else:
                continue

        diff = next_start_dt - est_time
        if 0 < diff < min_diff:
            min_diff = diff
            next_session = session_type
            next_start = next_start_dt

    return next_session, next_start, min_diff if next_start else timedelta(days=1)


def get_session_bias(session: SessionType) -> Dict:
    """
    Get typical price behavior patterns for a session.
    Based on historical ICT analysis.
    """
    biases = {
        SessionType.ASIAN: {
            "direction": "RANGE_BOUND",
            "typical_move": "20-40 pips",
            "stop_hunts": "Both directions possible",
            "strategy": "Range trading with tight stops",
        },
        SessionType.LONDON_OPEN: {
            "direction": "TREND_INITIATION",
            "typical_move": "40-80 pips",
            "stop_hunts": "Common - false breakouts",
            "strategy": "Wait for first move, fade the spike",
        },
        SessionType.LONDON: {
            "direction": "MIXED",
            "typical_move": "30-60 pips",
            "stop_hunts": "Common at highs/lows",
            "strategy": "Trade kill zones, fade momentum",
        },
        SessionType.NEW_YORK: {
            "direction": "VOLATILE",
            "typical_move": "50-100 pips",
            "stop_hunts": "Frequent around data",
            "strategy": "Trade with momentum, avoid around news",
        },
        SessionType.LONDON_CLOSE: {
            "direction": "REVERSAL",
            "typical_move": "30-50 pips",
            "stop_hunts": "Both sides common",
            "strategy": "Counter-trend entries",
        },
        SessionType.NY_CLOSE: {
            "direction": "LOW_LIQUIDITY",
            "typical_move": "Erratic",
            "stop_hunts": "Frequent",
            "strategy": "AVOID TRADING",
        },
    }

    return biases.get(session, {})


# ============================================================================
# COT ANALYSIS
# ============================================================================


def analyze_cot_positioning(
    symbol: str, cot_data: pd.DataFrame, lookback_weeks: int = 52
) -> COTAnalysis:
    """
    Analyze CFTC COT report data for positioning extremes.

    Args:
        symbol: Trading symbol (e.g., "EUR", "GBP")
        cot_data: DataFrame with columns: date, commercial_long, commercial_short,
                  large_spec_long, large_spec_short
        lookback_weeks: Number of weeks for percentile calculation

    Returns:
        COTAnalysis object
    """
    if len(cot_data) < 10:
        return COTAnalysis(
            symbol=symbol,
            report_date=datetime.now(timezone.utc),
            commercial_long=0,
            commercial_short=0,
            large_spec_long=0,
            large_spec_short=0,
            net_commercial=0,
            net_large_spec=0,
            commercial_percentile=50,
            large_spec_percentile=50,
            signal=COTSignal.NEUTRAL,
            extreme=False,
            positioning_trend="INSUFFICIENT_DATA",
        )

    # Get latest values
    latest = cot_data.iloc[-1]

    # Calculate net positions
    net_commercial = latest["commercial_long"] - latest["commercial_short"]
    net_large_spec = latest["large_spec_long"] - latest["large_spec_short"]

    # Calculate percentiles
    historical_net = cot_data["commercial_long"] - cot_data["commercial_short"]
    commercial_percentile = (
        (historical_net < net_commercial).sum() / len(historical_net) * 100
    )

    historical_large = cot_data["large_spec_long"] - cot_data["large_spec_short"]
    large_spec_percentile = (
        (historical_large < net_large_spec).sum() / len(historical_large) * 100
    )

    # Determine signal
    if commercial_percentile >= 90:
        signal = COTSignal.EXTREME_BULLISH
        extreme = True
    elif commercial_percentile >= 80:
        signal = COTSignal.BULLISH
        extreme = False
    elif commercial_percentile <= 10:
        signal = COTSignal.EXTREME_BEARISH
        extreme = True
    elif commercial_percentile <= 20:
        signal = COTSignal.BEARISH
        extreme = False
    else:
        signal = COTSignal.NEUTRAL
        extreme = False

    # Determine trend
    if len(cot_data) >= 4:
        recent_4wk = historical_net.tail(4).mean()
        prev_4wk = historical_net.tail(8).head(4).mean()
        if recent_4wk > prev_4wk:
            trend = "INCREASING_LONG"
        else:
            trend = "DECREASING_LONG"
    else:
        trend = "INSUFFICIENT_DATA"

    return COTAnalysis(
        symbol=symbol,
        report_date=latest.get("date", datetime.now(timezone.utc)),
        commercial_long=latest["commercial_long"],
        commercial_short=latest["commercial_short"],
        large_spec_long=latest["large_spec_long"],
        large_spec_short=latest["large_spec_short"],
        net_commercial=net_commercial,
        net_large_spec=net_large_spec,
        commercial_percentile=commercial_percentile,
        large_spec_percentile=large_spec_percentile,
        signal=signal,
        extreme=extreme,
        positioning_trend=trend,
    )


def calculate_cot_sentiment_weight(cot_analysis: COTAnalysis) -> float:
    """
    Convert COT analysis to sentiment weight (-1 to 1).
    Used in composite sentiment calculation.
    """
    # Map percentile to sentiment
    # 50 = neutral, 100 = extremely bullish, 0 = extremely bearish
    sentiment = (cot_analysis.commercial_percentile - 50) / 50

    return max(-1.0, min(1.0, sentiment))


# ============================================================================
# SENTIMENT AGGREGATION
# ============================================================================

# Weights from Apex platform
SENTIMENT_WEIGHTS = {
    "cot_commercial": 0.35,  # Highest weight - real institutional money
    "options_flow": 0.20,  # Derivatives positioning
    "news_nlp": 0.20,  # Quantitative news analysis
    "twitter": 0.15,  # Social momentum
    "retail_ssi": 0.07,  # Contrarian retail positioning
    "reddit": 0.03,  # Speculative retail sentiment
}


def calculate_composite_sentiment(
    symbol: str,
    cot_sentiment: float,
    options_sentiment: float = 0,
    news_sentiment: float = 0,
    twitter_sentiment: float = 0,
    retail_sentiment: float = 0,
    reddit_sentiment: float = 0,
) -> SentimentScore:
    """
    Calculate weighted composite sentiment score.

    Args:
        symbol: Trading symbol
        All sentiment values: -1 (extreme bearish) to 1 (extreme bullish)

    Returns:
        SentimentScore with composite score and interpretation
    """
    weights = SENTIMENT_WEIGHTS

    composite = (
        cot_sentiment * weights["cot_commercial"]
        + options_sentiment * weights["options_flow"]
        + news_sentiment * weights["news_nlp"]
        + twitter_sentiment * weights["twitter"]
        + retail_sentiment * weights["retail_ssi"]
        + reddit_sentiment * weights["reddit"]
    )

    # Clamp to [-1, 1]
    composite = max(-1.0, min(1.0, composite))

    # Interpret
    if composite <= -0.8:
        interpretation = "EXTREME_FEAR"
    elif composite <= -0.5:
        interpretation = "FEAR"
    elif composite < 0.5:
        interpretation = "NEUTRAL"
    elif composite < 0.8:
        interpretation = "GREED"
    else:
        interpretation = "EXTREME_GREED"

    return SentimentScore(
        symbol=symbol,
        timestamp=datetime.now(timezone.utc),
        cot_weighted=cot_sentiment * weights["cot_commercial"],
        options_weighted=options_sentiment * weights["options_flow"],
        news_weighted=news_sentiment * weights["news_nlp"],
        social_weighted=twitter_sentiment * weights["twitter"],
        retail_weighted=retail_sentiment * weights["retail_ssi"],
        composite=composite,
        interpretation=interpretation,
    )


def generate_sentiment_signals(sentiment: SentimentScore) -> List[Dict]:
    """Generate actionable trading signals from sentiment."""
    signals = []

    if sentiment.interpretation == "EXTREME_FEAR":
        signals.append(
            {
                "type": "CONTRARIAN_LONG",
                "confidence": 0.85,
                "rationale": "Extreme fear often marks market bottoms",
            }
        )
    elif sentiment.interpretation == "FEAR":
        signals.append(
            {
                "type": "CAUTIOUS_LONG",
                "confidence": 0.65,
                "rationale": "Fear suggests potential opportunity",
            }
        )
    elif sentiment.interpretation == "EXTREME_GREED":
        signals.append(
            {
                "type": "CONTRARIAN_SHORT",
                "confidence": 0.85,
                "rationale": "Extreme greed often marks market tops",
            }
        )
    elif sentiment.interpretation == "GREED":
        signals.append(
            {
                "type": "CAUTIOUS_SHORT",
                "confidence": 0.65,
                "rationale": "Greed suggests potential reversal risk",
            }
        )

    return signals


# ============================================================================
# SPECIAL PATTERNS
# ============================================================================


def detect_silver_bullet(
    ohlcv: pd.DataFrame, session: str = "London"
) -> Optional[Dict]:
    """
    ICT Silver Bullet: M1 FVG during London 10-11AM or NY 2-3PM EST.
    High-probability counter-trend trade.
    """
    if len(ohlcv) < 120:  # Need at least 2 hours of M1 data
        return None

    # Look for fair value gaps in recent candles
    for i in range(3, len(ohlcv)):
        candle1 = ohlcv.iloc[i - 2]
        candle2 = ohlcv.iloc[i - 1]
        candle3 = ohlcv.iloc[i]

        # Bullish FVG
        if candle3["low"] > candle1["high"]:
            gap_size = candle3["low"] - candle1["high"]
            avg_range = (
                ohlcv.iloc[i - 20 : i]["high"].max()
                - ohlcv.iloc[i - 20 : i]["low"].min()
            )

            if gap_size < avg_range * 0.3:  # Small gap
                return {
                    "pattern": "Silver Bullet",
                    "direction": "LONG",
                    "session": session,
                    "entry_zone": (candle1["high"], candle3["low"]),
                    "stop_loss": candle1["low"] * 0.9995,
                    "target": candle1["high"] + (candle1["high"] - candle3["low"]),
                    "quality": "HIGH",
                    "confidence": 0.75,
                }

        # Bearish FVG
        elif candle3["high"] < candle1["low"]:
            gap_size = candle1["low"] - candle3["high"]
            avg_range = (
                ohlcv.iloc[i - 20 : i]["high"].max()
                - ohlcv.iloc[i - 20 : i]["low"].min()
            )

            if gap_size < avg_range * 0.3:
                return {
                    "pattern": "Silver Bullet",
                    "direction": "SHORT",
                    "session": session,
                    "entry_zone": (candle3["high"], candle1["low"]),
                    "stop_loss": candle1["high"] * 1.0005,
                    "target": candle1["low"] - (candle1["low"] - candle3["high"]),
                    "quality": "HIGH",
                    "confidence": 0.75,
                }

    return None


def detect_judas_swing(ohlcv: pd.DataFrame) -> Optional[Dict]:
    """
    Judas Swing: False breakout at session open.
    The market spikes in one direction, stops out weak hands,
    then reverses violently in the opposite direction.
    """
    if len(ohlcv) < 20:
        return None

    recent = ohlcv.iloc[-20:]
    first_5 = recent.iloc[:5]
    last_5 = recent.iloc[-5:]

    # Calculate session range
    session_high = recent["high"].max()
    session_low = recent["low"].min()
    session_range = session_high - session_low

    # Check for spike
    first_high = first_5["high"].max()
    first_low = first_5["low"].min()

    # Judas swing patterns
    if first_high > session_high - session_range * 0.2:
        # Potential bearish judas - spike up then reverse
        reversal_pct = (session_high - recent["close"].iloc[-1]) / session_range

        if reversal_pct > 0.5:  # More than 50% reversal
            return {
                "pattern": "Judas Swing",
                "type": "BEARISH",
                "spike_high": session_high,
                "current_price": recent["close"].iloc[-1],
                "reversal_pct": reversal_pct,
                "target": session_low,
                "confidence": 0.70 if reversal_pct > 0.7 else 0.60,
            }

    elif first_low < session_low + session_range * 0.2:
        # Potential bullish judas - spike down then reverse
        reversal_pct = (recent["close"].iloc[-1] - session_low) / session_range

        if reversal_pct > 0.5:
            return {
                "pattern": "Judas Swing",
                "type": "BULLISH",
                "spike_low": session_low,
                "current_price": recent["close"].iloc[-1],
                "reversal_pct": reversal_pct,
                "target": session_high,
                "confidence": 0.70 if reversal_pct > 0.7 else 0.60,
            }

    return None


def analyze_power_of_3(ohlcv: pd.DataFrame) -> Dict:
    """
    Power of 3 (AMD): Accumulation → Manipulation → Distribution model.
    Identifies the three phases of smart money activity.
    """
    if len(ohlcv) < 100:
        return {"phase": "INSUFFICIENT_DATA", "quality": "LOW"}

    # Divide into 3 equal parts
    third = len(ohlcv) // 3

    accumulation = ohlcv.iloc[:third]
    manipulation = ohlcv.iloc[third : 2 * third]
    distribution = ohlcv.iloc[2 * third :]

    # Calculate volatility for each phase
    acc_vol = (accumulation["high"].max() - accumulation["low"].min()) / accumulation[
        "close"
    ].mean()
    manip_vol = (manipulation["high"].max() - manipulation["low"].min()) / manipulation[
        "close"
    ].mean()
    dist_vol = (distribution["high"].max() - distribution["low"].min()) / distribution[
        "close"
    ].mean()

    # Calculate volume profile
    acc_vol_avg = accumulation["volume"].mean()
    manip_vol_avg = manipulation["volume"].mean()
    dist_vol_avg = distribution["volume"].mean()

    # Determine current phase
    current_close = ohlcv["close"].iloc[-1]
    lowest = ohlcv["low"].min()
    highest = ohlcv["high"].max()
    mid_point = (highest + lowest) / 2

    # Phase determination
    if manip_vol > acc_vol * 1.5:
        phase = "MANIPULATION"
        quality = "HIGH"
    elif dist_vol > manip_vol * 1.3:
        phase = "DISTRIBUTION"
        quality = "MEDIUM"
    elif current_close < mid_point:
        phase = "ACCUMULATION"
        quality = "MEDIUM"
    else:
        phase = "TREND"
        quality = "LOW"

    return {
        "phase": phase,
        "quality": quality,
        "accumulation_volatility": acc_vol,
        "manipulation_volatility": manip_vol,
        "distribution_volatility": dist_vol,
        "volume_profile": {
            "accumulation": acc_vol_avg,
            "manipulation": manip_vol_avg,
            "distribution": dist_vol_avg,
        },
        "position_in_range": (current_close - lowest) / (highest - lowest),
        "swing_high": highest,
        "swing_low": lowest,
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """CLI for kill zones and COT analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Kill Zones & COT Analysis")
    parser.add_argument("--session", action="store_true", help="Show active sessions")
    parser.add_argument("--next-session", action="store_true", help="Show next session")
    parser.add_argument("--cot", help="Analyze COT data file")

    args = parser.parse_args()

    if args.session:
        active = get_active_sessions()
        print("\nActive Trading Sessions:")
        print("=" * 50)
        for session in active:
            print(f"\n{session.session_type.value}")
            print(f"  Time: {session.start_est} - {session.end_est} EST")
            print(f"  Pairs: {', '.join(session.pairs[:3])}...")
            print(f"  Volatility: {session.volatility_expectation}")
            print(f"  Priority: {session.priority}")

    if args.next_session:
        next_sess, start_time, countdown = get_next_session_start()
        print(f"\nNext Session: {next_sess.value if next_sess else 'None'}")
        print(
            f"Start Time: {start_time.strftime('%H:%M EST') if start_time else 'N/A'}"
        )
        print(f"Countdown: {countdown}")

    if args.cot:
        print(f"\nAnalyzing COT data from: {args.cot}")
        # In production, load and analyze COT data


if __name__ == "__main__":
    main()
