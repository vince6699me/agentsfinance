"""
AgentFinance v5 - Risk & Portfolio Team

Responsibility: Apply the 7-gate risk pipeline to every trade approved by Team 4.
Calculate position size, enforce daily/weekly loss limits, check portfolio correlation,
and maintain the portfolio state. Has absolute veto power over all trades.

Sub-Agents:
- Risk Manager: Applies all 7 gates; calculates position size using ATR-based stop
- Portfolio Monitor: Tracks all open positions; calculates net delta per sector
- Checklist Validator: Runs automated ICT pre-trade checklist (9 points)

7-Gate Risk Pipeline:
| Gate | Check | Action on Fail |
|------|-------|----------------|
| 1 | System Halt | Block all live trades; route to paper trade |
| 2 | Daily Loss Limit | Stop all trading for the day; alert via Telegram |
| 3 | Weekly Loss Limit | Skip next week; trigger manual review alert |
| 4 | News Window | Block scalp/short-term; allow with larger stop |
| 5 | Spread Check | Block entry; log spread spike; retry after 5 min |
| 6 | Correlation Check | Reduce 50% if >0.7; block if >0.85 |
| 7 | Minimum Confidence | Block if <65; reduce 30% if 65-75; full if >=75 |
"""

from app.teams.risk.pipeline import RiskPipeline, RiskCheckResult, GateResult
from app.teams.risk.portfolio import PortfolioMonitor
from app.teams.risk.position_sizing import PositionSizer

__all__ = [
    "RiskPipeline",
    "RiskCheckResult",
    "GateResult",
    "PortfolioMonitor",
    "PositionSizer",
]