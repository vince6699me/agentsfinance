# AgentFinance SMC/ICT v4

**Autonomous AI Trading System — SMC/ICT Department Only**

---

| System | Value |
|--------|-------|
| Architecture | Paperclip + Signal Fusion + cTrader |
| Focus Department | SMC/ICT Analysis (Department 6) |
| Agents | 4 Agents (18–21) |
| Strategies | 9 Implemented ICT Strategies + 5 Core Concepts |
| Execution | cTrader Open API (Demo + Live) |
| Infrastructure | n8n · Redis · Supabase · Vault |
| Version | v4.0.ICT — April 2026 |
| Status | Implementation Ready |

> **CONFIDENTIAL — INTERNAL SYSTEM DOCUMENTATION**

---

## Executive Summary

This version of AgentFinance focuses exclusively on the **SMC/ICT (Smart Money Concepts / Inner Circle Trader)** department — the highest-conviction, highest-win-rate analytical layer in the multi-agent framework.

Based on backtesting data (2,600 trades across 10 assets — Quantum Algo 2026):
- **Average Win Rate:** 61% 
- **Profit Factor:** 2.17
- **SMC/ICT Weight in Signal Fusion:** 40%
- **Annual Drawdown:** <8%

The SMC/ICT department generates precision entry and exit levels using institutional footprint analysis, eliminating the lower-conviction signals from other departments.

---

## Department Structure

| # | Department | Philosophy | Agents | Weight |
|---|------------|------------|--------|--------|
| **6** | **SMC/ICT Analysis** | Order blocks, structure, liquidity, kill zones | 18–21 | **40%** |

> **Note:** Other departments (1–5) are removed from the execution pipeline in this version. Their signals are logged for analysis but do not trigger trades. This simplifies the system and focuses on the highest-probability setups.

---

## Signal Flow

1. **Market Regime Filter:** ADX + ATR + BB Width classification
2. **SMC/ICT Department Analysis:** All 4 agents run concurrently
3. **Signal Fusion:** Composite score from SMC/ICT agents only
4. **Risk Pipeline:** 7-gate check
5. **Execution:** cTrader API
6. **Position Management:** TP1 → SL to breakeven → trailing stop
7. **Logging:** Supabase + Telegram

---

## Department 6: SMC/ICT Analysis

The SMC/ICT Analysis department implements the complete Inner Circle Trader Smart Money Concepts methodology — reading institutional footprints through order blocks, fair value gaps, liquidity sweeps, structure breaks, and kill zone timing.

### Agent 18 — Order Blocks & Fair Value Gap Agent

**Mission:** Detect and track institutional order blocks and fair value gaps across all monitored pairs and timeframes — classifying validity, calculating magnet strength, and generating limit entry orders at optimal retracement levels.

**SMC Concepts Implemented:**
| Concept | Definition | Entry Logic |
|---------|------------|--------------|
| Bullish OB | Last bearish candle before 100+ pip bullish move | Limit long at 50–61.8% retracement |
| Bearish OB | Last bullish candle before 100+ pip bearish move | Limit short at 50–61.8% retracement |
| Bullish FVG | 3-candle imbalance (gap above) | Limit long at 50% gap fill |
| Bearish FVG | 3-candle imbalance (gap below) | Limit short at 50% gap fill |
| Mitigation Block | Partially tested OB | Reduce position 50% |
| Breaker Block | Failed OB that flips | Aggressive entry, tight stop |

**Python Package:** `pip install smartmoneyconcepts`

**Strategies Implemented:**
| ID | Strategy | Tier | Target |
|----|----------|--------|--------|
| ICT-02 | PD Array FVG Scalp | Scalping | 25 pips |
| ICT-08 | Discount-Premium Position | Position | 300–500 pips |
| STRAT_027 | Fair Value Gap Trading | All | 25–300 pips |
| STRAT_030 | Order Block Trading | All | 30–500 pips |

**LLM Model:** codellama:34b — OB/FVG detection

---

### Agent 19 — Market Structure Agent

