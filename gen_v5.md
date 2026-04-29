# AGENTFINANCE v5.0 — Complete Project Plan

## Autonomous Multi-Team AI Trading System

**Version:** v5.0 — April 2026  
**Status:** Production-Ready Blueprint  
**CONFIDENTIAL — INTERNAL SYSTEM DOCUMENTATION**

---

# 1. Executive Summary

AgentFinance v5 is a complete, production-ready autonomous trading system that evolves the v4 department-based analysis architecture into a full operational team structure inspired by professional trading firms. The system coordinates eight specialised teams — each with dedicated AI agents, tools, and responsibilities — under a Chief Orchestrator that manages signal flow from market data collection through to trade execution and performance analytics.

The system covers five market sectors: Forex, Commodities (Gold and Oil), Stocks, Indices, and Crypto. It deploys 46 institutional-grade signal strategies and 7 execution tactics across all sectors, implemented by 21 specialised AI agents. The Trade Signals team replaces signal fusion with a debate mechanism — Bull, Bear, and Neutral analysts argue their case before a Fund Manager synthesises a final signal with a confidence score.

## 1.1 What is New in v5

| Component | v4 | v5 (This Plan) |
|-----------|-----|------------------|
| Architecture | Department-based signal fusion | 8 operational teams with debate mechanism |
| Signal Logic | Weighted confluence score | Bull vs Bear vs Neutral debate — Fund Manager decides |
| Scanner | Single-dept scanner | Dedicated Scanner Team with sector-specific endpoints |
| Sectors | Forex + some coverage | Forex, Commodities, Stocks, Indices, Crypto (full) |
| Execution | cTrader only | cTrader (Forex/Commodities) + Bybit (Crypto) |
| Backend | Node.js + Python mix | Pure Python FastAPI |
| Frontend | Basic React tabs | Full React/Vite dashboard with 10 pages |
| Backtesting | Manual | Dedicated Backtesting Team with automated pipelines |
| Analytics | Basic equity curve | Full Analytics Team with A/B testing and meta-eval |
| Enhancements | None | 26 structured enhancements (P0→P3 roadmap) |
| ML/RL | Not planned | Feature store ready from day 1; ML/RL phase-gated |

## 1.2 Strategic Goals

- Automate the full trading lifecycle — from market scanning to execution to reporting — with minimal human intervention
- Deploy institutional-quality analysis across five market sectors using 21 specialised agents
- Replace subjective signal fusion with a structured debate mechanism that produces explainable, auditable trade decisions
- Build a feature store from day one so ML and RL phases can be activated with immediately available labelled training data
- Deliver a professional React dashboard that makes all system activity visible, auditable, and controllable

---

# 2. Project Vision & Design Philosophy

## 2.1 Core Design Principles

AgentFinance v5 is built on five principles that guide every architectural decision:

### PRINCIPLE 1 — Institutional-Grade Analysis

Every signal produced by the system must be justified by at least two independent analytical perspectives. No single agent can produce a live trade. The debate mechanism and confluence requirements enforce this at every layer.

### PRINCIPLE 2 — Transparency and Auditability

Every decision the system makes — why an analysis was run, what signals were debated, what the Fund Manager decided and why, what risk parameters were applied — must be logged, queryable, and visible on the dashboard. Black-box decisions are not acceptable.

### PRINCIPLE 3 — Capital Preservation First

Risk management gates are non-negotiable. Hard daily and weekly loss limits, position correlation checks, and ADR-based stop distances are enforced before any order is placed. The Risk team has veto power over the entire pipeline.

### PRINCIPLE 4 — Modular and Extensible

Every team, agent, and strategy is a pluggable module. New strategies can be registered without modifying existing code. New agents can be added to teams. The ML/RL phase is a drop-in enhancement, not a rebuild.

### PRINCIPLE 5 — Production-Ready from Day One

The system starts with paper trading mirroring live markets, with every live trade feature working but risk-free. The go-live switch is a single parameter change, not a new deployment.

## 2.2 Market Coverage

| Sector | Instruments | Execution Venue | Primary Strategies |
|--------|-------------|-----------------|-------------------|
| Forex | 28 major/minor pairs + 20 exotics | cTrader (OANDA) | ICT-01 to 09, Carry Trade, Macro Event, Currency Strength |
| Commodities | XAUUSD (Gold), XTIUSD (Oil) | cTrader (OANDA) | ICT-02/03/08, Commodity-FX Intermarket, COT, VIX correlation |
| Stocks | Top 100 US equities (SPY, QQQ, AAPL, TSLA, etc.) | Bybit / broker API | MACD Divergence, MA Crossover, Volume Trading, Earnings |
| Indices | SP500, NAS100, DAX, FTSE, Nikkei | cTrader + Bybit | ICT-07/08 HTF, VIX-EMA, 20-Day Breakout, Perfect Order |
| Crypto | BTC, ETH, BNB, SOL, top-30 alts | Bybit | ICT-01/02, Breakout, Volume, TWAP execution |

---

# 3. System Architecture

## 3.1 High-Level Architecture

The v5 architecture is a layered pipeline where every layer has a single responsibility. Data flows in one direction — from raw market data to executed trades — with feedback loops for performance tracking and parameter optimisation.

