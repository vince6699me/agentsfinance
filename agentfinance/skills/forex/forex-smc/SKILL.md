---
name: forex-smc
description: >
  Forex-specific SMC trading strategies. Use when applying Smart Money Concepts to currency pairs,
  considering forex-specific factors like correlations, rate differentials, and session behavior.
---

# Forex SMC Skill

Applying SMC methodology specifically to forex markets.

## Forex-Specific SMC Factors

### Rate Differentials
- **Positive carry pairs**: Buy澳元/美元,美元/日元
- **Negative carry pairs**: Sell美元/瑞郎,美元/日元
- Carry affects institutional positioning
- COT data more reliable in forex

### Major Pairs Characteristics
| Pair | Volatility | Trendiness | Best SMC Setup |
|------|------------|------------|---------------|
| EURUSD | Medium | Trending | All setups |
| GBPUSD | High | Trending | Silver Bullet |
| USDJPY | High | Trend + Range | Liquidity grabs |
| AUDUSD | Medium | Trend-following | BOS/CHoCH |
| USDCAD | Medium | Range-prone | Range + SMC |
| USDCHF | Low | Safe haven | Counter-trend |

## Session-Based SMC

### London Session (07:00-10:00 UTC)
- High volatility, trending moves
- Best for momentum SMC setups
- OB retests after London open spike

### NY Session (12:00-15:00 UTC)
- Highest volatility
- Best for EURUSD, GBPUSD
- Watch for liquidity grabs at open

### Overlap (12:00-14:00 UTC)
- Most volatile period
- Trend continuation likely
- Avoid range-bound SMC setups

## Correlation Analysis
- EURUSD + GBPUSD (positive)
- USDJPY + USDCHF (negative to USD)
- AUDUSD + NZDUSD (positive)
- Avoid correlated entries
- Hedge correlated risk

## Typical Pip Targets
| Timeframe | Stop | TP1 | TP2 |
|-----------|------|-----|------|
| M15 | 10-15 | 15 | 25 |
| H1 | 20-30 | 40 | 60 |
| H4 | 40-60 | 80 | 120 |
| D1 | 80-150 | 200 | 400 |

## Confidence Scoring
| Factor | Weight |
|--------|--------|
| Kill zone timing | +20% |
| Major pair | +15% |
| Rate differential aligned | +20% |
| Cross-pair confirmation | +15% |
| Carry direction | +15% |
| COT extreme reading | +15% |
