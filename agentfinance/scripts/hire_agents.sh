# AgentFinance v3 - Paperclip Agent Hiring Manifest
# Run agents/hire_agents.sh to hire all agents via Paperclip CLI

# Department 1: Public Markets Intelligence (Agents 01-06)
paperclipai agent create \
  --config agents/public/01-sec-filings.yaml \
  --budget $15/month

paperclipai agent create \
  --config agents/public/02-transcripts.yaml \
  --budget $12/month

paperclipai agent create \
  --config agents/public/03-stock-data.yaml \
  --budget $20/month

paperclipai agent create \
  --config agents/public/04-financials.yaml \
  --budget $15/month

paperclipai agent create \
  --config agents/public/05-holdings.yaml \
  --budget $10/month

paperclipai agent create \
  --config agents/public/06-crypto.yaml \
  --budget $15/month

# Department 2: Private Markets Intelligence (Agents 07-12)
paperclipai agent create \
  --config agents/private/07-companies.yaml \
  --budget $12/month

paperclipai agent create \
  --config agents/private/08-funding.yaml \
  --budget $12/month

paperclipai agent create \
  --config agents/private/09-funds.yaml \
  --budget $10/month

paperclipai agent create \
  --config agents/private/10-deals.yaml \
  --budget $12/month

paperclipai agent create \
  --config agents/private/11-investors.yaml \
  --budget $10/month

paperclipai agent create \
  --config agents/private/12-debt.yaml \
  --budget $10/month

# Department 3: Research Intelligence (Agents 13-14)
paperclipai agent create \
  --config agents/research/13-web-scraping.yaml \
  --budget $15/month

paperclipai agent create \
  --config agents/research/14-deep-research.yaml \
  --budget $25/month

# Department 7: Investment Operations (Agents 15-18)
paperclipai agent create \
  --config agents/ops/15-portfolio.yaml \
  --budget $15/month

paperclipai agent create \
  --config agents/ops/16-reporting.yaml \
  --budget $12/month

paperclipai agent create \
  --config agents/ops/17-compliance.yaml \
  --budget $10/month

paperclipai agent create \
  --config agents/ops/18-supervisor.yaml \
  --budget $30/month

# Department 4: Asset Class Intelligence (Agents 19-21)
paperclipai agent create \
  --config agents/trading/19-forex-intelligence.yaml \
  --budget $20/month

paperclipai agent create \
  --config agents/trading/20-commodities-intelligence.yaml \
  --budget $18/month

paperclipai agent create \
  --config agents/trading/21-indices-intelligence.yaml \
  --budget $18/month

# Department 5: Trading Strategy Engine (Agents 22-26)
paperclipai agent create \
  --config agents/trading/22-smc-strategy.yaml \
  --budget $30/month

paperclipai agent create \
  --config agents/trading/23-technical-analysis.yaml \
  --budget $25/month

paperclipai agent create \
  --config agents/trading/24-fundamental-analysis.yaml \
  --budget $20/month

paperclipai agent create \
  --config agents/trading/25-sentiment-intelligence.yaml \
  --budget $18/month

paperclipai agent create \
  --config agents/trading/26-news-intelligence.yaml \
  --budget $20/month

# Department 6: Trading Automation (Agents 27-28)
paperclipai agent create \
  --config agents/trading/27-backtesting.yaml \
  --budget $20/month

paperclipai agent create \
  --config agents/trading/28-live-trading.yaml \
  --budget $25/month

# Set up supervisor as chief orchestrator
paperclipai agent set-master Supervisor-18 --agents "Agent-01 through Agent-28"

# Configure webhook triggers
paperclipai webhook create /filings/new --agent 01
paperclipai webhook create /smc/analyze --agent 22
paperclipai webhook create /trade/execute --agent 28

# Set up scheduled triggers
paperclipai schedule "0 14 * * 1-5" --agent 01  # SEC filings daily at market open
paperclipai schedule "*/15 0-22 * * 1-5" --agent 22  # SMC scan every 15 min
paperclipai schedule "0 6 * * 1-5" --agent 18  # Morning briefing
paperclipai schedule "0 18 * * 0" --agent 27  # Weekly performance