| Layer | Components | Technology | Responsibility |
|-------|------------|------------|----------------|
| Data Ingestion | REST/WebSocket adapters per sector | OANDA, Polygon, FRED, Bybit, Finnhub, CFTC | Collect OHLCV, news, economic data, COT reports |
| Caching | OHLCV and news cache | Redis (TTL: M15=2min, H1=10min, H4=30min, D1=1hr) | Reduce API calls by 85%; prevent redundant processing |
| Regime Filter | Market regime classifier | Python pandas — ADX + ATR + BB Width | Classify TRENDING/RANGING/TRANSITIONING before analysis |
| Team 1 | News & Market Data | 4 agents — Macro, News NLP, Sector Data, COT | Produce sector intelligence reports every 15 minutes |
| Team 2 | Live Markets Scanner | 5 sector scanner agents | Scan all sectors for active opportunities continuously |
| Team 3 | Analysis | 21 agents in 6 departments | Produce scored signals per sector and timeframe |
| Team 4 | Trade Signals (Debate) | Bull + Bear + Neutral + Fund Manager | Debate signals; produce final trade decision with confidence |
| Team 5 | Risk & Portfolio | Risk Manager + Portfolio Monitor + Checklist | Gate trades; calculate position size; enforce limits |
| Team 6 | Live Traders | 5 sector trader agents | Execute orders via cTrader/Bybit; manage open positions |
| Team 7 | Backtesting | 3 agents — Backtest, Optimiser, Validator | Run automated strategy backtests; validate parameters |
| Team 8 | Analytics | 4 agents — Meta-eval, Pattern, Performance, A/B | Track system performance; detect patterns; run experiments |
| Orchestration | Chief Orchestrator + n8n workflows | Python agent loop + n8n (port 5678) | Coordinate all teams; trigger workflows; manage state |
| Persistence | Trade log, signals, performance, features | Supabase (PostgreSQL) + Redis | Store all data; power dashboard queries; feed ML |
| Alerts & Comms | Telegram bot + Slack webhook (optional) | Telegram Bot API | Real-time notifications: signals, trades, alerts, reports |
| Frontend | React.js + Vite dashboard | React 18 + Vite + TailwindCSS + Recharts | 10-page dashboard: live prices, signals, trades, analytics |
| Secrets | API keys, broker credentials | HashiCorp Vault | Never hardcoded; rotatable without code changes |

## 3.2 Signal Flow (End-to-End)

The following sequence describes the complete path from market event to executed trade:

1. **Market event detected** (price move, news release, kill zone open, COT update)
2. **Team 1 — News & Market Data** agents collect and process relevant sector information
3. **Team 2 — Scanner** agents scan all five sectors for active setup opportunities
4. **Regime Filter** classifies current market regime for affected instruments
5. **Team 3 — Analysis** agents run parallel analysis (all 6 departments) per instrument
6. **Pre-Trade Checklist Validator** scores each candidate signal (9-point ICT checklist)
7. **Confidence Decay system** assigns half-life to each signal based on strategy tier
8. **Team 4 — Bull, Bear, and Neutral** agents debate signals; Fund Manager produces final decision with confidence score
9. **Team 5 — Risk Manager** runs 7-gate pipeline: halt check, drawdown limits, news window, spread check, correlation check, position sizing, minimum confidence threshold
10. **If all gates pass:** Team 6 sector trader places order via cTrader or Bybit API
11. **Position lifecycle management:** TP1 close, SL to breakeven, trailing stop activation
12. **Trade logged to Supabase;** Telegram notification sent; analytics updated
13. **Feature vector stored** for ML training data collection

## 3.3 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Agent Framework | Paperclip (or LangGraph) | Latest | Agent orchestration, tool calling, multi-agent coordination |
| LLM Engine | Ollama (local) | Latest | Self-hosted LLM inference — no external API cost |
| LLM Models | llama3.1:8b, mistral:7b, CodeLlama:34b, mixtral:8x7b | Various | Right-sized per agent role |
| Backend API | Python FastAPI | 0.110+ | REST endpoints for all teams and frontend |
| Frontend | React 18 + Vite + TailwindCSS | Latest | 10-page trading dashboard |
| Charts | Recharts + lightweight-charts | Latest | Equity curves, sector heatmaps, candlestick charts |
| Database | Supabase (PostgreSQL) | Managed | Trade log, signals, performance, feature store |
| Cache | Redis | 7+ | OHLCV cache, session state, pub/sub for live updates |
| Workflow Engine | n8n | Latest | 6 core automated workflows |
| Secrets | HashiCorp Vault | Latest | API keys, broker credentials |
| cTrader | cTrader Open API (REST + WebSocket) | v2 | Forex and Commodities execution |
| Bybit | Bybit REST API v5 | v5 | Crypto and Stocks execution |
| Alerts | Telegram Bot API | Latest | Trade notifications, daily reports, system alerts |
| Market Data | OANDA, Polygon, Finnhub, Yahoo Finance, FRED, CFTC | Various | Multi-source OHLCV, news, macro, COT data |
| Container | Docker + Docker Compose | Latest | Reproducible deployment, service isolation |
| OS | Ubuntu 22.04 LTS / Kali Linux | LTS | Production server or dedicated trading machine |

---

# 4. Team Structure & Agent Roster

AgentFinance v5 organises all agents into eight operational teams under a Chief Orchestrator. The Analysis team retains the six philosophy-based departments from v4; all other teams are new in v5.

## CHIEF ORCHESTRATOR

The Chief Orchestrator is the top-level coordination agent that manages the entire system lifecycle. It schedules team workflows, distributes market briefings, monitors system health, triggers the weekly COT Alignment Report, and has override authority over all team decisions.

| Responsibility | Frequency | Output |
|---------------|-----------|--------|
| Activate kill zone schedules | Every 15 minutes | Team 2 scanner trigger |
| Distribute daily market briefing | Pre-market (06:00 local) | Summary to all teams |
| Distribute weekly COT Alignment Report | Sunday 18:00 | COT + Technical + Fundamental alignment per sector |
| Monitor team health & agent uptime | Continuous | Watchdog alerts via Telegram |
| Emergency stop (kill switch) | On breach of weekly limit | Close all positions, halt all teams |
| Weekly performance review trigger | Friday 18:00 | Analytics Team summary to dashboard |

## TEAM 1 — News & Market Data

**Responsibility:** Collect, process, and distribute structured intelligence reports across all five market sectors every 15 minutes. The team aggregates news, macro data, COT reports, and economic calendar events and forwards them to the appropriate Analysis agents and Scanner team.

