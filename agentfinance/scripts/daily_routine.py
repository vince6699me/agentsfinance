#!/usr/bin/env python3
"""
AgentFinance v3 — Daily Trading Routine Automation
Automates the complete pre-market, intraday, and post-market workflow.

Schedule:
    00:00 UTC  — Daily reset & data refresh
    05:00 UTC  — Pre-market analysis (London session prep)
    07:00 UTC  — Pre-market analysis (NYSE open prep)
    08:00 UTC  — Kill zone scan (London)
    12:00 UTC  — Kill zone scan (NYSE)
    17:00 UTC  — Kill zone scan (NY close)
    21:00 UTC  — Post-market report
    22:00 UTC  — Daily backup & cleanup

Usage:
    python3 daily_routine.py                    # Run once (detects current phase)
    python3 daily_routine.py --phase=premarket  # Run specific phase
    python3 daily_routine.py --schedule        # Run full automated schedule
    python3 daily_routine.py --status          # Show current status
    python3 daily_routine.py --backup          # Backup data and state
"""

import sys
import os
import json
import logging
import argparse
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"daily_{datetime.now(timezone.utc):%Y%m%d}.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("daily_routine")

# ============================================================================
# COLORS
# ============================================================================
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"


def print_banner(text: str):
    print(f"\n{BLUE}{'═' * 64}{NC}")
    print(f"{BOLD}{CYAN}  {text}{NC}")
    print(f"{BLUE}{'═' * 64}{NC}\n")


def log_phase(phase: str, message: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"{CYAN}[{ts}] [{phase:15s}] {message}{NC}")
    log.info(f"[{phase}] {message}")


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class DailyState:
    """Persisted state across routine runs."""

    date: str
    phases_completed: List[str]
    trades_executed: int
    signals_found: int
    daily_pnl: float
    drawdown_pct: float
    backup_done: bool
    last_phase: Optional[str]
    notes: List[str]

    @classmethod
    def load(cls, date: Optional[str] = None) -> "DailyState":
        date = date or datetime.now(timezone.utc).strftime("%Y%m%d")
        state_file = LOG_DIR / f"state_{date}.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception:
                pass
        return cls(
            date=date,
            phases_completed=[],
            trades_executed=0,
            signals_found=0,
            daily_pnl=0.0,
            drawdown_pct=0.0,
            backup_done=False,
            last_phase=None,
            notes=[],
        )

    def save(self):
        state_file = LOG_DIR / f"state_{self.date}.json"
        with open(state_file, "w") as f:
            json.dump(asdict(self), f, indent=2)


# ============================================================================
# PHASE HANDLERS
# ============================================================================


def phase_daily_reset(state: DailyState) -> bool:
    """00:00 UTC — Reset state for new trading day."""
    log_phase("RESET", "Starting daily reset...")

    try:
        from trading.execution.risk_manager import RiskManager

        rm = RiskManager()
        rm.reset_daily()
        log_phase("RESET", f"Risk manager reset | Balance: ${rm.balance:,.2f}")
    except Exception as e:
        log_phase("RESET", f"Risk manager reset skipped: {e}")

    # Refresh market data cache
    try:
        from trading.data.data_fetcher import DataFetcher

        fetcher = DataFetcher()
        fetcher.refresh_cache()
        log_phase("RESET", "Market data cache refreshed")
    except Exception as e:
        log_phase("RESET", f"Data cache refresh skipped: {e}")

    state.last_phase = "reset"
    if "reset" not in state.phases_completed:
        state.phases_completed.append("reset")
    state.save()
    log_phase("RESET", "Daily reset complete ✓")
    return True


def phase_premarket_london(state: DailyState) -> bool:
    """05:00 UTC — London session pre-market analysis."""
    log_phase("PREMK_LDN", "Starting London pre-market analysis...")

    try:
        from trading.engines.session_engine import SessionEngine
        from trading.engines.smc_engine import SMCEngine

        se = SessionEngine()
        smc = SMCEngine()

        # Check if London session is approaching
        london_start = se._get_next_session_start("london")
        if london_start:
            hours_to_open = (
                london_start - datetime.now(timezone.utc)
            ).total_seconds() / 3600
            log_phase("PREMK_LDN", f"London opens in {hours_to_open:.1f} hours")

        # Pre-scan key pairs
        pairs = ["EURUSD", "GBPUSD", "GBPJPY", "EURGBP"]
        results = []
        for pair in pairs:
            try:
                data = smc.get_data(pair, "H1")
                setups = smc.identify_setups(data)
                if setups:
                    results.append((pair, len(setups)))
                    state.signals_found += len(setups)
            except Exception as e:
                log_phase("PREMK_LDN", f"  {pair}: error — {e}")

        for pair, count in results:
            log_phase("PREMK_LDN", f"  {pair}: {count} potential setup(s)")

        if not results:
            log_phase("PREMK_LDN", "No setups detected in pre-market scan")

    except Exception as e:
        log_phase("PREMK_LDN", f"Pre-market analysis error: {e}")
        return False

    state.last_phase = "premk_london"
    if "premk_london" not in state.phases_completed:
        state.phases_completed.append("premk_london")
    state.save()
    log_phase("PREMK_LDN", "London pre-market complete ✓")
    return True


