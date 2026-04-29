# ICT Strategy 03: Kill-Zone Pulse
**Tier:** Short-term | **Models source:** #2, #5, #11 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, FVG Strength Ranking, Fibonacci OTE 70.5%, Daily/Weekly Loss Limits, MSS entry alternative

---

## Concept

Trade the 30–50 pip intraday expansion triggered by a kill zone session displacement. Price breaks the Asian / prior session range during London or NY open, creates a momentum candle with body ≥ 70% of range, then pulls back to the 50% VWAP equilibrium or the 62% Fibonacci retracement level — creating a high-probability entry. Target the opposing session's range extreme.

**Edge basis:** Kill zone sessions concentrate institutional order flow. A 70%+ body displacement candle is institutional activity, not retail noise. The retrace to VWAP or 62% is where resting orders sit. Target the opposing session's high/low captures the range expansion before it reverses.

---

## Kill Zone Definitions

| Zone | Session | Time (ET) | Volume | Best Pairs |
|------|---------|-----------|--------|------------|
| London | Early London | 03:00–05:00 | High | EUR/USD, GBP/USD |
| NY AM | New York Morning | 08:30–11:00 | Highest | All majors |
| NY PM | New York Afternoon | 13:00–15:00 | Medium | USD/JPY, USD/CAD |
| Asia | Asia Session | 19:00–22:00 | Low | AUD/USD, USD/JPY |

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Context | 60M | Weekly bias, PD array terminus |
| Setup ID | 15M | Range definition, VWAP, displacement |
| Entry | 5M | Retrace confirmation, limit order placement |
| Micro | 1M | Precise fill timing |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Day before or pre-session)

**R1.** On the **60M chart**, determine weekly bias:
- `Weekly High` = highest high of the last **20 trading days** (excluding weekends/Sundays).
- `Weekly Low` = lowest low of the last **20 trading days**.
- If current price > midpoint of weekly range → bias bullish.
- If current price < midpoint → bias bearish.

**R2.** Map the **kill zone range** on the **15M chart**:
- `KZR High` = highest high of the LAST completed kill zone session (not the current one).
- `KZR Low` = lowest low of the LAST completed kill zone session.
- These are the external liquidity targets for today.

**R3.** Draw the **50% VWAP line** on the 15M chart (multi-session VWAP, or use a 50 EMA as proxy if VWAP unavailable).

**R4.** Identify **upcoming volatility events**:
- Mark medium/high impact events on the calendar.
- Today's trade plan: target the session OPPOSITE to the next volatility event.
- Example: high-impact event at 10:00 ET → plan short during NY AM kill zone if price opens near KZR High.

**R5.** Define the **PD array** (Potential Distribution array):
- PD = the daily range zone price is expected to expand into.
- Bullish bias + NY AM kill zone → PD is above KZR High (targeting buy-side liquidity).
- Bearish bias + NY AM kill zone → PD is below KZR Low (targeting sell-side liquidity).

---

### Phase 2 — Opportunity Discovery (During kill zone)

**R6.** Monitor the **displacement candle** on the **15M chart**:
- A displacement candle must appear within the kill zone time window.
- It must open near one end of the KZR and close near (or through) the opposite end.
- **Body requirement:** The candle's body must be ≥ 70% of its full range (high–low).
- Body must be in the direction of the trade (bullish candle for longs, bearish for shorts).

**R7.** Confirm the displacement is institutional (not noise):
- [ ] Candle is on the 15M chart — no sub-15M confirmation needed at this stage.
- [ ] Body ≥ 70% of range — ensures institutional conviction.
- [ ] Candle closes within the kill zone time window (R5).
- [ ] No high-impact news occurred within 10 minutes before the candle opened.

If all 4 conditions met → displacement is valid.

> **On the 70% body rule:**
> A candle with body < 70% of its range has significant opposing pressure — institutions are fighting the move. This is not a clean institutional flow signal. The 70% threshold is derived from displacement analysis across multiple ICT backtests: setups below this threshold show statistically lower win rates.

**R8.** Wait for the **retrace** on the **5M chart**:
- After the displacement candle, price retraces.
- For longs: price retraces lower toward the VWAP line or the 62% Fibonacci retracement of the displacement move.
- For shorts: price retraces higher toward VWAP or the 62% retracement.

**R9.** Check **entry zone confluence**:
- [ ] Entry zone is at VWAP (15M) ± 5 pips, OR
- [ ] Entry zone is at 62% Fibonacci retracement of the displacement move ± 5 pips, OR
- [ ] Entry zone is at the FVG edge formed during the retrace.

If ≥ 2 conditions met → valid setup. If < 2 → discard.

---

### Phase 3 — Trade Execution

**R10. Entry order:**
- LONG: `buy limit` at `entry zone low + 5 pips`.
- SHORT: `sell limit` at `entry zone high − 5 pips`.

**R11. Stop loss:**
- LONG: `displacement candle low − 15 pips` (or 20 pips from entry, whichever is greater).
- SHORT: `displacement candle high + 15 pips` (or 20 pips from entry, whichever is greater).
- Minimum stop: 15 pips.

