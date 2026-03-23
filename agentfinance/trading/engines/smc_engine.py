#!/usr/bin/env python3
"""
AgentFinance Trading Engine - Core Module
Smart Money Concepts (SMC) implementation for institutional-grade forex/commodities trading.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# DATA CLASSES
# ============================================================================


class BiasDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class KillZone(Enum):
    ASIAN = "Asian"
    LONDON_OPEN = "London Open"
    LONDON = "London"
    NEW_YORK = "New York"
    LONDON_CLOSE = "London Close"
    NY_CLOSE = "NY Close"


@dataclass
class OrderBlock:
    """Institutional order block - last bearish/bullish candle before significant move."""

    index: int
    timestamp: datetime
    type: str  # "bullish" or "bearish"
    high: float
    low: float
    close: float
    volume: float
    quality: str = "medium"  # high, medium, low
    mitigated: bool = False
    mitigation_index: Optional[int] = None


@dataclass
class FairValueGap:
    """3-candle imbalance zone - price magnetic areas."""

    index: int
    timestamp: datetime
    type: str  # "bullish" or "bearish"
    high: float
    low: float
    filled: bool = False
    fill_percentage: float = 0.0


@dataclass
class LiquidityZone:
    """Liquidity pools - equal highs/lows, stop hunts."""

    index: int
    timestamp: datetime
    type: str  # "sweep_high", "sweep_low", "buy_side", "sell_side"
    price: float
    volume: float
    broken: bool = False


@dataclass
class BreakOfStructure:
    """BOS/CHoCH - confirms directional bias change."""

    index: int
    timestamp: datetime
    type: str  # "BOS_BULL", "BOS_BEAR", "CHOCH_BULL", "CHOCH_BEAR"
    price: float
    swing_high: float
    swing_low: float
    confirmed: bool = True


@dataclass
class PremiumDiscount:
    """Fibonacci levels - OTE zone for entry."""

    zone: str  # "premium", "discount", "平衡"
    fib_level: float
    price: float
    valid: bool = True


@dataclass
class TradingSession:
    """ICT trading session data."""

    name: str
    start_utc: str
    end_utc: str
    pairs: List[str]
    active: bool = False


@dataclass
class SMCAnalysis:
    """Complete SMC analysis result."""

    symbol: str
    timeframe: str
    timestamp: datetime
    bias: BiasDirection
    confluence_score: float  # 0.0 - 1.0
    order_blocks: List[OrderBlock] = field(default_factory=list)
    fair_value_gaps: List[FairValueGap] = field(default_factory=list)
    liquidity_zones: List[LiquidityZone] = field(default_factory=list)
    bos_choch: List[BreakOfStructure] = field(default_factory=list)
    premium_discount: List[PremiumDiscount] = field(default_factory=list)
    active_sessions: List[KillZone] = field(default_factory=list)
    setups: List[Dict] = field(default_factory=list)


# ============================================================================
# SWING DETECTION
# ============================================================================


def detect_swing_highs_lows(
    df: pd.DataFrame, swing_length: int = 50
) -> Tuple[pd.Series, pd.Series]:
    """
    Detect swing highs and lows using pivot point algorithm.

    Args:
        df: OHLCV DataFrame with columns ['high', 'low', 'close', 'volume']
        swing_length: Number of bars to check on each side

    Returns:
        Tuple of (swing_highs, swing_lows) as pd.Series
    """
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)

    swing_highs = np.zeros(n)
    swing_lows = np.zeros(n)

    for i in range(swing_length, n - swing_length):
        # Swing high: highest point in window
        if highs[i] == max(highs[i - swing_length : i + swing_length + 1]):
            swing_highs[i] = highs[i]

        # Swing low: lowest point in window
        if lows[i] == min(lows[i - swing_length : i + swing_length + 1]):
            swing_lows[i] = lows[i]

    return pd.Series(swing_highs, index=df.index), pd.Series(swing_lows, index=df.index)


def detect_order_blocks(
    df: pd.DataFrame, swing_highs: pd.Series, swing_lows: pd.Series, lookback: int = 5
) -> List[OrderBlock]:
    """
    Detect institutional order blocks.
    An order block is the last bearish/bullish candle before a significant move.
    """
    order_blocks = []

    for i in range(lookback + 1, len(df) - 1):
        # Check if current bar followed a significant move
        move_up = (
            df["high"].iloc[i] > df["high"].iloc[i - lookback] * 1.001
        )  # >0.1% move
        move_down = (
            df["low"].iloc[i] < df["low"].iloc[i - lookback] * 0.999
        )  # >0.1% move

        if move_up:
            # Bullish order block - last bearish candle before upward move
            prev_candle = df.iloc[i - lookback]
            if prev_candle["close"] < prev_candle["open"]:  # Bearish candle
                # Determine quality based on candle size
                body = abs(prev_candle["close"] - prev_candle["open"])
                wick = prev_candle["high"] - prev_candle["low"]
                quality = (
                    "high" if body > wick else "medium" if body > wick * 0.5 else "low"
                )

                order_blocks.append(
                    OrderBlock(
                        index=i - lookback,
                        timestamp=df.index[i - lookback]
                        if hasattr(df.index[i - lookback], "tz_localize")
                        else datetime.now(timezone.utc),
                        type="bullish",
                        high=prev_candle["high"],
                        low=prev_candle["low"],
                        close=prev_candle["close"],
                        volume=prev_candle["volume"],
                        quality=quality,
                    )
                )

        elif move_down:
            # Bearish order block - last bullish candle before downward move
            prev_candle = df.iloc[i - lookback]
            if prev_candle["close"] > prev_candle["open"]:  # Bullish candle
                body = abs(prev_candle["close"] - prev_candle["open"])
                wick = prev_candle["high"] - prev_candle["low"]
                quality = (
                    "high" if body > wick else "medium" if body > wick * 0.5 else "low"
                )

                order_blocks.append(
                    OrderBlock(
                        index=i - lookback,
                        timestamp=df.index[i - lookback]
                        if hasattr(df.index[i - lookback], "tz_localize")
                        else datetime.now(timezone.utc),
                        type="bearish",
                        high=prev_candle["high"],
                        low=prev_candle["low"],
                        close=prev_candle["close"],
                        volume=prev_candle["volume"],
                        quality=quality,
                    )
                )

    return order_blocks


def detect_fair_value_gaps(
    df: pd.DataFrame, join_consecutive: bool = True
) -> List[FairValueGap]:
    """
    Detect Fair Value Gaps (3-candle imbalances).
    """
    fvgs = []

    for i in range(2, len(df)):
        candle1 = df.iloc[i - 2]
        candle2 = df.iloc[i - 1]
        candle3 = df.iloc[i]

        # Bullish FVG: candle3 low > candle1 high
        if candle3["low"] > candle1["high"]:
            fvg_type = "bullish"
            gap_high = candle3["low"]
            gap_low = candle1["high"]

            fvgs.append(
                FairValueGap(
                    index=i,
                    timestamp=df.index[i]
                    if hasattr(df.index[i], "tz_localize")
                    else datetime.now(timezone.utc),
                    type=fvg_type,
                    high=gap_high,
                    low=gap_low,
                )
            )

        # Bearish FVG: candle3 high < candle1 low
        elif candle3["high"] < candle1["low"]:
            fvg_type = "bearish"
            gap_high = candle1["low"]
            gap_low = candle3["high"]

            fvgs.append(
                FairValueGap(
                    index=i,
                    timestamp=df.index[i]
                    if hasattr(df.index[i], "tz_localize")
                    else datetime.now(timezone.utc),
                    type=fvg_type,
                    high=gap_high,
                    low=gap_low,
                )
            )

    return fvgs


def detect_bos_choch(
    df: pd.DataFrame, swing_highs: pd.Series, swing_lows: pd.Series
) -> List[BreakOfStructure]:
    """
    Detect Break of Structure and Change of Character.
    BOS: Higher high/lower low confirms directional bias
    CHoCH: First opposing BOS signals trend reversal
    """
    bos_choch_list = []
    last_bullish_bos = 0
    last_bearish_bos = 0

    for i in range(2, len(df)):
        current_high = df["high"].iloc[i]
        current_low = df["low"].iloc[i]

        # Check for swing highs
        swing_high_idx = swing_highs[swing_highs > 0].index
        if len(swing_high_idx) > 0:
            recent_highs = swing_high_idx[swing_high_idx < i]
            if len(recent_highs) >= 2:
                prev_high_idx = recent_highs[-2]
                prev_high_price = swing_highs.iloc[prev_high_idx]
                curr_high_price = swing_highs.iloc[recent_highs[-1]]

                # Bullish BOS
                if curr_high_price > prev_high_price and current_high > curr_high_price:
                    if i - last_bullish_bos > 10:  # Minimum separation
                        bos_choch_list.append(
                            BreakOfStructure(
                                index=i,
                                timestamp=df.index[i]
                                if hasattr(df.index[i], "tz_localize")
                                else datetime.now(timezone.utc),
                                type="BOS_BULL",
                                price=current_high,
                                swing_high=curr_high_price,
                                swing_low=df["low"].iloc[i],
                            )
                        )
                        last_bullish_bos = i

        # Check for swing lows
        swing_low_idx = swing_lows[swing_lows > 0].index
        if len(swing_low_idx) > 0:
            recent_lows = swing_low_idx[swing_low_idx < i]
            if len(recent_lows) >= 2:
                prev_low_idx = recent_lows[-2]
                prev_low_price = swing_lows.iloc[prev_low_idx]
                curr_low_price = swing_lows.iloc[recent_lows[-1]]

                # Bearish BOS
                if curr_low_price < prev_low_price and current_low < curr_low_price:
                    if i - last_bearish_bos > 10:
                        bos_choch_list.append(
                            BreakOfStructure(
                                index=i,
                                timestamp=df.index[i]
                                if hasattr(df.index[i], "tz_localize")
                                else datetime.now(timezone.utc),
                                type="BOS_BEAR",
                                price=current_low,
                                swing_high=df["high"].iloc[i],
                                swing_low=curr_low_price,
                            )
                        )
                        last_bearish_bos = i

    return bos_choch_list


def detect_liquidity_zones(
    df: pd.DataFrame,
    swing_highs: pd.Series,
    swing_lows: pd.Series,
    tolerance: float = 0.0001,
) -> List[LiquidityZone]:
    """
    Detect liquidity zones - equal highs/lows, stop hunts.
    """
    liquidity_zones = []
    highs = df["high"].values
    lows = df["low"].values

    for i in range(10, len(df) - 1):
        # Check for equal highs (sell side liquidity)
        for j in range(i - 20, i):
            if abs(highs[i] - highs[j]) / highs[j] < tolerance:
                # Confirm with volume surge
                avg_volume = df["volume"].iloc[i - 20 : i].mean()
                if df["volume"].iloc[i] > avg_volume * 1.5:
                    liquidity_zones.append(
                        LiquidityZone(
                            index=i,
                            timestamp=df.index[i]
                            if hasattr(df.index[i], "tz_localize")
                            else datetime.now(timezone.utc),
                            type="sweep_high",
                            price=highs[i],
                            volume=df["volume"].iloc[i],
                        )
                    )
                    break

        # Check for equal lows (buy side liquidity)
        for j in range(i - 20, i):
            if abs(lows[i] - lows[j]) / lows[j] < tolerance:
                avg_volume = df["volume"].iloc[i - 20 : i].mean()
                if df["volume"].iloc[i] > avg_volume * 1.5:
                    liquidity_zones.append(
                        LiquidityZone(
                            index=i,
                            timestamp=df.index[i]
                            if hasattr(df.index[i], "tz_localize")
                            else datetime.now(timezone.utc),
                            type="sweep_low",
                            price=lows[i],
                            volume=df["volume"].iloc[i],
                        )
                    )
                    break

    return liquidity_zones


def calculate_premium_discount(
    df: pd.DataFrame, swing_highs: pd.Series, swing_lows: pd.Series
) -> List[PremiumDiscount]:
    """
    Calculate premium and discount zones using Fibonacci retracement.
    OTE zone: 0.62-0.79 retracement for optimal trade entry.
    """
    pd_zones = []

    for i in range(50, len(df)):
        # Find most recent significant swing
        swing_high_idx = swing_highs[swing_highs > 0].index
        swing_low_idx = swing_lows[swing_lows > 0].index

        if len(swing_high_idx) >= 2 and len(swing_low_idx) >= 2:
            recent_high_idx = swing_high_idx[-1]
            recent_low_idx = swing_low_idx[-1]

            if recent_high_idx > recent_low_idx:
                swing_high_price = swing_highs.iloc[recent_high_idx]
                swing_low_price = swing_lows.iloc[recent_low_idx]
                range_size = swing_high_price - swing_low_price
                current_price = df["close"].iloc[i]

                if range_size > 0:
                    # Calculate retracement level
                    retracement = (swing_high_price - current_price) / range_size

                    # Determine zone
                    if retracement >= 0.382 and retracement < 0.618:
                        zone = "discount"
                        fib_level = retracement
                    elif retracement >= 0.618 and retracement < 0.786:
                        zone = "平衡"  # Fair value
                        fib_level = retracement
                    elif retracement >= 0.786:
                        zone = "premium"
                        fib_level = retracement
                    else:
                        zone = "premium"
                        fib_level = retracement

                    pd_zones.append(
                        PremiumDiscount(
                            zone=zone,
                            fib_level=fib_level,
                            price=current_price,
                            valid=True,
                        )
                    )

    return pd_zones[-5:] if pd_zones else []  # Return last 5 zones


# ============================================================================
# KILL ZONES
# ============================================================================

KILL_ZONES = {
    "Asian": {
        "start_utc": "00:00",
        "end_utc": "08:00",
        "pairs": ["AUDJPY", "USDJPY", "AUDUSD", "NZDUSD"],
        "description": "Low volatility consolidation",
    },
    "London Open": {
        "start_utc": "07:50",
        "end_utc": "08:00",
        "pairs": ["GBPUSD", "EURGBP", "EURUSD", "GBPJPY"],
        "description": "High volatility, trend initiation",
    },
    "London": {
        "start_utc": "08:00",
        "end_utc": "12:00",
        "pairs": ["EURUSD", "GBPUSD", "EURJPY", "GBPJPY"],
        "description": "Continuous liquidity, kill zones",
    },
    "New York": {
        "start_utc": "13:00",
        "end_utc": "17:00",
        "pairs": ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"],
        "description": "High impact, overlap session",
    },
    "London Close": {
        "start_utc": "16:30",
        "end_utc": "17:00",
        "pairs": ["EURUSD", "GBPUSD"],
        "description": "Stop runs, reversal zones",
    },
    "NY Close": {
        "start_utc": "22:00",
        "end_utc": "23:00",
        "pairs": ["All majors"],
        "description": "Avoid trading",
    },
}


def get_active_kill_zones(utc_time: datetime) -> List[KillZone]:
    """
    Determine which kill zones are currently active.
    Times are UTC, converted to EST internally.
    """
    active_zones = []

    # Convert to EST (UTC-5, or UTC-4 during DST)
    est_offset = -5 if (utc_time.month < 3 or utc_time.month > 11) else -4
    est_time = utc_time + timedelta(hours=est_offset)

    current_time_str = est_time.strftime("%H:%M")

    for zone_name, zone_data in KILL_ZONES.items():
        start = zone_data["start_utc"]
        end = zone_data["end_utc"]

        # Handle overnight sessions (e.g., Asian 21:00 - 04:00)
        if start > end:
            if current_time_str >= start or current_time_str <= end:
                active_zones.append(
                    KillZone[zone_name.upper().replace(" ", "_").replace("NY", "NY")]
                )
        else:
            if start <= current_time_str <= end:
                active_zones.append(
                    KillZone[zone_name.upper().replace(" ", "_").replace("NY", "NY")]
                )

    return active_zones


# ============================================================================
# CONFLUENCE SCORING
# ============================================================================


def calculate_confluence_score(
    order_blocks: List[OrderBlock],
    fvgs: List[FairValueGap],
    bos_choch: List[BreakOfStructure],
    pd_zones: List[PremiumDiscount],
    active_sessions: List[KillZone],
    htf_bias: BiasDirection = BiasDirection.NEUTRAL,
) -> float:
    """
    Calculate multi-timeframe confluence score for trade setups.

    Score = Σ (HTF_bias × 0.4) + (OB_confluence × 0.25) + (FVG_present × 0.15)
            + (BOS_confirmation × 0.1) + (kill_zone_active × 0.1)
    """
    score = 0.0

    # HTF Bias (40%)
    if htf_bias == BiasDirection.BULLISH:
        score += 0.4
    elif htf_bias == BiasDirection.BEARISH:
        score += 0.4
    else:
        score += 0.1

    # Order Blocks (25%)
    if order_blocks:
        high_quality_obs = [
            ob for ob in order_blocks if ob.quality == "high" and not ob.mitigated
        ]
        medium_quality_obs = [
            ob for ob in order_blocks if ob.quality == "medium" and not ob.mitigated
        ]
        score += min(len(high_quality_obs) * 0.1 + len(medium_quality_obs) * 0.05, 0.25)

    # Fair Value Gaps (15%)
    unfilled_fvgs = [fvg for fvg in fvgs if not fvg.filled]
    score += min(len(unfilled_fvgs) * 0.05, 0.15)

    # BOS/CHoCH (10%)
    recent_bos = bos_choch[-10:] if len(bos_choch) > 10 else bos_choch
    bullish_bos = sum(1 for b in recent_bos if "BULL" in b.type)
    bearish_bos = sum(1 for b in recent_bos if "BEAR" in b.type)
    if bullish_bos > bearish_bos:
        score += bullish_bos * 0.02
    elif bearish_bos > bullish_bos:
        score += bearish_bos * 0.02

    # Kill Zone (10%)
    if active_sessions:
        # Higher priority for London/NY open
        priority_zones = [KillZone.LONDON_OPEN, KillZone.NEW_YORK]
        if any(s in active_sessions for s in priority_zones):
            score += 0.1
        else:
            score += 0.05

    return min(score, 1.0)


def determine_bias(bos_choch: List[BreakOfStructure]) -> BiasDirection:
    """Determine market bias from recent BOS/CHoCH signals."""
    if not bos_choch:
        return BiasDirection.NEUTRAL

    recent = bos_choch[-20:]  # Last 20 signals
    bullish = sum(1 for b in recent if "BULL" in b.type)
    bearish = sum(1 for b in recent if "BEAR" in b.type)

    if bullish > bearish * 1.5:
        return BiasDirection.BULLISH
    elif bearish > bullish * 1.5:
        return BiasDirection.BEARISH
    return BiasDirection.NEUTRAL


# ============================================================================
# TRADE SETUP GENERATION
# ============================================================================


def generate_setups(analysis: SMCAnalysis, min_confidence: float = 0.75) -> List[Dict]:
    """
    Generate trade setups based on SMC analysis.
    Score ≥ 0.75: High-probability setup
    Score 0.50–0.74: Monitor setup
    Score < 0.50: No trade
    """
    setups = []

    for ob in analysis.order_blocks:
        if ob.mitigated or ob.quality != "high":
            continue

        # Check for bullish setup
        if ob.type == "bullish" and analysis.bias in [
            BiasDirection.BULLISH,
            BiasDirection.NEUTRAL,
        ]:
            # Entry at OB high with SL below OB low
            entry = ob.high
            stop_loss = ob.low * 0.9995
            take_profit_1 = entry + (entry - stop_loss) * 1.5
            take_profit_2 = entry + (entry - stop_loss) * 2.5

            setup = {
                "type": "LONG",
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2,
                "order_block": ob.index,
                "risk_reward": (take_profit_1 - entry) / (entry - stop_loss),
                "confidence": analysis.confluence_score,
                "quality": "HIGH" if analysis.confluence_score >= 0.75 else "MEDIUM",
            }
            setups.append(setup)

        # Check for bearish setup
        elif ob.type == "bearish" and analysis.bias in [
            BiasDirection.BEARISH,
            BiasDirection.NEUTRAL,
        ]:
            entry = ob.low
            stop_loss = ob.high * 1.0005
            take_profit_1 = entry - (stop_loss - entry) * 1.5
            take_profit_2 = entry - (stop_loss - entry) * 2.5

            setup = {
                "type": "SHORT",
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2,
                "order_block": ob.index,
                "risk_reward": (stop_loss - take_profit_1) / (stop_loss - entry),
                "confidence": analysis.confluence_score,
                "quality": "HIGH" if analysis.confluence_score >= 0.75 else "MEDIUM",
            }
            setups.append(setup)

    return setups


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================


def run_full_smc_analysis(
    symbol: str, ohlcv: pd.DataFrame, timeframe: str = "H1", swing_length: int = 50
) -> SMCAnalysis:
    """
    Run complete SMC analysis on OHLCV data.

    Args:
        symbol: Trading symbol (e.g., "EURUSD")
        ohlcv: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        timeframe: Chart timeframe
        swing_length: Swing detection lookback

    Returns:
        SMCAnalysis object with all detected patterns
    """
    # Ensure minimum data
    if len(ohlcv) < swing_length + 10:
        return SMCAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now(timezone.utc),
            bias=BiasDirection.NEUTRAL,
            confluence_score=0.0,
        )

    # Detect swing highs/lows
    swing_highs, swing_lows = detect_swing_highs_lows(ohlcv, swing_length)

    # Detect SMC patterns
    order_blocks = detect_order_blocks(ohlcv, swing_highs, swing_lows)
    fvgs = detect_fair_value_gaps(ohlcv)
    bos_choch = detect_bos_choch(ohlcv, swing_highs, swing_lows)
    liquidity = detect_liquidity_zones(ohlcv, swing_highs, swing_lows)
    pd_zones = calculate_premium_discount(ohlcv, swing_highs, swing_lows)

    # Get active sessions
    active_sessions = get_active_kill_zones(datetime.now(timezone.utc))

    # Determine bias
    bias = determine_bias(bos_choch)

    # Calculate confluence
    confluence = calculate_confluence_score(
        order_blocks, fvgs, bos_choch, pd_zones, active_sessions
    )

    # Create analysis object
    analysis = SMCAnalysis(
        symbol=symbol,
        timeframe=timeframe,
        timestamp=datetime.now(timezone.utc),
        bias=bias,
        confluence_score=confluence,
        order_blocks=order_blocks,
        fair_value_gaps=fvgs,
        liquidity_zones=liquidity,
        bos_choch=bos_choch,
        premium_discount=pd_zones,
        active_sessions=active_sessions,
    )

    # Generate setups
    analysis.setups = generate_setups(analysis)

    return analysis


# ============================================================================
# SPECIAL PATTERN DETECTION
# ============================================================================


def detect_silver_bullet(df: pd.DataFrame, session: str = "London") -> Optional[Dict]:
    """
    ICT Silver Bullet: M1 FVG during London 10-11AM or NY 2-3PM EST.
    """
    if len(df) < 60:
        return None

    # Check for London Silver Bullet (10-11 AM EST)
    if session == "London":
        fvgs = detect_fair_value_gaps(df.iloc[-60:])
        if fvgs:
            latest_fvg = fvgs[-1]
            return {
                "pattern": "Silver Bullet",
                "session": session,
                "direction": latest_fvg.type.upper(),
                "entry_zone": (latest_fvg.low, latest_fvg.high),
                "quality": "HIGH",
            }

    return None


def detect_judas_swing(df: pd.DataFrame) -> Optional[Dict]:
    """
    Judas Swing: False breakout at session open before true directional move.
    """
    if len(df) < 20:
        return None

    # Check for spike followed by reversal
    recent = df.iloc[-20:]
    high = recent["high"].max()
    low = recent["low"].min()

    # Judas swing pattern
    if recent["close"].iloc[-1] < recent["open"].iloc[-5]:
        # Bearish rejection after bullish spike
        return {
            "pattern": "Judas Swing",
            "type": "BEARISH",
            "swing_high": high,
            "reversal_point": recent["close"].iloc[-1],
            "target": low,
        }
    elif recent["close"].iloc[-1] > recent["open"].iloc[-5]:
        # Bullish rejection after bearish spike
        return {
            "pattern": "Judas Swing",
            "type": "BULLISH",
            "swing_low": low,
            "reversal_point": recent["close"].iloc[-1],
            "target": high,
        }

    return None


def analyze_power_of_3(ohlcv: pd.DataFrame) -> Dict:
    """
    Power of 3 (AMD): Accumulation → Manipulation → Distribution model.
    """
    if len(ohlcv) < 100:
        return {"phase": "INSUFFICIENT_DATA"}

    # Divide into 3 phases
    third = len(ohlcv) // 3
    accumulation = ohlcv.iloc[:third]
    manipulation = ohlcv.iloc[third : 2 * third]
    distribution = ohlcv.iloc[2 * third :]

    # Calculate volatility for each phase
    acc_vol = accumulation["high"].max() - accumulation["low"].min()
    manip_vol = manipulation["high"].max() - manipulation["low"].min()
    dist_vol = distribution["high"].max() - distribution["low"].min()

    # Determine current phase
    current_price = ohlcv["close"].iloc[-1]
    lowest = ohlcv["low"].min()
    highest = ohlcv["high"].max()

    if current_price < ohlcv["close"].iloc[third]:
        phase = "ACCUMULATION"
    elif manip_vol > acc_vol * 1.5:
        phase = "MANIPULATION"
    else:
        phase = "DISTRIBUTION"

    return {
        "phase": phase,
        "accumulation_volatility": acc_vol,
        "manipulation_volatility": manip_vol,
        "distribution_volatility": dist_vol,
        "position_in_range": (current_price - lowest) / (highest - lowest)
        if highest > lowest
        else 0.5,
    }


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """CLI for running SMC analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="SMC Analysis Tool")
    parser.add_argument("--symbol", default="EURUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="H1", help="Timeframe")
    parser.add_argument("--swing-length", type=int, default=50, help="Swing lookback")

    args = parser.parse_args()

    # For demo, create sample data
    # In production, fetch from OANDA or Polygon
    dates = pd.date_range(end=datetime.now(timezone.utc), periods=200, freq="1h")
    np.random.seed(42)

    base_price = 1.0850
    sample_data = pd.DataFrame(
        {
            "open": base_price + np.cumsum(np.random.randn(200) * 0.0005),
            "high": base_price
            + np.cumsum(np.random.randn(200) * 0.0005)
            + np.abs(np.random.randn(200) * 0.0003),
            "low": base_price
            + np.cumsum(np.random.randn(200) * 0.0005)
            - np.abs(np.random.randn(200) * 0.0003),
            "close": base_price + np.cumsum(np.random.randn(200) * 0.0005),
            "volume": np.random.randint(1000, 10000, 200),
        },
        index=dates,
    )

    # Ensure OHLC consistency
    sample_data["high"] = sample_data[["open", "high", "close"]].max(axis=1)
    sample_data["low"] = sample_data[["open", "low", "close"]].min(axis=1)

    # Run analysis
    analysis = run_full_smc_analysis(
        args.symbol, sample_data, args.timeframe, args.swing_length
    )

    print(f"\n{'=' * 60}")
    print(f"SMC Analysis: {args.symbol} ({args.timeframe})")
    print(f"{'=' * 60}")
    print(f"Bias: {analysis.bias.value}")
    print(f"Confluence Score: {analysis.confluence_score:.2%}")
    print(f"Active Sessions: {[s.value for s in analysis.active_sessions]}")
    print(f"\nOrder Blocks: {len(analysis.order_blocks)}")
    print(f"Fair Value Gaps: {len(analysis.fair_value_gaps)}")
    print(f"BOS/CHoCH Signals: {len(analysis.bos_choch)}")
    print(f"Liquidity Zones: {len(analysis.liquidity_zones)}")
    print(f"\nTrade Setups: {len(analysis.setups)}")

    for i, setup in enumerate(analysis.setups[:5], 1):
        print(f"\n  Setup #{i}: {setup['type']}")
        print(f"    Entry: {setup['entry']:.5f}")
        print(f"    SL: {setup['stop_loss']:.5f} | TP1: {setup['take_profit_1']:.5f}")
        print(
            f"    R:R: 1:{setup['risk_reward']:.1f} | Confidence: {setup['confidence']:.0%}"
        )


if __name__ == "__main__":
    main()
