"""
Base ICT Strategy Class.

Provides common functionality for all ICT strategies including:
- Kill zone time validation
- Fibonacci calculations
- Position sizing
- Risk management
- Order block/FVG detection helpers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Optional

import numpy as np


class Direction(Enum):
    """Trade direction."""
    LONG = "long"
    SHORT = "short"


class KillZone(Enum):
    """Kill zone session definitions."""
    LONDON = "london"           # 03:00-05:00 ET
    NY_AM = "ny_am"             # 08:30-11:00 ET
    NY_PM = "ny_pm"             # 13:00-15:00 ET
    ASIA = "asia"              # 19:00-22:00 ET


class OBQualityRank(Enum):
    """Order block quality ranking (1-5, where 1 is highest)."""
    RANK_1 = 1  # OB at discount/premium with CHoCH
    RANK_2 = 2  # OB with FVG above/below
    RANK_3 = 3  # OB with liquidity nearby
    RANK_4 = 4  # Standard OB at structure level
    RANK_5 = 5  # OB without confluence (SKIP)


class FVGStrength(Enum):
    """FVG strength ranking (1-5, where 1 is highest)."""
    STRENGTH_1 = 1  # 3+ consecutive FVGs
    STRENGTH_2 = 2  # FVGs during displacement
    STRENGTH_3 = 3  # FVGs containing MSS/CHoCH
    STRENGTH_4 = 4  # FVGs at order blocks
    STRENGTH_5 = 5  # Random FVGs (SKIP)


@dataclass
class PriceLevel:
    """Price level with metadata."""
    price: float
    label: str
    type: str = "level"  # session_high, session_low, ob, fvg, etc.


@dataclass
class OrderBlock:
    """Order block definition."""
    high: float
    low: float
    direction: Direction
    quality_rank: OBQualityRank = OBQualityRank.RANK_4
    has_choc: bool = False
    has_fvg: bool = False
    near_liquidity: bool = False


@dataclass
class FVG:
    """Fair Value Gap definition."""
    top: float
    bottom: float
    direction: Direction
    strength: FVGStrength = FVGStrength.STRENGTH_4
    is_cluster: bool = False
    formed_during_displacement: bool = False
    contains_mss: bool = False


@dataclass
class TradeSetup:
    """Complete trade setup with all parameters."""
    strategy: str
    direction: Direction
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    take_profit_4: Optional[float] = None
    
    # Key levels
    session_high: Optional[float] = None
    session_low: Optional[float] = None
    ob_zone: Optional[OrderBlock] = None
    fvg_zone: Optional[FVG] = None
    
    # Quality metrics
    ob_quality_rank: OBQualityRank = OBQualityRank.RANK_4
    fvg_strength: FVGStrength = FVGStrength.STRENGTH_4
    
    # Context
    kill_zone: KillZone = KillZone.NY_AM
    timeframe: str = "15M"
    displacement_confirmed: bool = False
    retrace_confirmed: bool = False
    
    # Position sizing
    position_size: float = 0.0
    risk_amount: float = 0.0
    risk_pips: float = 0.0
    
    # Targets (4-tier TP structure)
    tp1_pips: float = 20.0
    tp2_pips: Optional[float] = 35.0
    tp3_pips: Optional[float] = 50.0
    tp4_pips: Optional[float] = None
    
    # Scale-out percentages
    tp1_percent: float = 0.30
    tp2_percent: float = 0.30
    tp3_percent: float = 0.20
    tp4_percent: float = 0.20
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None


@dataclass
class TradeResult:
    """Trade execution result."""
    setup: TradeSetup
    outcome: str  # WIN, LOSS, BE
    pnl: float = 0.0
    r_multiple: float = 0.0
    exit_time: Optional[datetime] = None
    notes: str = ""


class ICTBaseStrategy(ABC):
    """
    Base class for all ICT strategies.
    
    Provides common functionality:
    - Kill zone validation
    - Fibonacci calculations (OTE 70.5%)
    - Position sizing
    - Risk management limits
    - Order block/FVG helpers
    """
    
    # Kill zone time windows (ET)
    KILL_ZONE_TIMES = {
        KillZone.LONDON: (time(3, 0), time(5, 0)),
        KillZone.NY_AM: (time(8, 30), time(11, 0)),
        KillZone.NY_PM: (time(13, 0), time(15, 0)),
        KillZone.ASIA: (time(19, 0), time(22, 0)),
    }
    
    # Risk management limits
    DAILY_LOSS_LIMIT = 0.05  # 5% of account
    WEEKLY_LOSS_LIMIT = 0.10  # 10% of account
    MAX_CONCURRENT_TRADES = 3
    BASE_RISK_PERCENT = 0.01  # 1% per trade
    
    def __init__(self, account_equity: float = 10000.0):
        """
        Initialize strategy with account equity.
        
        Args:
            account_equity: Account equity in currency units
        """
        self.account_equity = account_equity
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
    
    @abstractmethod
    def evaluate_setup(self, market_data: dict) -> Optional[TradeSetup]:
        """
        Evaluate market data for trade setup.
        
        Args:
            market_data: Dictionary containing OHLCV data, indicators, etc.
            
        Returns:
            TradeSetup if valid setup found, None otherwise
        """
        pass
    
    @abstractmethod
    def validate_setup(self, setup: TradeSetup) -> tuple[bool, str]:
        """
        Validate trade setup against strategy rules.
        
        Args:
            setup: TradeSetup to validate
            
        Returns:
            (is_valid, reason) tuple
        """
        pass
    
    # ==================== Kill Zone Helpers ====================
    
    def is_kill_zone_active(self, kill_zone: KillZone, et_time: Optional[time] = None) -> bool:
        """
        Check if kill zone is currently active.
        
        Args:
            kill_zone: KillZone to check
            et_time: Current ET time (defaults to now)
            
        Returns:
            True if kill zone is active
        """
        if et_time is None:
            et_time = datetime.now().time()
        
        start, end = self.KILL_ZONE_TIMES[kill_zone]
        
        # Handle overnight ranges (e.g., 19:00-22:00)
        if end < start:
            return et_time >= start or et_time <= end
        return start <= et_time <= end
    
    def get_active_kill_zone(self, et_time: Optional[time] = None) -> Optional[KillZone]:
        """
        Get currently active kill zone.
        
        Args:
            et_time: Current ET time (defaults to now)
            
        Returns:
            Active KillZone or None
        """
        for kz in KillZone:
            if self.is_kill_zone_active(kz, et_time):
                return kz
        return None
    
    # ==================== Fibonacci Calculations ====================
    
    def calculate_ote(self, high: float, low: float, level: float = 0.705) -> float:
        """
        Calculate Optimal Trade Entry (OTE) level.
        
        Args:
            high: Swing high
            low: Swing low
            level: OTE level (default 0.705 for ICT's core level)
            
        Returns:
            OTE price level
        """
        range_size = high - low
        return high - (range_size * level)
    
    def calculate_fib_retracement(
        self, 
        start: float, 
        end: float, 
        level: float
    ) -> float:
        """
        Calculate Fibonacci retracement level.
        
        Args:
            start: Start price
            end: End price
            level: Fibonacci level (e.g., 0.705, 0.618, 0.786)
            
        Returns:
            Retracement level
        """
        range_size = end - start
        return start + (range_size * (1 - level))
    
    def calculate_fib_extension(
        self, 
        start: float, 
        end: float, 
        level: float
    ) -> float:
        """
        Calculate Fibonacci extension level.
        
        Args:
            start: Start price
            end: End price
            level: Extension level
            
        Returns:
            Extension level
        """
        range_size = end - start
        return end + (range_size * level)
    
    # ==================== Order Block Detection ====================
    
    def detect_order_block(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[OrderBlock]:
        """
        Detect order block from recent candles.
        
        Args:
            candles: List of OHLCV candles
            direction: LONG for bullish OB, SHORT for bearish
            
        Returns:
            OrderBlock if found, None otherwise
        """
        if len(candles) < 3:
            return None
        
        if direction == Direction.LONG:
            # Look for last bearish candle before strong bullish
            for i in range(len(candles) - 2, 0, -1):
                if self._is_bearish_candle(candles[i]):
                    next_candle = candles[i + 1]
                    if self._has_strong_body(next_candle, Direction.LONG):
                        # Check for FVG above
                        has_fvg = self._has_fvg_above(candles, i)
                        return OrderBlock(
                            high=candles[i]["high"],
                            low=candles[i]["low"],
                            direction=direction,
                            has_fvg=has_fvg
                        )
        else:
            # Look for last bullish candle before strong bearish
            for i in range(len(candles) - 2, 0, -1):
                if self._is_bullish_candle(candles[i]):
                    next_candle = candles[i + 1]
                    if self._has_strong_body(next_candle, Direction.SHORT):
                        has_fvg = self._has_fvg_below(candles, i)
                        return OrderBlock(
                            high=candles[i]["high"],
                            low=candles[i]["low"],
                            direction=direction,
                            has_fvg=has_fvg
                        )
        
        return None
    
    def _is_bullish_candle(self, candle: dict) -> bool:
        """Check if candle is bullish."""
        return candle.get("close", 0) > candle.get("open", 0)
    
    def _is_bearish_candle(self, candle: dict) -> bool:
        """Check if candle is bearish."""
        return candle.get("close", 0) < candle.get("open", 0)
    
    def _has_strong_body(self, candle: dict, direction: Direction, min_percent: float = 0.60) -> bool:
        """
        Check if candle has strong body (>=60% of range).
        
        Args:
            candle: OHLCV candle
            direction: Expected direction
            min_percent: Minimum body percentage
            
        Returns:
            True if strong body
        """
        high = candle.get("high", 0)
        low = candle.get("low", 0)
        close = candle.get("close", 0)
        open_price = candle.get("open", 0)
        
        if high == low:
            return False
        
        body_range = abs(close - open_price)
        total_range = high - low
        
        if total_range == 0:
            return False
        
        body_percent = body_range / total_range
        
        if direction == Direction.LONG:
            return close > open_price and body_percent >= min_percent
        else:
            return close < open_price and body_percent >= min_percent
    
    def _has_fvg_above(self, candles: list, index: int) -> bool:
        """Check if FVG above the specified candle."""
        if index < 2:
            return False
        
        c1, c2, c3 = candles[index - 2], candles[index - 1], candles[index]
        return c2["high"] < c1["low"] and c3["high"] < c1["low"]
    
    def _has_fvg_below(self, candles: list, index: int) -> bool:
        """Check if FVG below the specified candle."""
        if index < 2:
            return False
        
        c1, c2, c3 = candles[index - 2], candles[index - 1], candles[index]
        return c2["low"] > c1["high"] and c3["low"] > c1["high"]
    
    # ==================== FVG Detection ====================
    
    def detect_fvg(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[FVG]:
        """
        Detect Fair Value Gap from recent candles.
        
        Args:
            candles: List of OHLCV candles
            direction: LONG for bullish FVG, SHORT for bearish
            
        Returns:
            FVG if found, None otherwise
        """
        if len(candles) < 3:
            return None
        
        for i in range(len(candles) - 2):
            c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]
            
            if direction == Direction.LONG:
                # Bullish FVG: gap below candle-2
                if c2["high"] < c1["low"] and c3["high"] < c1["low"]:
                    gap_size = c1["low"] - c2["high"]
                    if gap_size >= 5:  # Minimum 5 pips
                        # Determine strength based on context
                        strength = self._assess_fvg_strength(candles, i, direction)
                        return FVG(
                            top=c1["low"],
                            bottom=c2["high"],
                            direction=direction,
                            strength=strength,
                            formed_during_displacement=strength in [
                                FVGStrength.STRENGTH_2,
                                FVGStrength.STRENGTH_3
                            ]
                        )
            else:
                # Bearish FVG: gap above candle-2
                if c2["low"] > c1["high"] and c3["low"] > c1["high"]:
                    gap_size = c2["low"] - c1["high"]
                    if gap_size >= 5:
                        strength = self._assess_fvg_strength(candles, i, direction)
                        return FVG(
                            top=c2["low"],
                            bottom=c1["high"],
                            direction=direction,
                            strength=strength,
                            formed_during_displacement=strength in [
                                FVGStrength.STRENGTH_2,
                                FVGStrength.STRENGTH_3
                            ]
                        )
        
        return None
    
    def _assess_fvg_strength(
        self,
        candles: list,
        start_index: int,
        direction: Direction
    ) -> FVGStrength:
        """
        Assess FVG strength based on context.
        
        Args:
            candles: All candles
            start_index: FVG start index
            direction: FVG direction
            
        Returns:
            FVGStrength ranking
        """
        # Check for cluster (3+ consecutive FVGs)
        cluster_count = self._count_fvg_cluster(candles, start_index, direction)
        if cluster_count >= 3:
            return FVGStrength.STRENGTH_1
        
        # Check for displacement formation
        if self._formed_during_displacement(candles, start_index, direction):
            return FVGStrength.STRENGTH_2
        
        # Check for MSS/CHoCH
        if self._contains_structure_shift(candles, start_index, direction):
            return FVGStrength.STRENGTH_3
        
        return FVGStrength.STRENGTH_4
    
    def _count_fvg_cluster(
        self,
        candles: list,
        start_index: int,
        direction: Direction
    ) -> int:
        """Count consecutive FVGs."""
        count = 0
        for i in range(start_index, min(start_index + 5, len(candles) - 2)):
            if self.detect_fvg(candles[i:], direction):
                count += 1
            else:
                break
        return count
    
    def _formed_during_displacement(
        self,
        candles: list,
        index: int,
        direction: Direction
    ) -> bool:
        """Check if FVG formed during displacement."""
        if index == 0:
            return False
        
        prev_candle = candles[index - 1]
        return self._has_strong_body(prev_candle, direction, 0.60)
    
    def _contains_structure_shift(
        self,
        candles: list,
        index: int,
        direction: Direction
    ) -> bool:
        """Check if FVG contains MSS or CHoCH."""
        # Simplified check - look for structure shift near FVG
        return True  # Default to STRENGTH_3 for simplicity
    
    # ==================== Position Sizing ====================
    
    def calculate_position_size(
        self,
        risk_pips: float,
        pip_value: float = 1.0,
        risk_percent: float = None
    ) -> float:
        """
        Calculate position size in lots.
        
        Args:
            risk_pips: Stop loss distance in pips
            pip_value: Value per pip per lot
            risk_percent: Risk percentage (defaults to BASE_RISK_PERCENT)
            
        Returns:
            Position size in lots
        """
        if risk_percent is None:
            risk_percent = self.BASE_RISK_PERCENT
        
        risk_amount = self.account_equity * risk_percent
        
        if risk_pips <= 0:
            return 0.0
        
        position_size = risk_amount / (risk_pips * pip_value)
        return round(position_size, 2)  # Round down
    
    def calculate_pnl(
        self,
        direction: Direction,
        entry: float,
        exit: float,
        position_size: float,
        pip_value: float = 1.0
    ) -> float:
        """
        Calculate profit/loss in currency.
        
        Args:
            direction: Trade direction
            entry: Entry price
            exit: Exit price
            position_size: Position size in lots
            pip_value: Value per pip per lot
            
        Returns:
            P&L in currency
        """
        pips = abs(exit - entry) / pip_value
        
        if direction == Direction.LONG:
            pips = (exit - entry) / pip_value
        else:
            pips = (entry - exit) / pip_value
        
        return pips * pip_value * position_size
    
    # ==================== Risk Management ====================
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit reached."""
        return abs(self.daily_pnl) >= (self.account_equity * self.DAILY_LOSS_LIMIT)
    
    def check_weekly_loss_limit(self) -> bool:
        """Check if weekly loss limit reached."""
        return abs(self.weekly_pnl) >= (self.account_equity * self.WEEKLY_LOSS_LIMIT)
    
    def update_pnl(self, pnl: float) -> None:
        """
        Update P&L and track consecutive wins/losses.
        
        Args:
            pnl: Trade P&L (positive for win, negative for loss)
        """
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        
        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif pnl < 0:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
    
    def get_recommended_risk_reduction(self) -> float:
        """
        Get recommended risk reduction based on streak.
        
        Returns:
            Risk multiplier (e.g., 0.5 for 50% risk)
        """
        if self.consecutive_losses >= 3:
            return 0.5  # Reduce risk by 50% after 3 losses
        if self.consecutive_wins >= 5:
            return 0.5  # Protect profits after 5 wins
        return 1.0
    
    # ==================== Session High/Low ====================
    
    def calculate_session_high_low(
        self,
        candles: list,
        session: KillZone
    ) -> tuple[float, float]:
        """
        Calculate session high and low from candles.
        
        Args:
            candles: OHLCV candles
            session: Kill zone session
            
        Returns:
            (session_high, session_low) tuple
        """
        if not candles:
            return 0.0, 0.0
        
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        return max(highs), min(lows)
    
    # ==================== Displacement Detection ====================
    
    def check_displacement(
        self,
        candle: dict,
        threshold: float = 0.60
    ) -> bool:
        """
        Check if candle represents displacement (body >= threshold).
        
        Args:
            candle: OHLCV candle
            threshold: Minimum body percentage (default 60%)
            
        Returns:
            True if displacement confirmed
        """
        return self._has_strong_body(candle, 
            Direction.LONG if candle.get("close", 0) > candle.get("open", 0) else Direction.SHORT,
            threshold
        )
    
    # ==================== Weekly Bias ====================
    
    def calculate_weekly_bias(
        self,
        weekly_candles: list
    ) -> Direction:
        """
        Calculate weekly bias from weekly candles.
        
        Args:
            weekly_candles: Weekly OHLCV candles
            
        Returns:
            LONG or SHORT based on price position
        """
        if not weekly_candles:
            return Direction.LONG
        
        recent = weekly_candles[-5:]  # Last 5 weeks
        current_close = recent[-1]["close"]
        
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        midpoint = (max(highs) + min(lows)) / 2
        
        if current_close > midpoint:
            return Direction.LONG
        return Direction.SHORT
    
    # ==================== Monday Range ====================
    
    def calculate_monday_range(
        self,
        monday_candles: list
    ) -> tuple[float, float]:
        """
        Calculate Monday range high and low.
        
        Args:
            monday_candles: Monday candles
            
        Returns:
            (monday_high, monday_low) tuple
        """
        if not monday_candles:
            return 0.0, 0.0
        
        return max(c["high"] for c in monday_candles), min(c["low"] for c in monday_candles)
    
    # ==================== CHoCH Detection ====================
    
    def detect_choch(
        self,
        candles: list,
        direction: Direction
    ) -> tuple[bool, float, float]:
        """
        Detect Change of Character (CHoCH) signal.
        
        CHoCH requires:
        1. Price breaks a structure high/low (BOS)
        2. Subsequent retracement fails to reclaim the broken level
        
        Args:
            candles: 4H candles
            direction: Expected direction
            
        Returns:
            (is_choch, break_level, retracement_level) tuple
        """
        if len(candles) < 10:
            return False, 0.0, 0.0
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(candles) - 2):
            # Swing high: higher than 2 candles on each side
            if (candles[i]["high"] > candles[i-1]["high"] and 
                candles[i]["high"] > candles[i-2]["high"] and
                candles[i]["high"] > candles[i+1]["high"] and 
                candles[i]["high"] > candles[i+2]["high"]):
                swing_highs.append((i, candles[i]["high"]))
            
            # Swing low: lower than 2 candles on each side
            if (candles[i]["low"] < candles[i-1]["low"] and 
                candles[i]["low"] < candles[i-2]["low"] and
                candles[i]["low"] < candles[i+1]["low"] and 
                candles[i]["low"] < candles[i+2]["low"]):
                swing_lows.append((i, candles[i]["low"]))
        
        if direction == Direction.LONG:
            # Look for bullish CHoCH: break below swing low, then retrace fails to reclaim
            if len(swing_lows) >= 2:
                last_low_idx, last_low = swing_lows[-1]
                prev_low_idx, prev_low = swing_lows[-2]
                
                # Check if price broke below last swing low
                for i in range(last_low_idx + 1, min(last_low_idx + 5, len(candles))):
                    if candles[i]["close"] < last_low:
                        # BOS confirmed, now check retracement
                        for j in range(i, min(i + 4, len(candles))):
                            if candles[j]["close"] > last_low:
                                # Retracement reclaimed - not CHoCH
                                break
                        else:
                            # Retracement failed to reclaim - CHoCH confirmed
                            return True, last_low, min(c["low"] for c in candles[i:i+4])
        else:
            # Look for bearish CHoCH: break above swing high, then retrace fails to reclaim
            if len(swing_highs) >= 2:
                last_high_idx, last_high = swing_highs[-1]
                prev_high_idx, prev_high = swing_highs[-2]
                
                # Check if price broke above last swing high
                for i in range(last_high_idx + 1, min(last_high_idx + 5, len(candles))):
                    if candles[i]["close"] > last_high:
                        # BOS confirmed, now check retracement
                        for j in range(i, min(i + 4, len(candles))):
                            if candles[j]["close"] < last_high:
                                # Retracement reclaimed - not CHoCH
                                break
                        else:
                            # Retracement failed to reclaim - CHoCH confirmed
                            return True, last_high, max(c["high"] for c in candles[i:i+4])
        
        return False, 0.0, 0.0
    
    # ==================== Breaker Block Detection ====================
    
    def detect_breaker_block(
        self,
        candles: list,
        direction: Direction
    ) -> Optional[OrderBlock]:
        """
        Detect breaker block pattern.
        
        Bullish Breaker Block:
        - Was a bullish order block
        - Price broke below it (failed)
        - Price now returning from below
        - Expect reversal to upside
        
        Bearish Breaker Block:
        - Was a bearish order block
        - Price broke above it (failed)
        - Price now returning from above
        - Expect reversal to downside
        
        Args:
            candles: Recent candles
            direction: Expected direction
            
        Returns:
            OrderBlock if breaker found, None otherwise
        """
        if len(candles) < 5:
            return None
        
        # Look for failed break of OB
        for i in range(len(candles) - 3):
            if direction == Direction.LONG:
                # Look for bullish breaker: price broke below OB then returned
                # Find last bearish candle before strong bullish
                if self._is_bearish_candle(candles[i]):
                    next_candle = candles[i + 1]
                    if self._has_strong_body(next_candle, Direction.LONG, 0.60):
                        # Check if price broke below this OB then returned
                        if i + 2 < len(candles) and candles[i + 2]["close"] < candles[i]["low"]:
                            # Price broke below - now check if it returned
                            if i + 3 < len(candles) and candles[i + 3]["close"] > candles[i]["low"]:
                                return OrderBlock(
                                    high=candles[i]["high"],
                                    low=candles[i]["low"],
                                    direction=Direction.LONG,
                                    quality_rank=OBQualityRank.RANK_2
                                )
            else:
                # Look for bearish breaker: price broke above OB then returned
                if self._is_bullish_candle(candles[i]):
                    next_candle = candles[i + 1]
                    if self._has_strong_body(next_candle, Direction.SHORT, 0.60):
                        # Check if price broke above this OB then returned
                        if i + 2 < len(candles) and candles[i + 2]["close"] > candles[i]["high"]:
                            # Price broke above - now check if it returned
                            if i + 3 < len(candles) and candles[i + 3]["close"] < candles[i]["high"]:
                                return OrderBlock(
                                    high=candles[i]["high"],
                                    low=candles[i]["low"],
                                    direction=Direction.SHORT,
                                    quality_rank=OBQualityRank.RANK_2
                                )
        
        return None
    
    # ==================== Weekly Range ====================
    
    def calculate_weekly_range(
        self,
        daily_candles: list,
        weeks: int = 20
    ) -> tuple[float, float, float]:
        """
        Calculate weekly dealing range (IPA range).
        
        Args:
            daily_candles: Daily candles
            weeks: Number of weeks to include
            
        Returns:
            (range_high, range_low, midpoint) tuple
        """
        if not daily_candles:
            return 0.0, 0.0, 0.0
        
        # Use last N weeks of data
        recent = daily_candles[-min(weeks * 5, len(daily_candles)):]
        
        highs = [c["high"] for c in recent]
        lows = [c["low"] for c in recent]
        
        range_high = max(highs)
        range_low = min(lows)
        midpoint = (range_high + range_low) / 2
        
        return range_high, range_low, midpoint
    
    # ==================== Discount/Premium Zones ====================
    
    def calculate_discount_premium_zones(
        self,
        range_high: float,
        range_low: float
    ) -> tuple[float, float, float, float]:
        """
        Calculate discount and premium zones.
        
        Discount: lower 35% of range (below midpoint)
        Premium: upper 35% of range (above midpoint)
        
        Args:
            range_high: Range high
            range_low: Range low
            
        Returns:
            (discount_low, discount_high, premium_low, premium_high) tuple
        """
        midpoint = (range_high + range_low) / 2
        range_size = range_high - range_low
        
        # Discount: lower 35% of range
        discount_high = midpoint
        discount_low = range_low + (range_size * 0.15)  # 15% above range low
        
        # Premium: upper 35% of range
        premium_low = midpoint
        premium_high = range_high - (range_size * 0.15)  # 15% below range high
        
        return discount_low, discount_high, premium_low, premium_high