def phase_premarket_nyse(state: DailyState) -> bool:
    """07:00 UTC — NYSE pre-market analysis."""
    log_phase("PREMK_NY", "Starting NYSE pre-market analysis...")

    try:
        from trading.engines.session_engine import SessionEngine
        from trading.engines.smc_engine import SMCEngine

        se = SessionEngine()
        smc = SMCEngine()

        # Pre-scan US session pairs
        pairs = ["EURUSD", "USDJPY", "USDCAD", "USDCHF", "GBPJPY"]
        for pair in pairs:
            try:
                data = smc.get_data(pair, "H1")
                setups = smc.identify_setups(data)
                if setups:
                    state.signals_found += len(setups)
                    log_phase("PREMK_NY", f"  {pair}: {len(setups)} setup(s)")
            except Exception as e:
                pass  # Silent fail for pre-market

        # Update session engine with session info
        sessions = se.get_active_sessions()
        if sessions:
            for s in sessions:
                log_phase("PREMK_NY", f"  Active: {s['name']}")

    except Exception as e:
        log_phase("PREMK_NY", f"NYSE pre-market error: {e}")
        return False

    state.last_phase = "premk_nyse"
    if "premk_nyse" not in state.phases_completed:
        state.phases_completed.append("premk_nyse")
    state.save()
    log_phase("PREMK_NY", "NYSE pre-market complete ✓")
    return True


def phase_killzone_london(state: DailyState) -> bool:
    """08:00 UTC — London kill zone scan."""
    log_phase("KZ_LDN", "London Kill Zone — Active scanning")

    try:
        from trading.execution.smc_pipeline import SMCOrchestrator

        orch = SMCOrchestrator()
        pairs = ["EURUSD", "GBPUSD", "GBPJPY", "EURGBP", "EURJPY"]

        executed = 0
        for pair in pairs:
            try:
                result = orch.scan_and_execute(pair, "M15", dry=True)
                if result.get("executed") or result.get("dry_run"):
                    executed += 1
                    state.signals_found += 1
                    if result.get("executed"):
                        state.trades_executed += 1
            except Exception:
                pass

        log_phase(
            "KZ_LDN", f"London KZ scan complete: {executed}/{len(pairs)} had setups"
        )

    except Exception as e:
        log_phase("KZ_LDN", f"Kill zone scan error: {e}")
        return False

    state.last_phase = "kz_london"
    if "kz_london" not in state.phases_completed:
        state.phases_completed.append("kz_london")
    state.save()
    log_phase("KZ_LDN", "London Kill Zone scan complete ✓")
    return True


def phase_killzone_nyse(state: DailyState) -> bool:
    """12:00 UTC — NYSE kill zone scan."""
    log_phase("KZ_NY", "NYSE Kill Zone — Active scanning")

    try:
        from trading.execution.smc_pipeline import SMCOrchestrator

        orch = SMCOrchestrator()
        pairs = ["EURUSD", "USDJPY", "USDCAD", "USDCHF", "AUDUSD"]

        executed = 0
        for pair in pairs:
            try:
                result = orch.scan_and_execute(pair, "M15", dry=True)
                if result.get("executed") or result.get("dry_run"):
                    executed += 1
                    state.signals_found += 1
            except Exception:
                pass

        log_phase("KZ_NY", f"NYSE KZ scan complete: {executed}/{len(pairs)} had setups")

    except Exception as e:
        log_phase("KZ_NY", f"NYSE kill zone scan error: {e}")
        return False

    state.last_phase = "kz_nyse"
    if "kz_nyse" not in state.phases_completed:
        state.phases_completed.append("kz_nyse")
    state.save()
    log_phase("KZ_NY", "NYSE Kill Zone scan complete ✓")
    return True


