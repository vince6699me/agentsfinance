#!/usr/bin/env python3
"""
Agent 22 - SMC Strategy Agent
Smart Money Concepts analysis and signal generation.
Commands: scan, ob, fvg, bos, liquidity, setup, kill-zones, bias, confluence
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "trading", "engines")
)

try:
    from smc_engine import SMCEngine
    from session_engine import SessionEngine
except ImportError:
    print("Warning: Trading engines not available")
    SMCEngine = None
    SessionEngine = None


# Monitored symbols and timeframes
MONITORED_PAIRS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "NZDUSD",
    "EURGBP",
    "EURJPY",
    "GBPJPY",
    "XAUUSD",
    "XAGUSD",
    "SPX",
    "NAS100",
    "USOIL",
]

TIMEFRAMES = ["M15", "H1", "H4", "D1"]

MIN_CONFLUENCE = 0.75


def cmd_scan(symbol: str, timeframe: str = "H1") -> dict:
    """Full SMC scan on a symbol."""
    if SMCEngine is None:
        return {"error": "SMC engine not available", "symbol": symbol}

    engine = SMCEngine()
    result = engine.full_analysis(symbol, timeframe)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "timestamp": datetime.now().isoformat(),
        "bias": result.get("bias", "NEUTRAL"),
        "confluence_score": result.get("confluence_score", 0),
        "order_blocks": len(result.get("order_blocks", [])),
        "fair_value_gaps": len(result.get("fair_value_gaps", [])),
        "liquidity_zones": len(result.get("liquidity", [])),
        "bos_count": len(result.get("bos_choch", [])),
        "kills": engine.get_active_kill_zones(),
        "setup_ready": result.get("confluence_score", 0) >= MIN_CONFLUENCE,
        "recommendation": get_recommendation(result),
    }


def cmd_order_blocks(symbol: str, timeframe: str = "H4") -> dict:
    """Get order block analysis."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    obs = engine.get_order_blocks(symbol, timeframe)

    return {
        "command": "order_blocks",
        "symbol": symbol,
        "timeframe": timeframe,
        "order_blocks": obs,
        "bullish_obs": [ob for ob in obs if ob.get("type") == "bullish"],
        "bearish_obs": [ob for ob in obs if ob.get("type") == "bearish"],
        "active_obs": [ob for ob in obs if not ob.get("mitigated", False)],
    }


def cmd_fvg(symbol: str, timeframe: str = "H1") -> dict:
    """Get fair value gap analysis."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    fvgs = engine.get_fair_value_gaps(symbol, timeframe)

    return {
        "command": "fair_value_gaps",
        "symbol": symbol,
        "timeframe": timeframe,
        "fvgs": fvgs,
        "unfilled": [f for f in fvgs if not f.get("filled", False)],
        "partial_filled": [f for f in fvgs if f.get("fill_pct", 0) < 100],
    }


def cmd_liquidity(symbol: str, timeframe: str = "H1") -> dict:
    """Get liquidity zone analysis."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    zones = engine.get_liquidity_zones(symbol, timeframe)

    return {
        "command": "liquidity",
        "symbol": symbol,
        "timeframe": timeframe,
        "zones": zones,
        "sweeps": [z for z in zones if z.get("swept", False)],
        "active": [z for z in zones if not z.get("swept", False)],
    }


def cmd_premium_discount(symbol: str, timeframe: str = "H4") -> dict:
    """Get premium/discount zone analysis."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    zones = engine.get_premium_discount(symbol, timeframe)

    return {
        "command": "premium_discount",
        "symbol": symbol,
        "timeframe": timeframe,
        "zones": zones,
        "current_zone": zones.get("current_zone", "NEUTRAL")
        if isinstance(zones, dict)
        else "NEUTRAL",
    }


def cmd_kill_zones() -> dict:
    """Get current kill zone status."""
    if SessionEngine is None:
        return {"error": "Session engine not available"}

    engine = SessionEngine()
    zones = engine.get_active_kill_zones()

    return {
        "command": "kill_zones",
        "timestamp": datetime.now().isoformat(),
        "utc_time": datetime.utcnow().strftime("%H:%M"),
        "active_zones": zones,
        "next_zone": get_next_zone(),
        "trading_window": len(zones) > 0,
    }


def cmd_bias(symbol: str, timeframe: str = "H4") -> dict:
    """Determine market bias."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    bias = engine.get_bias(symbol, timeframe)

    return {
        "command": "bias",
        "symbol": symbol,
        "timeframe": timeframe,
        "bias": bias,
        "timestamp": datetime.now().isoformat(),
    }