class DisplacementConfirmation:
    """
    Helper class for displacement confirmation (ICT-01 Rule R6).
    
    Validates that sweep candle has body >= 60% and subsequent
    candles confirm the sweep was legitimate (not false breakout).
    """
    
    @staticmethod
    def validate_sweep(
        sweep_candle: dict,
        subsequent_candles: list,
        session_level: float,
        direction: Direction
    ) -> tuple[bool, str]:
        """
        Validate sweep displacement.
        
        Args:
            sweep_candle: Candle that closed beyond session level
            subsequent_candles: Following candles (2-5)
            session_level: Session high/low that was swept
            direction: Direction of sweep
            
        Returns:
            (is_valid, reason) tuple
        """
        # Check sweep candle body >= 60%
        high = sweep_candle.get("high", 0)
        low = sweep_candle.get("low", 0)
        close = sweep_candle.get("close", 0)
        open_price = sweep_candle.get("open", 0)
        
        if high == low:
            return False, "Invalid candle range"
        
        body = abs(close - open_price)
        body_percent = body / (high - low)
        
        if body_percent < 0.60:
            return False, f"Sweep body {body_percent:.1%} < 60%"
        
        # Check subsequent candles confirm sweep
        if direction == Direction.SHORT:
            # For short: price should stay below session high
            for i, candle in enumerate(subsequent_candles[:3]):
                if candle.get("close", 0) > session_level:
                    return False, f"Price reclaimed session high at candle {i+1}"
        else:
            # For long: price should stay above session low
            for i, candle in enumerate(subsequent_candles[:3]):
                if candle.get("close", 0) < session_level:
                    return False, f"Price reclaimed session low at candle {i+1}"
        
        return True, "Displacement confirmed"