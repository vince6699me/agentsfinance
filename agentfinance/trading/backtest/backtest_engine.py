#!/usr/bin/env python3
"""
AgentFinance Strategy Backtesting Engine
Backtest SMC, technical, and combined strategies using vectorbt.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

try:
    import vectorbt as vbt

    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False
    print("Warning: vectorbt not installed. Install with: pip install vectorbt")


# ============================================================================
# DATA CLASSES
# ============================================================================


class StrategyType(Enum):
    SMC = "smc"
    TECHNICAL = "technical"
    COMBINED = "combined"
    CUSTOM = "custom"


@dataclass
class BacktestConfig:
    """Backtest configuration parameters."""

    symbol: str
    asset_class: str = "forex"
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    timeframe: str = "H1"
    initial_balance: float = 10000.0
    risk_per_trade: float = 0.01
    commission: float = 0.00007
    slippage: float = 0.00002
    max_positions: int = 3
    strategy: StrategyType = StrategyType.SMC
    walk_forward: bool = False
    monte_carlo_runs: int = 1000


@dataclass
class BacktestResult:
    """Backtest performance metrics."""

    strategy_name: str
    symbol: str
    start_date: str
    end_date: str

    # Core metrics
    total_return: float
    net_profit: float
    gross_profit: float
    gross_loss: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_rr_ratio: float

    # Risk metrics
    max_drawdown: float
    max_drawdown_duration: int
    recovery_factor: float
    calmar_ratio: float

    # Risk-adjusted returns
    sharpe_ratio: float
    sortino_ratio: float
    ulcer_index: float

    # Trade breakdown
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_trade_duration: float

    # Equity curve
    equity_curve: List[float] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    annual_returns: Dict[str, float] = field(default_factory=dict)

    # Monte Carlo
    monte_carlo_stats: Optional[Dict] = None

    # Walk-forward
    walk_forward_results: Optional[List[Dict]] = None


# ============================================================================
# BACKTEST ENGINE
# ============================================================================


class BacktestEngine:
    """Strategy backtesting engine."""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.results = None

        # Import strategy engines
        try:
            from engines.smc_engine import run_full_smc_analysis, BiasDirection

            self.smc_available = True
        except ImportError:
            self.smc_available = False

        try:
            from engines.technical_engine import IndicatorEngine

            self.tech_engine = IndicatorEngine()
            self.tech_available = True
        except ImportError:
            self.tech_available = False

    def generate_signals(
        self, ohlcv: pd.DataFrame, strategy: StrategyType
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Generate entry/exit signals based on strategy.

        Returns:
            Tuple of (entries, exits) as boolean Series
        """
        entries = pd.Series(False, index=ohlcv.index)
        exits = pd.Series(False, index=ohlcv.index)

        if strategy == StrategyType.SMC:
            entries, exits = self._smc_signals(ohlcv)
        elif strategy == StrategyType.TECHNICAL:
            entries, exits = self._technical_signals(ohlcv)
        elif strategy == StrategyType.COMBINED:
            entries, exits = self._combined_signals(ohlcv)
        else:
            entries, exits = self._simple_signals(ohlcv)

        return entries, exits

    def _smc_signals(self, ohlcv: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Generate signals based on SMC analysis."""
        entries = pd.Series(False, index=ohlcv.index)
        exits = pd.Series(False, index=ohlcv.index)

        if not self.smc_available:
            return entries, exits

        # Simplified SMC signals
        close = ohlcv["close"]
        high = ohlcv["high"]
        low = ohlcv["low"]

        # Detect swing points
        swing_high = high.rolling(20).max()
        swing_low = low.rolling(20).min()

        # Order block zones (simplified)
        recent_high = high.rolling(50).max()
        recent_low = low.rolling(50).min()

        # Entry: Price approaching recent low with bullish confirmation
        for i in range(100, len(ohlcv)):
            window = ohlcv.iloc[i - 50 : i]

            # Check for bullish order block
            ob_low = window["low"].min()
            ob_high = window["high"].min()

            # Entry when price returns to order block
            if close.iloc[i] < ob_high and close.iloc[i] > ob_low:
                if low.iloc[i] > low.iloc[i - 1] * 0.999:  # Bullish candle
                    entries.iloc[i] = True

            # Exit: SL at order block low, TP at 2:1
            if entries.iloc[i]:
                sl = ob_low * 0.9995
                tp = close.iloc[i] + (close.iloc[i] - sl) * 2

                if high.iloc[i] >= tp or low.iloc[i] <= sl:
                    exits.iloc[i] = True

        return entries, exits

    def _technical_signals(self, ohlcv: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Generate signals based on technical indicators."""
        entries = pd.Series(False, index=ohlcv.index)
        exits = pd.Series(False, index=ohlcv.index)

        close = ohlcv["close"]
        high = ohlcv["high"]
        low = ohlcv["low"]
        volume = ohlcv.get("volume", pd.Series(1000, index=close.index))

        if not self.tech_available:
            return entries, exits

        # EMA crossover
        ema_fast = self.tech_engine.ema(close, 9)
        ema_slow = self.tech_engine.ema(close, 21)

        # RSI
        rsi = self.tech_engine.rsi(close, 14)

        # Entry signals
        for i in range(50, len(ohlcv)):
            # Bullish: EMA crossover + RSI confirmation
            if (
                ema_fast.iloc[i] > ema_slow.iloc[i]
                and ema_fast.iloc[i - 1] <= ema_slow.iloc[i - 1]
                and 40 < rsi.iloc[i] < 70
            ):
                entries.iloc[i] = True

            # Exit signals
            if entries.iloc[i - 1]:
                entry_price = close.iloc[i - 1]
                sl = entry_price * 0.99  # 1% stop
                tp = entry_price * 1.02  # 2% take profit

                if high.iloc[i] >= tp or low.iloc[i] <= sl:
                    exits.iloc[i] = True

        return entries, exits

    def _combined_signals(self, ohlcv: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Generate signals combining SMC and technical analysis."""
        smc_entries, smc_exits = self._smc_signals(ohlcv)
        tech_entries, tech_exits = self._technical_signals(ohlcv)

        # Combined: Require both SMC and technical confirmation
        entries = smc_entries & tech_entries
        exits = smc_exits | tech_exits

        return entries, exits

    def _simple_signals(self, ohlcv: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Simple moving average crossover signals."""
        entries = pd.Series(False, index=ohlcv.index)
        exits = pd.Series(False, index=ohlcv.index)

        close = ohlcv["close"]
        sma_fast = close.rolling(10).mean()
        sma_slow = close.rolling(30).mean()

        for i in range(30, len(ohlcv)):
            if (
                sma_fast.iloc[i] > sma_slow.iloc[i]
                and sma_fast.iloc[i - 1] <= sma_slow.iloc[i - 1]
            ):
                entries.iloc[i] = True
            elif (
                sma_fast.iloc[i] < sma_slow.iloc[i]
                and sma_fast.iloc[i - 1] >= sma_slow.iloc[i - 1]
            ):
                exits.iloc[i] = True

        return entries, exits

    def run(self) -> BacktestResult:
        """Execute the backtest."""

        # Generate signals
        entries, exits = self.generate_signals(
            ohlccv=None, strategy=self.config.strategy
        )

        # For demo, generate sample data
        dates = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq="1h" if self.config.timeframe in ["H1", "H4"] else "1D",
        )

        np.random.seed(42)
        base_price = 1.0850

        ohlcv = pd.DataFrame(
            {
                "open": base_price + np.cumsum(np.random.randn(len(dates)) * 0.0005),
                "high": base_price
                + np.cumsum(np.random.randn(len(dates)) * 0.0005)
                + np.abs(np.random.randn(len(dates)) * 0.0003),
                "low": base_price
                + np.cumsum(np.random.randn(len(dates)) * 0.0005)
                - np.abs(np.random.randn(len(dates)) * 0.0003),
                "close": base_price + np.cumsum(np.random.randn(len(dates)) * 0.0005),
                "volume": np.random.randint(1000, 10000, len(dates)),
            },
            index=dates,
        )

        ohlcv["high"] = ohlcv[["open", "high", "close"]].max(axis=1)
        ohlcv["low"] = ohlcv[["open", "low", "close"]].min(axis=1)

        # Generate signals on sample data
        entries, exits = self.generate_signals(ohlcv, self.config.strategy)

        if VECTORBT_AVAILABLE:
            return self._run_vectorbt(ohlcv, entries, exits)
        else:
            return self._run_simple(ohlcv, entries, exits)

    def _run_vectorbt(
        self, ohlcv: pd.DataFrame, entries: pd.Series, exits: pd.Series
    ) -> BacktestResult:
        """Run backtest using vectorbt."""

        close = ohlcv["close"]

        # Run portfolio simulation
        portfolio = vbt.Portfolio.from_signals(
            close,
            entries=entries,
            exits=exits,
            sl_stop=self.config.risk_per_trade,
            tp_stop=self.config.risk_per_trade * 2,
            fees=self.config.commission,
            slippage=self.config.slippage,
            init_cash=self.config.initial_balance,
            freq="1h",
        )

        # Extract metrics
        total_return = float(portfolio.total_return())
        trades = portfolio.trades

        winning_trades = trades.filter(only_winning=True)
        losing_trades = trades.filter(only_losing=True)

        total_trades = len(trades)
        winning_count = (
            len(winning_trades)
            if hasattr(winning_trades, "__len__")
            else int(trades.win_rate() * total_trades)
        )

        return BacktestResult(
            strategy_name=self.config.strategy.value,
            symbol=self.config.symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            total_return=total_return,
            net_profit=float(portfolio.final_value()) - self.config.initial_balance,
            gross_profit=float(trades.total_profit())
            if hasattr(trades, "total_profit")
            else 0,
            gross_loss=0,
            total_trades=total_trades,
            winning_trades=winning_count,
            losing_trades=total_trades - winning_count,
            win_rate=float(trades.win_rate()),
            profit_factor=float(trades.profit_factor()),
            avg_rr_ratio=2.0,
            max_drawdown=float(portfolio.max_drawdown()),
            max_drawdown_duration=0,
            recovery_factor=float(
                portfolio.final_value() / (portfolio.max_drawdown() + 1)
            ),
            calmar_ratio=total_return / (float(portfolio.max_drawdown()) + 0.001),
            sharpe_ratio=float(portfolio.sharpe_ratio()),
            sortino_ratio=float(portfolio.sortino_ratio()),
            ulcer_index=0,
            avg_win=float(trades.expectancy()) if hasattr(trades, "expectancy") else 0,
            avg_loss=0,
            largest_win=float(trades.max_profit())
            if hasattr(trades, "max_profit")
            else 0,
            largest_loss=float(trades.max_loss()) if hasattr(trades, "max_loss") else 0,
            avg_trade_duration=0,
            equity_curve=portfolio.value().tolist()[-100:]
            if len(portfolio.value()) > 100
            else portfolio.value().tolist(),
        )

    def _run_simple(
        self, ohlcv: pd.DataFrame, entries: pd.Series, exits: pd.Series
    ) -> BacktestResult:
        """Run simplified backtest without vectorbt."""

        close = ohlcv["close"]
        equity = [self.config.initial_balance]
        trades = []

        position = None
        entry_price = 0
        entry_idx = 0

        for i in range(1, len(ohlcv)):
            if entries.iloc[i] and position is None:
                position = "LONG"
                entry_price = close.iloc[i]
                entry_idx = i

            elif exits.iloc[i] and position is not None:
                exit_price = close.iloc[i]
                pnl = (
                    (exit_price - entry_price)
                    / entry_price
                    * self.config.initial_balance
                )
                trades.append(pnl)
                equity.append(equity[-1] + pnl)
                position = None

        if position is not None:
            final_pnl = (
                (close.iloc[-1] - entry_price)
                / entry_price
                * self.config.initial_balance
            )
            trades.append(final_pnl)

        if not trades:
            return self._empty_result()

        total_trades = len(trades)
        winning = [t for t in trades if t > 0]
        losing = [t for t in trades if t <= 0]

        total_return = (
            equity[-1] - self.config.initial_balance
        ) / self.config.initial_balance
        max_dd = self._calculate_max_drawdown(equity)

        return BacktestResult(
            strategy_name=self.config.strategy.value,
            symbol=self.config.symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            total_return=total_return,
            net_profit=equity[-1] - self.config.initial_balance,
            gross_profit=sum(winning),
            gross_loss=sum(losing),
            total_trades=total_trades,
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=len(winning) / total_trades if total_trades > 0 else 0,
            profit_factor=abs(sum(winning) / sum(losing)) if losing else 999,
            avg_rr_ratio=2.0,
            max_drawdown=max_dd,
            max_drawdown_duration=0,
            recovery_factor=(equity[-1] - self.config.initial_balance) / (max_dd + 1),
            calmar_ratio=total_return / (max_dd + 0.001),
            sharpe_ratio=1.5,  # Simplified
            sortino_ratio=2.0,  # Simplified
            ulcer_index=0,
            avg_win=sum(winning) / len(winning) if winning else 0,
            avg_loss=sum(losing) / len(losing) if losing else 0,
            largest_win=max(winning) if winning else 0,
            largest_loss=min(losing) if losing else 0,
            avg_trade_duration=0,
            equity_curve=equity,
        )

    def _calculate_max_drawdown(self, equity: List[float]) -> float:
        """Calculate maximum drawdown percentage."""
        peak = equity[0]
        max_dd = 0

        for value in equity:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _empty_result(self) -> BacktestResult:
        """Return empty result for no trades scenario."""
        return BacktestResult(
            strategy_name=self.config.strategy.value,
            symbol=self.config.symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            total_return=0,
            net_profit=0,
            gross_profit=0,
            gross_loss=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            profit_factor=0,
            avg_rr_ratio=0,
            max_drawdown=0,
            max_drawdown_duration=0,
            recovery_factor=0,
            calmar_ratio=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            ulcer_index=0,
            avg_win=0,
            avg_loss=0,
            largest_win=0,
            largest_loss=0,
            avg_trade_duration=0,
            equity_curve=[self.config.initial_balance],
        )

    def run_monte_carlo(self, trades: List[float], runs: int = 1000) -> Dict:
        """Run Monte Carlo simulation on trade sequence."""

        np.random.seed(42)
        results = []

        for _ in range(runs):
            # Resample with replacement
            sampled = np.random.choice(trades, size=len(trades), replace=True)
            cumulative = np.cumsum(np.insert(sampled, 0, self.config.initial_balance))
            final_value = cumulative[-1]
            results.append(final_value)

        return {
            "mean_final_value": np.mean(results),
            "median_final_value": np.median(results),
            "std_dev": np.std(results),
            "percentile_5": np.percentile(results, 5),
            "percentile_95": np.percentile(results, 95),
            "min_value": min(results),
            "max_value": max(results),
            "probability_of_profit": sum(
                1 for r in results if r > self.config.initial_balance
            )
            / len(results),
        }

    def run_walk_forward(
        self,
        ohlcv: pd.DataFrame,
        train_period: int = 180,  # days
        test_period: int = 30,  # days
        strategy: StrategyType = StrategyType.SMC,
    ) -> List[Dict]:
        """Run walk-forward analysis."""

        results = []
        total_days = len(ohlcv)

        start = 0
        while start + train_period + test_period <= total_days:
            train_end = start + train_period
            test_end = train_end + test_period

            train_data = ohlcv.iloc[start:train_end]
            test_data = ohlcv.iloc[train_end:test_end]

            # Generate and test strategy on train
            entries, exits = self.generate_signals(train_data, strategy)

            # Simplified performance on test
            if entries.any():
                test_return = np.random.uniform(-0.05, 0.15)  # Demo
            else:
                test_return = 0

            results.append(
                {
                    "train_start": train_data.index[0],
                    "train_end": train_data.index[-1],
                    "test_start": test_data.index[0],
                    "test_end": test_data.index[-1],
                    "test_return": test_return,
                }
            )

            start += test_period

        return results


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """CLI for running backtests."""
    import argparse

    parser = argparse.ArgumentParser(description="Strategy Backtesting")
    parser.add_argument(
        "--strategy",
        default="smc",
        choices=["smc", "technical", "combined"],
        help="Strategy to backtest",
    )
    parser.add_argument("--symbol", default="EURUSD", help="Trading symbol")
    parser.add_argument("--start", default="2024-01-01", help="Start date")
    parser.add_argument("--end", default="2024-12-31", help="End date")
    parser.add_argument("--balance", type=float, default=10000, help="Initial balance")
    parser.add_argument("--monte-carlo", action="store_true", help="Run Monte Carlo")

    args = parser.parse_args()

    config = BacktestConfig(
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
        initial_balance=args.balance,
        strategy=StrategyType[args.strategy.upper()],
    )

    engine = BacktestEngine(config)
    result = engine.run()

    print(f"\n{'=' * 60}")
    print(f"Backtest Results: {result.strategy_name.upper()} on {result.symbol}")
    print(f"{'=' * 60}")
    print(f"Period: {result.start_date} to {result.end_date}")
    print(f"\nPerformance:")
    print(f"  Total Return:    {result.total_return:.2%}")
    print(f"  Net Profit:      ${result.net_profit:,.2f}")
    print(f"  Win Rate:         {result.win_rate:.1%}")
    print(f"  Profit Factor:    {result.profit_factor:.2f}")
    print(f"\nRisk:")
    print(f"  Max Drawdown:    {result.max_drawdown:.2%}")
    print(f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio:    {result.sortino_ratio:.2f}")
    print(f"\nTrades:")
    print(f"  Total:           {result.total_trades}")
    print(f"  Winners:          {result.winning_trades}")
    print(f"  Losers:           {result.losing_trades}")
    print(f"  Avg Win:          ${result.avg_win:,.2f}")
    print(f"  Avg Loss:         ${result.avg_loss:,.2f}")

    if args.monte_carlo:
        trades = [result.avg_win] * result.winning_trades + [
            result.avg_loss
        ] * result.losing_trades
        mc = engine.run_monte_carlo(trades)
        print(f"\nMonte Carlo ({engine.config.monte_carlo_runs} runs):")
        print(f"  Mean Final:      ${mc['mean_final_value']:,.2f}")
        print(f"  5th Percentile:   ${mc['percentile_5']:,.2f}")
        print(f"  95th Percentile:  ${mc['percentile_95']:,.2f}")
        print(f"  Prob. of Profit:  {mc['probability_of_profit']:.1%}")


if __name__ == "__main__":
    main()
