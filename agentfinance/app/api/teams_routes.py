"""
Teams API router for AgentFinance v5.

Modular design with separate endpoints for each of the 8 operational teams:
1. News & Market Data
2. Live Markets Scanner
3. Analysis (6 departments)
4. Trade Signals (Debate)
5. Risk & Portfolio
6. Live Traders
7. Backtesting
8. Analytics

Following REST API design: resource-based URLs, consistent response format,
proper error responses, and API versioning.
"""

from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field


router = APIRouter()


# ============================================================================
# Team Definitions
# ============================================================================

TEAMS = {
    "news-market-data": {
        "id": "T1",
        "name": "News & Market Data",
        "description": "Collect news + market data per sector",
        "agents": 4,
        "agents_detail": [
            {"id": "T1-A1", "name": "Macro Intelligence Agent", "role": "Monitor GDP, CPI, PCE, interest rates, CB meetings"},
            {"id": "T1-A2", "name": "News NLP Agent", "role": "Score headlines -1.0 to +1.0 per sector"},
            {"id": "T1-A3", "name": "Sector Data Collector", "role": "Fetch OHLCV, order book, volume"},
            {"id": "T1-A4", "name": "COT Report Agent", "role": "Parse CFTC COT weekly; calculate percentile"},
        ],
    },
    "scanner": {
        "id": "T2",
        "name": "Live Markets Scanner",
        "description": "Scan all 5 sectors for opportunities",
        "agents": 5,
        "agents_detail": [
            {"id": "T2-A1", "name": "Forex Scanner", "sector": "Forex"},
            {"id": "T2-A2", "name": "Commodities Scanner", "sector": "Commodities"},
            {"id": "T2-A3", "name": "Stocks Scanner", "sector": "Stocks"},
            {"id": "T2-A4", "name": "Indices Scanner", "sector": "Indices"},
            {"id": "T2-A5", "name": "Crypto Scanner", "sector": "Crypto"},
        ],
    },
    "analysis": {
        "id": "T3",
        "name": "Analysis",
        "description": "6 philosophy-based departments (21 agents)",
        "agents": 21,
        "departments": [
            {"id": 1, "name": "Fundamental Analysis", "agents": 4, "strategies": 7},
            {"id": 2, "name": "Technical Analysis", "agents": 3, "strategies": 10},
            {"id": 3, "name": "Sentiment Analysis", "agents": 3, "strategies": 4},
            {"id": 4, "name": "Intermarket Analysis", "agents": 3, "strategies": 3},
            {"id": 5, "name": "Quantitative/Systematic", "agents": 4, "strategies": 10},
            {"id": 6, "name": "SMC/ICT Analysis", "agents": 4, "strategies": 18},
        ],
    },
    "trade-signals": {
        "id": "T4",
        "name": "Trade Signals",
        "description": "Bull/Bear/Neutral debate → Fund Manager decision",
        "agents": 4,
        "agents_detail": [
            {"id": "T4-A1", "name": "Bull Analyst", "role": "Argues the long/buy case"},
            {"id": "T4-A2", "name": "Bear Analyst", "role": "Argues the short/sell case"},
            {"id": "T4-A3", "name": "Neutral/Risk Analyst", "role": "Stress-tests both cases"},
            {"id": "T4-A4", "name": "Fund Manager", "role": "Final decision maker"},
        ],
    },
    "risk-portfolio": {
        "id": "T5",
        "name": "Risk & Portfolio",
        "description": "Position sizing, drawdown limits, 7-gate pipeline",
        "agents": 3,
        "agents_detail": [
            {"id": "T5-A1", "name": "Risk Manager", "role": "Applies all 7 gates; calculates position size"},
            {"id": "T5-A2", "name": "Portfolio Monitor", "role": "Tracks open positions; monitors correlation"},
            {"id": "T5-A3", "name": "Checklist Validator", "role": "Runs ICT 9-point checklist before debate"},
        ],
    },
    "live-traders": {
        "id": "T6",
        "name": "Live Traders",
        "description": "Sector-specific execution (cTrader + Bybit)",
        "agents": 5,
        "agents_detail": [
            {"id": "T6-A1", "name": "Forex Trader", "venue": "cTrader"},
            {"id": "T6-A2", "name": "Commodities Trader", "venue": "cTrader"},
            {"id": "T6-A3", "name": "Stocks Trader", "venue": "Bybit"},
            {"id": "T6-A4", "name": "Indices Trader", "venue": "cTrader + Bybit"},
            {"id": "T6-A5", "name": "Crypto Trader", "venue": "Bybit"},
        ],
    },
    "backtesting": {
        "id": "T7",
        "name": "Backtesting",
        "description": "Automated strategy testing",
        "agents": 3,
        "agents_detail": [
            {"id": "T7-A1", "name": "Backtesting Engine", "role": "Run full historical backtests"},
            {"id": "T7-A2", "name": "Parameter Optimiser", "role": "Walk-forward optimisation"},
            {"id": "T7-A3", "name": "Synthetic Data Generator", "role": "Monte Carlo simulation"},
        ],
    },
    "analytics": {
        "id": "T8",
        "name": "Analytics",
        "description": "Performance tracking, A/B tests, meta-evaluation",
        "agents": 4,
        "agents_detail": [
            {"id": "T8-A1", "name": "Meta-Evaluation Agent", "role": "Monitor 21 analysis agents"},
            {"id": "T8-A2", "name": "Latent Pattern Detector", "role": "Find hidden cross-sector patterns"},
            {"id": "T8-A3", "name": "Performance Tracker", "role": "Maintain equity curve, P&L attribution"},
            {"id": "T8-A4", "name": "A/B Test Manager", "role": "Compare agent configurations"},
        ],
    },
}