**R12. Position sizing:**
```
Risk Amount ($) = Account Equity × 1.5%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Risk increases to 1.5% for this tier (larger target = larger position justified).

---

### Phase 4 — Trade Management

**R13. Profit targets:**

| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Entry ± 30 pips | 80% of position | Close immediately |
| TP2 | Entry ± 50 pips | 20% of position | Trail stop on remainder |

- TP1 of 30 pips is the base target (matches Model #11).
- TP2 of 50 pips is the stretch goal — only pursue if momentum is strong.

**R14. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at 15 pips profit | Reduce stop by 5 pips toward entry |
| Price at 25 pips profit | Move stop to breakeven |
| Price at 35 pips profit | Move stop to +10 pips |
| Price at KZR High/Low | Close remainder immediately |

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Displacement candle body < 70% of range → no trade. |
| INV2 | High-impact news in next 30 min → cancel order. |
| INV3 | Price moves beyond KZR High/Low before retrace completes → invalidate (momentum ran). |
| INV4 | Kill zone closes without retrace entry → cancel order. |
| INV5 | Price re-trades the kill zone high/low in opposite direction → invalidate. |
| INV6 | Stop distance > 30 pips → skip (too wide for short-term). |
| INV7 | 3 consecutive losses → stop trading for the day. |

---

## Time-of-Day Filters

| Time Window | Action |
|------------|--------|
| 00:00–02:59 ET | No trades. No kill zone active. |
| 03:00–05:00 ET | London kill zone only. |
| 05:01–08:29 ET | No trades. Kill zones closed. |
| 08:30–11:00 ET | NY AM kill zone only (highest priority). |
| 11:01–12:59 ET | No trades. Kill zones closed. |
| 13:00–15:00 ET | NY PM kill zone only. |
| 15:01–18:59 ET | No trades. |
| 19:00–22:00 ET | Asia session (optional, lower priority). |
| 23:00+ | No trades. Day closed. |

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 58–65% |
| Average R:R | 1:2 to 1:3 |
| Daily opportunity rate | 1–2 |
| Target pip range | 30–50 pips |
| Max stop distance | 30 pips |
| Annual drawdown target | < 8% |
| Best market fit | EUR/USD, GBP/USD, USDCAD |

---

## Entry Checklist (quick-scan)

- [ ] Kill zone session identified
- [ ] Weekly bias confirmed on 60M chart
- [ ] KZR High/Low drawn on 15M chart from last kill zone session
- [ ] VWAP (or 50 EMA) drawn on 15M chart
- [ ] No high-impact news in next 30 min
- [ ] 15M displacement candle appears (body ≥ 70% of range) during kill zone
- [ ] Displacement confirmed institutional (no news 10 min prior)
- [ ] 5M retrace confirmed to entry zone
- [ ] Confluence ≥ 2/3 conditions met
- [ ] Kill zone still active
- [ ] Stop distance ≤ 30 pips
- [ ] Enter with limit order ± 5 pips from entry zone

---

## Author Notes

Strategy #3 is the "pulse" — it's a heartbeat pattern. Every kill zone session that has institutional participation will produce a displacement candle. You wait for the pulse (displacement), then enter the retrace. Simple, mechanical, and effective.

The 70% body rule is a filter that eliminates 40–50% of apparent setups. Most candles don't have institutional conviction. The ones that do are immediately identifiable: body fills almost the entire candle, closes near the extreme, and has little to no wick on the direction side. This is what institutional order flow looks like on a chart.

The 62% Fibonacci level is mathematically significant — it represents the 0.618 golden ratio retracement of the displacement move. Institutional algorithms target specific Fibonacci levels. When price retrace lands within 5 pips of 62% during a kill zone, it's a strong signal that the retrace is institutional in origin, not retail.

The 30/50 pip dual target (R13) reflects Model #11's structure but allows for Model #2's larger target. Taking 80% at TP1 locks profit; holding 20% for TP2 preserves the upside without overexposing capital.

---

## Enhanced Risk Management (v2)

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
**Timeframe:** 60M → 15M → 5M

**Setup:**
- HT Trend: BULLISH / BEARISH
- Structure Displacement: [70% body confirmed]
- OB/FVG: [Details]
- Kill Zone: [London/NY/etc]
- OB Quality Rank: [1-5]

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: 30 pips
- TP2: 50 pips
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
| 5 | OB without confluence | **SKIP** |

---

## FVG Strength Ranking (v2)

Use only FVGs with strength 1–3:

| Strength | Description | Trade Approach |
|----------|-------------|---------------|
| 1 | 3+ consecutive FVGs | **Maximum conviction** |
| 2 | FVGs formed during displacement | **High conviction** |
| 3 | FVGs containing MSS/CHoCH | **High conviction** |
| 4 | FVGs at order blocks | Medium-High |
| 5 | FVGs at liquidity zones | **SKIP — Low** |

---

## Fibonacci OTE 70.5% (v2)

Replace "62% Fibonacci" with precise 70.5% level:

| Level | Fib | Description |
|-------|-----|-------------|
| OTE Primary | **70.5%** | ICT core OTE |
| OTE Secondary | 61.8% | Standard Fib |
| OTE Tertiary | 78.6% | Extended |

**R8 Updated:** Use "70.5% OTE level" instead of "62% Fibonacci" for entry zone.

---

## MSS as Alternate Entry (v2) — CRITICAL

Strategy #03 now supports MSS as primary entry confirmation (faster than CHoCH):

**Bullish MSS:**
- Price falls below extreme demand zone on 15M
- DOES NOT require prior bullish BOS
- Confirms order flow change → **Valid entry signal**

**Bearish MSS:**
- Price rises above extreme supply zone on 15M
- DOES NOT require prior bearish BOS
- Confirms order flow change → **Valid entry signal**

**Entry Pathway (v2):**
| Pathway | Trigger | Position Size |
|---------|---------|--------------|
| Primary | Displacement confirmed + CHoCH | 100% |
| Alternate | Displacement confirmed + MSS (no CHoCH) | 75% |
| Fallback | Only displacement, no CHoCH/MSS | **SKIP** |

**Logic:** MSS confirms faster than CHoCH. If displacement + MSS but no CHoCH yet → enter at 75% size. If neither → skip.