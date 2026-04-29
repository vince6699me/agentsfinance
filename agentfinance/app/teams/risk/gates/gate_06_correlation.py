"""
AgentFinance v5 - Gate 6: Correlation Check

Gate 6: Correlation Check
Check: Does new position increase portfolio correlation above 0.7?
Action on Fail: Reduce position size by 50% if >0.7; block if >0.85
"""

from typing import Dict, Any, List, Optional
import logging

from app.teams.risk.pipeline import GateName, GateResult, GateAction

logger = logging.getLogger(__name__)


# Correlation matrix for major forex pairs (simulated)
CORRELATION_MATRIX = {
    ("EURUSD", "GBPUSD"): 0.85,
    ("EURUSD", "AUDUSD"): 0.65,
    ("EURUSD", "USDJPY"): -0.75,
    ("EURUSD", "USDCHF"): -0.70,
    ("GBPUSD", "USDJPY"): -0.65,
    ("GBPUSD", "AUDUSD"): 0.70,
    ("USDJPY", "USDCHF"): 0.60,
    ("AUDUSD", "NZDUSD"): 0.80,
    ("USDCAD", "XTIUSD"): 0.55,  # Oil and CAD correlation
    ("XAUUSD", "XTIUSD"): 0.35,  # Gold and Oil
    ("XAUUSD", "USDJPY"): -0.45,  # Gold and JPY (risk sentiment)
}


class Gate6Correlation:
    """
    Gate 6: Correlation Check
    
    Checks if adding a new position would increase portfolio correlation above 0.7.
    - Reduce position by 50% if correlation > 0.7
    - Block entirely if correlation > 0.85
    """

    def __init__(self):
        self.gate_name = GateName.GATE_6_CORRELATION
        self.correlation_reduce_threshold = 0.7
        self.correlation_block_threshold = 0.85

    def check(
        self,
        signal_id: int,
        symbol: str,
        direction: str,
        confidence: float,
        strategy_tier: str,
        portfolio_id: int,
        previous_results: List[GateResult],
    ) -> GateResult:
        """
        Check if new position would create excessive correlation.
        
        Args:
            signal_id: ID of the signal
            symbol: Trading symbol
            direction: Trade direction
            confidence: Confidence score
            strategy_tier: Strategy tier
            portfolio_id: Portfolio ID
            previous_results: Results from previous gates
            
        Returns:
            GateResult with pass/fail and action
        """
        logger.debug(f"Gate 6: Checking correlation for signal {signal_id}, symbol: {symbol}")
        
        # Get current open positions (would be from Portfolio model in production)
        open_positions = self._get_open_positions(portfolio_id)
        
        if not open_positions:
            logger.info(f"Gate 6: No open positions, allowing trade")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message="No open positions - correlation check passed",
                action=None,
                metadata={"open_positions": 0},
            )
        
        # Calculate max correlation with new position
        max_correlation = self._calculate_max_correlation(symbol, open_positions)
        
        logger.info(f"Gate 6: Max correlation for {symbol}: {max_correlation:.2f}")
        
        # Check correlation thresholds
        if max_correlation > self.correlation_block_threshold:
            logger.warning(f"Gate 6: CORRELATION TOO HIGH - {max_correlation:.2f} > {self.correlation_block_threshold}")
            return GateResult(
                gate_name=self.gate_name,
                passed=False,
                message=f"Correlation too high: {max_correlation:.2f} (block threshold: {self.correlation_block_threshold})",
                action=GateAction.BLOCK,
                metadata={
                    "max_correlation": max_correlation,
                    "block_threshold": self.correlation_block_threshold,
                    "open_positions": [p["symbol"] for p in open_positions],
                },
            )
        
        if max_correlation > self.correlation_reduce_threshold:
            logger.warning(f"Gate 6: Correlation elevated - reducing position by 50%")
            return GateResult(
                gate_name=self.gate_name,
                passed=True,
                message=f"Correlation elevated: {max_correlation:.2f} - position reduced by 50%",
                action=None,
                reduction_factor=0.5,
                metadata={
                    "max_correlation": max_correlation,
                    "reduce_threshold": self.correlation_reduce_threshold,
                    "position_reduced": True,
                    "open_positions": [p["symbol"] for p in open_positions],
                },
            )
        
        logger.info(f"Gate 6: Correlation within limits: {max_correlation:.2f}")
        return GateResult(
            gate_name=self.gate_name,
            passed=True,
            message=f"Correlation within limits: {max_correlation:.2f}",
            action=None,
            metadata={
                "max_correlation": max_correlation,
                "open_positions": [p["symbol"] for p in open_positions],
            },
        )

    def _get_open_positions(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Get open positions for portfolio.
        
        In production, query Position model.
        """
        # Simulated: Return empty list (no open positions)
        # In production, query Portfolio.positions
        return []

    def _calculate_max_correlation(self, symbol: str, open_positions: List[Dict[str, Any]]) -> float:
        """
        Calculate maximum correlation between new position and existing positions.
        
        Args:
            symbol: New position symbol
            open_positions: List of existing position symbols
            
        Returns:
            float: Maximum correlation coefficient
        """
        if not open_positions:
            return 0.0
        
        max_corr = 0.0
        
        for pos in open_positions:
            pos_symbol = pos.get("symbol", "")
            corr = self._get_correlation(symbol, pos_symbol)
            if abs(corr) > abs(max_corr):
                max_corr = corr
        
        return abs(max_corr)

    def _get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Get correlation between two symbols."""
        # Check both directions in matrix
        if (symbol1, symbol2) in CORRELATION_MATRIX:
            return CORRELATION_MATRIX[(symbol1, symbol2)]
        if (symbol2, symbol1) in CORRELATION_MATRIX:
            return CORRELATION_MATRIX[(symbol2, symbol1)]
        
        # Default: assume low correlation
        return 0.1

    def get_portfolio_correlation_matrix(self, portfolio_id: int) -> Dict[str, Dict[str, float]]:
        """
        Get correlation matrix for all open positions.
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Dict of symbol -> correlation with other symbols
        """
        positions = self._get_open_positions(portfolio_id)
        symbols = [p["symbol"] for p in positions]
        
        matrix = {}
        for sym1 in symbols:
            matrix[sym1] = {}
            for sym2 in symbols:
                if sym1 != sym2:
                    matrix[sym1][sym2] = self._get_correlation(sym1, sym2)
        
        return matrix