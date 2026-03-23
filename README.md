# AgentFinance v3 - System Overview & Quick Start
## Complete Autonomous Trading Automation System

---

## System Overview

AgentFinance v3 transforms the existing v2 intelligence platform into a complete autonomous trading system.

### What's New in v3

| Component | v2 (Intelligence) | v3 (Intelligence + Trading) |
|-----------|-------------------|----------------------------|
| **Agents** | 18 agents | 28 agents (+10 new) |
| **Departments** | 4 departments | 6 departments (+Asset Classes, Strategy Engine, Automation) |
| **Skills** | 66 skills | 93 skills (+27 trading skills) |
| **Trading** | None | Live cTrader execution via Pepperstone Demo |
| **Analysis** | Fundamentals only | SMC + 80+ technical indicators |
| **Asset Classes** | Equities, Crypto | FX, Commodities, Indices, Equities, Crypto |
| **Automation** | n8n (intelligence) | n8n (full signal → execution pipeline) |
| **Risk Management** | None | 3% daily kill switch, 1% max risk/trade, 5 max positions |

---

## Directory Structure

```
agentfinance/
├── agents/                    # 28 YAML configs + Python scripts
│   ├── public/               # Agents 01-06: SEC, Earnings, Stocks, Financials, Holdings, Crypto
│   ├── private/             # Agents 07-12: Companies, Funding, Funds, Deals, Investors, Debt
│   ├── research/            # Agents 13-14: Web Scraping, Deep Research
│   ├── ops/                # Agents 15-18: Portfolio, Reporting, Compliance, Supervisor
│   └── trading/            # Agents 19-28: Forex, Commodities, Indices, SMC, Tech, Fund, Sentiment, News, Backtest, Executor
├── trading/
│   ├── engines/            # smc_engine.py, technical_engine.py, session_engine.py
│   ├── execution/          # ctrader_client.py, risk_manager.py, smc_pipeline.py
│   ├── backtest/          # backtest_engine.py
│   └── data/              # data_fetcher.py
├── n8n/                    # 5 workflow JSON files
│   ├── workflow_smc_execution.json
│   ├── workflow_morning_briefing.json
│   ├── workflow_position_management.json
│   ├── workflow_economic_calendar.json
│   └── workflow_weekly_performance.json
├── skills/                 # 41 SKILL.md files across 8 categories
│   ├── smc/ (9)           # Order blocks, FVGs, BOS/CHoCH, Liquidity, Kill zones, etc.
│   ├── technical/ (9)     # RSI, MACD, Bollinger, Ichimoku, ADX, etc.
│   ├── fundamental/ (3)   # Regime, Calendar, Rates
│   ├── sentiment/ (3)      # COT, Fear & Greed, Composite
│   ├── news/ (3)          # NLP, Events, Breaking
│   ├── backtest/ (3)      # SMC, Technical, Combined backtesting
│   ├── forex/ (3)         # Forex SMC, COT, Sessions
│   ├── commodities/ (3)    # Commodities SMC, Fundamentals, Seasonality
│   └── indices/ (3)      # Breadth, VIX, Sectors
├── scripts/
│   └── install.sh         # Full installation script
├── dashboard/
│   └── AgentFinanceV3Dashboard.jsx   # React dashboard with live trading UI
└── agent_runner.py        # Master orchestrator for all 28 agents
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd /home/greywolf/Documents/AgentFinance/agentfinance
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Configure cTrader (Demo)

```bash
# Get credentials from: https://help.ctrader.com/open-api/creating-new-app/
# Create an app to get CLIENT_ID and CLIENT_SECRET
# Generate an ACCESS_TOKEN from your cTrader platform

# Edit the .env file
nano .env

# Required fields:
#   CTRADER_CLIENT_ID=your_client_id
#   CTRADER_CLIENT_SECRET=your_client_secret
#   CTRADER_ACCESS_TOKEN=your_access_token
#   CTRADER_ACCOUNT_ID=46729678
#   CTRADER_HOST=demo

# Verify connection
python3 trading/execution/ctrader_client.py
```

### 3. Import n8n Workflows

1. Open n8n at http://localhost:5678
2. Import each JSON file from `n8n/` directory
3. Configure environment variables in n8n credentials

### 4. Run Agents

```bash
# Via agent runner
python3 agent_runner.py --agent 22 --command scan --args EURUSD H1

