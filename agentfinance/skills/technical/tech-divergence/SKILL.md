---
name: tech-divergence
description: >
  Technical divergence detection across multiple indicators. Use when identifying hidden
  and regular divergences as reversal signals across RSI, MACD, Stochastic, and CCI.
---

# Tech Divergence Skill

Divergences occur when price and indicator move in opposite directions, signaling potential reversals.

## Divergence Types

### Regular Divergence (Trend Reversal)

| Type | Price | Indicator | Signal |
|------|-------|-----------|--------|
| Bullish | Lower low | Higher low | Reversal UP |
| Bearish | Higher high | Lower high | Reversal DOWN |

### Hidden Divergence (Trend Continuation)

| Type | Price | Indicator | Signal |
|------|-------|-----------|--------|
| Bullish | Higher low | Lower low | Trend continues UP |
| Bearish | Lower high | Higher high | Trend continues DOWN |

## Detection Rules

### Bullish Regular Divergence
1. Price makes lower low (LL)
2. RSI/MACD/Stochastic makes higher low (HL)
3. Indicator in oversold zone preferred
4. Signal: Entry when indicator crosses up

### Bearish Regular Divergence
1. Price makes higher high (HH)
2. RSI/MACD/Stochastic makes lower high (LH)
3. Indicator in overbought zone preferred
4. Signal: Entry when indicator crosses down

## Trading Rules

### Multi-Indicator Confirmation
1. Divergence on 2+ indicators = Stronger signal
2. Divergence on higher timeframe = Higher conviction
3. Divergence + price action = Confirmed reversal

### Entry Strategy
1. Identify divergence
2. Wait for indicator signal line crossover
3. Confirm with price action (candle reversal)
4. Enter on next candle

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| 3+ indicators showing divergence | +30% |
| Indicator in extreme zone | +25% |
| Higher timeframe confirmed | +20% |
| Price action reversal candle | +15% |
| Hidden vs Regular (regular = stronger) | +10% |

## Example

```
GBPUSD H4: Triple divergence
- Price: Higher high at 1.2750
- RSI: Lower high at 58 (prev 68)
- MACD: Lower histogram peak
- Stochastic: Flattening at 70
↓
Bearish divergence confirmed
↓
SELL after bearish candle close
Stop: Above 1.2750 (30 pips)
TP: 1.2650 (100 pips, 3:1)
Confidence: 82%
```
