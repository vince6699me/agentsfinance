---
name: tech-macd
description: >
  MACD (Moving Average Convergence Divergence) analysis. Use when identifying trend direction,
  momentum shifts, and MACD crossovers for trade entries.
---

# Tech MACD Skill

MACD combines trend and momentum into a single indicator using the relationship between two EMAs.

## Core Parameters

| Parameter | Standard | Fast | Slow |
|-----------|----------|------|------|
| Fast EMA | 12 | 8 | 16 |
| Slow EMA | 26 | 12 | 32 |
| Signal Line | 9 | 6 | 12 |

## Signal Types

### MACD Crossover
- **Bullish Crossover**: MACD crosses above signal line → Buy
- **Bearish Crossover**: MACD crosses below signal line → Sell

### Centerline Crossover
- **Bullish**: MACD crosses above 0 → Momentum bullish
- **Bearish**: MACD crosses below 0 → Momentum bearish

### Histogram
- **Growing Histogram**: Momentum increasing in direction of trend
- **Shrinking Histogram**: Momentum weakening, potential reversal
- **Divergence**: Price vs histogram = reversal signal

## Trading Rules

### Trend-Following
1. MACD > 0 → Only buy setups
2. MACD < 0 → Only sell setups
3. Histogram growing = confirm entry

### Momentum Entry
1. Wait for MACD to cross signal line
2. Histogram must be at least 2 bars growing
3. Enter on next candle open

### Histogram Reversal
1. 3+ bars of shrinking histogram
2. Price making new highs/lows without MACD confirmation
3. Enter opposite direction when histogram starts growing

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Crossover at extreme (>2 ATR) | +25% |
| Zero-line crossover confirmation | +20% |
| Histogram 3+ bars growing | +20% |
| Multiple timeframe MACD aligned | +20% |
| Volume surge on crossover | +15% |

## Example

```
GBPUSD H4: MACD bullish crossover
- MACD crosses above signal line
- MACD line above zero
- Histogram growing (2 bars)
↓
BUY on confirmation candle
Stop: Below last swing low (40 pips)
TP: Next resistance (80 pips, 2:1)
Confidence: 78%
```
