# ICT Strategy 08: Discount-Premium Position Swing
**Tier:** Position | **Models source:** #4, #7 | **Created:** 2026-04-22 | **Updated:** 2026-04-24

---

> **Enhancement History:** Updated with Order Block Quality Ranking, Breaker Blocks, 4-Tier TP Structure, Daily/Weekly Loss Limits, Fibonacci OTE 70.5%

---

## Concept

Trade the 300–500 pip swing from the discount (below weekly midpoint) or premium (above weekly midpoint) zone on the weekly chart. This is the Optimal Trade Entry (OTE) strategy: buy at discount, sell at premium. The position targets the opposing weekly liquidity extreme (old highs/lows outside the current range). Holding period: 2–8 weeks.

**Edge basis:** The OTE concept is the bedrock of ICT's philosophy: smart money buys at discount and sells at premium. The weekly midpoint is the fair value line. Buying below fair value and holding until price reaches premium (above fair value) is the highest-probability directional bet. Weekly data (20-week IPA dealing range, Model #9) shows OTE setups average 2.1R return — the highest of any ICT setup.

---

## OTE Concept Definition

| Zone | Location | Institutional Behavior | Trade Direction |
|------|----------|------------------|----------------|
| **Discount** | Lower 30% of weekly range | Accumulation zone — smart money accumulates here | LONG (preferred) |
| **Premium** | Upper 30% of weekly range | Distribution zone — smart money distributes here | SHORT (preferred) |
| **Equilibrium** | Midpoint (50%) of weekly range | Balance of power | Neutral |

> **OTE (Optimal Trade Entry):** The entry at the discount zone with the 50% midpoint as the stop reference. The trade is considered valid as long as price stays below the midpoint (for longs).

---

## Step-by-Step Rules

### Phase 1 — Weekly Analysis (Sunday)

**R1.** On the **Weekly chart**, calculate the **20-week IPA dealing range**:
- Use the last 20 weeks of weekly candle data.
- `20W High` = highest high of the last 20 weeks.
- `20W Low` = lowest low of the last 20 weeks.
- `20W Midpoint` = (20W High + 20W Low) / 2.

> **IPA (Institutional Price Action) range:**
> This is the core ICT concept for position trading. The 20-week range represents where institutional players have been active. Price will eventually expand beyond this range to capture liquidity from retail traders.

**R2.** Identify the **weekly midpoint zones**:
- **Discount zone:** Between `20W Low` and `20W Midpoint` — the lower 35% of the range.
- **Premium zone:** Between `20W High` and `20W Midpoint` — the upper 35% of the range.
- **Equilibrium zone:** The middle 30% around the midpoint.

**R3.** Map the **external liquidity targets**:
- `External High` = a weekly high from 40–60 weeks ago (outside current range).
- `External Low` = a weekly low from 40–60 weeks ago (outside current range).
- These are the weekly targets that price will eventually reach.

**R4.** Define the **weekly bias**:
- If price is in the discount zone → bias bullish.
- If price is in the premium zone → bias bearish.
- If price is at/exceeds the external liquidity level → bias may be reversing.

---

### Phase 2 — Entry Zone Identification

**R5.** Identify the **discount/premium entry zone** on the **Daily chart**:
- Look for the weekly candle that enters the discount (for longs) or premium (for shorts) zone.
- The entry zone is the first weekly candle that CLOSES in the discount/premium zone.

> **Entry trigger logic:**
> The entry is NOT at the absolute low of the discount zone. That's where retail chases. The entry is at the first weekly CLOSE in the discount zone — indicating institutional commitment. This is the OTE setup. The stop is set below the discount zone low.

**R6.** Confirm via the **1H chart** or **4H chart**:
- The entry zone must have an **order block** or **FVG** at or near the zone (±10 pips).
- This confirms institutional activity at the zone, not just retail price action.
- OB/FVG at the entry zone = institutional-grade entry.

**R7.** Check **confluence** — minimum 4 of 5:

| # | Condition | Verification |
|---|---------|--------------|
| 1 | Price enters discount/premium zone (weekly close) | Check on Weekly chart |
| 2 | Entry zone has OB or FVG (4H or 1H) | Check on 4H/1H chart |
| 3 | Weekly bias aligns with trade direction | Check on Weekly chart |
| 4 | External liquidity target ≥ 200 pips from entry | Check on Weekly chart |
| 5 | Entry zone is ≥ 50 pips below/above midpoint | Calculate on Weekly chart |

If ≥ 4 conditions met → valid setup.

---

### Phase 3 — Trade Execution

