---
name: sentiment-cot
description: >
  CFTC Commitment of Traders report analysis. Use when analyzing institutional positioning,
  extreme sentiment readings, and contrarian trade signals from COT data.
---

# Sentiment COT Skill

COT data reveals what large traders (commercial hedgers) are doing vs. speculators.

## Key COT Concepts

### Trader Categories
| Category | Role | Behavior |
|----------|------|----------|
| **Commercial** | Hedgers (smart money) | Follow fundamental value |
| **Non-Commercial** | Large speculators | Often wrong at extremes |
| **Non-Reportable** | Small traders | Typically contrarian |

### Interpretation
- Commercials **long** + price rising = Bullish confirmation
- Commercials **short** + price rising = Topping signal
- Non-commercial extreme positioning = Reversal risk

## Key Metrics

| Metric | Formula | Signal |
|--------|---------|--------|
| Net Position | Long - Short | Direction bias |
| Change in Position | This week - Last week | Momentum |
| % of OI | Position / Open Interest | Conviction |
| Percentile | vs 52-week range | Extreme reading |

## Extreme Reading Thresholds

| Reading | Percentile | Signal |
|---------|-----------|--------|
| Very Bullish | > 85% | Extreme long (reversal risk) |
| Bullish | 60-85% | Above average longs |
| Neutral | 40-60% | Normal positioning |
| Bearish | 15-40% | Below average longs |
| Very Bearish | < 15% | Extreme short (reversal risk) |

## Trading Rules

### Contrarian Setup (Extreme Readings)
1. Net position at 90th+ percentile
2. Price at resistance with OB signals
3. → **SHORT** (contrarian to crowded trade)

4. Net position at 10th- percentile
5. Price at support with OB signals
6. → **LONG** (contrarian to crowded trade)

### Trend Confirmation
1. Commercials adding to longs in uptrend → Confirm buy
2. Commercials adding to shorts in downtrend → Confirm sell
3. commercials reducing positions at extremes → Reversal warning

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| At historical extreme (>85th/15th pct) | +30% |
| Commercial positioning confirms | +25% |
| Price action confirms divergence | +20% |
| Multiple weeks of positioning change | +15% |
| Open interest trending with price | +10% |

## Limitations
- COT data released weekly (Tues, 3:30pm ET - 3-day lag)
- Not useful for intraday
- Commercial hedging can mask true view
- Combine with price action for confirmation
