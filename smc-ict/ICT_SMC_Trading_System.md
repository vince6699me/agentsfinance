# ICT Smart Money Concept Trading System

**Version:** 1.0  
**Methodology:** Inner Circle Trader (ICT)  
**Timeframe:** Multi-timeframe (Weekly → Daily → H4 → H1/Lower)  
**Markets:** Forex, Crypto, Indices

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Market Structure Analysis](#market-structure-analysis)
3. [Liquidity Concepts](#liquidity-concepts)
4. [Order Blocks](#order-blocks)
5. [Fair Value Gaps](#fair-value-gaps)
6. [Kill Zones & Timing](#kill-zones--timing)
7. [Trade Setup Framework](#trade-setup-framework)
8. [Entry, Exit & Risk Management](#entry-exit--risk-management)
9. [Trade Checklist](#trade-checklist)

---

## System Overview

### Core Philosophy
Trade in the direction of institutional flow by identifying where "smart money" has placed orders and riding the resulting price movements.

### Trading Rules (Priority Order)

1. **Structure First** - Never trade against market structure
2. **With the Trend** - Only trade in direction of higher timeframe trend
3. **At Valid Levels** - Enter only at order blocks, FVGs, or liquidity zones
4. **Proper Timing** - Trade only during active kill zones
5. **Defined Risk** - Always use stop loss and defined risk/reward

### Required Timeframes

| Role | Timeframe | Purpose |
|------|-----------|---------|
| **Direction** | Weekly + Daily | Identify trend direction |
| **Structure** | H4 | Confirm BOS/CHOCH, identify OBs |
| **Entry** | H1 + M15 | Precise entry at OTE |
| **Timing** | M5 + M1 | Kill zone execution |

---

## Market Structure Analysis

### Trend Identification

**Uptrend Definition:**
- Higher Highs (HH)
- Higher Lows (HL)
- Price breaking above previous highs

**Downtrend Definition:**
- Lower Highs (LH)
- Lower Lows (LL)
- Price breaking below previous lows

### Break of Structure (BOS)

**Bullish BOS:**
1. Price makes a higher high
2. Pullback occurs (higher low forms)
3. Price breaks above previous high with momentum

**Bearish BOS:**
1. Price makes a lower low
2. Pullback occurs (lower high forms)
3. Price breaks below previous low with momentum

### Change of Character (CHOCH)

**Bullish CHOCH (Trend Reversal):**
1. Price breaks below extreme demand zone
2. Occurs AFTER bullish BOS
3. Signals potential trend change to bullish

**Bearish CHOCH (Trend Reversal):**
1. Price breaks above extreme supply zone
2. Occurs AFTER bearish BOS
3. Signals potential trend change to bearish

### Market Structure Shift (MSS)

**Bullish MSS:**
- Price falls below extreme demand zone
- DOES NOT require prior bullish BOS
- Confirms order flow change

**Bearish MSS:**
- Price rises above extreme supply zone
- DOES NOT require prior bearish BOS
- Confirms order flow change

### Displacement

**Definition:** Strong impulsive move characterized by:
- Consecutive large candles (70%+ body-to-wick ratio)
- Minimal wicks
- High volume
- Clear direction

**Displacement Rules:**
- Always creates FVGs (1-3 gaps)
- Always creates market structure shift
- Creates new liquidity pools
- Establishes new order blocks

---

## Liquidity Concepts

### Liquidity Types

| Type | Description | Trading Implication |
|------|-------------|-------------------|
| **Swing Highs/Lows** | Previous extreme price points | Primary reversal zones |
| **Round Numbers** | Psychological levels (150.00, 100.00) | Stop clusters |
| **Fractal Levels** | M15/H1 highs matching H4/daily | Multi-timeframe liquidity |
| **Trendline Liquidity** | Liquidity above/below trendlines | Breakout entries |
| **Day/Week Highs** | Session extremes | High-probability grabs |

### Liquidity Grabs

**Pattern:**
1. Price approaches liquidity pool (stop loss area)
2. Quick wick through the level
3. Immediate reversal
4. Creates breaker block or order block

**Trading the Grab:**
- Wait for liquidity grab to complete
- Confirm reversal candlestick
- Enter in direction of original trend
- Stop loss beyond the grab

### Equal Highs/Lows (EQH/EQL)

**Pattern:** Price tests same high/low multiple times

**Implications:**
- Each retest weakens the level
- Final grab creates strong reversal
- Typically precedes CHOCH or MSS

---

## Order Blocks

### Order Block Definition

**Bullish Order Block:**
- Last candle before significant bullish displacement
- Candle body shows institutional accumulation
- Typically bearish candle that marks institutional buy zone

**Bearish Order Block:**
- Last candle before significant bearish displacement
- Candle body shows institutional distribution
- Typically bullish candle that marks institutional sell zone

### Identifying Order Blocks

**Bullish OB Criteria:**
1. Preceded by bearish momentum/displacement
2. Candle has significant bearish body
3. Followed by strong bullish move (displacement)
4. Located at discount zone (lower half of move)

**Bearish OB Criteria:**
1. Preceded by bullish momentum/displacement
2. Candle has significant bullish body
3. Followed by strong bearish move (displacement)
4. Located at premium zone (upper half of move)

### Order Block Quality Ranking

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount (bullish) / premium (bearish) with Choch | Highest |
| 2 | OB with FVG above/below | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB at structure level | Medium |
| 5 | OB without confluence | Low |

### Trading Order Blocks

**Bullish Order Block Entry:**
```
Entry Zone: Top 50% of the order block candle
Stop Loss: Below the order block low
Target: Next supply zone / previous high / 1:2 RR minimum
```

**Bearish Order Block Entry:**
```
Entry Zone: Bottom 50% of the order block candle
Stop Loss: Above the order block high
Target: Next demand zone / previous low / 1:2 RR minimum
```

### Breaker Blocks

**Definition:** Failed order block that reverses from opposite direction

**Bullish Breaker Block:**
- Was a bullish order block
- Price broke below it (failed)
- Price now returning from below
- Expect reversal to upside

**Bearish Breaker Block:**
- Was a bearish order block
- Price broke above it (failed)
- Price now returning from above
- Expect reversal to downside

---

## Fair Value Gaps

### FVG Definition

**Bullish FVG:** Three-candle pattern where:
- Candle 1 closes bullish
- Candle 2 is small
- Candle 3 closes bullish
- Gap between Candle 1's low and Candle 3's high

**Bearish FVG:** Three-candle pattern where:
- Candle 1 closes bearish
- Candle 2 is small
- Candle 3 closes bearish
- Gap between Candle 1's high and Candle 3's low

### FVG Types

| Type | Price Position | Trading Implication |
|------|---------------|-------------------|
| **Bearish FVG** | Above current price | Sell into the gap fill |
| **Bullish FVG** | Below current price | Buy into the gap fill |

### FVG Strength Ranking

**Strongest FVGs:**
1. 3+ consecutive FVGs (FVG cluster)
2. FVGs formed during displacement
3. FVGs containing market structure shift
4. FVGs at order blocks
5. FVGs at liquidity zones

### Trading FVGs

**Bullish FVG Entry:**
```
Entry: Buy limit at bottom of FVG
Stop: Below FVG low
Target: Previous high or next resistance
```

**Bearish FVG Entry:**
```
Entry: Sell limit at top of FVG
Stop: Above FVG high
Target: Previous low or next support
```

---

## Kill Zones & Timing

### Kill Zone Schedule (EST)

| Kill Zone | Time | Active Market | Best Pairs |
|-----------|------|--------------|------------|
| **Asian** | 8PM - 10PM | Tokyo | AUD, NZD, JPY |
| **London** | 2AM - 5AM | London | EUR, GBP |
| **London Open** | 5AM - 7AM | Overlap | All majors |
| **New York** | 7AM - 9AM | New York | USD pairs |
| **London Close** | 10AM - 12PM | London close | All majors |

### Kill Zone Characteristics

**London Kill Zone:**
- Highest volatility
- Best for directional trades
- Creates daily highs/lows
- 70% of daily range formed

**New York Kill Zone:**
- High volatility at open
- Follows London direction
- Good for continuation
- liquidity grabs common

**Asian Kill Zone:**
- Lower volatility
- Range-bound behavior
- Best for reversal trades
- Quiet accumulation

### Best Trading Times

| Priority | Time (EST) | Strategy |
|----------|-----------|----------|
| 1 | 5AM - 7AM | London Open momentum |
| 2 | 7AM - 9AM | NY Open continuation |
| 3 | 2AM - 5AM | London range trades |
| 4 | 10AM - 12PM | London Close reversals |

---

## Trade Setup Framework

### Phase 1: Higher Timeframe Analysis (Weekly + Daily)

1. **Identify Trend Direction**
   - Weekly: HH/HL or LH/LL
   - Daily: Confirm trend alignment

2. **Mark Key Levels**
   - Weekly highs/lows
   - Monthly extremes
   - Major order blocks
   - Significant FVGs

3. **Determine Market Phase**
   - Accumulation
   - Manipulation
   - Distribution

### Phase 2: Intermediate Timeframe (H4)

1. **Identify Current Structure**
   - Current BOS/CHOCH
   - Active order blocks
   - Liquidity pools

2. **Mark Discount/Premium Zones**
   - Upper half = Premium
   - Lower half = Discount

3. **Wait for Displacement**
   - Identify strong moves
   - Mark resulting FVGs
   - Note order blocks formed

### Phase 3: Entry Timeframe (H1 + M15)

1. **Identify Entry Zone**
   - Order block retest
   - FVG fill zone
   - Liquidity grab completion

2. **Confirm Market Structure**
   - CHOCH or MSS on H1
   - Entry aligned with H4 trend

3. **Calculate Optimal Trade Entry (OTE)**
   - Fibonacci 61.8% - 79% retracement
   - Also known as 70.5% level

### Phase 4: Execution (M5 + M1)

1. **Wait for Kill Zone**
2. **Confirm Entry Signal**
   - Reversal candlestick
   - FVG formation
   - Liquidity grab complete
3. **Execute Trade**
   - Limit order at OTE
   - Stop loss at logical level
4. **Adjust for Breakeven**

---

## Entry, Exit & Risk Management

### Entry Rules

**Bullish Entry Conditions:**
1. ✅ Higher timeframe uptrend
2. ✅ Price at bullish order block OR bullish FVG
3. ✅ Located in discount zone
4. ✅ During active kill zone
5. ✅ OTE confirmation (61.8%-79% Fib)
6. ✅ Minimum 1:2 risk/reward

**Bearish Entry Conditions:**
1. ✅ Higher timeframe downtrend
2. ✅ Price at bearish order block OR bearish FVG
3. ✅ Located in premium zone
4. ✅ During active kill zone
5. ✅ OTE confirmation (61.8%-79% Fib)
6. ✅ Minimum 1:2 risk/reward

### Stop Loss Placement

| Scenario | Stop Location |
|----------|--------------|
| Bullish OB | Below OB low |
| Bearish OB | Above OB high |
| Bullish FVG | Below FVG low |
| Bearish FVG | Above FVG high |
| Liquidity Grab | Beyond grab wick |
| Breaker Block | Beyond breaker extreme |

### Take Profit Strategy

**Multiple Targets:**
```
Target 1: 1R (Break even on full lot)
Target 2: 1.5R to 2R (Partial exit 50%)
Target 3: 3R (Trailing stop)
Target 4: Structure extreme (Full exit)
```

**Target Priority:**
1. Next order block (opposite direction)
2. Previous structure extreme
3. Supply/Demand zone
4. Liquidity pool

### Risk Management Rules

| Rule | Specification |
|------|--------------|
| Max Risk Per Trade | 1-2% of account |
| Max Concurrent Trades | 3-5 positions |
| Daily Loss Limit | 5% of account |
| Weekly Loss Limit | 10% of account |
| Min Risk/Reward | 1:2 |
| Max Position Size | Calculated from stop loss |

### Position Size Calculator

```
Position Size = (Account Risk × Risk %) / (Stop Loss × Pip Value)

Example:
Account: $10,000
Risk per trade: 2%
Stop loss: 50 pips
Pip value (EURUSD standard): $10

Position = ($10,000 × 0.02) / (50 × $10)
Position = $200 / $500
Position = 0.4 lots (4 mini lots)
```

---

## Trade Checklist

### Pre-Trade Checklist

- [ ] Higher timeframe trend identified
- [ ] Current market structure confirmed
- [ ] Active order block or FVG identified
- [ ] Price in discount (bullish) or premium (bearish) zone
- [ ] Kill zone timing confirmed
- [ ] Minimum 1:2 risk/reward ratio
- [ ] Stop loss level determined
- [ ] Take profit targets marked
- [ ] Position size calculated
- [ ] Total risk ≤ 2% account

### Entry Checklist

- [ ] Price reached entry zone
- [ ] Entry signal confirmed (candlestick/FVG)
- [ ] Kill zone active
- [ ] Stop loss placed
- [ ] Partial TP set at 1R
- [ ] Trade logged with timestamp

### Exit Checklist

- [ ] Target hit or stop triggered
- [ ] Trade outcome logged
- [ ] Win/loss recorded
- [ ] Lessons noted (if applicable)

---

## Trade Log Template

```markdown
## Trade #___

**Date:** YYYY-MM-DD  
**Pair:** XXXYYY  
**Direction:** LONG / SHORT  
**Timeframe:** H4 → H1  

**Setup:**
- HT Trend: BULLISH / BEARISH
- Structure: BOS / CHOCH / MSS
- OB/FVG: [Details]
- Kill Zone: [London/NY/etc]

**Levels:**
- Entry: _______
- Stop Loss: _______
- Take Profit: _______
- Risk: _______ R

**Result:**
- Outcome: WIN / LOSS / BE
- P&L: _______
- R-multiple: _______

**Notes:**
- [Observations]
```

---

## Common Patterns Quick Reference

### Silver Bullet Setup
1. Price in discount (bullish) / premium (bearish)
2. H4 bullish/bearish candle closes
3. Next H1 candle enters order block
4. Enter on M5/M1 at OTE

### Judas Swing Setup
1. Market creates liquidity grab (swing high/low)
2. Immediate reversal
3. Entry in direction of original trend
4. Target next liquidity pool

### Macd Divergence + SMC
1. Macd shows divergence
2. Price at order block
3. Structure confirms reversal
4. High-probability entry

### Fibonacci Sweep
1. Price respects 61.8% Fib level
2. Candlestick reversal signal
3. Order block confirmation
4. Enter at 70.5% level

---

## Best Practices

### Do's ✅
- Always respect market structure
- Trade in direction of higher timeframe trend
- Use kill zones for timing
- Wait for confirmation before entry
- Maintain strict risk management
- Keep detailed trade logs

### Don'ts ❌
- Trade against structure
- Enter without defined stop loss
- Overleverage position size
- Trade outside kill zones
- Chase price after miss
- Revenge trade losses

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Win Rate | >50% |
| Average R:R | 1:2 minimum |
| Max Drawdown | <15% monthly |
| Profit Factor | >1.5 |
| Avg Trades/Week | 3-5 |

---

*System Version 1.0 - ICT Smart Money Concept Trading System*
*Based on Inner Circle Trader methodology*