def cmd_confluence(symbol: str, timeframe: str = "H1") -> dict:
    """Calculate confluence score."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    confluence = engine.get_confluence_score(symbol, timeframe)

    return {
        "command": "confluence",
        "symbol": symbol,
        "timeframe": timeframe,
        "score": confluence,
        "rating": get_confluence_rating(confluence),
        "trade_ready": confluence >= MIN_CONFLUENCE,
    }


def cmd_setup(symbol: str, timeframe: str = "H1") -> dict:
    """Generate trade setup."""
    if SMCEngine is None:
        return {"error": "SMC engine not available"}

    engine = SMCEngine()
    setups = engine.generate_setups(symbol, timeframe)

    return {
        "command": "setup",
        "symbol": symbol,
        "timeframe": timeframe,
        "setups": setups,
        "timestamp": datetime.now().isoformat(),
    }


def get_recommendation(result: dict) -> str:
    """Generate recommendation based on SMC analysis."""
    confluence = result.get("confluence_score", 0)
    bias = result.get("bias", "NEUTRAL")

    if confluence >= 0.85 and bias != "NEUTRAL":
        return "HIGH CONFIDENCE - Execute trade"
    elif confluence >= 0.75 and bias != "NEUTRAL":
        return "GOOD CONFIDENCE - Monitor for entry"
    elif confluence >= 0.5:
        return "LOWER CONFIDENCE - Wait for more confluence"
    else:
        return "INSUFFICIENT CONFIDENCE - No trade"


def get_confluence_rating(score: float) -> str:
    """Get confluence rating string."""
    if score >= 0.85:
        return "EXCELLENT"
    elif score >= 0.75:
        return "GOOD"
    elif score >= 0.5:
        return "FAIR"
    else:
        return "POOR"


def get_next_zone() -> Optional[dict]:
    """Get next upcoming kill zone."""
    now = datetime.utcnow()
    current_hour = now.hour

    zones = [
        {"name": "London Open", start: 2, end: 4},
        {"name": "London", start: 3, end: 12},
        {"name": "NY Open", start: 8, end: 12},
        {"name": "London Close", start: 10, end: 11},
    ]

    for zone in zones:
        if zone["start"] > current_hour:
            return zone
    return {"name": "Tokyo / Asian", "start": 21, "end": 4}


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(
            "SMC Strategy Agent - Commands: scan, ob, fvg, liquidity, setup, kill-zones, bias, confluence"
        )
        print("Usage: python smc_strategy.py <command> [symbol] [timeframe]")
        sys.exit(1)

    command = sys.argv[1].lower()
    symbol = sys.argv[2] if len(sys.argv) > 2 else "EURUSD"
    timeframe = sys.argv[3] if len(sys.argv) > 3 else "H1"

    commands = {
        "scan": lambda: cmd_scan(symbol, timeframe),
        "ob": lambda: cmd_order_blocks(symbol, timeframe),
        "fvg": lambda: cmd_fvg(symbol, timeframe),
        "liquidity": lambda: cmd_liquidity(symbol, timeframe),
        "premium": lambda: cmd_premium_discount(symbol, timeframe),
        "kill-zones": cmd_kill_zones,
        "bias": lambda: cmd_bias(symbol, timeframe),
        "confluence": lambda: cmd_confluence(symbol, timeframe),
        "setup": lambda: cmd_setup(symbol, timeframe),
    }

    handler = commands.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        print(
            "Available: scan, ob, fvg, liquidity, premium, kill-zones, bias, confluence, setup"
        )
        sys.exit(1)

    result = handler()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
