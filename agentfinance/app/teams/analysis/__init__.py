"""
Analysis Team for AgentFinance v5.

Provides the Team 3 Analysis module which contains 6 philosophy-based
departments with 21 specialized AI agents.

Structure:
- departments/      - Individual department implementations
- router.py        - API router for analysis endpoints
- __init__.py      - Main exports and setup

Departments:
1. Fundamental Analysis (Agents 01-04)
2. Technical Analysis (Agents 05-07)
3. Sentiment Analysis (Agents 08-10)
4. Intermarket Analysis (Agents 11-13)
5. Quantitative/Systematic (Agents 14-17)
6. SMC/ICT Analysis (Agents 18-21)
"""

from .router import router as analysis_router
from .departments import (
    DepartmentId,
    DepartmentResult,
    AgentResult,
    BaseDepartment,
    DepartmentRegistry,
    get_registry,
    # Import departments
    FundamentalAnalysisDepartment,
    TechnicalAnalysisDepartment,
    SentimentAnalysisDepartment,
    IntermarketAnalysisDepartment,
    QuantitativeDepartment,
    SMCICTDepartment,
)


# Re-export department info
from .router import DEPARTMENT_INFO  # noqa: E402


__all__ = [
    # Router
    "analysis_router",
    # Base classes
    "DepartmentId",
    "DepartmentResult",
    "AgentResult",
    "BaseDepartment",
    "DepartmentRegistry",
    "get_registry",
    # Departments
    "FundamentalAnalysisDepartment",
    "TechnicalAnalysisDepartment",
    "SentimentAnalysisDepartment",
    "IntermarketAnalysisDepartment",
    "QuantitativeDepartment",
    "SMCICTDepartment",
    # Info
    "DEPARTMENT_INFO",
]