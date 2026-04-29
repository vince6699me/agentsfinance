# ICT Strategy 06: Sell-Side Redistribution Swing
**Tier:** Swing | **Models source:** #6, #7, #10 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, Breaker Blocks, 4-Tier TP Structure, Daily/Weekly Loss Limits

---

## Concept

Trade the 75–100 pip bearish swing after a **second-stage distribution** forms on the 4H chart. The strategy exploits the market maker sell-side dynamic: institutional players distribute large long positions during the first stage (range), then trigger sell-side liquidity sweeps (below the range) to capture retail buy stops, before driving price lower in a parabolic collapse. Entry is a limit short at the first-stage high ±5 pips after sell-side liquidity has been swept.

**Edge basis:** Second-stage distributions (sell-side redistribution) are the most violent price movements in any market. They occur when large institutional players have completed accumulation and begin distribution. The first stage redistributes to retail; the second stage — driven by sell-side liquidity sweeps — creates the parabolic move. Bearish markets drop faster than bullish markets rise. The 20-day range extremes provide the structural map.

---

## Why Sell-Side Is Different

| Characteristic | Buy-Side Move | Sell-Side Move |
|--------------|--------------|---------------|
| Movement style | Gradual, sustained | Parabolic, rapid |
| Liquidity sweep | Above range highs | Below range lows |
| Drop speed | Moderate | Fast, often 2–3x buy-side velocity |
| Warning signals | Subtle | Overt manipulation |
| Institutional timing | Accumulation → gradual rise | Distribution → sharp drop |
| Retail trap | Sell-stops above highs | Buy-stops below lows |
| Average extension | 1–2x range | 2–4x range |

---

## Timeframes

| Role | Timeframe | Purpose |
|------|----------|---------|
| Structure | 4H | Second-stage distribution identification |
| Bias | Daily | Weekly dealing range, external liquidity |
| Entry | 1H | First-stage high/low identification, entry zone |
| Confirmation | 15M | Sell-side sweep confirmation, limit order |

---

## Step-by-Step Rules

### Phase 1 — Preparation (Weekly)

**R1.** On the **Daily chart**, define the **20-day dealing range**:
- `Range High` = highest high of the last **20 trading days** (excluding Sundays).
- `Range Low` = lowest low of the last **20 trading days**.
- `Range Midpoint` = (Range High + Range Low) / 2.

**R2.** Identify the **first-stage redistribution zone** (first stage):
- The first stage is the last rally within the 20-day range that approached or exceeded `Range High` but failed to break out.
- Look for: price reaching `Range High`, followed by a retracement lower, followed by a second rally that ALSO reaches `Range High` but fails again.
- This double-top failure at `Range High` = institutional distribution in the premium zone.
- Draw the **first-stage line** at the highest point of the failed rally.

**R3.** Identify the **discount zone** (sell-side target):
- Discount zone = the lower 30% of the 20-day range (below `Range Midpoint`).
- This is where sell-side liquidity pools sit — below the range.
- The discount terminus = `Range Low − 30 pips` (extension below the range).
- This is where price must sweep to trigger the second-stage move.

**R4.** Determine market phase:

| Phase | Condition | Strategy Approach |
|-------|---------|----------------|
| Accumulation | Price in lower 30% of range, building | No trade. Watch for first stage. |
| First Stage | Double-top at Range High, retrace to mid | Map first-stage line. Wait. |
| Kill Zone | Price sweeps below Range Low | Enter short at first-stage line. |
| Second Stage | Discount terminal reached | Hold and manage position. |

---

### Phase 2 — Opportunity Discovery

**R5.** Monitor for the **sell-side liquidity sweep** on the **15M chart**:
- Price must CLOSE below `Range Low` (the 20-day low).
- The sweep candle must have body ≥ 60% of its range.
- Following candle must NOT immediately reclaim `Range Low`.
- This confirms retail buy stops below `Range Low` were harvested.

**R6.** Confirm **first-stage redistribution** is in progress:
- After the sweep, price must retrace HIGHER — back toward `Range Midpoint` or higher.
- This retrace is the second-stage entry opportunity.
- The retrace must reach or exceed the **first-stage line** (±5 pips).

