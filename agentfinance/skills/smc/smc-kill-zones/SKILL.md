---
name: smc-kill-zones
description: >
  SMC kill zone trading sessions and timing. Use when identifying high-probability trading
  windows, avoiding low-volatility periods, and timing entries around institutional sessions.
---

# SMC Kill Zones Skill

Kill zones are high-probability trading windows when institutional traders are most active.

## Session Overview (EST → UTC conversion: EST-5, DST-4)

| Kill Zone | EST | UTC | Volatility | Best Pairs |
|-----------|-----|-----|------------|------------|
| London Open | 02:00-05:00 | 07:00-10:00 | High | EUR, GBP, CHF |
| NY Open | 07:00-10:00 | 12:00-15:00 | Very High | All majors |
| London Close | 10:00-12:00 | 15:00-17:00 | Medium | GBP, EUR |
| Asia Session | 19:00-00:00 | 00:00-05:00 | Low | JPY, AUD |

## Best Trading Windows

### London Kill Zone (07:00-10:00 UTC)
- High volatility, trending moves
- Best for momentum scalps
- Fade range expansions in first 30 min

### NY Kill Zone (12:00-15:00 UTC)
- Highest volatility
- Best for EURUSD, GBPUSD
- Avoid first 30 min (chop)
- Lunch (14:00-15:00 UTC) often mean-reverts

### London Close (15:00-17:00 UTC)
- London profit-taking
- Range-bound possible
- Good for reversal trades

## Trading Rules by Session

### During Kill Zone
- Trade with momentum (SMC bias)
- Use tighter stops (20-30 pips)
- Take profits faster (1-2 RR)
- Increase position size by 20-25%

### Outside Kill Zones
- Range trading, fewer setups
- Wider stops (40-50 pips)
- Look for longer-term swings
- Reduce position size by 25-50%

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Trading during London/NY kill zone | +30% |
| Aligns with daily bias | +25% |
| Clear session structure forming | +20% |
| Volume increasing | +15% |
| High-impact news NOT imminent | +10% |

## Key Times to Avoid

- 05:00-07:00 UTC: Low volatility, range
- 17:00-19:00 UTC: Dead zone, London closed
- 23:00-00:00 UTC: Asia open, low liquidity
- High-impact news events: Skip the trade

## Example

```
EURUSD: +30% confidence boost for kill zone trades
Best entries: 07:00-09:00 UTC (London open momentum)
Stop: 20 pips
TP: 40 pips (2:1)
Session bias: Bullish (overnight higher low)
```