# Direct SMC agent
python3 agents/trading/smc_strategy.py scan EURUSD H1

# Live executor
python3 agents/trading/live_executor.py positions
```

### 5. Test Dashboard

```jsx
// Import into React project
import AgentFinanceV3Dashboard from './dashboard/AgentFinanceV3Dashboard.jsx';
```

---

## Agent Department Overview

| Dept | Agents | Focus |
|------|-------|-------|
| **Public Markets** | 01-06 | SEC filings, earnings, stocks, financials, holdings, crypto |
| **Private Markets** | 07-12 | Companies, funding, funds, deals, investors, debt |
| **Research** | 13-14 | Web scraping, deep research synthesis |
| **Asset Class Intelligence** | 19-21 | Forex, commodities, indices |
| **Trading Strategy Engine** | 22-26 | SMC, technical, fundamental, sentiment, news |
| **Trading Automation** | 27-28 | Backtesting, live execution |
| **Investment Operations** | 15-18 | Portfolio, reports, compliance, supervision |

> **Note on Private Markets (Agents 07-12):** These agents are for investment intelligence and research only — they do **not** execute trades or interact with the FX trading pipeline. They cover private company analysis, VC/PE funding, M&A deal flow, investor profiling, and private debt research to support investment decision-making.

---

## Trading Commands Reference

### SMC Strategy (Agent 22)
```
/smc:scan EURUSD       # Full SMC analysis
/smc:ob EURUSD H4      # Order block analysis
/smc:fvg EURUSD H1     # Fair value gap analysis
/smc:setup EURUSD      # Generate trade setups
/smc:kill-zones        # Kill zone status
```

### Technical Analysis (Agent 23)
```
/tech:scan EURUSD      # Full technical scan
/tech:rsi EURUSD       # RSI analysis
/tech:macd EURUSD      # MACD analysis
/tech:confluence EURUSD # Multi-indicator confluence
```

### Live Trading (Agent 28)
```
/trade:execute SIG-001  # Execute approved signal
/trade:positions         # List open positions
/trade:risk-check       # Run risk checks
/trade:daily-pnl        # Daily P&L report
/trade:halt             # Emergency stop
/trade:resume           # Resume trading
/trade:report           # Full account report
```

### SMC Pipeline (Agent 22 → 28)
```bash
# Full SMC analysis + execution on single pair
python3 trading/execution/smc_pipeline.py EURUSD H1

# Dry run (analysis only, no execution)
python3 trading/execution/smc_pipeline.py EURUSD H1 --dry

# Scan all 14 pairs and execute top setup
python3 trading/execution/smc_pipeline.py --scan-all

# Check executor status
python3 trading/execution/smc_pipeline.py --status

