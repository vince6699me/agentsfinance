# AgentFinance v3 - Paperclip Agent Configurations

This directory contains YAML configurations for all 28 agents in AgentFinance v3.

## Directory Structure

```
agents/
├── public/          # Department 1: SEC, earnings, stocks, financials, holdings, crypto
├── private/        # Department 2: Companies, funding, funds, deals, investors, debt
├── research/       # Department 3: Web scraping, deep research
├── trading/        # Department 4-6: Asset class, strategy, automation
└── ops/           # Department 7: Portfolio, reports, compliance, supervisor
```

## Quick Start

```bash
# Deploy all agents
cd ~/agentfinance
cp -r agents/* ~/agency/paperclip/agents/

# Or deploy specific department
cp agents/trading/*.yaml ~/agency/paperclip/agents/
```

## Agent Overview

| Dept | Agent | Mission |
|------|-------|---------|
| 1 | 01-SEC-Filings | SEC filing intelligence (10-K, 10-Q, 8-K, S-1) |
| 1 | 02-Transcripts | Earnings call analysis |
| 1 | 03-Stock-Data | Real-time market data |
| 1 | 04-Financials | Financial statement analysis |
| 1 | 05-Holdings | Institutional ownership |
| 1 | 06-Crypto | Cryptocurrency intelligence |
| 2 | 07-Private-Companies | Private company research |
| 2 | 08-Funding | VC/PE funding analysis |
| 2 | 09-Private-Funds | Fund manager due diligence |
| 2 | 10-Deals | M&A and transaction analytics |
| 2 | 11-Investors | Investor profiling |
| 2 | 12-Private-Debt | Credit & direct lending |
| 3 | 13-Web-Intelligence | Web scraping & extraction |
| 3 | 14-Deep-Research | Multi-source synthesis |
| 4 | 19-Forex-Intelligence | FX market analysis |
| 4 | 20-Commodities | Commodity market analysis |
| 4 | 21-Indices | Global equity indices |
| 5 | 22-SMC-Strategy | Smart Money Concepts |
| 5 | 23-Technical-Analysis | 80+ technical indicators |
| 5 | 24-Fundamental-Analysis | Macro regime & fundamentals |
| 5 | 25-Sentiment | COT, fear/greed, social |
| 5 | 26-News-Intelligence | NLP news analysis |
| 6 | 27-Backtesting | Strategy backtesting |
| 6 | 28-Live-Trading | cTrader execution |
| 7 | 15-Portfolio-Monitor | Real-time risk & alerts |
| 7 | 16-Report-Writer | Research report authoring |
| 7 | 17-Compliance | Investment compliance |
| 7 | 18-Supervisor | Chief orchestrator |

## Agent Configuration Format

```yaml
agent:
  name: Agent Name
  model: codellama:34b
  adapter: python
  script: ~/agentfinance/agents/[dept]/agent_script.py
  skills:
    - skill-name-1
    - skill-name-2
  budget: $25/month
  triggers:
    - cron: "*/15 * * * *"
    - webhook: /api/agent-trigger
  context_window: 32k
  temperature: 0.3
```

## Running Agents

```bash
# Run single agent
paperclipai agent run 19-Forex-Intelligence --command "/fx:scan"

# Run with parameters
paperclipai agent run 22-SMC-Strategy --command "/smc:setup EURUSD"

# Check agent status
paperclipai agents status

# View agent logs
paperclipai logs 19-Forex-Intelligence
```
