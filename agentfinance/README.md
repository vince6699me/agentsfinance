# AgentFinance v5

**Autonomous Multi-Team AI Trading System**

Version: 5.0.0  
Status: Production-Ready Blueprint  
Architecture: 8 Operational Teams with 21 Specialized AI Agents

---

## Overview

AgentFinance v5 is a complete autonomous trading system that coordinates eight specialized teams — each with dedicated AI agents, tools, and responsibilities — under a Chief Orchestrator that manages signal flow from market data collection through to trade execution and performance analytics.

The system covers five market sectors: Forex, Commodities (Gold/Oil), Stocks, Indices, and Crypto. It deploys 46 institutional-grade signal strategies and 7 execution tactics across all sectors, implemented by 21 specialized AI agents.

---

## Architecture

### 8 Operational Teams

| Team | Description | Agents |
|------|-------------|--------|
| **T1: News & Market Data** | Collect news + market data per sector | 4 |
| **T2: Live Markets Scanner** | Scan all 5 sectors for opportunities | 5 |
| **T3: Analysis** | 6 philosophy-based departments | 21 |
| **T4: Trade Signals** | Bull/Bear/Neutral debate → Fund Manager | 4 |
| **T5: Risk & Portfolio** | Position sizing, drawdown limits, 7-gate pipeline | 3 |
| **T6: Live Traders** | Sector-specific execution (cTrader + Bybit) | 5 |
| **T7: Backtesting** | Automated strategy testing | 3 |
| **T8: Analytics** | Performance tracking, A/B tests, meta-evaluation | 4 |

**Total: 49 agents across 8 teams**

### Market Coverage

| Sector | Instruments | Execution | Primary Strategies |
|--------|-------------|-----------|---------------------|
| Forex | 28+ pairs | cTrader | ICT-01 to 09, Carry Trade |
| Commodities | Gold, Oil | cTrader | ICT-02/03/08, Intermarket |
| Stocks | Top 100 US | Bybit | MACD Divergence, MA Crossover |
| Indices | SP500, NAS100, DAX | cTrader + Bybit | HTF Structure, VIX-EMA |
| Crypto | BTC, ETH, 30+ alts | Bybit | Breakout, Volume, TWAP |

---

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite (included)
- Ollama for local LLM (optional)

### Installation

```bash
# Clone and navigate to project
cd agentfinance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Edit .env with your API keys (optional for initial testing)
```

### Running the Application

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Project Structure

```
agentfinance/
├── app/
│   ├── __init__.py          # Package init
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration with environment variables
│   ├── api/                 # API routers
│   │   ├── __init__.py
│   │   ├── health.py        # Health check endpoints
│   │   └── teams/           # Team endpoints
│   │       └── __init__.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   └── logging.py       # Logging setup
│   └── models/              # Data models
│       └── __init__.py
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .env.template            # Environment template
```

---

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status
- `GET /api/v1/ping` - Simple ping for monitoring

### Team Endpoints
- `GET /api/v1/teams/status` - All teams status
- `GET /api/v1/teams/team-1/news` - News & Market Data
- `GET /api/v1/teams/team-2/scan-sector/{sector}` - Scan single sector
- `GET /api/v1/teams/team-2/scan-all-sectors` - Scan all sectors
- `POST /api/v1/teams/team-4/debate` - Initiate signal debate
- `POST /api/v1/teams/team-5/risk-gates/{signal_id}` - Run risk pipeline
- `POST /api/v1/teams/team-6/execute` - Execute trade

---

## Configuration

All configuration is managed through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | AgentFinance v5 | Application name |
| `DEBUG` | false | Debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `PAPER_MODE` | true | Paper trading mode |
| `LOG_LEVEL` | INFO | Logging level |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server |
| `OLLAMA_MODEL` | llama3.1:8b | Default LLM model |

### API Keys (Optional)

For full functionality, configure:
- `OANDA_API_KEY`, `OANDA_ACCOUNT_ID` - Forex/Commodities
- `BYBIT_API_KEY`, `BYBIT_API_SECRET` - Crypto/Stocks
- `TELEGRAM_BOT_TOKEN` - Notifications
- `FINNHUB_API_KEY` - Market data

---

## Design Principles

### Modular Design
- Single responsibility per module
- Clear interfaces (explicit inputs/outputs)
- Independent and composable

### Functional Approach
- Pure functions where possible
- Immutability (create new data, don't modify)
- Composition over inheritance

### Clean Code
- Meaningful names
- Small functions (< 50 lines)
- Error handling at boundaries

### REST API Design
- Resource-based URLs
- Standard HTTP status codes
- Consistent response format

---

## Development Status

### Stage 1: Complete ✅
- [x] Project skeleton with FastAPI
- [x] SQLite database setup
- [x] Basic API endpoints
- [x] Health checks

### Stage 2: In Progress
- [ ] Team structure with 6 departments + 21 agents
- [ ] ICT strategies core (ICT-01 to ICT-09)
- [ ] Agent orchestration framework

### Stage 3: Planned
- [ ] Scanner endpoints
- [ ] Debate mechanism
- [ ] Risk pipeline with 7 gates

### Stage 4: Future
- [ ] Dashboard with signals view
- [ ] Activity feed
- [ ] Basic analytics

---

## License

CONFIDENTIAL — INTERNAL SYSTEM DOCUMENTATION

---

## Support

For internal development support, contact the AgentFinance development team.