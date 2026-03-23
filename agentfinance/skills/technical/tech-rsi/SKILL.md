---
name: tech-rsi
description: >
  RSI (Relative Strength Index) technical indicator analysis. Use when identifying overbought/oversold
  conditions, RSI divergences, and RSI-based trend signals.
---

# Tech RSI Skill

RSI measures the magnitude and speed of price changes to identify overbought/oversold conditions.

## Core Parameters

| Parameter | Standard | Conservative | Aggressive |
|-----------|----------|--------------|------------|
| Period | 14 | 21 | 7 |
| Overbought | 70 | 80 | 60 |
| Oversold | 30 | 20 | 40 |

## Signal Types

### Overbought/Oversold
- **OB > 70**: Potential reversal or continuation of rally
- **OS < 30**: Potential reversal or continuation of decline
- **Extreme > 80/ < 20**: High conviction reversal zones

### RSI Divergence
- **Bullish Divergence**: Price makes lower low, RSI makes higher low = reversal up
- **Bearish Divergence**: Price makes higher high, RSI makes lower high = reversal down

### Hidden Divergence (Trend Continuation)
- **Bullish Hidden**: Price makes higher low, RSI makes lower low = trend continues up
- **Bearish Hidden**: Price makes lower high, RSI makes higher high = trend continues down

## Trading Rules

### Range-Bound Strategy
1. RSI < 30 → Potential long entry (OS zone)
2. RSI > 70 → Potential short entry (OB zone)
3. Exit opposite band or at 50-line crossover

### Trend-Following Strategy
1. RSI > 50 → Bias bullish
2. RSI < 50 → Bias bearish
3. Pullbacks to 40-50 (bull) or 50-60 (bear) = entries

### Divergence Strategy
1. Identify divergence on price vs RSI
2. Wait for RSI to cross 50-line or extreme band
3. Enter in direction of RSI breakout

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| RSI in extreme zone (80/20) | +25% |
| Divergence confirmed | +30% |
| Multiple timeframe alignment | +20% |
| Volume confirmation | +15% |
| 50-line crossover in trend direction | +10% |

## Example

```
EURUSD H1: RSI showing bearish divergence
- Price: Higher high at 1.0950
- RSI: Lower high at 62 (below previous 68)
↓
RSI crosses below 60 → SELL
Stop: Above 1.0950 (30 pips)
TP: 1.0880 (R:R 2:1)
Confidence: 72%
```
