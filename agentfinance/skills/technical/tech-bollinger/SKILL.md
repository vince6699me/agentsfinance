---
name: tech-bollinger
description: >
  Bollinger Bands indicator analysis. Use when identifying volatility expansion/contraction,
  mean reversion trades, and Bollinger Band squeeze breakout signals.
---

# Tech Bollinger Bands Skill

Bollinger Bands measure volatility using a middle band (SMA) with upper/lower bands at standard deviations.

## Core Parameters

| Parameter | Standard | Narrow | Wide |
|-----------|----------|--------|------|
| Period | 20 | 20 | 20 |
| Std Dev | 2.0 | 1.5 | 3.0 |

## Signal Types

### Mean Reversion
- **Lower Band Touch**: Price often bounces from lower band → Buy
- **Upper Band Touch**: Price often bounces from upper band → Sell
- **Middle Band Retest**: After band touch, price often retests middle → TP target

### Trend Continuation
- **Walk the Band**: Price riding upper band in uptrend = strong buy
- **Walk the Band**: Price riding lower band in downtrend = strong sell
- **Band Squeeze**: Contraction followed by expansion = breakout coming

### Bollinger Squeeze
- Bands contract (squeeze) → volatility at lows
- Breakout direction usually follows 20-period trend
- Volume surge on squeeze break = confirmation

## Trading Rules

### Mean Reversion
1. Price touches lower band + RSI OS = Buy
2. Price touches upper band + RSI OB = Sell
3. TP: Middle band or opposite band

### Trend Following
1. Price above middle band + middle band sloping up = Buy
2. Price below middle band + middle band sloping down = Sell
3. Stop: Middle band or opposite band

### Squeeze Breakout
1. Bands squeeze to minimum width
2. Wait for candle close outside bands
3. Enter in direction of breakout
4. Stop: Inside the squeeze range

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Band touch + RSI extreme | +25% |
| Squeeze before expansion | +20% |
| Volume confirmation | +20% |
| Multiple timeframe alignment | +20% |
| Strong candle close outside band | +15% |

## Example

```
USDJPY H1: Bollinger Band setup
- Price touches lower band
- RSI at 28 (oversold)
- Bands beginning to expand
↓
BUY at 148.20
Stop: Below lower band (20 pips)
TP1: Middle band at 148.60
TP2: Upper band at 149.00
Confidence: 80%
```
