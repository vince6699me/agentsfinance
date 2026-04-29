# ICT Strategy 05: CHoCH Momentum Swing
**Tier:** Swing | **Models source:** #3, #9, #10 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, Breaker Blocks, 4-Tier TP Structure, Daily/Weekly Loss Limits, MSS entry

---

## Concept

Trade the 75–100 pip swing after a Change of Character (CHoCH) confirms a trend shift on the 4H chart. CHoCH occurs when price breaks a structure high/low AND the subsequent retrace fails to reclaim it — confirming institutional commitment. Entry is a limit order at the 50% equilibrium retrace, with the 4H structure extremes as targets. Hold time: 2–5 trading days.

**Edge basis:** CHoCH is the highest-probability continuation signal in the SMC framework. It confirms the market has accepted a new equilibrium level — the break was not a fakeout but institutional flow. The retrace to the 50% level is where smart money re-enters after the initial displacement. Target the opposing 4H structure extreme captures the full swing move.

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Trend / Structure | 4H | CHoCH identification, structure extremes |
| Bias | Daily | Weekly dealing range, PD array terminus |
| Entry | 1H | Equilibrium retrace, VWAP alignment |
| Confirmation | 15M | Displacement confirmation, limit order |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Sunday or day open)

**R1.** On the **4H chart**, identify the **current structure sequence**:
- Find the most recent clear swing high and swing low.
- Label them consecutively: `Swing High 1` → `Swing Low 1` → `Swing High 2` → `Swing Low 2`.
- The structure alternates: each high is higher than the last high = bullish sequence.
- Each low is lower than the last low = bearish sequence.

**R2.** Identify the **CHoCH signal** on the **4H chart**:
CHoCH requires BOTH conditions:

| Type | Condition 1 | Condition 2 |
|------|------------|-------------|
| Bullish CHoCH | Price closes above last Swing High | Next retracement low stays above that Swing High |
| Bearish CHoCH | Price closes below last Swing Low | Next retracement high stays below that Swing Low |

- The break must be a **4H candle close** (not intraday spike).
- The subsequent retracement must NOT reclaim the broken level within 2–4 4H candles.
- CHoCH is confirmed only after the retracement completes, not at the moment of the break.

> **CHoCH vs. BOS distinction:**
> BOS (Break of Structure) is the initial break — it signals potential. CHoCH is the confirmation — it signals commitment. You never trade the BOS; you trade the CHoCH confirmation. The retracement creates the entry zone, which becomes the high-probability entry point.

**R3.** On the **Daily chart**, map the **weekly dealing range**:
- `Weekly High` = highest high of the last 20 trading days.
- `Weekly Low` = lowest low of the last 20 trading days.
- CHoCH direction should align with the weekly bias for highest probability.

**R4.** Define the **PD array terminus** and **target zones**:
- Bullish CHoCH → terminus = zone near Weekly High or above (premium targeting).
- Bearish CHoCH → terminus = zone near Weekly Low or below (discount targeting).
- These are the 4H structure extremes that define TP2.

---

### Phase 2 — Opportunity Discovery

**R5.** Wait for the **CHoCH confirmation** (R2 conditions met):
- The CHoCH candle closes on the 4H chart.
- The subsequent 1–2 retracement candles confirm the level is defended.
- Do not enter at the moment of the CHoCH break — wait for retrace.

**R6.** On the **1H chart**, identify the **equilibrium entry zone**:
- Bullish CHoCH: entry zone = the 50% retracement of the CHoCH displacement move, near VWAP on 1H.
- Bearish CHoCH: entry zone = the 50% retracement of the CHoCH displacement move, near VWAP on 1H.
- The 50% level is the equilibrium — where the market "decided" to break.

**R7.** Check **confluence** — minimum 3 of 4:
- [ ] CHoCH confirmed on 4H chart (not just BOS).
- [ ] Entry zone at 50% retrace within ±10 pips of 1H VWAP.
- [ ] Weekly bias aligns with CHoCH direction.
- [ ] CHoCH target zone (Weekly High/Low) is ≥ 50 pips from entry.

If ≥ 3 conditions met → valid setup.

---

### Phase 3 — Trade Execution

**R8. Entry order:**
- LONG: `buy limit` at `entry zone low + 5 pips`.
- SHORT: `sell limit` at `entry zone high − 5 pips`.
- **Validity:** Order expires after 4 4H candles (2 trading days). If not filled → cancel and reassess.

