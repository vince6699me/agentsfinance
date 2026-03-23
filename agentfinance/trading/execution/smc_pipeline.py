#!/usr/bin/env python3
"""
AgentFinance SMC → Execution Pipeline
Wires Agent 22 (SMC Strategy) → Agent 28 (Live Executor)
for fully automated signal-to-trade execution.

Flow:
    Agent 22 (SMC Strategy)
         ↓ generates signal dict
    smc_pipeline.py (validation + routing)
         ↓ filtered signal
    Agent 28 (Trading Executor)
         ↓ risk gates + cTrader
    Pepperstone Demo Account

Usage:
    python smc_pipeline.py EURUSD H1          # Scan and execute best setup
    python smc_pipeline.py EURUSD H1 --dry    # Dry run (no execution)
    python smc_pipeline.py --scan-all       # Scan all monitored pairs
    python smc_pipeline.py --status         # Show pipeline status

Environment (.env):
    CTRADER_ACCOUNT_ID=46729678
    CTRADER_HOST=demo
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "execution"))
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "trading")
)

from live_executor import TradingExecutor

try:
    from smc_engine import SMCEngine

    SMCEngineAvailable = True
except ImportError:
    SMCEngineAvailable = False


# ============================================================================
# CONFIGURATION
# ============================================================================

MONITORED_PAIRS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    "EURGBP",
    "EURJPY",
    "XAUUSD",
    "XAGUSD",
]

EXECUTION_MODE = "DEMO"  # "DEMO" or "LIVE" — set LIVE only after testing


# ============================================================================
# SMC PIPELINE
# ============================================================================


class SMCPipeline:
    """
    Complete SMC Signal → Execution pipeline.
    Orchestrates Agent 22 analysis → filtering → Agent 28 execution.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.executor = None if dry_run else TradingExecutor()
        self.engine = SMCEngine() if SMCEngineAvailable else None
        self.results: List[Dict] = []

        mode = "DRY RUN (no execution)" if dry_run else "LIVE DEMO"
        self.log(f"SMCPipeline initialized — {mode}")

    def log(self, msg: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        print(f"[{ts}] [Pipeline] {msg}")

    # --------------------------------------------------------------------------
    # ANALYSIS (Agent 22)
    # --------------------------------------------------------------------------

    def analyze(self, symbol: str, timeframe: str = "H1") -> Dict[str, Any]:
        """
        Run full SMC analysis (Agent 22).
        Returns complete analysis with trade-ready signal data.
        """
        self.log(f"Analyzing {symbol} {timeframe}...")

        if not SMCEngineAvailable or self.engine is None:
            return self._mock_analysis(symbol, timeframe)

        try:
            result = self.engine.full_analysis(symbol, timeframe)
            return self._build_signal(symbol, timeframe, result)
        except Exception as e:
            self.log(f"Analysis error for {symbol}: {e}")
            return self._mock_analysis(symbol, timeframe)

    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all monitored pairs and rank by confluence."""
        self.log(f"Scanning {len(MONITORED_PAIRS)} pairs...")
        signals = []
        for pair in MONITORED_PAIRS:
            for tf in ["H1", "H4"]:
                result = self.analyze(pair, tf)
                if result.get("setup_ready"):
                    signals.append(result)
        # Rank by confidence
        signals.sort(key=lambda x: x.get("confluence_score", 0), reverse=True)
        self.log(f"Found {len(signals)} trade-ready setups")
        return signals

    # --------------------------------------------------------------------------
    # SIGNAL BUILDING
    # --------------------------------------------------------------------------

    def _build_signal(self, symbol: str, timeframe: str, analysis: Dict) -> Dict:
        """Convert SMC analysis output to execution signal."""
        bias = analysis.get("bias", "NEUTRAL")
        confluence = analysis.get("confluence_score", 0)

        # Determine direction
        direction = None
        if bias == "BULLISH":
            direction = "BUY"
        elif bias == "BEARISH":
            direction = "SELL"

        # Extract entry, SL, TP from analysis
        order_blocks = analysis.get("order_blocks", [])
        fvgs = analysis.get("fair_value_gaps", [])

        entry_price = analysis.get("current_price")
        stop_loss = analysis.get("stop_loss")
        take_profit = analysis.get("take_profit")

        setup_ready = (
            confluence >= 0.75
            and direction is not None
            and entry_price is not None
            and stop_loss is not None
            and take_profit is not None
        )

        return {
            # Identity
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            # SMC data
            "bias": bias,
            "direction": direction,
            "confluence_score": confluence,
            "order_blocks_count": len(order_blocks),
            "fvgs_count": len(fvgs),
            "kills_active": analysis.get("active_kill_zones", []),
            # Execution data
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "volume": self._calculate_volume(symbol),
            "setup_ready": setup_ready,
            "setup_type": f"SMC {bias}",
        }

    def _mock_analysis(self, symbol: str, timeframe: str) -> Dict:
        """Return mock analysis when SMC engine unavailable."""
        biases = {
            "EURUSD": "BULLISH",
            "GBPUSD": "BULLISH",
            "USDJPY": "BEARISH",
            "XAUUSD": "NEUTRAL",
            "AUDUSD": "BULLISH",
            "USDCAD": "NEUTRAL",
        }
        bias = biases.get(symbol, "NEUTRAL")
        direction = {"BULLISH": "BUY", "BEARISH": "SELL", "NEUTRAL": None}.get(bias)

        # Mock prices
        prices = {
            "EURUSD": (1.0823, 1.0756, 1.0890),
            "GBPUSD": (1.2678, 1.2600, 1.2800),
            "USDJPY": (148.50, 149.20, 147.80),
            "XAUUSD": (2345.0, 2372.0, 2310.0),
            "AUDUSD": (0.6540, 0.6490, 0.6620),
            "USDCAD": (1.3560, 1.3620, 1.3480),
        }
        entry, sl, tp = prices.get(symbol, (1.1000, 1.0900, 1.1200))

        confluence = {
            "EURUSD": 0.82,
            "GBPUSD": 0.79,
            "USDJPY": 0.65,
            "XAUUSD": 0.70,
            "AUDUSD": 0.75,
        }.get(symbol, 0.60)

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "bias": bias,
            "direction": direction,
            "confluence_score": confluence,
            "order_blocks_count": 2,
            "fvgs_count": 1,
            "kills_active": ["London Open"],
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "volume": self._calculate_volume(symbol),
            "setup_ready": confluence >= 0.75 and direction is not None,
            "setup_type": f"SMC {bias} (demo)",
        }

    def _calculate_volume(self, symbol: str) -> float:
        """Calculate position size in lots based on ~1% risk."""
        # Simplified: 0.10 lots for most pairs
        # Real implementation would use account balance, SL distance, and symbol pip value
        return 0.10

    # --------------------------------------------------------------------------
    # EXECUTION GATE
    # --------------------------------------------------------------------------

    def execute_signal(self, signal: Dict) -> Dict:
        """
        Pass a signal through all execution gates and execute.
        Returns execution result with full pipeline metadata.
        Always appends to self.results (for summary tracking).
        """
        if self.dry_run:
            self.log(
                f"[DRY RUN] Would execute: {signal['symbol']} {signal.get('direction')} "
                f"Conf={signal.get('confluence_score', 0):.0%}"
            )
            result = {"status": "DRY_RUN", "signal": signal}
        elif not signal.get("setup_ready"):
            self.log(
                f"Setup not ready: {signal['symbol']} "
                f"Conf={signal.get('confluence_score', 0):.0%} "
                f"(needs 75%+)"
            )
            result = {
                "status": "SKIPPED",
                "reason": "setup_not_ready",
                "signal": signal,
            }
        else:
            self.log(
                f"Executing: {signal['symbol']} {signal.get('direction')} "
                f"Conf={signal.get('confluence_score', 0):.0%}"
            )
            result = self.executor.execute_from_smc(signal)

        self.results.append(
            {
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "signal": signal,
                "execution": result,
            }
        )

        return result

    # --------------------------------------------------------------------------
    # FULL PIPELINE
    # --------------------------------------------------------------------------

    def run(self, symbol: str, timeframe: str = "H1") -> Dict:
        """
        Full pipeline: analyze → validate → execute.
        Returns execution result.
        """
        # Step 1: SMC Analysis (Agent 22)
        self.log("Step 1/3: Running SMC analysis (Agent 22)...")
        analysis = self.analyze(symbol, timeframe)

        if not analysis.get("setup_ready"):
            return {
                "step": "analysis",
                "status": "NO_SETUP",
                "symbol": symbol,
                "analysis": analysis,
                "message": f"{symbol} has no trade-ready setup. "
                f"Confluence {analysis.get('confluence_score', 0):.0%} (need 75%+)",
            }

        # Step 2: Kill zone + session check
        self.log("Step 2/3: Validating session context...")
        active_zones = analysis.get("kills_active", [])
        if not active_zones:
            self.log(f"  Warning: No active kill zones for {symbol}")

        # Step 3: Execute (Agent 28)
        self.log("Step 3/3: Executing trade (Agent 28)...")
        result = self.execute_signal(analysis)

        return {
            "step": "executed",
            "symbol": symbol,
            "analysis": analysis,
            "execution": result,
            "pipeline": "Agent 22 (SMC) -> Agent 28 (Executor) -> cTrader",
        }

    def summary(self) -> Dict:
        """Return pipeline summary."""
        total = len(self.results)
        executed = [
            r for r in self.results if r["execution"].get("status") == "EXECUTED"
        ]
        rejected = [
            r for r in self.results if r["execution"].get("status") == "REJECTED"
        ]
        dry_runs = [
            r for r in self.results if r["execution"].get("status") == "DRY_RUN"
        ]

        return {
            "mode": "DRY RUN" if self.dry_run else "LIVE DEMO",
            "total_signals": total,
            "executed": len(executed),
            "rejected": len(rejected),
            "dry_runs": len(dry_runs),
            "results": self.results,
        }


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="AgentFinance SMC Pipeline")
    parser.add_argument("symbol", nargs="?", default="EURUSD", help="Trading symbol")
    parser.add_argument(
        "timeframe", nargs="?", default="H1", help="Timeframe (H1, H4, D1)"
    )
    parser.add_argument(
        "--scan-all", action="store_true", help="Scan all monitored pairs"
    )
    parser.add_argument("--dry", action="store_true", help="Dry run (no execution)")
    parser.add_argument("--status", action="store_true", help="Show executor status")
    args = parser.parse_args()

    if args.status:
        executor = TradingExecutor()
        print(json.dumps(executor.cmd_report(), indent=2, default=str))
        return

    if args.scan_all:
        pipeline = SMCPipeline(dry_run=args.dry)
        signals = pipeline.scan_all()
        print(f"\n{'=' * 60}")
        print(f"  SMC Pipeline — Scan Results ({'DRY RUN' if args.dry else 'LIVE'})")
        print(f"{'=' * 60}")
        print(f"  Found {len(signals)} trade-ready setups\n")
        for s in signals:
            print(
                f"  {s['symbol']:8} {s['timeframe']:3} "
                f"{s['bias']:8} "
                f"Conf={s['confluence_score']:.0%} "
                f"OBs={s['order_blocks_count']} "
                f"FVGs={s['fvgs_count']} "
                f"Entry={s.get('entry_price')}"
            )
        if signals:
            mode_label = "DRY RUN — no execution" if args.dry else "Executing"
            print(f"\n  {mode_label} top setup...")
            top = signals[0]
            result = pipeline.execute_signal(top)
            print(
                f"\n  Result: {result.get('status')} — {result.get('reason', result.get('order_id', ''))}"
            )
        print(json.dumps(pipeline.summary(), indent=2, default=str))
        return

    # Single pair run
    pipeline = SMCPipeline(dry_run=args.dry)
    result = pipeline.run(args.symbol.upper(), args.timeframe.upper())
    print(json.dumps(result, indent=2, default=str))
    print(f"\n{'=' * 60}")
    print(f"  Summary: {json.dumps(pipeline.summary(), indent=2, default=str)}")


if __name__ == "__main__":
    main()
