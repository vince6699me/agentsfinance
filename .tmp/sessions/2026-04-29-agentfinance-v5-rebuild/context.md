# Task Context: AgentFinance v5 Complete Rebuild

**Session ID:** 2026-04-29-agentfinance-v5-rebuild
**Created:** 2026-04-29
**Status:** completed

## Current Request

Complete rebuild of AgentFinance trading system with the following specifications:
- **Architecture:** 8 operational teams with 21 specialized AI agents
- **Teams:** News & Market Data → Scanner → Analysis (6 departments) → Trade Signals (Debate) → Risk & Portfolio → Live Traders → Backtesting → Analytics
- **Market Coverage:** Forex, Commodities (Gold/Oil), Stocks, Indices, Crypto
- **Tech Stack:** Python FastAPI + React/Vite + SQLite + Ollama LLM
- **Execution:** Paper trading only (initially)
- **Database:** SQLite (as specified)

**Implementation Approach:** Staged development starting with core basic features:
- Stage 1: Project skeleton + SQLite setup + basic API + minimal dashboard
- Stage 2: Team structure + agent framework + ICT strategies core
- Stage 3: Scanner endpoints + debate mechanism + risk pipeline
- Stage 4: Dashboard enhancements + analytics + backtesting

## Context Files (Standards to Follow)

- `/home/greywolf/.config/opencode/context/core/standards/code-quality.md` — Modular, functional, maintainable code patterns
- `/home/greywolf/.config/opencode/context/core/standards/security-patterns.md` — Security, input validation, error handling
- `/home/greywolf/.config/opencode/context/development/principles/api-design.md` — REST API design principles
- `/home/greywolf/.config/opencode/context/development/principles/clean-code.md` — Clean code, Python guidelines

## Reference Files (Source Material)

- `/home/greywolf/agentsfinance/gen_v5.md` — Complete v5 project plan (8 teams, 21 agents, 46 strategies)
- `/home/greywolf/agentsfinance/Claude-Agentfinance project restructuring with analysis departments.md` — Department structure
- `/home/greywolf/agentsfinance/smc-ict/ICT-Strategies-Enhancement-Reference.md` — ICT v2 enhancements
- `/home/greywolf/agentsfinance/smc-ict/ICT-01-Micro-Sweep-Scalp.md` through ICT-09 — Full ICT strategy details

## External Docs Fetched

- FastAPI project setup + SQLite integration patterns
- React/Vite scaffolding + configuration
- SQLite connection patterns with Python

## Components

### Backend (FastAPI)
- API endpoints for all 8 teams
- SQLite database with proper schema
- Agent orchestration framework
- Strategy registry with ICT v2 enhancements

### Frontend (React/Vite)
- Basic dashboard with sector selector
- Signals view and activity feed
- Minimal pages (expand in later stages)

### Teams Structure
1. **News & Market Data** — Collect news + market data per sector
2. **Live Markets Scanner** — Scan all 5 sectors for opportunities
3. **Analysis** — 6 philosophy-based departments (21 agents)
4. **Trade Signals** — Bull/Bear/Neutral debate → Fund Manager decision
5. **Risk & Portfolio** — Position sizing, drawdown limits, 7-gate pipeline
6. **Live Traders** — Sector-specific execution (cTrader + Bybit)
7. **Backtesting** — Automated strategy testing
8. **Analytics** — Performance tracking, A/B tests, meta-evaluation

### Core Strategies (Stage 2)
- ICT-01 to ICT-09 (Micro-Sweep, PD Array FVG, Kill-Zone Pulse, Weekly Bias, CHoCH, Sell-Side Redistribution, HTF Structure Break, Discount-Premium, Silver Bullet)
- Structural concepts: MSS, Breaker Blocks, OTE 70.5%, OB Quality Ranking, FVG Strength Ranking

## Constraints

- **Database:** SQLite only (no external DB)
- **Execution:** Paper trading only initially
- **Frontend:** Basic pages first, expand later
- **LLM:** Ollama local models
- **Communication:** Telegram via python-telegram-bot (no n8n)

## Exit Criteria

- [ ] Stage 1: Project skeleton with FastAPI + SQLite + basic React dashboard
- [ ] Stage 2: Team structure implemented with 6 departments + 21 agents
- [ ] Stage 2: ICT strategies core (ICT-01 to ICT-09) with v2 enhancements
- [ ] Stage 3: Scanner endpoints working (`/scan-sector/{sector}`, `/scan-all-sectors`)
- [ ] Stage 3: Debate mechanism implemented (Bull/Bear/Neutral → Fund Manager)
- [ ] Stage 3: Risk pipeline with 7 gates
- [ ] Stage 4: Dashboard with signals view, activity feed, basic analytics