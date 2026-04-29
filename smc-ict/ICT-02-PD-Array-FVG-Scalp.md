# ICT Strategy 02: PD Array FVG Scalp
**Tier:** Scalping | **Models source:** #6, #8, #12 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, FVG Strength Ranking, Fibonacci OTE 70.5%, Daily/Weekly Loss Limits

---

## Concept

Trade the 25-pip intraday move after a fair value gap (FVG) forms on the 15M chart during a kill zone session. The gap represents institutional order absorption — price skipped over an inefficient zone, and that zone becomes support/resistance. Entry is a limit order at the FVG edge ±5 pips, with the 25-pip target as a weekly compounding goal.

**Edge basis:** FVGs form when institutional orders absorb opposing pressure, creating a price vacuum. Price returns to fill the inefficiency 85–90% of the time (10-year backtest). The gap's edge is where smart money placed resting orders — price must revisit to execute them.

---

## Instruments & Sessions

| Session | Kill Zone | Tradeable Pairs |
|---------|-----------|-----------------|
| London | 03:00–05:00 ET | EUR/USD, GBP/USD, EUR/GBP |
| New York AM | 08:30–11:00 ET | All majors |
| Asia (quiet) | 19:00–22:00 ET | USD/JPY, AUD/USD (low liquidity) |

*Best performance during NY AM kill zone — highest institutional volume.*

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Context | 60M | Define weekly bias, PD array location |
| Zone ID | 15M | Identify FVG, define dealing range |
| Entry | 5M | Micro-structure confirmation |
| Confirmation | 1M | Precise entry timing |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Weekend or day open)

**R1.** On the **60M chart**, determine weekly bias:
- Identify highest high and lowest low of the **last 20 trading days** (excluding weekends and Sundays).
- This defines the **Weekly Dealing Range**.
- If current price is above range midpoint → bias bullish; below → bias bearish.
- This is the **PD Array (Potential Distribution Array)** context.

**R2.** Calculate the **PD array terminus** (target zone):
- Bullish bias: terminus = area near lowest low of dealing range (discount).
- Bearish bias: terminus = area near highest high of dealing range (premium).
- Map both terminus zones on the chart — these are where price expansion will target.

**R3.** Note high-impact economic events on the calendar:
- Schedule volatility injections: events with potential to trigger range expansion.
- Classify as: **low** (< 10 pip expected move), **medium** (10–25 pips), **high** (25+ pips, e.g., NFP, FOMC).
- Trades are planned around medium/high events; high events are avoided for scalp entries.

**R4.** On the **15M chart**, define the **Dealing Range** for today:
- `DR High` = highest high of the last 20 trading days (same as weekly).
- `DR Low` = lowest low of the last 20 trading days (same as weekly).
- Note: this 20-day range is used across all ICT models for consistency.

---

### Phase 2 — Opportunity Discovery (During kill zone)

**R5.** Identify the **FVG signal** on the **15M chart**:
An FVG (Fair Value Gap) requires ALL three conditions on the same timeframe:

| Type | Condition |
|------|-----------|
| Bullish FVG | candle-2 high < candle-1 low (gap below candle-2) AND candle-3 high < candle-1 low |
| Bearish FVG | candle-2 low > candle-1 high (gap above candle-2) AND candle-3 low > candle-1 high |

- The gap must span ≥ 5 pips. Anything smaller is noise.
- FVG must form DURING the kill zone session (within kill zone time window).
- Price must be in a retrace from the opposite direction — confirming the gap was formed by institutional activity, not just a spike.

**R6.** Classify the FVG by location relative to PD array:
| Classification | Bullish FVG Location | Bearish FVG Location | Trade Direction |
|----------------|---------------------|---------------------|----------------|
| **Discount** | Below midpoint of dealing range | Above midpoint of dealing range | LONG (preferred) |
| **Premium** | Above midpoint of dealing range | Below midpoint of dealing range | SHORT (preferred) |
| **External** | Below DR Low | Above DR High | HIGH PROBABILITY |

- **Discount FVGs** → bias long (smart money buys where value exists).
- **Premium FVGs** → bias short (smart money sells where premium exists).
- **External FVGs** (beyond the range extremes) → highest conviction, as institutional targets are outside the retail dealing range.

