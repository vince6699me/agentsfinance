---
name: smc-liquidity
description: >
  Smart Money Concepts liquidity detection and trading. Use when identifying stop hunts,
  liquidity pools, liquidity grabs, and trading against retail stop runs.
---

# SMC Liquidity Skill

Institutions need liquidity (stops) to fill their large orders. Identifying liquidity pools is key.

## Core Concepts

### Liquidity Pools
Areas where large concentrations of stop orders exist:
- Above/below swing highs/lows (retail stops)
- Break of structure levels
- Range highs/lows
- Round numbers (1.1000, 1.2000)
- High-volume nodes

### Liquidity Grab (Stop Hunt)
When price quickly sweeps through a liquidity pool before reversing:
- "Stop run above" = price spikes above stops, then falls
- "Stop run below" = price dips below stops, then rises
- Often followed by FVGs at the reversal point

## Detection Patterns

### Equal Highs/Lows
- Two or more highs at same level = liquidity above
- Two or more lows at same level = liquidity below

### Trendline Liquidity
- Breaks of trendlines with subsequent grab of swing levels

### Range Liquidity
- Sweep of range high/low before reversal

### Swing Faults
- Failed attempt to break a swing level = weakness
- Often leads to CHoCH

## Trading Rules

1. **Identify the pool**: Look for equal highs/lows, round numbers, broken structures
2. **Wait for the grab**: Price sweeps through the pool
3. **Confirm reversal**: FVG, OB, or momentum divergence at the grab
4. **Enter**: Market order on reversal confirmation
5. **Stop**: Above/below the grabbed liquidity level

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Multiple liquidity runs at same level | +25% |
| CHoCH follows the liquidity grab | +25% |
| FVG forms at reversal point | +20% |
| Located in premium/discount zone | +15% |
| Institutional order block nearby | +15% |

## Example

```
GBPUSD: Price grabs liquidity above 1.2750 (swing high)
↓
Bearish FVG forms at 1.2755
↓
Sell on return to FVG at 1.2750
Stop: 1.2770
TP: 1.2700
Confidence: 80%
```
