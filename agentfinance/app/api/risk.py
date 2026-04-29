"""
AgentFinance v5 - Risk API Endpoints

API endpoints for the Risk & Portfolio team:
- POST /risk/check - Run 7-gate risk pipeline on a signal
- GET /risk/status - Get current risk pipeline status
- GET /risk/portfolio - Get portfolio exposure summary
- POST /risk/position-size - Calculate position size
- GET /risk/correlations - Get correlation matrix
- POST /risk/reset-daily - Reset daily loss limit (admin)
- POST /risk/reset-weekly - Reset weekly loss limit (admin)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.teams.risk import RiskPipeline, PortfolioMonitor, PositionSizer
from app.teams.risk.pipeline import GateAction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["risk"])

# Global instances (in production, use dependency injection)
_risk_pipeline = RiskPipeline()
_portfolio_monitor = PortfolioMonitor()
_position_sizer = PositionSizer()


# Request/Response Models
class RiskCheckRequest(BaseModel):
    """Request model for risk check."""
    signal_id: int = Field(..., description="Signal ID to check")
    symbol: str = Field(..., description="Trading symbol")
    direction: str = Field(..., description="Trade direction (buy/sell)")
    confidence: float = Field(..., ge=0, le=100, description="Fund Manager confidence score")
    strategy_tier: str = Field(default="short-term", description="Strategy tier")
    portfolio_id: int = Field(default=1, description="Portfolio ID")


class PositionSizeRequest(BaseModel):
    """Request model for position size calculation."""
    account_balance: float = Field(..., gt=0, description="Account balance")
    symbol: str = Field(..., description="Trading symbol")
    direction: str = Field(..., description="Trade direction")
    strategy_tier: str = Field(default="short-term", description="Strategy tier")
    atr_value: Optional[float] = Field(None, description="ATR(14) value")
    adr_value: Optional[float] = Field(None, description="Average Daily Range")
    risk_multiplier: float = Field(default=1.0, description="Risk multiplier from pipeline")


class RiskCheckResponse(BaseModel):
    """Response model for risk check."""
    signal_id: int
    symbol: str
    direction: str
    confidence: float
    all_gates_passed: bool
    gate_results: List[Dict[str, Any]]
    final_action: str
    position_size_multiplier: float
    blocked_reason: Optional[str]
    checked_at: str


class PortfolioSummaryResponse(BaseModel):
    """Response model for portfolio summary."""
    total_positions: int
    total_quantity: float
    total_pnl: float
    sector_exposures: List[Dict[str, Any]]
    concurrent_limit: Dict[str, Any]
    portfolio_delta: float


# API Endpoints
@router.post("/check", response_model=RiskCheckResponse)
async def check_risk(request: RiskCheckRequest) -> RiskCheckResponse:
    """
    Run the 7-gate risk pipeline on a signal.
    
    Validates a trade signal against all 7 risk gates and returns
    the result with position size multiplier and any blocking reasons.
    """
    logger.info(f"Risk check request for signal {request.signal_id}: {request.symbol} {request.direction}")
    
    try:
        result = _risk_pipeline.check_all_gates(
            signal_id=request.signal_id,
            symbol=request.symbol,
            direction=request.direction,
            confidence=request.confidence,
            strategy_tier=request.strategy_tier,
            portfolio_id=request.portfolio_id,
        )
        
        return RiskCheckResponse(
            signal_id=result.signal_id,
            symbol=result.symbol,
            direction=result.direction,
            confidence=result.confidence,
            all_gates_passed=result.all_gates_passed,
            gate_results=[
                {
                    "gate": g.gate_name.value,
                    "passed": g.passed,
                    "message": g.message,
                    "action": g.action.value if g.action else None,
                    "reduction_factor": g.reduction_factor,
                }
                for g in result.gate_results
            ],
            final_action=result.final_action.value,
            position_size_multiplier=result.position_size_multiplier,
            blocked_reason=result.blocked_reason,
            checked_at=result.checked_at.isoformat(),
        )
        
    except Exception as e:
        logger.error(f"Error in risk check: {e}")
        raise HTTPException(status_code=500, detail=f"Risk check failed: {str(e)}")


@router.get("/status")
async def get_risk_status() -> Dict[str, Any]:
    """
    Get current risk pipeline status.
    
    Returns the status of daily/weekly loss limits and whether
    trading is currently allowed.
    """
    return _risk_pipeline.get_pipeline_status()


@router.get("/portfolio", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(portfolio_id: int = 1) -> PortfolioSummaryResponse:
    """
    Get portfolio exposure summary.
    
    Returns current positions, sector exposures, and risk metrics.
    """
    logger.info(f"Portfolio summary request for portfolio {portfolio_id}")
    
    # In production, fetch from database
    # For now, return empty summary
    positions = []
    
    summary = _portfolio_monitor.get_portfolio_summary(positions)
    
    return PortfolioSummaryResponse(**summary)


@router.post("/position-size")
async def calculate_position_size(request: PositionSizeRequest) -> Dict[str, Any]:
    """
    Calculate position size for a trade.
    
    Uses ATR-based stop distance and ADR consumption limits
    to calculate the appropriate position size.
    """
    logger.info(f"Position size request for {request.symbol} {request.direction}")
    
    try:
        result = _position_sizer.calculate(
            account_balance=request.account_balance,
            symbol=request.symbol,
            direction=request.direction,
            strategy_tier=request.strategy_tier,
            atr_value=request.atr_value,
            adr_value=request.adr_value,
            risk_multiplier=request.risk_multiplier,
        )
        
        return {
            "units": result.units,
            "lot_size": result.lot_size,
            "risk_amount": result.risk_amount,
            "stop_distance_pips": result.stop_distance_pips,
            "atr_value": result.atr_value,
            "risk_percentage": result.risk_percentage,
            "tier_multiplier": result.tier_multiplier,
            "final_multiplier": result.final_multiplier,
        }
        
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        raise HTTPException(status_code=500, detail=f"Position size calculation failed: {str(e)}")


@router.get("/correlations")
async def get_correlations(portfolio_id: int = 1) -> Dict[str, Any]:
    """
    Get correlation matrix for open positions.
    
    Returns the correlation between all open positions
    to help identify concentration risk.
    """
    # In production, fetch positions from database
    positions = []
    
    matrix = _portfolio_monitor.get_correlation_matrix(portfolio_id)
    
    return {
        "portfolio_id": portfolio_id,
        "correlation_matrix": matrix,
        "positions_count": len(positions),
    }


@router.post("/reset-daily")
async def reset_daily_limit() -> Dict[str, str]:
    """
    Reset daily loss limit (admin function).
    
    Manually reset the daily loss limit trigger.
    Should only be used after manual review.
    """
    logger.warning("Daily loss limit manually reset")
    _risk_pipeline.reset_daily_limit()
    
    return {"status": "success", "message": "Daily loss limit reset"}


@router.post("/reset-weekly")
async def reset_weekly_limit() -> Dict[str, str]:
    """
    Reset weekly loss limit (admin function).
    
    Manually reset the weekly loss limit trigger.
    Should only be used after manual review.
    """
    logger.warning("Weekly loss limit manually reset")
    _risk_pipeline.reset_weekly_limit()
    
    return {"status": "success", "message": "Weekly loss limit reset"}


@router.get("/gates")
async def get_gate_info() -> Dict[str, Any]:
    """
    Get information about all 7 risk gates.
    
    Returns gate definitions and their thresholds.
    """
    return {
        "gates": [
            {
                "gate": 1,
                "name": "system_halt",
                "description": "Check if kill switch active or system in paper mode",
                "action_on_fail": "Block live trades; route to paper trade",
            },
            {
                "gate": 2,
                "name": "daily_loss_limit",
                "description": "Check if daily P&L dropped below -5%",
                "action_on_fail": "Stop all trading for the day; alert via Telegram",
            },
            {
                "gate": 3,
                "name": "weekly_loss_limit",
                "description": "Check if weekly P&L dropped below -10%",
                "action_on_fail": "Skip next week; trigger manual review alert",
            },
            {
                "gate": 4,
                "name": "news_window",
                "description": "Check for high-impact news within 30 minutes",
                "action_on_fail": "Block scalp/short-term; allow with larger stop",
            },
            {
                "gate": 5,
                "name": "spread_check",
                "description": "Check if spread > 2x historical average",
                "action_on_fail": "Block entry; log spread spike; retry after 5 min",
            },
            {
                "gate": 6,
                "name": "correlation_check",
                "description": "Check if new position increases correlation > 0.7",
                "action_on_fail": "Reduce 50% if >0.7; block if >0.85",
            },
            {
                "gate": 7,
                "name": "minimum_confidence",
                "description": "Check if Fund Manager confidence >= 65",
                "action_on_fail": "Block if <65; reduce 30% if 65-75; full if >=75",
            },
        ],
        "position_tiers": {
            "scalp": {"atr_multiplier": 0.5, "size_multiplier": 0.5},
            "short-term": {"atr_multiplier": 1.0, "size_multiplier": 0.75},
            "swing": {"atr_multiplier": 1.5, "size_multiplier": 1.0},
            "position": {"atr_multiplier": 2.0, "size_multiplier": 1.0},
        },
    }