| Agent | Role | Data Sources | Output |
|-------|------|--------------|--------|
| T1-A1 — Macro Intelligence Agent | Monitor GDP, CPI, PCE, interest rates, CB meetings | FRED, TradingEconomics, IMF, Central bank sites | Macro bias report per major economy |
| T1-A2 — News NLP Agent | Score headlines -1.0 to +1.0 per sector; 4hr rolling index | Finnhub, NewsAPI, Reuters, Bloomberg RSS | 4-hour sentiment index per sector |
| T1-A3 — Sector Data Collector | Fetch OHLCV, order book, volume for all monitored instruments | OANDA, Polygon, Yahoo Finance, Bybit | Cached OHLCV packets to Redis |
| T1-A4 — COT Report Agent | Parse CFTC COT weekly; calculate percentile; detect extremes | CFTC.gov, Barchart COT data | COT index per instrument; alignment report |

### API Endpoints provided by the Scanner team:

- `/scan-sector/{sector}` — Scan a single sector and return ranked opportunities
- `/scan-all-sectors` — Scan all five sectors in parallel; return aggregated opportunity list
- `/sector-opportunities/{sector}` — Return top-5 current opportunities for a sector with confidence scores

## TEAM 2 — Live Markets Scanner

**Responsibility:** Continuously scan all five market sectors for active trading opportunities. Each sector has a dedicated scanner agent that calls /scan-sector/{sector} and /sector-opportunities/{sector} endpoints. The Scanner Coordinator aggregates results and routes them to Team 3.

| Agent | Sector | Scan Frequency | Methods |
|-------|--------|----------------|---------|
| T2-A1 — Forex Scanner | Forex (28+ pairs) | Every 5 minutes during kill zones | Kill zone detection, OB/FVG scan, MA crossover, currency strength matrix |
| T2-A2 — Commodities Scanner | Gold, Oil | Every 5 minutes | ICT structure scan, commodity-FX correlation check, supply/demand levels |
| T2-A3 — Stocks Scanner | Top 100 US equities | Every 15 minutes | Earnings calendar, momentum scan, volume surge, MACD divergence screen |
| T2-A4 — Indices Scanner | SP500, NAS100, DAX, FTSE, Nikkei | Every 5 minutes | VIX correlation, HTF structure, breakout detection, regime classification |
| T2-A5 — Crypto Scanner | BTC, ETH, top-30 alts | Every 5 minutes | FVG scan, breakout scan, volume analysis, TWAP opportunity detection |

## TEAM 3 — Analysis (6 Departments)

**Responsibility:** Perform deep multi-methodology analysis on candidate opportunities identified by Team 2. The 21 analysis agents are organised into six departments, each specialising in a distinct analytical philosophy. All six departments run concurrently via asyncio.

| Dept | Department | Philosophy | Agents | Strategies |
|------|------------|------------|--------|------------|
| 1 | Fundamental Analysis | Macro, CB policy, earnings, economic cycles | Agents 01-04 | 7 strategies |
| 2 | Technical Analysis | Price action, indicators, multi-TF analysis | Agents 05-07 | 10 strategies |
| 3 | Sentiment Analysis | COT, retail positioning, news NLP, fear/greed | Agents 08-10 | 4 strategies |
| 4 | Intermarket Analysis | Cross-asset correlations, bonds/commodities/FX | Agents 11-13 | 3 strategies |
| 5 | Quantitative/Systematic | Algorithmic strategies, statistical models | Agents 14-17 | 3 strategies + 7 tactics |
| 6 | SMC/ICT Analysis | Order blocks, liquidity, structure, kill zones | Agents 18-21 | 18 strategies |

### Department 1 — Fundamental Analysis (Agents 01–04)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 01 — Macro Economics | Global macro conditions and directional bias | GDP/CPI/PCE, yield curve shape, growth-inflation quadrant, CB meeting calendar, rate probability tracking |
| 02 — Forex Fundamentals | Currency pair fundamentals and carry analysis | 28+ pairs monitored, currency strength matrix, carry trade scoring, economic surprise index, CB policy divergence |
| 03 — Commodities Fundamental | Gold and oil supply/demand dynamics | EIA weekly reports, OPEC decisions, gold-dollar inverse, commodity-FX leading indicator analysis |
| 04 — Equity Fundamental | Stock and index earnings and valuation | Earnings calendar, P/E relative valuation, sector rotation, revenue surprise scoring |

### Department 2 — Technical Analysis (Agents 05–07)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 05 — Price Action | Structure and displacement analysis | Multi-TF trend identification, displacement detection (body >= 70%), VWAP alignment, key level mapping |
| 06 — Indicators | Oscillator and momentum analysis | RSI/MACD divergence, Bollinger Band squeeze, Double BB zone classification, ATR volatility, Perfect Order (7/21/50 EMA) |
| 07 — Trend Analysis | EMA systems and trend strength | EMA 5/13/50/200 alignment, 20-day breakout detection, MTF momentum (Miner), MA crossover signals, ADX trend classification |

### Department 3 — Sentiment Analysis (Agents 08–10)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 08 — COT Sentiment | CFTC positioning and commercial/speculator extremes | COT Index (52-week percentile), commercial vs large spec divergence, position unwinding detection, weekly COT alignment report |
| 09 — Market Sentiment | VIX, retail positioning, fear/greed | VIX-EMA crossover, VIX-S&P inverse correlation, VIX COT, retail positioning from broker data |
| 10 — News NLP | News sentiment scoring and divergence | Headline scoring (-1 to +1), 4hr rolling sentiment index, source weighting, price-sentiment divergence detection |

### Department 4 — Intermarket Analysis (Agents 11–13)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 11 — Bond-Equity Analyst | Yield curve and equity market correlation | Bond spread as leading indicator, yield curve inversion probability, credit spread monitoring, risk-on/risk-off classification |
| 12 — Commodity-FX Analyst | Commodity prices as FX leading indicators | Gold/AUD, Oil/CAD, Copper/AUD correlations, divergence detection, Z-score alerts when pairs decouple |
| 13 — Correlation Monitor | Cross-sector correlation tracking | Rolling correlation matrix (all 5 sectors), correlation breakdown alerts, intermarket divergence scanner (15-min cycle) |

