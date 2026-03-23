---
name: smc-fair-value-gaps
description: >
  Smart Money Concepts fair value gap (FVG) detection. Use when identifying imbalanced price
  gaps, trading the 3-candle rule, and filling FVGs as mean reversion signals.
---

# SMC Fair Value Gaps Skill

FVGs represent price imbalances created when institutions move price too fast, leaving gaps.

## Core Concepts

### FVG Formation (3-Candle Rule)
A gap exists between candles 1 and 3 when:
- Candle 1: Bullish candle
- Candle 2: Small candle (inside candle)
- Candle 3: Bullish candle that gaps above candle 1's high

For bearish FVG: inverse logic

```
Bullish FVG: candle1.low > candle3.high (gap between)
Bearish FVG: candle1.high < candle3.low (gap below)
```

## Trading Rules

### Bullish FVG
- Price returning to FVG = buying opportunity
- Trade from the bottom 1/3 of the FVG (mitigation zone)
- Stop below the FVG low

### Bearish FVG
- Price returning to FVG = selling opportunity
- Trade from the top 1/3 of the FVG (mitigation zone)
- Stop above the FVG high

## FVG Hierarchy

| Type | Description | Trading |
|------|-------------|---------|
| Induced | Forms within a trend (weaker) | Fade cautiously |
| Displaced | Breaks structure (stronger) | Trade with momentum |
| Composite | Multiple overlapping FVGs | High confluence zone |

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Located in premium/discount zone | +25% |
| Displaced FVG (broke BOS) | +25% |
| Confluence with OB | +20% |
| Fresh (not yet filled) | +15% |
| Volume confirmation | +15% |

## Example Setup

```
Signal: Bullish FVG on GBPUSD M15
FVG Range: 1.2670 - 1.2680
Entry: 1.2672 (market on pullback)
Stop: 1.2658 (12 pips)
TP: 1.2710 (3:1 R:R)
Confidence: 72%
```
