# ICT Strategy 01: Micro-Sweep Scalp
**Tier:** Scalping | **Models source:** #1, #6, #12 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, FVG Strength Ranking, Fibonacci OTE 70.5%, Daily/Weekly Loss Limits

---

## Concept

Trade the 20-pip scalp after a session high/low liquidity sweep. Price sweeps the previous session's high (buy-side) or low (sell-side), triggering stop orders, then retraces into an order block or FVG zone — creating optimal entry. Targets the opposing external liquidity level.

**Edge basis:** Displacement of session high/low = institutional stop hunt. Retrace into OB/FVG = smart money absorbing trapped retail orders. The 20-pip target captures the immediate recoil before the next session absorbs the move.

---

## Instruments & Sessions

| Session | Kill Zone | Tradeable Pairs |
|---------|-----------|-----------------|
| London | 03:00–05:00 ET | EUR/USD, GBP/USD, EUR/GBP, AUD/USD |
| New York AM | 08:30–11:00 ET | All majors, US indices (ES, NQ) |
| New York PM | 13:00–15:00 ET | USDMXN, USD/CAD (lower volatility) |

*Exclude kills during NFP (first Friday 08:30 ET) and FOMC days.*

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Context | 15M | Define session range, identify OB/FVG |
| Entry | 5M | Confirm sweep + displacement + retrace |
| Confirmation | 1M | Micro-displacement for precise entry |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Before kill zone opens)

**R1.** Identify the kill zone session: `London` (03:00–05:00 ET) or `NY AM` (08:30–11:00 ET).

**R2.** On the **15M chart**, draw the session range:
- `Session High` = highest high of the previous kill zone session
- `Session Low` = lowest low of the previous kill zone session
- These are the liquidity levels price will target.

**R3.** On the 15M chart, identify the **order block (OB)** or **fair value gap (FVG)**:
- **Bullish OB:** Last bearish candle before a strong bullish candle (2+ bodies), within 5 pips below Session Low.
- **Bearish OB:** Last bullish candle before a strong bearish candle, within 5 pips above Session High.
- **Bullish FVG:** 3-candle pattern where candle 2's high < candle 1's low AND candle 3's high < candle 1's low (gap above).
- **Bearish FVG:** Mirror pattern below.

**R4.** Determine bias on the **15M chart**:
- Price above VWAP (or 50 EMA on 15M) → bias bullish; look for longs.
- Price below VWAP → bias bearish; look for shorts.
- Do NOT trade against HTF bias if 4H chart shows strong trend.

**R5.** Check economic calendar: confirm NO high-impact news within 30 minutes of kill zone open.

---

### Phase 2 — Opportunity Discovery (During kill zone)

**R6.** Wait for the **sweep signal** on the **5M chart**:
- **Bullish sweep:** Price must CLOSE above the Session Low (not just spike/wick). Then price must close back BELOW Session Low within 2–5 candles — this confirms retail buy stops were harvested.
- **Bearish sweep:** Price must CLOSE below the Session High. Then price must close back ABOVE Session High within 2–5 candles.

> ⚠️ **Entry trigger — displacement confirmation (DISPLACEMENT RULE):**
> For a valid SHORT entry:
> 1. Sweep candle (closes below Session High) must have body ≥ 60% of its range.
> 2. Following candle(s) must close BELOW the sweep candle's body low.
> 3. Price must NOT reclaim Session High within 3 candles of the sweep.
> For a valid LONG entry: mirror above with Session Low.

**R7.** Wait for **retrace entry** on the **5M chart**:
- Short: price retrace higher, into or near the identified bearish OB/FVG zone.
- Long: price retrace lower, into the identified bullish OB/FVG zone.
- Retrace must be ≥ 5 pips from sweep low/high before entry is valid. No entry on initial sweep candle.

**R8.** Check **confluence** — minimum 2 of 3:
- [ ] OB or FVG zone at entry level (±5 pips).
- [ ] 62% Fibonacci retracement of the sweep move overlaps the entry zone.
- [ ] VWAP (15M) at or near entry level.

If ≥2 conditions met → valid setup. If <2 → discard.

---

### Phase 3 — Trade Execution

**R9. Entry order:**
- SHORT: `sell limit` at `OB/FVG zone high − 5 pips`.
- LONG: `buy limit` at `OB/FVG zone low + 5 pips`.
- **Validity window:** Order expires if not filled within the kill zone + 30 minutes.

**R10. Stop loss:**
- SHORT: `Session High + 20 pips`.
- LONG: `Session Low − 20 pips`.
- Minimum stop: 15 pips. If calculated stop < 15 pips → skip trade (insufficient room).

