# AgentFinance v3 — Implementation Guide
## Upgrading AgentFinance v2 → Full Trading Automation Stack

> **Scope:** Adds 10 new agents (28 total), integrates SMC strategy engine, 80+ technical indicators, fundamental economic analysis, multi-asset class coverage, strategy backtesting, and live cTrader execution — transforming AgentFinance from an investment intelligence platform into a complete autonomous trading system.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [New Agents — 10 Additions](#2-new-agents--10-additions)
3. [Removed / Consolidated from v2](#3-removed--consolidated-from-v2)
4. [SMC Strategy Engine](#4-smc-strategy-engine)
5. [Technical Indicators — cinar/indicator](#5-technical-indicators--cinarindicator)
6. [Apex Platform Services Integration](#6-apex-platform-services-integration)
7. [New Skills Library — Trading Skills](#7-new-skills-library--trading-skills)
8. [cTrader CLI — Live Trading Execution](#8-ctrader-cli--live-trading-execution)
9. [Strategy Backtesting Agent](#9-strategy-backtesting-agent)
10. [n8n Workflow Blueprints — Trading Automation](#10-n8n-workflow-blueprints--trading-automation)
11. [Data Sources & API Configuration](#11-data-sources--api-configuration)
12. [Installation on Kali Linux](#12-installation-on-kali-linux)
13. [Risk Management & Safety Gates](#13-risk-management--safety-gates)
14. [Performance Optimisations](#14-performance-optimisations)
15. [Enhancement Roadmap](#15-enhancement-roadmap)

---

## 1. Architecture Overview

### v2 → v3 Stack Changes

```
AgentFinance v2 (Intelligence Only)          AgentFinance v3 (Intelligence + Trading)
─────────────────────────────────────        ────────────────────────────────────────
Financial MCP Server (data)              →   Financial MCP Server + Market Data APIs
OpenClaw / OpenCode (analysis)           →   OpenClaw + SMC Engine + Indicator Engine
18 agents / 4 departments               →   28 agents / 6 departments
n8n (intelligence distribution)          →   n8n (intelligence + trade execution)
No live trading                          →   cTrader CLI (live execution)
No backtesting                           →   Backtest Engine (historical + walk-forward)
Equities + crypto + private markets      →   All asset classes: FX, Commodities, Indices
```

### New Department Structure

| # | Department | Agents | Focus |
|---|-----------|--------|-------|
| 1 | Public Markets Intelligence | 01–06 | SEC, earnings, stocks, financials, holdings, crypto |
| 2 | Private Markets Intelligence | 07–12 | Companies, funding, funds, deals, investors, debt |
| 3 | Research Intelligence | 13–14 | Web scraping, deep research synthesis |
| **4** | **Asset Class Intelligence** | **19–21** | **Forex, Commodities, Indices** |
| **5** | **Trading Strategy Engine** | **22–26** | **SMC, Technical, Fundamental, Sentiment, News** |
| **6** | **Trading Automation** | **27–28** | **Backtesting, Live Execution** |
| 7 | Investment Operations | 15–18 | Portfolio, reports, compliance, supervisor |

---

## 2. New Agents — 10 Additions

### Department 4: Asset Class Intelligence

---

#### Agent 19 — Forex Intelligence Agent

**Mission:** Provide institutional-grade forex market analysis covering all major, minor, and exotic currency pairs — combining SMC structure analysis, COT positioning, central bank policy divergence, and session-aware kill zone timing to generate high-probability trade setups.

**Data Sources:**
- OANDA API (real-time FX rates, order book)
- CFTC COT reports (institutional positioning)
- Central bank websites (Fed, ECB, BOE, BOJ rate decisions)
- DailyFX economic calendar (news events, impact ratings)

**Capabilities:**
- 28 major/minor pairs + 20 exotic pairs continuously monitored
- Kill zone alerts: Asian (21:00–04:00), London (03:00–05:00), New York (08:00–12:00), London Close (10:30–11:00) EST
- Central bank divergence scoring: rate differential × policy direction × risk appetite
- SMC analysis per pair: order blocks, FVGs, liquidity sweeps, BOS/CHoCH on M15/H1/H4/D1
- COT analysis: commercial vs large speculator positioning, extreme readings
- Correlation matrix: identify correlated pair opportunities and hedges

**Skills:**
```
forex-smc-analysis          forex-cot-report           forex-kill-zones
forex-central-bank-policy   forex-correlation-matrix   forex-session-pairs
forex-liquidity-map         forex-retail-sentiment      forex-carry-trade
```

**Commands:**
```
/fx:setup <PAIR>            /fx:kill-zones             /fx:cot <PAIR>
/fx:pairs <SESSION>         /fx:divergence             /fx:scan
/fx:structure <PAIR> <TF>   /fx:report
```

---

#### Agent 20 — Commodities Intelligence Agent

**Mission:** Analyse all commodity markets — precious metals, energy, agricultural, and soft commodities — using supply/demand fundamentals, seasonality, COT positioning, geopolitical risk premiums, and SMC structure to generate directional trade setups.

**Data Sources:**
- TradingEconomics API (supply, demand, inventory data)
- EIA weekly petroleum status report (crude/natural gas)
- USDA WASDE reports (agricultural supply/demand)
- World Gold Council (gold demand data)
- CFTC COT reports (futures positioning)

**Capabilities:**
- Precious metals: XAUUSD, XAGUSD, Platinum, Palladium — inflation hedge analysis
- Energy: WTI, Brent, Natural Gas, Heating Oil — EIA inventory + OPEC production
- Agricultural: Corn, Wheat, Soybeans, Coffee, Sugar, Cotton — WASDE + weather
- Seasonality patterns: 10-year average seasonal performance per commodity
- Geopolitical risk premium calculation: conflict zones, sanctions, supply disruption
- SMC structure: order blocks and FVGs on commodities futures charts

**Skills:**
```
commodities-smc             commodities-cot             commodities-seasonality
commodities-fundamentals    commodities-eia-report       commodities-wasde
commodities-geopolitical    commodities-inventory        commodities-supply-demand
```

**Commands:**
```
/commod:gold                /commod:oil                 /commod:agri <SYMBOL>
/commod:seasonality <SYM>   /commod:inventory           /commod:geopolitical
/commod:setup <SYMBOL>      /commod:report
```

---

#### Agent 21 — Indices Intelligence Agent

**Mission:** Monitor and analyse all major global equity indices — US (SPX, NDX, DJI, RUT), European (DAX, FTSE, CAC, SMI), Asian (Nikkei, Hang Seng, ASX) — using SMC, market internals, breadth analysis, and macro regime to generate directional bias and index trade setups.

**Data Sources:**
- Polygon.io (index prices, constituents)
- FRED API (VIX, SKEW, market breadth)
- NYSE/NASDAQ advance-decline data
- Put/call ratios (CBOE)
- S&P 500 sector performance (12 GICS sectors)

**Capabilities:**
- Market breadth analysis: A/D line, new highs/lows, % above 50/200MA
- VIX regime classification: low (<15), normal (15-25), elevated (25-35), crisis (>35)
- SKEW Index: tail risk assessment, options market positioning
- Sector rotation model: identify sector leadership and laggards
- Inter-market analysis: stocks vs bonds vs dollar vs commodities
- SMC on index charts: identify distribution/accumulation, fair value gaps, order blocks
- Risk-on / risk-off regime detection for all asset class positioning

**Skills:**
```
indices-smc                 indices-breadth             indices-vix-regime
indices-sector-rotation     indices-internals            indices-intermarket
indices-skew                indices-advance-decline      indices-macro-regime
```

**Commands:**
```
/index:spx                  /index:breadth              /index:vix
/index:sectors              /index:regime               /index:global
/index:setup <SYMBOL>       /index:report
```

---

### Department 5: Trading Strategy Engine

---

#### Agent 22 — SMC Strategy Agent

**Mission:** Apply the complete ICT Smart Money Concepts methodology (via `smartmoneyconcepts` Python package) across all monitored instruments — detecting institutional footprints, generating precision trade setups aligned with smart money, and providing confluenced entry/exit levels with kill zone timing.

**Source:** `pip install smartmoneyconcepts` — github.com/joshyattridge/smart-money-concepts

**SMC Methodology Implemented:**

| Concept | Description | Timeframes |
|---------|-------------|------------|
| **Order Blocks** | Last bearish/bullish candle before significant move — institutional entry zones | M15, H1, H4, D1 |
| **Fair Value Gaps** | 3-candle imbalance — price magnetic zones, partial/full fill tracking | All TFs |
| **Break of Structure** | Higher high/lower low — confirms directional bias change | H1, H4 |
| **Change of Character** | First opposing BOS — early trend reversal signal | M15, H1 |
| **Liquidity Sweeps** | Equal highs/lows, stop hunts, buy/sell side liquidity | All TFs |
| **Premium/Discount** | Fibonacci levels — OTE zone for entry (0.62–0.79 retracement) | H1, H4 |
| **Kill Zones** | ICT session timing for entry precision | Real-time |
| **Silver Bullet** | 3-candle setup during London/NY open using FVG | 10:00–11:00, 14:00–15:00 EST |
| **Judas Swing** | False breakout before true directional move | Market open |
| **Power of 3** | Accumulation → Manipulation → Distribution model | Daily |
| **ICT Bias** | Higher timeframe direction determines lower TF entries | HTF → LTF |
| **Optimal Trade Entry** | 0.62–0.705 Fibonacci retracement within order block | H1 |

**Key Functions (Python `smartmoneyconcepts`):**
```python
from smartmoneyconcepts import smc

# Core SMC analysis
ob = smc.ob(ohlc_df, swing_highs_lows)           # Order blocks
fvg = smc.fvg(ohlc_df, join_consecutive=True)    # Fair value gaps
bos = smc.bos_choch(ohlc_df, swing_highs_lows)   # BOS + CHoCH
liquidity = smc.liquidity(ohlc_df, swing_highs_lows)  # Liquidity zones
swings = smc.swing_highs_lows(ohlc_df, swing_length=50)
premium_discount = smc.premium_discount_levels(ohlc_df, swing_highs_lows)
previous_highs_lows = smc.previous_high_low(ohlc_df)
sessions = smc.sessions(ohlc_df, session="London", start="08:00", end="17:00")
```

**Multi-Timeframe SMC Confluence Scoring:**
```
Score = Σ (HTF_bias × 0.4) + (OB_confluence × 0.25) + (FVG_present × 0.15)
          + (BOS_confirmation × 0.1) + (kill_zone_active × 0.1)
```

**Setup Generation Rules:**
- Score ≥ 0.75: High-probability setup — flag for execution
- Score 0.50–0.74: Monitor setup — alert trader
- Score < 0.50: No trade — insufficient confluence

**Commands:**
```
/smc:scan <SYMBOL>          /smc:ob <SYMBOL> <TF>      /smc:fvg <SYMBOL> <TF>
/smc:bos <SYMBOL>           /smc:liquidity <SYMBOL>    /smc:premium <SYMBOL>
/smc:setup <SYMBOL>         /smc:silver-bullet         /smc:judas-swing
/smc:power-of-3 <SYMBOL>    /smc:kill-zones            /smc:bias <SYMBOL>
/smc:confluence <SYMBOL>    /smc:report
```

---

#### Agent 23 — Technical Analysis Agent

**Mission:** Apply a comprehensive suite of 80+ technical indicators (from `cinar/indicator` Go library, ported to Python via OpenCode) across all monitored instruments — generating trend, momentum, volatility, and volume signals that provide quantitative confirmation for SMC setups.

**Source:** github.com/cinar/indicator — Go library with Python wrapper

**Indicator Categories Implemented:**

**Trend Indicators:**
```
EMA(9,21,50,100,200)    SMA(20,50,200)         WMA(10,20)
DEMA                     TEMA                    HMA (Hull)
Ichimoku (Tenkan/Kijun/Senkou/Chikou)           ADX(14)
Parabolic SAR            SuperTrend(10,3)        Aroon(25)
```

**Momentum Indicators:**
```
RSI(14)                  Stochastic(14,3,3)      MACD(12,26,9)
ROC(10)                  Williams %R(14)         CCI(20)
Ultimate Oscillator      Awesome Oscillator      MFI(14)
Elder Force Index        TRIX(15)                KST
```

**Volatility Indicators:**
```
Bollinger Bands(20,2)    ATR(14)                 Keltner Channels(20,2)
Donchian Channels(20)    Standard Deviation       Historical Volatility
VIX correlation          Chaikin Volatility       Ulcer Index
```

**Volume Indicators:**
```
OBV                      VWAP                    Chaikin Money Flow
Volume Profile           Accumulation/Distribution    Force Index
VROC                     Volume-Weighted RSI     Ease of Movement
```

**Custom Strategies (from cinar/indicator `strategy/` directory):**
```
GoldenCross / DeathCross              RSI + MACD Confluence
Bollinger Band Squeeze + Breakout     Ichimoku Full System
Three White Soldiers / Three Crows    Marubozu Detection
Supertrend + RSI Filter               Buy/Sell Hold Strategy
```

**Multi-Indicator Confluence Score:**
```
Trend score    = (EMA_alignment × 0.3) + (ADX × 0.2) + (Ichimoku × 0.5)
Momentum score = (RSI × 0.35) + (MACD × 0.35) + (Stochastic × 0.3)
Volume score   = (OBV_trend × 0.4) + (VWAP × 0.35) + (CMF × 0.25)
Final score    = (Trend × 0.45) + (Momentum × 0.35) + (Volume × 0.2)
```

**Commands:**
```
/tech:scan <SYMBOL>         /tech:rsi <SYMBOL>          /tech:macd <SYMBOL>
/tech:bb <SYMBOL>           /tech:ichimoku <SYMBOL>     /tech:adx <SYMBOL>
/tech:momentum <SYMBOL>     /tech:volume <SYMBOL>       /tech:divergence <SYMBOL>
/tech:confluence <SYMBOL>   /tech:report <SYMBOL>       /tech:strategy <NAME>
```

---

#### Agent 24 — Fundamental Analysis Agent

**Mission:** Monitor and interpret macroeconomic data releases that drive asset class direction — interest rate decisions, inflation (CPI/PCE), employment (NFP), GDP, PMI, retail sales, and central bank communications — generating a macro regime score that sets directional bias for all asset classes.

**Data Sources:**
- FRED API (Federal Reserve Economic Data — 800,000+ series)
- Investing.com economic calendar (scheduled releases + prior/forecast/actual)
- World Bank API (global GDP, inflation, current account data)
- BIS (Bank for International Settlements — central bank data)
- TradingEconomics API (190 countries, all indicators)

**Macro Regime Model:**

| Regime | Rates | Inflation | Growth | Asset Impact |
|--------|-------|-----------|--------|-------------|
| Goldilocks | Falling/Stable | Low/Falling | Strong | Equities ↑, Bonds ↑, USD neutral |
| Overheating | Rising | Rising | Strong | Commodities ↑, Short bonds, Value stocks |
| Stagflation | Rising | High | Weak | Gold ↑, Short equities, Long USD |
| Recession | Falling | Low | Weak | Bonds ↑, Gold ↑, Short risk assets |
| Reflation | Stable | Rising | Recovering | Cyclicals ↑, Commodities ↑ |

**Key Indicators Tracked:**

*United States:*
```
Fed Funds Rate target      Core CPI/PCE (MoM/YoY)    NFP + Unemployment rate
GDP (QoQ/YoY)              ISM Manufacturing/Services  Retail Sales
JOLTS Job Openings         Consumer Confidence         Housing Starts/Permits
Fed FOMC minutes + dots    Yield curve (2Y-10Y spread) TGA balance
```

*Global:*
```
ECB/BOE/BOJ/RBA/RBNZ rate decisions    G7 GDP comparison
Global PMI composite                    China NBS/Caixin PMI
Eurozone CPI + unemployment             UK CPI + employment
DXY (Dollar Index) regime               Global risk appetite index
```

**Economic Calendar Automation:**
```python
# Daily calendar check
scheduled_releases = calendar.get_today_high_impact()
for release in scheduled_releases:
    if release.actual != release.forecast:
        surprise_pct = (actual - forecast) / std_dev
        generate_macro_alert(release, surprise_pct)
        update_macro_regime_score()
        reprice_asset_class_bias()
```

**Commands:**
```
/macro:regime               /macro:calendar             /macro:rates
/macro:inflation            /macro:gdp                  /macro:nfp
/macro:cpi                  /macro:fed                  /macro:global
/macro:surprise <EVENT>     /macro:report               /macro:bias
```

---

#### Agent 25 — Sentiment Intelligence Agent

**Mission:** Aggregate sentiment signals from all available sources — COT institutional positioning, Fear & Greed Index, options market (put/call ratios), social media (Reddit/Twitter), retail broker positioning (SSI), and news sentiment NLP — into a composite sentiment score that identifies contrarian trade opportunities.

**Data Sources:**
- CFTC COT reports (futures positioning — released every Friday)
- CNN Fear & Greed Index API
- CBOE put/call ratio (daily)
- Retail trader SSI (IG, OANDA, Pepperstone positioning data)
- Reddit API (wallstreetbets, Forex, investing subreddits)
- Twitter/X API v2 (cashtag sentiment)
- News NLP sentiment (OpenClaw local model)

**Sentiment Weight Matrix (from Apex platform):**
```python
SENTIMENT_WEIGHTS = {
    "cot_commercial":   0.35,   # Highest weight — real institutional money
    "options_flow":     0.20,   # Derivatives positioning
    "news_nlp":         0.20,   # Quantitative news analysis
    "twitter":          0.15,   # Social momentum
    "retail_ssi":       0.07,   # Contrarian retail positioning
    "reddit":           0.03,   # Speculative retail sentiment
}
```

**Sentiment Signals Generated:**
- **COT Extreme**: Commercials > 80th percentile bullish/bearish → contrarian signal
- **Fear Extremes**: F&G < 20 (extreme fear = buy) or > 80 (extreme greed = sell)
- **Options Skew**: Put/Call > 1.3 (bearish) or < 0.7 (bullish)
- **SSI Divergence**: Retail > 70% long = institutions likely short
- **Social Momentum**: Rapid sentiment shift > 2 standard deviations

**Commands:**
```
/sentiment:cot <SYMBOL>     /sentiment:fear-greed       /sentiment:options <SYMBOL>
/sentiment:social <SYMBOL>  /sentiment:retail <SYMBOL>  /sentiment:composite <SYMBOL>
/sentiment:extremes         /sentiment:divergence       /sentiment:report
```

---

#### Agent 26 — News Intelligence Agent

**Mission:** Monitor all financial news sources for market-moving events, earnings surprises, geopolitical shocks, and regulatory changes — performing NLP sentiment analysis locally via OpenClaw, and correlating news events with price action to generate trade alerts and macro context updates.

**Data Sources:**
- NewsAPI (3,000+ sources, real-time)
- Reuters API / Bloomberg (via financial MCP server)
- Benzinga API (earnings, analyst changes, FDA approvals)
- Twitter/X financial accounts (real-time breaking news)
- Central bank speech monitoring (Fed, ECB, BOE websites)
- SEC 8-K filings (material event detection — via SEC agent)

**NLP Analysis (Local OpenClaw):**
```python
# Sentiment scoring on headlines
sentiment = pipeline("financial-sentiment", model="ProsusAI/finbert")
score = sentiment(headline)
# → {"positive": 0.72, "negative": 0.21, "neutral": 0.07}

# Entity extraction
entities = ner_pipeline(article)
# → {"companies": ["AAPL"], "events": ["earnings beat"], "impact": "positive"}
```

**Alert Categories:**
- 🔴 CRITICAL: Central bank rate surprises, systemic risk events, flash crashes
- 🟠 HIGH: Earnings beats/misses >10%, M&A announcements, major analyst calls
- 🟡 MEDIUM: Economic data surprises, sector-specific news, geopolitical tensions
- 🟢 LOW: Routine news, analyst initiations, minor corporate updates

**Commands:**
```
/news:scan                  /news:symbol <TICKER>       /news:macro
/news:sentiment <TOPIC>     /news:calendar              /news:alerts
/news:breaking              /news:geopolitical          /news:report
```

---

### Department 6: Trading Automation

---

#### Agent 27 — Strategy Backtesting Agent

**Mission:** Backtest any combination of SMC, technical, fundamental, and sentiment strategies on historical data across all asset classes — generating comprehensive performance metrics, Monte Carlo simulations, walk-forward analysis, and parameter optimisation reports to validate strategy edges before live deployment.

**Backtesting Engine:**

Based on Apex platform `smcBacktest.ts` + cinar/indicator `backtest/` framework, ported to Python with pandas/numpy:

```python
class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.smc = SMCEngine()          # joshyattridge/smart-money-concepts
        self.indicators = IndicatorEngine()  # cinar/indicator

    def run(self) -> BacktestResult:
        # 1. Load historical OHLCV
        # 2. Apply strategy signals
        # 3. Simulate entries/exits with commission + slippage
        # 4. Calculate performance metrics
        # 5. Generate equity curve
        # 6. Monte Carlo simulation
        # 7. Walk-forward validation
```

**Backtest Configuration:**
```python
@dataclass
class BacktestConfig:
    symbol: str
    asset_class: str              # "forex" | "equity" | "crypto" | "commodity" | "index"
    start_date: str
    end_date: str
    timeframe: str                # "M5" | "M15" | "H1" | "H4" | "D1"
    initial_balance: float        # Default 10,000
    risk_per_trade: float         # Default 1% per trade
    commission: float             # Default 0.0007 (7 pips for FX)
    slippage: float               # Default 0.0002 (2 pips)
    max_positions: int            # Default 3 concurrent
    strategy: str                 # "smc" | "technical" | "combined" | "custom"
    strategy_params: dict         # Strategy-specific parameters
    walk_forward: bool            # Enable walk-forward validation
    monte_carlo_runs: int         # Default 1000
```

**Performance Metrics Calculated:**
```python
# Core metrics
total_return: float               net_profit: float
win_rate: float                   profit_factor: float
avg_rr_ratio: float               max_drawdown: float
max_drawdown_duration: int        # Days
recovery_factor: float            calmar_ratio: float

# Risk-adjusted
sharpe_ratio: float               sortino_ratio: float
ulcer_index: float                var_95: float

# Trade breakdown
total_trades: int                 winning_trades: int
avg_win: float                    avg_loss: float
largest_win: float                largest_loss: float
avg_trade_duration: float         # Hours

# Monthly/annual breakdown
monthly_returns: Dict[str, float]
annual_returns: Dict[str, float]
equity_curve: List[float]
```

**Strategy Presets:**

| Preset | Entry Rule | Risk | Win Rate Target |
|--------|-----------|------|-----------------|
| Conservative SMC | HTF bias + H4 OB + Kill Zone | 0.5% | 65%+ |
| Balanced SMC+Tech | SMC confluence + RSI + MACD | 1.0% | 55%+ |
| Aggressive Breakout | BOS confirmation + volume | 1.5% | 45%+ |
| Scalp Silver Bullet | ICT Silver Bullet + FVG fill | 0.75% | 60%+ |
| Macro Momentum | Fundamental regime + trend | 1.0% | 50%+ |

**Walk-Forward Validation:**
```
In-sample: 70% of data (strategy optimisation)
Out-of-sample: 30% of data (strategy validation)
Rolling windows: 6-month in-sample / 2-month out-of-sample
```

**Commands:**
```
/backtest:run <STRATEGY> <SYMBOL>   /backtest:smc <SYMBOL>
/backtest:compare <S1> <S2>         /backtest:optimise <STRATEGY>
/backtest:montecarlo <STRATEGY>     /backtest:walkforward <STRATEGY>
/backtest:report <RUN-ID>           /backtest:export <RUN-ID>
```

---

#### Agent 28 — Live Trading Executor

**Mission:** Execute approved trade setups on live markets via cTrader CLI — managing order entry, stop loss, take profit, partial closes, trailing stops, and position monitoring. Acts as the autonomous execution layer that receives approved signals from all strategy agents and manages the full trade lifecycle with strict risk controls.

**Execution Platform: cTrader CLI**

```bash
# Install cTrader CLI
npm install -g @ctrader/cli    # or platform-specific package

# Configure broker connection
ctrader configure \
  --server live.ctrader.com \
  --account ACCOUNT_ID \
  --password PASS

# Authentication
ctrader auth --oauth2 --client-id CLIENT_ID --client-secret CLIENT_SECRET
```

**Order Execution Workflow:**

```
Signal Received → Risk Check → Size Calculation → Order Preview → APPROVE → Execute → Monitor
```

```bash
# Place market order with SL/TP
ctrader order create \
  --symbol "EURUSD" \
  --side buy \
  --type market \
  --volume 0.1 \
  --stop-loss 1.07234 \
  --take-profit 1.08456 \
  --label "SMC-OB-LONDON-2025-03-20"

# Manage open position
ctrader position modify \
  --id POSITION_ID \
  --stop-loss 1.07500 \      # Trail stop loss
  --take-profit-1 1.08000 \  # Partial TP
  --take-profit-2 1.08456

# Close position
ctrader position close --id POSITION_ID --volume 0.05  # Partial close
ctrader position close --id POSITION_ID                 # Full close

# Monitor portfolio
ctrader portfolio status
ctrader positions list
ctrader orders list
```

**Risk Management Pre-Execution Checks:**
```python
def pre_trade_risk_check(signal: TradeSignal) -> bool:
    checks = [
        max_daily_loss_not_exceeded(),      # Hard stop: 3% daily drawdown
        max_concurrent_positions_ok(),       # Max 5 open positions
        correlation_risk_acceptable(),       # No >80% correlated positions
        news_event_window_clear(),           # No trades 15min before high-impact news
        spread_within_threshold(),           # Spread < 2x average
        account_margin_adequate(),           # >200% margin level
        kill_zone_active_if_required(),      # SMC signals need kill zone
        signal_age_within_limit(),           # Signal < 4 hours old
    ]
    return all(checks)
```

**Position Sizing:**
```python
def calculate_position_size(
    account_balance: float,
    risk_pct: float,          # 1% default
    entry: float,
    stop_loss: float,
    instrument_type: str,
) -> float:
    risk_amount = account_balance * risk_pct
    pips_at_risk = abs(entry - stop_loss) / pip_size[instrument_type]
    pip_value = get_pip_value(instrument_type, account_currency)
    lot_size = risk_amount / (pips_at_risk * pip_value)
    return round(lot_size, 2)
```

**Execution Safety Gates:**

| Gate | Condition | Action |
|------|-----------|--------|
| HOLD | Signal confidence < 75% | Queue for manual review |
| ALERT | Daily P&L < -1.5% | Notify trader, no new trades |
| PAUSE | Daily P&L < -2.5% | Halt all automated execution |
| HALT | Daily P&L < -3.0% | Close all positions, shutdown |
| MANUAL | Spread > 3x average | Force manual execution review |
| BLOCK | Pending high-impact news | Block 15min before/after |

**Approval Workflow:**
```
Signal → Agent 27 (backtest validated?) → Risk check → Telegram APPROVE
→ cTrader CLI execute → Position monitor → n8n status webhook → Telegram P&L alert
```

**Commands:**
```
/trade:execute <SIGNAL-ID>    /trade:close <POSITION-ID>
/trade:modify <POSITION-ID>   /trade:positions
/trade:risk-check             /trade:daily-pnl
/trade:halt                   /trade:resume
/trade:journal <TRADE-ID>     /trade:report
```

---

## 3. Removed / Consolidated from v2

The following v2 features are **removed or merged** to reduce bloat and improve focus:

| Removed | Reason | Replacement |
|---------|--------|-------------|
| Separate Holdings Intelligence (Agent 05) | Low trading utility | Merged into SEC Filings Agent |
| Separate Investors Intelligence (Agent 11) | Not used in trading loop | Merged into Private Funds Agent |
| Separate Private Debt Analyst (Agent 12) | Not relevant to trading | Merged into Fundamental Agent |
| Investment Report Writer (Agent 16) output format | Overly investment-banking focused | Replaced with Trade Journal reports |
| Deep Research Agent (Agent 14) IC memo output | Not useful in trading context | Re-scoped to market research only |

**Net result:** Same 18 v2 agents (re-scoped where noted) + 10 new = 28 total

---

## 4. SMC Strategy Engine

### Installation

```bash
# Python SMC package
pip install smartmoneyconcepts --break-system-packages
pip install pandas numpy ta-lib vectorbt --break-system-packages

# Test installation
python3 -c "from smartmoneyconcepts import smc; print('SMC ready')"
```

### Core Analysis Script

```python
#!/usr/bin/env python3
"""smc_analyzer.py — Run SMC analysis on any OHLCV dataset"""

import pandas as pd
from smartmoneyconcepts import smc

def run_full_smc_analysis(symbol: str, ohlc_df: pd.DataFrame) -> dict:
    """Run complete SMC analysis and return structured results."""

    # 1. Swing highs/lows (foundation for all SMC concepts)
    swings = smc.swing_highs_lows(ohlc_df, swing_length=50)

    # 2. Break of Structure + Change of Character
    bos_choch = smc.bos_choch(ohlc_df, swings)

    # 3. Order Blocks
    order_blocks = smc.ob(ohlc_df, swings)

    # 4. Fair Value Gaps
    fvgs = smc.fvg(ohlc_df, join_consecutive=True)

    # 5. Liquidity zones
    liquidity = smc.liquidity(ohlc_df, swings)

    # 6. Premium / Discount zones
    pd_zones = smc.premium_discount_levels(ohlc_df, swings)

    # 7. Previous session highs/lows
    prev_hl = smc.previous_high_low(ohlc_df)

    # 8. ICT Trading sessions
    london = smc.sessions(ohlc_df, "London", "08:00", "17:00", "UTC")
    newyork = smc.sessions(ohlc_df, "New York", "13:00", "22:00", "UTC")

    # 9. Confluence score
    confluence = calculate_confluence(order_blocks, fvgs, bos_choch, pd_zones)

    return {
        "symbol": symbol,
        "swings": swings,
        "bos_choch": bos_choch,
        "order_blocks": order_blocks,
        "fvgs": fvgs,
        "liquidity": liquidity,
        "premium_discount": pd_zones,
        "sessions": {"london": london, "newyork": newyork},
        "confluence_score": confluence,
        "bias": determine_bias(bos_choch),
        "setups": generate_setups(order_blocks, fvgs, pd_zones, confluence),
    }


def calculate_confluence(ob, fvg, bos, pd) -> float:
    score = 0.0
    if ob is not None and not ob.empty:
        active_obs = ob[ob["OB"] != 0]
        score += min(len(active_obs) * 0.1, 0.3)
    if fvg is not None and not fvg.empty:
        unfilled = fvg[~fvg["MitigatedIndex"].notna()]
        score += min(len(unfilled) * 0.05, 0.2)
    if bos is not None and not bos.empty:
        recent_bos = bos.tail(5)
        score += (recent_bos["BOS"] != 0).sum() * 0.1
    return min(score, 1.0)


def determine_bias(bos_choch: pd.DataFrame) -> str:
    if bos_choch is None or bos_choch.empty:
        return "NEUTRAL"
    recent = bos_choch.tail(10)
    bullish = (recent["BOS"] == 1).sum() + (recent["CHOCH"] == 1).sum()
    bearish = (recent["BOS"] == -1).sum() + (recent["CHOCH"] == -1).sum()
    if bullish > bearish * 1.5:
        return "BULLISH"
    elif bearish > bullish * 1.5:
        return "BEARISH"
    return "NEUTRAL"
```

### Paperclip Agent Integration

```yaml
# ~/agency/paperclip/agents/smc-strategy.yaml
agent:
  name: SMC Strategy Agent
  model: codellama:34b
  adapter: python
  script: ~/agency/trading/smc_analyzer.py
  skills:
    - smc-order-blocks
    - smc-fair-value-gaps
    - smc-bos-choch
    - smc-liquidity
    - smc-kill-zones
    - smc-confluence
  budget: $25/month
  triggers:
    - cron: "*/15 * * * *"    # Every 15 minutes during market hours
    - webhook: /smc/analyze
```

---

## 5. Technical Indicators — cinar/indicator

### Installation (Go binary + Python wrapper)

```bash
# Install Go
sudo apt install -y golang-go

# Clone and build indicator CLI
git clone https://github.com/cinar/indicator ~/agency/indicator
cd ~/agency/indicator
go build -o ~/agency/bin/indicator ./cmd/indicator/

# Verify
~/agency/bin/indicator --help

# Python wrapper using subprocess
pip install pandas numpy --break-system-packages
```

### Python Integration

```python
#!/usr/bin/env python3
"""technical_engine.py — cinar/indicator integration"""

import subprocess
import json
import pandas as pd

class IndicatorEngine:
    """Wrapper around cinar/indicator Go binary + pure Python implementations."""

    def run_all(self, ohlcv: pd.DataFrame) -> dict:
        return {
            # Trend
            "ema_9":    self.ema(ohlcv["close"], 9),
            "ema_21":   self.ema(ohlcv["close"], 21),
            "ema_50":   self.ema(ohlcv["close"], 50),
            "ema_200":  self.ema(ohlcv["close"], 200),
            "sma_20":   self.sma(ohlcv["close"], 20),
            "sma_200":  self.sma(ohlcv["close"], 200),
            "ichimoku": self.ichimoku(ohlcv),
            "adx":      self.adx(ohlcv, 14),
            "supertrend": self.supertrend(ohlcv, 10, 3),

            # Momentum
            "rsi":      self.rsi(ohlcv["close"], 14),
            "macd":     self.macd(ohlcv["close"], 12, 26, 9),
            "stoch":    self.stochastic(ohlcv, 14, 3),
            "cci":      self.cci(ohlcv, 20),
            "roc":      self.roc(ohlcv["close"], 10),
            "mfi":      self.mfi(ohlcv, 14),

            # Volatility
            "bb":       self.bollinger_bands(ohlcv["close"], 20, 2),
            "atr":      self.atr(ohlcv, 14),
            "keltner":  self.keltner_channels(ohlcv, 20, 2),
            "hv":       self.historical_volatility(ohlcv["close"], 21),

            # Volume
            "obv":      self.on_balance_volume(ohlcv),
            "vwap":     self.vwap(ohlcv),
            "cmf":      self.chaikin_money_flow(ohlcv, 20),
            "ad":       self.accumulation_distribution(ohlcv),
        }

    def get_confluence_signal(self, indicators: dict) -> dict:
        """Aggregate all indicators into a single directional signal."""
        bull_score, bear_score = 0, 0

        # Trend signals
        if indicators["ema_9"].iloc[-1] > indicators["ema_21"].iloc[-1]: bull_score += 1
        else: bear_score += 1
        if indicators["adx"].iloc[-1] > 25: bull_score += 0.5  # Strong trend

        # Momentum signals
        rsi = indicators["rsi"].iloc[-1]
        if 40 < rsi < 70: bull_score += 0.5
        elif rsi < 30: bull_score += 1      # Oversold
        elif rsi > 70: bear_score += 1      # Overbought

        macd = indicators["macd"]
        if macd["histogram"].iloc[-1] > 0: bull_score += 0.5
        else: bear_score += 0.5

        # Volume confirmation
        if indicators["obv"].iloc[-1] > indicators["obv"].iloc[-5]: bull_score += 0.5
        else: bear_score += 0.5

        total = bull_score + bear_score
        return {
            "direction": "LONG" if bull_score > bear_score else "SHORT",
            "confidence": max(bull_score, bear_score) / total,
            "bull_score": bull_score,
            "bear_score": bear_score,
        }
```

---

## 6. Apex Platform Services Integration

The following services from the Apex platform document are ported and integrated:

### Kill Zone Service

```python
# ~/agency/trading/kill_zones.py
from datetime import datetime, timezone, timedelta

KILL_ZONES = {
    "Asian":         {"start": "21:00", "end": "04:00", "pairs": ["AUDJPY","USDJPY","AUDUSD","NZDUSD"]},
    "London Open":   {"start": "02:50", "end": "04:00", "pairs": ["GBPUSD","EURGBP","EURUSD","GBPJPY"]},
    "London":        {"start": "03:00", "end": "12:00", "pairs": ["EURUSD","GBPUSD","EURJPY","GBPJPY"]},
    "New York":      {"start": "08:00", "end": "17:00", "pairs": ["EURUSD","GBPUSD","USDJPY","USDCAD"]},
    "London Close":  {"start": "10:30", "end": "11:00", "pairs": ["EURUSD","GBPUSD"]},
    "NY Close":      {"start": "16:00", "end": "17:00", "pairs": ["All majors — avoid trading"]},
}

def get_active_kill_zones(utc_time: datetime) -> list:
    est_time = utc_time - timedelta(hours=5)
    return [name for name, kz in KILL_ZONES.items()
            if is_in_session(est_time, kz["start"], kz["end"])]
```

### COT Analysis Service

```python
# ~/agency/trading/cot_analyzer.py
# CFTC COT data: downloaded every Friday after 15:30 EST release
import pandas as pd
import requests

def get_cot_data(symbol: str) -> dict:
    """Fetch and analyse CFTC COT report for symbol."""
    url = "https://www.cftc.gov/dea/futures/deahistfo.zip"
    # Process CSV: commercial_long, commercial_short, large_spec_long, large_spec_short
    ...

def analyze_cot_extremes(symbol: str, lookback: int = 52) -> dict:
    """Identify COT positioning extremes (percentile rank)."""
    data = get_cot_data(symbol)
    net_commercial = data.commercial_long - data.commercial_short
    percentile = scipy.stats.percentileofscore(
        net_commercial.tail(lookback), net_commercial.iloc[-1]
    )
    return {
        "net_commercial": net_commercial.iloc[-1],
        "percentile": percentile,
        "signal": "BULLISH" if percentile > 80 else "BEARISH" if percentile < 20 else "NEUTRAL",
        "extreme": percentile > 90 or percentile < 10,
    }
```

### Special Pattern Detection (from Apex `aiIntelligence.ts`)

```python
def detect_silver_bullet(ohlcv: pd.DataFrame, session: str) -> dict:
    """ICT Silver Bullet: M1 FVG during London 10-11AM or NY 2-3PM EST."""
    ...

def detect_judas_swing(ohlcv: pd.DataFrame) -> dict:
    """False breakout at session open before true directional move."""
    ...

def analyze_power_of_3(daily_ohlcv: pd.DataFrame) -> dict:
    """AMD: Accumulation (Asia) → Manipulation (London) → Distribution (NY)."""
    ...
```

---

## 7. New Skills Library — Trading Skills

Install trading skills alongside financial skills:

```bash
# Trading-specific skills
ls ~/agency/paperclip/skills/trading/

smc-order-blocks/         smc-fair-value-gaps/       smc-bos-choch/
smc-liquidity/            smc-kill-zones/             smc-confluence/
smc-silver-bullet/        smc-judas-swing/            smc-power-of-3/
tech-rsi/                 tech-macd/                  tech-bollinger/
tech-ichimoku/            tech-adx/                   tech-momentum/
tech-volume/              tech-divergence/             tech-confluence/
fundamental-regime/       fundamental-calendar/        fundamental-rates/
sentiment-cot/            sentiment-fear-greed/        sentiment-composite/
news-nlp/                 news-events/                 news-breaking/
backtest-smc/             backtest-technical/          backtest-combined/
forex-smc/                forex-cot/                   forex-sessions/
commodities-smc/          commodities-fundamentals/    commodities-seasonality/
indices-breadth/          indices-vix/                 indices-sectors/
```

**Skill Installation:**
```bash
# Add trading skills to Paperclip
cp -r ~/agency/trading/skills/* ~/agency/paperclip/skills/trading/

# Or install from registry when available
npx skills add AgentKits/trading-skills
```

---

## 8. cTrader CLI — Live Trading Execution

### Setup & Authentication

```bash
# Install cTrader Open API CLI
npm install -g @spotware/ctrader-cli 2>/dev/null \
  || pip install ctrader-open-api --break-system-packages

# For the Open API Python client
git clone https://github.com/spotware/OpenApiPy ~/agency/ctrader
cd ~/agency/ctrader && pip install -e . --break-system-packages

# Store credentials in Vault
vault kv put secret/trading/ctrader \
  client-id=YOUR_CLIENT_ID \
  client-secret=YOUR_CLIENT_SECRET \
  account-id=YOUR_ACCOUNT_ID \
  access-token=YOUR_ACCESS_TOKEN
```

### Trade Execution Script

```python
#!/usr/bin/env python3
"""live_executor.py — cTrader Open API execution layer"""

from ctrader_open_api import Client, Protobuf, TcpProtocol
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *

class CTraderExecutor:
    def __init__(self, account_id: int, access_token: str):
        self.client = Client("live.ctraderapi.com", 5035, TcpProtocol)
        self.account_id = account_id
        self.access_token = access_token

    def place_market_order(
        self,
        symbol_id: int,
        direction: str,       # "BUY" | "SELL"
        volume: int,          # In units (100 = 0.01 lot)
        stop_loss_pips: int,
        take_profit_pips: int,
        label: str,
    ) -> dict:
        """Place a market order with SL/TP."""
        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self.account_id
        request.symbolId = symbol_id
        request.orderType = ProtoOAOrderType.MARKET
        request.tradeSide = ProtoOATradeSide.BUY if direction == "BUY" else ProtoOATradeSide.SELL
        request.volume = volume
        request.relativeStopLoss = stop_loss_pips
        request.relativeTakeProfit = take_profit_pips
        request.comment = label
        # Submit and return position ID
        ...

    def close_position(self, position_id: int, volume: int = None) -> bool:
        """Close full or partial position."""
        ...

    def modify_position(
        self, position_id: int,
        new_stop_loss: float = None,
        new_take_profit: float = None
    ) -> bool:
        """Modify SL/TP on open position."""
        ...

    def get_portfolio(self) -> dict:
        """Get all open positions, orders, and account equity."""
        ...
```

### n8n → cTrader Execution Flow

```
Signal generated → n8n receives webhook
  → Parse signal (symbol, direction, entry, SL, TP, confidence)
  → Risk check (Python script)
  → IF approved: Telegram APPROVE button
  → Trader approves → cTrader execute
  → Position ID returned → monitor webhook active
  → Price hits TP1 → partial close (50%)
  → Trail SL to breakeven
  → Price hits TP2 → full close
  → P&L recorded → journal entry → daily digest
```

---

## 9. Strategy Backtesting Agent

### Running Backtests via Paperclip CLI

```bash
# Run SMC backtest on EURUSD H1 for 2024
paperclipai task create \
  --agent backtest-agent \
  --command "/backtest:run smc EURUSD" \
  --params '{"timeframe":"H1","start":"2024-01-01","end":"2024-12-31","risk":1.0}'

# Compare strategies
paperclipai task create \
  --agent backtest-agent \
  --command "/backtest:compare smc technical EURUSD H4 2023-2024"

# Walk-forward validation
paperclipai task create \
  --agent backtest-agent \
  --command "/backtest:walkforward smc GBPUSD H1 2023-2024"
```

### Vectorbt Backtest Script

```python
#!/usr/bin/env python3
"""backtest_engine.py — Strategy backtesting using vectorbt"""

import vectorbt as vbt
import pandas as pd
import numpy as np
from smc_analyzer import run_full_smc_analysis
from technical_engine import IndicatorEngine

def backtest_smc_strategy(
    symbol: str,
    ohlcv: pd.DataFrame,
    config: dict
) -> dict:
    """Backtest SMC strategy using vectorbt."""

    # Generate signals
    signals = []
    for i in range(50, len(ohlcv)):
        window = ohlcv.iloc[:i]
        analysis = run_full_smc_analysis(symbol, window)
        if analysis["confluence_score"] >= 0.75:
            direction = analysis["bias"]
            if direction in ["BULLISH", "BEARISH"]:
                signals.append({
                    "index": i,
                    "direction": direction,
                    "entry": ohlcv["close"].iloc[i],
                    "sl": calculate_sl(analysis, direction),
                    "tp": calculate_tp(analysis, direction),
                })

    # Build entry/exit arrays
    entries = pd.Series(False, index=ohlcv.index)
    exits = pd.Series(False, index=ohlcv.index)
    for sig in signals:
        entries.iloc[sig["index"]] = True

    # Run vectorbt simulation
    portfolio = vbt.Portfolio.from_signals(
        ohlcv["close"],
        entries=entries,
        exits=exits,
        sl_stop=config.get("stop_loss_pct", 0.01),
        tp_stop=config.get("take_profit_pct", 0.02),
        fees=config.get("commission", 0.0007),
        slippage=config.get("slippage", 0.0002),
        init_cash=config.get("initial_balance", 10000),
        freq="1H",
    )

    return {
        "total_return": portfolio.total_return(),
        "sharpe_ratio": portfolio.sharpe_ratio(),
        "sortino_ratio": portfolio.sortino_ratio(),
        "max_drawdown": portfolio.max_drawdown(),
        "win_rate": portfolio.trades.win_rate(),
        "profit_factor": portfolio.trades.profit_factor(),
        "total_trades": portfolio.trades.count(),
        "avg_rr": portfolio.trades.expectancy(),
        "equity_curve": portfolio.value().to_list(),
        "monthly_returns": portfolio.returns().resample("M").apply(
            lambda x: (1 + x).prod() - 1
        ).to_dict(),
    }
```

---

## 10. n8n Workflow Blueprints — Trading Automation

### Flow 1: SMC Signal → Execution Pipeline

```
Trigger: Every 15 min cron (market hours only: Mon-Fri 00:00-22:00 UTC)

Node 1: Check kill zones → is any session active?
Node 2: IF active session → fetch OHLCV for all monitored symbols (15 pairs)
Node 3: Python → run_full_smc_analysis() on all symbols in parallel
Node 4: Filter → confluence_score >= 0.75
Node 5: Technical confirmation → IndicatorEngine.get_confluence_signal()
Node 6: Fundamental regime check → is macro aligned with trade direction?
Node 7: Sentiment check → is sentiment confirming or extreme contrarian?
Node 8: Risk check → max positions, daily loss, correlation check
Node 9: Calculate position size → kelly_criterion * 0.5 (half-Kelly)
Node 10: Build signal package → symbol, direction, entry, SL, TP, confidence, R:R
Node 11: Telegram message → "🟢 TRADE ALERT: BUY EURUSD 1.0823 | SL 1.0756 | TP1 1.0890 | TP2 1.0980 | R:R 2.1 | Conf 81%"
Node 12: InlineKeyboard → [✅ EXECUTE] [👁 WATCH] [❌ REJECT]
Node 13: EXECUTE → cTrader API → place market order
Node 14: Confirm → "Position #12345 opened: 0.1 lot EURUSD @ 1.0823"
```

### Flow 2: Position Management & Trailing

```
Trigger: Webhook from cTrader position update every 5 min

Node 1: Receive position status update
Node 2: Check if TP1 hit (50% of distance)
Node 3: IF TP1 hit → close 50% of position
Node 4: Move SL to breakeven + 5 pips
Node 5: IF TP2 hit → close remaining position
Node 6: IF SL hit → close all, log loss to journal
Node 7: Update Supabase trade journal
Node 8: Telegram notification with trade result
```

### Flow 3: Economic Calendar Block

```
Trigger: Cron every 30 min

Node 1: Fetch investing.com calendar for next 4 hours
Node 2: Filter: impact = HIGH or CRITICAL
Node 3: IF event in next 30 min → activate trade block
Node 4: Telegram: "⚠️ High-impact event in 30min: US NFP — Execution blocked"
Node 5: IF existing position in affected currency → send alert
Node 6: After event → check actual vs forecast → generate post-news setup
Node 7: Lift block after 15 min post-release
```

### Flow 4: Morning Intelligence Briefing (Enhanced)

```
Trigger: Cron 06:00 UTC Monday-Friday

Node 1: Economic calendar for today → high/medium impact events
Node 2: Overnight SMC analysis → any setups formed during Asian session?
Node 3: COT update check → new report released this week?
Node 4: Active trade status → P&L, open positions, pending orders
Node 5: Kill zone schedule → next active session and best pairs
Node 6: Macro regime → has anything changed in past 24h?
Node 7: Compile briefing → Telegram rich message
Node 8: Notion → save briefing to intelligence database
```

### Flow 5: Weekly Performance Review

```
Trigger: Cron Sunday 18:00 UTC

Node 1: Pull all closed trades from Supabase (past 7 days)
Node 2: Calculate: win rate, profit factor, total pips, R:R achieved
Node 3: Strategy breakdown: which strategies performed best/worst?
Node 4: Compare to backtest expectations — is live performance matching?
Node 5: Identify: which sessions had best results?
Node 6: Recommendations: adjust strategy weights for coming week
Node 7: Generate weekly journal entry → Notion
Node 8: Telegram weekly P&L digest
```

---

## 11. Data Sources & API Configuration

```bash
# Store all trading API keys in Vault
vault kv put secret/trading/apis \
  polygon-key=YOUR_KEY \
  alpha-vantage=YOUR_KEY \
  oanda-api=YOUR_KEY \
  oanda-account=YOUR_ACCOUNT \
  newsapi-key=YOUR_KEY \
  twitter-bearer=YOUR_TOKEN \
  investing-scraper-key=YOUR_KEY \
  fred-api-key=YOUR_KEY \
  tradingeconomics-key=YOUR_KEY

# .env.trading (loaded by n8n and Python scripts)
POLYGON_API_KEY=$(vault kv get -field=polygon-key secret/trading/apis)
OANDA_API_KEY=$(vault kv get -field=oanda-api secret/trading/apis)
FRED_API_KEY=$(vault kv get -field=fred-api-key secret/trading/apis)
CTRADER_ACCESS_TOKEN=$(vault kv get -field=access-token secret/trading/ctrader)
```

**Data Source Map:**

| Asset Class | OHLCV Data | Fundamentals | Sentiment |
|-------------|-----------|--------------|-----------|
| Forex | OANDA API | Central bank websites | CFTC COT, SSI |
| Commodities | Polygon.io | EIA, USDA, World Bank | CFTC COT |
| Indices | Polygon.io | FRED (VIX, A/D) | CBOE put/call |
| Equities | Polygon.io | Financial MCP Server | SEC + COT |
| Crypto | Financial MCP | On-chain analytics | Fear & Greed |

---

## 12. Installation on Kali Linux

### Full v3 Setup Script

```bash
#!/bin/bash
# install-agentfinance-v3.sh

echo "=== AgentFinance v3 Installation ==="

# 1. Core dependencies
sudo apt update && sudo apt install -y \
  golang-go python3-pip python3-venv git curl \
  redis-server postgresql-client jq

# 2. Python environment
python3 -m venv ~/agency/trading/venv
source ~/agency/trading/venv/bin/activate

pip install \
  smartmoneyconcepts \
  pandas numpy scipy statsmodels \
  vectorbt ta-lib \
  requests aiohttp websockets \
  ctrader-open-api \
  transformers torch  # For local NLP (FinBERT)
  
# 3. Go indicator library
git clone https://github.com/cinar/indicator ~/agency/indicator
cd ~/agency/indicator && go build -o ~/agency/bin/indicator ./cmd/...

# 4. SMC package verification
python3 -c "from smartmoneyconcepts import smc; print('✓ SMC package ready')"

# 5. cTrader CLI
pip install ctrader-open-api --break-system-packages

# 6. Paperclip (from v2)
# Already installed — just add new agent configs
cp ~/agency/v3/agents/*.yaml ~/agency/paperclip/agents/

# 7. Trading skills
cp -r ~/agency/v3/skills/* ~/agency/paperclip/skills/

# 8. n8n workflows
# Import v3 workflow JSONs via n8n UI at http://localhost:5678

echo "=== v3 Installation Complete ==="
echo "28 agents ready | SMC + Indicators + cTrader configured"
```

---

## 13. Risk Management & Safety Gates

### Hard Risk Rules (Non-Negotiable)

```python
RISK_RULES = {
    "max_risk_per_trade":     0.01,    # 1% account per trade
    "max_daily_drawdown":     0.03,    # 3% daily → halt all trading
    "max_concurrent_trades":  5,       # Max open positions
    "max_correlation_overlap":0.8,     # No two positions >80% correlated
    "min_rr_ratio":           1.5,     # Minimum 1.5:1 risk/reward
    "pre_news_block_minutes": 15,      # Block before high-impact news
    "post_news_block_minutes":15,      # Block after high-impact news
    "max_spread_multiplier":  3.0,     # Block if spread >3x average
    "signal_max_age_hours":   4,       # Signals expire after 4 hours
    "min_confidence_score":   0.75,    # Minimum signal confidence
    "max_monthly_drawdown":   0.08,    # 8% monthly → stop trading
}
```

### Kill Switch

```bash
# Emergency stop — closes all positions, halts all agents
paperclipai org halt-all
ctrader positions close-all
vault kv put secret/trading/status mode=halted
```

---

## 14. Performance Optimisations

### Removed from v2 (optimisations)

1. **Removed**: IP-protection focus on source code privacy — trading systems need speed over air-gap
2. **Removed**: Investment-banking report style outputs — replaced with compact trade summaries
3. **Removed**: Manual IC approval for all trades — automated for small sizes, APPROVE for larger
4. **Removed**: 7-year audit log for every action — retained for trades only (regulatory)

### Added Optimisations

1. **Signal caching**: Redis caches SMC analysis results for 15 minutes — avoid re-computation
2. **Parallel processing**: All 15 monitored symbols analysed concurrently using `asyncio`
3. **Streaming prices**: WebSocket connections to OANDA and Polygon instead of REST polling
4. **Local FinBERT**: News NLP runs on-device — eliminates OpenAI API latency for sentiment
5. **Vectorbt**: Backtests run in seconds using pandas vectorisation, not trade-by-trade loops
6. **Pre-computed COT**: COT percentiles computed on Friday release, cached for the week
7. **Kill zone guard**: SMC scanner only runs during active sessions — saves CPU/API costs

---

## 15. Enhancement Roadmap

### Phase 1 (Immediate — v3.0)
- [ ] Deploy all 28 agents on Paperclip
- [ ] Install SMC + indicator engines
- [ ] Configure cTrader demo account
- [ ] Run 3-month backtest on top 5 FX pairs
- [ ] Validate SMC signals on paper trading for 30 days

### Phase 2 (v3.1)
- [ ] **Multi-timeframe dashboard**: React/Vite UI showing live SMC overlays
- [ ] **Alert consolidation**: Single Telegram channel for all signals, ranked by quality
- [ ] **Auto-journal**: Every trade auto-documented with entry reasoning + screenshots

### Phase 3 (v3.2)
- [ ] **ML signal filter**: Train XGBoost model on historical signals → filter false positives
- [ ] **Portfolio optimiser**: Kelly Criterion + correlation-adjusted position sizing
- [ ] **Multi-broker**: Add Interactive Brokers API for equities, Binance for crypto

### Phase 4 (v3.3)
- [ ] **Strategy marketplace**: Share and compare strategies with other AgentFinance users
- [ ] **Adaptive parameters**: Agents auto-adjust strategy parameters based on recent performance
- [ ] **Client mode**: Manage trading for multiple clients with isolated portfolios

---

*AgentFinance v3 — Implementation Guide*
*Built on: Paperclip + SMC Engine (joshyattridge) + Indicators (cinar) + Apex Platform + cTrader*
*Architecture: 28 agents · 6 departments · Full-cycle trading automation · Kali Linux*
