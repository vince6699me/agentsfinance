---
name: smc-bos-choch
description: >
  Smart Money Concepts Break of Structure (BOS) and Change of Character (CHoCH) detection.
  Use when identifying trend shifts, structure breaks, and validating momentum changes.
---

# SMC BOS/CHoCH Skill

BOS and CHoCH are the foundation of SMC trend identification and trade validation.

## Core Concepts

### Break of Structure (BOS)
A break of the last swing high/low that confirms the current trend direction.
- Bullish BOS: Price breaks above last swing high in uptrend
- Bearish BOS: Price breaks below last swing low in downtrend

### Change of Character (CHoCH)
A structure break that ALSO signals a potential trend change.
- Occurs when the last swing low is broken in an uptrend (bullish CHoCH)
- Occurs when the last swing high is broken in a downtrend (bearish CHoCH)
- CHoCH is essentially a BOS that breaks the previous wave 4

## Structure Detection

```
Trend: Higher Highs (HH), Higher Lows (HL) = Bullish
Trend: Lower Highs (LH), Lower Lows (LL) = Bearish

BOS Bullish: Price > last swing high
BOS Bearish: Price < last swing low

CHoCH Bullish: Price < last swing low (in uptrend)
CHoCH Bearish: Price > last swing high (in downtrend)
```

## Trading Rules

### Entry on BOS
- Enter on pullback after BOS confirmation
- Stop at the broken structure point
- TP at next structure level

### Entry on CHoCH
- CHoCH = potential trend reversal
- Wait for retest of broken structure
- Confirm with FVGs, OBs, or momentum divergence

## Confidence Scoring

| Factor | Weight |
|--------|--------|
| Strong momentum candle closes beyond structure | +30% |
| Followed by pullback and continuation | +25% |
| CHoCH vs BOS (CHoCH = higher conviction) | +20% |
| Higher timeframe confirms | +20% |
| Volume surge on break | +15% |
| Multiple timeframe alignment | +10% (max) |

## Example

```
EURUSD H1: Price breaks above 1.0880 (swing high)
BOS Confirmed → Look for pullback entries
Entry: 1.0870 pullback
Stop: 1.0855
TP: 1.0910
Confidence: 75%
```