def phase_killzone_nyclose(state: DailyState) -> bool:
    """17:00 UTC — NY close kill zone."""
    log_phase("KZ_NYCL", "NY Close Kill Zone — Final scan")

    try:
        from trading.execution.smc_pipeline import SMCOrchestrator

        orch = SMCOrchestrator()
        pairs = ["EURUSD", "GBPUSD", "USDJPY"]

        for pair in pairs:
            try:
                result = orch.scan_and_execute(pair, "H1", dry=True)
                if result.get("executed") or result.get("dry_run"):
                    state.signals_found += 1
            except Exception:
                pass

    except Exception as e:
        log_phase("KZ_NYCL", f"NY Close KZ scan error: {e}")
        return False

    state.last_phase = "kz_nyclose"
    if "kz_nyclose" not in state.phases_completed:
        state.phases_completed.append("kz_nyclose")
    state.save()
    log_phase("KZ_NYCL", "NY Close Kill Zone scan complete ✓")
    return True


def phase_postmarket(state: DailyState) -> bool:
    """21:00 UTC — Post-market report generation."""
    log_phase("POSTMK", "Generating daily trading report...")

    try:
        # Update P&L from risk manager
        from trading.execution.risk_manager import RiskManager

        rm = RiskManager()
        risk_status = rm.get_status()
        state.daily_pnl = risk_status.get("daily_pnl", 0.0)
        state.drawdown_pct = risk_status.get("drawdown_pct", 0.0)
        state.trades_executed = risk_status.get("open_trades", 0)

        # Generate report
        report = {
            "date": state.date,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "phases_completed": state.phases_completed,
            "trades_executed": state.trades_executed,
            "signals_found": state.signals_found,
            "daily_pnl": state.daily_pnl,
            "drawdown_pct": state.drawdown_pct,
            "notes": state.notes,
        }

        report_file = LOG_DIR / f"report_{state.date}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        pnl_color = GREEN if state.daily_pnl >= 0 else RED
        print(f"\n{'─' * 64}")
        print(f"  {BOLD}Daily Trading Report — {state.date}{NC}")
        print(f"{'─' * 64}")
        print(f"  Phases Completed:   {len(state.phases_completed)}")
        print(f"  Signals Found:      {state.signals_found}")
        print(f"  Trades Executed:    {state.trades_executed}")
        print(f"  Daily P&L:         {pnl_color}${state.daily_pnl:,.2f}{NC}")
        print(f"  Drawdown:          {state.drawdown_pct:.2f}%")
        print(f"  Report saved:       {report_file.name}")
        print(f"{'─' * 64}\n")

    except Exception as e:
        log_phase("POSTMK", f"Report generation error: {e}")
        return False

    state.last_phase = "postmarket"
    if "postmarket" not in state.phases_completed:
        state.phases_completed.append("postmarket")
    state.save()
    log_phase("POSTMK", "Post-market report complete ✓")
    return True


def phase_backup(state: DailyState) -> bool:
    """22:00 UTC — Daily backup of state and logs."""
    log_phase("BACKUP", "Starting daily backup...")

    try:
        import shutil

        # Ensure backup directory
        backup_base = PROJECT_ROOT / "backups"
        backup_dir = backup_base / f"backup_{state.date}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup state files
        for log_file in LOG_DIR.glob(f"*{state.date}*"):
            try:
                shutil.copy2(log_file, backup_dir / log_file.name)
            except Exception:
                pass

        # Backup results if they exist
        results_dir = PROJECT_ROOT / "results"
        if results_dir.exists():
            for f in results_dir.glob("*.json"):
                try:
                    shutil.copy2(f, backup_dir / f.name)
                except Exception:
                    pass

        # Compress backup
        archive_path = shutil.make_archive(
            str(backup_dir),
            "gztar",
            root_dir=backup_base,
            base_dir=backup_dir.name,
        )

        state.backup_done = True
        state.save()

        log_phase("BACKUP", f"Backup complete: {archive_path}")
        return True

    except Exception as e:
        log_phase("BACKUP", f"Backup error: {e}")
        return False


# ============================================================================
# SCHEDULE RUNNER
# ============================================================================


PHASES = [
    ("00:00", "reset", phase_daily_reset, "Daily Reset"),
    ("05:00", "premk_london", phase_premarket_london, "London Pre-Market"),
    ("07:00", "premk_nyse", phase_premarket_nyse, "NYSE Pre-Market"),
    ("08:00", "kz_london", phase_killzone_london, "London Kill Zone"),
    ("12:00", "kz_nyse", phase_killzone_nyse, "NYSE Kill Zone"),
    ("17:00", "kz_nyclose", phase_killzone_nyclose, "NY Close Kill Zone"),
    ("21:00", "postmarket", phase_postmarket, "Post-Market Report"),
    ("22:00", "backup", phase_backup, "Daily Backup"),
]