**R9. Stop loss:**
- LONG: `below CHoCH retracement low − 25 pips`.
- SHORT: `above CHoCH retracement high + 25 pips`.
- Minimum stop: 25 pips. Maximum stop: 50 pips.
- Stop must be OUTSIDE the CHoCH level — not too close (whipsaws), not too far (poor R:R).

**R10. Position sizing:**
```
Risk Amount ($) = Account Equity × 2%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Risk increases to 2% for swing tier (longer hold time = larger position justified).

---

### Phase 4 — Trade Management

**R11. Profit targets:**

| Leg | Target | Size | Basis |
|-----|--------|------|-------|
| TP1 | Entry ± 75 pips | 50% of position | CHoCH move magnitude |
| TP2 | Entry ± 100 pips | 30% of position | 4H structure extreme |
| TP3 | At PD array terminus | 20% of position | Weekly range target |

- TP3 (weekly terminus) is optional — only pursue if weekly bias is strong and no HTF resistance is near.
- TP1 is the minimum target. If price stalls at TP1 for more than 2 candles → close 50% there.

**R12. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at 40 pips profit | Move stop to breakeven |
| Price at 60 pips profit | Move stop to +20 pips |
| Price at 4H structure extreme | Close 30% remainder here |
| Price at Weekly High/Low (TP3) | Close all remaining |

---

## Holding Period & Time Rules

| Phase | Duration | Rule |
|------|---------|------|
| Entry window | Up to 4 4H candles (2 days) | Must enter or cancel |
| Holding period | Up to 10 4H candles (5 days) | Monitor for TP or invalidation |
| Extended hold | Beyond 5 days | Only if TP2 approaching, no opposing HTF structure |

> **5-day holding rule:** If the position has not reached TP1 within 5 trading days, evaluate whether the setup is still valid. CHoCH setups that don't move within 5 days often invalidate — the market may be consolidating. Close at breakeven and move on.

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Only BOS confirmed (no retracement confirmation) → no entry. |
| INV2 | Weekly bias contradicts CHoCH direction → no trade. |
| INV3 | CHoCH target < 50 pips from entry → insufficient room; skip. |
| INV4 | Stop distance > 50 pips → too wide for swing. |
| INV5 | Price reclaims the CHoCH level within 2 4H candles → CHoCH invalidated, no trade. |
| INV6 | 5 consecutive swing losses → skip next week, review rules. |
| INV7 | NFP week: CHoCH forms → skip trade (hold over NFP too risky). |

---

## CHoCH vs. Market Structure Shift (MSS) Distinction

| Signal | Chart | Confirmation | Trading Approach |
|--------|-------|---------|--------------|
| **BOS** | 4H | Initial break of swing high/low | Observe only — do not enter |
| **CHoCH** | 4H | Break + retracement fails to reclaim | Enter on retrace |
| **MSS** | 15M | Lower-high (short) or higher-low (long) on 15M | Enter for faster/shorter-term swing |

- Trade CHoCH for 2–5 day swings (primary approach for this strategy).
- MSS is a faster variant — trade it on 15M for 1–2 day swings with smaller position size.
- MSS validity window: only trade if 15M chart shows clear MSS within the kill zone session.

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 60–68% |
| Average R:R | 1:3 to 1:5 |
| Holding period | 2–5 trading days |
| Target pip range | 75–100 pips |
| Weekly setups | 1–3 |
| Annual drawdown target | < 10% |
| Best market fit | EUR/USD, GBP/USD, XAU/USD |

*Based on: 72% of impulsive moves > 100 pips captured by CHoCH (Backtrader 5-year GBP/USD); 64.2% XAU/USD WR (Quantum Algo 2026).*

---

## Entry Checklist (quick-scan)

- [ ] 4H chart: structure sequence identified (swing highs/lows labeled)
- [ ] 4H chart: CHoCH confirmed (not just BOS)
- [ ] Daily chart: weekly dealing range mapped
- [ ] Weekly bias aligns with CHoCH direction
- [ ] 1H chart: equilibrium entry zone at 50% retrace + VWAP
- [ ] TP target ≥ 50 pips from entry
- [ ] Stop distance ≤ 50 pips
- [ ] Favorable macro / weekly calendar (no opposing high-impact events)
- [ ] Enter with limit order ± 5 pips from entry zone

---

## Author Notes

CHoCH is the most underutilized signal in the ICT framework — most traders react to the BOS break and enter immediately, only to get stopped out when the "real" move hasn't confirmed. CHoCH demands patience: wait for the break, wait for the retrace, then enter. This 2-step confirmation eliminates the majority of false breakouts.

The 50% equilibrium entry is derived from market equilibrium theory: after a directional displacement, price returns to the midpoint to test the new balance of power. Smart money uses this level to add to positions. The 1H VWAP at this level confirms institutional alignment.

The CHoCH vs. MSS distinction is critical for framework implementation. CHoCH on 4H captures the macro swing (75–100 pips, 2–5 days). MSS on 15M captures the micro swing (30–50 pips, 1–2 days). Both are valid, but they have different risk profiles and holding periods. The agent must know which timeframe it's tracking.

The 2% risk (vs. 1–1.5% for shorter tiers) is justified by the longer holding period. The position is held overnight and over weekends, which introduces gap risk. Larger stops (25–50 pips) and larger position sizing (2%) maintain the same capital efficiency while accounting for overnight noise.

---

## Enhanced Risk Management (v2)

### Daily/Weekly Loss Limits (v2)
| Limit Type | Specification | Action When Hit |
|-----------|--------------|----------------|
| **Daily Loss Limit** | 5% of account | Stop trading for the day |
| **Weekly Loss Limit** | 10% of account | Skip next week's swing trades |
| Max Concurrent Trades | 3 positions | No new entries |

### Trade Log Template (v2)
```markdown
## Trade #___