**R7.** Check **confluence** — minimum 2 of 3:
- [ ] FVG is in discount (bullish) or premium (bearish) zone relative to PD array.
- [ ] FVG edge aligns within ±5 pips of a 62% Fibonacci retracement from the daily range high/low.
- [ ] Kill zone session is active (London or NY AM).

If ≥2 conditions met → valid setup. If <2 → discard.

**R8.** Filter by weekly bias alignment:
- Bullish weekly bias + bullish FVG in discount → **high conviction long**.
- Bearish weekly bias + bearish FVG in premium → **high conviction short**.
- Bullish weekly bias + bearish FVG in premium → valid short but reduce size.
- When bias and FVG direction disagree → only trade if external FVG (beyond range extremes).

---

### Phase 3 — Trade Execution

**R9. Entry order:**
- LONG: `buy limit` at `FVG bottom edge + 5 pips`.
- SHORT: `sell limit` at `FVG top edge − 5 pips`.
- **Validity window:** Order expires at end of kill zone + 30 min, OR at the next kill zone open, whichever comes first.

> **Offset justification (the ± 5 pips):**
> The 5-pip offset accounts for spread widening and broker slippage during kill zone volume. Without the offset, limit orders sit at the exact FVG edge and may be skipped when institutional flow hits. The offset places the order just inside/outside the zone, closer to where smart money's resting orders sit.

**R10. Stop loss:**
- LONG: `FVG bottom edge − 20 pips` (below the gap).
- SHORT: `FVG top edge + 20 pips` (above the gap).
- Minimum stop: 15 pips. If gap depth < 15 pips from entry → widen to 15 pips (accept higher risk).