# ============================================================================
# Team Models
# ============================================================================


class TeamStatusResponse(BaseModel):
    """Standardized team status response."""

    team_id: str
    team_name: str
    status: str
    last_updated: str
    agents_active: int = 0


class ScanSectorRequest(BaseModel):
    """Request model for sector scanning."""

    sector: str = Field(..., description="Sector to scan (forex, commodities, stocks, indices, crypto)")
    timeframe: Optional[str] = Field(default="H1", description="Analysis timeframe")


class ScanResult(BaseModel):
    """Scan result model."""

    sector: str
    opportunities_found: int
    top_opportunities: list[dict[str, Any]]
    scan_time: str


class SignalDebateRequest(BaseModel):
    """Request model for signal debate."""

    signal_id: str
    instrument: str
    sector: str


class DebateResponse(BaseModel):
    """Debate response model."""

    signal_id: str
    bull_case: dict[str, Any]
    bear_case: dict[str, Any]
    neutral_case: dict[str, Any]
    fund_manager_decision: dict[str, Any]
    confidence_score: int


class RiskGateResponse(BaseModel):
    """Risk gate check response."""

    gate_number: int
    gate_name: str
    passed: bool
    details: Optional[str] = None


class TradeExecutionRequest(BaseModel):
    """Trade execution request model."""

    signal_id: str
    instrument: str
    direction: str  # LONG or SHORT
    position_size: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class TradeExecutionResponse(BaseModel):
    """Trade execution response model."""

    trade_id: str
    status: str
    execution_venue: str
    timestamp: str


# ============================================================================
# Team 1: News & Market Data
# ============================================================================


@router.get("/team-1/news", response_model=dict[str, Any])
async def get_news_intelligence(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    hours: int = Query(4, description="Hours of news to retrieve"),
) -> dict[str, Any]:
    """
    Get news and market data intelligence.

    Team 1 collects and processes structured intelligence reports
    across all five market sectors.
    """
    return {
        "data": {
            "team": "News & Market Data",
            "team_id": "T1",
            "sector": sector,
            "time_window_hours": hours,
            "reports": [],  # Placeholder - implement actual news collection
            "sentiment_index": {},  # Placeholder - implement sentiment scoring
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "agents_active": 4,
        },
    }


