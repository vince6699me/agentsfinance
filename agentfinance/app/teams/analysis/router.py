"""
Analysis Router for AgentFinance v5.

Provides unified API for routing analysis requests to appropriate departments
based on sector, instrument, and analysis requirements.

Routes:
- /analyze/{instrument} - Full 6-department analysis
- /analyze/{instrument}/{department} - Single department analysis
- /departments - List all departments
- /departments/{id} - Get department details

Following REST API design principles.
"""

from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from .departments import (
    DepartmentId,
    DepartmentResult,
    get_registry,
    # Import all departments to trigger registration
    fundamental,
    technical,
    sentiment,
    intermarket,
    quantitative,
    smc_ict,
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])


# ============================================================================
# Department Information
# ============================================================================

DEPARTMENT_INFO = {
    1: {
        "id": 1,
        "name": "Fundamental Analysis",
        "description": "Macro economics, forex, commodities, and equity fundamentals",
        "agents": 4,
        "agent_ids": ["T3-D1-A01", "T3-D1-A02", "T3-D1-A03", "T3-D1-A04"],
        "strategies": 7,
    },
    2: {
        "id": 2,
        "name": "Technical Analysis",
        "description": "Price action, indicators, and trend analysis",
        "agents": 3,
        "agent_ids": ["T3-D2-A05", "T3-D2-A06", "T3-D2-A07"],
        "strategies": 10,
    },
    3: {
        "id": 3,
        "name": "Sentiment Analysis",
        "description": "COT, market sentiment, and news NLP",
        "agents": 3,
        "agent_ids": ["T3-D3-A08", "T3-D3-A09", "T3-D3-A10"],
        "strategies": 4,
    },
    4: {
        "id": 4,
        "name": "Intermarket Analysis",
        "description": "Bond-equity, commodity-FX, and correlation analysis",
        "agents": 3,
        "agent_ids": ["T3-D4-A11", "T3-D4-A12", "T3-D4-A13"],
        "strategies": 3,
    },
    5: {
        "id": 5,
        "name": "Quantitative/Systematic",
        "description": "Statistical models, volume, algorithmic execution, optimization",
        "agents": 4,
        "agent_ids": ["T3-D5-A14", "T3-D5-A15", "T3-D5-A16", "T3-D5-A17"],
        "strategies": 10,
    },
    6: {
        "id": 6,
        "name": "SMC/ICT Analysis",
        "description": "Order blocks, market structure, liquidity, kill zones",
        "agents": 4,
        "agent_ids": ["T3-D6-A18", "T3-D6-A19", "T3-D6-A20", "T3-D6-A21"],
        "strategies": 18,
    },
}


# ============================================================================
# Router Functions
# ============================================================================

def get_department_name(dept_id: int) -> str:
    """Get department name by ID."""
    return DEPARTMENT_INFO.get(dept_id, {}).get("name", "Unknown")