### Department 5 — Quantitative/Systematic Analysis (Agents 14–17)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 14 — Statistical Modeller | Quantitative signals and mean reversion | Range trading (Bollinger + price levels), breakout confirmation with volume, statistical divergence scoring |
| 15 — Volume Analyst | Volume profile and institutional flow | Volume surge detection, OBV divergence, VWAP execution quality, volume dry-up signals |
| 16 — Algorithmic Execution | Smart order execution tactics | VWAP/TWAP/POV execution for large orders, ADR-based position sizing, trailing one-bar high/low entry |
| 17 — Parameter Optimiser | Strategy parameter management and testing | Parameter version control, performance attribution per strategy, A/B test coordination with Analytics team |

### Department 6 — SMC/ICT Analysis (Agents 18–21)

| Agent | Role | Key Capabilities |
|-------|------|-------------------|
| 18 — Order Block & FVG | Order block detection and FVG analysis | OB quality ranking (1-5), FVG strength ranking (1-5), breaker block identification, 70.5% OTE level calculation |
| 19 — Market Structure | BOS/CHoCH/MSS identification | Multi-TF structure mapping (Weekly to M15), CHoCH vs MSS distinction, displacement confirmation (body >= 60%) |
| 20 — Liquidity Analyst | Liquidity pools and sweep detection | Session high/low mapping, equal highs/lows detection, Judas Swing identification, Power of Three (AMD) phase tracking |
| 21 — Session/Kill Zone | Kill zone timing and session analysis | Full 5-window schedule (Asian/London/LondonOpen/NY/LondonClose), ADR consumption tracking, Silver Bullet window management |

## TEAM 4 — Trade Signals (Debate Mechanism)

**Responsibility:** Replace signal fusion with a structured debate. Every candidate signal is argued by three analyst roles before the Fund Manager produces the final trade decision. This mechanism produces explainable, auditable decisions with quantified confidence scores.

| Role | Perspective | Responsibilities |
|------|-------------|-------------------|
| Bull Analyst | Argues the long/buy case | Cite supporting analysis from all 6 departments; identify strongest confluence factors; project upside target with probability |
| Bear Analyst | Argues the short/sell case | Challenge the Bull case; identify counter-signals; stress-test the setup against opposing HTF structure; flag manipulation risk |
| Neutral/Risk Analyst | Stress-tests both cases | Evaluate overall risk; check spread, correlation, news proximity; apply Checklist Validator scores; recommend position adjustment |
| Fund Manager | Final decision maker | Synthesise all three cases; produce final LONG/SHORT/NO TRADE decision with 0-100 confidence score; set position parameters |

### Debate rules:

- **Minimum confluence:** 3 of 6 departments must provide supporting signals (hard rule)
- **Confidence threshold:** Fund Manager confidence must be >= 65/100 for entry; >= 80/100 for full position size
- **Checklist gate:** Pre-trade checklist must score >= 7/9 (ICT criteria) before debate begins
- **Expired signals:** Signals past their confidence half-life are not debated
- **Debate transcript:** Full Bull/Bear/Neutral arguments logged to Supabase and visible on dashboard

## TEAM 5 — Risk & Portfolio Management

**Responsibility:** Apply the 7-gate risk pipeline to every trade approved by Team 4. Calculate position size, enforce daily/weekly loss limits, check portfolio correlation, and maintain the portfolio state. Has absolute veto power over all trades.

### 7-Gate Risk Pipeline

| Gate | Check | Action on Fail |
|------|-------|----------------|
| Gate 1 — System Halt | Is the kill switch active or system in paper mode? | Block all live trades; route to paper trade |
| Gate 2 — Daily Loss Limit | Has daily P&L dropped below -5% of account? | Stop all trading for the day; alert via Telegram |
| Gate 3 — Weekly Loss Limit | Has weekly P&L dropped below -10% of account? | Skip next week; trigger manual review alert |
| Gate 4 — News Window | Is high-impact news within 30 minutes? | Block scalp/short-term entries; allow position entries with larger stop |
| Gate 5 — Spread Check | Is current spread > 2x the historical average? | Block entry; log spread spike; retry after 5 minutes |
| Gate 6 — Correlation Check | Does new position increase portfolio correlation above 0.7? | Reduce position size by 50% or block if correlation > 0.85 |
| Gate 7 — Minimum Confidence | Is Fund Manager confidence score >= 65? | Block if < 65; reduce size by 30% if 65-75; full size if >= 75 |

### Sub-Agents

| Sub-Agent | Role |
|-----------|------|
| Risk Manager | Applies all 7 gates; calculates position size using ATR-based stop distance; enforces ADR consumption limit (80% rule) |
| Portfolio Monitor | Tracks all open positions; calculates net delta per sector; monitors correlation matrix; triggers rebalancing alerts |
| Checklist Validator | Runs automated ICT pre-trade checklist (9 points) before debate; blocks debate for signals scoring < 7/9 |

## TEAM 6 — Live Traders

**Responsibility:** Execute trades via cTrader and Bybit APIs. Each sector has a dedicated trader agent responsible for order placement, position management, and trade lifecycle (TP1 close → SL to breakeven → trailing stop). Implements Category B execution tactics.

| Agent | Sector | Execution Venue | Execution Tactics Used |
|-------|--------|-----------------|------------------------|
| T6-A1 — Forex Trader | Forex (all pairs) | cTrader Open API (port 9009) | VWAP execution, POV participation, trailing one-bar high/low, two-unit management |
| T6-A2 — Commodities Trader | Gold, Oil | cTrader Open API | VWAP execution, ADR-based sizing, swing breakout entry trigger |
| T6-A3 — Stocks Trader | Top 100 US equities | Bybit REST API v5 | TWAP execution, two-unit management, trailing stop |
| T6-A4 — Indices Trader | SP500, NAS100, DAX, etc. | cTrader + Bybit | VWAP execution, ADR sizing, HTF trailing stop |
| T6-A5 — Crypto Trader | BTC, ETH, top-30 alts | Bybit REST API v5 | TWAP execution, POV participation, tight trailing stop |

