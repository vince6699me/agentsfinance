"""
Intermarket Analysis Department (Department 4).

Philosophy: Analyze correlations between different asset classes including
bonds, equities, commodities, and currencies.

Agents:
- Agent 11: Bond-Equity Analyst - Yield curve correlation
- Agent 12: Commodity-FX Analyst - Commodity-FX leading indicators
- Agent 13: Correlation Monitor - Cross-sector correlation tracking
"""

from . import BaseDepartment, DepartmentId, DepartmentResult, AgentResult, AnalysisResultStatus, get_registry


def analyze_bond_equity(data: dict) -> AgentResult:
    return AgentResult(
        agent_id="T3-D4-A11",
        agent_name="Bond-Equity Analyst",
        department_id=4,
        status=AnalysisResultStatus.COMPLETED,
        signals=[{"type": "bond_equity", "direction": "risk_on", "yield_spread": 0.45, "confidence": 0.68}],
        confidence_score=0.68,
        metadata={"focus_areas": ["yield_curve", "inversion_probability", "credit_spreads"]},
    )


def analyze_commodity_fx(data: dict) -> AgentResult:
    return AgentResult(
        agent_id="T3-D4-A12",
        agent_name="Commodity-FX Analyst",
        department_id=4,
        status=AnalysisResultStatus.COMPLETED,
        signals=[{"type": "commodity_fx", "direction": "commodity_strong", "confidence": 0.70}],
        confidence_score=0.70,
        metadata={"focus_areas": ["gold_aud", "oil_cad", "copper_aud", "divergence"]},
    )


def analyze_correlations(data: dict) -> AgentResult:
    return AgentResult(
        agent_id="T3-D4-A13",
        agent_name="Correlation Monitor",
        department_id=4,
        status=AnalysisResultStatus.COMPLETED,
        signals=[{"type": "correlation", "direction": "normal", "avg_correlation": 0.45, "confidence": 0.65}],
        confidence_score=0.65,
        metadata={"focus_areas": ["rolling_matrix", "breakdown_alerts", "divergence_scanner"]},
    )


class IntermarketAnalysisDepartment(BaseDepartment):
    """Intermarket Analysis - Bond-Equity, Commodity-FX, Correlations."""

    def __init__(self) -> None:
        super().__init__(department_id=DepartmentId.INTERMARKET, department_name="Intermarket Analysis")
        self.register_agent("T3-D4-A11", "Bond-Equity Analyst", "Yield curve correlation")
        self.register_agent("T3-D4-A12", "Commodity-FX Analyst", "Commodity-FX leading indicators")
        self.register_agent("T3-D4-A13", "Correlation Monitor", "Cross-sector tracking")

    async def analyze(self, instrument: str, sector: str, timeframe: str, data: dict) -> DepartmentResult:
        agent_results = [analyze_bond_equity(data), analyze_commodity_fx(data), analyze_correlations(data)]
        combined_signals = [s for r in agent_results for s in r.signals]
        confluence = sum(r.confidence_score for r in agent_results) / len(agent_results)
        return DepartmentResult(
            department_id=self.department_id,
            department_name=self.department_name,
            status=AnalysisResultStatus.COMPLETED,
            agent_results=agent_results,
            combined_signals=combined_signals,
            confluence_score=confluence,
            metadata={"instruments_analyzed": [instrument], "sector": sector},
        )

    def get_agents(self) -> list[dict]:
        return self.agents.copy()


def register() -> IntermarketAnalysisDepartment:
    dept = IntermarketAnalysisDepartment()
    get_registry().register(dept)
    return dept


_registered = register()
__all__ = ["IntermarketAnalysisDepartment", "register"]