---
name: tech-momentum
description: >
  Momentum indicators analysis - combining multiple momentum tools. Use when identifying
  overbought/oversold conditions, momentum divergences, and rate of change signals.
---

# Tech Momentum Skill

Momentum measures the rate of price change and identifies potential reversals or trend strength.

## Core Momentum Indicators

### Rate of Change (ROC)
- **ROC > 0**: Price rising (positive momentum)
- **ROC < 0**: Price falling (negative momentum)
- **ROC extreme**: Potential reversal zone
- Period: 10-14 standard

### Momentum (Classic)
- **Momentum > 0**: Buying pressure
- **Momentum < 0**: Selling pressure
- **Crossing 100**: Trend shift
- Period: 10-14 standard

### Stochastic
- **%K > %D + >80**: Overbought
- **%K < %D - <20**: Oversold
- **%K crosses %D**: Entry signal
- Periods: 14, 3, 3

## Trading Rules

### Momentum Crossover
1. Momentum crosses above 0 → Potential buy
2. Momentum crosses below 0 → Potential sell
3. Confirm with price action

### Stochastic Strategy
1. Stochastic < 20 → Watch for buy setup
2. %K crosses above %D → Buy
3. Stochastic > 80 → Watch for sell setup
4. %K crosses below %D → Sell

### ROC Strategy
1. ROC at extreme (+5/-5) → Mean reversion possible
2. ROC reversing from extreme → Entry
3. ROC crossing 0 → Trend confirmation

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Multiple indicators aligned | +30% |
| At extreme zone | +25% |
| Divergence confirmed | +25% |
| Zero-line crossover | +15% |
| Volume confirmation | +15% |

## Example

```
GBPUSD: Multiple momentum confirm
- ROC at -4 (extreme bearish)
- Stochastic at 15 (oversold)
- %K crossing above %D
↓
BUY signal
Stop: Below lows (25 pips)
TP: ROC returns to 0 (50 pips)
Confidence: 80%
```