### Position Lifecycle (all sectors):

- **TP1 at 1R:** Close 25-30% of position; move stop to breakeven
- **TP2 at 2R:** Close additional 25-30%; trail stop to lock profit
- **TP3 at 3R:** Activate dynamic trailing stop
- **TP4 at structure extreme:** Close full remaining position

## TEAM 7 — Backtesting

**Responsibility:** Run automated strategy backtests on historical data. Validate strategy parameters before live deployment. Maintain a library of vetted strategy configurations. Interface with the parameter version control system.

| Agent | Role | Output |
|-------|------|--------|
| T7-A1 — Backtesting Engine | Run full historical backtests on all 46 strategies across 5 sectors | Win rate, P&L, max drawdown, Sharpe, Sortino per strategy per sector |
| T7-A2 — Parameter Optimiser | Walk-forward optimisation of strategy parameters | Optimal parameter sets per strategy; version-controlled change log |
| T7-A3 — Synthetic Data Generator | Monte Carlo simulation for low-frequency strategies (ICT-07/08) | Synthetic price scenarios for position strategy validation; 1000+ market cycles |

## TEAM 8 — Analytics

**Responsibility:** Track all system performance data, detect latent patterns, run A/B tests, and feed the meta-evaluation agent that monitors individual agent accuracy over time.

| Agent | Role | Output |
|-------|------|--------|
| T8-A1 — Meta-Evaluation Agent | Monitor performance of all 21 analysis agents; detect accuracy degradation | Agent specialisation scores; retraining triggers; weekly performance report |
| T8-A2 — Latent Pattern Detector | Find hidden cross-sector patterns via PCA and correlation analysis | Pattern alerts: new inter-market relationships; anomaly detection; regime shift early warning |
| T8-A3 — Performance Tracker | Maintain equity curve, P&L attribution, strategy performance metrics | Strategy P&L attribution table; Sharpe/Sortino per strategy; rolling win rate charts |
| T8-A4 — A/B Test Manager | Compare agent configurations, strategy parameters, and debate formats | A/B test results: statistical significance, effect size; recommendation to Parameter Optimiser |

---

# 5. Strategy Registry

The AgentFinance v5 strategy registry contains 46 signal strategies across 5 thematic blocks, plus 7 execution tactics used by the Live Traders and Risk teams. All strategies have been reviewed, updated to v2 (ICT strategies), and assigned to specific Analysis department agents.

## BLOCK 1 — ICT / Smart Money Concepts (18 strategies)

**Global v2 updates applied to all ICT strategies:**

- OTE entry level: 70.5% primary (replaces generic 62%); 61.8% secondary; 78.6% tertiary
- OB quality filter: Ranks 1-3 for entry (Rank 5 = skip always)
- FVG strength filter: Strength 1-3 for entry (Strength 5 = skip)
- Daily loss limit: 5% of account — stop trading for the day
- Weekly loss limit: 10% of account — skip next week
- Max concurrent trades: 3 positions
- 4-tier TP structure for swing/position tier: TP1=1R, TP2=1.5-2R, TP3=3R, TP4=structure extreme
- Standardised trade log template applied to all strategies

| ID | Strategy | Tier | Target | Key v2 Updates |
|----|----------|------|--------|----------------|
| ICT-01 | Micro-Sweep Scalp | Scalping | 20 pips | OB rank 1-3; FVG strength 1-3; 70.5% OTE; MSS alternate (50% size); expanded kill zones |
| ICT-02 | PD Array FVG Scalp | Scalping | 25 pips | FVG strength 1-3 critical filter; 70.5% OTE; expanded kill zones; MSS alternate if FVG weak (50% size) |
| ICT-03 | Kill-Zone Pulse | Short-term | 30-50 pips | 70.5% OTE replaces 62%; MSS dual-path (100%/75%/skip); OB rank filter added |
| ICT-04 | Weekly Bias Expansion | Short-term | 50 pips | 70.5% OTE; FVG strength 1-3; MSS alternate at 75% size; Tue/Wed only rule |
| ICT-05 | CHoCH Momentum Swing | Swing | 75-100 pips | Breaker block as alternate entry; MSS dual-path; 4-tier TP structure; OB rank 1-4 acceptable |
| ICT-06 | Sell-Side Redistribution | Swing | 75-100 pips | Bearish breaker block entry rules added; 4-tier TP; crash vs controlled decline rule |
| ICT-07 | HTF Structure Break | Position | 200-300 pips | Breaker block alternate; 4-tier TP (100/180/250/weekly); OB rank 1-4; weekly close management |
| ICT-08 | Discount-Premium Position | Position | 300-500 pips | 70.5% OTE replaces midpoint for entry; breaker block entry; 4-tier TP; 20-week IPA range; 2.5% risk |
| ICT-09 | Silver Bullet Time-Window | Scalp/Short hybrid | 15-30 pips | NEW: 3 time windows (3-4AM, 10-11AM, 2-3PM NY); minimum movement framework; window failure rule |
| R2-007 | Market Structure Shift (MSS) | Structural signal | Varies | Distinct from CHoCH — no prior BOS required; 75% position size; faster entries |
| R2-009 | Breaker Block Trading | Structural reversal | Varies | Failed OB that flips; bullish: buy at top +5; bearish: sell at bottom -5; alternate entry in ICT-05 to 08 |
| R2-010 | Liquidity Grab / Judas Swing | Manipulation play | Varies | Combines stop hunt sweep with immediate reversal entry; target next liquidity pool |
| R2-011 | Optimal Trade Entry (OTE) | Precision entry | — | 70.5% primary; 61.8% secondary; 78.6% tertiary; always within kill zone |
| R2-012 | Power of Three (AMD) | Cycle phase | — | Accumulation/Manipulation/Distribution cycle mapping; combined with kill zones |
| R2-013 | Kill Zone Timing | Session filter | — | Full 5-window schedule: Asian/London/LondonOpen/NY/LondonClose; gating for all ICT entries |
| R2-028 | BTMM Three-Day Cycle | Market maker cycle | — | MM driven/Retail driven/MM return cycle; EMAs 5/13/50/200, TDI, ADR, pivot points |
| NEW-A | MACD Divergence + SMC | Confluence signal | Varies | MACD divergence + OB rank 1-3 + structure confirmation; bridges Technical and SMC departments |
| NEW-B | Fibonacci Sweep | Precision reversal | Varies | 61.8% Fib + candlestick reversal + OB confirmation + 70.5% OTE entry |

