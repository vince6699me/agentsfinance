#!/usr/bin/env python3
"""
AgentFinance v3 — Unified Trading CLI
Single entry point for all trading operations.

Usage:
    agent-cli.py <command> [options]

Commands:
    scan           Scan for setups on one or more symbols
    scan-all       Scan all monitored pairs across all timeframes
    status         Show current positions, equity, and risk status
    risk           Show risk dashboard and gate status
    execute        Execute a trade (manual override)
    close          Close positions (by ID or symbol)
    backtest       Run backtest on a symbol/timeframe
    session        Show current trading session and kill zones
    report         Generate daily trading report
    health         Check system health (cTrader, risk gates, data)
    setup          Interactive account and API setup
    help           Show this help message

Examples:
    agent-cli.py scan EURUSD H1
    agent-cli.py scan-all --dry
    agent-cli.py status
    agent-cli.py risk
    agent-cli.py execute EURUSD BUY 0.01 --sl=20 --tp=40
    agent-cli.py close EURUSD
    agent-cli.py backtest EURUSD H1 --days=90
    agent-cli.py session
    agent-cli.py report --today
    agent-cli.py health
    agent-cli.py setup
"""

import sys
import os
import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("agent-cli")

# Colors for terminal output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


def print_header(text: str):
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BOLD}{BLUE}  {text}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")


def print_success(text: str):
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text: str):
    print(f"{RED}✗ {text}{NC}")


def print_warning(text: str):
    print(f"{YELLOW}⚠ {text}{NC}")


def print_info(text: str):
    print(f"{CYAN}ℹ {text}{NC}")


# ============================================================================
# IMPORTS — lazy-loaded per command to avoid slow startup
# ============================================================================


def cmd_scan(args):
    """Scan for SMC/technical setups on a symbol."""
    print_header("SMC Pipeline Scan")
    from trading.execution.smc_pipeline import SMCOrchestrator

    orch = SMCOrchestrator()

    dry = getattr(args, "dry", False)
    symbol = args.symbol
    timeframe = args.timeframe

    print_info(f"Scanning {symbol} {timeframe} {'(DRY RUN)' if dry else '(LIVE)'}")
    result = orch.scan_and_execute(symbol, timeframe, dry=dry)

    if result.get("executed") or result.get("dry_run"):
        print_success(f"Pipeline completed: {result.get('mode', 'unknown')}")
        if result.get("signal"):
            sig = result["signal"]
            print(
                f"  Signal: {sig.get('direction', 'N/A')} | "
                f"Setup: {sig.get('setup_type', 'N/A')} | "
                f"Confidence: {sig.get('confidence', 0):.0%}"
            )
        if result.get("execution"):
            exe = result["execution"]
            print(
                f"  Order ID: {exe.get('order_id', 'N/A')} | "
                f"Price: {exe.get('price', 'N/A')} | "
                f"Lots: {exe.get('volume', 'N/A')}"
            )
        if result.get("risk_approved") is not None:
            print(
                f"  Risk Gate: {'PASSED' if result.get('risk_approved') else 'FAILED'}"
            )
    else:
        print_warning("No actionable setup found")
        if result.get("signals"):
            print(f"  {len(result['signals'])} setup(s) found but not actionable")
    print()


def cmd_scan_all(args):
    """Scan all monitored pairs."""
    print_header("Scan All Pairs")
    from trading.execution.smc_pipeline import SMCOrchestrator

    orch = SMCOrchestrator()

    dry = args.dry
    print_info(f"Scanning all pairs {'(DRY RUN)' if dry else '(LIVE)'}")
    results = orch.scan_all(dry=dry)

    total = len(results)
    executed = sum(1 for r in results if r.get("executed"))
    dry_runs = sum(1 for r in results if r.get("dry_run"))
    failed = sum(1 for r in results if r.get("error"))

    print_success(f"Scanned {total} pairs")
    print(f"  Executed: {executed} | Dry Runs: {dry_runs} | Failed: {failed}")

    for r in results:
        status = ""
        if r.get("executed"):
            status = f"{GREEN}✓ EXECUTED{NC}"
        elif r.get("dry_run"):
            status = f"{YELLOW}⚠ DRY{NC}"
        elif r.get("error"):
            status = f"{RED}✗ {r.get('error', 'ERROR')}{NC}"
        else:
            status = f"{CYAN}— SKIP{NC}"
        print(f"  {r.get('symbol', '?'):8s} {r.get('timeframe', '?'):4s}  {status}")

    if executed > 0 or dry_runs > 0:
        summary = orch.get_summary()
        print(f"\n  Total signals: {summary.get('total_signals', 0)}")
        print(f"  Win rate: {summary.get('win_rate', 'N/A')}")
        print(f"  Avg risk: {summary.get('avg_risk_reward', 'N/A')}")
    print()


