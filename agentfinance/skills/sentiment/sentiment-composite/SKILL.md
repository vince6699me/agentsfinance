---
name: sentiment-composite
description: >
  Composite sentiment analysis across multiple sources. Use when combining COT data,
  fear/greed indices, positioning data, and social sentiment for multi-source sentiment analysis.
---

# Sentiment Composite Skill

Best sentiment analysis combines multiple data sources for higher accuracy.

## Data Sources

| Source | Frequency | Reliability | Latency |
|--------|-----------|------------|---------|
| COT Report | Weekly | High | 3 days |
| Fear-Greed Index | Daily | Medium | Real-time |
| Options Skew | Daily | High | Real-time |
| Positioning (IG, etc.) | Daily | Medium | Real-time |
| Social Media | Real-time | Low | Real-time |
| Analyst Ratings | Weekly | Medium | Variable |

## Composite Score Calculation

```
Composite = (COT × 30%) + (FearGreed × 20%) + (Options × 25%) + (Positioning × 15%) + (Social × 10%)
```

## Signal Generation

| Composite Score | Sentiment | Action |
|----------------|-----------|--------|
| > 75% | Very Bullish | Reduce longs, watch for reversal |
| 60-75% | Bullish | Hold longs, cautious on new |
| 40-60% | Neutral | No strong bias |
| 25-40% | Bearish | Hold shorts, cautious on new |
| < 25% | Very Bearish | Reduce shorts, watch for reversal |

## Trading Rules

### Confirmed Sentiment (All Sources Agree)
1. All indicators show same direction
2. High conviction setup
3. Larger position size justified
4. Strong trend likely to continue

### Divergent Sentiment (Sources Disagree)
1. Look for the dominant/lagging indicator
2. When laggard shifts, trend often accelerates
3. Wait for consensus before high conviction
4. Reduce position size

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| All sources aligned | +35% |
| Majority (3+ of 5) agree | +25% |
| COT and Fear-Greed confirm | +20% |
| Historical pattern matches | +10% |
| Volume confirms | +10% |

## Example

```
EURUSD Sentiment Composite:
- COT: 78% bullish (commercial longs) → +30%
- Fear-Greed: 72 (greed zone) → +14%
- Options Skew: Bearish → +18%
- IG Retail: 75% retail long → +10%
- Social: Mixed → +5%
Total: 77% → Very Bullish → REDUCE EXPOSURE
```