> **Second-stage entry logic:**
> The entry is NOT at the sweep low (that's where retail traders get stopped). The entry is at the first-stage line — the level where institutional players are distributing their long positions from the first stage. They need price to return here to sell their inventory to retail buyers who were stopped out below the range.

**R7.** Check **confluence** — minimum 3 of 4:
- [ ] Sell-side liquidity sweep confirmed below `Range Low` (body ≥ 60%, candle closes below).
- [ ] Price retrace reaches or exceeds the first-stage line.
- [ ] Range Midpoint is above the entry zone (price is in the upper half on the retrace).
- [ ] Weekly bias is bearish (confirmed on Daily chart).

If ≥ 3 conditions met → valid setup.

---

### Phase 3 — Trade Execution

**R8. Entry order:**
- SHORT: `sell limit` at `first-stage line − 5 pips`.
- **Validity:** Order expires after 6 1H candles. If not filled → cancel and reassess.

**R9. Stop loss:**
- SHORT: `above first-stage line + 25 pips`.
- Minimum stop: 25 pips. Maximum stop: 50 pips.
- If the retrace doesn't reach the first-stage line → no entry.

**R10. Position sizing:**
```
Risk Amount ($) = Account Equity × 2%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Round DOWN.

---

### Phase 4 — Trade Management

**R11. Profit targets:**

| Leg | Target | Size | Basis |
|-----|--------|------|-------|
| TP1 | Entry − 75 pips | 50% of position | Minimum target |
| TP2 | Entry − 100 pips | 30% of position | Discount terminal |
| TP3 | Range Low − 30 pips | 20% of position | Parabolic extension |

- TP2 of 100 pips aligns with the discount terminal (below Range Low).
- TP3 is the lottery ticket — only pursue if price has dropped through Range Low with momentum.
- Sell-side moves can extend 2–4x the range magnitude. TP3 captures this.

**R12. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at 40 pips profit | Move stop to breakeven |
| Price at 60 pips profit | Move stop to +15 pips |
| Price at Range Low | Close 30% remainder here (TP2) |
| Price at Range Low − 30 pips | Close all remaining |

---

## Sell-Side Behavioral Rules

**R13. Position sizing adjustment for sell-side:**
- Due to faster, larger moves: if TP3 is reached by the 2nd 1H candle (extremely fast drop) → close ALL positions immediately. This is a "crash-type decline" (Model #6 distinction: controlled vs. crash). The fast drop may be a liquidity cascade, not institutional flow. Do not hold through it.

**R14. Market character rules:**
| Character | Indicator | Position Rule |
|----------|---------|------------|
| **Controlled distribution** | Gradual decline, retrace between drops | Hold to TP2/TP3 |
| **Crash-type decline** | Parabolic drop in < 1 hour, no retrace | Exit at first retrace immediately |
| **Second stage extended** | Price below Range Low for > 3 candles | Reduce to TP1, close remainder at TP2 |

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Price sweeps Range Low but immediately retraces and reclaims it within 1 candle → no second-stage trade. |
| INV2 | Price retraces but does NOT reach first-stage line → no entry. |
| INV3 | Range is narrow (< 50 pips 20-day range) → insufficient room; skip. |
| INV4 | Stop distance > 50 pips → too wide for swing. |
| INV5 | NFP week → skip second-stage entries (volatility too high). |
| INV6 | FOMC week → skip second-stage entries (central bank risk). |
| INV7 | 3 consecutive sell-side losses → skip next week. |

---

## Performance Characteristics

| Metric | Expected Range |
|--------|---------------|
| Win rate | 58–65% |
| Average R:R | 1:3 to 1:6 |
| Holding period | 2–7 trading days |
| Target pip range | 75–100 pips (TP1/TP2) |
| Parabolic extension | 100–200+ pips (TP3, rare) |
| Weekly setups | 0–2 |
| Annual drawdown target | < 10% |
| Best market fit | GBP/USD (highest sell-side frequency), XAU/USD, crude oil |

> **On crash vs. controlled:** The 2020 oil price collapse (negative oil futures) was a crash-type decline driven by real supply/demand dynamics, not pure institutional distribution. The strategy handles both: controlled = hold to TP2; crash = exit immediately and re-evaluate. The distinguishing factor is speed — crash moves happen in < 1 hour with no retrace. Controlled moves have inter-move retrace intervals.

---

## Entry Checklist (quick-scan)

- [ ] Daily chart: 20-day range (last 20 trading days) defined
- [ ] Daily chart: first-stage redistribution identified at Range High
- [ ] First-stage line drawn
- [ ] Discount terminus mapped below Range Low
- [ ] Weekly bias is bearish
- [ ] 15M chart: sell-side sweep confirmed (close below Range Low, body ≥ 60%)
- [ ] Price retrace reaches first-stage line
- [ ] Confluence ≥ 3/4 conditions met
- [ ] Stop distance ≤ 50 pips
- [ ] Enter with sell limit order at first-stage line − 5 pips

---

## Author Notes

Strategy #6 is the most conceptually advanced of the eight strategies — it requires understanding why institutional players behave differently on the buy and sell sides. On the sell side, institutions don't gradually build short positions; they already hold longs (accumulated during the accumulation phase), wait for retail to buy at the top, then trigger sell-side sweeps to stop out retail buy stops below the range. The parabolic move is the result of removing buy-side liquidity AND executing the sell order in a single efficient move.

The first-stage line (R2) is the critical element. ICT calls this the "accumulation zone" — institutions accumulated during the first stage, and they need price to return here to exit their longs. The second-stage entry is not a new short; it's a continuation of the first-stage distribution. Smart money is already short. The entry is riding their coattails.

The Model #6 distinction between controlled distribution and crash-type declines (R14) is essential for capital preservation. Crash-type declines (flash crashes, liquidity events) move so fast that position management breaks down. The fix is mechanical: if TP3 is reached by the 2nd candle, exit everything immediately. Do not hold through a crash.

On commodities: crude oil and natural gas are structurally prone to second-stage distribution due to real-world supply/demand dynamics. The leverage in futures markets amplifies the effect. The strategy applies to all markets, but commodities require tighter position sizing for the leverage component.

---

## Enhanced Risk Management (v2)

### Daily/Weekly Loss Limits (v2)
| Limit Type | Specification | Action When Hit |
|-----------|--------------|----------------|
| **Daily Loss Limit** | 5% of account | Stop trading for the day |
| **Weekly Loss Limit** | 10% of account | Skip next week |
| Max Concurrent Trades | 3 positions | No new entries |

### Trade Log Template (v2)
```markdown
## Trade #___

**Date:** YYYY-MM-DD
**Pair:** XXXYYY
**Direction:** SHORT (sell-side only)
**Timeframe:** Daily → 4H → 1H

**Setup:**
- Market Phase: Second-stage distribution
- First-Stage Line: [Price level]
- Discount Sweep: [Confirmed]
- OB Quality Rank: [1-5]
- Kill Zone: [NY AM/etc]

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: 75 pips
- TP2: 100 pips
- TP3: Discount terminal
- Risk: _______ R

**Result:**
- Outcome: WIN / LOSS / BE
- P&L: _______
- R-multiple: _______

**Notes:**
- [Controlled vs Crash evaluation]
```

---

## 4-Tier Take Profit Structure (v2)

| Target | R-Multiple | Position Action |
|--------|-----------|--------------|
| TP1 | 1R | Break even on full lot |
| TP2 | 1.5R–2R | Partial exit 50% |
| TP3 | 3R | Trailing stop activated |
| TP4 | Discount terminal | Full exit |

**Updated R11:**
| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | 1R | 25% | Move stop to breakeven |
| TP2 | 2R | 30% | Lock profit |
| TP3 | 3R | 25% | Activate trailing |
| TP4 | Discount terminal | 20% | Final exit |

---

## Order Block Quality Ranking (v2)

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at premium with sell-side CHoCH | **Highest** |
| 2 | OB with FVG below | High |
| 3 | OB with liquidity nearby | Medium |
| 4 | Standard OB | Medium |
| 5 | OB without confluence | **SKIP** |

---

## Breaker Blocks for Sell-Side (v2)

**Bearish Breaker Block (applies to Strategy #06):**
- Was a bearish order block
- Price broke above it (failed)
- Price now returning from above
- Expect further downside → Enter short

### Breaker Entry Rules
```
Entry: Sell limit at breaker bottom − 5 pips
Stop: Above breaker high + 10 pips
Target: Next demand zone
```

---

## Fibonacci OTE 70.5% (v2)

| Level | Fib |
|-------|-----|
| **OTE Primary** | **70.5%** |
| OTE Secondary | 61.8% |

**R6 Updated:** Use 70.5% OTE for entry zone retracement.