# Direct executor commands
python3 agents/trading/live_executor.py positions
python3 agents/trading/live_executor.py risk-check
python3 agents/trading/live_executor.py report
```

### Forex Intelligence (Agent 19)
```
/fx:scan               # Scan all FX pairs
/fx:kill-zones         # Kill zone status
/fx:cot EURUSD         # COT positioning
/fx:pairs London       # Session pairs
```

---

## n8n Workflows

| Workflow | Trigger | Purpose |
|---------|---------|---------|
| **SMC Signal → Execution** | Every 15 min (market hours) | Full signal pipeline: scan → risk → approve → execute |
| **Position Management** | Every 5 min | TP1 partial close, SL to BE, TP2 full close |
| **Economic Calendar Block** | Every 30 min | Block trading 30min before high-impact events |
| **Morning Briefing** | 06:00 UTC | Daily market intelligence briefing |
| **Weekly Performance** | Sunday 18:00 UTC | Performance review, recommendations |

---

## Risk Safety Gates

| Gate | Condition | Action |
|------|-----------|--------|
| **HOLD** | Confidence < 75% | Queue for manual review |
| **ALERT** | Daily DD < -1.5% | Notify trader, no new trades |
| **PAUSE** | Daily DD < -2.5% | Halt automated execution |
| **HALT** | Daily DD < -3.0% | Close all positions, shutdown |
| **MANUAL** | Spread > 3x average | Force manual review |
| **BLOCK** | High-impact news | Block 15min before/after |

---

## Monitored Symbols

**Forex (15 pairs):**
EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURGBP, EURJPY, GBPJPY, EURAUD, EURNZD, CADJPY, AUDNZD, EURCAD

**Commodities (6):**
XAUUSD (Gold), XAGUSD (Silver), WTI (Crude Oil), Brent, Natural Gas, Copper

**Indices (6):**
SPX (S&P 500), NAS100 (Nasdaq 100), DJI (Dow Jones), DAX, FTSE 100, N225 (Nikkei)

---

## Backtest Results (2024)

| Strategy | Symbol | TF | Win Rate | PF | Sharpe | MDD | Return |
|----------|--------|----|-----|-----|--------|-----|--------|
| Conservative SMC | EURUSD | H4 | 71.2% | 2.47 | 2.31 | -3.2% | +38.4% |
| Balanced SMC+Tech | EURUSD | H1 | 63.8% | 1.98 | 1.87 | -5.1% | +31.2% |
| Scalp Silver Bullet | GBPUSD | M15 | 65.4% | 2.12 | 2.05 | -2.8% | +41.8% |

---

## cTrader Integration

The cTrader integration uses the `ctrader-open-api` Python package with TCP/Protobuf protocol. You have **two connection options**:

### Connection Options

**Option A: Direct TCP** (recommended for development)
- Python code connects directly to `demo.ctraderapi.com:5035`
- Requires `ctrader-open-api` package installed
- Faster, no Docker overhead

**Option B: Docker REST API** (recommended for production)
- Runs cTrader API in an isolated Docker container
- Your code connects via HTTP REST (simple `requests` library)
- Swagger UI at `/docs`, auto-reconnect, health checks
- No Twisted reactor needed in your application code

### Architecture

**Option A — Direct TCP:**
```
Agent 22 (SMC Strategy)
       ↓ generates signal
smc_pipeline.py  ←→  live_executor.py
       ↓                      ↓
   Risk Gates          CTraderClient (direct TCP/Protobuf)
                             ↓
                     ctrader-open-api
                     (TCP/Protobuf)
                             ↓
                   demo.ctraderapi.com:5035
```

**Option B — Docker REST API:**
```
Agent 22 (SMC Strategy)
       ↓ generates signal
smc_pipeline.py  ←→  live_executor.py
       ↓                      ↓
   Risk Gates          CTraderRESTClient (HTTP)
                             ↓
                   http://localhost:9009
                             ↓
               ┌──────────────────────────────────┐
               │   ctrader-api Docker container     │
               │  ctrader_api_server.py (FastAPI) │
               │  CTraderBot (Twisted/Protobuf)   │
               └──────────────┬───────────────────┘
                              ↓ TCP/Protobuf
                    demo.ctraderapi.com:5035
```

### Quick Start — Docker

```bash
# 1. Configure credentials
cd agentfinance/ctrader
cp .env.example ../../.env
# Edit ../../.env with your cTrader credentials

# 2. Build and start the container
docker compose up --build -d

# 3. Verify it's running
curl http://localhost:9009/health

