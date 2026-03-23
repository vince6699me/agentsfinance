---
name: tech-adx
description: >
  ADX (Average Directional Index) trend strength analysis. Use when measuring trend strength,
  filtering ranging markets, and identifying trend vs consolidation phases.
---

# Tech ADX Skill

ADX measures trend strength (not direction). Combined with +/- DI, it identifies trend and direction.

## Core Parameters

| Parameter | Standard | Sensitive | Conservative |
|-----------|----------|-----------|--------------|
| Period | 14 | 7 | 21 |
| Strong Trend | >25 | >20 | >30 |
| Weak/No Trend | <20 | <15 | <25 |

## Signal Types

### ADX Level
- **ADX > 25**: Trend is established (strong)
- **ADX < 20**: No trend / ranging
- **ADX > 40**: Extremely strong trend (exhaustion risk)
- **ADX Rising**: Trend strengthening
- **ADX Falling**: Trend weakening

### DI Crossover
- **+DI > -DI**: Bullish momentum
- **-DI > +DI**: Bearish momentum
- **Crossover + ADX rising**: Confirm trend entry

## Trading Rules

### Trend Trading
1. ADX > 25 + +DI > -DI → Buy in pullbacks
2. ADX > 25 + -DI > +DI → Sell in rallies
3. Stop: Recent swing low/high

### Range Trading
1. ADX < 20 → No trend, range trade
2. Buy at support, sell at resistance
3. Stop: Beyond range boundaries
4. Exit when ADX > 25 (breakout)

### Trend Exhaustion
1. ADX > 40 + overbought/oversold = Exhaustion
2. Consider profit-taking
3. Watch for reversal signals

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| ADX > 25 and rising | +25% |
| +DI/-DI crossover confirmation | +25% |
| ADX > 40 (high conviction) | +15% |
| Pullback entry in established trend | +20% |
| Multiple timeframe ADX aligned | +15% |

## Example

```
AUDUSD H1: ADX trend setup
- ADX = 28 (rising, trend strengthening)
- +DI crosses above -DI
↓
BUY on pullback to support
Stop: Below swing low (30 pips)
TP: 2x risk (60 pips)
Confidence: 75%
```