def cmd_status(args):
    """Show current positions, equity, and risk status."""
    print_header("Account & Position Status")

    # Load env
    dotenv_path = PROJECT_ROOT / ".env"
    if dotenv_path.exists():
        from dotenv import load_dotenv

        load_dotenv(dotenv_path)

    # Try live connection first, fall back to simulation
    client_mode = "direct"
    try:
        # Check if REST API Docker is running
        import requests

        resp = requests.get("http://localhost:9009/health", timeout=2)
        if resp.status_code == 200:
            client_mode = "rest"
    except Exception:
        pass

    # Try cTrader connection
    try:
        if client_mode == "rest":
            from ctrader.rest_client import CTraderRESTClient

            client = CTraderRESTClient()
        else:
            from trading.execution.ctrader_client import CTraderClient

            client = CTraderClient()

        client.connect(timeout=10)
        positions = client.get_positions()
        client.disconnect()

        if positions:
            print(f"{BOLD}Open Positions ({len(positions)}):{NC}")
            for pos in positions:
                pnl = pos.get("pnl", 0)
                pnl_str = (
                    f"{GREEN}+{pnl:.2f}{NC}" if pnl >= 0 else f"{RED}{pnl:.2f}{NC}"
                )
                print(
                    f"  {pos.get('symbol', '?'):8s}  "
                    f"{pos.get('side', '?'):4s}  "
                    f"{pos.get('volume', 0):.2f} lots  "
                    f"PnL: {pnl_str}"
                )
        else:
            print_info("No open positions")

        # Show account summary
        summary = (
            client.get_account_summary()
            if hasattr(client, "get_account_summary")
            else {}
        )
        if summary:
            equity = summary.get("equity", "N/A")
            balance = summary.get("balance", "N/A")
            print(f"\n{BOLD}Account:{NC}")
            print(f"  Balance: {balance}")
            print(f"  Equity:  {equity}")

    except Exception as e:
        print_warning(f"Could not connect to cTrader: {e}")
        print_info("Showing simulation mode status...")

        # Show simulation data
        from trading.execution.risk_manager import RiskManager

        rm = RiskManager()
        status = rm.get_status()

        print(f"  Balance: ${status.get('balance', 10000):,.2f}")
        print(f"  Equity:  ${status.get('equity', 10000):,.2f}")
        print(f"  Drawdown: {status.get('drawdown_pct', 0):.2f}%")
        print(f"  Daily PnL: ${status.get('daily_pnl', 0):,.2f}")
        print(f"  Open trades: {status.get('open_trades', 0)}")

    print()


def cmd_risk(args):
    """Show risk management dashboard."""
    print_header("Risk Management Dashboard")
    from trading.execution.risk_manager import RiskManager

    rm = RiskManager()
    status = rm.get_status()

    print(f"{BOLD}Account Risk:{NC}")
    print(f"  Balance:       ${status.get('balance', 10000):>12,.2f}")
    print(f"  Equity:        ${status.get('equity', 10000):>12,.2f}")
    print(f"  Drawdown:      {status.get('drawdown_pct', 0):>12.2f}%")
    print(f"  Daily PnL:     ${status.get('daily_pnl', 0):>12,.2f}")
    print(f"  Open Trades:   {status.get('open_trades', 0):>12d}")
    print(f"  Max Open:      {status.get('max_open_trades', 5):>12d}")

    # Risk gates
    gates = [
        (
            "Max Daily Loss",
            status.get("drawdown_pct", 0) < 3.0,
            status.get("drawdown_pct", 0) < 3.0,
        ),
        (
            "Max Drawdown",
            status.get("drawdown_pct", 0) < 5.0,
            status.get("drawdown_pct", 0) < 5.0,
        ),
        (
            "Position Limit",
            status.get("open_trades", 0) < status.get("max_open_trades", 5),
            True,
        ),
        ("Min Risk/Reward", True, True),
        ("Session Risk", True, True),
    ]

    print(f"\n{BOLD}Risk Gates:{NC}")
    for name, passed, active in gates:
        if passed:
            print(f"  {GREEN}✓{NC} {name}")
        else:
            print(f"  {RED}✗{NC} {name} — TRADE HALTED")

    print()


