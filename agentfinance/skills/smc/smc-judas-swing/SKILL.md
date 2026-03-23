---
name: smc-judas-swing
description: >
  SMC Judas Swing pattern - a trap setup where institutions trap both bulls and bears.
  Use when identifying multi-step traps and trading the reversal from institutional traps.
---

# SMC Judas Swing Skill

The Judas Swing is a multi-timeframe trap pattern that catches both retail traders and early institutional traders.

## Pattern Concept

Institutions need to trap retail traders AND other institutions to acquire positions. The Judas Swing creates maximum pain.

### Bearish Judas Swing (Trap for Buyers)
1. Price breaks above structure (bulls enter)
2. Pulls back to OB (more bulls)
3. Fails to break higher → reverses
4. Bulls trapped → institutional short begins

### Bullish Judas Swing (Trap for Sellers)
1. Price breaks below structure (bears enter)
2. Pulls back to OB (more bears)
3. Fails to break lower → reverses
4. Bears trapped → institutional long begins

## Detection Rules

### Bearish Judas Swing
```
1. Break of swing high (bull trap begins)
2. Price returns to test OB
3. Lower high forms (rejection)
4. Break below OB = confirmation
```

### Bullish Judas Swing
```
1. Break of swing low (bear trap begins)
2. Price returns to test OB
3. Higher low forms (support)
4. Break above OB = confirmation
```

## Key Levels

| Level | Significance |
|-------|-------------|
| Trap Entry | Point where retail gets trapped |
| Trap Exit | Where trapped traders stop out |
| Flip Zone | Where trapped become trend followers |

## Trading Rules

### Entry
- Wait for trap to be " sprung" (break below/above trap zone)
- Enter on retest of the broken level
- FVG at retest = high conviction

### Stop Loss
- Above/below the swing extreme that was trapped
- Conservative: 1 ATR beyond trap zone

### Targets
- TP1: Next structure level (1R)
- TP2: Previous swing (2R)
- TP3: Opposite kill zone (3R)

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Clear 3-wave trap structure | +30% |
| CHoCH confirms reversal | +25% |
| FVG at entry point | +20% |
| Premium/discount zone | +15% |
| Kill zone timing | +10% |

## Example

```
EURUSD H4 Bearish Judas Swing:
1. Price breaks above 1.0950 (trap)
2. Returns to OB at 1.0920-1.0930
3. Lower high at 1.0960
4. Break below 1.0920 = confirmation

Entry: 1.0920 (retest)
Stop: 1.0970 (50 pips)
TP1: 1.0860 (1:1)
TP2: 1.0800 (2:1)
Confidence: 82%
```
