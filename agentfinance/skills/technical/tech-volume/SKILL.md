---
name: tech-volume
description: >
  Volume analysis for confirming price action. Use when validating breakouts, identifying
  accumulation/distribution, and confirming trend strength with volume indicators.
---

# Tech Volume Skill

Volume confirms price action and identifies institutional activity hidden in price movements.

## Core Volume Indicators

### OBV (On-Balance Volume)
- **OBV rising**: Accumulation (smart money buying)
- **OBV falling**: Distribution (smart money selling)
- **OBV divergence**: Reversal signal

### VWAP (Volume Weighted Average Price)
- **Price > VWAP**: Bullish bias
- **Price < VWAP**: Bearish bias
- **VWAP as support/resistance**: Intraday entries

### Volume Profile
- **High volume nodes**: Institutional activity zones
- **Low volume nodes**: Weak areas (prone to fills)
- **POC (Point of Control)**: Fair value area

### CMF (Chaikin Money Flow)
- **CMF > 0**: Buying pressure
- **CMF < 0**: Selling pressure
- **CMF divergence**: Reversal signal

## Trading Rules

### Breakout Confirmation
1. Price breaks resistance + volume surge (1.5x avg) = Valid
2. Price breaks resistance + volume decline = False break
3. Volume surge on pullback = Institutional accumulation

### VWAP Trading
1. Price above VWAP → Buy on pullbacks to VWAP
2. Price below VWAP → Sell on rallies to VWAP
3. VWAP breakout + volume = Trend day

### OBV Confirmation
1. OBV making higher highs with price = Confirmed uptrend
2. OBV divergence with price = Reversal warning
3. OBV break of trend = Confirm breakout

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Volume surge on breakout | +30% |
| OBV confirming direction | +25% |
| VWAP support/resistance holding | +20% |
| CMF aligned with trade direction | +15% |
| High volume node confluence | +10% |

## Example

```
EURUSD: Volume confirmation
- Price breaks above 1.0900 resistance
- Volume = 2x 20-day average
- OBV rising (new highs)
- VWAP above price (bullish bias)
↓
BUY confirmation
Stop: Below 1.0880 (20 pips)
TP: 1.0950 (50 pips, 2.5:1)
Confidence: 85%
```