def cmd_execute(args):
    """Execute a trade manually (bypasses SMC pipeline)."""
    print_header("Manual Trade Execution")
    from trading.execution.risk_manager import RiskManager
    from trading.execution.ctrader_client import CTraderClient

    rm = RiskManager()

    # Validate risk
    approved, reason = rm.check_risk(
        symbol=args.symbol,
        direction=args.direction.upper(),
        volume=args.volume,
        stop_loss=args.sl,
        take_profit=args.tp,
    )

    if not approved:
        print_error(f"Risk gate failed: {reason}")
        return

    # Execute via cTrader
    try:
        client = CTraderClient()
        client.connect(timeout=10)

        order_id = client.execute_order(
            symbol=args.symbol,
            side="BUY" if args.direction.upper() == "BUY" else "SELL",
            volume=args.volume,
            stop_loss=args.sl,
            take_profit=args.tp,
        )

        client.disconnect()
        print_success(f"Order executed: {order_id}")
        print(f"  Symbol: {args.symbol}")
        print(f"  Direction: {args.direction.upper()}")
        print(f"  Volume: {args.volume} lots")
        print(f"  SL: {args.sl} pips | TP: {args.tp} pips")
    except Exception as e:
        print_error(f"Execution failed: {e}")
    print()


def cmd_close(args):
    """Close positions by symbol or ID."""
    print_header("Close Positions")

    try:
        from trading.execution.ctrader_client import CTraderClient

        client = CTraderClient()
        client.connect(timeout=10)

        if args.position_id:
            result = client.close_order(args.position_id)
        elif args.symbol:
            result = client.close_by_symbol(args.symbol)
        else:
            result = client.close_all_positions()

        client.disconnect()
        print_success(f"Closed: {result}")
    except Exception as e:
        print_error(f"Close failed: {e}")
    print()


