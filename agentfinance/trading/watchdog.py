#!/usr/bin/env python3
"""
AgentFinance v3 - Trading Watchdog
=================================
Dead man's switch and process monitor.

Monitors:
- Agent heartbeats (PID file + timestamp)
- Daily routine execution
- Emergency stop triggers
- System health checks

If the watchdog detects a frozen or dead agent system, it:
1. Logs the issue
2. Attempts graceful recovery
3. Triggers emergency close if all agents are dead

Setup as a systemd service for production reliability.
"""

import os
import sys
import json
import time
import signal
import logging
import socket
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

WATCHDOG_DIR = os.path.join(os.path.dirname(__file__), "../../../.watchdog")
PID_DIR = os.path.join(WATCHDOG_DIR, "pids")
HEARTBEAT_FILE = os.path.join(WATCHDOG_DIR, "heartbeat.json")
LOCK_FILE = os.path.join(WATCHDOG_DIR, "watchdog.lock")
CONFIG_FILE = os.path.join(WATCHDOG_DIR, "config.json")

DEFAULT_CONFIG = {
    "heartbeat_timeout_seconds": 300,  # 5 min — if no heartbeat, alert
    "critical_timeout_seconds": 600,  # 10 min — if no heartbeat, kill
    "check_interval_seconds": 60,  # Check every 60 seconds
    "max_restart_attempts": 3,  # Max restarts before giving up
    "restart_cooldown_seconds": 120,  # Wait between restart attempts
    "emergency_close_on_critical": True,  # Close positions if critical timeout
    "notify_webhook": "",  # Webhook URL for alerts
    "agents_to_monitor": [
        "agent_cli",
        "daily_routine",
        "agent_runner",
    ],
    "shutdown_hours": [0, 22],  # UTC hours when system should be shut down
}

logger = logging.getLogger("watchdog")


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────


class AgentStatus(Enum):
    ALIVE = "ALIVE"
    STALE = "STALE"  # Heartbeat late but not critical
    DEAD = "DEAD"  # Heartbeat missed (critical)
    UNKNOWN = "UNKNOWN"  # Never seen


class Action(Enum):
    NONE = "none"
    ALERT = "alert"
    RESTART = "restart"
    KILL = "kill"
    EMERGENCY_CLOSE = "emergency_close"


# ─────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────


@dataclass
class AgentHealth:
    """Health record for a monitored agent."""

    name: str
    pid: Optional[int]
    last_heartbeat: Optional[datetime]
    status: AgentStatus
    restart_count: int = 0
    last_restart: Optional[datetime] = None


@dataclass
class WatchdogDecision:
    """Decision made by the watchdog."""

    agent: str
    action: Action
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


# ─────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                os.path.join(WATCHDOG_DIR, "watchdog.log"),
                mode="a",
            ),
        ],
    )


