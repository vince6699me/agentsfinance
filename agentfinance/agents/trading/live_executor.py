#!/usr/bin/env python3
"""
Agent 28 - Live Trading Executor
Complete signal-to-execution pipeline via cTrader.
Receives signals from Agent 22 (SMC Strategy) and executes live trades.

Pepperstone Demo Account ID: 46729678

Usage:
    python live_executor.py positions       # List open positions
    python live_executor.py execute EURUSD BUY 1.0823 1.0756 1.0950 0.10
    python live_executor.py close #1247
    python live_executor.py risk-check
    python live_executor.py halt
    python live_executor.py report

Signal format from Agent 22 (SMC):
    {
        "symbol": "EURUSD",
        "direction": "BUY",
        "entry_price": 1.0823,
        "stop_loss": 1.0756,
        "take_profit": 1.0890,
        "volume": 0.10,
        "confidence": 0.82,
        "kill_zone": "London",
        "setup_type": "Order Block Retest",
    }
"""

import sys
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Add trading execution path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "trading", "execution")
)

from ctrader_client import CTraderClient

try:
    from risk_manager import RiskManager, RiskConfig

    RISK_CONFIG = RiskConfig()
except ImportError:
    RiskManager = None
    RISK_CONFIG = None

# ============================================================================
# CONFIGURATION
# ============================================================================

ACCOUNT_ID = 46729678  # Pepperstone Demo

RISK_LIMITS = {
    "max_risk_per_trade": 0.01,  # 1% per trade
    "max_daily_loss": 0.03,  # 3% daily halt
    "max_positions": 5,  # Max 5 open positions
    "min_rr_ratio": 1.5,  # Min 1.5:1 reward:risk
    "min_confidence": 0.75,  # Min 75% confidence
}

# ============================================================================
# TRADING EXECUTOR
# ============================================================================


