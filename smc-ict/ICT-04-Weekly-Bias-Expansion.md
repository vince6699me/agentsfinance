# ICT Strategy 04: Weekly Bias Expansion
**Tier:** Short-term | **Models source:** #2, #8, #9 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, FVG Strength Ranking, Fibonacci OTE 70.5%, Daily/Weekly Loss Limits, MSS entry

---

## Concept

Trade the 50-pip intraday expansion aligned with the weekly bias, using the Monday–Wednesday setup window. The strategy identifies the weekly dealing range structure, waits for Monday's range to form, then trades Tuesday or Wednesday when price displaces toward the weekly target during the NY AM kill zone. Combines with the 6% monthly compounding model for position sizing.

**Edge basis:** Markets establish bias early in the week. Monday is range-building; Tuesday and Wednesday are expansion days. Trading the expansion aligned with the HTF bias captures the highest-probability directional move. ICT's own analysis confirms Tuesday and Wednesday produce the best setups — Monday patterns are unreliable due to weekend gap fills.

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| HTF Bias | Weekly (D) | Weekly dealing range, bias direction |
| Setup ID | 4H | Range extremes, PD array terminus |
| Entry | 15M | Kill zone structure, VWAP alignment |
| Confirmation | 5M | Displacement + retrace confirmation |

---

## Weekly Calendar Model

| Day | Primary Activity | Trade Rule |
|----|----------------|-----------|
| **Monday** | Range-building, weekend gap fill analysis | Observe only. No entries. Identify the Monday range extremes. |
| **Tuesday** | Range expansion (highest probability) | Trade setups aligned with weekly bias. |
| **Wednesday** | Range expansion (high probability) | Trade setups aligned with weekly bias. Second-chance opportunities from Monday. |
| **Thursday** | Trend continuation / reversal | Trade against Thursday closes only if HTF structure confirms. |
| **Friday** | NFP preparation, early close | Avoid high-impact news days. Reduced volume. |

> **Monday observation rule:** ICT's own 30+ years of analysis confirms Monday is the least reliable day for ICT-style entries. Weekend gaps create misleading range extremes. Use Monday to map the developing weekly range, not to trade it.

---

## Step-by-Step Rules

### Phase 1 — Preparation (Sunday evening or Monday morning)

**R1.** Analyze the **weekly chart (D or 4H)**:
- Identify `Weekly High` and `Weekly Low` of the last completed weekly candle.
- If current week has no structure yet → use last 4 completed weeks' range.
- Calculate `Weekly Midpoint` = (Weekly High + Weekly Low) / 2.
- Current price vs. midpoint → weekly bias (bullish if above, bearish if below).

**R2.** Map the **PD array terminus**:
- Bullish bias: terminus = zone near Weekly Low or below (discount level).
- Bearish bias: terminus = zone near Weekly High or above (premium level).
- Price discovery array = the zone where weekly expansion will terminate.

