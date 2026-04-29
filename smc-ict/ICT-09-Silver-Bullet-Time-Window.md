# ICT Strategy 09: Silver Bullet Time-Window Setup
**Tier:** Scalping / Short-term Hybrid | **Models source:** #1, #2, #3, Silver Bullet | **Created:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, FVG Strength Ranking, Fibonacci OTE 70.5%, Daily/Weekly Loss Limits

---

## Concept

The **ICT Silver Bullet** is a **time-based algorithmic model** — setups form within specific 60-minute windows daily, not at just any price level. It combines liquidity draws with time-synchronized priceaction to produce high-probability setups. The key innovation is the **minimum movement framework**: trades are only taken if the target move is at least 15 pips (Forex) or 10 handles/points (futures).

**Edge basis:** The 60-minute window concentrates institutional activity. Unlike discretionary setups that may form anywhere, Silver Bullet setups only exist during specific hours when institutional algorithms deploy capital. This creates a natural filter that dramatically increases setup quality. The time window is not the trade duration — it's the setup formation window. The trade can extend well beyond it.

---

## Minimum Movement Framework

| Asset Class | Minimum Target | Equivalency |
|------------|---------------|-------------|
| Forex pairs | ≥ 15 pips | — |
| Index futures | ≥ 10 handles (points) | ≈ 20 pips |
| E-mini S&P | ≥ 5 handles | ≈ 10 pips |
| Crypto | ≥ 15 pips (or %) | Similar to Forex |

> **Filter rule:** If the setup's potential move is below the minimum framework → **do not trade**. This is the highest-probability filter.

---

## Three Silver Bullet Windows

| Setup | Time Window (NY Local) | Best Markets | Direction | Pattern Type |
|-------|----------------------|--------------|-----------|-------------|
| Silver Bullet #1 | 3:00 a.m. – 4:00 a.m. | Futures, Forex (London) | Bearish | FVG (premium) |
| Silver Bullet #2 | 10:00 a.m. – 11:00 a.m. | E-mini S&P, indices | Bearish | FVG (premium) |
| Silver Bullet #3 | 2:00 p.m. – 3:00 p.m. | Futures, Forex (PM) | Bullish | FVG (discount) |

*Times are New York local. Adjust for DST.*

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Context | 60M / 4H | Weekly bias, liquidity targets |
| Setup ID | 15M | FVG identification, structure shift |
| Entry | 5M | Entry confirmation within window |
| Confirmation | 1M | Precise fill timing |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Before window opens)

**R1.** Identify today's **active Silver Bullet window**:
- London Open: 3:00–4:00 AM (Focus: futures, EUR pairs)
- AM Session: 10:00–11:00 AM (Focus: indices)
- PM Session: 2:00–3:00 PM (Focus: futures, continuation)

**R2.** Identify **liquidity draws** on the **15M chart** (in priority order):

| Priority | Liquidity Type | Description |
|----------|--------------|-------------|
| 1 | Previous day high/low | Primary intraday target |
| 2 | Previous session high/low | London, Asian, prior sessions |
| 3 | Previous weekly high/low | Weekly context |
| 4 | Week open gap | Gap from Sunday/Monday open |
| 5 | Fair Value Gap | Market inefficiency (if present) |

- Map top 3 liquidity draws on the chart.