**R11. Position sizing:**
```
Risk Amount ($) = Account Equity × 1%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Round DOWN. Example: $10,000 × 1% = $100 / 20 pips / $1 = 5 mini lots.

---

### Phase 4 — Trade Management

**R12. Profit targets (scale out):**

| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Entry ± 20 pips | 80% of position | Close immediately |
| TP2 | Entry ± 35 pips | 20% of position | Trail stop on remainder |

**R13. Stop adjustment:**
| Condition | Action |
|----------|--------|
| Price at TP1 (20 pips profit) | Reduce stop loss by 5 pips toward entry |
| Price at TP2 (35 pips profit) | Move stop to breakeven |
| Price reaches Session High/Low | Close remainder immediately |

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Kill zone session ends with no sweep → no trade that session. |
| INV2 | Sweep occurs but no retrace (price runs away immediately) → no trade. |
| INV3 | High-impact news hits within 5 minutes of planned entry → cancel order. |
| INV4 | Stop pip distance < 15 pips → skip trade. |
| INV5 | Price reclaims session high/low before retrace completes → invalidate setup. |
| INV6 | More than 2 consecutive losing trades → skip next session, review rules. |

---

## Performance Characteristics (backtesting guidance)

| Metric | Expected Range |
|--------|---------------|
| Win rate | 55–65% |
| Average R:R | 1:2 to 1:3 |
| Max consecutive losses | 5–7 |
| Daily opportunity rate | 0–3 per session |
| Annual drawdown target | < 8% |
| Best market fit | EUR/USD, GBP/USD |

*Based on: 2,600-trade backtest across 10 assets (61% WR, 2.17 PF — Quantum Algo 2026); Aggressive mode 90 trades/5yr backtest (45% WR, 1.95 PF — DOE_Trade TradingView).*

---

## Entry Checklist (quick-scan)

- [ ] Kill zone session identified (London or NY AM)
- [ ] Previous session high/low drawn on 15M chart
- [ ] OB or FVG identified near session high/low
- [ ] 15M bias confirmed (above/below VWAP)
- [ ] No high-impact news in next 30 min
- [ ] 5M displacement candle closes and confirms sweep
- [ ] 5M retrace returns to OB/FVG zone
- [ ] Confluence ≥ 2/3 conditions met
- [ ] Stop pip distance ≥ 15 pips
- [ ] Enter with limit order ± 5 pips from zone

---

## Author Notes

The displacement rule (R6) is the critical differentiator. Many traders enter on the sweep itself — this is a losing pattern because institutional orders are rarely filled at the extreme. Waiting for the retrace (R7) and requiring displacement confirmation (R6 body ≥ 60% of range) eliminates the majority of false setups. The 62% Fibonacci overlay in R8 provides a secondary confirmation layer borrowed from Model #11's structure, creating consistency across tiers.

The 80%/20% scale-out (R12) ensures locked profit while leaving room for extended moves. The 20% remainder acts as a lottery ticket — most days TP1 is the ceiling, but occasionally the full swing move develops.

---

## Enhanced Risk Management (v2)

### Position Sizing Formula
```
Risk Amount ($) = Account Equity × 1%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```

### Daily/Weekly Loss Limits (v2)
| Limit Type | Specification | Action When Hit |
|-----------|--------------|----------------|
| **Daily Loss Limit** | 5% of account | Stop trading for the day |
| **Weekly Loss Limit** | 10% of account | Skip next week's trades |
| Max Concurrent Trades | 3 positions | No new entries |

### Trade Log Template (v2)
```markdown
## Trade #___

**Date:** YYYY-MM-DD
**Pair:** XXXYYY
**Direction:** LONG / SHORT
**Timeframe:** 15M → 5M

**Setup:**
- HT Trend: BULLISH / BEARISH
- Structure: BOS / CHOCH / MSS
- OB/FVG: [Details]
- Kill Zone: [London/NY/etc]
- OB Quality Rank: [1-5]
- FVG Strength: [1-5]

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

## Order Block Quality Ranking (v2)

Use only Order Blocks with rank 1–3 for entries:

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount (bullish) / premium (bearish) with CHoCH | Highest |
| 2 | OB with FVG above/below | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB at structure level | Medium |
| 5 | OB without confluence | Low → SKIP |

**Application:** Only enter if OB ranks 1–3. Discard OB rank 5.

---

## FVG Strength Ranking (v2)

Use only FVGs with strength 1–3 for entries:

| Strength | Description | Trade Approach |
|----------|-------------|---------------|
| 1 | 3+ consecutive FVGs (FVG cluster) | Maximum conviction |
| 2 | FVGs formed during displacement | High conviction |
| 3 | FVGs containing market structure shift | High conviction |
| 4 | FVGs at order blocks | Medium-High |
| 5 | FVGs at liquidity zones | Medium → Consider skipping |

**Application:** Only trade FVG strength 1–3. Standard FVGs (strength 5) produce lower win rates.

---

## Fibonacci OTE 70.5% (v2)

The optimal trade entry uses the precise 70.5% level (not 62%):

| Level | Fib | Description |
|-------|-----|-------------|
| OTE Primary | **70.5%** | ICT's core OTE level (0.618 + 0.087) |
| OTE Secondary | 61.8% | Standard Fibonacci retracement |
| OTE Tertiary | 78.6% | Extended Fib level |

**R8 Updated:** Replace "62% Fibonacci" with "70.5% OTE level" in confluence check.

---

## MSS as Alternate Entry (v2)

MSS does NOT require prior BOS — use as faster entry confirmation:

**Bullish MSS:**
- Price falls below extreme demand zone
- DOES NOT require prior bullish BOS
- Confirms order flow change → Valid entry signal

**Bearish MSS:**
- Price rises above extreme supply zone
- DOES NOT require prior bearish BOS
- Confirms order flow change → Valid entry signal

**Application:** If CHoCH doesn't form but MSS does → enter with reduced position (50%).