## BLOCK 2 — Technical Analysis (10 strategies)

Price pattern strategies removed per final strategy review. 10 indicator and trend-based strategies retained.

| ID | Strategy | Sectors | Timeframe | Department Agent |
|----|----------|---------|-----------|------------------|
| STRAT_003 | Technical Divergence Trading | All | H1-D1 | Agent 06 — Indicators |
| STRAT_004 | Moving Average Crossover | All | H1-D1 | Agent 07 — Trend |
| STRAT_006 | MACD Trading | All | H1-D1 | Agent 06 — Indicators |
| STRAT_007 | Bollinger Bands Trading | All | M15-D1 | Agent 06 — Indicators |
| STRAT_010 | Multiple Time Frame Analysis | All | Multi-TF | Agent 05 — Price Action |
| STRAT_011 | Double Bollinger Bands (Lien) | FX, Commodities | H1-D1 | Agent 06 — Indicators |
| STRAT_015 | 20-Day Breakout Trade | All | D1 | Agent 07 — Trend |
| STRAT_017 | Perfect Order Strategy | All | H4-D1 | Agent 07 — Trend |
| R1-013 | MTF Momentum (Miner) | All | Multi-TF | Agent 07 — Trend |
| R2-019 | Double MA Crossover | All | H1-D1 | Agent 07 — Trend |

## BLOCK 3 — Fundamental & Intermarket (7 strategies)

| ID | Strategy | Sectors | Signal Type | Department Agent |
|----|----------|---------|-------------|------------------|
| STRAT_018 | Pairing Strong vs Weak Currency | Forex | Currency strength matrix | Agent 02 — FX Fundamentals |
| STRAT_019 | Carry Trade | Forex | Rate differential | Agent 02 — FX Fundamentals |
| STRAT_020 | Macro Event-Driven Trade | FX, Commodities, Indices | Event trigger | Agent 01 — Macro Economics |
| STRAT_021 | Commodity as Leading Indicator | FX, Commodities | Intermarket lead | Agent 12 — Commodity-FX |
| STRAT_022 | Bond Spreads as Leading Indicator | FX, Indices | Intermarket lead | Agent 11 — Bond-Equity |
| STRAT_025 | Central Bank Intervention | Forex | CB regime signal | Agent 01 — Macro Economics |
| STRAT_026 | Intermarket Analysis (Murphy) | All | Cross-asset regime | Agent 13 — Correlation Monitor |

## BLOCK 4 — Sentiment & Volatility (4 strategies)

| ID | Strategy | Sectors | Signal Type | Key Notes |
|----|----------|---------|-------------|-----------|
| R2-001 | VIX-EMA Crossover | Indices, Stocks | VIX directional | 20-EMA on VIX; sell when EMA crosses above VIX; buy when crosses below |
| R2-002 | VIX-S&P 500 Correlation | Indices, Stocks | Inverse correlation | VIX rising = short S&P; VIX falling = long S&P; exploits documented inverse relationship |
| R2-003 | VIX COT Report Sentiment | Indices, Stocks | CFTC positioning | VIX futures extremes -> contrarian signal; combined with R2-001 for highest confidence |
| COT-001 | COT Report Trading (Enhanced) | FX, Commodities | Smart money positioning | Commercial extremes (5-10yr percentile); fade large specs at extremes; price action confirmation required |

## BLOCK 5 — Range, Breakout & Volume (3 strategies)

| ID | Strategy | Sectors | Signal Type | Notes |
|----|----------|---------|-------------|-------|
| R2-016 | Range Trading | All | Mean reversion | Horizontal range boundaries; buy support / sell resistance; Bollinger squeeze complement |
| R2-017 | Breakout Trading | All | Momentum | Close beyond established range with volume confirmation; measured move target; complements STRAT_015 |
| R2-018 | Volume Trading | Stocks, Crypto | Volume signal | Volume surge confirms price moves; OBV divergence flags reversals; volume dry-up = exhaustion |

## BLOCK 6 — Execution Tactics (7 tactics — Category B)

These are not signal generators. Used by Team 6 (Live Traders) and Team 5 (Risk) for order placement and position lifecycle management.

| ID | Tactic | Used By | Application |
|----|--------|---------|--------------|
| B-01 | VWAP Execution | Forex Trader, Commodities Trader | Slice large orders by historical intraday volume profile; reduces market impact on liquid pairs |
| B-02 | TWAP Execution | Crypto Trader, Stocks Trader | Uniform time-slice execution where VWAP curve unavailable; preferred for Bybit execution |
| B-03 | POV / Participation Rate | Forex Trader | Execute as 10-25% of live volume on the most liquid FX pairs |
| B-04 | Trailing One-Bar High/Low Entry | All Traders | Precise entry trigger — 1-bar break of swing extreme; used with CHoCH and BOS setups |
| B-05 | Swing Breakout Entry Trigger | All Traders | Structural entry on swing breakout confirmation; stop at opposite swing extreme |
| B-06 | Two-Unit Trade Management | Risk Team, All Traders | Unit 1 = quick TP at 38.2-50% retracement; Unit 2 = trail stop for full trend capture |
| B-07 | ADR-Based Position Sizing | Risk Team | Average Daily Range used to set stop distance and position size; sourced from BTMM methodology |

---

# 6. Enhancements & Improvements Plan

The following 26 enhancements have been identified and prioritised across four tiers. P0 enhancements are built into the base system as non-optional features. P1 enhancements are built in Phase 2. P2 and P3 are roadmap items.