**R3.** Note the **Monday range** (observe, don't trade):
- On Monday, track the developing range: `Monday High` and `Monday Low`.
- This range will likely be INSIDE the weekly range — it's building structure.
- If Monday breaks below Weekly Low or above Weekly High → watch for external liquidity targeting on Tuesday.

**R4.** Schedule the **weekly trade plan**:
- Target 1–2 setups per week (per Model #8's discipline rule).
- Days: Tuesday or Wednesday preferred.
- Sessions: NY AM kill zone (08:30–11:00 ET) only for this tier.
- Pip target: 50 pips per trade.

---

### Phase 2 — Opportunity Discovery (Tuesday or Wednesday, pre-kill zone)

**R5.** Confirm the **Monday range** and **Tuesday development**:
- `Monday Range High` = highest high of Monday's candle.
- `Monday Range Low` = lowest low of Monday's candle.
- `Tuesday Open` = Tuesday's 08:30 ET candle open on the 15M chart.

**R6.** Determine bias alignment:
- Bullish weekly bias + price above Monday range midpoint → look for longs on Tuesday.
- Bearish weekly bias + price below Monday range midpoint → look for shorts on Tuesday.
- Bias and Monday structure disagree → NO trade until Wednesday or Thursday.

**R7.** Identify the **entry target zone** on the **15M chart**:
- For longs: discount zone = area near the lower half of the Monday–Tuesday developing range, below VWAP.
- For shorts: premium zone = area near the upper half of the developing range, above VWAP.
- Zone must be ≥ 15 pips away from current price to allow for a valid stop.

**R8.** Check **confluence** — minimum 3 of 4:
- [ ] Weekly bias aligns with trade direction.
- [ ] Entry zone is in discount (long) or premium (short) relative to Monday's developing range.
- [ ] Entry zone is at or within 5 pips of the 62% Fibonacci retracement of the Monday range move.
- [ ] No high-impact news in next 60 minutes.

If ≥ 3 conditions met → valid setup.

---

### Phase 3 — Trade Execution

**R9. Entry order:**
- LONG: `buy limit` at `entry zone low + 5 pips`.
- SHORT: `sell limit` at `entry zone high − 5 pips`.
- **Validity:** Order expires at 11:00 ET (kill zone close) if not filled.

**R10. Stop loss:**
- LONG: `below Monday Range Low − 20 pips`.
- SHORT: `above Monday Range High + 20 pips`.
- Minimum stop: 20 pips (this tier requires more room than scalping).

**R11. Position sizing (6% Monthly Framework):**
```
Risk Amount ($) = Account Equity × 1%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
Target per trade: 50 pips = 50 × pip_value × position_size
Weekly target: 50 pips per week (1 setup)
Monthly target: ~6% (compounded)
```
Example: $10,000 account, 1% risk = $100, 20-pip stop → 5 mini lots.
50 pips × $1 × 5 = $250 profit on 1% risk = 2.5R expectancy per trade.

---

### Phase 4 — Trade Management

**R12. Profit targets:**

| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Entry ± 50 pips | 80% of position | Close immediately |
| TP2 | Entry ± 75 pips | 20% of position | Trail stop on remainder |

- The 50-pip primary target is the key differentiator from scalp strategies.
- The 75-pip secondary target captures extensions aligned with weekly bias.
- Scaled exit preserves the compounding model while allowing upside.

**R13. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at 25 pips profit | Reduce stop by 10 pips toward entry |
| Price at 40 pips profit | Move stop to breakeven |
| Price at 60 pips profit | Move stop to +15 pips |
| Price at Weekly High/Low | Close remainder immediately |

---

## Risk Management Framework (from Model #8 / #9)

**Dynamic position sizing:**
- After 1 full-loss trade: reduce risk to 50% of base ($0.5%) until 50% of the loss is recovered.
- After 5 consecutive winning trades: reduce risk to 50% to protect equity.
- After 3 consecutive losses: skip the next session, review the rules.

**Equity smoothing targets:**
- Target monthly return: 6% (compounded weekly).
- Max drawdown per month: 4%.
- Max daily drawdown: 1.5%.
- If daily drawdown exceeds 1.5% → stop trading for the day.

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Monday is used for observation only. No entries on Monday. |
| INV2 | Tuesday setup contradicts weekly bias → no trade. |
| INV3 | High-impact news in next 60 min → cancel order. |
| INV4 | Kill zone closes without entry → cancel order. |
| INV5 | Price moves > 100 pips in opposite direction of bias on Tuesday → weekly bias may have shifted; skip Wednesday and reassess. |
| INV6 | Stop distance > 35 pips → skip (too wide for short-term). |
| INV7 | More than 1 setup already taken this week → no additional trades. |

---

## Time-of-Week Filters

| Day | Trade Permission |
|-----|---------------|
| Sunday | No trades. Prepare weekly analysis. |
| Monday | Observe only. Map weekly and Monday range. |
| Tuesday | ✅ Primary trade day. Bias-aligned kills only. |
| Wednesday | ✅ Secondary trade day. Bias-aligned kills only. |
| Thursday | ⚠️ Conditional. Only if Wednesday did not produce setup and Thursday close confirms bias. |
| Friday | ❌ Avoid. NFP, early close, reduced institutional volume. |

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 58–65% |
| Average R:R | 1:2.5 to 1:3.75 |
| Trades per week | 1–2 |
| Target pip range | 50–75 pips |
| Monthly target | ~6% (compounded) |
| Annual target | ~100% (doubling via compounding) |
| Best market fit | EUR/USD, GBP/USD, USD/JPY |

*Based on: 6% monthly target from Model #8 (ICT); 61% average WR across SMC (Quantum Algo 2026); 68% H4 WR on EUR/USD (Myfxbook 2024).*

---

## Entry Checklist (quick-scan)

- [ ] Day is Tuesday or Wednesday
- [ ] Weekly bias confirmed on weekly/4H chart
- [ ] Monday range mapped on 15M chart
- [ ] Bias aligns with trade direction
- [ ] Entry zone identified in discount/premium relative to Monday range
- [ ] 62% Fibonacci confluence confirmed
- [ ] No high-impact news in next 60 min
- [ ] Kill zone (NY AM) active
- [ ] Stop distance ≤ 35 pips
- [ ] No more than 1 setup taken this week
- [ ] Enter with limit order ± 5 pips from entry zone

---

## Author Notes

Strategy #4 is the weekly compounding vehicle. Its power is in the constraint: 1 setup per week, 50 pips, disciplined exit. Most traders fail because they overtrade. This strategy forces patience by making Tuesday and Wednesday the only game days.

The Monday observation rule (R3) is counterintuitive — many want to trade Monday. ICT's own data (30 years) shows Monday is the lowest-quality day for ICT setups. The range isn't established yet, weekend gaps create false structure, and institutional participation is lower. Using Monday as a mapping day rather than a trading day is one of the highest-value rules in this entire strategy set.

The 62% Fibonacci level here (R8) serves the same function as in Strategy #3: it's a mathematically precise entry zone that institutional algorithms target. When all three confluence conditions (bias, zone, Fibonacci) align, the setup is institutional-grade. When fewer than 3 align, it's retail-grade and should be skipped.

The weekly target of 50 pips is achievable in 1–2 trades per week. Compounding at 1% risk × 2.5R expectancy = 2.5% per winning trade. Even at a 50% win rate, that's 1.25% per trade × 2 trades = 2.5% weekly. Four weeks = 10% monthly before the 50% risk-reduction rule. ICT's 6% monthly target is conservative — it's designed to be achievable even in difficult weeks.

---

## Enhanced Risk Management (v2)

### Daily/Weekly Loss Limits (v2)
| Limit Type | Specification | Action When Hit |
|-----------|--------------|----------------|
| **Daily Loss Limit** | 5% of account | Stop trading for the day |
| **Weekly Loss Limit** | 10% of account | **Skip next week's position trades** |
| Max Concurrent Trades | 3 positions | No new entries |
| Weekly Setup Limit | 1 setup max | **Core rule** |

### Trade Log Template (v2)
```markdown
## Trade #___

**Date:** YYYY-MM-DD
**Day:** Tuesday / Wednesday
**Pair:** XXXYYY
**Direction:** LONG / SHORT
**Timeframe:** Weekly → 4H → 15M

**Setup:**
- Weekly Bias: BULLISH / BEARISH
- Monday Range: [High/Low]
- OB Quality Rank: [1-5]
- Kill Zone: NY AM

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: 50 pips
- TP2: 75 pips
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

Use only OB ranks 1–3:

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount/premium with CHoCH | **Highest** |
| 2 | OB with FVG | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB | Medium |
| 5 | OB without confluence | **SKIP** |

---

## FVG Strength Ranking (v2)

Only trade FVG strength 1–3:

| Strength | Description |
|----------|-------------|
| 1 | 3+ consecutive FVGs |
| 2 | FVGs during displacement |
| 3 | FVGs with MSS/CHoCH |
| 4 | FVGs at OB |
| 5 | **SKIP** |

---

## Fibonacci OTE 70.5% (v2)

Replace "62% Fibonacci" with "70.5% OTE level":

| Level | Fib |
|-------|-----|
| **OTE Primary** | **70.5%** |
| OTE Secondary | 61.8% |
| OTE Tertiary | 78.6% |

**R8 Updated:** Use 70.5% OTE for entry zone calculation.

---

## MSS Entry Alternative (v2)

MSS provides faster entry signal when CHoCH hasn't formed yet:

**Bullish MSS:**
- Price breaks below Monday range low
- No prior BOS required
- Confirms order flow → Enter at **75% size**

**Bearish MSS:**
- Price breaks above Monday range high
- No prior BOS required
- Confirms order flow → Enter at **75% size**