@router.get("/team-1/macro", response_model=dict[str, Any])
async def get_macro_intelligence() -> dict[str, Any]:
    """
    Get macro intelligence report.

    Monitors GDP, CPI, PCE, interest rates, CB meetings.
    """
    return {
        "data": {
            "team": "Macro Intelligence",
            "team_id": "T1-A1",
            "reports": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/team-1/cot", response_model=dict[str, Any])
async def get_cot_report() -> dict[str, Any]:
    """
    Get COT (Commitments of Traders) report.

    Parses CFTC COT weekly; calculates percentile; detects extremes.
    """
    return {
        "data": {
            "team": "COT Report",
            "team_id": "T1-A4",
            "reports": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# ============================================================================
# Team 2: Live Markets Scanner
# ============================================================================


@router.get("/team-2/scan-sector/{sector}", response_model=ScanResult)
async def scan_sector(
    sector: str,
    timeframe: str = Query("H1", description="Analysis timeframe"),
) -> ScanResult:
    """
    Scan a single sector for trading opportunities.

    Returns ranked opportunities for the specified sector.
    """
    valid_sectors = ["forex", "commodities", "stocks", "indices", "crypto"]
    if sector.lower() not in valid_sectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sector. Must be one of: {valid_sectors}",
        )

    # Placeholder - implement actual scanner logic
    return ScanResult(
        sector=sector.lower(),
        opportunities_found=0,
        top_opportunities=[],
        scan_time=datetime.utcnow().isoformat(),
    )


@router.get("/team-2/scan-all-sectors", response_model=dict[str, Any])
async def scan_all_sectors() -> dict[str, Any]:
    """
    Scan all five sectors in parallel.

    Returns aggregated opportunity list across all markets.
    """
    sectors = ["forex", "commodities", "stocks", "indices", "crypto"]

    return {
        "data": {
            "team": "Live Markets Scanner",
            "team_id": "T2",
            "sectors_scanned": sectors,
            "total_opportunities": 0,
            "results": {},  # Placeholder - implement actual scanning
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_duration_ms": 0,
        },
    }


@router.get("/team-2/sector-opportunities/{sector}", response_model=dict[str, Any])
async def get_sector_opportunities(
    sector: str,
    limit: int = Query(5, ge=1, le=20, description="Number of top opportunities"),
) -> dict[str, Any]:
    """
    Get top opportunities for a specific sector.

    Returns top-N current opportunities with confidence scores.
    """
    return {
        "data": {
            "sector": sector,
            "opportunities": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
        },
    }


# ============================================================================
# Team 3: Analysis (6 Departments)
# ============================================================================


@router.get("/team-3/departments", response_model=dict[str, Any])
async def list_analysis_departments() -> dict[str, Any]:
    """
    List all 6 analysis departments.

    Returns department structure and agent assignments.
    """
    departments = [
        {"id": 1, "name": "Fundamental Analysis", "agents": 4, "strategies": 7},
        {"id": 2, "name": "Technical Analysis", "agents": 3, "strategies": 10},
        {"id": 3, "name": "Sentiment Analysis", "agents": 3, "strategies": 4},
        {"id": 4, "name": "Intermarket Analysis", "agents": 3, "strategies": 3},
        {"id": 5, "name": "Quantitative/Systematic", "agents": 4, "strategies": 10},
        {"id": 6, "name": "SMC/ICT Analysis", "agents": 4, "strategies": 18},
    ]

    return {
        "data": {
            "team": "Analysis",
            "team_id": "T3",
            "total_agents": 21,
            "departments": departments,
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/team-3/analyze/{instrument}", response_model=dict[str, Any])
async def analyze_instrument(
    instrument: str,
    sector: str = Query(..., description="Instrument sector"),
    timeframe: str = Query("H1", description="Analysis timeframe"),
) -> dict[str, Any]:
    """
    Run full analysis on an instrument.

    Executes all 6 departments in parallel for multi-methodology analysis.
    """
    return {
        "data": {
            "team": "Analysis",
            "team_id": "T3",
            "instrument": instrument,
            "sector": sector,
            "timeframe": timeframe,
            "department_results": {},  # Placeholder
            "confluence_score": 0,
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "departments_run": 6,
        },
    }


# ============================================================================
# Team 4: Trade Signals (Debate Mechanism)
# ============================================================================


@router.post("/team-4/debate", response_model=DebateResponse)
async def initiate_debate(request: SignalDebateRequest) -> DebateResponse:
    """
    Initiate Bull/Bear/Neutral debate for a signal.

    Three analysts argue their case before Fund Manager produces final decision.
    """
    # Placeholder - implement actual debate mechanism
    return DebateResponse(
        signal_id=request.signal_id,
        bull_case={"arguments": [], "score": 0},
        bear_case={"arguments": [], "score": 0},
        neutral_case={"risk_assessment": {}, "checklist_score": 0},
        fund_manager_decision={"decision": "NO_TRADE", "rationale": ""},
        confidence_score=0,
    )


@router.get("/team-4/signals", response_model=dict[str, Any])
async def list_signals(
    status: Optional[str] = Query(None, description="Filter by signal status"),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """
    List trade signals with debate outcomes.

    Returns signals with Bull/Bear/NNeutral arguments and Fund Manager decisions.
    """
    return {
        "data": {
            "team": "Trade Signals",
            "team_id": "T4",
            "signals": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
        },
    }


# ============================================================================
# Team 5: Risk & Portfolio
# ============================================================================


@router.post("/team-5/risk-gates/{signal_id}", response_model=dict[str, Any])
async def run_risk_pipeline(signal_id: str) -> dict[str, Any]:
    """
    Run 7-gate risk pipeline for a signal.

    Returns gate-by-gate results with position sizing calculation.
    """
    gates = [
        {"gate": 1, "name": "System Halt", "passed": True},
        {"gate": 2, "name": "Daily Loss Limit", "passed": True},
        {"gate": 3, "name": "Weekly Loss Limit", "passed": True},
        {"gate": 4, "name": "News Window", "passed": True},
        {"gate": 5, "name": "Spread Check", "passed": True},
        {"gate": 6, "name": "Correlation Check", "passed": True},
        {"gate": 7, "name": "Minimum Confidence", "passed": True},
    ]

    return {
        "data": {
            "team": "Risk & Portfolio",
            "team_id": "T5",
            "signal_id": signal_id,
            "gates": gates,
            "all_passed": True,
            "position_size": 0.0,
            "position_sizing_method": "ATR-based",
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/team-5/portfolio", response_model=dict[str, Any])
async def get_portfolio_status() -> dict[str, Any]:
    """
    Get current portfolio status.

    Returns open positions, net delta per sector, correlation matrix.
    """
    return {
        "data": {
            "team": "Risk & Portfolio",
            "team_id": "T5",
            "open_positions": [],
            "total_pnl": 0.0,
            "daily_pnl": 0.0,
            "weekly_pnl": 0.0,
            "correlation_matrix": {},
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# ============================================================================
# Team 6: Live Traders
# ============================================================================


@router.post("/team-6/execute", response_model=TradeExecutionResponse)
async def execute_trade(request: TradeExecutionRequest) -> TradeExecutionResponse:
    """
    Execute a trade via cTrader or Bybit.

    Routes to appropriate execution venue based on sector.
    """
    # Determine execution venue based on sector
    execution_venue = "ctrade"  # Placeholder - implement logic

    return TradeExecutionResponse(
        trade_id=f"trade_{datetime.utcnow().timestamp()}",
        status="pending",
        execution_venue=execution_venue,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/team-6/positions", response_model=dict[str, Any])
async def list_open_positions(
    sector: Optional[str] = Query(None, description="Filter by sector"),
) -> dict[str, Any]:
    """
    List all open positions.

    Returns positions with lifecycle status (TP1, TP2, trailing, etc.).
    """
    return {
        "data": {
            "team": "Live Traders",
            "team_id": "T6",
            "positions": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
        },
    }


# ============================================================================
# Team 7: Backtesting
# ============================================================================


@router.get("/team-7/backtests", response_model=dict[str, Any])
async def list_backtests(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
) -> dict[str, Any]:
    """
    List available backtest results.

    Returns historical backtest results with performance metrics.
    """
    return {
        "data": {
            "team": "Backtesting",
            "team_id": "T7",
            "backtests": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
        },
    }


@router.post("/team-7/run-backtest", response_model=dict[str, Any])
async def run_backtest(
    strategy: str = Query(..., description="Strategy to backtest"),
    sector: str = Query(..., description="Sector to backtest"),
    start_date: str = Query(..., description="Start date"),
    end_date: str = Query(..., description="End date"),
) -> dict[str, Any]:
    """
    Run a new backtest.

    Executes automated strategy backtest on historical data.
    """
    return {
        "data": {
            "team": "Backtesting",
            "team_id": "T7",
            "status": "queued",
            "job_id": f"bt_{datetime.utcnow().timestamp()}",
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# ============================================================================
# Team 8: Analytics
# ============================================================================


@router.get("/team-8/performance", response_model=dict[str, Any])
async def get_performance_metrics(
    period: str = Query("daily", description="Performance period"),
) -> dict[str, Any]:
    """
    Get system performance metrics.

    Returns equity curve, P&L attribution, strategy performance.
    """
    return {
        "data": {
            "team": "Analytics",
            "team_id": "T8",
            "equity_curve": [],
            "pnl_attribution": {},
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "period": period,
        },
    }


@router.get("/team-8/agent-performance", response_model=dict[str, Any])
async def get_agent_performance() -> dict[str, Any]:
    """
    Get individual agent performance metrics.

    Returns accuracy scores for all 21 analysis agents.
    """
    return {
        "data": {
            "team": "Analytics",
            "team_id": "T8",
            "agent_metrics": [],  # Placeholder
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# ============================================================================
# Team Status Endpoints
# ============================================================================


# Valid team names for validation
VALID_TEAMS = list(TEAMS.keys())


@router.get("", response_model=dict[str, Any])
async def list_all_teams() -> dict[str, Any]:
    """
    List all 8 teams with their details.

    Returns complete team structure including agents and descriptions.
    Following REST API design: resource-based URLs, consistent response format.
    """
    teams_list = []
    for team_key, team_data in TEAMS.items():
        teams_list.append({
            "id": team_data["id"],
            "name": team_data["name"],
            "key": team_key,
            "description": team_data["description"],
            "agents": team_data["agents"],
        })

    return {
        "data": {
            "teams": teams_list,
            "total_teams": len(TEAMS),
            "total_agents": sum(team["agents"] for team in TEAMS.values()),
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v1",
        },
    }


@router.get("/{team_name}", response_model=dict[str, Any])
async def get_team_details(team_name: str) -> dict[str, Any]:
    """
    Get details for a specific team.

    Returns complete team information including agent details.
    """
    # Normalize team name
    team_key = team_name.lower().replace(" ", "-").replace("&", "-")

    # Find matching team
    matching_team = None
    for tk, td in TEAMS.items():
        if team_key in tk or tk.replace("-", " ") in team_name.lower():
            matching_team = td
            break

    if not matching_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TEAM_NOT_FOUND",
                    "message": f"Team '{team_name}' not found",
                    "valid_teams": list(TEAMS.keys()),
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    return {
        "data": matching_team,
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v1",
        },
    }


@router.get("/{team_name}/status", response_model=dict[str, Any])
async def get_team_status(team_name: str) -> dict[str, Any]:
    """
    Get operational status for a specific team.

    Returns current team status including last activity and agent states.
    Following REST API design: proper error responses with error field.
    """
    # Normalize team name
    team_key = None
    matching_team = None

    for tk, td in TEAMS.items():
        normalized_input = team_name.lower().replace(" ", "-").replace("&", "-")
        if normalized_input in tk or tk.replace("-", " ") in team_name.lower():
            team_key = tk
            matching_team = td
            break

    if not matching_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TEAM_NOT_FOUND",
                    "message": f"Team '{team_name}' not found",
                    "valid_teams": list(TEAMS.keys()),
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    # Return status (placeholder - implement actual status tracking)
    return {
        "data": {
            "team_id": matching_team["id"],
            "team_name": matching_team["name"],
            "status": "operational",  # Placeholder - implement actual status
            "last_updated": datetime.utcnow().isoformat(),
            "agents_active": matching_team["agents"],
            "agents_total": matching_team["agents"],
            "health": "healthy",
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v1",
        },
    }


@router.get("/{team_name}/tasks", response_model=dict[str, Any])
async def get_team_tasks(
    team_name: str,
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum tasks to return"),
) -> dict[str, Any]:
    """
    Get tasks for a specific team.

    Returns current and recent tasks for the team with status tracking.
    """
    # Normalize team name
    team_key = None
    matching_team = None

    for tk, td in TEAMS.items():
        normalized_input = team_name.lower().replace(" ", "-").replace("&", "-")
        if normalized_input in tk or tk.replace("-", " ") in team_name.lower():
            team_key = tk
            matching_team = td
            break

    if not matching_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "TEAM_NOT_FOUND",
                    "message": f"Team '{team_name}' not found",
                    "valid_teams": list(TEAMS.keys()),
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    # Return empty tasks (placeholder - implement actual task tracking)
    return {
        "data": {
            "team_id": matching_team["id"],
            "team_name": matching_team["name"],
            "tasks": [],  # Placeholder - implement actual task tracking
            "status_filter": status,
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "count": 0,
            "version": "v1",
        },
    }


@router.get("/status", response_model=dict[str, Any])
async def get_all_teams_status() -> dict[str, Any]:
    """
    Get status of all 8 teams.

    Returns operational status for the entire system.
    Following REST API design: consistent response format.
    """
    teams = []
    for team_key, team_data in TEAMS.items():
        teams.append({
            "id": team_data["id"],
            "name": team_data["name"],
            "status": "operational",  # Placeholder - implement actual status
            "agents": team_data["agents"],
            "health": "healthy",
        })

    return {
        "data": {
            "teams": teams,
            "total_agents": sum(team["agents"] for team in TEAMS.values()),
            "system_status": "operational",
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v1",
        },
    }