class TradingExecutor:
    """
    Live trading executor with full cTrader integration.
    Implements the complete signal -> risk check -> execution pipeline.
    """

    def __init__(self):
        # Initialize cTrader client
        self.client = CTraderClient(
            account_id=ACCOUNT_ID,
            host=os.environ.get("CTRADER_HOST", "demo"),
        )
        self.client.connect(timeout=30)

        # Initialize risk manager
        self.risk = RiskManager(RISK_CONFIG) if RiskManager else None

        # State
        self.status = "ACTIVE"
        self.halted_since = None
        self.halt_reason = None

        # Session tracking
        self.session_start = datetime.now(timezone.utc)
        self.daily_pnl = 0.0
        self.trades_today = 0

        self._log(f"Executor initialized — Status: {self.status}")

    def _log(self, msg: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        print(f"[{ts}] [Executor] {msg}")

    # -------------------------------------------------------------------------
    # CORE EXECUTION
    # -------------------------------------------------------------------------

    def cmd_execute(self, signal: Dict[str, Any]) -> Dict:
        """
        Execute a trade signal from SMC analysis.
        Full pipeline: signal validation -> risk check -> order placement.
        """
        self._log(
            f"EXECUTE signal received: {signal.get('symbol')} {signal.get('direction')}"
        )

        # Gate 1: System halted
        if self.status == "HALTED":
            self._log("BLOCKED — system halted")
            return {
                "status": "REJECTED",
                "reason": f"System HALTED — {self.halt_reason or 'see /trade:resume'}",
                "gate": "system_halt",
            }

        # Gate 2: Required fields
        required = ["symbol", "direction", "entry_price", "stop_loss", "take_profit"]
        missing = [f for f in required if f not in signal]
        if missing:
            return {
                "status": "REJECTED",
                "reason": f"Missing fields: {', '.join(missing)}",
                "gate": "validation",
            }

        symbol = signal["symbol"].upper()
        direction = signal["direction"].upper()
        entry = float(signal["entry_price"])
        stop_loss = float(signal["stop_loss"])
        take_profit = float(signal["take_profit"])
        volume = float(signal.get("volume", 0.10))
        confidence = float(signal.get("confidence", 0.75))
        label = signal.get(
            "label", f"SMC-{datetime.now(timezone.utc).strftime('%m%d')}"
        )

        # Gate 3: Confidence threshold
        if confidence < RISK_LIMITS["min_confidence"]:
            return {
                "status": "REJECTED",
                "reason": f"Confidence {confidence:.0%} below minimum {RISK_LIMITS['min_confidence']:.0%}",
                "gate": "confidence",
            }

        # Gate 4: Position limit
        positions = self.client.get_positions()
        if len(positions) >= RISK_LIMITS["max_positions"]:
            return {
                "status": "REJECTED",
                "reason": f"Max positions ({RISK_LIMITS['max_positions']}) reached",
                "gate": "position_limit",
            }

        # Gate 5: Risk-reward ratio
        risk_pips = abs(entry - stop_loss)
        reward_pips = abs(take_profit - entry)
        rr_ratio = reward_pips / risk_pips if risk_pips > 0 else 0
        if rr_ratio < RISK_LIMITS["min_rr_ratio"]:
            return {
                "status": "REJECTED",
                "reason": f"RR {rr_ratio:.2f} below minimum {RISK_LIMITS['min_rr_ratio']}",
                "gate": "risk_reward",
            }

        # Gate 6: Full risk manager checks
        if self.risk:
            risk_check = self.risk.pre_trade_check(
                {
                    "symbol": symbol,
                    "direction": direction,
                    "entry_price": entry,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "volume": volume,
                    "confidence": confidence,
                }
            )
            if not risk_check.get("passed", False):
                return {
                    "status": "REJECTED",
                    "reason": risk_check.get("reason", "Risk check failed"),
                    "gate": "risk_manager",
                    "risk_details": risk_check,
                }

        # Execute
        self._log(
            f"Executing: {direction} {volume} lots {symbol} "
            f"Entry={entry} SL={stop_loss} TP={take_profit} "
            f"RR={rr_ratio:.2f} Conf={confidence:.0%}"
        )

        result = self.client.place_market_order(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume=volume,
            label=label,
        )

        if not result.get("success"):
            return {
                "status": "REJECTED",
                "reason": result.get("error", "Order placement failed"),
                "gate": "order_placement",
            }

        self.trades_today += 1
        self._log(
            f"Order placed: {result.get('order_id', 'N/A')} — {result.get('status')}"
        )

        return {
            "status": "EXECUTED",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "order_id": result.get("order_id"),
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "volume": volume,
            "rr_ratio": round(rr_ratio, 2),
            "confidence": confidence,
            "risk_amount_pct": RISK_LIMITS["max_risk_per_trade"],
            "kill_zone": signal.get("kill_zone"),
            "setup_type": signal.get("setup_type"),
            "label": label,
            "simulation": result.get("simulation", False),
        }

    # -------------------------------------------------------------------------
    # POSITION MANAGEMENT
    # -------------------------------------------------------------------------

    def cmd_close(
        self, position_id: str, volume: float = None, reason: str = "manual"
    ) -> Dict:
        """Close an open position."""
        self._log(f"CLOSE position: #{position_id} ({reason})")
        try:
            pid = int(position_id.lstrip("#"))
        except ValueError:
            return {"status": "ERROR", "reason": f"Invalid position ID: {position_id}"}

        result = self.client.close_position(pid, volume)
        if result.get("success"):
            self._log(f"Position #{position_id} close requested")
            return {
                "status": "CLOSED",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "position_id": position_id,
                "closed_volume": volume or "FULL",
                "reason": reason,
            }
        return {
            "status": "FAILED",
            "reason": result.get("error", "Close failed"),
            "position_id": position_id,
        }

    def cmd_modify(
        self, position_id: str, stop_loss: float = None, take_profit: float = None
    ) -> Dict:
        """Modify position SL/TP."""
        self._log(f"MODIFY position: #{position_id} SL={stop_loss} TP={take_profit}")
        if self.risk:
            result = self.risk.modify_position(position_id, stop_loss, take_profit)
            return {"status": "MODIFIED", "position_id": position_id, **result}
        return {"status": "MODIFIED", "position_id": position_id, "simulation": True}

    def cmd_positions(self) -> Dict:
        """List all open positions."""
        positions = self.client.get_positions()
        account = self.client.get_account_summary()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": self.status,
            "account": account,
            "open_positions": [
                {
                    "id": f"#{p['id']}",
                    "symbol": p["symbol_name"],
                    "side": p["side"],
                    "volume": p["volume"],
                    "entry": p.get("entry_price"),
                    "pnl": round(p.get("pnl", 0), 2),
                    "swap": round(p.get("swap", 0), 2),
                }
                for p in positions
            ],
            "count": len(positions),
            "max_allowed": RISK_LIMITS["max_positions"],
            "margin_level": account.get("margin_level"),
            "daily_pnl": round(self.daily_pnl, 2),
        }

    def cmd_pending(self) -> Dict:
        """List all pending (limit/stop) orders."""
        orders = self.client.get_pending_orders()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "pending_orders": [
                {
                    "id": f"#{o['id']}",
                    "symbol": o["symbol_name"],
                    "side": o["side"],
                    "volume": o["volume"],
                }
                for o in orders
            ],
            "count": len(orders),
        }

    # -------------------------------------------------------------------------
    # RISK & REPORTING
    # -------------------------------------------------------------------------

    def cmd_risk_check(self) -> Dict:
        """Run all risk checks."""
        checks = {}
        account = self.client.get_account_summary()

        # 1. Daily loss
        daily_pnl_pct = abs(self.daily_pnl) / max(account.get("balance", 10500), 1)
        checks["daily_loss"] = {
            "passed": daily_pnl_pct < RISK_LIMITS["max_daily_loss"],
            "current_pct": round(daily_pnl_pct * 100, 2),
            "limit_pct": RISK_LIMITS["max_daily_loss"] * 100,
            "daily_pnl": round(self.daily_pnl, 2),
        }

        # 2. Position limit
        positions = self.client.get_positions()
        checks["position_limit"] = {
            "passed": len(positions) < RISK_LIMITS["max_positions"],
            "current": len(positions),
            "limit": RISK_LIMITS["max_positions"],
        }

        # 3. Margin level
        margin_level = account.get("margin_level", 999)
        checks["margin_level"] = {
            "passed": margin_level > 150,
            "current": round(margin_level, 1),
            "minimum": 150,
        }

        # 4. Full risk manager
        if self.risk:
            rm_checks = self.risk.run_all_checks()
            checks.update(rm_checks)

        all_passed = all(c.get("passed", True) for c in checks.values())

        # Auto-halt if daily loss exceeded
        if not checks["daily_loss"]["passed"] and self.status == "ACTIVE":
            self._log("CRITICAL: Daily loss limit exceeded — AUTO HALT")
            self.cmd_halt("Daily loss limit exceeded")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "all_checks_passed": all_passed,
            "system_status": self.status,
            "checks": checks,
        }

    def cmd_daily_pnl(self) -> Dict:
        """Get daily P&L report."""
        pnl_data = self.client.get_daily_pnl()
        account = self.client.get_account_summary()
        self.daily_pnl = pnl_data.get("daily_pnl", 0)
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            **pnl_data,
            "trades_today": self.trades_today,
            "within_daily_limit": abs(self.daily_pnl)
            < RISK_LIMITS["max_daily_loss"] * account.get("balance", 10500),
        }

    def cmd_report(self) -> Dict:
        """Generate full trading report."""
        account = self.client.get_account_summary()
        positions = self.client.get_positions()
        pnl_data = self.client.get_daily_pnl()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "system_status": self.status,
            "halted_since": self.halted_since.isoformat()
            if self.halted_since
            else None,
            "account": account,
            "open_positions": len(positions),
            "max_positions": RISK_LIMITS["max_positions"],
            "daily_pnl": pnl_data.get("daily_pnl"),
            "daily_pnl_pct": pnl_data.get("daily_pnl_pct"),
            "trades_today": self.trades_today,
            "margin_level": account.get("margin_level"),
            "risk_limits": RISK_LIMITS,
        }

    # -------------------------------------------------------------------------
    # EMERGENCY CONTROLS
    # -------------------------------------------------------------------------

    def cmd_halt(self, reason: str = "Manual") -> Dict:
        """Emergency halt — stop all trading."""
        self.status = "HALTED"
        self.halted_since = datetime.now(timezone.utc)
        self.halt_reason = reason
        self._log(f"*** HALTED: {reason} ***")

        close_result = self.client.close_all_positions()

        return {
            "status": "HALTED",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "halted_since": self.halted_since.isoformat(),
            "reason": reason,
            "positions_closed": close_result.get("closed_count", 0),
            "action": "All positions closed. Trading suspended. Use /trade:resume.",
        }

    def cmd_resume(self) -> Dict:
        """Resume trading after halt."""
        if self.status != "HALTED":
            return {
                "status": "IGNORED",
                "reason": "Not halted",
                "current_status": self.status,
            }

        self.status = "ACTIVE"
        duration = (
            (datetime.now(timezone.utc) - self.halted_since).total_seconds()
            if self.halted_since
            else 0
        )
        self._log(f"RESUMED after {duration:.0f}s halt")
        self.halted_since = None
        self.halt_reason = None

        return {
            "status": "ACTIVE",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "halt_duration_seconds": round(duration),
            "action": "Trading resumed. All safety gates active.",
        }

    def cmd_cancel_order(self, order_id: str) -> Dict:
        """Cancel a pending order."""
        try:
            oid = int(order_id.lstrip("#"))
        except ValueError:
            return {"status": "ERROR", "reason": f"Invalid order ID: {order_id}"}
        result = self.client.cancel_order(oid)
        self._log(f"Order #{order_id} cancel: {result.get('status')}")
        return {"timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), **result}

    # -------------------------------------------------------------------------
    # SMC PIPELINE — Agent 22 -> Agent 28
    # -------------------------------------------------------------------------

    def execute_from_smc(self, smc_signal: Dict[str, Any]) -> Dict:
        """
        Full SMC -> Execution pipeline.
        Receives output from Agent 22 (SMC Strategy) and executes if all gates pass.

        Expected smc_signal format from Agent 22:
            {
                "symbol": "EURUSD",
                "direction": "BUY",
                "bias": "BULLISH",
                "confluence_score": 0.82,
                "kill_zone": "London",
                "entry_price": 1.0823,
                "stop_loss": 1.0756,
                "take_profit_1": 1.0890,
                "take_profit_2": 1.0980,
                "volume": 0.10,
                "setup_type": "Order Block Retest",
            }
        """
        signal = {
            "symbol": smc_signal.get("symbol"),
            "direction": smc_signal.get("direction"),
            "entry_price": smc_signal.get("entry_price"),
            "stop_loss": smc_signal.get("stop_loss"),
            "take_profit": smc_signal.get("take_profit_1")
            or smc_signal.get("take_profit"),
            "volume": float(smc_signal.get("volume", 0.10)),
            "confidence": float(smc_signal.get("confluence_score", 0.75)),
            "kill_zone": smc_signal.get("kill_zone"),
            "setup_type": smc_signal.get("setup_type") or smc_signal.get("bias"),
            "smc_bias": smc_signal.get("bias"),
        }
        result = self.cmd_execute(signal)
        result["smc_pipeline"] = True
        result["smc_bias"] = signal["smc_bias"]
        result["kill_zone"] = signal["kill_zone"]
        return result


# ============================================================================
# CLI ENTRY POINT
# ============================================================================


def main():
    executor = TradingExecutor()

    if len(sys.argv) < 2:
        print("Agent 28 — Live Trading Executor")
        print(
            "Commands: positions, pending, risk-check, daily-pnl, report, halt, resume"
        )
        print("Usage:")
        print("  python live_executor.py positions")
        print("  python live_executor.py execute EURUSD BUY 1.0823 1.0756 1.0950 0.10")
        print("  python live_executor.py close #1247")
        print("  python live_executor.py risk-check")
        print("  python live_executor.py halt")
        print("  python live_executor.py smc signal.json")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "execute" and len(args) >= 5:
        symbol, direction = args[0], args[1]
        entry, sl, tp = float(args[2]), float(args[3]), float(args[4])
        volume = float(args[5]) if len(args) > 5 else 0.10
        result = executor.cmd_execute(
            {
                "symbol": symbol,
                "direction": direction,
                "entry_price": entry,
                "stop_loss": sl,
                "take_profit": tp,
                "volume": volume,
            }
        )
    elif cmd == "close" and len(args) >= 1:
        result = executor.cmd_close(args[0])
    elif cmd == "cancel" and len(args) >= 1:
        result = executor.cmd_cancel_order(args[0])
    elif cmd == "smc" and len(args) >= 1:
        try:
            with open(args[0]) as f:
                smc_signal = json.load(f)
            result = executor.execute_from_smc(smc_signal)
        except Exception as e:
            result = {"error": str(e)}
    elif cmd == "positions":
        result = executor.cmd_positions()
    elif cmd == "pending":
        result = executor.cmd_pending()
    elif cmd == "risk-check":
        result = executor.cmd_risk_check()
    elif cmd == "daily-pnl":
        result = executor.cmd_daily_pnl()
    elif cmd == "report":
        result = executor.cmd_report()
    elif cmd == "halt":
        result = executor.cmd_halt("Manual CLI")
    elif cmd == "resume":
        result = executor.cmd_resume()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
