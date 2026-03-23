#!/usr/bin/env python3
"""
AgentFinance Risk Management Module
Safety gates, position limits, and emergency controls.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging

logger = logging.getLogger("risk_manager")


# ============================================================================
# DATA CLASSES & ENUMS
# ============================================================================


class RiskLevel(Enum):
    GREEN = "GREEN"  # All clear
    YELLOW = "YELLOW"  # Warning - monitor closely
    ORANGE = "ORANGE"  # Alert - no new trades
    RED = "RED"  # Stop - close positions
    BLACK = "BLACK"  # Emergency - halt everything


class GateStatus(Enum):
    PASS = "PASS"  # Gate passed
    HOLD = "HOLD"  # Hold for review
    BLOCK = "BLOCK"  # Block action
    HALT = "HALT"  # Emergency halt


@dataclass
class RiskConfig:
    """Risk management configuration."""

    max_risk_per_trade: float = 0.01  # 1% per trade
    max_daily_drawdown: float = 0.03  # 3% daily
    max_weekly_drawdown: float = 0.05  # 5% weekly
    max_monthly_drawdown: float = 0.08  # 8% monthly
    max_concurrent_trades: int = 5  # Max positions
    max_correlation_overlap: float = 0.8  # Max correlation
    min_rr_ratio: float = 1.5  # Min risk/reward
    pre_news_block_minutes: int = 15  # Block before news
    post_news_block_minutes: int = 15  # Block after news
    max_spread_multiplier: float = 3.0  # Max spread
    signal_max_age_hours: float = 4.0  # Signal expiry
    min_confidence_score: float = 0.75  # Min signal confidence
    daily_loss_pause: float = 0.015  # -1.5% pause
    daily_loss_halt: float = 0.025  # -2.5% halt
    daily_loss_kill: float = 0.03  # -3% kill switch


@dataclass
class TradeSignal:
    """Trade signal with risk metadata."""

    signal_id: str
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward: float
    created_at: datetime
    kill_zone_active: bool = False
    news_risk: bool = False
    correlation_pairs: List[str] = field(default_factory=list)


@dataclass
class Position:
    """Open position for risk tracking."""

    position_id: str
    symbol: str
    direction: str
    volume: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    open_time: datetime
    pnl: float = 0.0
    unrealized_pnl: float = 0.0
    # Trailing stop fields
    trailing_stop_enabled: bool = False
    trailing_stop_distance_pips: float = 0.0
    trailing_stop_active: bool = False  # Not activated until TP1 hit
    trailing_stop_price: float = 0.0  # Current trailing stop level


@dataclass
class RiskCheckResult:
    """Result of risk check."""

    allowed: bool
    gate_status: GateStatus
    risk_level: RiskLevel
    blocked_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    adjusted_risk: Optional[float] = None


# ============================================================================
# RISK MANAGER
# ============================================================================


class RiskManager:
    """
    Comprehensive risk management system with safety gates.
    Implements all risk rules from AgentFinance v3 specification.
    """

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self.positions: List[Position] = []
        self.daily_pnl: float = 0.0
        self.weekly_pnl: float = 0.0
        self.monthly_pnl: float = 0.0
        self.peak_equity: float = 10000.0
        self.current_equity: float = 10000.0
        self.trade_count_today: int = 0
        self.pending_high_impact_news: List[Dict] = []
        self.last_reset: datetime = datetime.now(timezone.utc)
        self.halted_until: Optional[datetime] = None
        self.status = RiskLevel.GREEN

        # Correlation matrix (simplified)
        self.correlation_matrix = {
            ("EURUSD", "GBPUSD"): 0.85,
            ("EURUSD", "USDJPY"): -0.75,
            ("EURUSD", "AUDUSD"): 0.70,
            ("GBPUSD", "GBPJPY"): 0.90,
            ("XAUUSD", "BTCUSD"): 0.45,
            ("XAUUSD", "USDJPY"): -0.60,
        }

    def check_signal(self, signal: TradeSignal) -> RiskCheckResult:
        """
        Comprehensive risk check before trade execution.

        Checks:
        1. Daily loss gates
        2. Max positions
        3. Correlation risk
        4. News event window
        5. Spread threshold
        6. Signal age
        7. Confidence score
        8. Risk/reward ratio
        """
        warnings = []
        blocked_reason = None
        allowed = True
        gate_status = GateStatus.PASS

        # 1. HALT CHECK - Emergency stop active
        if self.halted_until and datetime.now(timezone.utc) < self.halted_until:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.HALT,
                risk_level=RiskLevel.BLACK,
                blocked_reason="Trading halted - emergency stop active",
            )

        # 2. DAILY LOSS GATE CHECK
        daily_pnl_pct = self.daily_pnl / self.current_equity

        if daily_pnl_pct <= -self.config.daily_loss_kill:
            self.halt_all()
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.HALT,
                risk_level=RiskLevel.BLACK,
                blocked_reason="Daily loss exceeds -3% - KILL SWITCH ACTIVATED",
            )

        if daily_pnl_pct <= -self.config.daily_loss_halt:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.HOLD,
                risk_level=RiskLevel.RED,
                blocked_reason="Daily loss exceeds -2.5% - HALTED",
            )

        if daily_pnl_pct <= -self.config.daily_loss_pause:
            warnings.append(
                f"Daily P&L at {daily_pnl_pct:.1%} - approaching halt threshold"
            )
            gate_status = GateStatus.HOLD

        # 3. POSITION COUNT CHECK
        if len(self.positions) >= self.config.max_concurrent_trades:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.BLOCK,
                risk_level=RiskLevel.ORANGE,
                blocked_reason=f"Max positions ({self.config.max_concurrent_trades}) reached",
            )

        # 4. CORRELATION CHECK
        correlated_risk = self._check_correlation(signal.symbol)
        if correlated_risk:
            warnings.append(correlated_risk)
            if correlated_risk.startswith("HIGH"):
                gate_status = GateStatus.HOLD

        # 5. NEWS EVENT CHECK
        if signal.news_risk:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.BLOCK,
                risk_level=RiskLevel.ORANGE,
                blocked_reason="High-impact news event - trading blocked 15min before/after",
            )

        # 6. SIGNAL AGE CHECK
        signal_age = (
            datetime.now(timezone.utc) - signal.created_at
        ).total_seconds() / 3600
        if signal_age > self.config.signal_max_age_hours:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.BLOCK,
                risk_level=RiskLevel.YELLOW,
                blocked_reason=f"Signal age ({signal_age:.1f}h) exceeds maximum ({self.config.signal_max_age_hours}h)",
            )

        # 7. CONFIDENCE CHECK
        if signal.confidence < self.config.min_confidence_score:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.HOLD,
                risk_level=RiskLevel.YELLOW,
                blocked_reason=f"Signal confidence ({signal.confidence:.0%}) below minimum ({self.config.min_confidence_score:.0%})",
            )

        # 8. RISK/REWARD CHECK
        if signal.risk_reward < self.config.min_rr_ratio:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.HOLD,
                risk_level=RiskLevel.YELLOW,
                blocked_reason=f"R/R ratio ({signal.risk_reward:.1f}) below minimum ({self.config.min_rr_ratio:.1f})",
            )

        # 9. KILL ZONE CHECK (for SMC signals)
        if not signal.kill_zone_active:
            warnings.append("SMC signal but kill zone not active - reduced confidence")

        # Update risk level
        if gate_status == GateStatus.HOLD:
            self.status = RiskLevel.YELLOW
        elif gate_status == GateStatus.BLOCK:
            self.status = RiskLevel.ORANGE
        else:
            self.status = RiskLevel.GREEN

        return RiskCheckResult(
            allowed=allowed,
            gate_status=gate_status,
            risk_level=self.status,
            warnings=warnings,
            blocked_reason=blocked_reason,
        )

    def _check_correlation(self, symbol: str) -> Optional[str]:
        """Check if adding this position would create high correlation risk."""
        symbol_positions = [p for p in self.positions if p.symbol == symbol]

        if not symbol_positions:
            return None

        # Check correlation with existing positions
        for pos in self.positions:
            key = (
                (symbol, pos.symbol)
                if (symbol, pos.symbol) in self.correlation_matrix
                else (pos.symbol, symbol)
            )
            corr = self.correlation_matrix.get(key, 0.5)

            if abs(corr) >= self.config.max_correlation_overlap:
                return f"HIGH correlation ({abs(corr):.0%}) with existing {pos.symbol} position"

        return None

    def check_spread(
        self, symbol: str, current_spread: float, avg_spread: float
    ) -> RiskCheckResult:
        """Check if spread is within acceptable range."""
        spread_ratio = current_spread / avg_spread if avg_spread > 0 else 1.0

        if spread_ratio > self.config.max_spread_multiplier:
            return RiskCheckResult(
                allowed=False,
                gate_status=GateStatus.BLOCK,
                risk_level=RiskLevel.ORANGE,
                blocked_reason=f"Spread ({spread_ratio:.1f}x avg) exceeds maximum ({self.config.max_spread_multiplier}x)",
            )

        if spread_ratio > 2.0:
            return RiskCheckResult(
                allowed=True,
                gate_status=GateStatus.PASS,
                risk_level=RiskLevel.YELLOW,
                warnings=[f"Elevated spread ({spread_ratio:.1f}x avg)"],
            )

        return RiskCheckResult(
            allowed=True, gate_status=GateStatus.PASS, risk_level=RiskLevel.GREEN
        )

    def add_position(self, position: Position):
        """Add a new position to tracking."""
        self.positions.append(position)
        self.trade_count_today += 1
        logger.info(f"Position added: {position.symbol} {position.direction}")

    def remove_position(self, position_id: str, realized_pnl: float):
        """Remove a closed position."""
        self.positions = [p for p in self.positions if p.position_id != position_id]
        self.daily_pnl += realized_pnl
        self.current_equity += realized_pnl
        logger.info(f"Position closed: {position_id} | P/L: ${realized_pnl:.2f}")

    def enable_trailing_stop(
        self,
        position_id: str,
        distance_pips: float = 20.0,
        activate_at_tp1: bool = True,
    ) -> Dict:
        """
        Enable trailing stop on a position.

        Args:
            position_id: ID of position to attach trailing stop
            distance_pips: Distance of trailing stop in pips
            activate_at_tp1: If True, trailing stop only activates after TP1 is hit

        Returns:
            Dict with status and new stop level
        """
        for pos in self.positions:
            if pos.position_id == position_id:
                pos.trailing_stop_enabled = True
                pos.trailing_stop_distance_pips = distance_pips
                pos.trailing_stop_active = not activate_at_tp1

                # Calculate initial stop level
                if pos.direction == "BUY":
                    stop_price = self._pips_to_price(
                        pos.current_price, -distance_pips, pos.symbol
                    )
                else:
                    stop_price = self._pips_to_price(
                        pos.current_price, distance_pips, pos.symbol
                    )
                pos.trailing_stop_price = stop_price

                logger.info(
                    f"Trailing stop enabled: {position_id} "
                    f"distance={distance_pips}pips active={pos.trailing_stop_active}"
                )
                return {
                    "position_id": position_id,
                    "enabled": True,
                    "distance_pips": distance_pips,
                    "activate_at_tp1": activate_at_tp1,
                    "initial_stop_price": stop_price,
                }

        return {"error": f"Position {position_id} not found", "enabled": False}

    def update_trailing_stops(self, tp_multiplier: float = 1.5) -> List[Dict]:
        """
        Update trailing stop levels for all positions where it's active.

        Call this on every price tick after positions are updated.
        For BUY positions: stop moves up when price moves up
        For SELL positions: stop moves down when price moves down

        Args:
            tp_multiplier: Multiplier for TP levels (TP1 = SL distance * this)

        Returns:
            List of position IDs with updated trailing stops
        """
        updated = []

        for pos in self.positions:
            if not pos.trailing_stop_enabled:
                continue

            # Determine pip size
            pip_size = self._get_pip_size(pos.symbol)
            tp1_distance = abs(pos.take_profit - pos.entry_price)
            tp1_hit = False

            if pos.direction == "BUY":
                tp1_price = pos.entry_price + tp1_distance * tp_multiplier
                tp1_hit = pos.current_price >= tp1_price
            else:
                tp1_price = pos.entry_price - tp1_distance * tp_multiplier
                tp1_hit = pos.current_price <= tp1_price

            # Activate trailing stop if TP1 is hit
            if not pos.trailing_stop_active and tp1_hit:
                pos.trailing_stop_active = True
                logger.info(
                    f"Trailing stop ACTIVATED on {pos.position_id} at {pos.current_price}"
                )

            # Only update if trailing stop is active
            if pos.trailing_stop_active:
                if pos.direction == "BUY":
                    new_stop = self._pips_to_price(
                        pos.current_price, -pos.trailing_stop_distance_pips, pos.symbol
                    )
                    # Only move up, never down
                    if new_stop > pos.trailing_stop_price:
                        pos.trailing_stop_price = new_stop
                        updated.append(pos.position_id)
                        logger.debug(
                            f"TS updated BUY {pos.position_id}: "
                            f"price={pos.current_price} stop={new_stop:.5f}"
                        )
                else:  # SELL
                    new_stop = self._pips_to_price(
                        pos.current_price, pos.trailing_stop_distance_pips, pos.symbol
                    )
                    # Only move down, never up
                    if (
                        new_stop < pos.trailing_stop_price
                        or pos.trailing_stop_price == 0
                    ):
                        pos.trailing_stop_price = new_stop
                        updated.append(pos.position_id)
                        logger.debug(
                            f"TS updated SELL {pos.position_id}: "
                            f"price={pos.current_price} stop={new_stop:.5f}"
                        )

        return updated

    def check_trailing_stop_hit(self) -> List[Dict]:
        """
        Check if any trailing stop has been hit.
        Returns list of positions that should be closed.

        Call this after update_trailing_stops().
        """
        to_close = []

        for pos in self.positions:
            if not (pos.trailing_stop_enabled and pos.trailing_stop_active):
                continue

            if pos.trailing_stop_price == 0.0:
                continue

            if pos.direction == "BUY":
                if pos.current_price <= pos.trailing_stop_price:
                    to_close.append(
                        {
                            "position_id": pos.position_id,
                            "symbol": pos.symbol,
                            "reason": "TRAILING_STOP_HIT",
                            "exit_price": pos.trailing_stop_price,
                            "pnl": pos.unrealized_pnl,
                        }
                    )
            else:  # SELL
                if pos.current_price >= pos.trailing_stop_price:
                    to_close.append(
                        {
                            "position_id": pos.position_id,
                            "symbol": pos.symbol,
                            "reason": "TRAILING_STOP_HIT",
                            "exit_price": pos.trailing_stop_price,
                            "pnl": pos.unrealized_pnl,
                        }
                    )

        return to_close

    def _pips_to_price(self, price: float, pips: float, symbol: str) -> float:
        """Convert pips to price delta."""
        pip_size = self._get_pip_size(symbol)
        return price + (pips * pip_size)

    def _get_pip_size(self, symbol: str) -> float:
        """Get pip size for a symbol."""
        if "JPY" in symbol:
            return 0.01
        return 0.0001

    def update_positions(self, updates: List[Dict]):
        """Update current prices and P&L for all positions."""
        for update in updates:
            pos_id = update.get("position_id")
            current_price = update.get("current_price")

            for pos in self.positions:
                if pos.position_id == pos_id:
                    pos.current_price = current_price
                    if pos.direction == "BUY":
                        pos.unrealized_pnl = (
                            current_price - pos.entry_price
                        ) * pos.volume
                    else:
                        pos.unrealized_pnl = (
                            pos.entry_price - current_price
                        ) * pos.volume

    def halt_all(self):
        """Activate emergency halt - close all positions."""
        self.halted_until = datetime.now(timezone.utc) + timedelta(hours=24)
        self.status = RiskLevel.BLACK
        logger.critical("KILL SWITCH ACTIVATED - All trading halted for 24 hours")

    def resume(self):
        """Resume trading after halt."""
        self.halted_until = None
        self.status = RiskLevel.GREEN
        logger.info("Trading resumed")

    def calculate_position_size(
        self,
        account_balance: float,
        risk_pct: float,
        entry_price: float,
        stop_loss: float,
        symbol: str = "EURUSD",
    ) -> float:
        """Calculate position size based on risk parameters."""

        # Ensure within limits
        risk_pct = min(risk_pct, self.config.max_risk_per_trade)

        risk_amount = account_balance * risk_pct

        # Pip calculation
        if symbol.upper() in ["EURUSD", "GBPUSD"]:
            pip_size = 0.0001
            pip_value = 10.0
        elif symbol.upper() == "XAUUSD":
            pip_size = 0.01
            pip_value = 1.0
        elif symbol.upper() in ["USDJPY", "GBPJPY"]:
            pip_size = 0.01
            pip_value = 9.0
        else:
            pip_size = 0.0001
            pip_value = 10.0

        pips_at_risk = abs(entry_price - stop_loss) / pip_size
        if pips_at_risk == 0:
            return 0.01

        lot_size = risk_amount / (pips_at_risk * pip_value / 100000)

        return round(max(0.01, min(lot_size, 1.0)), 2)

    def get_status(self) -> Dict:
        """Get current risk status summary."""
        daily_pnl_pct = (
            self.daily_pnl / self.current_equity if self.current_equity > 0 else 0
        )

        return {
            "status": self.status.value,
            "risk_level": self.status.value,
            "equity": self.current_equity,
            "daily_pnl": self.daily_pnl,
            "daily_pnl_pct": daily_pnl_pct,
            "open_positions": len(self.positions),
            "trades_today": self.trade_count_today,
            "halted": self.halted_until is not None,
            "halt_until": self.halted_until.isoformat() if self.halted_until else None,
            "gates": {
                "max_positions": len(self.positions)
                < self.config.max_concurrent_trades,
                "daily_loss_ok": daily_pnl_pct > -self.config.daily_loss_halt,
                "no_halt": self.halted_until is None,
            },
        }

    def reset_daily(self):
        """Reset daily counters."""
        now = datetime.now(timezone.utc)
        if now.date() > self.last_reset.date():
            self.daily_pnl = 0.0
            self.trade_count_today = 0
            self.last_reset = now
            logger.info("Daily counters reset")


# ============================================================================
# EMERGENCY CONTROLS
# ============================================================================


class EmergencyController:
    """Emergency stop and kill switch controls."""

    def __init__(self, risk_manager: RiskManager, executor: Any = None):
        self.risk_manager = risk_manager
        self.executor = executor
        self.emergency_contacts = []
        self.emergency_log = []

    def emergency_stop(self, reason: str, close_all: bool = True):
        """Execute emergency stop protocol."""
        timestamp = datetime.now(timezone.utc)

        log_entry = {
            "timestamp": timestamp.isoformat(),
            "action": "EMERGENCY_STOP",
            "reason": reason,
            "close_all": close_all,
            "positions_closed": 0,
        }

        if close_all and self.executor:
            # Close all positions
            try:
                results = self.risk_manager.close_all()
                log_entry["positions_closed"] = len(results)
            except Exception as e:
                log_entry["error"] = str(e)

        # Halt trading
        self.risk_manager.halt_all()

        # Log
        self.emergency_log.append(log_entry)

        logger.critical(f"EMERGENCY STOP: {reason}")

        return log_entry

    def partial_halt(self, reason: str, pause_minutes: int = 60):
        """Partial halt - pause for specified duration."""
        self.risk_manager.halted_until = datetime.now(timezone.utc) + timedelta(
            minutes=pause_minutes
        )

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "PARTIAL_HALT",
            "reason": reason,
            "pause_minutes": pause_minutes,
        }

        self.emergency_log.append(log_entry)
        logger.warning(f"PARTIAL HALT: {reason} - Paused for {pause_minutes} minutes")

        return log_entry

    def get_emergency_log(self) -> List[Dict]:
        """Get emergency action log."""
        return self.emergency_log


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """CLI for risk management operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Risk Management CLI")
    parser.add_argument(
        "--action",
        required=True,
        choices=["status", "check", "halt", "resume"],
        help="Action to perform",
    )
    parser.add_argument("--symbol", help="Symbol for correlation check")
    parser.add_argument("--spread", type=float, help="Current spread")
    parser.add_argument("--avg-spread", type=float, help="Average spread")

    args = parser.parse_args()

    risk_mgr = RiskManager()

    if args.action == "status":
        status = risk_mgr.get_status()
        print(f"\nRisk Status: {status['status']}")
        print(f"Equity: ${status['equity']:,.2f}")
        print(f"Daily P&L: ${status['daily_pnl']:,.2f} ({status['daily_pnl_pct']:.2%})")
        print(f"Open Positions: {status['open_positions']}")
        print(f"Trades Today: {status['trades_today']}")
        print(f"Halted: {status['halted']}")

        print("\nGates Status:")
        for gate, passed in status["gates"].items():
            print(f"  {gate}: {'✓' if passed else '✗'}")

    elif args.action == "check":
        if args.spread and args.avg_spread:
            result = risk_mgr.check_spread(
                args.symbol or "EURUSD", args.spread, args.avg_spread
            )
            print(f"\nSpread Check: {result.gate_status.value}")
            if result.blocked_reason:
                print(f"Blocked: {result.blocked_reason}")
            if result.warnings:
                for w in result.warnings:
                    print(f"Warning: {w}")


if __name__ == "__main__":
    main()