| Enhancement | Impact | Effort | Priority | Phase |
|-------------|--------|--------|----------|-------|
| Regime-Adaptive Strategy Selection | ★★★★★ | Medium | P0 | 1 |
| Multi-TF Confluence Scoring | ★★★★★ | Medium | P0 | 1 |
| Paper Trading with Live Mirroring | ★★★★★ | Low | P0 | 1 |
| Human-in-the-Loop Approval Gates | ★★★★★ | Medium | P0 | 1 |
| Feature Store for ML | ★★★★★ | Medium | P0 | 1 |
| Economic Calendar Intelligence Engine | ★★★★★ | Medium | P1 | 2 |
| Strategy Performance Attribution | ★★★★★ | Medium | P1 | 2 |
| Confidence Decay System | ★★★★★ | Medium | P1 | 2 |
| Correlation-Adjusted Sizing | ★★★★ | Medium | P1 | 2 |
| Dynamic ATR-Based Stops | ★★★★ | Medium | P1 | 2 |
| Tiered Alert Priority System | ★★★★ | Low | P1 | 2 |
| Pre-Trade Checklist Validator | ★★★★ | Low | P1 | 2 |
| Signal Confidence Visual (dashboard) | ★★★★ | Low | P1 | 2 |
| Session Liquidity Profiling | ★★★★ | Medium | P2 | 3 |
| Intermarket Divergence Alerts | ★★★★ | Low | P2 | 3 |
| Opportunity Pipeline View | ★★★★ | Medium | P2 | 3 |
| Weekly Strategy Review Automation | ★★★★ | Medium | P2 | 3 |
| Debate Memory & Consensus History | ★★★ | Low | P2 | 3 |
| Slippage Monitoring | ★★★ | Low | P2 | 3 |
| P&L Heatmap by Strategy/Sector | ★★★ | Low | P2 | 3 |
| Agent Live Activity Feed | ★★★ | Low | P2 | 3 |
| COT Flow Tracker | ★★★★ | Low | P2 | 3 |
| False Breakout Filter | ★★★★ | Low | P2 | 3 |
| Synthetic Data Generator | ★★★★ | High | P3 | 4 |
| Parameter Version Control | ★★★ | Low | P3 | 4 |
| Multi-Source Sentiment Scoring | ★★★★ | Medium | P3 | 4 |

## 6.1 P0 Enhancements — Built Into Base System

### Regime-Adaptive Strategy Selection

Every analysis cycle begins by classifying the current market regime using ADX, ATR, and Bollinger Band Width. The classification (TRENDING / RANGING / TRANSITIONING) determines which strategy blocks are eligible:

- **TRENDING** regime: ICT swing/position strategies (ICT-05 to 09), Perfect Order, 20-Day Breakout, HTF Structure Break
- **RANGING** regime: Range Trading (R2-016), Double Bollinger Bands, Bollinger mean reversion, ICT kill zone scalps
- **TRANSITIONING** regime: CHoCH, MSS, Breaker Blocks, Intermarket Divergence signals only

Strategies that are ineligible for the current regime are suppressed. This single filter is estimated to improve win rate by 8-12%.

### Multi-TF Confluence Scoring

Every signal must be corroborated across at least two timeframes before reaching the Trade Signals team. The MTF confluence score (0-100) is calculated as: HTF alignment (40 pts) + Intermediate confirmation (30 pts) + Entry timeframe setup (30 pts). Signals scoring < 60 are discarded before debate.

### Paper Trading with Live Mirroring

The system operates in two modes:

- **Paper mode:** All signals generated, debated, and cleared through the full pipeline, but orders are placed to a simulated broker rather than live venues. P&L, fill prices, and execution quality are recorded as if live.
- **Live mode:** Identical pipeline; only difference is order routing.

The go-live switch is a single environment variable (`PAPER_MODE=false`), making live deployment instant with zero code changes. All system components (risk gates, position sizing, lifecycle management) work identically in both modes.

### Human-in-the-Loop Approval Gates

Three approval gates are embedded in the pipeline for human oversight:

1. **Pre-Debate Gate:** Human can review and reject signals before Bull/Bear debate
2. **Pre-Trade Gate:** Human can review and approve/reject trades before execution
3. **Emergency Stop:** Human can trigger full system halt via Telegram

Each gate produces a log entry, decision timestamp, and optional rationale visible on the dashboard.

### Feature Store for ML

Every signal, debate outcome, trade, and performance metric generates a labelled feature vector stored in Supabase:

| Feature | Description | Type |
|---------|-------------|------|
| Market regime | TRENDING/RANGING/TRANSITIONING | Categorical |
| Confluence count | Number of supporting departments (0-6) | Integer |
| MTF score | Multi-timeframe confluence (0-100) | Float |
| Bull/Bear/Neutral votes | Debate outcome per role | Enum |
| Confidence score | Fund Manager confidence (0-100) | Float |
| Risk gates passed | Binary vector (7 gates) | Bitfield |
| Position size | Calculated position size in units | Float |
| P&L (R multiples) | Profit/loss as risk multiple | Float |
| Trade duration | Time in market (minutes) | Integer |

This enables the ML/RL phase (Phase 4) to train models on high-quality, labelled data from day one.

## 6.2 P1 Enhancements — Phase 2

### Economic Calendar Intelligence Engine

An embedded economic calendar engine that:

- Pre-scans high-impact news (NFP, CB meetings, GDP, CPI) 24 hours ahead
- Auto-generates "avoid trade" windows for each instrument
- Adjusts risk parameters dynamically during high-volatility events

### Strategy Performance Attribution

Every trade is attributed to a specific strategy, agent, and sector. Attribution data is stored per-trade and aggregated to:

- Win rate per strategy
- P&L per strategy
- Sharpe/Sortino per strategy
- Agent accuracy scores (derived from whether their signal was part of winning trades)

### Confidence Decay System

Each strategy tier is assigned a confidence half-life:

| Tier | Example | Half-Life |
|------|---------|-----------|
| Scalp | ICT-01, ICT-02 | 15 minutes |
| Short-term | ICT-03, ICT-04 | 60 minutes |
| Swing | ICT-05, ICT-06 | 4 hours |
| Position | ICT-07, ICT-08 | 24 hours |