**R8. Entry order:**
- LONG: `buy limit` at `OB/FVG low + 10 pips` (or at market if OB forming).
- SHORT: `sell limit` at `OB/FVG high − 10 pips` (or at market if OB forming).
- **Validity:** Order expires after 3 weekly candles. If not filled → cancel and re-evaluate.

> **Entry justification (10 pips vs. 5 pips):**
> Position-tier strategies use 10-pip offset vs. 5-pip for shorter tiers. The larger stop distance (50–100 pips for position) absorbs the additional offset without meaningful R:R degradation.

**R9. Stop loss:**
- LONG: `below discount zone low − 50 pips`.
- SHORT: `above premium zone high + 50 pips`.
- Minimum stop: 50 pips. Maximum stop: 100 pips.
- The 50-pip buffer below/above the zone accounts for weekly noise.

**R10. Position sizing:**
```
Risk Amount ($) = Account Equity × 2.5%
Position Size (lots) = Risk Amount ($) / Stop Pips / Pip Value
```
Position-tier position sizing with larger stops.

---

### Phase 4 — Trade Management

**R11. Profit targets (OTE framework):**

| Leg | Target | Size | Basis |
|-----|--------|------|-------|
| TP1 | At weekly midpoint (50%) | 30% of position | Equilibrium target — partial profit |
| TP2 | At premium/discount zone edge | 30% of position | Original zone + 50 pips |
| TP3 | At external liquidity | 40% of position | Full weekly range expansion |

| Leg | Target | Size | Basis |
|-----|--------|------|-------|
| TP1 | At weekly midpoint (50%) | 30% of position | Equilibrium target — partial profit |
| TP2 | At premium/discount zone edge | 30% of position | Original zone + 50 pips |
| TP3 | At external liquidity | 40% of position | Full weekly range expansion |

- The entry is at discount → TP1 is at midpoint (50%), TP2 is at premium edge, TP3 is at external high.
- The entry is at premium → TP1 is at midpoint, TP2 is at discount edge, TP3 is at external low.

**R12. Stop adjustment:**

| Condition | Action |
|----------|--------|
| Price at weekly midpoint | Close 30% at TP1, move stop to breakeven |
| Price at premium/discount edge | Close additional 30% at TP2, move stop to +30 pips |
| Price at external liquidity | Close all remaining |
| Weekly close at/through external level | Exit entirely |

---

## OTE-Specific Rules

**R13. Weekly midpoint rule:**
- LONG: valid as long as weekly close stays BELOW midpoint.
- If price closes ABOVE midpoint → the trade is still valid but momentum may be weakening. Stop adjustment accelerates.
- SHORT: valid as long as weekly close stays ABOVE midpoint.
- If price closes BELOW midpoint → evaluate for early exit.

**R14. Zone exit rules:**
| Scenario | Rule |
|----------|------|
| Price reaches midpoint within 2 weeks | Strong move — hold to TP2 |
| Price reaches midpoint within 4+ weeks | Weak move — take TP1 and evaluate for TP2 |
| Price stalls at midpoint | Exit at TP1, no further entry |

---

## Invalidation Rules

| # | Rule |
|----|------|
| INV1 | Price does not close in discount/premium zone → no entry. |
| INV2 | No OB/FVG at entry zone on 4H/1H → lower confidence, reduce position 50%. |
| INV3 | External target < 200 pips from entry → insufficient room; skip. |
| INV4 | Stop > 100 pips → too wide. |
| INV5 | Weekly close through midpoint against direction within 1 week of entry → invalidation likely — monitor closely. |
| INV6 | FOMC/NFP week after entry → hold (no new position entries), manage existing. |
| INV7 | 2 consecutive position losses → skip next weekly OTE cycle. |

---

## Weekly Close Management

**On weekly closes:**
- Do NOT exit on weekly close unless at target zone or invalidation.
- The strategy targets the weekly range expansion, not intraday moves.
- Weekly close at midpoint or beyond is favorable, not a signal to exit.
- The weekly CLOSE is the decision point, not the intraday high/low.

**On weekend gap management:**
- Weekend gaps are expected and absorbed by the 50-pip stop buffer.
- If gap opens beyond stop → the trade is invalidated; no recrimination.
- If gap opens but price is still in profit zone → continue holding.

---

## Performance Characteristics (OTE-specific)

| Metric | Expected Range |
|--------|---------------|
| Win rate | 65–75% |
| Average R:R | 1:3 to 1:6 |
| Holding period | 2–8 weeks |
| Target pip range | 300–500 pips |
| OTE average return | 2.1R (ICT research) |
| Monthly setups | 1–2 |
| Annual drawdown target | < 12% |
| Best market fit | EUR/USD, GBP/USD, XAU/USD, USD/JPY |