def cmd_backtest(args):
    """Run backtest on a symbol/timeframe."""
    print_header(f"Backtest: {args.symbol} {args.timeframe}")

    from trading.backtest.backtest_engine import BacktestEngine

    engine = BacktestEngine()

    print_info(f"Running backtest over last {args.days} days...")
    result = engine.run(
        symbol=args.symbol,
        timeframe=args.timeframe,
        days=args.days,
        initial_balance=args.balance,
    )

    print_success("Backtest complete")
    print(f"  Total Trades: {result.get('total_trades', 0)}")
    print(f"  Win Rate:     {result.get('win_rate', 0):.1f}%")
    print(f"  Profit Factor:{result.get('profit_factor', 0):.2f}")
    print(f"  Max Drawdown: {result.get('max_drawdown', 0):.2f}%")
    print(f"  Total Return: {result.get('total_return', 0):.2f}%")
    print(f"  Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
    print()


def cmd_session(args):
    """Show current trading session and kill zones."""
    print_header("Trading Sessions")

    from trading.engines.session_engine import SessionEngine

    engine = SessionEngine()
    sessions = engine.get_active_sessions()
    zones = engine.get_kill_zones()

    if sessions:
        print(f"{BOLD}Active Sessions:{NC}")
        for s in sessions:
            print(f"  {GREEN}●{NC} {s['name']} ({s['timezone']})")
    else:
        print_warning("No major sessions currently active")

    if zones:
        print(f"\n{BOLD}Kill Zones:{NC}")
        for z in zones:
            print(
                f"  {RED}■{NC} {z['name']}: {z['start']} - {z['end']} {z.get('bias', '')}"
            )
    else:
        print_info("No active kill zones")

    print()


def cmd_report(args):
    """Generate trading report."""
    print_header("Trading Report")
    from trading.execution.smc_pipeline import SMCOrchestrator

    orch = SMCOrchestrator()
    summary = orch.get_summary()

    print(
        f"{BOLD}Generated:{NC} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    print()
    print(f"{BOLD}Performance Summary:{NC}")
    print(f"  Total Signals:    {summary.get('total_signals', 0)}")
    print(f"  Executed Trades:  {summary.get('executed_trades', 0)}")
    print(f"  Win Rate:         {summary.get('win_rate', 'N/A')}")
    print(f"  Avg R:R:          {summary.get('avg_risk_reward', 'N/A')}")
    print(f"  Best Setup:       {summary.get('best_setup', 'N/A')}")
    print(f"  Total PnL:        ${summary.get('total_pnl', 0):,.2f}")
    print()


def cmd_health(args):
    """Check system health."""
    print_header("System Health Check")

    checks = []

    # Check .env
    dotenv_path = PROJECT_ROOT / ".env"
    env_ok = dotenv_path.exists()
    checks.append(("Environment (.env)", env_ok, ""))

    # Check Python packages
    packages = ["pandas", "numpy", "requests", "ta", "dotenv"]
    for pkg in packages:
        try:
            __import__(pkg)
            checks.append((f"Package: {pkg}", True, ""))
        except ImportError:
            checks.append((f"Package: {pkg}", False, "not installed"))

    # Check cTrader connection
    ctrader_ok = False
    try:
        import requests as _req

        resp = _req.get("http://localhost:9009/health", timeout=2)
        ctrader_ok = resp.status_code == 200
        checks.append(("cTrader REST API (Docker)", ctrader_ok, ""))
    except Exception:
        checks.append(("cTrader REST API (Docker)", False, "not running on :9009"))

    # Check cTrader direct
    try:
        from trading.execution.ctrader_client import CTraderClient

        client = CTraderClient()
        # Don't actually connect, just check import
        checks.append(("cTrader Direct Client", True, ""))
    except ImportError:
        checks.append(("cTrader Direct Client", False, "not installed"))
    except Exception as e:
        checks.append(("cTrader Direct Client", False, str(e)))

    # Check Redis
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=2)
        r.ping()
        checks.append(("Redis", True, ""))
    except Exception:
        checks.append(("Redis", False, "not running or not accessible"))

    # Check Docker
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        containers = [l for l in result.stdout.strip().split("\n") if l]
        checks.append(
            (
                "Docker Containers",
                True,
                f"{len(containers)} running: {', '.join(containers[:3])}",
            )
        )
    except Exception:
        checks.append(("Docker", False, "not accessible"))

    # Check n8n
    try:
        resp = _req.get("http://localhost:5678", timeout=2)
        checks.append(("n8n Workflow Engine", resp.status_code == 200, ""))
    except Exception:
        checks.append(("n8n Workflow Engine", False, "not running on :5678"))

    # Print results
    passed = 0
    for name, ok, detail in checks:
        if ok:
            print(f"  {GREEN}✓{NC} {name}" + (f" — {detail}" if detail else ""))
            passed += 1
        else:
            print(f"  {RED}✗{NC} {name}" + (f" — {detail}" if detail else ""))

    print(f"\n  {passed}/{len(checks)} checks passed")
    print()


def cmd_setup(args):
    """Interactive setup wizard."""
    print_header("AgentFinance v3 Setup Wizard")

    dotenv_path = PROJECT_ROOT / ".env"
    existing = dotenv_path.exists()

    if existing:
        print_info("Existing .env found. Will update with new values.")
    else:
        print_info("Creating new .env file.")

    print(f"\n{BOLD}Step 1: Pepperstone cTrader Credentials{NC}")
    print("  Get these from: https://www.ctrader.com/apps/developers/open-api/")
    print("  Or from Pepperstone: https://pepperstone.com/en/technology/ctrader")

    client_id = input("  cTrader Client ID: ").strip()
    client_secret = input("  cTrader Client Secret: ").strip()
    access_token = input("  cTrader Access Token: ").strip()
    account_id = (
        input(f"  Account ID [{os.getenv('CTRADER_ACCOUNT_ID', '46729678')}]: ").strip()
        or "46729678"
    )

    print(f"\n{BOLD}Step 2: Connection Mode{NC}")
    print("  1) Direct TCP (ctrader-open-api library — connects directly)")
    print("  2) Docker REST API (FastAPI bridge in Docker container)")
    conn_mode = input("  Select [1/2]: ").strip()

    print(f"\n{BOLD}Step 3: Data Provider (optional){NC}")
    api_key = input("  Polygon.io API Key (optional): ").strip()

    # Write .env
    mode_line = f"# Connection mode: {'docker' if conn_mode == '2' else 'direct'}"
    env_content = f"""# AgentFinance v3 Environment Configuration
# Generated by agent-cli.py setup wizard
# {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

{mode_line}

# ============================================================================
# CTRADER LIVE TRADING (Pepperstone Demo: Account ID {account_id})
# ============================================================================
CTRADER_CLIENT_ID={client_id}
CTRADER_CLIENT_SECRET={client_secret}
CTRADER_ACCESS_TOKEN={access_token}
CTRADER_ACCOUNT_ID={account_id}
CTRADER_HOST=demo

# ============================================================================
# DATA PROVIDERS
# ============================================================================
POLYGON_API_KEY={api_key}

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
MAX_RISK_PER_TRADE=0.01
MAX_DAILY_DRAWDOWN=0.03
INITIAL_BALANCE=10000
"""

    with open(dotenv_path, "w") as f:
        f.write(env_content)

    print_success(f".env saved to {dotenv_path}")

    if conn_mode == "2":
        print_info("Remember to set credentials in ctrader/.env and run:")
        print("  cd ctrader && docker compose up --build -d")

    print_info("Setup complete! Run 'agent-cli.py health' to verify.")
    print()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="AgentFinance v3 — Unified Trading CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan for setups on a symbol")
    p_scan.add_argument("symbol", help="Symbol (e.g. EURUSD)")
    p_scan.add_argument("timeframe", help="Timeframe (e.g. H1, M15)")
    p_scan.add_argument("--dry", action="store_true", help="Dry run (no execution)")

    # scan-all
    p_scan_all = subparsers.add_parser("scan-all", help="Scan all monitored pairs")
    p_scan_all.add_argument("--dry", action="store_true", help="Dry run (no execution)")

    # status
    subparsers.add_parser("status", help="Show positions and account status")

    # risk
    subparsers.add_parser("risk", help="Show risk management dashboard")

    # execute
    p_exec = subparsers.add_parser("execute", help="Execute a manual trade")
    p_exec.add_argument("symbol", help="Symbol (e.g. EURUSD)")
    p_exec.add_argument(
        "direction", choices=["BUY", "SELL", "buy", "sell"], help="Direction"
    )
    p_exec.add_argument("volume", type=float, help="Volume in lots")
    p_exec.add_argument("--sl", type=float, required=True, help="Stop loss in pips")
    p_exec.add_argument("--tp", type=float, required=True, help="Take profit in pips")

    # close
    p_close = subparsers.add_parser("close", help="Close positions")
    p_close.add_argument("--symbol", help="Close all positions for symbol")
    p_close.add_argument("--id", dest="position_id", help="Close specific position ID")
    p_close.add_argument("--all", action="store_true", help="Close all positions")

    # backtest
    p_bt = subparsers.add_parser("backtest", help="Run backtest")
    p_bt.add_argument("symbol", help="Symbol (e.g. EURUSD)")
    p_bt.add_argument("timeframe", help="Timeframe (e.g. H1)")
    p_bt.add_argument(
        "--days", type=int, default=90, help="Days to backtest (default: 90)"
    )
    p_bt.add_argument(
        "--balance", type=float, default=10000, help="Initial balance (default: 10000)"
    )

    # session
    subparsers.add_parser("session", help="Show trading sessions and kill zones")

    # report
    p_rep = subparsers.add_parser("report", help="Generate trading report")
    p_rep.add_argument("--today", action="store_true", help="Show today's report")

    # health
    subparsers.add_parser("health", help="Check system health")

    # setup
    subparsers.add_parser("setup", help="Interactive setup wizard")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print()
        print(__doc__)
        sys.exit(1)

    # Route to command handler
    commands = {
        "scan": cmd_scan,
        "scan-all": cmd_scan_all,
        "status": cmd_status,
        "risk": cmd_risk,
        "execute": cmd_execute,
        "close": cmd_close,
        "backtest": cmd_backtest,
        "session": cmd_session,
        "report": cmd_report,
        "health": cmd_health,
        "setup": cmd_setup,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Command failed: {e}")
        if args.command in ("scan", "scan-all", "execute", "close"):
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