**Mission:** Monitor and classify market structure across all timeframes — identifying BOS, CHoCH, MSS, and HH/LL sequences to establish trend direction and reversal probability.

**Structure Concepts:**
| Concept | Trigger | Implication |
|---------|----------|--------------|
| BOS — Bullish | Price closes above prior swing high | Trend continuation |
| BOS — Bearish | Price closes below prior swing low | Trend continuation |
| CHoCH — Bullish | First BOS opposite downtrend | Early reversal |
| CHoCH — Bearish | First BOS opposite uptrend | Early reversal |
| MSS | Structure break on lower TF | LTF entry trigger |
| HH/HL | Higher highs/higher lows | Confirmed uptrend |
| LH/LL | Lower highs/lower lows | Confirmed downtrend |

**Strategies Implemented:**
| ID | Strategy | Tier |
|----|----------|--------|
| ICT-05 | CHoCH Momentum Swing | Swing (75–100 pips) |
| ICT-07 | HTF Structure Break | Position (200–300 pips) |
| STRAT_028 | Break of Structure | All tiers |
| STRAT_029 | Change of Character | All tiers |

**LLM Model:** codellama:34b — structure detection

---

### Agent 20 — Liquidity Analysis Agent

**Mission:** Map institutional liquidity pools — equal highs/lows, buy-side/sell-side liquidity, stop hunts, and Power of Three (AMD) cycle.

**Liquidity Concepts:**
- **Buy-Side Liquidity (BSL):** Equal highs, previous day/week highs
- **Sell-Side Liquidity (SSL):** Equal lows, previous day/week lows
- **Liquidity Grab / Stop Hunt:** Price sweeps BSL/SSL then reverses
- **Power of Three (AMD):** Accumulation → Manipulation → Distribution
- **OTE (Optimal Trade Entry):** 62–79% Fibonacci retracement

**Strategies Implemented:**
| ID | Strategy | Tier | Target |
|----|----------|--------|--------|
| ICT-01 | Micro-Sweep Scalp | Scalping | 20 pips |
| ICT-06 | Sell-Side Redistribution | Swing | 75–100 pips |
| R2-010 | Liquidity Grab Trading | Scalp | 20–50 pips |
| R2-011 | OTE with Fibonacci | All | 50–300 pips |

**LLM Model:** codellama:34b — liquidity mapping

---

### Agent 21 — Kill Zone & Session Agent

**Mission:** Manage time-based precision — identifying active kill zones, session liquidity, BTMM cycle, and Silver Bullet setups.

**Kill Zone Schedule:**
| Kill Zone | EST Time | UTC Time | Focus |
|-----------|----------|----------|-------|
| Asian | 20:00–00:00 | 01:00–05:00 | JPY, AUD, NZD |
| London Open | 03:00–05:00 | 08:00–10:00 | EUR, GBP, CHF |
| NY AM | 07:00–10:00 | 12:00–15:00 | USD pairs |
| NY PM | 13:30–16:00 | 18:30–21:00 | USD pairs |
| London Close | 10:00–12:00 | 15:00–17:00 | EUR, GBP |
| Silver Bullet Long | 10:00–11:00 | 15:00–16:00 | FVG setup |
| Silver Bullet Short | 14:00–15:00 | 19:00–20:00 | FVG setup |

> **Kill Zone Guard:** Agent 21 issues STANDBY outside active kill zones. SMC pipeline generates signals ONLY during valid kill zones — reduces false signals by ~40%.

**Strategies Implemented:**
| ID | Strategy | Session |
|----|----------|---------|
| ICT-03 | Kill-Zone Pulse (30–50 pip) | London, NY AM |
| ICT-04 | Weekly Bias Expansion (50 pip) | NY AM Tue/Wed |
| ICT-09 | Silver Bullet Time-Window | 3 windows daily |

**LLM Model:** mistral:7b — session classification

---

## Implemented Strategies Summary