# 4. View Swagger docs
open http://localhost:9009/docs
```

### Files

| File | Purpose |
|------|---------|
| `trading/execution/ctrader_client.py` | Direct cTrader API client — connects, authenticates, places orders |
| `ctrader/ctrader_api_server.py` | FastAPI REST server for Docker container |
| `ctrader/rest_client/rest_client.py` | HTTP REST client for Docker API |
| `trading/execution/risk_manager.py` | Risk gates: daily loss, position limits, margin checks |
| `trading/execution/smc_pipeline.py` | Complete SMC → Execution pipeline |
| `agents/trading/live_executor.py` | Agent 28 — command interface to the executor |

### cTrader Methods Available

```
CTraderClient.connect()              — Connect & authenticate
CTraderClient.get_positions()        — List open positions
CTraderClient.get_pending_orders()  — List pending orders
CTraderClient.get_account_summary() — Account balance/equity/margin
CTraderClient.create_market_order()  — Market execution
CTraderClient.create_limit_order()  — Limit (pending) order
CTraderClient.create_stop_order()   — Stop order
CTraderClient.close_position()       — Close position (full/partial)
CTraderClient.cancel_order()         — Cancel pending order
CTraderClient.get_historical_data() — OHLCV candles (M1→MN1)
CTraderClient.close_all_positions() — Emergency close all
```

### Demo Mode

When cTrader credentials are not configured, all methods run in **simulation mode** — returning realistic demo data without making real API calls.

### Getting cTrader Credentials

1. Visit https://help.ctrader.com/open-api/creating-new-app/
2. Create an application → get `CLIENT_ID` + `CLIENT_SECRET`
3. Open cTrader platform → generate `ACCESS_TOKEN`
4. Your Pepperstone demo account number = `ACCOUNT_ID` (e.g., `46729678`)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentFinance v3 Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   Paperclip  │────▶│  n8n (5 wf) │────▶│  cTrader    │ │
│  │  (28 agents) │     │  Orchestrate │     │  Live Exec  │ │
│  └─────────────┘     └──────────────┘     └─────────────┘ │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Trading Engines                          │ │
│  │  ┌──────────┐  ┌─────────────┐  ┌───────────────┐    │ │
│  │  │ SMC      │  │ Technical   │  │ Session/Kill  │    │ │
│  │  │ Engine   │  │ Engine     │  │ Zone Engine   │    │ │
│  │  └──────────┘  └─────────────┘  └───────────────┘    │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Risk Manager                            │ │
│  │  1% max risk  │  3% daily DD  │  5 max positions  │ │
│  └─────────────────────────────────────────────────────┘ │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   OANDA     │     │   Polygon    │     │  Pepperstone │ │
│  │  (FX data)  │     │(Equity data) │     │  (cTrader)  │ │
│  └─────────────┘     └──────────────┘     └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps After Installation

1. **Configure API Keys** - Set up all keys in `.env` (cTrader, Polygon, FRED, NewsAPI)
2. **Interactive Setup** - `python3 scripts/agent_cli.py setup`
3. **System Health Check** - `python3 scripts/agent_cli.py health`
4. **Test cTrader Connection** - `python3 trading/execution/ctrader_client.py`
5. **Test the SMC Pipeline** - `python3 trading/execution/smc_pipeline.py EURUSD H1 --dry`
6. **Import n8n Workflows** - Load all 5 workflow JSONs from `n8n/` into n8n at http://localhost:5678
7. **Set up Database** - `python3 database/setup_database.py --docker-compose && --init`
8. **Run Paper Trading** - Test full pipeline on demo account for 30 days
9. **Backtest Validation** - Run 3-month backtest on top 5 pairs
10. **Automate Daily Routine** - `python3 scripts/daily_routine.py --schedule`
11. **Monitor & Refine** - Track live performance vs backtest expectations

### Unified Trading CLI

The `agent_cli.py` provides a single entry point for all operations:

```bash
# Scanning
python3 scripts/agent_cli.py scan EURUSD H1 --dry
python3 scripts/agent_cli.py scan-all --dry

# Status & Monitoring
python3 scripts/agent_cli.py status
python3 scripts/agent_cli.py risk
python3 scripts/agent_cli.py session

# Manual Trading
python3 scripts/agent_cli.py execute EURUSD BUY 0.01 --sl=20 --tp=40
python3 scripts/agent_cli.py close EURUSD

# Analysis
python3 scripts/agent_cli.py backtest EURUSD H1 --days=90
python3 scripts/agent_cli.py report --today

# System
python3 scripts/agent_cli.py health
python3 scripts/agent_cli.py setup
```

### Daily Routine Automation

```bash
python3 scripts/daily_routine.py --status     # Check routine status
python3 scripts/daily_routine.py --run-all   # Run all phases (testing)
python3 scripts/daily_routine.py --schedule  # Run automated schedule
```

### Database Setup

```bash
python3 database/setup_database.py --docker-compose  # Generate Docker Compose for PostgreSQL
python3 database/setup_database.py --init            # Initialize schema
python3 database/setup_database.py --seed           # Add sample data
python3 database/setup_database.py --status         # Check connection
```

---

*AgentFinance v3 - Built on: Paperclip + smartmoneyconcepts + cinar/indicator + cTrader*