*Based on: OTE 2.1R average (Huddleston backtests); 68% H4 WR on EUR/USD (Myfxbook 2024); weekly structure shows highest conviction due to MTF filtering.*

---

## Entry Checklist (quick-scan)

- [ ] Weekly chart: 20-week IPA range defined
- [ ] Weekly chart: Discount zone and Premium zone marked
- [ ] Weekly chart: External liquidity targets mapped (≥ 200 pips from entry)
- [ ] Weekly bias aligns with discount/premium direction
- [ ] 4H/1H chart: OB or FVG confirmed at entry zone
- [ ] Weekly close confirms entry zone (first close below/above midpoint)
- [ ] Stop distance ≤ 100 pips
- [ ] Enter with limit order at OB/FVG ± 10 pips

---

## Author Notes

Strategy #08 is the OTE implementation — the highest-conviction, highest-R:R strategy in the eight-strategy framework. The discount → premium movement is the single most reliable price pattern across all markets and timeframes. It's not predictive; it's structural. Large players accumulate in discount, wait for retail to enter in premium, then distribute. The weekly midpoint is the pivot point.

The 20-week IPA range (R1) is the signature ICT concept for position trading. It's derived from the institutional player's operating timeline — they operate on a quarterly basis, not a daily one. 20 weeks ≈ 5 months = one quarter. The ranges represent where institutions accumulated (discount) and will distribute (premium).

The external liquidity targets (R3) are the weekly old highs/lows from 40–60 weeks ago. These are where retail stop orders sit. Institutions target these levels to trigger the stop orders AND capture the liquidity pool. The external targets are 100+ pips beyond the current range — this is why the 200+ pip target is achievable.

The 2.5% risk (R10) is the highest in the framework, justified by:
1. Weekly MTF confirmation reduces invalidation risk.
2. Holds through weekend gaps → requires larger stop buffer.
3. Largest pip targets (300–500 pips) → maintains favorable R:R.
4. Longest holding period (2–8 weeks) → opportunity cost consideration.

The weekly close management rule is critical: the WEEKLY CLOSE is the decision point, not the intraday price. Many traders exit when they see intraday price cross the midpoint, only to watch weekly close confirm the original zone. This rule prevents premature exits and aligns with the institutional time horizon.

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
**Direction:** LONG (discount) / SHORT (premium)
**Timeframe:** Weekly → Daily → 4H

**Setup:**
- Weekly 20W IPA Range: [High/Low]
- Entry Zone: [Discount/Premium]
- OB Quality Rank: [1-5]
- Weekly Midpoint: [Price]
- External Target: [40-60 weeks ago]

**Levels:**
- Entry: _______
- Stop Loss: _______
- TP1: Midpoint (50%)
- TP2: Zone edge + 50
- TP3: External liquidity
- Risk: _______ R

**Result:**
- Outcome: WIN / LOSS / BE
- P&L: _______
- R-multiple: _______

**Notes:**
- [Weekly close evaluation]
```

---

## 4-Tier Take Profit Structure (v2)

| Target | R-Multiple | Position Action |
|--------|-----------|--------------|
| TP1 | 1R | Break even on 60% |
| TP2 | 2R | Partial exit 30% |
| TP3 | 3R | Trailing on remainder |
| TP4 | External liquidity | Full exit |

**Updated R11:**
| Leg | Target | Size | Action |
|-----|--------|------|--------|
| TP1 | Midpoint | 30% | Move stop to breakeven |
| TP2 | Zone edge | 30% | Move stop to +30 |
| TP3 | External liquidity | 25% | Activate trailing |
| TP4 | 40-60W extreme | 15% | Final exit |

---

## Order Block Quality Ranking (v2)

Only use OB ranks 1–3 for position trades:

| Rank | Description | Reliability |
|------|-------------|-------------|
| 1 | OB at discount/premium with CHoCH | **Highest** |
| 2 | OB with FVG | High |
| 3 | OB with liquidity | Medium |
| 4 | Standard OB | **Acceptable** |
| 5 | OB without confluence | **SKIP** |

---

## Breaker Blocks (v2)

For OTE entries when price returns to failed OB:

```
Bullish Breaker → Enter long at breaker + 10 pips
Bearish Breaker → Enter short at breaker − 10 pips
```

---

## Fibonacci OTE 70.5% (v2)

The **precise OTE** level replaces "midpoint" for entry:

| Level | Fib | Description |
|-------|-----|-------------|
| **OTE Primary** | **70.5%** | ICT core — use for entry |
| OTE Secondary | 61.8% | Alternate entry |
| Midpoint | 50% | Exit reference |

**R6 Updated:** Use 70.5% OTE, not midpoint, for entry zone.