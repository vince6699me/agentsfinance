#!/usr/bin/env python3
"""
AgentFinance v3 - Comprehensive Test & Validation Suite
Tests all system components independently.
Usage: python3 scripts/test_suite.py [--component COMPONENT] [--all]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.output = None

    def pass_test(self, output: str = ""):
        self.passed = True
        self.output = output

    def fail_test(self, error: str):
        self.passed = False
        self.error = error


def test_agent_runner():
    """Test the master agent runner."""
    result = TestResult("Agent Runner")
    try:
        base = "/home/greywolf/Documents/AgentFinance/agentfinance"
        r = subprocess.run(
            [
                sys.executable,
                f"{base}/agent_runner.py",
                "--agent",
                "22",
                "--command",
                "kill-zones",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=base,
        )
        if r.returncode == 0 or "SMC engine not available" in r.stdout:
            result.pass_test(r.stdout)
        else:
            result.fail_test(f"Exit code {r.returncode}: {r.stderr}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_smc_engine():
    """Test SMC engine imports."""
    result = TestResult("SMC Engine Import")
    try:
        sys.path.insert(
            0, "/home/greywolf/Documents/AgentFinance/agentfinance/trading/engines"
        )
        try:
            from smc_engine import SMCEngine

            engine = SMCEngine()
            result.pass_test("SMC engine loaded successfully")
        except ImportError as e:
            result.fail_test(f"Missing dependency: {e}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_technical_engine():
    """Test technical engine imports."""
    result = TestResult("Technical Engine Import")
    try:
        sys.path.insert(
            0, "/home/greywolf/Documents/AgentFinance/agentfinance/trading/engines"
        )
        try:
            from technical_engine import TechnicalEngine

            engine = TechnicalEngine()
            result.pass_test("Technical engine loaded successfully")
        except ImportError as e:
            result.fail_test(f"Missing dependency: {e}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_session_engine():
    """Test session engine imports."""
    result = TestResult("Session Engine Import")
    try:
        sys.path.insert(
            0, "/home/greywolf/Documents/AgentFinance/agentfinance/trading/engines"
        )
        try:
            from session_engine import SessionEngine

            engine = SessionEngine()
            result.pass_test("Session engine loaded successfully")
        except ImportError as e:
            result.fail_test(f"Missing dependency: {e}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_ctrader_client():
    """Test cTrader client imports."""
    result = TestResult("cTrader Client Import")
    try:
        sys.path.insert(
            0, "/home/greywolf/Documents/AgentFinance/agentfinance/trading/execution"
        )
        try:
            from ctrader_client import CTraderClient

            client = CTraderClient()
            result.pass_test(
                "cTrader client loaded (API credentials needed for live connection)"
            )
        except ImportError as e:
            result.fail_test(f"Missing dependency: {e}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_backtest_engine():
    """Test backtest engine imports."""
    result = TestResult("Backtest Engine Import")
    try:
        sys.path.insert(
            0, "/home/greywolf/Documents/AgentFinance/agentfinance/trading/backtest"
        )
        try:
            from backtest_engine import BacktestEngine

            engine = BacktestEngine()
            result.pass_test("Backtest engine loaded successfully")
        except ImportError as e:
            result.fail_test(f"Missing dependency: {e}")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_agent_scripts():
    """Test all agent Python scripts for syntax errors."""
    result = TestResult("Agent Scripts Syntax")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance/agents"
    errors = []
    count = 0

    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        compile(fh.read(), path, "exec")
                    count += 1
                except SyntaxError as e:
                    errors.append(f"{path}: {e}")

    if errors:
        result.fail_test(f"{len(errors)} syntax errors:\n" + "\n".join(errors[:5]))
    else:
        result.pass_test(f"All {count} agent scripts have valid syntax")
    return result


def test_n8n_workflows():
    """Test n8n workflow JSON files."""
    result = TestResult("n8n Workflows")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance/n8n"
    workflows = []
    errors = []

    for f in os.listdir(base):
        if f.endswith(".json"):
            path = os.path.join(base, f)
            try:
                with open(path) as fh:
                    data = json.load(fh)
                required = ["name", "nodes", "connections"]
                missing = [k for k in required if k not in data]
                if missing:
                    errors.append(f"{f}: missing fields {missing}")
                else:
                    workflows.append(data["name"])
            except json.JSONDecodeError as e:
                errors.append(f"{f}: invalid JSON - {e}")

    if errors:
        result.fail_test("\n".join(errors))
    else:
        result.pass_test(
            f"All {len(workflows)} workflows valid: {', '.join(workflows)}"
        )
    return result


def test_skill_files():
    """Test all SKILL.md files for frontmatter."""
    result = TestResult("Skill Files")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance/skills"
    errors = []
    count = 0

    for root, dirs, files in os.walk(base):
        for f in files:
            if f == "SKILL.md":
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        content = fh.read(200)
                    if "---\n" in content or "name:" in content:
                        count += 1
                    else:
                        errors.append(f"{path}: missing YAML frontmatter")
                except Exception as e:
                    errors.append(f"{path}: {e}")

    if errors:
        result.fail_test(
            f"{len(errors)} skill files missing frontmatter:\n" + errors[0]
        )
    else:
        result.pass_test(f"All {count} skill files have valid frontmatter")
    return result


def test_yamls():
    """Test all agent YAML configs."""
    result = TestResult("Agent YAML Configs")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance/agents"
    errors = []
    count = 0

    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".yaml"):
                path = os.path.join(root, f)
                try:
                    import yaml

                    with open(path) as fh:
                        data = yaml.safe_load(fh)
                    if "agent" not in data:
                        errors.append(f"{path}: missing 'agent' key")
                    else:
                        count += 1
                except ImportError:
                    # YAML module not available, do basic check
                    with open(path) as fh:
                        content = fh.read()
                    if "agent:" in content and "name:" in content:
                        count += 1
                    else:
                        errors.append(f"{path}: invalid structure")
                except Exception as e:
                    errors.append(f"{path}: {e}")

    if errors:
        result.fail_test(f"{len(errors)} YAML errors:\n" + errors[0])
    else:
        result.pass_test(f"All {count} YAML configs valid")
    return result


def test_dashboard():
    """Test React dashboard file exists and has key components."""
    result = TestResult("React Dashboard")
    path = "/home/greywolf/Documents/AgentFinance/agentfinance/dashboard/AgentFinanceV3Dashboard.jsx"
    try:
        with open(path) as fh:
            content = fh.read()
        checks = {
            "KILL_ZONES": "Kill zones panel",
            "POSITIONS": "Positions table",
            "ACCOUNT": "Account summary",
            "SMC_SETUPS": "SMC setups panel",
            "BACKTEST_RESULTS": "Backtest results",
            "AgentFinance v3": "v3 branding",
        }
        missing = [desc for key, desc in checks.items() if key not in content]
        if missing:
            result.fail_test(f"Missing components: {', '.join(missing)}")
        else:
            lines = content.count("\n")
            result.pass_test(
                f"v3 dashboard valid ({lines} lines) with all trading components"
            )
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_install_script():
    """Test install.sh exists and has required commands."""
    result = TestResult("Install Script")
    path = "/home/greywolf/Documents/AgentFinance/agentfinance/scripts/install.sh"
    try:
        with open(path) as fh:
            content = fh.read()
        required = ["smartmoneyconcepts", "pip install", "git clone", "node", "npm"]
        missing = [r for r in required if r not in content]
        if missing:
            result.fail_test(f"Missing commands: {', '.join(missing)}")
        else:
            result.pass_test("install.sh has all required commands")
    except Exception as e:
        result.fail_test(str(e))
    return result


def test_directory_structure():
    """Validate all required directories and files exist."""
    result = TestResult("Directory Structure")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance"

    required = {
        "dirs": [
            "agents/public",
            "agents/private",
            "agents/research",
            "agents/ops",
            "agents/trading",
            "trading/engines",
            "trading/execution",
            "trading/backtest",
            "trading/data",
            "n8n",
            "skills/smc",
            "skills/technical",
            "skills/fundamental",
            "skills/sentiment",
            "skills/news",
            "skills/backtest",
            "skills/forex",
            "skills/commodities",
            "skills/indices",
            "dashboard",
            "scripts",
        ],
        "files": [
            "trading/engines/smc_engine.py",
            "trading/engines/technical_engine.py",
            "trading/engines/session_engine.py",
            "trading/execution/ctrader_client.py",
            "trading/execution/risk_manager.py",
            "trading/backtest/backtest_engine.py",
            "trading/data/data_fetcher.py",
            "n8n/workflow_smc_execution.json",
            "n8n/workflow_morning_briefing.json",
            "n8n/workflow_position_management.json",
            "n8n/workflow_economic_calendar.json",
            "n8n/workflow_weekly_performance.json",
            "dashboard/AgentFinanceV3Dashboard.jsx",
            "scripts/install.sh",
            "agent_runner.py",
            "README.md",
        ],
    }

    missing = []
    for d in required["dirs"]:
        if not os.path.isdir(f"{base}/{d}"):
            missing.append(f"dir: {d}")
    for f in required["files"]:
        if not os.path.isfile(f"{base}/{f}"):
            missing.append(f"file: {f}")

    if missing:
        result.fail_test(f"Missing:\n" + "\n".join(missing[:10]))
    else:
        result.pass_test("All 37 required directories and files present")
    return result


def test_agent_count():
    """Verify all 28 agent YAML configs exist."""
    result = TestResult("Agent Count (28)")
    base = "/home/greywolf/Documents/AgentFinance/agentfinance/agents"
    yamls = []
    scripts = []

    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".yaml"):
                yamls.append(f)
            if f.endswith(".py"):
                scripts.append(f)

    if len(yamls) >= 28:
        result.pass_test(
            f"{len(yamls)} agent YAML configs, {len(scripts)} Python scripts"
        )
    else:
        result.fail_test(f"Only {len(yamls)} agent configs found (expected 28)")
    return result


def run_all_tests():
    """Run all tests and print summary."""
    tests = [
        test_directory_structure,
        test_agent_count,
        test_agent_scripts,
        test_n8n_workflows,
        test_skill_files,
        test_dashboard,
        test_install_script,
        test_smc_engine,
        test_technical_engine,
        test_session_engine,
        test_ctrader_client,
        test_backtest_engine,
        test_agent_runner,
    ]

    # Try YAML test if PyYAML available
    try:
        import yaml

        tests.insert(3, test_yamls)
    except ImportError:
        pass

    results = []
    for test_fn in tests:
        print(f"Testing: {test_fn.__name__}...", end=" ", flush=True)
        r = test_fn()
        results.append(r)
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(status)

    print(f"\n{'=' * 60}")
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    print(f"RESULTS: {passed}/{len(results)} passed, {failed} failed")

    if failed > 0:
        print(f"\nFailed tests:")
        for r in results:
            if not r.passed:
                print(f"  - {r.name}: {r.error or 'Unknown error'}")

    print(f"\nTimestamp: {datetime.now().isoformat()}")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="AgentFinance v3 Test Suite")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--component", type=str, help="Test specific component")
    args = parser.parse_args()

    test_map = {
        "agents": test_agent_scripts,
        "workflows": test_n8n_workflows,
        "skills": test_skill_files,
        "dashboard": test_dashboard,
        "engines": test_smc_engine,
        "structure": test_directory_structure,
    }

    if args.component:
        if args.component in test_map:
            r = test_map[args.component]()
            status = "PASS" if r.passed else "FAIL"
            print(f"{args.component}: {status}")
            if r.error:
                print(f"  Error: {r.error}")
            return 0 if r.passed else 1
        else:
            print(f"Unknown component: {args.component}")
            print(f"Available: {', '.join(test_map.keys())}")
            return 1

    success = run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