**R3.** Determine **weekly bias** on the **60M chart**:
- Price above 20-day midpoint → bias bullish (Silver Bullet #3 favored)
- Price below 20-day midpoint → bias bearish (Silver Bullet #1/#2 favored)
- Bias and window direction should align.

**R4.** Check for **minimum movement** potential:
- Calculate: entry zone → nearest liquidity draw (target)
- Bullish: target must be ≥ 15 pips above entry
- Bearish: target must be ≥ 15 pips below entry
- If < 15 pips potential → **skip setup**

---

### Phase 2 — Setup Formation (During 60-minute window)

**R5.** Monitor for **Silver Bullet pattern** within the active window:

**For Silver Bullet #1 / #2 (Bearish):**

| Condition | Requirement |
|-----------|-------------|
| FVG forms | Bearish FVG (gap above price) between 10:00-11:00 (or 3:00-4:00) candle range |
| Structure shift | Price below a recent swing low on 15M |
| Liquidity draw | Sell-side liquidity below recent equal lows |
| Price body | Bodies stay inside/in the FVG (wicks may exceed), confirming support |
| Potential | ≥ 10 handles (futures) or ≥ 15 pips (Forex) to target |

**For Silver Bullet #3 (Bullish):**

| Condition | Requirement |
|-----------|-------------|
| FVG forms | Bullish FVG (gap below price) between 2:00-3:00 candle range |
| Structure shift | Price above a recent swing high on 15M |
| Liquidity draw | Buy-side liquidity above recent equal highs |
| Price body | Bodies stay inside/in the FVG, confirming support |
| Potential | ≥ 12 handles (futures) or ≥ 15 pips (Forex) to target |

> **Body validation rule:** Price bodies (not wicks) must stay inside or respect the FVG. If bodies violate the FVG completely → setup is invalidated.

**R6.** Check **confluence** — minimum 3 of 4:

- [ ] FVG forms within the 60-minute window (time-synchronized)
- [ ] Structure shift confirms direction (MSS or CHoCH on 15M)
- [ ] Liquidity draw identified (< 15 pips from entry)
- [ ] Weekly bias aligns with trade direction

If ≥ 3 conditions met → valid Silver Bullet setup.

---

### Phase 3 — Trade Execution

**R7. Entry order:**
- BEARISH: `sell limit` at `FVG top edge − 5 pips`.
- BULLISH: `buy limit` at `FVG bottom edge + 5 pips`.
- **Validity:** Order expires at window close + 30 minutes.

> **Window close rule:** The entry MUST occur within or before the window closes. Entries outside the 60-minute window are not Silver Bullet setups — they are regular ICT setups and should be traded with different rules.

**R8. Stop loss:**
- BEARISH: `above FVG high + 15 pips`.
- BULLISH: `below FVG low − 15 pips`.
- Minimum stop: 10 pips (futures) / 15 pips (Forex). Maximum stop: 25 pips.

**R9. Position sizing:**
```
Risk Amount ($) = Account Equity × 1%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```

---

### Phase 4 — Trade Management

**R10. Profit targets:**

| Leg | Target | Size | Basis |
|-----|--------|------|-------|
| TP1 | Minimum framework (15 pips / 10 handles) | 80% | Lock minimum profit |
| TP2 | Liquidity draw target | 20% | Full draw capture |

- **TP1 is non-negotiable.** Reaching the minimum framework is the setup's purpose.
- TP2 is the stretch target if momentum is strong.

**R11. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at TP1 (minimum target) | Move stop to breakeven |
| Price 5 pips from liquidity draw | Close 20% remainder |
| Window closes + 60 min with no TP1 | Close at market |

---

## Special Rules

**R12. Window failure rule:**
- If no valid Silver Bullet setup forms during a window → **do not force a trade**.
- Wait for the next window. Not all windows produce setups every day.
- This is by design, not failure.

**R13. Multi-window trade rule:**
- A trade entered in one window may hold through subsequent windows.
- If entering during PM window but price action suggests extending to next window → hold.
- Stop management remains the same.

**R14. Specialization recommendation:**
- Master ONE window first (e.g., AM session for indices).
- Do not attempt all three until consistent profitability is achieved.
- Specialization leads to mastery.

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | FVG forms outside the 60-minute window → not a Silver Bullet setup. |
| INV2 | Price bodies violate FVG completely → setup invalid. |
| INV3 | Minimum movement potential < 15 pips (Forex) / 10 handles (futures) → skip. |
| INV4 | No structure shift (BOS/CHOCH/MSS) on 15M → skip. |
| INV5 | Entry does not occur by window close + 30 min → cancel. |
| INV6 | 3 consecutive Silver Bullet losses → skip next window, review rules. |

---

## Comparison: Silver Bullet vs. Regular ICT Setups

| Attribute | Silver Bullet | Regular ICT |
|-----------|-------------|------------|
| **Formation** | Time-synchronized (specific hour) | Price-synchronized (any time) |
| **Filter** | Minimum movement framework | FVG/OB/Liquidity |
| **Frequency** | 0–3 per day (one per window) | Multiple per day |
| **Win rate** | Higher (due to time filter) | Lower (more setup variety) |
| **Entry window** | Strict 60-min window | Kill zone (broader) |
| **Edge source** | Institutional time deployment | Price structure |

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 60–70% |
| Average R:R | 1:2 to 1:3 |
| Setup frequency | 0–3 per day |
| Target pip range | 15–30 pips |
| Annual drawdown target | < 8% |

*Based on: Silver Bullet "highly consistent and extremely high probability" (ICT); time-filtered setups show highest conviction.*

---

## Entry Checklist (quick-scan)

- [ ] Active Silver Bullet window identified
- [ ] Liquidity draws mapped (top 3)
- [ ] Weekly bias aligns with setup direction
- [ ] Minimum movement ≥ 15 pips / 10 handles
- [ ] FVG confirmed inside the 60-minute window
- [ ] Structure shift confirmed on 15M
- [ ] Price bodies respect (don't violate) the FVG
- [ ] Confluence ≥ 3/4 conditions met
- [ ] Entry placed at FVG edge ± 5 pips
- [ ] Order valid until window close + 30 min

---

## Author Notes

The Silver Bullet is unique in the ICT framework because it's **time-synchronized first, price-synchronized second**. Most ICT traders focus on price structure and use kill zones for timing. Silver Bullet inverts this: the time window is the primary filter, price structure is secondary.

The minimum movement framework (R4) is the highest-value rule. Many setups are tradeable but not worth trading if the target move is only 8–10 pips. The minimum framework filters these out automatically.

The "do not force" rule (R12) is psychologically difficult but critical. Silver Bullet setups don't appear every window, every day. Accepting this is essential for long-term performance. The setups that do form are high-conviction specifically because they require specific time+price conditions.

The specialization recommendation (R14) follows ICT's own advice. Master the AM session for indices before expanding to other windows. The patterns are consistent — but reading them well requires focused practice.

---

## Enhanced Risk Management (v2)

### Daily/Weekly Loss Limits (v2)
| Limit Type | Specification | Action When Hit |
|-----------|--------------|----------------|
| **Daily Loss Limit** | 5% of account | Stop trading for the day |
| **Weekly Loss Limit** | 10% of account | Skip next week's windows |
| Max Concurrent Trades | 3 positions | No new entries |
| Windows per day | 3 max | One per window |

### Trade Log Template (v2)
```markdown
## Trade #___

**Date:** YYYY-MM-DD
**Window:** [London 3-4 / AM 10-11 / PM 2-3]
**Pair:** XXXYYY
**Direction:** LONG / SHORT
**Timeframe:** 15M → 5M → 1M

**Setup:**
- Silver Bullet Window: [Number]
- FVG Strength: [1-5]
- Liquidity Draw: [Type]
- Kill Zone: [Active]
- Min Movement: [≥15 pips confirmed]

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: 15 pips
- TP2: Liquidity draw
- Risk: _______ R

**Result:**
- Outcome: WIN / LOSS / BE
- P&L: _______
- R-multiple: _______

**Notes:**
- [Window evaluation]
```

---

## FVG Strength Ranking (v2) — CRITICAL

Silver Bullet RELIES on FVG. Apply strength ranking strictly:

| Strength | Description | Trade Approach |
|----------|-------------|-------------|
| 1 | 3+ consecutive FVGs in window | **Maximum — Enter** |
| 2 | FVG during displacement | **High — Enter** |
| 3 | FVG containing MSS | **High — Enter** |
| 4 | FVG at order block | Medium — Enter at 75% |
| 5 | Random FVG | **SKIP** |

---

## Order Block Quality Ranking (v2)

If entering at OB (not pure FVG):

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount/premium with CHoCH | **Highest** |
| 2 | OB with FVG | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB | **Acceptable** |
| 5 | OB without confluence | **SKIP** |

---

## Fibonacci OTE 70.5% (v2)

For Silver Bullet entries near OB, use precise 70.5%:

| Level | Fib |
|-------|-----|
| **OTE Primary** | **70.5%** |
| OTE Secondary | 61.8% |

**R7/8 Updated:** If entering at OB, use 70.5% OTE zone.

---

## 4-Tier Take Profit Structure (v2)

| Target | R-Multiple | Position Action |
|--------|-----------|--------------|
| TP1 | 1R | Break even on full lot |
| TP2 | 1.5R–2R | Partial exit 80% |
| TP3 | 3R | Trailing stop |
| TP4 | Liquidity draw | Full exit |

**Updated R10:**
| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Min framework | 60% | Lock base profit |
| TP2 | 1.5R | 20% | Secure + |
| TP3 | Liquidity draw | 20% | Trail stop |