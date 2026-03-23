# AgentFinance v3 — Complete Project Summary
> **Date**: March 2026 | **Platform**: Kali Linux | **Target**: Autonomous FX/Commodities Trading System
> **Demo Account**: Pepperstone #46729678 (cTrader)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [28 AI Agents](#3-28-ai-agents)
4. [Trading Engines](#4-trading-engines)
5. [Execution & Risk Layer](#5-execution--risk-layer)
6. [Skills Library](#6-skills-library)
7. [n8n Workflows](#7-n8n-workflows)
8. [cTrader Docker REST API](#8-ctrader-docker-rest-api)
9. [React Dashboard](#9-react-dashboard)
10. [Installation](#10-installation)
11. [Quick Start Commands](#11-quick-start-commands)
12. [Risk Management Rules](#12-risk-management-rules)
13. [Data Sources & APIs](#13-data-sources--apis)
14. [Rebuild Instructions](#14-rebuild-instructions)
15. [Architecture Diagram](#15-architecture-diagram)

---

## 1. Overview

**AgentFinance v3** is a production-grade autonomous trading system combining 28 specialized AI agents, Smart Money Concepts (SMC) strategy engine, 80+ technical indicators, multi-asset coverage (FX, commodities, indices, equities, crypto), vectorbt-powered backtesting, and live cTrader execution via Pepperstone.

The system evolved from v2 (investment intelligence) into a full-cycle trading platform. It runs on Kali Linux with Paperclip agent orchestration, n8n workflow automation, and a React dashboard for monitoring.

**Key numbers:**
- 28 AI agents across 7 departments
- 41 trading skills across 8 categories
- 5 n8n automation workflows
- 4 trading engines (SMC, technical, session/kill-zones, data fetcher)
- 3 execution modules (cTrader client, risk manager, pipeline)
- 1 Docker REST API container for cTrader
- 1 React dashboard (7 tabs, all components)
- ~23,000 total lines of code

---

## 2. Project Structure

```
AgentFinance/
├── agentfinance/                          # Main project directory
│   ├── README.md                          # System overview
│   ├── .env.example                       # Environment template
│   ├── .env.template                      # Legacy template
│   ├── agent_runner.py                    # Master CLI orchestrator (476 lines)
│   │
│   ├── agents/                            # 28 agents (YAML + Python)
│   │   ├── README.md                      # Agent manifest
│   │   ├── public/                        # Department 1: Agents 01-06
│   │   ├── private/                       # Department 2: Agents 07-12
│   │   ├── research/                     # Department 3: Agents 13-14
│   │   ├── ops/                          # Department 4: Agents 15-18
│   │   ├── trading/                      # Department 5-6: Agents 19-28
│   │   │   ├── 19-forex-intelligence.yaml + forex_intelligence.py
│   │   │   ├── 20-commodities-intelligence.yaml + commodities_intelligence.py
│   │   │   ├── 21-indices-intelligence.yaml + indices_intelligence.py
│   │   │   ├── 22-smc-strategy.yaml + smc_strategy.py
│   │   │   ├── 23-technical-analysis.yaml + technical_analysis.py
│   │   │   ├── 24-fundamental-analysis.yaml + fundamental_analysis.py
│   │   │   ├── 25-sentiment-intelligence.yaml + sentiment_intelligence.py
│   │   │   ├── 26-news-intelligence.yaml + news_intelligence.py
│   │   │   ├── 27-backtesting.yaml + backtesting.py
│   │   │   └── 28-live-trading.yaml + live_executor.py
│   │   │
│   │   ├── public/                       # (also contains: sec_filings, stock_data, financials, crypto, holdings)
│   │   ├── private/                      # (also contains: companies, funding, funds, deals, investors, debt)
│   │   ├── research/                     # (also contains: web_scraping, deep_research)
│   │   └── ops/                          # (also contains: portfolio, reporting, compliance, supervisor)
│   │
│   ├── trading/                          # Core trading engine
│   │   ├── README.md                      # Trading module overview
│   │   ├── engines/
│   │   │   ├── smc_engine.py             # SMC methodology (936 lines)
│   │   │   ├── technical_engine.py       # 80+ indicators (992 lines)
│   │   │   └── session_engine.py         # Kill zones + COT (760 lines)
│   │   ├── execution/
│   │   │   ├── ctrader_client.py        # cTrader TCP/Protobuf client (844 lines)
│   │   │   ├── risk_manager.py           # Safety gates (549 lines)
│   │   │   └── smc_pipeline.py           # Signal→execution pipeline (408 lines)
│   │   ├── backtest/
│   │   │   └── backtest_engine.py         # vectorbt backtesting (661 lines)
│   │   └── data/
│   │       └── data_fetcher.py           # Multi-source data (1172 lines)
│   │
│   ├── ctrader/                          # cTrader Docker REST API
│   │   ├── README.md                      # Docker setup guide
│   │   ├── Dockerfile                     # Python 3.11-bookworm
│   │   ├── docker-compose.yml            # Container orchestration
│   │   ├── requirements.docker.txt        # Docker pip deps
│   │   ├── .env.example                  # Docker env template
│   │   ├── ctrader_api_server.py         # FastAPI REST bridge (897 lines)
│   │   ├── __init__.py
│   │   └── rest_client/
│   │       ├── __init__.py
│   │       └── rest_client.py            # HTTP REST client (368 lines)
│   │
│   ├── skills/                            # 41 SKILL.md files
│   │   ├── smc/                         # 9 skills
│   │   ├── technical/                    # 9 skills
│   │   ├── fundamental/                  # 3 skills
│   │   ├── sentiment/                   # 3 skills
│   │   ├── news/                        # 3 skills
│   │   ├── backtest/                    # 3 skills
│   │   ├── forex/                       # 3 skills
│   │   ├── commodities/                 # 3 skills
│   │   └── indices/                     # 3 skills
│   │
│   ├── n8n/                              # 5 automation workflows
│   │   ├── workflow_smc_execution.json
│   │   ├── workflow_position_management.json
│   │   ├── workflow_economic_calendar.json
│   │   ├── workflow_morning_briefing.json
│   │   └── workflow_weekly_performance.json
│   │
│   ├── scripts/
│   │   ├── install.sh                   # Full Kali Linux installation (380 lines)
│   │   ├── hire_agents.sh               # Paperclip agent deployment (135 lines)
│   │   └── test_suite.py                # Validation suite (496 lines)
│   │
│   └── dashboard/
│       └── AgentFinanceV3Dashboard.jsx  # React dashboard component (1114 lines)
│
├── dashboard-app/                        # React/Vite frontend
│   ├── package.json                      # React 19.2.4, Vite 8.0.1
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── AgentFinanceV3Dashboard.jsx  # Main dashboard
│   │   └── assets/
│   └── public/
│
├── AgentFinance_v3_Implementation_Guide.md  # Upgrade specification (1433 lines)
├── ctrader-openapi-guide.md               # cTrader API reference
└── apex-platform-prompt.md                # Trading platform spec

```

---

## 3. 28 AI Agents

Each agent has:
- **YAML config**: Paperclip configuration (name, model `codellama:34b`, skills, triggers, commands, budget, memory)
- **Python script**: CLI tool with `analyze()`, `report()`, `scan()` methods + main() handler

### Department 1 — Public Markets Intelligence (Agents 01-06)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 01 | SEC Filings Analyst | fundamentals, regulatory | 10-K, 8-K, Form 4, SEC EDGAR filings, regulatory changes |
| 02 | Transcripts Analyst | nlp, guidance | Earnings call transcription analysis, sentiment, forward guidance |
| 03 | Stock Data Analyst | market-data, pricing | Real-time quotes, FX, commodities, equities, crypto prices |
| 04 | Financials Analyst | financial-statements | Income statements, balance sheets, cash flow analysis |
| 05 | Holdings Intelligence | institutional, 13f | Institutional ownership tracking, 13-F filings, whale trades |
| 06 | Crypto Intelligence | blockchain, defi | DeFi protocols, on-chain metrics, DEX data, Bitcoin dominance |

### Department 2 — Private Markets Intelligence (Agents 07-12)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 07 | Company Intelligence | private-markets, databases | Crunchbase, PitchBook, Bloomberg private company data |
| 08 | Funding Intelligence | venture, deal-tracking | VC/PE funding rounds, valuations, deal flow |
| 09 | Fund Intelligence | hedge-funds, pe-funds | Fund manager due diligence, performance tracking |
| 10 | Deals Intelligence | ma, ipo, comps | M&A analytics, IPO pipeline, comparable company analysis |
| 11 | Investor Intelligence | investor-network, gp-profiles | GP/LP profiling, investor networks, allocation patterns |
| 12 | Private Debt Intelligence | credit-markets, covenants | Direct lending, CLOs, covenant analysis, credit spreads |

### Department 3 — Research Intelligence (Agents 13-14)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 13 | Web Intelligence | web-scraping, structured-data | Job posting analysis, pricing intelligence, structured scraping |
| 14 | Deep Research | multi-source, synthesis | Cross-source synthesis, investment memos, research reports |

### Department 4 — Asset Class Intelligence (Agents 19-21)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 19 | Forex Intelligence | forex-smc, forex-cot, forex-sessions | 28 FX pairs, SMC analysis, COT, kill zones, 15 pairs monitored |
| 20 | Commodities Intelligence | commodities-smc, fundamentals, seasonality | Gold, silver, WTI, Brent, natural gas, copper, EIA reports |
| 21 | Indices Intelligence | indices-breadth, vix, sectors | SPX, NDX, DJI, DAX, FTSE, breadth, sector rotation, VIX |

### Department 5 — Trading Strategy Engine (Agents 22-26)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 22 | SMC Strategy Agent | 9 SMC skills | Order blocks, FVGs, BOS/CHoCH, liquidity, premium/discount, confluence |
| 23 | Technical Analysis Agent | 9 technical skills | 80+ indicators, chart patterns, multi-timeframe confluence |
| 24 | Fundamental Analysis Agent | 3 fundamental skills | Macro regime, CPI, NFP, Fed/ECB rate decisions, GDP |
| 25 | Sentiment Intelligence Agent | 3 sentiment skills | COT reports, Fear & Greed index, options flow, social sentiment |
| 26 | News Intelligence Agent | 3 news skills | NLP news analysis, breaking news alerts, geopolitical risk |

### Department 6 — Trading Automation (Agents 27-28)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 27 | Strategy Backtesting Agent | 3 backtest skills | vectorbt backtesting, Monte Carlo, walk-forward validation |
| 28 | Live Trading Executor | trading, execution, risk | cTrader execution, all order types, 7 risk gates, SL/TP management |

### Department 7 — Investment Operations (Agents 15-18)

| ID | Name | Skills | Purpose |
|----|------|--------|---------|
| 15 | Portfolio Monitor | portfolio, risk | Real-time P&L, beta, VaR, correlation, position exposure |
| 16 | Investment Report Writer | reporting, writing | IC memos, earnings notes, weekly summaries, institutional reports |
| 17 | Compliance Monitor | compliance, regulatory | 13-F obligations, position limits, insider trading restrictions |
| 18 | Trading Supervisor | orchestration, overview | Chief orchestrator, daily briefings, signal approval queue |

---

## 4. Trading Engines

### 4.1 `smc_engine.py` — Smart Money Concepts Engine (936 lines)

**Purpose**: Institutional-grade SMC methodology implementation

**Key Classes:**
- `BiasDirection` (Enum): BULLISH, BEARISH, NEUTRAL
- `KillZone` (Enum): ASIAN, LONDON_OPEN, LONDON, NEW_YORK, LONDON_CLOSE, NY_CLOSE
- `OrderBlock` (dataclass): institutional order blocks with quality scoring
- `FairValueGap` (dataclass): 3-candle imbalance zones
- `SwingHighLow` (dataclass): swing detection for structure
- `LiquidityZone` (dataclass): buy-side/sell-side liquidity areas
- `InducementZone` (dataclass): liquidity sweeps and inducement patterns
- `SMCSignal` (dataclass): complete trade signal output

**Key Methods:**
- `detect_order_blocks()` — find institutional order blocks
- `detect_fair_value_gaps()` — identify imbalance zones
- `detect_bos_choch()` — break of structure + change of character
- `detect_liquidity_zones()` — liquidity pools, buy-side/sell-side grabs
- `detect_swing_highs_lows()` — swing high/low detection
- `identify_premium_discount()` — premium/discount zone classification
- `detect_mitigations()` — block/zone mitigation tracking
- `full_smc_analysis()` — complete multi-timeframe SMC analysis

**Monitored Pairs:** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURGBP, EURJPY, GBPJPY, XAUUSD, XAGUSD

### 4.2 `technical_engine.py` — Technical Analysis Engine (992 lines)

**Purpose**: 80+ technical indicators with pure Python implementations

**Indicator Categories:**

| Category | Indicators |
|---------|-----------|
| Trend | SMA, EMA, WMA, DEMA, TEMA, VWMA, Hull MA, KAMA, ALMA |
| Momentum | RSI, Stochastic (slow/fast/full), CCI, ROC, Williams %R, MFI, ROC |
| Volatility | Bollinger Bands, ATR, Keltner Channels, Donchian Channels, Ulcer Index |
| Volume | OBV, VWAP, A/D Line, CMF, Volume Profile, Force Index, MFI |
| Pattern | Head & Shoulders, Double Top/Bottom, Triangles, Flags, Wedges |
| Ichimoku | Tenkan-sen, Kijun-sen, Senkou Span A/B, Chikou Span |
| MACD | Standard MACD, Histogram, Signal line, crossovers |
| Pivot | Classic, Fibonacci, Camarilla, Woodie, DeMark pivot points |
| Custom | Supertrend, Parabolic SAR, Aroon, TRIX, Williams Alligator |

**Key Methods:**
- `calculate_confluence()` — multi-indicator alignment scoring
- `detect_divergences()` — bullish/bearish regular + hidden divergences
- `identify_support_resistance()` — key price levels
- `analyze_volume_profile()` — point of control, value areas
- `detect_chart_patterns()` — candlestick + chart patterns

### 4.3 `session_engine.py` — Kill Zones & COT Engine (760 lines)

**Purpose**: Trading session timing and institutional positioning analysis

**Key Classes:**
- `SessionType` (Enum): ASIAN, LONDON_OPEN, LONDON, NEW_YORK, LONDON_CLOSE, NY_CLOSE
- `COTSignal` (Enum): EXTREME_BULLISH, BULLISH, NEUTRAL, BEARISH, EXTREME_BEARISH
- `KillZone` (dataclass): session info, UTC times, overlap detection
- `COTData` (dataclass): CFTC commitment of traders data
- `SessionAnalysis` (dataclass): session result with entry zones

**Key Methods:**
- `get_active_session()` — determine current kill zone
- `get_session_times()` — UTC session boundaries
- `is_in_kill_zone()` — check if price is in active session window
- `get_kill_zone_bias()` — directional bias during session
- `fetch_cot_data()` — pull CFTC COT weekly data
- `analyze_cot_report()` — net positioning, commercial vs non-commercial
- `get_session_entry_zones()` — optimal entry ranges per session
- `detect_silver_bullet()` — high-probability London Open patterns
- `detect_judas_swing()` — order block rejection during kill zones

### 4.4 `data_fetcher.py` — Multi-Source Market Data (1172 lines)

**Purpose**: Unified data access across all market sources

**Data Sources:**

| Source | Asset Class | Endpoint |
|--------|-------------|----------|
| OANDA | Forex | `https://api-fxpractice.oanda.com` |
| Polygon.io | Equities, Indices, Crypto | `https://api.polygon.io` |
| FRED | Macro | `https://api.stlouisfed.org/fred` |
| CFTC | COT Reports | `https://api.stlouisfed.org/fred/series/observations` |
| NewsAPI | News | `https://newsapi.org/v2` |

**Key Classes:**
- `DataConfig` (dataclass): API keys and configuration
- `OHLCVData` (dataclass): standardized OHLCV candle format
- `MarketSnapshot` (dataclass): multi-asset snapshot
- `DataFetcher`: main orchestrator class

**Key Methods:**
- `fetch_ohlcv()` — unified OHLCV fetch (auto-selects source by asset class)
- `fetch_oanda_forex()` — OANDA forex candles
- `fetch_polygon()` — Polygon equity/index data
- `fetch_fred_macro()` — FRED economic indicators
- `fetch_cot()` — CFTC COT positioning data
- `fetch_news()` — NewsAPI headlines and articles
- `fetch_multiple_timeframes()` — multi-TF data for single symbol

---

## 5. Execution & Risk Layer

### 5.1 `smc_pipeline.py` — SMC Signal → Execution Pipeline (408 lines)

**Purpose**: Complete end-to-end pipeline from SMC analysis to cTrader execution

**Architecture:**
```
Agent 22 (SMC Strategy) → smc_pipeline.py → Risk Manager → Agent 28 (Executor) → cTrader
```

**Key Classes:**
- `SMCPipeline`: Main pipeline orchestrator

**CLI Commands:**
```bash
python smc_pipeline.py EURUSD H1           # Scan single pair
python smc_pipeline.py EURUSD H1 --dry   # Dry run (no execution)
python smc_pipeline.py --scan-all        # Scan 10 pairs (H1 + H4)
python smc_pipeline.py --scan-all --dry    # Scan + dry run
python smc_pipeline.py --status          # Show executor status
```

**Key Methods:**
- `analyze()` — run SMC analysis (Agent 22)
- `scan_all()` — scan all monitored pairs, rank by confluence
- `execute_signal()` — pass through risk gates + execute
- `run()` — full 3-step pipeline (analyze → validate → execute)
- `summary()` — return pipeline statistics

**Monitored Pairs (scan-all):** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, EURGBP, EURJPY, XAUUSD, XAGUSD (each on H1 + H4)

### 5.2 `risk_manager.py` — Risk Gates & Safety Controls (549 lines)

**Purpose**: Pre-trade validation and continuous risk monitoring

**Safety Gates (all must pass for trade execution):**

| Gate | Rule | Action on Failure |
|------|------|-----------------|
| System Halt | `daily_pnl < -3%` | REJECT — full halt |
| Validation | Signal has all required fields | REJECT — missing data |
| Confidence | `confidence >= 75%` | REJECT — low confidence |
| Position Limit | `open_positions < 5` | REJECT — max positions |
| Risk/Reward | `rr_ratio >= 1.5` | REJECT — insufficient R:R |
| Risk Manager | `position_size <= safe_size` | REJECT — too large |
| Spread Check | `spread <= 3x_avg_spread` | REJECT — excessive spread |

**Key Methods:**
- `pre_trade_check()` — validate signal against all gates
- `calculate_position_size()` — Kelly criterion or fixed fraction
- `calculate_risk_reward()` — R:R ratio from SL/TP distances
- `check_correlation()` — prevent correlated position stacking
- `check_daily_loss()` — daily P&L vs kill switch threshold
- `get_risk_summary()` — current portfolio risk metrics

### 5.3 `ctrader_client.py` — cTrader Direct TCP Client (844 lines)

**Purpose**: Direct cTrader OpenAPI integration via TCP/Protobuf

**Connection:** `demo.ctraderapi.com:5035` (demo) or `live.ctraderapi.com:5035` (live)

**Protocol:** ctrader-open-api (Twisted + Protobuf)

**Key Methods:**
- `connect()` — authenticate with CLIENT_ID + ACCESS_TOKEN
- `get_positions()` — list all open positions
- `get_pending_orders()` — list pending limit/stop orders
- `get_account_summary()` — balance, equity, margin, margin level
- `create_market_order()` — market execution with SL/TP
- `create_limit_order()` — pending limit order
- `create_stop_order()` — stop entry order
- `close_position()` — close by position ID (full/partial)
- `close_all_positions()` — emergency full close
- `cancel_order()` — cancel pending order
- `amend_position()` — modify SL/TP on open position
- `get_historical_data()` — OHLCV candles (M1 to MN1)
- `get_daily_pnl()` — trading day P&L

**Simulation Mode:** Returns realistic demo data when credentials are missing

### 5.4 `live_executor.py` — Agent 28 (588 lines)

**Purpose**: Command-line interface for live trading operations

**Commands:**
```bash
python live_executor.py positions              # List open positions
python live_executor.py orders                # List pending orders
python live_executor.py account               # Account summary
python live_executor.py execute EURUSD BUY 1.0823 1.0756 1.0890 0.10
python live_executor.py close #1247           # Close position by ID
python live_executor.py amend #1247 1.0750 1.0900  # Amend SL/TP
python live_executor.py risk-check            # Run all risk gates
python live_executor.py halt                   # Halt all trading
python live_executor.py resume                # Resume trading
python live_executor.py report                # Full system report
```

**7 Execution Gates (in order):**
1. `check_system_halt()` — daily loss threshold
2. `validate_signal()` — required fields present
3. `check_confidence()` — minimum 75%
4. `check_position_limit()` — max 5 positions
5. `check_risk_reward()` — min 1.5 R:R
6. `risk_manager.pre_trade_check()` — full risk validation
7. `check_spread()` — spread not > 3x average

### 5.5 `backtest_engine.py` — Strategy Backtesting (661 lines)

**Purpose**: Validate strategies against historical data using vectorbt

**Backtest Config:**
```python
symbol: str           # Trading symbol
timeframe: str        # M15, H1, H4, D1
start_date: str       # Backtest start
end_date: str         # Backtest end
initial_balance: float # Starting capital
risk_percent: float   # Risk per trade (default 0.01)
commission: float     # Per-trade commission
slippage: float       # Slippage in pips
strategy: StrategyType  # SMC, TECHNICAL, COMBINED, CUSTOM
```

**Metrics Returned:**
- Win rate, profit factor, Sharpe ratio, Sortino ratio
- Maximum drawdown (%), max drawdown duration
- Total return, annual return, monthly breakdown
- Average trade duration, expectancy per trade
- Equity curve (DataFrame)

**Key Methods:**
- `backtest_smc()` — pure SMC strategy signals
- `backtest_technical()` — pure technical indicator strategy
- `backtest_combined()` — SMC + technical confluence
- `monte_carlo()` — 1000-iteration Monte Carlo simulation
- `walk_forward()` — walk-forward optimization
- `optimize_parameters()` — parameter grid search

---

## 6. Skills Library

**41 SKILL.md files across 8 categories.** Each skill follows the format:

```yaml
---
name: skill-category/skill-name
description: One-line purpose
---
# Markdown content:
- Concept explanation
- Rules and conditions
- Confidence scoring
- Examples and thresholds
```

### 6.1 SMC Skills (9 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `smc-order-blocks` | 57 | Bullish/bearish OB identification, quality grading, mitigation |
| `smc-fair-value-gaps` | 66 | 3-candle imbalance zones, fill probability, re-test entries |
| `smc-bos-choch` | 70 | Break of structure, change of character, momentum shifts |
| `smc-liquidity` | 73 | Buy-side/sell-side sweeps, liquidity pools, stop hunts |
| `smc-kill-zones` | 78 | London/NY open patterns, session overlap, optimal entries |
| `smc-confluence` | 91 | Multi-factor confluence scoring, zone alignment |
| `smc-silver-bullet` | 80 | High-probability kill zone SMC patterns |
| `smc-judas-swing` | 94 | Order block rejection patterns, institutional spoofing |
| `smc-power-of-3` | 95 | Power of 3 concept: 3 touches, 3 swings, 3 candles |

### 6.2 Technical Skills (9 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `tech-rsi` | 73 | RSI overbought/oversold, divergences, signal line |
| `tech-macd` | 74 | MACD histogram, signal crossovers, zeroline |
| `tech-bollinger` | 77 | Bollinger Band squeezes, breakouts, mean reversion |
| `tech-ichimoku` | 77 | Tenkan/Kijun crossover, cloud breakout, Chikou confirmation |
| `tech-adx` | 73 | ADX trend strength, -DI/+DI crossover |
| `tech-momentum` | 72 | Momentum oscillators, rate of change, acceleration |
| `tech-volume` | 74 | Volume profile, OBV, VWAP, Climax indicator |
| `tech-divergence` | 80 | Regular/hidden divergences, multi-timeframe |
| `tech-confluence` | 73 | Multi-indicator alignment, scoring system |

### 6.3 Fundamental Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `fundamental-regime` | 80 | Inflation, growth, monetary policy regimes |
| `fundamental-calendar` | 70 | Economic calendar, high-impact news scheduling |
| `fundamental-rates` | 77 | Central bank rates, yield curves, carry |

### 6.4 Sentiment Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `sentiment-cot` | 75 | CFTC COT net positioning, commercial vs speculative |
| `sentiment-fear-greed` | 69 | Fear & Greed index, CNN alternative metrics |
| `sentiment-composite` | 73 | Multi-source sentiment aggregation, scoring |

### 6.5 News Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `news-nlp` | 72 | NLP sentiment scoring, headline classification |
| `news-events` | 69 | Scheduled news events, NFP, FOMC, earnings |
| `news-breaking` | 73 | Breaking news alerts, geopolitical risk detection |

### 6.6 Backtest Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `backtest-smc` | 69 | SMC-only strategy backtesting parameters |
| `backtest-technical` | 62 | Technical indicator strategy optimization |
| `backtest-combined` | 59 | Combined SMC + technical parameter sets |

### 6.7 Forex Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `forex-smc` | 70 | FX-specific SMC application, pair correlations |
| `forex-cot` | 70 | Currency-specific COT positioning analysis |
| `forex-sessions` | 74 | Forex session timing, peak liquidity hours |

### 6.8 Commodities Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `commodities-smc` | 69 | Gold, oil, agriculture SMC patterns |
| `commodities-fundamentals` | 62 | Supply/demand, EIA, OPEC, seasonal cycles |
| `commodities-seasonality` | 69 | Historical seasonal price patterns |

### 6.9 Indices Skills (3 skills)

| Skill | Lines | Focus |
|-------|-------|-------|
| `indices-breadth` | 65 | Advance/decline, breadth thrust, NYSE stats |
| `indices-vix` | 64 | VIX term structure, VVIX, VPOC analysis |
| `indices-sectors` | 72 | Sector rotation, relative strength, SPX sectors |

---

## 7. n8n Workflows

### 7.1 `workflow_smc_execution.json` (248 lines)

**Trigger**: Every 15 minutes during market hours (00:00-22:00 UTC, Mon-Fri)

**Flow:**
```
Kill Zone Check → Fetch OHLCV → SMC Analysis
    → Confidence Filter (>= 75%)
    → Technical Confirmation
    → Risk Manager Check
    → Telegram Alert (signal details)
    → cTrader Execution (if live mode)
```

**Inputs**: Trading pair, timeframe, last analysis timestamp
**Outputs**: Telegram message with signal, cTrader order, Supabase log entry

### 7.2 `workflow_position_management.json` (411 lines)

**Trigger**: Every 5 minutes

**Flow:**
```
Fetch Open Positions → TP/SL Check Loop
    → TP1 Hit (50% partial close)
    → SL Moved to Breakeven
    → TP2 Hit (full close)
    → SL Hit → Journal Entry
    → Telegram Notification (all events)
    → Supabase Trade Log Update
```

### 7.3 `workflow_economic_calendar.json` (346 lines)

**Trigger**: Every 30 minutes

**Flow:**
```
Fetch Investing.com Calendar
    → Filter HIGH/CRITICAL Events
    → Event Within 30min
        → Block All Trading
        → Close Pending Orders
        → Telegram Alert (HIGH IMPACT)
        → Post-Event (30min after)
        → Resume Trading
        → Analyze Market Reaction
```

### 7.4 `workflow_morning_briefing.json` (119 lines)

**Trigger**: 06:00 UTC, Monday-Friday

**Flow:**
```
Economic Calendar → Overnight SMC (4H)
    → COT Update → Active Positions Review
    → Kill Zone Schedule
    → Macro Regime Assessment
    → Telegram Briefing (all metrics)
```

### 7.5 `workflow_weekly_performance.json` (232 lines)

**Trigger**: Sunday 18:00 UTC

**Flow:**
```
Pull Closed Trades (Supabase)
    → Calculate Metrics (win rate, PF, pips, Sharpe)
    → Strategy Breakdown
    → Compare to Backtest Baseline
    → Generate Recommendations
    → Telegram Weekly Report
    → Supabase Archive
```

---

## 8. cTrader Docker REST API

**Purpose**: Isolated REST bridge for cTrader OpenAPI — eliminates Twisted reactor dependency from main application code.

### Architecture

```
AgentFinance Python
       ↓ HTTP POST/GET
Docker Container :9009
       ↓ FastAPI + Uvicorn
CTraderBot (Twisted/Protobuf)
       ↓ TCP/Protobuf
demo.ctraderapi.com:5035
       ↓
Pepperstone cTrader Platform
```

### Files

| File | Lines | Purpose |
|------|-------|---------|
| `ctrader_api_server.py` | 897 | FastAPI REST server with all trading endpoints |
| `rest_client/rest_client.py` | 368 | Python HTTP client (drop-in replacement) |
| `Dockerfile` | 21 | `python:3.11-bookworm` + pip deps |
| `docker-compose.yml` | 51 | Container with health checks, env vars, logging |
| `requirements.docker.txt` | 10 | fastapi, uvicorn, ctrader-open-api, twisted |
| `.env.example` | 40 | Credential template |

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Connection + account status |
| GET | `/symbols` | List 14 trading symbols |
| GET | `/positions` | Open positions with P&L |
| GET | `/orders` | Pending limit/stop orders |
| GET | `/account` | Balance, equity, margin, margin level |
| POST | `/orders/market` | Market execution (BUY/SELL) |
| POST | `/orders/limit` | Limit order |
| POST | `/orders/stop` | Stop entry order |
| POST | `/orders/close` | Close position (full/partial) |
| POST | `/orders/cancel` | Cancel pending order |
| POST | `/orders/amend` | Amend SL/TP |
| POST | `/orders/close-all` | Emergency close all |
| POST | `/trendbars` | Historical OHLCV candles |

### Setup

```bash
cd ctrader/
cp .env.example ../.env
# Add CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, CTRADER_ACCESS_TOKEN
docker compose up --build -d
curl http://localhost:9009/health
# Swagger UI: http://localhost:9009/docs
```

---

## 9. React Dashboard

**File**: `dashboard-app/src/AgentFinanceV3Dashboard.jsx` (1114 lines)

**Stack**: React 19.2.4 + Vite 8.0.1

**Design System:**
- Dark theme background (`#0f1117`, `#1a1d27`)
- Gold accent (`#C9A84C`) — primary highlights
- Green (`#22C984`) — bullish/profit
- Red (`#FF4B6B`) — bearish/loss
- Blue (`#4A8FFF`) — neutral/info
- Purple (`#A78BFA`) — sentiment
- Amber (`#F59E0B`) — warnings
- Cyan (`#22D3EE`) — data points

**Tabs (7):**
1. **Trading** — Active signals, SMC analysis results, pipeline status
2. **Positions** — Open positions, P&L, margin, pending orders
3. **Agents** — 28 agent cards with status (active/idle/error), run counts, skills, commands
4. **Skills** — Skills library browser across 8 categories
5. **Workflows** — n8n workflow status and monitoring
6. **Feed** — Activity feed, Telegram notifications, trade journal
7. **System** — Agent runner status, data sources, API health

**Agent Cards Display:**
- Agent name + ID
- Department color badge
- Status indicator (green=active, yellow=idle, red=error)
- Run count + last run time
- Skills list
- Commands
- Tags

---

## 10. Installation

**Target**: Kali Linux (Debian-based)

### Dependencies

**System (apt):**
```
golang-go, redis-server, postgresql, jq, libpq-dev,
lsb-release, git, curl, wget, build-essential
```

**Python packages (pip):**
```
numpy, pandas, ta, vectorbt, smartmoneyconcepts,
transformers, torch, sentencepiece, requests,
python-dotenv, twisted, protobuf, ctrader-open-api==0.9.2,
mcp>=0.9.0
```

**Node.js:** v20.x (nodesource)

**Docker:** docker-compose for cTrader REST API container

### Install Script

```bash
cd agentfinance/
bash scripts/install.sh
```

Install script sections:
1. System deps (apt)
2. Python venv + pip packages
3. Node.js 20.x
4. cTrader CLI tools
5. Go + indicator library
6. Environment configuration
7. Redis setup
8. Verification checks

---

## 11. Quick Start Commands

```bash
# 1. Activate environment
source agentfinance/venv/bin/activate

# 2. Start cTrader Docker (optional)
cd agentfinance/ctrader/
docker compose up --build -d
curl http://localhost:9009/health

# 3. Test simulation mode (no credentials needed)
cd agentfinance
python3 trading/execution/smc_pipeline.py --scan-all --dry

# 4. Test executor
python3 agents/trading/live_executor.py positions
python3 agents/trading/live_executor.py report

# 5. Run single agent
python3 agent_runner.py --agent 22 --command "scan EURUSD"

# 6. Run test suite
python3 scripts/test_suite.py

# 7. Start dashboard
cd dashboard-app && npm run dev
# → http://localhost:5173

# 8. Deploy agents to Paperclip
bash scripts/hire_agents.sh
```

---

## 12. Risk Management Rules

| Parameter | Value |
|-----------|-------|
| Max risk per trade | 1% of account |
| Max daily drawdown — halt | 3% |
| Max daily drawdown — pause | 2.5% |
| Max daily drawdown — alert | 1.5% |
| Max weekly drawdown | 5% |
| Max monthly drawdown | 8% |
| Max concurrent positions | 5 |
| Min risk/reward ratio | 1.5 |
| Min signal confidence | 75% |
| Max spread multiplier | 3× average |
| Pre/post news block | 15 minutes |
| Signal max age | 4 hours |

**Monitored Symbols:**
- **Forex (15):** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURGBP, EURJPY, GBPJPY, EURAUD, EURNZD, CADJPY, AUDNZD, EURCAD
- **Commodities (6):** XAUUSD, XAGUSD, WTI, Brent, Natural Gas, Copper
- **Indices (6):** SPX, NAS100, DJI, DAX, FTSE 100, N225

---

## 13. Data Sources & APIs

| Service | Purpose | API Type |
|---------|---------|----------|
| Pepperstone cTrader | Live trading execution | TCP/Protobuf (direct) or REST (Docker) |
| OANDA | Forex market data | REST API |
| Polygon.io | Equities, indices, crypto | REST API |
| FRED (St. Louis Fed) | Macro economic data | REST API |
| CFTC | Commitment of Traders | FRED series |
| NewsAPI | Financial news headlines | REST API |
| Investing.com | Economic calendar | Web scraping |

---

## 14. Rebuild Instructions

### Step 1 — Directory Setup

```bash
mkdir -p agentfinance/{agents/{public,private,research,ops,trading},trading/{engines,execution,backtest,data},ctrader/rest_client,skills/{smc,technical,fundamental,sentiment,news,backtest,forex,commodities,indices},n8n,scripts,dashboard}
```

### Step 2 — Core Files

Create files in order of dependency:
1. **Python engines** — `smc_engine.py`, `technical_engine.py`, `session_engine.py`, `data_fetcher.py`
2. **Execution layer** — `risk_manager.py`, `ctrader_client.py`, `smc_pipeline.py`, `backtest_engine.py`
3. **Agent scripts** — 28 Python agent scripts + 28 YAML configs
4. **Skills** — 41 SKILL.md files
5. **Docker** — `ctrader_api_server.py`, `rest_client.py`, `Dockerfile`, `docker-compose.yml`
6. **Workflows** — 5 n8n JSON workflow files
7. **Dashboard** — React component + Vite config

### Step 3 — Configuration

```bash
cp agentfinance/.env.example agentfinance/.env
# Fill in:
# - CTRADER_CLIENT_ID / CTRADER_CLIENT_SECRET / CTRADER_ACCESS_TOKEN
# - OANDA_API_KEY / OANDA_ACCOUNT_ID
# - POLYGON_API_KEY
# - FRED_API_KEY
# - NEWSAPI_KEY
# - TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
```

### Step 4 — Deployment

```bash
# Install all dependencies
bash agentfinance/scripts/install.sh

# Deploy Docker cTrader API
cd agentfinance/ctrader && docker compose up --build -d

# Deploy agents to Paperclip
bash agentfinance/scripts/hire_agents.sh

# Verify everything
python3 agentfinance/scripts/test_suite.py
```

---

## 15. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PAPERCLIP AGENT LAYER (28 agents)                  │
│                                                                               │
│  Department 1: Public Markets ──────── Agents 01-06 (SEC, earnings, stocks) │
│  Department 2: Private Markets ──────── Agents 07-12 (VC, PE, M&A, credit)   │
│  Department 3: Research ────────────── Agents 13-14 (web scraping, deep)    │
│  Department 4: Asset Classes ───────── Agents 19-21 (FX, commodities, indices)│
│  Department 5: Strategy Engine ─────── Agents 22-26 (SMC, tech, macro)     │
│  Department 6: Automation ───────────── Agents 27-28 (backtest, live trade)  │
│  Department 7: Operations ────────────── Agents 15-18 (portfolio, reports)   │
└────────────────────────────────────────────┬──────────────────────────────────┘
                                             │
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      agent_runner.py (476 lines)                              │
│           Master CLI: python agent_runner.py --agent <id> --command <cmd>     │
└────────────────────────────────────────────┬──────────────────────────────────┘
                                             │
                    ┌────────────────────────┴───────────────────────┐
                    ▼                                                  ▼
┌─────────────────────────────────────┐    ┌──────────────────────────────────┐
│      TRADING ENGINES (3,688 lines)  │    │    INTELLIGENCE ENGINES           │
│                                       │    │                                   │
│  smc_engine.py (936L)               │    │  sec_filings.py (Agent 01)        │
│  • Order blocks, FVGs, BOS/CHoCH   │    │  stock_data.py (Agent 03)        │
│  • Liquidity zones, swing detection│    │  financials.py (Agent 04)         │
│  • Premium/discount, mitigations    │    │  holdings.py (Agent 05)          │
│  • 27-instrument support            │    │  companies.py (Agent 07)         │
│                                       │    │  web_scraping.py (Agent 13)      │
│  technical_engine.py (992L)          │    │  deep_research.py (Agent 14)     │
│  • 80+ indicators                   │    │                                   │
│  • SMA, EMA, RSI, MACD, Bollinger │    └───────────────────────────────────┘
│  • Ichimoku, ATR, VWAP, volume     │
│                                       │
│  session_engine.py (760L)            │
│  • Kill zones (Asian, London, NY)  │
│  • COT analysis, Silver Bullet      │
│  • Judas swing, Power of 3         │
│                                       │
│  data_fetcher.py (1172L)            │
│  • OANDA, Polygon, FRED, COT       │
│  • NewsAPI, multi-TF aggregation   │
└─────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  EXECUTION & RISK LAYER (2,502 lines)                       │
│                                                                               │
│  smc_pipeline.py (408L)           risk_manager.py (549L)                     │
│  • 3-step: analyze→validate→    • 7-gate pre-trade validation             │
│    execute                        • Position sizing (Kelly criterion)        │
│  • --scan-all, --dry mode        • Correlation checks                        │
│  • 10 pairs × 2 TFs              • Daily loss monitoring                      │
│                                   • R:R ratio enforcement                     │
│  backtest_engine.py (661L)         live_executor.py (588L)                   │
│  • vectorbt backtesting            • CLI: positions, orders, execute,          │
│  • Monte Carlo (1000 runs)          close, amend, halt, resume, report       │
│  • Walk-forward optimization        • 7 execution gates                        │
│  • SMC + technical + combined      • SMC pipeline integration                  │
└────────────────────────────────────────────┬──────────────────────────────────┘
                                             │
                    ┌────────────────────────┴─────────────────────────────────┐
                    ▼                                                       ▼
┌────────────────────────────────────────┐    ┌──────────────────────────────────┐
│     OPTION A: Direct TCP (no Docker)   │    │  OPTION B: Docker REST API       │
│                                        │    │                                   │
│  ctrader_client.py (844L)             │    │  REST Client ──HTTP──► Container  │
│  Twisted/Protobuf direct connection    │    │  (368 lines)        (ctrader_api_ │
│  to demo.ctraderapi.com:5035         │    │                     server.py 897L)│
│                                        │    │           │                    │
│  + Requires ctrader-open-api package  │    │           ▼                    │
│  + Requires Twisted in application     │    │  CTraderBot (Twisted/Protobuf)   │
└────────────────────────────────────────┘    │           │                    │
                                                └───────────┼────────────────────┘
                                                            ▼
                                               demo.ctraderapi.com:5035
                                                            │
                                               ┌────────────┴────────────┐
                                               │  Pepperstone Demo       │
                                               │  Account #46729678      │
                                               └─────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         AUTOMATION LAYER (n8n)                             │
│                                                                               │
│  workflow_smc_execution.json ─────── Every 15 min ─── Kill zone → SMC → trade │
│  workflow_position_management.json ── Every 5 min ─── TP/SL/breakeven mgmt  │
│  workflow_economic_calendar.json ─── Every 30 min ── News block → halt      │
│  workflow_morning_briefing.json ─── 06:00 UTC ────── Daily briefing        │
│  workflow_weekly_performance.json ─── Sun 18:00 ────── Weekly report        │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD LAYER                                     │
│                                                                               │
│  React 19 + Vite 8 ─── AgentFinanceV3Dashboard.jsx (1114L)                 │
│  7 tabs: Trading │ Positions │ Agents │ Skills │ Workflows │ Feed │ System  │
│  28 agent cards with status, skills, commands                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Line Count Summary

| Component | Files | Lines |
|----------|-------|-------|
| Agent Python scripts | 28 | ~2,900 |
| Agent YAML configs | 28 | ~1,200 |
| Trading engines | 4 | ~3,860 |
| Execution layer | 4 | ~2,502 |
| Backtest engine | 1 | 661 |
| cTrader Docker API | 4 | ~1,287 |
| Skills library | 41 | ~2,888 |
| n8n workflows | 5 | ~1,356 |
| Dashboard | 1 | ~1,114 |
| Install/deploy | 3 | ~1,011 |
| Orchestrator | 1 | 476 |
| **Total** | | **~23,255 lines** |

---

## Version Information

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| Node.js | 20.x |
| React | 19.2.4 |
| Vite | 8.0.1 |
| Docker | 29.3.0+ |
| cTrader OpenAPI | 0.9.2 |
| Twisted | 25.5.0 |
| Paperclip Model | CodeLLama 34B |
| Kali Linux | Latest (Debian trixie) |
| Dashboard Port | 5173 |
| cTrader REST Port | 9009 |
| n8n Port | 5678 |
| cTrader Demo | Account #46729678 |

---

*AgentFinance v3 — Built with Paperclip agents, Smart Money Concepts, and cTrader OpenAPI*
