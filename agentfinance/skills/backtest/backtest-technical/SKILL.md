---
name: backtest-technical
description: >
  Backtesting framework for technical indicator strategies. Use when optimizing indicator parameters,
  testing indicator combinations, and measuring technical trading performance.
---

# Backtest Technical Skill

Systematic backtesting of technical indicator-based strategies.

## Technical Strategy Components

### Entry Signals
- Indicator crossovers (EMA, MACD, Stochastic)
- Overbought/oversold reversals (RSI, Stochastic)
- Indicator divergence signals
- Breakout confirmations

### Indicator Parameters
| Indicator | Period Range | Default |
|-----------|-------------|---------|
| SMA | 10-200 | 20, 50, 200 |
| EMA | 5-100 | 9, 21, 50 |
| RSI | 7-21 | 14 |
| MACD | (12,26,9) | Standard |
| ATR | 5-30 | 14 |
| Bollinger | 15-30 / 1.5-3 | 20/2 |

## Multi-Indicator Confluence Backtest

### Signal Combination Rules
- 2+ indicators must agree
- Weight each indicator
- Require minimum combined score
- Filter by trend (ADX > 25)

### Example Confluence
```
BUY: EMA_9 > EMA_21 + RSI > 50 + MACD > Signal
Combined Score = 0.4 + 0.3 + 0.3 = 1.0 (> 0.7 threshold)
```

## Optimization Strategy

### Grid Search
- Test all parameter combinations
- Use parallel processing for speed
- 1000+ combinations typical

### Genetic Algorithm
- Faster than grid search
- Finds local optima
- Less exhaustive than grid

## Key Metrics to Track
- Total trades, win rate
- Average win/loss
- Profit factor, Sharpe ratio
- Max drawdown, drawdown duration
- Expectancy per trade
- Consistency across market conditions
