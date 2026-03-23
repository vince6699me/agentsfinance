---
name: indices-vix
description: >
  VIX-based index trading strategy. Use when analyzing market volatility, identifying
  regime changes, and trading based on fear/sentiment through VIX derivatives.
---

# Indices VIX Skill

VIX analysis for index trading decisions.

## VIX Basics

### What is VIX?
- CBOE Volatility Index
- Measures 30-day implied volatility
- "Fear gauge" of the market
- Inverse correlation with S&P 500

### VIX Levels
| Level | Market State | Trading Implication |
|-------|-------------|-------------------|
| < 12 | Complacent | Reduce exposure |
| 12-20 | Normal | Normal trading |
| 20-30 | Anxious | Reduce, hedges on |
| 30-40 | Fearful | Minimal exposure |
| > 40 | Panic | Cash/heavy hedging |

## VIX Trading Strategies

### Low VIX (< 15)
- Reduce position sizes
- Sell volatility (short premium)
- More directional bets
- Buy OTM options cheaply

### High VIX (> 25)
- Increase hedging
- Buy volatility (long premium)
- Defensive positioning
- Look for reversal signals

## VIX Products
| Product | Symbol | Use |
|--------|--------|-----|
| VIX Futures | /VX | Contango/backwardation |
| VIX Options | /VX | Direct volatility plays |
| S&P Options | SPX | Hedging, income |
| VVIX | VVIX | VIX of VIX |

## Contango/Backwardation
| Structure | Meaning | Strategy |
|-----------|---------|---------|
| Contango | Futures > VIX | Roll cost, sell futures |
| Backwardation | Futures < VIX | Roll benefit, buy futures |

## Confidence Scoring
| Factor | Weight |
|--------|--------|
| VIX at extreme level | +30% |
| VIX rising/falling trend | +25% |
| Contango/backwardation | +20% |
| Term structure confirming | +15% |
| Market structure (SMC) | +10% |
