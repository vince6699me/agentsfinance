"""
Department Router for AgentFinance v5 Analysis Team.

Provides unified API for routing analysis requests to appropriate departments.

Routes:
- /departments - List all departments
- /departments/{id} - Get department details
- /analyze/{instrument} - Full 6-department analysis
- /analyze/{instrument}/department/{dept_id} - Single department analysis
"""

from typing import Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from . import DepartmentId, get_registry
# Import departments to trigger registration
from . import fundamental, technical, sentiment, intermarket, quantitative, smc_ict


router = APIRouter(prefix="/analysis", tags=["Analysis"])

DEPARTMENT_INFO = {
    1: {"id": 1, "name": "Fundamental Analysis", "description": "Macro, Forex, Commodities, Equity", "agents": 4},
    2: {"id": 2, "name": "Technical Analysis", "description": "Price Action, Indicators, Trend", "agents": 3},
    3: {"id": 3, "name": "Sentiment Analysis", "description": "COT, Market, News NLP", "agents": 3},
    4: {"id": 4, "name": "Intermarket Analysis", "description": "Bond-Equity, Commodity-FX, Correlations", "agents": 3},
    5: {"id": 5, "name": "Quantitative/Systematic", "description": "Statistical, Volume, Algo, Optimiser", "agents": 4},
    6: {"id": 6, "name": "SMC/ICT Analysis", "description": "Order Blocks, Structure, Liquidity, Kill Zones", "agents": 4},
}


@router.get("/departments", response_model=dict[str, Any])
async def list_departments() -> dict[str, Any]:
    """List all 6 analysis departments."""
    return {
        "data": {"total_departments": 6, "total_agents": 21, "departments": list(DEPARTMENT_INFO.values())},
        "meta": {"timestamp": datetime.utcnow().isoformat()},
    }


@router.get("/departments/{dept_id}", response_model=dict[str, Any])
async def get_department(dept_id: int) -> dict[str, Any]:
    """Get details for a specific department."""
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(status_code=404, detail=f"Department {dept_id} not found")
    dept = get_registry().get(DepartmentId(dept_id))
    info = DEPARTMENT_INFO[dept_id].copy()
    if dept:
        info["agents_detail"] = dept.get_agents()
    return {"data": info, "meta": {"timestamp": datetime.utcnow().isoformat()}}


@router.get("/analyze/{instrument}", response_model=dict[str, Any])
async def analyze_instrument(
    instrument: str,
    sector: str = Query(..., description="Market sector"),
    timeframe: str = Query("H1", description="Analysis timeframe"),
    departments: Optional[str] = Query(None, description="Comma-separated department IDs or 'all'"),
) -> dict[str, Any]:
    """Run analysis on an instrument across specified or all departments."""
    valid_sectors = ["forex", "commodities", "stocks", "indices", "crypto"]
    if sector.lower() not in valid_sectors:
        raise HTTPException(status_code=400, detail=f"Invalid sector. Must be one of: {valid_sectors}")

    if departments and departments != "all":
        try:
            dept_ids = [int(d.strip()) for d in departments.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Departments must be comma-separated integers")
    else:
        dept_ids = list(DEPARTMENT_INFO.keys())

    results = []
    for dept_id in dept_ids:
        dept = get_registry().get(DepartmentId(dept_id))
        if dept:
            result = await dept.analyze(instrument, sector.lower(), timeframe, {})
            results.append({
                "department_id": result.department_id.value,
                "department_name": result.department_name,
                "confluence_score": result.confluence_score,
                "signals": result.combined_signals,
                "agent_count": len(result.agent_results),
            })

    overall = sum(r["confluence_score"] for r in results) / len(results) if results else 0.0
    return {
        "data": {
            "instrument": instrument,
            "sector": sector.lower(),
            "timeframe": timeframe,
            "departments_run": len(results),
            "department_results": results,
            "overall_confluence": round(overall, 2),
        },
        "meta": {"timestamp": datetime.utcnow().isoformat()},
    }


@router.get("/analyze/{instrument}/department/{dept_id}", response_model=dict[str, Any])
async def analyze_single_dept(instrument: str, dept_id: int, sector: str = Query(...), timeframe: str = Query("H1")) -> dict[str, Any]:
    """Run single department analysis on an instrument."""
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(status_code=404, detail=f"Department {dept_id} not found")
    dept = get_registry().get(DepartmentId(dept_id))
    if not dept:
        raise HTTPException(status_code=500, detail=f"Department {dept_id} not available")
    result = await dept.analyze(instrument, sector.lower(), timeframe, {})
    return {
        "data": {
            "instrument": instrument,
            "department_id": result.department_id.value,
            "department_name": result.department_name,
            "confluence_score": result.confluence_score,
            "signals": result.combined_signals,
            "agents": [{"agent_id": a.agent_id, "name": a.agent_name, "confidence": a.confidence_score} for a in result.agent_results],
        },
        "meta": {"timestamp": datetime.utcnow().isoformat()},
    }


__all__ = ["router", "DEPARTMENT_INFO"]