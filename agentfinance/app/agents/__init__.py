"""
AgentFinance v5 — 21 Agent Framework

Core agent system with:
- Base agent class/interface
- Role-based system prompts for each of 21 agents
- Agent registration system
- Agent execution framework
"""

from app.agents.base import BaseAgent, AgentConfig, AgentResult
from app.agents.registry import AgentRegistry, get_registry, register_agent
from app.agents.executor import AgentExecutor, execute_agent, execute_all_agents

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
    "AgentRegistry",
    "get_registry",
    "register_agent",
    "AgentExecutor",
    "execute_agent",
    "execute_all_agents",
]

# Agent IDs and their roles
AGENT_ROSTER = {
    # Team 1 — News & Market Data (T1-A1 to T1-A4)
    "T1-A1": {"role": "Macro Intelligence Agent", "department": "News & Market Data"},
    "T1-A2": {"role": "News NLP Agent", "department": "News & Market Data"},
    "T1-A3": {"role": "Sector Data Collector", "department": "News & Market Data"},
    "T1-A4": {"role": "COT Report Agent", "department": "News & Market Data"},
    # Team 2 — Scanner (T2-A1 to T2-A5)
    "T2-A1": {"role": "Forex Scanner", "department": "Scanner"},
    "T2-A2": {"role": "Commodities Scanner", "department": "Scanner"},
    "T2-A3": {"role": "Stocks Scanner", "department": "Scanner"},
    "T2-A4": {"role": "Indices Scanner", "department": "Scanner"},
    "T2-A5": {"role": "Crypto Scanner", "department": "Scanner"},
    # Department 1 — Fundamental Analysis (01-04)
    "01": {"role": "Macro Economics", "department": "Fundamental"},
    "02": {"role": "Forex Fundamentals", "department": "Fundamental"},
    "03": {"role": "Commodities Fundamentals", "department": "Fundamental"},
    "04": {"role": "Equity Fundamentals", "department": "Fundamental"},
    # Department 2 — Technical Analysis (05-07)
    "05": {"role": "Price Action", "department": "Technical"},
    "06": {"role": "Indicators", "department": "Technical"},
    "07": {"role": "Trend Analysis", "department": "Technical"},
    # Department 3 — Sentiment Analysis (08-10)
    "08": {"role": "COT Sentiment", "department": "Sentiment"},
    "09": {"role": "Market Sentiment", "department": "Sentiment"},
    "10": {"role": "News NLP", "department": "Sentiment"},
    # Department 4 — Intermarket Analysis (11-13)
    "11": {"role": "Bond-Equity", "department": "Intermarket"},
    "12": {"role": "Commodity-FX", "department": "Intermarket"},
    "13": {"role": "Correlation Monitor", "department": "Intermarket"},
    # Department 5 — Quantitative/Systematic (14-17)
    "14": {"role": "Statistical Modeller", "department": "Quantitative"},
    "15": {"role": "Volume Analyst", "department": "Quantitative"},
    "16": {"role": "Algorithmic Execution", "department": "Quantitative"},
    "17": {"role": "Parameter Optimiser", "department": "Quantitative"},
    # Department 6 — SMC/ICT Analysis (18-21)
    "18": {"role": "Order Block & FVG", "department": "SMC/ICT"},
    "19": {"role": "Market Structure", "department": "SMC/ICT"},
    "20": {"role": "Liquidity Analyst", "department": "SMC/ICT"},
    "21": {"role": "Session/Kill Zone", "department": "SMC/ICT"},
}