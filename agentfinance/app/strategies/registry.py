"""
AgentFinance v5 - Strategy Registry

Central registry containing all 46 signal strategies and 7 execution tactics.
Provides lookup by category, tier, sector, and strategy ID.

Strategy Blocks:
- Block 1: ICT/SMC (18 strategies)
- Block 2: Technical Analysis (10 strategies)
- Block 3: Fundamental & Intermarket (7 strategies)
- Block 4: Sentiment & Volatility (4 strategies)
- Block 5: Range, Breakout & Volume (3 strategies)
- Block 6: Execution Tactics (7 tactics)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyDefinition:
    """Definition of a trading strategy or execution tactic."""
    strategy_id: str
    name: str
    category: str
    tier: Optional[str]
    sector: str
    department: str
    is_tactic: bool = False
    description: str = ""
    target_pips: Optional[str] = None
    v2_enabled: bool = False
    parameters: Dict = field(default_factory=dict)
    # v2 enhancement fields
    ob_quality_filter: Optional[str] = None
    fvg_strength_filter: Optional[str] = None
    ote_level: Optional[str] = None
    kill_zone_required: bool = False
    mss_alternate: bool = False
    tp_tiers: Optional[List[Dict]] = None


class StrategyRegistry:
    """
    Central registry for all trading strategies and execution tactics.
    
    Provides methods to:
    - Get strategy by ID
    - List strategies by category
    - List strategies by tier
    - List strategies by sector
    - List all execution tactics
    - Search strategies by keyword
    """
    
    def __init__(self):
        self._strategies: Dict[str, StrategyDefinition] = {}
        self._by_category: Dict[str, List[str]] = {}
        self._by_tier: Dict[str, List[str]] = {}
        self._by_sector: Dict[str, List[str]] = {}
        self._by_department: Dict[str, List[str]] = {}
        self._tactics: List[str] = []
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize all 46 strategies and 7 tactics."""
        
        # =========================================================================
        # BLOCK 1 — ICT / Smart Money Concepts (18 strategies)
        # =========================================================================
        
        # ICT-01 to ICT-09 (Core ICT strategies)
        self._register(StrategyDefinition(
            strategy_id="ICT-01",
            name="Micro-Sweep Scalp",
            category="ict",
            tier="scalp",
            sector="forex",
            department="smc_ict",
            description="Scalp strategy using micro-sweep patterns with OB quality and FVG strength filters. Targets 20 pips.",
            target_pips="20",
            v2_enabled=True,
            ob_quality_filter="1-3",
            fvg_strength_filter="1-3",
            ote_level="70.5%",
            kill_zone_required=True,
            mss_alternate=True,
            parameters={
                "ob_rank_range": [1, 3],
                "fvg_strength_range": [1, 3],
                "ote_primary": 0.705,
                "ote_secondary": 0.618,
                "ote_tertiary": 0.786,
                "mss_position_size": 0.50,
                "kill_zones": ["asian", "london", "london_open", "ny", "london_close"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-02",
            name="PD Array FVG Scalp",
            category="ict",
            tier="scalp",
            sector="forex",
            department="smc_ict",
            description="Scalp strategy using PD Array (Previous Day) Fair Value Gaps. Targets 25 pips.",
            target_pips="25",
            v2_enabled=True,
            fvg_strength_filter="1-3",
            ote_level="70.5%",
            kill_zone_required=True,
            mss_alternate=True,
            parameters={
                "fvg_strength_range": [1, 3],
                "ote_primary": 0.705,
                "pd_array_required": True,
                "kill_zones": ["london", "ny"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-03",
            name="Kill-Zone Pulse",
            category="ict",
            tier="short-term",
            sector="forex",
            department="smc_ict",
            description="Short-term strategy leveraging kill zone momentum. Targets 30-50 pips.",
            target_pips="30-50",
            v2_enabled=True,
            ob_quality_filter="1-3",
            ote_level="70.5%",
            kill_zone_required=True,
            mss_alternate=True,
            parameters={
                "ob_rank_range": [1, 3],
                "ote_primary": 0.705,
                "mss_dual_path": True,
                "kill_zones": ["london", "london_open", "ny"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-04",
            name="Weekly Bias Expansion",
            category="ict",
            tier="short-term",
            sector="forex",
            department="smc_ict",
            description="Short-term strategy using weekly bias expansion patterns. Targets 50 pips. Tue/Wed only.",
            target_pips="50",
            v2_enabled=True,
            fvg_strength_filter="1-3",
            ote_level="70.5%",
            kill_zone_required=True,
            mss_alternate=True,
            parameters={
                "fvg_strength_range": [1, 3],
                "ote_primary": 0.705,
                "mss_position_size": 0.75,
                "days_allowed": ["tuesday", "wednesday"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-05",
            name="CHoCH Momentum Swing",
            category="ict",
            tier="swing",
            sector="forex",
            department="smc_ict",
            description="Swing strategy using Change of Character (CHoCH) momentum. Targets 75-100 pips.",
            target_pips="75-100",
            v2_enabled=True,
            ob_quality_filter="1-4",
            kill_zone_required=True,
            mss_alternate=True,
            tp_tiers=[
                {"tier": "TP1", "r_multiple": 1.0, "position_close": 0.25},
                {"tier": "TP2", "r_multiple": 1.5, "position_close": 0.25},
                {"tier": "TP3", "r_multiple": 3.0, "trailing_stop": True},
                {"tier": "TP4", "r_multiple": "structure", "position_close": "remaining"},
            ],
            parameters={
                "ob_rank_range": [1, 4],
                "breaker_block_alternate": True,
                "mss_dual_path": True,
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-06",
            name="Sell-Side Redistribution",
            category="ict",
            tier="swing",
            sector="forex",
            department="smc_ict",
            description="Bearish swing strategy for sell-side redistribution patterns. Targets 75-100 pips.",
            target_pips="75-100",
            v2_enabled=True,
            ob_quality_filter="1-4",
            kill_zone_required=True,
            tp_tiers=[
                {"tier": "TP1", "r_multiple": 1.0, "position_close": 0.25},
                {"tier": "TP2", "r_multiple": 1.5, "position_close": 0.25},
                {"tier": "TP3", "r_multiple": 3.0, "trailing_stop": True},
                {"tier": "TP4", "r_multiple": "structure", "position_close": "remaining"},
            ],
            parameters={
                "ob_rank_range": [1, 4],
                "breaker_block_entry": True,
                "crash_vs_controlled": True,
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-07",
            name="HTF Structure Break",
            category="ict",
            tier="position",
            sector="forex",
            department="smc_ict",
            description="Position strategy using Higher Timeframe structure breaks. Targets 200-300 pips.",
            target_pips="200-300",
            v2_enabled=True,
            ob_quality_filter="1-4",
            kill_zone_required=True,
            tp_tiers=[
                {"tier": "TP1", "r_multiple": 1.0, "position_close": 0.25},
                {"tier": "TP2", "r_multiple": 1.8, "position_close": 0.25},
                {"tier": "TP3", "r_multiple": 2.5, "position_close": 0.25},
                {"tier": "TP4", "r_multiple": "weekly", "position_close": "remaining"},
            ],
            parameters={
                "ob_rank_range": [1, 4],
                "breaker_block_alternate": True,
                "weekly_close_management": True,
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-08",
            name="Discount-Premium Position",
            category="ict",
            tier="position",
            sector="forex",
            department="smc_ict",
            description="Position strategy trading from discount (bullish) or premium (bearish) zones. Targets 300-500 pips.",
            target_pips="300-500",
            v2_enabled=True,
            ote_level="70.5%",
            kill_zone_required=True,
            tp_tiers=[
                {"tier": "TP1", "r_multiple": 1.0, "position_close": 0.25},
                {"tier": "TP2", "r_multiple": 2.0, "position_close": 0.25},
                {"tier": "TP3", "r_multiple": 3.0, "position_close": 0.25},
                {"tier": "TP4", "r_multiple": "weekly", "position_close": "remaining"},
            ],
            parameters={
                "ote_primary": 0.705,
                "breaker_block_entry": True,
                "ipa_range_weeks": 20,
                "risk_percent": 2.5,
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="ICT-09",
            name="Silver Bullet Time-Window",
            category="ict",
            tier="scalp",
            sector="forex",
            department="smc_ict",
            description="Scalp/short hybrid using specific time windows. Targets 15-30 pips.",
            target_pips="15-30",
            v2_enabled=True,
            kill_zone_required=True,
            parameters={
                "time_windows": [
                    {"window": "3-4AM NY", "start": "03:00", "end": "04:00"},
                    {"window": "10-11AM NY", "start": "10:00", "end": "11:00"},
                    {"window": "2-3PM NY", "start": "14:00", "end": "15:00"},
                ],
                "minimum_movement_framework": True,
                "window_failure_rule": True,
            }
        ))
        
        # R2-007: Market Structure Shift (MSS)
        self._register(StrategyDefinition(
            strategy_id="R2-007",
            name="Market Structure Shift (MSS)",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Structural signal - distinct from CHoCH, does not require prior BOS. 75% position size.",
            v2_enabled=True,
            parameters={
                "mss_definition": "independent_signal",
                "no_prior_bos_required": True,
                "position_size": 0.75,
            }
        ))
        
        # R2-009: Breaker Block Trading
        self._register(StrategyDefinition(
            strategy_id="R2-009",
            name="Breaker Block Trading",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Structural reversal strategy using failed order blocks that flip. Alternate entry for ICT-05 to 08.",
            v2_enabled=True,
            parameters={
                "bullish_entry": "breaker_top + 5 pips",
                "bullish_stop": "breaker_low - 10 pips",
                "bearish_entry": "breaker_bottom - 5 pips",
                "bearish_stop": "breaker_high + 10 pips",
            }
        ))
        
        # R2-010: Liquidity Grab / Judas Swing
        self._register(StrategyDefinition(
            strategy_id="R2-010",
            name="Liquidity Grab / Judas Swing",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Manipulation play combining stop hunt sweep with immediate reversal entry. Target next liquidity pool.",
            v2_enabled=True,
            parameters={
                "pattern": "liquidity_sweep_then_reversal",
                "entry_timing": "immediate_after_sweep",
                "target": "next_liquidity_pool",
            }
        ))
        
        # R2-011: Optimal Trade Entry (OTE)
        self._register(StrategyDefinition(
            strategy_id="R2-011",
            name="Optimal Trade Entry (OTE)",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Precision entry levels using Fibonacci. 70.5% primary, 61.8% secondary, 78.6% tertiary. Always within kill zone.",
            v2_enabled=True,
            kill_zone_required=True,
            parameters={
                "ote_primary": 0.705,
                "ote_secondary": 0.618,
                "ote_tertiary": 0.786,
                "always_in_kill_zone": True,
            }
        ))
        
        # R2-012: Power of Three (AMD)
        self._register(StrategyDefinition(
            strategy_id="R2-012",
            name="Power of Three (AMD)",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Cycle phase mapping - Accumulation, Manipulation, Distribution. Combined with kill zones.",
            v2_enabled=True,
            parameters={
                "phases": ["accumulation", "manipulation", "distribution"],
                "combined_with_kill_zones": True,
            }
        ))
        
        # R2-013: Kill Zone Timing
        self._register(StrategyDefinition(
            strategy_id="R2-013",
            name="Kill Zone Timing",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Session filter using full 5-window kill zone schedule. Gating for all ICT entries.",
            v2_enabled=True,
            kill_zone_required=True,
            parameters={
                "kill_zones": [
                    {"name": "Asian", "est": "8PM-10PM", "market": "Tokyo"},
                    {"name": "London", "est": "2AM-5AM", "market": "London"},
                    {"name": "London Open", "est": "5AM-7AM", "market": "Overlap"},
                    {"name": "NY", "est": "7AM-9AM", "market": "New York"},
                    {"name": "London Close", "est": "10AM-12PM", "market": "London"},
                ],
                "gating_for_all_ict": True,
            }
        ))
        
        # R2-028: BTMM Three-Day Cycle
        self._register(StrategyDefinition(
            strategy_id="R2-028",
            name="BTMM Three-Day Cycle",
            category="ict",
            tier="structural",
            sector="forex",
            department="smc_ict",
            description="Market maker cycle - MM driven, Retail driven, MM return. Uses EMAs 5/13/50/200, TDI, ADR, pivot points.",
            v2_enabled=True,
            parameters={
                "cycle_phases": ["mm_driven", "retail_driven", "mm_return"],
                "indicators": ["ema_5", "ema_13", "ema_50", "ema_200", "tdi", "adr", "pivot"],
            }
        ))
        
        # NEW-A: MACD Divergence + SMC
        self._register(StrategyDefinition(
            strategy_id="NEW-A",
            name="MACD Divergence + SMC",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Confluence signal combining MACD divergence with OB rank 1-3 and structure confirmation. Bridges Technical and SMC departments.",
            v2_enabled=True,
            parameters={
                "macd_divergence_required": True,
                "ob_rank_range": [1, 3],
                "structure_confirmation": True,
                "bridges_departments": ["technical", "smc_ict"],
            }
        ))
        
        # NEW-B: Fibonacci Sweep
        self._register(StrategyDefinition(
            strategy_id="NEW-B",
            name="Fibonacci Sweep",
            category="ict",
            tier="structural",
            sector="all",
            department="smc_ict",
            description="Precision reversal using 61.8% Fib + candlestick reversal + OB confirmation + 70.5% OTE entry.",
            v2_enabled=True,
            ote_level="70.5%",
            parameters={
                "fib_level": 0.618,
                "candlestick_reversal": True,
                "ob_confirmation": True,
                "ote_entry": 0.705,
            }
        ))
        
        # =========================================================================
        # BLOCK 2 — Technical Analysis (10 strategies)
        # =========================================================================
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_003",
            name="Technical Divergence Trading",
            category="technical",
            tier="short-term",
            sector="all",
            department="technical",
            description="Trading based on RSI/MACD price divergence from indicator divergence.",
            parameters={"indicators": ["rsi", "macd"], "timeframes": ["h1", "h4", "d1"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_004",
            name="Moving Average Crossover",
            category="technical",
            tier="short-term",
            sector="all",
            department="technical",
            description="EMA crossover strategy for trend direction and entry signals.",
            parameters={"emas": [5, 13, 50, 200], "timeframes": ["h1", "h4", "d1"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_006",
            name="MACD Trading",
            category="technical",
            tier="short-term",
            sector="all",
            department="technical",
            description="MACD-based trading using histogram crossovers and zero-line breaks.",
            parameters={"macd_fast": 12, "macd_slow": 26, "macd_signal": 9}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_007",
            name="Bollinger Bands Trading",
            category="technical",
            tier="short-term",
            sector="all",
            department="technical",
            description="Mean reversion and breakout trading using Bollinger Bands.",
            parameters={"period": 20, "std_dev": 2, "timeframes": ["m15", "h1", "h4", "d1"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_010",
            name="Multiple Time Frame Analysis",
            category="technical",
            tier="swing",
            sector="all",
            department="technical",
            description="Multi-TF analysis for trend confirmation and entry timing.",
            parameters={"htf": ["d1", "w1"], "itf": ["h4", "h1"], "ltf": ["m15", "m30"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_011",
            name="Double Bollinger Bands (Lien)",
            category="technical",
            tier="short-term",
            sector="forex,commodities",
            department="technical",
            description="Double Bollinger Bands strategy for trend and range identification.",
            parameters={"bb1_std": 1, "bb2_std": 2, "period": 20}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_015",
            name="20-Day Breakout Trade",
            category="technical",
            tier="swing",
            sector="all",
            department="technical",
            description="Breakout trading using 20-day high/low closes.",
            parameters={"lookback_days": 20, "timeframe": "d1"}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_017",
            name="Perfect Order Strategy",
            category="technical",
            tier="swing",
            sector="all",
            department="technical",
            description="EMA Perfect Order - 7/21/50 EMA alignment for trend confirmation.",
            parameters={"emas": [7, 21, 50], "timeframes": ["h4", "d1"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R1-013",
            name="MTF Momentum (Miner)",
            category="technical",
            tier="swing",
            sector="all",
            department="technical",
            description="Multi-timeframe momentum strategy from Trader's Miner.",
            parameters={"mtf_alignment": True, "timeframes": ["d1", "h4", "h1"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R2-019",
            name="Double MA Crossover",
            category="technical",
            tier="short-term",
            sector="all",
            department="technical",
            description="Dual moving average crossover for trend entry signals.",
            parameters={"fast_ma": 50, "slow_ma": 200, "timeframes": ["h1", "h4", "d1"]}
        ))
        
        # =========================================================================
        # BLOCK 3 — Fundamental & Intermarket (7 strategies)
        # =========================================================================
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_018",
            name="Pairing Strong vs Weak Currency",
            category="fundamental",
            tier="swing",
            sector="forex",
            department="fundamental",
            description="Currency strength matrix strategy - pair strongest against weakest.",
            parameters={"currency_strength_matrix": True, "rebalance": "daily"}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_019",
            name="Carry Trade",
            category="fundamental",
            tier="position",
            sector="forex",
            department="fundamental",
            description="Carry trade using interest rate differentials.",
            parameters={"min_rate_diff": 2.0, "min_interest": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_020",
            name="Macro Event-Driven Trade",
            category="fundamental",
            tier="short-term",
            sector="forex,commodities,indices",
            department="fundamental",
            description="Trade around high-impact macro events (NFP, CB meetings, GDP).",
            parameters={"event_calendar": True, "high_impact_only": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_021",
            name="Commodity as Leading Indicator",
            category="intermarket",
            tier="swing",
            sector="forex,commodities",
            department="intermarket",
            description="Use commodity prices as leading indicators for currency pairs.",
            parameters={"correlations": ["gold/aud", "oil/cad", "copper/aud"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_022",
            name="Bond Spreads as Leading Indicator",
            category="intermarket",
            tier="swing",
            sector="forex,indices",
            department="intermarket",
            description="Use bond yield spreads as leading indicators for equities and FX.",
            parameters={"bond_spreads": True, "yield_curve": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_025",
            name="Central Bank Intervention",
            category="fundamental",
            tier="short-term",
            sector="forex",
            department="fundamental",
            description="Trade central bank intervention signals and regime changes.",
            parameters={"cb_statements": True, "rate_decisions": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="STRAT_026",
            name="Intermarket Analysis (Murphy)",
            category="intermarket",
            tier="swing",
            sector="all",
            department="intermarket",
            description="Cross-asset regime analysis following Murphy's intermarket principles.",
            parameters={"asset_classes": ["bonds", "commodities", "stocks", "fx"]}
        ))
        
        # =========================================================================
        # BLOCK 4 — Sentiment & Volatility (4 strategies)
        # =========================================================================
        
        self._register(StrategyDefinition(
            strategy_id="R2-001",
            name="VIX-EMA Crossover",
            category="sentiment",
            tier="short-term",
            sector="indices,stocks",
            department="sentiment",
            description="VIX directional strategy using 20-EMA on VIX. Sell when EMA crosses above VIX, buy when crosses below.",
            parameters={"vix_ema_period": 20, "signal": "ema_crossover"}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R2-002",
            name="VIX-S&P 500 Correlation",
            category="sentiment",
            tier="short-term",
            sector="indices,stocks",
            department="sentiment",
            description="Inverse correlation strategy - VIX rising = short S&P, VIX falling = long S&P.",
            parameters={"correlation": "inverse", "instruments": ["vix", "sp500"]}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R2-003",
            name="VIX COT Report Sentiment",
            category="sentiment",
            tier="short-term",
            sector="indices,stocks",
            department="sentiment",
            description="CFTC VIX futures positioning extremes as contrarian signals. Combined with R2-001 for highest confidence.",
            parameters={"cot_percentile_range": [5, 10, 90, 95], "combine_with_r2_001": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="COT-001",
            name="COT Report Trading (Enhanced)",
            category="sentiment",
            tier="swing",
            sector="forex,commodities",
            department="sentiment",
            description="Smart money positioning using COT commercial extremes (5-10yr percentile). Fade large specs at extremes with price action confirmation.",
            parameters={"commercial_percentile_range": [5, 10], "large_spec_percentile_range": [90, 95], "price_action_confirmation": True}
        ))
        
        # =========================================================================
        # BLOCK 5 — Range, Breakout & Volume (3 strategies)
        # =========================================================================
        
        self._register(StrategyDefinition(
            strategy_id="R2-016",
            name="Range Trading",
            category="quantitative",
            tier="short-term",
            sector="all",
            department="quantitative",
            description="Mean reversion using horizontal range boundaries. Buy support / sell resistance. Complements Bollinger squeeze.",
            parameters={"range_detection": "horizontal", "entry_on_support_resistance": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R2-017",
            name="Breakout Trading",
            category="quantitative",
            tier="swing",
            sector="all",
            department="quantitative",
            description="Momentum breakout - close beyond established range with volume confirmation. Measured move target. Complements STRAT_015.",
            parameters={"volume_confirmation": True, "measured_move": True}
        ))
        
        self._register(StrategyDefinition(
            strategy_id="R2-018",
            name="Volume Trading",
            category="quantitative",
            tier="short-term",
            sector="stocks,crypto",
            department="quantitative",
            description="Volume surge confirms price moves. OBV divergence flags reversals. Volume dry-up = exhaustion.",
            parameters={"volume_surge_threshold": 1.5, "obv_divergence": True, "volume_dryup_signal": True}
        ))
        
        # =========================================================================
        # BLOCK 6 — Execution Tactics (7 tactics)
        # =========================================================================
        
        self._register(StrategyDefinition(
            strategy_id="B-01",
            name="VWAP Execution",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Slice large orders by historical intraday volume profile. Reduces market impact on liquid pairs.",
            parameters={
                "execution_method": "vwap",
                "slice_strategy": "volume_profile",
                "used_by": ["forex_trader", "commodities_trader"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-02",
            name="TWAP Execution",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Uniform time-slice execution where VWAP curve unavailable. Preferred for Bybit execution.",
            parameters={
                "execution_method": "twap",
                "slice_strategy": "uniform_time",
                "used_by": ["crypto_trader", "stocks_trader"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-03",
            name="POV / Participation Rate",
            category="execution",
            tier="execution",
            sector="forex",
            department="quantitative",
            is_tactic=True,
            description="Execute as 10-25% of live volume on the most liquid FX pairs.",
            parameters={
                "execution_method": "pov",
                "participation_rate": "10-25%",
                "used_by": ["forex_trader"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-04",
            name="Trailing One-Bar High/Low Entry",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Precise entry trigger - 1-bar break of swing extreme. Used with CHoCH and BOS setups.",
            parameters={
                "entry_trigger": "one_bar_break",
                "swing_extreme": "high_or_low",
                "used_by": ["all_traders"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-05",
            name="Swing Breakout Entry Trigger",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Structural entry on swing breakout confirmation. Stop at opposite swing extreme.",
            parameters={
                "entry_trigger": "swing_breakout",
                "stop_placement": "opposite_swing_extreme",
                "used_by": ["all_traders"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-06",
            name="Two-Unit Trade Management",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Unit 1 = quick TP at 38.2-50% retracement. Unit 2 = trail stop for full trend capture.",
            parameters={
                "unit_1": {"tp_percent": "38.2-50%", "position_size": 0.5},
                "unit_2": {"trailing_stop": True, "position_size": 0.5},
                "used_by": ["risk_team", "all_traders"],
            }
        ))
        
        self._register(StrategyDefinition(
            strategy_id="B-07",
            name="ADR-Based Position Sizing",
            category="execution",
            tier="execution",
            sector="all",
            department="quantitative",
            is_tactic=True,
            description="Average Daily Range used to set stop distance and position size. Sourced from BTMM methodology.",
            parameters={
                "position_sizing": "adr_based",
                "stop_distance": "atr_14",
                "used_by": ["risk_team"],
            }
        ))
        
        logger.info(f"Strategy registry initialized with {len(self._strategies)} strategies and tactics")
    
    def _register(self, strategy: StrategyDefinition):
        """Register a strategy in the registry."""
        self._strategies[strategy.strategy_id] = strategy
        
        # Index by category
        if strategy.category not in self._by_category:
            self._by_category[strategy.category] = []
        self._by_category[strategy.category].append(strategy.strategy_id)
        
        # Index by tier
        if strategy.tier:
            if strategy.tier not in self._by_tier:
                self._by_tier[strategy.tier] = []
            self._by_tier[strategy.tier].append(strategy.strategy_id)
        
        # Index by sector
        if strategy.sector:
            sectors = strategy.sector.split(",")
            for sector in sectors:
                sector = sector.strip()
                if sector not in self._by_sector:
                    self._by_sector[sector] = []
                self._by_sector[sector].append(strategy.strategy_id)
        
        # Index by department
        if strategy.department:
            if strategy.department not in self._by_department:
                self._by_department[strategy.department] = []
            self._by_department[strategy.department].append(strategy.strategy_id)
        
        # Track tactics
        if strategy.is_tactic:
            self._tactics.append(strategy.strategy_id)
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyDefinition]:
        """Get a strategy by its ID."""
        return self._strategies.get(strategy_id)
    
    def get_by_category(self, category: str) -> List[StrategyDefinition]:
        """Get all strategies in a category."""
        strategy_ids = self._by_category.get(category, [])
        return [self._strategies[sid] for sid in strategy_ids]
    
    def get_by_tier(self, tier: str) -> List[StrategyDefinition]:
        """Get all strategies of a specific tier."""
        strategy_ids = self._by_tier.get(tier, [])
        return [self._strategies[sid] for sid in strategy_ids]
    
    def get_by_sector(self, sector: str) -> List[StrategyDefinition]:
        """Get all strategies applicable to a sector."""
        strategy_ids = self._by_sector.get(sector, [])
        return [self._strategies[sid] for sid in strategy_ids]
    
    def get_by_department(self, department: str) -> List[StrategyDefinition]:
        """Get all strategies owned by a department."""
        strategy_ids = self._by_department.get(department, [])
        return [self._strategies[sid] for sid in strategy_ids]
    
    def get_tactics(self) -> List[StrategyDefinition]:
        """Get all execution tactics."""
        return [self._strategies[tid] for tid in self._tactics]
    
    def get_all_strategies(self) -> List[StrategyDefinition]:
        """Get all strategies (excluding tactics)."""
        return [s for s in self._strategies.values() if not s.is_tactic]
    
    def get_all_tactics(self) -> List[StrategyDefinition]:
        """Get all execution tactics."""
        return [self._strategies[tid] for tid in self._tactics]
    
    def search(self, keyword: str) -> List[StrategyDefinition]:
        """Search strategies by keyword in name or description."""
        keyword_lower = keyword.lower()
        results = []
        for strategy in self._strategies.values():
            if keyword_lower in strategy.name.lower() or keyword_lower in strategy.description.lower():
                results.append(strategy)
        return results
    
    def get_v2_strategies(self) -> List[StrategyDefinition]:
        """Get all strategies with v2 enhancements enabled."""
        return [s for s in self._strategies.values() if s.v2_enabled]
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        strategies = [s for s in self._strategies.values() if not s.is_tactic]
        tactics = [s for s in self._strategies.values() if s.is_tactic]
        
        return {
            "total_strategies": len(strategies),
            "total_tactics": len(tactics),
            "total": len(self._strategies),
            "by_category": {cat: len(ids) for cat, ids in self._by_category.items()},
            "by_tier": {tier: len(ids) for tier, ids in self._by_tier.items()},
            "by_sector": {sector: len(ids) for sector, ids in self._by_sector.items()},
            "by_department": {dept: len(ids) for dept, ids in self._by_department.items()},
            "v2_enabled": len([s for s in strategies if s.v2_enabled]),
        }


# Global registry instance
strategy_registry = StrategyRegistry()

__all__ = [
    "StrategyDefinition",
    "StrategyRegistry",
    "strategy_registry",
]