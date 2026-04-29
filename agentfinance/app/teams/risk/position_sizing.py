"""
AgentFinance v5 - Position Sizing Calculator

Calculates position size based on:
- Account balance and risk percentage
- ATR-based stop distance
- ADR (Average Daily Range) consumption limit (80% rule)
- Strategy tier adjustments
- Correlation-adjusted sizing (portfolio correlation matrix)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class PositionSizeResult:
    """Result of position size calculation."""
    units: float
    lot_size: float
    risk_amount: float
    stop_distance_pips: float
    atr_value: float
    risk_percentage: float
    tier_multiplier: float
    final_multiplier: float
    correlation_adjustment: float = 1.0
    adr_consumption_pct: float = 0.0
    adr_adjusted: bool = False


@dataclass
class CorrelationState:
    """State of portfolio correlation tracking."""
    matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    open_positions: List[Dict[str, Any]] = field(default_factory=list)


class PositionSizer:
    """
    Position size calculator using ATR-based stops.
    
    Calculates position size using:
    - Risk per trade (default 1-2% of account)
    - ATR(14) stop distance
    - ADR consumption limit (80% rule)
    - Strategy tier adjustments
    - Correlation-adjusted sizing (portfolio correlation matrix)
    """

    # ATR multiples by strategy tier
    ATR_MULTIPLIERS = {
        "scalp": 0.5,
        "short-term": 1.0,
        "swing": 1.5,
        "position": 2.0,
    }

    # Position size multipliers by strategy tier
    TIER_MULTIPLIERS = {
        "scalp": 0.5,
        "short-term": 0.75,
        "swing": 1.0,
        "position": 1.0,
    }

    # Correlation thresholds
    CORRELATION_REDUCE_THRESHOLD = 0.7
    CORRELATION_BLOCK_THRESHOLD = 0.85

    def __init__(self):
        self.default_risk_percentage = 0.02  # 2% default
        self.adr_consumption_limit = 0.80  # 80% ADR limit
        self._correlation_state = CorrelationState()
        self._correlation_update_interval = timedelta(minutes=15)

    # ========== CORRELATION MATRIX ==========

    # Full correlation matrix for all monitored instruments
    CORRELATION_MATRIX: Dict[str, Dict[str, float]] = {
        "EURUSD": {"GBPUSD": 0.85, "AUDUSD": 0.65, "USDJPY": -0.75, "USDCHF": -0.70, "USDCAD": 0.45, "XAUUSD": 0.25, "XTIUSD": 0.15},
        "GBPUSD": {"EURUSD": 0.85, "AUDUSD": 0.70, "USDJPY": -0.65, "USDCHF": -0.55, "USDCAD": 0.50, "XAUUSD": 0.30, "XTIUSD": 0.20},
        "USDJPY": {"EURUSD": -0.75, "GBPUSD": -0.65, "USDCHF": 0.60, "XAUUSD": -0.45, "XTIUSD": -0.25},
        "USDCHF": {"EURUSD": -0.70, "GBPUSD": -0.55, "USDJPY": 0.60, "USDCAD": 0.40},
        "AUDUSD": {"EURUSD": 0.65, "GBPUSD": 0.70, "NZDUSD": 0.80, "USDCAD": 0.55},
        "USDCAD": {"EURUSD": 0.45, "GBPUSD": 0.50, "USDCHF": 0.40, "AUDUSD": 0.55, "XTIUSD": 0.55},
        "NZDUSD": {"AUDUSD": 0.80, "EURUSD": 0.50, "GBPUSD": 0.55},
        "XAUUSD": {"EURUSD": 0.25, "GBPUSD": 0.30, "USDJPY": -0.45, "XTIUSD": 0.35},
        "XTIUSD": {"USDCAD": 0.55, "XAUUSD": 0.35, "EURUSD": 0.15, "GBPUSD": 0.20, "USDJPY": -0.25},
    }

    def update_correlation_matrix(self, open_positions: List[Dict[str, Any]]) -> None:
        """
        Update correlation state with current open positions.
        
        Called every 15 minutes by the risk pipeline.
        
        Args:
            open_positions: List of open position dicts with 'symbol' key
        """
        self._correlation_state.open_positions = open_positions
        self._correlation_state.last_updated = datetime.utcnow()
        
        # Build matrix for open positions only
        symbols = [p.get("symbol", "") for p in open_positions if p.get("symbol")]
        matrix = {}
        
        for sym1 in symbols:
            matrix[sym1] = {}
            for sym2 in symbols:
                if sym1 != sym2:
                    matrix[sym1][sym2] = self._get_correlation(sym1, sym2)
        
        self._correlation_state.matrix = matrix
        logger.info(f"Correlation matrix updated with {len(open_positions)} positions")

    def _get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Get correlation between two symbols."""
        if symbol1 in self.CORRELATION_MATRIX:
            return self.CORRELATION_MATRIX[symbol1].get(symbol2, 0.1)
        if symbol2 in self.CORRELATION_MATRIX:
            return self.CORRELATION_MATRIX[symbol2].get(symbol1, 0.1)
        return 0.1  # Default low correlation

    def get_max_correlation(self, symbol: str) -> float:
        """
        Get maximum correlation of symbol with any open position.
        
        Args:
            symbol: Trading symbol to check
            
        Returns:
            Maximum correlation coefficient (0-1)
        """
        if not self._correlation_state.open_positions:
            return 0.0
        
        max_corr = 0.0
        for pos in self._correlation_state.open_positions:
            pos_symbol = pos.get("symbol", "")
            corr = abs(self._get_correlation(symbol, pos_symbol))
            if corr > max_corr:
                max_corr = corr
        
        return max_corr

    def calculate_correlation_adjustment(self, symbol: str) -> float:
        """
        Calculate position size adjustment based on portfolio correlation.
        
        Correlation-Adjusted Sizing Rules:
        - Correlation < 0.7: No adjustment (1.0)
        - Correlation 0.7-0.85: Reduce position by 50% (0.5)
        - Correlation > 0.85: Full block (0.0) - caller should handle this
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Adjustment factor (0.0 to 1.0)
        """
        max_corr = self.get_max_correlation(symbol)
        
        if max_corr >= self.CORRELATION_BLOCK_THRESHOLD:
            logger.warning(f"Correlation {max_corr:.2f} >= {self.CORRELATION_BLOCK_THRESHOLD} - FULL BLOCK")
            return 0.0
        
        if max_corr >= self.CORRELATION_REDUCE_THRESHOLD:
            # Linear reduction: 0.7 -> 0.5, 0.85 -> 0.0
            reduction = (max_corr - self.CORRELATION_REDUCE_THRESHOLD) / (self.CORRELATION_BLOCK_THRESHOLD - self.CORRELATION_REDUCE_THRESHOLD)
            adjustment = 1.0 - (reduction * 0.5)  # Reduce by up to 50%
            logger.info(f"Correlation {max_corr:.2f} - position reduced to {adjustment:.1%}")
            return adjustment
        
        return 1.0  # No adjustment needed

    def is_correlation_blocked(self, symbol: str) -> bool:
        """Check if symbol should be blocked due to correlation."""
        return self.get_max_correlation(symbol) >= self.CORRELATION_BLOCK_THRESHOLD

    def calculate(
        self,
        account_balance: float,
        symbol: str,
        direction: str,
        strategy_tier: str = "short-term",
        atr_value: Optional[float] = None,
        adr_value: Optional[float] = None,
        risk_multiplier: float = 1.0,
        open_positions: Optional[List[Dict[str, Any]]] = None,
    ) -> PositionSizeResult:
        """
        Calculate position size for a trade.
        
        Args:
            account_balance: Account balance in account currency
            symbol: Trading symbol (e.g., "EURUSD")
            direction: Trade direction ("buy" or "sell")
            strategy_tier: Strategy tier ("scalp", "short-term", "swing", "position")
            atr_value: ATR(14) value (if known)
            adr_value: Average Daily Range (if known)
            risk_multiplier: Additional risk multiplier from risk pipeline
            open_positions: List of open positions for correlation check
            
        Returns:
            PositionSizeResult with calculated position size
        """
        logger.info(f"Calculating position size for {symbol} {direction} ({strategy_tier})")
        
        # Update correlation matrix if open positions provided
        adr_adjusted = False
        if open_positions:
            self.update_correlation_matrix(open_positions)
        
        # Get ATR value (simulated - in production, fetch from market data)
        if atr_value is None:
            atr_value = self._get_atr(symbol)
        
        # Get ADR value
        if adr_value is None:
            adr_value = self._get_adr(symbol)
        
        # Get ATR multiplier for strategy tier
        atr_multiplier = self.ATR_MULTIPLIERS.get(strategy_tier, 1.0)
        
        # Calculate stop distance in pips
        stop_distance_pips = atr_value * atr_multiplier
        
        # Track ADR consumption
        adr_consumption_pct = 0.0
        
        # Check ADR consumption limit (80% rule)
        if adr_value and adr_value > 0:
            adr_consumption_pct = stop_distance_pips / adr_value
            if adr_consumption_pct > self.adr_consumption_limit:
                logger.warning(f"ADR consumption: {adr_consumption_pct:.2%} > {self.adr_consumption_limit:.2%} - reducing stop")
                # Adjust stop to stay within 80% ADR
                stop_distance_pips = adr_value * self.adr_consumption_limit
                adr_adjusted = True
                logger.info(f"Adjusted stop distance to {stop_distance_pips:.2f} pips (80% ADR)")
        
        # Calculate risk amount
        risk_percentage = self.default_risk_percentage * risk_multiplier
        risk_amount = account_balance * risk_percentage
        
        # Calculate position size
        # For forex: units = risk_amount / stop_distance
        # Note: For non-forex, pip value calculation differs
        pip_value = self._get_pip_value(symbol)
        if pip_value and stop_distance_pips > 0:
            units = risk_amount / (stop_distance_pips * pip_value)
        else:
            # Fallback calculation
            units = risk_amount / stop_distance_pips if stop_distance_pips > 0 else 0
        
        # Apply tier multiplier
        tier_multiplier = self.TIER_MULTIPLIERS.get(strategy_tier, 1.0)
        
        # ========== CORRELATION-ADJUSTED SIZING ==========
        # Calculate correlation adjustment
        correlation_adjustment = self.calculate_correlation_adjustment(symbol)
        
        # Check if correlation blocks the trade entirely
        if correlation_adjustment == 0.0:
            logger.warning(f"Position BLOCKED due to correlation: {symbol}")
            return PositionSizeResult(
                units=0.0,
                lot_size=0.0,
                risk_amount=0.0,
                stop_distance_pips=stop_distance_pips,
                atr_value=atr_value,
                risk_percentage=risk_percentage,
                tier_multiplier=tier_multiplier,
                final_multiplier=0.0,
                correlation_adjustment=0.0,
                adr_consumption_pct=adr_consumption_pct,
                adr_adjusted=adr_adjusted,
            )
        
        # Apply correlation adjustment
        final_units = units * tier_multiplier * correlation_adjustment
        
        # Calculate lot size (standard lots)
        lot_size = final_units / 100000  # 1 standard lot = 100,000 units
        
        logger.info(f"Position size: {final_units:.0f} units ({lot_size:.2f} lots), risk: ${risk_amount:.2f}")
        logger.info(f"  - ATR stop: {atr_multiplier}x ATR = {stop_distance_pips:.2f} pips")
        logger.info(f"  - ADR consumption: {adr_consumption_pct:.1%} {'(adjusted)' if adr_adjusted else ''}")
        logger.info(f"  - Correlation adjustment: {correlation_adjustment:.1%}")
        
        return PositionSizeResult(
            units=final_units,
            lot_size=lot_size,
            risk_amount=risk_amount,
            stop_distance_pips=stop_distance_pips,
            atr_value=atr_value,
            risk_percentage=risk_percentage,
            tier_multiplier=tier_multiplier,
            final_multiplier=risk_multiplier * tier_multiplier * correlation_adjustment,
            correlation_adjustment=correlation_adjustment,
            adr_consumption_pct=adr_consumption_pct,
            adr_adjusted=adr_adjusted,
        )

    def _get_atr(self, symbol: str) -> float:
        """
        Get ATR(14) value for symbol.
        
        In production, calculate from historical data or fetch from API.
        """
        # Simulated ATR values
        atr_values = {
            "EURUSD": 0.0015,  # 15 pips
            "GBPUSD": 0.0020,  # 20 pips
            "USDJPY": 0.15,    # 15 pips
            "USDCHF": 0.0015,
            "AUDUSD": 0.0018,
            "USDCAD": 0.0015,
            "NZDUSD": 0.0020,
            "XAUUSD": 15.0,    # Gold
            "XTIUSD": 1.5,     # Oil
        }
        return atr_values.get(symbol, 0.0015)

    def _get_adr(self, symbol: str) -> float:
        """
        Get Average Daily Range for symbol.
        
        In production, calculate from historical data.
        """
        # Simulated ADR values
        adr_values = {
            "EURUSD": 0.0120,  # 120 pips
            "GBPUSD": 0.0150,  # 150 pips
            "USDJPY": 1.20,    # 120 pips
            "USDCHF": 0.0120,
            "AUDUSD": 0.0150,
            "USDCAD": 0.0120,
            "NZDUSD": 0.0150,
            "XAUUSD": 25.0,    # Gold
            "XTIUSD": 2.5,     # Oil
        }
        return adr_values.get(symbol, 0.0120)

    def _get_pip_value(self, symbol: str) -> Optional[float]:
        """
        Get pip value in account currency for standard lot.
        
        For forex pairs with USD as quote currency, pip = $10
        """
        # Simplified pip values
        if "USD" in symbol:
            return 10.0  # $10 per pip for standard lot
        return None

    def calculate_risk_reward(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        direction: str,
    ) -> Dict[str, float]:
        """
        Calculate risk:reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            direction: "buy" or "sell"
            
        Returns:
            Dict with risk, reward, and ratio
        """
        if direction == "buy":
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk > 0:
            ratio = reward / risk
        else:
            ratio = 0.0
        
        return {
            "risk": risk,
            "reward": reward,
            "risk_reward_ratio": ratio,
            "is_favorable": ratio >= 2.0,
        }

    def validate_position_size(
        self,
        units: float,
        account_balance: float,
        max_position_percentage: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Validate position size against account limits.
        
        Args:
            units: Calculated position units
            account_balance: Account balance
            max_position_percentage: Maximum % of account for single position
            
        Returns:
            Dict with validation result
        """
        position_value = units * self._get_pip_value("EURUSD") or 0
        position_percentage = position_value / account_balance if account_balance > 0 else 0
        
        is_valid = position_percentage <= max_position_percentage
        
        return {
            "is_valid": is_valid,
            "position_value": position_value,
            "position_percentage": position_percentage,
            "max_percentage": max_position_percentage,
            "message": "Position size OK" if is_valid else f"Position too large: {position_percentage:.1%} of account",
        }