def ensure_dirs():
    """Ensure watchdog directories exist."""
    os.makedirs(WATCHDOG_DIR, exist_ok=True)
    os.makedirs(PID_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# Config Manager
# ─────────────────────────────────────────────


def load_config() -> Dict:
    """Load watchdog configuration."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            saved = json.load(f)
            return {**DEFAULT_CONFIG, **saved}
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict):
    """Save watchdog configuration."""
    ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ─────────────────────────────────────────────
# PID Management
# ─────────────────────────────────────────────


def write_pid(name: str, pid: int):
    """Write agent PID to file."""
    ensure_dirs()
    pid_file = os.path.join(PID_DIR, f"{name}.pid")
    with open(pid_file, "w") as f:
        f.write(
            json.dumps(
                {
                    "name": name,
                    "pid": pid,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        )


def read_pid(name: str) -> Optional[Dict]:
    """Read agent PID file."""
    pid_file = os.path.join(PID_DIR, f"{name}.pid")
    if not os.path.exists(pid_file):
        return None
    try:
        with open(pid_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def is_process_alive(pid: int) -> bool:
    """Check if a process is still running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def remove_pid(name: str):
    """Remove agent PID file."""
    pid_file = os.path.join(PID_DIR, f"{name}.pid")
    if os.path.exists(pid_file):
        os.unlink(pid_file)


# ─────────────────────────────────────────────
# Heartbeat Management
# ─────────────────────────────────────────────


def write_heartbeat(agent_name: str, metadata: Optional[Dict] = None):
    """
    Write a heartbeat for an agent.
    Called by agents to signal they are alive.

    Usage in agents:
        from trading.watchdog import write_heartbeat
        write_heartbeat("agent_cli", {"phase": "scanning", "pairs": 5})
    """
    ensure_dirs()
    heartbeat = {
        "agent": agent_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }
    if metadata:
        heartbeat["metadata"] = metadata

    with open(HEARTBEAT_FILE, "w") as f:
        json.dump(heartbeat, f)

    # Also update per-agent heartbeat
    agent_beat_file = os.path.join(WATCHDOG_DIR, f"heartbeat_{agent_name}.json")
    with open(agent_beat_file, "w") as f:
        json.dump(heartbeat, f)


def read_heartbeats() -> Dict[str, Dict]:
    """Read all agent heartbeats."""
    heartbeats = {}
    wd = Path(WATCHDOG_DIR)
    for beat_file in wd.glob("heartbeat_*.json"):
        try:
            with open(beat_file) as f:
                data = json.load(f)
                name = beat_file.stem.replace("heartbeat_", "")
                heartbeats[name] = data
        except (json.JSONDecodeError, OSError):
            continue
    return heartbeats


# ─────────────────────────────────────────────
# Health Assessment
# ─────────────────────────────────────────────


def assess_agent_health(
    name: str,
    config: Dict,
    heartbeat: Optional[Dict] = None,
    pid_info: Optional[Dict] = None,
) -> AgentHealth:
    """Assess the health of a single agent."""
    now = datetime.now(timezone.utc)
    pid = pid_info.get("pid") if pid_info else None

    if heartbeat is None:
        return AgentHealth(
            name=name,
            pid=pid,
            last_heartbeat=None,
            status=AgentStatus.UNKNOWN,
        )

    last_ts = datetime.fromisoformat(heartbeat["timestamp"].replace("Z", "+00:00"))
    age_seconds = (now - last_ts).total_seconds()

    if age_seconds > config["critical_timeout_seconds"]:
        status = AgentStatus.DEAD
    elif age_seconds > config["heartbeat_timeout_seconds"]:
        status = AgentStatus.STALE
    else:
        status = AgentStatus.ALIVE

    # Check if process is still running
    if pid and not is_process_alive(pid):
        status = AgentStatus.DEAD

    return AgentHealth(
        name=name,
        pid=pid,
        last_heartbeat=last_ts,
        status=status,
    )


# ─────────────────────────────────────────────
# Decision Engine
# ─────────────────────────────────────────────


def make_decisions(
    agents: List[AgentHealth],
    config: Dict,
) -> List[WatchdogDecision]:
    """Decide what action to take for each agent."""
    decisions = []

    for agent in agents:
        if agent.status == AgentStatus.DEAD:
            if agent.restart_count < config["max_restart_attempts"]:
                decisions.append(
                    WatchdogDecision(
                        agent=agent.name,
                        action=Action.RESTART,
                        reason=f"Agent dead (heartbeat age: {agent.last_heartbeat})",
                    )
                )
            else:
                decisions.append(
                    WatchdogDecision(
                        agent=agent.name,
                        action=Action.EMERGENCY_CLOSE,
                        reason=f"Max restarts exceeded ({agent.restart_count})",
                    )
                )
        elif agent.status == AgentStatus.STALE:
            decisions.append(
                WatchdogDecision(
                    agent=agent.name,
                    action=Action.ALERT,
                    reason=f"Agent heartbeat stale",
                )
            )
        else:
            decisions.append(
                WatchdogDecision(
                    agent=agent.name,
                    action=Action.NONE,
                    reason="Agent healthy",
                )
            )

    # If ALL agents are dead, trigger emergency close
    all_dead = all(a.status == AgentStatus.DEAD for a in agents)
    if all_dead and config["emergency_close_on_critical"]:
        decisions.append(
            WatchdogDecision(
                agent="__system__",
                action=Action.EMERGENCY_CLOSE,
                reason="All agents are dead — emergency close triggered",
            )
        )

    return decisions


# ─────────────────────────────────────────────
# Action Execution
# ─────────────────────────────────────────────


def execute_decision(
    decision: WatchdogDecision,
    agent_health: Dict[str, AgentHealth],
) -> bool:
    """Execute a watchdog decision. Returns True if action was taken."""
    agent_name = decision.agent

    if decision.action == Action.NONE:
        return False

    if decision.action == Action.ALERT:
        logger.warning(f"ALERT: {agent_name} — {decision.reason}")
        return True

    if decision.action == Action.RESTART:
        health = agent_health.get(agent_name)
        if health:
            health.restart_count += 1
            health.last_restart = datetime.now(timezone.utc)
        logger.warning(f"RESTART: {agent_name} — {decision.reason}")
        # Attempt restart via supervisor or systemd
        _attempt_restart(agent_name)
        return True

    if decision.action == Action.EMERGENCY_CLOSE:
        logger.critical(f"EMERGENCY CLOSE: {decision.reason}")
        _trigger_emergency_close()
        return True

    return False


def _attempt_restart(agent_name: str):
    """Attempt to restart an agent via systemd."""
    service_name = f"agentfinance-{agent_name}.service"
    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            logger.info(f"Restarted {agent_name} via systemd")
        else:
            logger.error(f"Failed to restart {agent_name}: {result.stderr.decode()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"Cannot restart {agent_name}: systemd not available")
        # Fallback: try to start the script directly
        _start_agent_direct(agent_name)


def _start_agent_direct(agent_name: str):
    """Fallback: start agent script directly."""
    agent_dir = Path(__file__).parent.parent.parent
    scripts_dir = agent_dir / "scripts"
    script_map = {
        "agent_cli": scripts_dir / "agent_cli.py",
        "daily_routine": scripts_dir / "daily_routine.py",
        "agent_runner": scripts_dir / "agent_runner.py",
    }

    script = script_map.get(agent_name)
    if script and script.exists():
        try:
            subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(agent_dir),
                stdout=open(os.devnull, "w"),
                stderr=open(os.devnull, "w"),
            )
            logger.info(f"Started {agent_name} directly")
        except Exception as e:
            logger.error(f"Failed to start {agent_name}: {e}")


def _trigger_emergency_close():
    """Trigger emergency close via the trading executor."""
    # Try to trigger emergency close via REST API or direct execution
    try:
        import requests

        # Attempt graceful close via the cTrader API
        resp = requests.post(
            "http://localhost:9009/orders/close-all",
            headers={"X-API-Key": os.getenv("REST_API_KEY", "")},
            timeout=10,
        )
        logger.info(f"Emergency close API response: {resp.status_code}")
    except Exception as e:
        logger.error(f"Emergency close failed: {e}")
        # Last resort: write flag file for other processes
        flag_file = os.path.join(WATCHDOG_DIR, "EMERGENCY_CLOSE")
        with open(flag_file, "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())
        logger.critical(f"Emergency close flag written to {flag_file}")


# ─────────────────────────────────────────────
# Nightly Shutdown Check
# ─────────────────────────────────────────────


def should_shutdown(config: Dict) -> bool:
    """Check if system should be shut down based on time."""
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour
    shutdown_hours = config.get("shutdown_hours", [0, 22])

    if shutdown_hours[0] <= current_hour or current_hour >= shutdown_hours[1]:
        # Weekend check (UTC: Saturday = 5, Sunday = 6)
        if now_utc.weekday() >= 5:
            return True
        # Weekday shutdown
        return True

    return False


# ─────────────────────────────────────────────
# Main Watchdog Loop
# ─────────────────────────────────────────────


class Watchdog:
    """Main watchdog monitor."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or load_config()
        self.running = False
        self.agent_health: Dict[str, AgentHealth] = {}
        self.action_log: List[WatchdogDecision] = []
        ensure_dirs()

    def check_once(self) -> List[WatchdogDecision]:
        """Run one watchdog check cycle."""
        agents = []
        heartbeats = read_heartbeats()

        for agent_name in self.config["agents_to_monitor"]:
            pid_info = read_pid(agent_name)
            heartbeat = heartbeats.get(agent_name)
            health = assess_agent_health(agent_name, self.config, heartbeat, pid_info)
            agents.append(health)
            self.agent_health[agent_name] = health

        decisions = make_decisions(agents, self.config)
        actions_taken = 0

        for decision in decisions:
            if execute_decision(decision, self.agent_health):
                actions_taken += 1
            self.action_log.append(decision)

        logger.info(
            f"Check complete: {len(agents)} agents, "
            f"{sum(1 for a in agents if a.status == AgentStatus.ALIVE)} alive, "
            f"{sum(1 for a in agents if a.status == AgentStatus.DEAD)} dead, "
            f"{actions_taken} actions taken"
        )

        return decisions

    def run(self):
        """Run the watchdog loop."""
        self.running = True

        # Write our own PID
        write_pid("watchdog", os.getpid())

        logger.info(
            f"Watchdog started — checking every "
            f"{self.config['check_interval_seconds']}s"
        )

        while self.running:
            try:
                # Check shutdown time
                if should_shutdown(self.config):
                    logger.info("Shutdown time reached — stopping watchdog")
                    self.shutdown()
                    break

                # Run health check
                self.check_once()

                # Sleep until next check
                time.sleep(self.config["check_interval_seconds"])

            except KeyboardInterrupt:
                logger.info("Watchdog interrupted — shutting down")
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(30)

    def shutdown(self):
        """Graceful shutdown."""
        self.running = False
        remove_pid("watchdog")
        logger.info("Watchdog stopped")

    def status(self) -> Dict:
        """Get current watchdog status."""
        return {
            "running": self.running,
            "config": self.config,
            "agents": {
                name: {
                    "status": h.status.value,
                    "pid": h.pid,
                    "last_heartbeat": (
                        h.last_heartbeat.isoformat() if h.last_heartbeat else None
                    ),
                    "restart_count": h.restart_count,
                }
                for name, h in self.agent_health.items()
            },
            "recent_actions": [
                {
                    "agent": d.agent,
                    "action": d.action.value,
                    "reason": d.reason,
                    "timestamp": d.timestamp.isoformat(),
                }
                for d in self.action_log[-10:]
            ],
        }


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AgentFinance Watchdog")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--check", action="store_true", help="Run single check")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument(
        "--heartbeat", metavar="AGENT", help="Send heartbeat for agent (for testing)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    setup_logging(args.verbose)
    ensure_dirs()

    if args.heartbeat:
        write_heartbeat(args.heartbeat, {"source": "cli_test"})
        print(f"Heartbeat sent for: {args.heartbeat}")
        return

    if args.status:
        wd = Watchdog()
        import json

        print(json.dumps(wd.status(), indent=2))
        return

    if args.check:
        wd = Watchdog()
        decisions = wd.check_once()
        for d in decisions:
            print(f"[{d.action.value:20}] {d.agent}: {d.reason}")
        return

    # Run watchdog loop
    wd = Watchdog()
    wd.run()


if __name__ == "__main__":
    main()