After the half-life expires, confidence drops by 50%. After 2 half-lives (e.g., 30 min for scalp), the signal is automatically archived and no longer eligible for debate.

### Correlation-Adjusted Sizing

The Risk team's existing correlation check (Gate 6) is enhanced with dynamic sizing:

- Portfolio correlation matrix updated every 15 minutes
- New position sizing reduced inversely to correlation increase
- Full blocking only at 0.85+ correlation threshold

### Dynamic ATR-Based Stops

Stop distance is calculated as a multiple of the instrument's ATR (14), rather than fixed pips:

| Strategy Tier | ATR Multiple | Notes |
|---------------|--------------|-------|
| Scalp | 0.5x ATR | Tight stops for quick moves |
| Short-term | 1.0x ATR | Standard |
| Swing | 1.5x ATR | Wider for swings |
| Position | 2.0x ATR | Wide stops, higher R |

### Tiered Alert Priority System

Alerts are categorised by priority with escalating notification paths:

| Priority | Trigger | Notification |
|----------|---------|--------------|
| P0 — Critical | Daily loss limit hit, emergency stop | Immediate Telegram + SMS |
| P1 — High | Trade closed at 3R+, weekly limit approach | Telegram to main channel |
| P2 — Medium | New signal generated, debate started | Dashboard feed only |
| P3 — Low | Agent health check, COT update | Daily digest |

### Pre-Trade Checklist Validator

Automated ICT 9-point checklist run before debate:

1. Kill zone active
2. Bull/Bear structure confirmed
3. OTE within zone
4. OB quality >= 3 or FVG strength >= 3
5. Liquidity pool identified
6. ADR consumption < 80%
7. No high-impact news within 30 min
8. Spread within normal range
9. Regime alignment confirmed

Signals scoring < 7/9 are blocked before debate begins.

### Signal Confidence Visual (dashboard)

Each signal on the dashboard displays:

- Confidence score gauge (0-100)
- Confluence count (bars per department)
- Half-life indicator (time remaining)
- Bull/Bear/Neutral vote breakdown

## 6.3 P2 Enhancements — Phase 3

### Session Liquidity Profiling

Track liquidity pool migration patterns per session:

- Asian session high/lows as liquidity for London
- London session sweeps, then liquidity shifts to NY
- Session close as liquidity pool for next session open

### Intermarket Divergence Alerts

Cross-sector divergence detection:

- Asset X moves but correlated asset Y does not confirm
- Z-score alerts when divergence exceeds 2 std dev
- 15-minute scan cycle

### Opportunity Pipeline View

A Kanban-style pipeline view on the dashboard showing all candidate signals at each stage:

- Scanned → Analysed → Debated → Approved → Executed → Closed

### Weekly Strategy Review Automation

Automated Friday 18:00 report containing:

- Top 3 performing strategies (by R)
- Bottom 3 strategies
- Agent leaderboard (accuracy scores)
- Recommended parameter adjustments
- Next week's regime forecast

### Debate Memory & Consensus History

Store debate transcripts and aggregate consensus patterns:

- Track which agent perspectives win most often
- Identify bias patterns in Bull/Bear/NNeutral arguments
- Use consensus history to weight future debates

### Slippage Monitoring

Track and report execution slippage per trade:

- Ordered price vs filled price
- Slippage in pips and R-multiple
- Venue comparison (cTrader vs Bybit)

### P&L Heatmap by Strategy/Sector

Visual heatmap on the dashboard:

- Rows: Strategies
- Columns: Sectors
- Cell: Aggregate P&L (green/red gradient)

### Agent Live Activity Feed

Real-time scrolling feed on the dashboard showing:

- "Agent 18: OB detected on GBPUSD"
- "Agent 05: CHoCH confirmed on XAUUSD"
- "Fund Manager: Signal approved — LONG AUDJPY, conf=78"

### COT Flow Tracker

Weekly COT data parsed and visualized:

- Commercial net positioning (52-week percentile)
- Large speculator net positioning
- Historical divergence from price
- Trading signals from extremes

### False Breakout Filter

Additional validation before entry:

- Volume check — breakout must have 1.5x average volume
- Close confirmation — close beyond level, not just wick
- Retest requirement — level must be retested within 3 bars

## 6.4 P3 Enhancements — Phase 4 (ML/RL)

### Synthetic Data Generator

Monte Carlo simulation engine for low-frequency strategies (ICT-07, ICT-08):

- 1000+ synthetic price paths per strategy
- Inject liquidity sweeps, stop hunts, and false breakouts
- Validate strategy robustness before live deployment

### Parameter Version Control

Full versioning of all strategy parameters:

- Git-like commit history for every parameter change
- Rollback capability to any previous version
- A/B test linking to parameter commits

### Multi-Source Sentiment Scoring

Expand from single-source (Finnhub/NewsAPI) to multi-source:

- Reddit, Twitter/X, StockTwits sentiment
- Discord trading group sentiment (where available)
- Weighted aggregate sentiment score

---

# Appendix: Project Information Summary

| Attribute | Value |
|-----------|-------|
| Architecture | Multi-Team — 8 Operational Teams + Chief Orchestrator |
| Analysis Agents | 21 Agents across 6 Analysis Departments |
| Total Teams | 8 Teams (News, Scanner, Analysis, Signals, Risk, Traders, Backtesting, Analytics) |
| Strategies | 46 Signal Strategies + 7 Execution Tactics |
| Market Sectors | Forex · Commodities (Gold/Oil) · Stocks · Indices · Crypto |
| Backend | Python FastAPI + Ollama LLM Engine |
| Frontend | React.js + Vite Dashboard |
| Execution | cTrader Open API + Bybit API |
| Infrastructure | Redis · Supabase · Vault · n8n · Telegram |
| Version | v5.0 — April 2026 |
| Status | Production-Ready Blueprint |

---

*Generated from gen_v5.js — AgentFinance v5.0 Project Plan Generator*