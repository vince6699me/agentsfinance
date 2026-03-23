---
name: forex-cot
description: >
  Forex COT (Commitment of Traders) analysis. Use when analyzing currency positioning
  from CFTC reports, identifying institutional sentiment, and forecasting reversals.
---

# Forex COT Skill

COT data analysis specifically for forex currency pairs.

## Forex COT Data Sources
- CFTC publishes forex futures data weekly
- Covers: USD Index, EUR, GBP, JPY, AUD, CAD, CHF
- 3-day reporting lag
- Best for weekly/daily analysis

## Key Metrics for Forex

### Net Non-Commercial Position
- Long - Short = Net positioning
- Positive = Net long USD
- Negative = Net short USD

### Positioning Extremes
| Percentile | Signal |
|------------|--------|
| > 90% | Extreme long (reversal risk) |
| < 10% | Extreme short (reversal risk) |
| 30-70% | Normal range |

## Currency-Specific Signals

### USD Index (DXY)
- Proxy for overall USD positioning
- DXY up = USD strengthening
- Commercial hedging useful signal

### EUR/USD
- Net non-commercial EUR position
- Extreme long EUR = bearish signal
- Commercial hedgers often correct

### USD/JPY
- Watch JPY positioning closely
- Carry trade positioning indicator
- Risk-off flows affect positioning

## COT-Based Trading Rules

### Reversal Signal
1. Net position at 90th percentile
2. Price at resistance
3. Technical signals turning bearish
→ **SHORT** signal

### Trend Confirmation
1. Net position shifting bullish
2. Price in uptrend
3. No extreme readings
→ **HOLD/ADD** long

## Confidence Scoring
| Factor | Weight |
|--------|--------|
| At historical extreme | +30% |
| Multiple weeks of shift | +25% |
| Price not following position | +20% |
| Commercials confirm | +15% |
| Technical alignment | +10% |
