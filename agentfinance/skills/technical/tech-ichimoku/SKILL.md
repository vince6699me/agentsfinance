---
name: tech-ichimoku
description: >
  Ichimoku Cloud analysis. Use when identifying trend direction, support/resistance zones,
  and trading signals from the Ichimoku cloud components.
---

# Tech Ichimoku Skill

Ichimoku provides a comprehensive view of trend, momentum, and support/resistance in one indicator.

## Core Components

| Component | Purpose | Period |
|-----------|---------|--------|
| Tenkan-sen | Fast signal line | 9 |
| Kijun-sen | Slow signal line | 26 |
| Senkou Span A | Cloud leading edge | (T+K)/2 |
| Senkou Span B | Cloud leading edge | 52 |
| Chikou Span | Lagging line | 26 |

## The Cloud (Kumo)

- **Above Cloud**: Trend bullish, cloud = support
- **Below Cloud**: Trend bearish, cloud = resistance
- **Inside Cloud**: Consolidation, cloud = range boundaries

## Signal Types

### Tenkan/Kijun Crossover
- **Bullish TK Cross**: Tenkan crosses above Kijun → Buy
- **Bearish TK Cross**: Tenkan crosses below Kijun → Sell

### Price vs Cloud
- **Price above cloud**: Only buy
- **Price below cloud**: Only sell
- **Price in cloud**: Avoid or range trade

### Cloud Thickness
- **Thick cloud**: Strong support/resistance
- **Thin cloud**: Weak support/resistance (prone to break)

## Trading Rules

### Trend Confirmation
1. Price above cloud + TK > KJ = Strong buy
2. Price below cloud + TK < KJ = Strong sell
3. Chikou above/below price = additional confirmation

### Entry
1. TK/KJ bullish cross above cloud = Buy
2. TK/KJ bearish cross below cloud = Sell
3. Price holding above/below cloud = Hold

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| All components aligned (same direction) | +30% |
| Thick cloud support/resistance | +20% |
| Chikou confirming | +15% |
| Cross above/below cloud | +20% |
| Previous cloud breakout holding | +15% |

## Example

```
EURUSD H4 Ichimoku:
- Price above cloud
- Tenkan above Kijun
- Chikou above price (confirming uptrend)
↓
BUY signal
Stop: Below cloud (40 pips)
TP: Previous high (80 pips, 2:1)
Confidence: 82%
```
