---
name: backtest-smc
description: >
  Backtesting framework for SMC-based trading strategies. Use when validating SMC trade setups,
  optimizing order block and FVG parameters, and measuring strategy performance.
---

# Backtest SMC Skill

Validate SMC strategies through systematic backtesting.

## SMC Backtest Components

### Entry Signals
- Order block retest entries
- FVG mitigation trades
- BOS/CHoCH breakouts
- Liquidity grab reversals
- Silver Bullet patterns

### Exit Rules
- TP at next structure level
- Stop at order block extreme
- Time-based exits (kill zone close)
- Trailing stops after 1R profit

### Parameters to Optimize
| Parameter | Range | Best Fit |
|-----------|-------|---------|
| Lookback period | 20-100 | Medium |
| OB min/max candles | 1-5 | 1-3 |
| FVG min size | 0.5-2 ATR | 1 ATR |
| SL multiple | 0.5-2 ATR | 1 ATR |
| TP ratio | 1:1 to 3:1 | 2:1 |

## Backtest Setup

### Data Requirements
- OHLCV data (1H or 4H recommended)
- 1+ year for robustness
- Multiple market conditions

### SMC Detection Parameters
```python
params = {
    'lookback': 50,         # Swing detection
    'ob_min_candles': 1,    # OB formation
    'ob_max_candles': 4,
    'fvg_threshold': 1.0,    # ATR multiples
    'sl_atr_mult': 1.5,
    'tp_atr_mult': 3.0,
}
```

## Performance Metrics

| Metric | Target | Acceptable |
|--------|--------|-----------|
| Win Rate | >45% | >35% |
| Profit Factor | >1.5 | >1.2 |
| Sharpe Ratio | >1.5 | >1.0 |
| Max Drawdown | <15% | <25% |
| Avg R:R | >2:1 | >1.5:1 |

## Walk-Forward Analysis
1. Train on in-sample data (70%)
2. Validate on out-of-sample (30%)
3. Repeat with rolling windows
4. Accept if OOS performance similar to IS