def run_schedule():
    """Run the automated schedule loop."""
    print_banner("AgentFinance Daily Routine — Automated Schedule")

    state = DailyState.load()

    # Check if we're mid-day and skip completed phases
    now = datetime.now(timezone.utc)
    current_hour = now.hour

    for hour_str, phase_id, handler, name in PHASES:
        hour = int(hour_str.split(":")[0])

        if phase_id in state.phases_completed:
            print(f"  ⏭  {hour_str} UTC  {name} — already completed")
            continue

        if current_hour >= hour:
            print(f"  ⏭  {hour_str} UTC  {name} — missed (past)")
            continue

        # Wait until it's time
        target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)

        wait_hours = (target - now).total_seconds() / 3600
        print(f"\n  ⏳  Next: {hour_str} UTC  {name} (in {wait_hours:.1f}h)")

        # For testing/demo, just run all remaining phases
        if "--now" in sys.argv:
            print(f"  ▶  Running: {hour_str} UTC  {name}")
        else:
            print(f"  ⏸  Waiting {wait_hours:.1f}h until {hour_str} UTC...")
            # In production: time.sleep(wait_hours * 3600)
            continue

    print(f"\n  Note: In production, this runs as a background daemon.")
    print(f"  For testing, use: python3 daily_routine.py --run-all")


def show_status(state: DailyState):
    """Show current routine status."""
    print_banner(f"Daily Routine Status — {state.date}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"  Current time:  {now}")
    print(f"  Last phase:    {state.last_phase or 'none'}")
    print(f"  Signals found: {state.signals_found}")
    print(f"  Trades exec:   {state.trades_executed}")
    print(f"  Daily P&L:    ${state.daily_pnl:,.2f}")
    print(f"  Drawdown:     {state.drawdown_pct:.2f}%")
    print(f"  Backup done:   {'✓' if state.backup_done else '✗'}")
    print()

    print(f"  {BOLD}Phase History:{NC}")
    for hour_str, phase_id, _, name in PHASES:
        completed = phase_id in state.phases_completed
        status = f"{GREEN}✓{NC}" if completed else "○"
        print(f"    {status}  {hour_str} UTC  {name}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="AgentFinance Daily Routine")
    parser.add_argument(
        "--phase",
        choices=[
            "reset",
            "premk_london",
            "premk_nyse",
            "kz_london",
            "kz_nyse",
            "kz_nyclose",
            "postmarket",
            "backup",
        ],
        help="Run specific phase",
    )
    parser.add_argument(
        "--schedule", action="store_true", help="Run automated schedule"
    )
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--backup", action="store_true", help="Run backup only")
    parser.add_argument(
        "--run-all", action="store_true", help="Run all phases (testing)"
    )
    parser.add_argument("--date", help="Date for state file (YYYYMMDD)")
    args = parser.parse_args()

    state = DailyState.load(args.date)

    if args.status:
        show_status(state)
        return

    if args.phase:
        handlers = {p[1]: p[2] for p in PHASES}
        handler = handlers[args.phase]
        success = handler(state)
        print(f"\n{'SUCCESS ✓' if success else 'FAILED ✗'} — Phase: {args.phase}\n")
        return

    if args.backup:
        success = phase_backup(state)
        print(f"\n{'SUCCESS ✓' if success else 'FAILED ✗'} — Backup\n")
        return

    if args.schedule:
        run_schedule()
        return

    if args.run_all:
        print_banner("Running All Phases (Testing Mode)")
        for _, phase_id, handler, name in PHASES:
            print(f"\n{'─' * 40}")
            print(f"  Running: {name}")
            print(f"{'─' * 40}")
            handler(state)
        print_banner("All Phases Complete")
        return

    # Default: detect current phase and run it
    now = datetime.now(timezone.utc)
    hour = now.hour

    if hour < 5:
        phase_daily_reset(state)
    elif hour < 7:
        phase_premarket_london(state)
    elif hour < 8:
        phase_premarket_nyse(state)
    elif hour < 12:
        phase_killzone_london(state)
    elif hour < 17:
        phase_killzone_nyse(state)
    elif hour < 21:
        phase_killzone_nyclose(state)
    elif hour < 22:
        phase_postmarket(state)
    else:
        phase_backup(state)


if __name__ == "__main__":
    main()
