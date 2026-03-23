---
name: backtest-combined
description: >
  Backtesting combined SMC + Technical strategies. Use when testing multi-factor trading
  systems that combine structural analysis with indicator confirmation.
---

# Backtest Combined Skill

Combined SMC + Technical indicator backtesting framework.

## Multi-Factor Strategy Design

### Factor Hierarchy
1. **Structure (SMC)**: Primary filter - trend direction
2. **Entry (Combined)**: Signal confirmation
3. **Risk (Technical)**: Position sizing

### Strategy Template
```
Filter: SMC bias (bullish/bearish/neutral)
  ↓
Entry: SMC pattern + Technical confirmation
  ↓
Sizing: ATR-based position sizing
  ↓
Exit: Structure-based TP + Technical trailing
```

## Combined Entry Matrix

| SMC Signal | Tech Confirm | Action |
|-----------|-------------|--------|
| OB in discount | RSI OS + divergence | BUY |
| OB in discount | No confirm | WATCH |
| OB in premium | RSI OB | SKIP |
| FVG unmitigated | MACD cross | BUY |
| FVG mitigated | No confirm | SKIP |

## Confidence Scoring in Backtest

```
Total Score = (SMC_Score × 0.5) + (Tech_Score × 0.5)
Minimum to enter: 0.65
Minimum for full position: 0.80
```

## Performance Expectations
| Regime | Expected Win Rate |
|--------|-----------------|
| Trending | 50-60% |
| Ranging | 35-45% |
| Volatile | 40-50% |
| Overall | 45-55% |

## Regime-Specific Optimization
- Trend trades: Higher TP, trailing stops
- Range trades: Mean reversion, tighter SL
- Volatile: Smaller size, wider SL