**R11. Position sizing:**
```
Risk Amount ($) = Account Equity × 1%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Round DOWN.

**R12. Profit targets (Model #8 — 6% Monthly / 25-pip target):**

| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Entry ± 25 pips | 100% of position | Close immediately |
| (Alt) | Entry ± 15 pips | 100% of position | Only if kill zone about to close |

- Target 25 pips for weekly compounding goal. Reduce to 15 pips only in the final 30 min of the kill zone.
- Do NOT adjust target upward during the trade — set it and walk away.
- One trade per setup. After TP1 hit, wait for next FVG — do not re-enter same session.

---

### Phase 4 — Trade Management

**R13. Stop adjustment:**
| Condition | Action |
|----------|--------|
| Price at TP1 (25 pips profit) | Remove from chart — trade complete |
| Price retrace > 50% of TP1 without triggering | Move stop to breakeven |
| Price at 15M VWAP (key level) | Monitor for early exit signal |

**R14. Time-based exit:**
- If position is not within 10 pips of TP1 by kill zone close + 15 min → close at market.
- Do not hold scalp positions overnight — overnight exposure introduces HTF risk.

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | FVG forms outside kill zone session → discard (lower probability). |
| INV2 | FVG spans < 5 pips → discard (insufficient structural inefficiency). |
| INV3 | High-impact news in next 30 min → cancel order before news. |
| INV4 | Kill zone closes with no entry → cancel order. |
| INV5 | Price fills FVG in wrong direction (closes through gap entirely) → invalidate. |
| INV6 | Stop pip distance < 15 pips → skip trade. |
| INV7 | 3 consecutive losses in same session → stop trading that session. |

---

## Weekly Compounding Model (Model #8 Integration)

This strategy connects to a larger weekly compounding framework:

| Metric | Value |
|--------|-------|
| Weekly target | 25 pips per week (from Models #8/#9) |
| Monthly target | ~6% (compounded weekly) |
| Annual target | ~100% (doubling annually via compounding) |
| Trades per week | 1–3 high-quality setups |
| Max trades per session | 1 (discipline rule) |

> **Compounding logic:** With 1% risk per trade and a 25-pip target, consistent execution (~2 winning weeks per month) compounds to ~6% monthly. Missing weeks are absorbed by the 50% risk-reduction rule.

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 55–65% |
| Average R:R | 1:2 to 1:2.5 |
| FVG fill rate | 85–90% |
| Weekly setups | 1–3 |
| Annual drawdown target | < 8% |
| Best market fit | EUR/USD, GBP/USD, USD/JPY |

*Based on: FVG 85–90% fill rate (Backtrader 2024); 61% average WR across SMC strategies (Quantum Algo 2026).*

---

## Entry Checklist (quick-scan)

- [ ] Kill zone session identified
- [ ] Weekly bias confirmed on 60M chart
- [ ] DR high/low defined (last 20 trading days)
- [ ] FVG identified on 15M chart during kill zone (gap ≥ 5 pips)
- [ ] FVG classified: discount / premium / external
- [ ] Confluence ≥ 2/3 conditions met
- [ ] Weekly bias aligns with FVG direction (or external FVG confirmed)
- [ ] No high-impact news in next 30 min
- [ ] Kill zone still active
- [ ] Stop pip distance ≥ 15 pips
- [ ] Enter with limit order ± 5 pips from FVG edge

---

## Author Notes

Strategy #2 is the foundation of ICT's "bread and butter" approach — low-risk, high-frequency setups that compound weekly. It is intentionally simple: find the FVG, place the order, hit the target, walk away. The complexity is in the filter (R7–R8), not in the entry itself.

The weekly compounding model is the key insight. Many traders chase large wins; this strategy accepts 25 pips per week as the ceiling. The math is compelling: 25 pips × 4 weeks × 12 months = 300 pips annually. At 1% risk per trade, that's a 30% annual return in pure pip terms — before winning percentage is factored in. With 61% WR, the compounding effect is significant.

The discount/premium classification (R6) is derived from the equilibrium concept: smart money buys at discount (below fair value) and sells at premium (above fair value). This isn't arbitrary — it's the logic of any large institutional buyer who must accumulate or distribute large positions without moving price significantly. FVGs in discount zones represent accumulation; FVGs in premium zones represent distribution.

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
- Structure: BOS / CHOCH / MSS
- FVG Type: [Discount/Premium/External]
- Kill Zone: [London/NY/etc]
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

## FVG Strength Ranking (v2) — CRITICAL

Use only FVGs with strength 1–3 for entries. This is the PRIMARY filter for Strategy #02:

| Strength | Description | Trade Approach |
|----------|-------------|---------------|
| 1 | 3+ consecutive FVGs (FVG cluster) | **Maximum conviction** |
| 2 | FVGs formed during displacement | **High conviction** |
| 3 | FVGs containing market structure shift | **High conviction** |
| 4 | FVGs at order blocks | Medium-High |
| 5 | FVGs at liquidity zones | **SKIP — Low conviction** |

**Application:** Only trade FVG strength 1–3. Strength 5 = skip. This single filter dramatically improves win rate.

### FVG Validation Checklist (v2)
Before trading any FVG, confirm:
- [ ] FVG formed during displacement (Strength 2) OR contains MSS/CHoCH (Strength 3)
- [ ] NOT just a random price gap (Strength 5)
- [ ] FVG spans ≥ 5 pips
- [ ] Price bodies respect FVG (no complete violation)

---

## Fibonacci OTE 70.5% (v2)

The optimal trade entry uses the precise 70.5% level:

| Level | Fib | Description |
|-------|-----|-------------|
| OTE Primary | **70.5%** | ICT's core OTE level (0.618 + 0.087) |
| OTE Secondary | 61.8% | Standard Fibonacci retracement |
| OTE Tertiary | 78.6% | Extended Fib level |

**R6 Updated:** Use 70.5% OTE instead of generic "62% Fibonacci" for entry zone calculation.

---

## MSS as Faster Entry Alternative (v2)

MSS does NOT require prior BOS — use when FVG strength is 4–5 but MSS confirms:

**Bullish MSS:**
- Price falls below extreme demand zone
- CONFIRMS order flow change → Use as entry signal if FVG is weak

**Bearish MSS:**
- Price rises above extreme supply zone
- CONFIRMS order flow change → Use as entry signal if FVG is weak

**Application:** If FVG strength is 4–5 but MSS confirms → enter with reduced position (50% size).