def get_department_by_id(dept_id: int) -> Optional[BaseDepartment]:
    """Get department instance by ID."""
    try:
        dept_enum = DepartmentId(dept_id)
        return get_registry().get(dept_enum)
    except ValueError:
        return None


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/departments", response_model=dict[str, Any])
async def list_departments() -> dict[str, Any]:
    """
    List all 6 analysis departments.
    
    Returns department structure, agent counts, and strategy counts.
    """
    return {
        "data": {
            "team": "Analysis",
            "team_id": "T3",
            "total_departments": 6,
            "total_agents": 21,
            "departments": list(DEPARTMENT_INFO.values()),
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/departments/{dept_id}", response_model=dict[str, Any])
async def get_department(dept_id: int) -> dict[str, Any]:
    """
    Get details for a specific department.
    
    Returns department info, agents, and capabilities.
    """
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEPARTMENT_NOT_FOUND",
                    "message": f"Department {dept_id} not found",
                    "valid_ids": list(DEPARTMENT_INFO.keys()),
                },
            },
        )
    
    dept_info = DEPARTMENT_INFO[dept_id].copy()
    dept = get_department_by_id(dept_id)
    
    if dept:
        dept_info["agents_detail"] = dept.get_agents()
    
    return {
        "data": dept_info,
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/analyze/{instrument}", response_model=dict[str, Any])
async def analyze_instrument(
    instrument: str,
    sector: str = Query(..., description="Market sector"),
    timeframe: str = Query("H1", description="Analysis timeframe"),
    departments: Optional[str] = Query(
        None,
        description="Comma-separated department IDs (e.g., '1,2,6') or 'all'",
    ),
) -> dict[str, Any]:
    """
    Run analysis on an instrument.
    
    Executes specified departments or all 6 departments in parallel.
    Returns aggregated signals and confluence scores.
    """
    # Validate sector
    valid_sectors = ["forex", "commodities", "stocks", "indices", "crypto"]
    if sector.lower() not in valid_sectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_SECTOR",
                    "message": f"Invalid sector. Must be one of: {valid_sectors}",
                },
            },
        )
    
    # Determine which departments to run
    if departments and departments != "all":
        try:
            dept_ids = [int(d.strip()) for d in departments.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_DEPARTMENT_LIST",
                        "message": "Departments must be comma-separated integers",
                    },
                },
            )
    else:
        dept_ids = list(DEPARTMENT_INFO.keys())
    
    # Run analysis for each department
    results = []
    for dept_id in dept_ids:
        dept = get_department_by_id(dept_id)
        if dept:
            # In production, use asyncio.gather for parallel execution
            result = await dept.analyze(
                instrument=instrument,
                sector=sector.lower(),
                timeframe=timeframe,
                data={},  # Placeholder - pass actual market data
            )
            results.append({
                "department_id": result.department_id.value,
                "department_name": result.department_name,
                "status": result.status.value,
                "confluence_score": result.confluence_score,
                "signals": result.combined_signals,
                "agent_count": len(result.agent_results),
            })
    
    # Calculate overall confluence
    overall_confluence = (
        sum(r["confluence_score"] for r in results) / len(results)
        if results else 0.0
    )
    
    return {
        "data": {
            "instrument": instrument,
            "sector": sector.lower(),
            "timeframe": timeframe,
            "departments_run": len(results),
            "department_results": results,
            "overall_confluence": round(overall_confluence, 2),
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


@router.get("/analyze/{instrument}/department/{dept_id}", response_model=dict[str, Any])
async def analyze_instrument_single_department(
    instrument: str,
    dept_id: int,
    sector: str = Query(..., description="Market sector"),
    timeframe: str = Query("H1", description="Analysis timeframe"),
) -> dict[str, Any]:
    """
    Run single department analysis on an instrument.
    
    Returns analysis from one specific department.
    """
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEPARTMENT_NOT_FOUND",
                    "message": f"Department {dept_id} not found",
                },
            },
        )
    
    dept = get_department_by_id(dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "DEPARTMENT_NOT_INITIALIZED",
                    "message": f"Department {dept_id} not available",
                },
            },
        )
    
    result = await dept.analyze(
        instrument=instrument,
        sector=sector.lower(),
        timeframe=timeframe,
        data={},
    )
    
    return {
        "data": {
            "instrument": instrument,
            "sector": sector.lower(),
            "timeframe": timeframe,
            "department_id": result.department_id.value,
            "department_name": result.department_name,
            "status": result.status.value,
            "confluence_score": result.confluence_score,
            "signals": result.combined_signals,
            "agent_results": [
                {
                    "agent_id": ar.agent_id,
                    "agent_name": ar.agent_name,
                    "confidence": ar.confidence_score,
                    "signals": ar.signals,
                }
                for ar in result.agent_results
            ],
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# ============================================================================
# Exports
# ============================================================================

__all__ = ["router", "DEPARTMENT_INFO"]


# Need to import BaseDepartment for type hint
from .departments import BaseDepartment  # noqa: E402