**Date:** YYYY-MM-DD
**Pair:** XXXYYY
**Direction:** LONG / SHORT
**Timeframe:** 4H → 1H → 15M

**Setup:**
- HT Trend: BULLISH / BEARISH
- Structure: CHoCH / MSS
- OB Quality Rank: [1-5]
- OB/FVG Details: [Location]
- Kill Zone: [London/NY/etc]

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: 75 pips
- TP2: 100 pips
- TP3: Weekly extreme
- Risk: _______ R

**Result:**
- Outcome: WIN / LOSS / BE
- P&L: _______
- R-multiple: _______

**Notes:**
- [Observations]
```

---

## 4-Tier Take Profit Structure (v2)

Replace dual TP with 4-tier structure:

| Target | R-Multiple | Position Action |
|--------|-----------|--------------|
| TP1 | 1R | Break even on full lot |
| TP2 | 1.5R–2R | Partial exit 50% |
| TP3 | 3R | Trailing stop activated |
| TP4 | Structure extreme | Full exit |

**Updated R11:**
| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | 1R | 30% | Move stop to breakeven |
| TP2 | 2R | 30% | Lock profit |
| TP3 | 3R | 20% | Activate trailing stop |
| TP4 | Structure extreme | 20% | Final exit |

---

## Order Block Quality Ranking (v2)

Use OB ranks 1–3 (rank 4 acceptable for swing):

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount/premium with CHoCH | **Highest** |
| 2 | OB with FVG | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB at structure level | **Acceptable** |
| 5 | OB without confluence | **SKIP** |

---

## Breaker Blocks (v2) — NEW

Strategy #05 now includes Breaker Block entries:

**Bullish Breaker Block:**
- Was a bullish order block
- Price broke below it (failed)
- Price now returning from below
- Expect reversal to upside → **Enter long**

**Bearish Breaker Block:**
- Was a bearish order block
- Price broke above it (failed)
- Price now returning from above
- Expect reversal to downside → **Enter short**

### Breaker Block Entry Rules
```
Bullish Breaker:
- Entry: Buy limit at breaker top + 5 pips
- Stop: Below breaker low − 10 pips
- Target: Next supply zone

Bearish Breaker:
- Entry: Sell limit at breaker bottom − 5 pips
- Stop: Above breaker high + 10 pips
- Target: Next demand zone
```

---

## Fibonacci OTE 70.5% (v2)

Replace "50%" with 70.5% OTE:

| Level | Fib |
|-------|-----|
| **OTE Primary** | **70.5%** |
| OTE Secondary | 61.8% |

**R6 Updated:** Use 70.5% OTE instead of 50% for equilibrium entry.

---

## MSS vs CHoCH Dual-Path Entry (v2)

| Signal | Requires Prior BOS | Position Size | Holding Period |
|--------|--------------|-------------|-------------|
| **CHoCH** | Yes (after BOS) | 100% | 2–5 days |
| **MSS** | No | 75% | 1–2 days |

**Logic:**
- If CHoCH confirms → enter at 100% size
- If MSS (no CHoCH yet) → enter at 75% size
- If neither → skip