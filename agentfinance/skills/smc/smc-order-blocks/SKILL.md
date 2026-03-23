---
name: smc-order-blocks
description: >
  Smart Money Concepts order block detection and trading. Use when identifying institutional order zones,
  bullish/bearish order blocks, mitigation zones, and order block-based trade setups.
---

# SMC Order Blocks Skill

Order blocks represent areas where institutions placed large orders, creating a "fair value" zone.

## Core Concepts

### Bullish Order Block
- Last bearish candle before a significant bullish move (2+ candles)
- Typically 1-4 candles in length
- Represents institutional buying area

### Bearish Order Block
- Last bullish candle before a significant bearish move (2+ candles)
- Typically 1-4 candles in length
- Represents institutional selling area

## Detection Logic

```
bullish_ob = last_bearish_candle → followed by 2+ bullish candles
bearish_ob = last_bullish_candle → followed by 2+ bearish candles
```

## Trading Rules

1. **Order Block Re-test**: Wait for price to return to unmitigated order block
2. **Mitigation**: If price closes beyond the OB high/low by 50%, consider it mitigated
3. **Entry**: Limit order at the OB extreme, or market order on confirmation
4. **Stop Loss**: Below/above the order block (conservative: 1 ATR)
5. **TP Targets**: Previous swing high/low, next order block, or Fibonacci extensions

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Strong momentum after OB formation | +30% |
| Multiple OBs in confluence | +20% |
| Located in premium/discount zone | +20% |
| Fresh (not yet touched) | +15% |
| Higher timeframe alignment | +15% |

## Example Setup

```
Signal: Bullish Order Block on EURUSD H4
Entry: 1.0850 (limit at OB low)
Stop: 1.0820 (20 pips, 0.5 ATR)
TP: 1.0920 (R:R = 3.5:1)
Confidence: 78%
```