| Strategy | Tier | Target | Win Rate (est.) | R:R |
|----------|------|--------|------------------|-----|
| ICT-01: Micro-Sweep Scalp | Scalping | 20 pips | 55–65% | 1:2 |
| ICT-02: PD Array FVG Scalp | Scalping | 25 pips | 55–65% | 1:2 |
| ICT-03: Kill-Zone Pulse | Short-term | 30–50 pips | 58–65% | 1:2.5 |
| ICT-04: Weekly Bias Expansion | Short-term | 50 pips | 58–65% | 1:2.5 |
| ICT-05: CHoCH Momentum Swing | Swing | 75–100 pips | 60–68% | 1:3 |
| ICT-06: Sell-Side Redistribution | Swing | 75–100 pips | 60–68% | 1:3 |
| ICT-07: HTF Structure Break | Position | 200–300 pips | 62–72% | 1:4 |
| ICT-08: Discount-Premium Position | Position | 300–500 pips | 65–75% | 1:5 |
| ICT-09: Silver Bullet Time-Window | Scalping | ≥15 pips | 60–70% | 1:2 |

---

## Signal Fusion (SMC/ICT Only)

### Department Weights

| Department | Weight | Note |
|------------|--------|------|
| SMC/ICT | 100% | All other departments bypassed in v4.ICT |

### Fusion Logic

```python
@dataclass
class FusedSignal:
    symbol: str
    direction: str           # LONG / SHORT / NEUTRAL
    composite_confidence: float   # 0.0 → 1.0
    smc_score: float        # Agent 18-21 combined
    ob_quality_rank: int     # 1-5 (per enhancement)
    fvg_strength: int        # 1-5 (per enhancement)
    veto_active: bool
    veto_reason: str
```

### Hard Veto Rules

| Veto Trigger | Agent | Action |
|--------------|-------|--------|
| High-impact news ±15 min | Agent 21 | Block trade |
| Daily drawdown > 2.5% | Risk Manager | Halt trading |
| Open trades >= 5 | Risk Manager | No new entries |
| Spread > 3x average | Risk Manager | Block trade |
| Signal age > 4 hours | Fusion | Signal expires |
| Confidence < 0.75 | Fusion | No trade |
| Kill zone not active | Agent 21 | STANDBY |

---

## Performance Characteristics (Backtesting Guidance)

| Metric | Expected |
|--------|----------|
| Win Rate | 55–75% |
| Profit Factor | 1.95–2.47 |
| Average R:R | 1:2 to 1:5 |
| Annual Drawdown | < 8% |
| Max Consecutive Losses | 5–7 |

*Source: 2,600-trade backtest (Quantum Algo 2026); 10-asset study*

---

## Folder Structure

```
AgentFinance/
├── docs/
│   └── agentfinance_smcict_v4.md    # This document
├── strategies/
│   └── smc-ict/
│       ├── ICT-01-Micro-Sweep-Scalp.md
│       ├── ICT-02-PD-Array-FVG-Scalp.md
│       ├── ICT-03-Kill-Zone-Pulse.md
│       ├── ICT-04-Weekly-Bias-Expansion.md
│       ├── ICT-05-CHoCH-Momentum-Swing.md
│       ├── ICT-06-Sell-Side-Redistribution-Swing.md
│       ├── ICT-07-HTF-Structure-Break.md
│       ├── ICT-08-Discount-Premium-Position.md
│       ├── ICT-09-Silver-Bullet-Time-Window.md
│       └── ICT-Strategies-Enhancement-Reference.md
├── agents/
│   └── [Agent configs - README]
├── workflows/
│   └── [n8n workflow configs - README]
└── scripts/
    └── [Utility scripts - README]
```

---

## Getting Started

1. **Install Dependencies:**
   ```bash
   pip install smartmoneyconcepts pandas numpy
   ```

2. **Configure Kill Zones:**
   - Set timezone to EST/EDT
   - Verify kill zone times match market hours

3. **Run Signal Fusion:**
   ```bash
   python signal_fusion.py
   ```

4. **Execute Trades:**
   ```bash
   python ctrader_api_server.py
   ```

---

*Document Version: v4.0.ICT*
*Generated: April 2026*
*Status: Implementation Ready*