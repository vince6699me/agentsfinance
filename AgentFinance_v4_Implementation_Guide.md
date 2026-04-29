

**AgentFinance v4**

Complete Implementation Guide


Autonomous AI Trading System

| **System** | **Value** |
| - | - |
| Architecture | Paperclip + Signal Fusion + cTrader |
| Agents | 21 Agents across 6 Analysis Departments |
| Departments | Fundamental · Technical · Sentiment · Intermarket · Quantitative · SMC/ICT |
| Strategies | 79 registered strategies across 3 strategy registries |
| Execution | cTrader Open API (Demo + Live) |
| Infrastructure | n8n · Redis · Supabase · Vault · Kali Linux |
| Version | v4.0 — April 2026 |
| Status | Implementation Ready |


CONFIDENTIAL — INTERNAL SYSTEM DOCUMENTATION


# **Executive Summary**


**AgentFinance v4 is a fully autonomous AI-powered trading system built on the Paperclip agent orchestration framework. It replaces the legacy department structure (Public Markets, Private Markets, Research, Operations) with six philosophy-driven analysis departments that mirror how professional trading firms are organised — by the methodology each team applies to the market.**

**The six new departments are: Fundamental Analysis, Technical Analysis, Sentiment Analysis, Intermarket Analysis, Quantitative/Systematic Analysis, and SMC/ICT Analysis. Every department has dedicated AI agents with their own toolkits, data sources, and registered strategies sourced from an extensive library of 79 formally extracted trading strategies.**

### **Key Improvements Over v3**

- **Signal Fusion Layer: cross-department confluence engine that combines all six analytical perspectives before execution**

- **Signal Fusion Layer: weighted composite scoring — no trade executes without multi-department agreement**

- **REST API authentication on all order endpoints — mandatory before live trading**

- **Redis OHLCV caching — reduces API calls by 85% across all 20+ monitored pairs**

- **Market Regime Filter — upstream of all analysis; prevents false signals in ranging markets**

- **Watchdog process — independent systemd service that closes all positions if system goes offline**

- **Right-sized LLM models per agent — CodeLLama 34B only for code agents; Mistral 7B for classification**

- **Equity curve dashboard — 8th tab added to React dashboard for real-time P&L visualization**

- **Forex Factory JSON calendar — replaces fragile Investing.com scraper**

- **Trailing stop logic — after TP1 hit, 15-pip trail captures full trend extension**


| **Metric** | **v3** | **v4** |
| - | - | - |
| Departments | 7 (mixed) | 6 (philosophy-based) |
| Total Agents | 28 | 21 (focused) |
| Registered Strategies | — | 79 across 3 registries |
| Signal Fusion | None | 6-department weighted fusion |
| REST Security | None | API Key auth on all order endpoints |
| Caching | Not active | Redis — 85% API call reduction |
| Market Regime Filter | None | ADX + ATR + BB Width |
| Watchdog | None | systemd — 30-min dead man switch |
| Calendar Source | Investing.com (fragile) | Forex Factory JSON (stable) |


# **1. Architecture Overview**


## **1.1 System Architecture**

**AgentFinance v4 operates as a layered autonomous system. Market data flows in through API adapters, is processed in parallel by six analytical departments, fused into a single confluenced signal, passed through a 7-gate risk pipeline, and then executed via the cTrader Open API. Every step is orchestrated by n8n workflows with logging to Supabase and alerts via Telegram.**


| **Layer** | **Components** | **Technology** |
| - | - | - |
| Data Ingestion | OANDA, Polygon, FRED, NewsAPI, CFTC COT | REST APIs + WebSocket |
| Caching | OHLCV cache — 10 min H1/H4, 2 min M15 | Redis |
| Market Regime | ADX, ATR, Bollinger Width filter | Python + pandas |
| Dept. 1 — Fundamental | Macro, FX Fund., Commodities, Equity Fund. | Agents 01–04 |
| Dept. 2 — Technical | Price Action, Indicators, Trend | Agents 05–07 |
| Dept. 3 — Sentiment | COT, Market Sentiment, News NLP | Agents 08–10 |
| Dept. 4 — Intermarket | Bond-Equity, Commodity-FX, Correlations | Agents 11–13 |
| Dept. 5 — Quantitative | Stat Arb, Factor Models, Algo Execution | Agents 14–17 |
| Dept. 6 — SMC/ICT | Order Blocks, Structure, Liquidity, Sessions | Agents 18–21 |
| Signal Fusion | Weighted composite score, hard veto rules | signal\_fusion.py |
| Risk Management | 7-gate pipeline, drawdown limits, correlation | risk\_manager.py |
| Execution | cTrader REST API (port 9009), authenticated | ctrader\_api\_server.py |
| Orchestration | Trade triggers, monitoring, reporting | n8n (port 5678) |
| Persistence | Trade log, signals, performance | Supabase (PostgreSQL) |
| Monitoring | React dashboard, Telegram alerts, equity curve | Vite + React |

## **1.2 Department Structure**

| **\#** | **Department** | **Philosophy** | **Agents** | **Strategies** |
| - | - | - | - | - |
| 1 | Fundamental Analysis | Macro, CB policy, earnings, COT fundamentals | 01–04 | 10 |
| 2 | Technical Analysis | Price action, indicators, patterns, trends | 05–07 | 22 |
| 3 | Sentiment Analysis | COT, retail positioning, news NLP, fear/greed | 08–10 | 8 |
| 4 | Intermarket Analysis | Cross-asset correlations, bonds/commodities/FX | 11–13 | 6 |
| 5 | Quantitative/Systematic | Algo execution, stat arb, factor models | 14–17 | 21 |
| 6 | SMC/ICT Analysis | Order blocks, structure, liquidity, kill zones | 18–21 | 12 |

## **1.3 Signal Flow**

**The signal flow follows a strict sequence that cannot be bypassed:**

- **Step 1 — Market Regime Filter: ADX + ATR + BB Width classification before any analysis runs**

- **Step 2 — Parallel department analysis: all 6 departments run concurrently via asyncio**

- **Step 3 — Signal Fusion: composite score calculated with hard veto rules applied**

- **Step 4 — Risk Pipeline: 7-gate check (halt → drawdown → news → spread → correlation → sizing → confidence)**

- **Step 5 — Execution: authenticated REST call to cTrader API server**

- **Step 6 — Position Management: TP1 partial close → SL to breakeven → trailing stop**

- **Step 7 — Logging: trade written to Supabase, Telegram notification sent**


| **DEPARTMENT 1  Fundamental Analysis** |
| - |


**The Fundamental Analysis department interprets macroeconomic forces, central bank policy divergence, currency pair fundamentals, commodity supply/demand dynamics, and equity financials. It provides the macro framework within which all other departments operate — establishing the directional bias that SMC and technical agents refine into precise entries.**

| **01** | **Macro Economics Agent** Monitor global macroeconomic conditions — GDP, inflation, interest rates, employment — and translate them into actionable directional bias for all asset classes. |
| :-: | - |

#### **Data Sources**

- **FRED API — GDP, CPI, PCE, unemployment, yield curves**

- **Central bank websites — Fed, ECB, BOE, BOJ, RBA, SNB meeting statements**

- **IMF World Economic Outlook — global growth forecasts**

- **TradingEconomics API — real-time macro indicator releases**

#### **Capabilities**

- **Interest rate differential scoring: rate × policy direction × market pricing**

- **Inflation regime classification: deflation / low / target / elevated / runaway**

- **Yield curve shape analysis: normal / flat / inverted — recession probability**

- **Growth-inflation quadrant mapping: Goldilocks / Overheating / Stagflation / Recession**

- **Central bank meeting calendar: pre-meeting positioning, rate probability tracking**

#### **Registered Strategies**

| **ID** | **Strategy** | **Timeframe** | **Asset Class** |
| - | - | - | - |
| STRAT\_020 | Macro Event-Driven Trade | Event-based | FX, Commodities, Indices |
| STRAT\_025 | Central Bank Intervention Trading | Event-based | FX, Bonds |
| STRAT\_019 | Carry Trade Strategy | Long-term | FX |
| STRAT\_022 | Bond Spreads as Leading Indicator | Medium-term | FX, Equities |

#### **Skills**

- **macro-gdp-analysis · macro-inflation-tracker · macro-yield-curve**

- **macro-cb-policy · macro-growth-quadrant · macro-rate-probability**

#### **LLM Model**

**llama3.1:8b — economic analysis and prose synthesis**


| **02** | **Forex Fundamentals Agent** Analyse currency pair fundamentals — central bank policy divergence, interest rate differentials, carry attractiveness, and economic cycle positioning — to generate fundamental directional bias per pair. |
| :-: | - |

#### **Data Sources**

- **OANDA API — real-time FX rates, order book depth**

- **CFTC COT reports — commercial vs large speculator positioning**

- **Central bank forward guidance — dot plots, press conferences**

- **BIS quarterly FX turnover data — liquidity profiling**

#### **Capabilities**

- **28 major/minor pairs + 20 exotic pairs continuously monitored**

- **Currency strength matrix: relative ranking of all 8 majors**

- **Carry trade scoring: interest rate differential × current account × momentum**

- **Pairing algorithm: match strongest currency vs weakest — STRAT\_018**

- **Economic surprise index: actual vs consensus across all G10 economies**

- **Session-aware kill zone alerts: Asian, London, NY, London Close**

#### **Registered Strategies**

| **ID** | **Strategy** | **Signal Type** | **Weight** |
| - | - | - | - |
| STRAT\_018 | Pairing Strong with Weak (Fundamental) | Directional bias | High |
| STRAT\_019 | Carry Trade Strategy | Yield differential signal | Medium |
| STRAT\_020 | Macro Event-Driven Trade | Event-triggered entry | High |
| STRAT\_025 | Central Bank Intervention Trading | Regime signal | Critical |

#### **Skills**

- **forex-central-bank-policy · forex-carry-trade · forex-currency-strength**

- **forex-economic-surprise · forex-cot-report · forex-session-pairs**

#### **LLM Model**

**llama3.1:8b — fundamental scoring and currency strength synthesis**


| **03** | **Commodities Fundamental Agent** Analyse commodity markets using supply/demand fundamentals, inventory reports, WASDE/EIA data, geopolitical risk premiums, and COT positioning to generate directional bias for energy, metals, and agricultural markets. |
| :-: | - |

#### **Data Sources**

- **EIA weekly petroleum status report — crude/natural gas inventories**

- **USDA WASDE reports — agricultural supply/demand**

- **World Gold Council — gold demand data**

- **CFTC COT reports — futures positioning**

- **TradingEconomics API — commodity price series**

#### **Registered Strategies**

| **ID** | **Strategy** | **Commodity** | **Signal Type** |
| - | - | - | - |
| STRAT\_021 | Commodity Prices as Leading Indicator | All | Intermarket signal |
| STRAT\_019 | Carry Trade (commodity-linked FX) | AUD/NZD/CAD | FX bias |
| STRAT\_020 | Macro Event-Driven Trade | Oil, Gold | Event-triggered |

#### **Skills**

- **commodities-eia-report · commodities-wasde · commodities-seasonality**

- **commodities-geopolitical · commodities-supply-demand · commodities-cot**

#### **LLM Model**

**mistral:7b — supply/demand scoring and report parsing**


| **04** | **Equity Fundamentals Agent** Evaluate equity instruments using financial statements, earnings quality, valuation multiples, sector positioning, and institutional holdings — generating fundamental signals for index and single-stock CFD trading. |
| :-: | - |

#### **Data Sources**

- **Financial MCP Server — SEC filings, 10-K/10-Q, earnings calls**

- **Polygon.io — earnings calendar, analyst estimates**

- **FRED API — VIX, sector performance, put/call ratios**

#### **Capabilities**

- **P/E, EV/EBITDA, Price/Book, PEG ratio scoring across S&P 500 constituents**

- **Earnings quality analysis: accruals ratio, cash flow vs reported earnings**

- **Sector rotation model — identify leadership vs laggard GICS sectors**

- **Market breadth: A/D line, new highs/lows, % above 50/200MA**

- **VIX regime classification: low \<15, normal 15-25, elevated 25-35, crisis \>35**

#### **LLM Model**

**llama3.1:8b — financial statement analysis and equity synthesis**


| **DEPARTMENT 2  Technical Analysis** |
| - |


**The Technical Analysis department applies price action methods, indicator-based signals, and chart pattern recognition across all monitored instruments. It operates entirely from OHLCV data and produces directional signals that are weighted at 25% in the Signal Fusion engine. Technical agents run on all timeframes from M15 to Weekly.**

| **05** | **Price Action & Patterns Agent** Identify high-probability candlestick and chart patterns — engulfing, pin bar, head and shoulders, flags, wedges, triangles, cup and handle — and generate pattern-completion entry signals with measured targets. |
| :-: | - |

#### **Data Sources**

- **OANDA API — M15, H1, H4, D1 OHLCV data for all monitored pairs**

- **Polygon.io — equity index and commodity OHLCV**

#### **Capabilities**

- **Candlestick: engulfing, pin bar/hammer, doji, shooting star, inside bar**

- **Continuation: flag, pennant, rising/falling wedge, cup and handle**

- **Reversal: head and shoulders, double top/bottom, triple top/bottom**

- **Consolidation: ascending, descending, symmetrical triangle breakouts**

- **Inside Days Breakout Play (STRAT\_013) — 2–5 day range compression**

- **20-Day Breakout Trade (STRAT\_015) — range expansion after consolidation**

#### **Registered Strategies**

| **ID** | **Strategy** | **Pattern Type** | **Win Rate (est.)** |
| - | - | - | - |
| STRAT\_013 | Inside Days Breakout Play | Continuation | ~60% |
| STRAT\_015 | 20-Day Breakout Trade | Breakout | ~58% |
| STRAT\_016 | Channel Trading Strategy | Range / Trend | ~62% |
| R2-020 | Head and Shoulders / Inverse H&S | Reversal | ~63% |
| R2-021 | Double Top / Double Bottom | Reversal | ~60% |
| R2-022 | Engulfing Candlestick Pattern | Reversal / Continuation | ~58% |
| R2-023 | Pin Bar / Hammer / Shooting Star | Reversal | ~61% |
| R2-024 | Flag and Pennant Patterns | Continuation | ~64% |
| R2-025 | Rising and Falling Wedge | Reversal / Continuation | ~59% |
| R2-026 | Triangle Patterns (All Types) | Breakout | ~61% |
| R2-027 | Cup and Handle Pattern | Continuation | ~65% |

#### **Skills**

- **pattern-candlestick · pattern-chart-formations · pattern-breakout**

- **pattern-reversal · pattern-continuation · pattern-measured-move**

#### **LLM Model**

**codellama:34b — pattern detection code generation for novel configurations**


| **06** | **Indicator-Based Analysis Agent** Apply a comprehensive suite of 80+ technical indicators — momentum oscillators, trend followers, volume, and volatility indicators — using the cinar/indicator Go library to generate systematic, rule-based signals. |
| :-: | - |

#### **Indicator Categories**

| **Category** | **Indicators Deployed** |
| - | - |
| Trend | EMA (5,13,20,50,200), SMA, DEMA, TEMA, WMA, HMA, Supertrend, Ichimoku |
| Momentum | RSI (14), MACD (12/26/9), Stochastic (5,3), CCI, Williams %R, ROC, MFI |
| Volatility | Bollinger Bands (20,2), ATR (14), Keltner Channel, Donchian Channel |
| Volume | OBV, VWAP, CMF, A/D Line, Force Index, Volume SMA |
| Composite | ADX/DI (14), Perfect Order (7/21/50 EMAs), Double Bollinger Bands |

#### **Registered Strategies**

| **ID** | **Strategy** | **Primary Indicator** | **Signal** |
| - | - | - | - |
| STRAT\_003 | Technical Divergence Trading | RSI/MACD vs Price | Reversal |
| STRAT\_004 | Moving Average Crossover | EMA crossovers | Trend |
| STRAT\_005 | Stochastic Oscillator Trading | Stochastic (5,3) | Overbought/Sold |
| STRAT\_006 | MACD Trading | MACD (12/26/9) | Momentum |
| STRAT\_007 | Bollinger Bands Trading | BB (20,2) | Mean Reversion |
| STRAT\_011 | Double Bollinger Bands Strategy | DBB (Kathy Lien) | Trend + Range |
| STRAT\_017 | Perfect Order Strategy | 7/21/50 EMA alignment | Trend Strength |
| R1-013 | Multiple Time Frame Momentum (MTF) | Multi-TF alignment | Confluence |

#### **Skills**

- **indicator-momentum · indicator-trend · indicator-volatility · indicator-volume**

- **indicator-confluence · indicator-divergence · indicator-mtf-alignment**

#### **LLM Model**

**mistral:7b — indicator scoring and threshold evaluation**


| **07** | **Trend Analysis Agent** Identify and quantify trend direction, strength, and maturity across all timeframes. Applies Fibonacci/Elliott Wave analysis, trend line and channel mapping, and multi-timeframe trend alignment. |
| :-: | - |

#### **Registered Strategies**

| **ID** | **Strategy** | **Method** | **Timeframe** |
| - | - | - | - |
| STRAT\_008 | Trend Line and Channel Trading | Drawn levels, channel bounds | H1–D1 |
| STRAT\_009 | Fibonacci and Elliott Wave Analysis | 0.382/0.618/OTE retracement | H4–W1 |
| STRAT\_010 | Multiple Time Frame Analysis | Top-down alignment (W/D/H4/H1) | Multi-TF |
| R1-014 | ABC Correction / Gartley Pattern Reversal | Elliott ABC structure | H1–D1 |
| R1-015 | Five-Wave Trend Completion (Elliott Wave) | Impulse wave count | D1–W1 |
| R1-016 | Dynamic Price Cluster Reversal | Fib confluence cluster | H4–D1 |
| R1-017 | Dynamic Time Projection Reversal | Fib time projection | D1 |

#### **Skills**

- **trend-fibonacci · trend-elliott-wave · trend-channel · trend-mtf-alignment**

- **trend-strength-adx · trend-maturity-scoring**

#### **LLM Model**

**llama3.1:8b — Elliott Wave interpretation and trend narrative synthesis**


| **DEPARTMENT 3  Sentiment Analysis** |
| - |


**The Sentiment Analysis department reads the market's psychological state from three angles: institutional positioning (COT reports), retail crowd behaviour (SSI, fear/greed), and information flow (news NLP, economic events). Sentiment signals carry a 10% weight in the fusion engine but can issue hard veto signals — particularly for high-impact news events.**

| **08** | **COT Positioning Agent** Parse and analyse CFTC Commitment of Traders reports weekly — tracking commercial hedger vs large speculator vs small retail positioning — to identify extreme sentiment readings that historically precede major reversals. |
| :-: | - |

#### **Data Sources**

- **CFTC.gov — weekly COT legacy and disaggregated reports (released Friday 15:30 ET)**

- **Quandl/FRED — historical COT data series for percentile analysis**

#### **Capabilities**

- **Net positioning calculation: (long - short) for each trader class**

- **52-week percentile ranking: extreme readings signal mean-reversion setup**

- **Commercial Hedger Index (CHI) — commercial hedgers are the 'smart money'**

- **COT Index: (current net - 52wk min) / (52wk max - 52wk min) × 100**

- **Covers: all major FX futures, Gold, Silver, Crude, Natural Gas, S&P futures**

- **Pre-computed Friday release, cached for the entire trading week**

#### **Registered Strategies**

| **ID** | **Strategy** | **Signal** | **Reliability** |
| - | - | - | - |
| R2-003 | VIX COT Report Sentiment Strategy | Extreme VIX positioning signal | High |
| STRAT\_018 | Pairing Strong with Weak | COT-confirmed currency strength | High |
| STRAT\_019 | Carry Trade (COT confirmation) | Institutional carry accumulation | Medium |

#### **Skills**

- **cot-commercial-index · cot-percentile-ranking · cot-extreme-reading**

- **cot-net-positioning · cot-weekly-parser · cot-divergence-alert**

#### **LLM Model**

**mistral:7b — COT data interpretation and percentile scoring**


| **09** | **Market Sentiment Agent** Aggregate retail trader sentiment — OANDA SSI, broker positioning ratios, fear/greed indices, VIX regime — to identify contrarian opportunities when the crowd is positioned to the extreme. |
| :-: | - |

#### **Data Sources**

- **OANDA Speculative Sentiment Index (SSI) — retail long/short ratios**

- **CBOE VIX index — fear gauge**

- **CNN Fear & Greed Index — multi-factor sentiment**

- **Put/Call ratios — options market positioning**

- **AAII Investor Survey — individual investor bullish/bearish readings**

#### **Capabilities**

- **Contrarian signal: \>75% retail long = potential reversal downward (SSI)**

- **VIX-S&P correlation trading: VIX \>25 = elevated fear → watch for reversal**

- **VIX EMA-20 crossover strategy (R2-001): trades VIX derivatives**

- **Fear & Greed composite: integrates price momentum, safe haven flows, junk bond demand**

#### **Registered Strategies**

| **ID** | **Strategy** | **Data Source** | **Signal Type** |
| - | - | - | - |
| R2-001 | VIX-EMA Crossover Strategy | VIX price + 20-EMA | Directional (VIX) |
| R2-002 | VIX-S&P 500 Correlation Strategy | VIX vs S&P inverse | Equity directional |
| R2-003 | VIX COT Report Sentiment Strategy | CFTC VIX futures | Extreme positioning |

#### **LLM Model**

**mistral:7b — sentiment aggregation and scoring**


| **10** | **News Sentiment & Event Risk Agent** Monitor, classify, and score news flow and economic calendar events using FinBERT NLP — generating event-risk flags, news sentiment scores, and high-impact blackout windows to protect open trades. |
| :-: | - |

#### **Data Sources**

- **NewsAPI — real-time financial news headlines**

- **Forex Factory JSON feed — economic calendar (replaces Investing.com scraper)**

- **FRED releases calendar — US data release dates (CPI, NFP, GDP)**

- **Reuters/Bloomberg RSS feeds — central bank communications**

#### **Capabilities**

- **FinBERT on-device NLP: bullish/bearish/neutral news sentiment scoring**

- **Economic impact classification: Low / Medium / High / Critical impact events**

- **Pre-event blackout: +/-15 minutes around high-impact releases — hard trade block**

- **Post-event directional bias: actual vs forecast deviation → momentum signal**

- **Currency-specific news score: aggregate sentiment per currency over 4h rolling window**

#### **Registered Strategies**

| **ID** | **Strategy** | **Trigger** | **Timeframe** |
| - | - | - | - |
| R2-015 | News Trading Strategy | Economic release deviation | Intraday |
| STRAT\_020 | Macro Event-Driven Trade | Central bank announcement | Event-based |
| STRAT\_025 | Central Bank Intervention Trading | CB jawboning / rate change | Event-based |
| **⛔ Hard Veto Rule** If Agent 10 detects a high-impact event within 15 minutes, Signal Fusion will return veto=True regardless of all other scores. No trade is executed during blackout windows. |

#### **LLM Model**

**mistral:7b — news classification (binary task — 7B is sufficient)**


| **DEPARTMENT 4  Intermarket Analysis** |
| - |


**The Intermarket Analysis department, inspired by John Murphy's foundational work, studies the relationships between bonds, equities, commodities, and currencies. It generates directional bias by identifying which asset classes are leading, which are lagging, and what the cross-asset flow implies for forex and commodity trades.**

| **11** | **Bond-Equity Intermarket Agent** Analyse the relationship between government bond yields, equity indices, and currency markets — tracking yield curve shape, credit spreads, and the dollar-bond relationship to derive macro regime signals. |
| :-: | - |

#### **Data Sources**

- **FRED API — US 2Y, 10Y, 30Y Treasury yields; yield curve spread (10Y-2Y)**

- **Polygon.io — TLT, IEF (bond ETFs), DXY price series**

- **CBOE — investment grade and high-yield credit spreads**

#### **Capabilities**

- **Yield curve regime: normal / flat / inverted — recession probability scoring**

- **Bond-equity correlation: rising rates + falling stocks = risk-off signal**

- **Dollar-yield correlation: rising DXY + yields → EM currency pressure**

- **Credit spread monitor: investment grade vs high yield divergence alert**

#### **Registered Strategies**

| **ID** | **Strategy** | **Signal** |
| - | - | - |
| STRAT\_022 | Bond Spreads as Leading Indicator | Credit spread → equity/FX directional bias |
| STRAT\_026 | Intermarket Analysis (Murphy) | Cross-asset regime classification |
| STRAT\_023 | Risk Reversals Strategy | Options market positioning signal |

#### **Skills**

- **intermarket-yield-curve · intermarket-credit-spreads · intermarket-dollar-yield**

#### **LLM Model**

**llama3.1:8b — intermarket narrative synthesis**


| **12** | **Commodity-Currency Intermarket Agent** Track the well-documented relationships between commodity prices and currency pairs — AUD/NZD with metals/agricultural, CAD with crude oil, NOK with Brent — to generate FX bias from commodity market moves. |
| :-: | - |

#### **Key Relationships Monitored**

| **Commodity** | **Currency Pair** | **Correlation** | **Typical Lead** |
| - | - | - | - |
| Gold (XAU) | AUD/USD, USD/CHF inverse | +0.7 to +0.85 | Simultaneous |
| Crude Oil (WTI) | USD/CAD inverse, NOK pairs | -0.75 to -0.90 | Oil leads 1–2 days |
| Iron Ore | AUD/USD | +0.65 to +0.80 | Iron leads 1 week |
| Copper | AUD/USD, risk appetite | +0.60 to +0.75 | Simultaneous |
| Agricultural | NZD/USD, BRL | +0.50 to +0.65 | Simultaneous |

#### **Registered Strategies**

| **ID** | **Strategy** | **Signal Type** |
| - | - | - |
| STRAT\_021 | Commodity Prices as Leading Indicator | FX directional bias from commodity divergence |
| STRAT\_026 | Intermarket Analysis | Commodity-FX divergence signal |

#### **LLM Model**

**mistral:7b — correlation calculation and divergence scoring**


| **13** | **Global Correlations & Regime Agent** Calculate and maintain the full cross-asset correlation matrix, identify risk-on vs risk-off regimes, detect correlation breakdowns that signal regime changes, and generate portfolio-level hedge recommendations. |
| :-: | - |

#### **Capabilities**

- **20-pair FX correlation matrix — updated every H4 candle close**

- **Risk-on / risk-off regime classification (VIX + DXY + Gold + Bonds)**

- **Correlation breakdown alert: pairs \>80% correlated → cap position overlap**

- **Sector rotation signals from cross-index relative strength**

- **Risk reversal pricing: options market implied direction (STRAT\_023, STRAT\_024)**

#### **Registered Strategies**

| **ID** | **Strategy** | **Application** |
| - | - | - |
| STRAT\_023 | Risk Reversals Strategy | Options market implied FX direction |
| STRAT\_024 | Option Volatility Timing | Implied vol expansion/contraction timing |
| STRAT\_026 | Intermarket Analysis | Full cross-asset regime signal |

#### **LLM Model**

**mistral:7b — regime classification and correlation matrix interpretation**


| **DEPARTMENT 5  Quantitative / Systematic Analysis** |
| - |


**The Quantitative/Systematic Analysis department applies mathematical and statistical methods to generate objective, emotion-free signals. It implements algorithmic execution strategies, statistical arbitrage, factor models, and the backtesting infrastructure. Its signals carry a 10% fusion weight but are critical for execution quality and position sizing.**

| **14** | **Statistical Arbitrage Agent** Identify and trade statistically cointegrated currency pairs and asset pairs — pairs trading, mean reversion spreads, and index arbitrage — using cointegration tests, Z-score monitoring, and Kalman filter dynamic hedging. |
| :-: | - |

#### **Methods**

- **Engle-Granger cointegration test — identify persistent pair relationships**

- **Johansen test — multivariate cointegration for basket trades**

- **Z-score entry: enter at Z \> ±2.0, exit at Z = 0, stop at Z \> ±3.5**

- **Kalman filter hedge ratio — dynamic beta adjustment as relationship evolves**

- **Pairs: EURUSD/GBPUSD, AUDUSD/NZDUSD, USDCAD/USDNOK, XAUUSD/XAGUSD**

#### **Registered Strategies**

| **ID** | **Strategy** | **Method** | **Timeframe** |
| - | - | - | - |
| R1-006 | Pairs Trading / Statistical Arbitrage | Cointegration Z-score | H1–D1 |
| R1-007 | Market Making / Auto Market Making | Bid-ask spread capture | M1–M5 |

#### **LLM Model**

**codellama:34b — generating cointegration analysis and dynamic hedging code**


| **15** | **Factor Model Agent** Apply systematic multi-factor models to rank currency pairs and asset classes — combining momentum, value (PPP deviation), carry, and quality factors into composite factor scores for medium-term positioning. |
| :-: | - |

#### **Factors Implemented**

| **Factor** | **Definition** | **Asset Class** | **Signal** |
| - | - | - | - |
| Momentum | 12-1 month return ranking | FX, Equities | Continuation |
| Value (PPP) | Deviation from purchasing power parity | FX | Mean reversion |
| Carry | Interest rate differential (annualised) | FX | Long high-yielder |
| Quality | Current account balance + fiscal deficit | FX | Fundamental strength |
| Low Volatility | 30-day realized vol ranking | FX, Equities | Risk-adjusted |
| Trend Strength | ADX percentile over 52 weeks | All | Regime filter |

#### **Registered Strategies**

| **ID** | **Strategy** | **Factor** |
| - | - | - |
| R1-013 | Multiple Time Frame Momentum Strategy | Momentum (multi-TF) |
| STRAT\_004 | Moving Average Crossover Signal | Momentum (price-based) |
| STRAT\_019 | Carry Trade Strategy | Carry factor |

#### **LLM Model**

**mistral:7b — factor scoring and composite ranking**


| **16** | **Algorithmic Execution Agent** Manage order execution quality using institutional execution algorithms — VWAP, TWAP, POV, Implementation Shortfall, Smart Order Routing — minimising market impact and slippage on all orders from the Signal Fusion layer. |
| :-: | - |

#### **Execution Algorithms**

| **Algorithm** | **Use Case** | **Key Parameter** |
| - | - | - |
| VWAP | Large orders aligned with volume profile | Historical volume curve (U-shaped) |
| TWAP | Uniform time slicing, low-liquidity markets | Trading horizon duration |
| POV / Participation Rate | Track % of live market volume | Target rate: 10–25% |
| Arrival Price | Minimize implementation shortfall from signal time | Risk aversion λ |
| Implementation Shortfall | Optimal trade-off: urgency vs market impact | Alpha decay rate |
| Smart Order Routing | Route child orders to best venue/price | Venue priority + rebates |

#### **Registered Strategies**

| **ID** | **Strategy** |
| - | - |
| R1-001 | VWAP Strategy — volume-weighted execution |
| R1-002 | TWAP Strategy — uniform time slicing |
| R1-003 | Percentage of Volume (POV) Strategy |
| R1-004 | Arrival Price Algorithm |
| R1-005 | Implementation Shortfall Algorithm |
| R1-010 | Smart Order Routing (SOR) |
| R1-019 | Trailing One-Bar High/Low Entry Trigger |
| R1-020 | Swing Breakout Entry Trigger |
| R1-021 | Two-Unit Trade Management (Multiple-Unit Exit) |

#### **LLM Model**

**None — pure Python execution math; no LLM required for order routing calculations**


| **17** | **Backtesting & Walk-Forward Agent** Run historical and walk-forward backtests on all registered strategies using vectorbt — producing performance metrics, drawdown analysis, parameter sensitivity, and live-vs-backtest comparison reports. |
| :-: | - |

#### **Backtesting Engine**

- **vectorbt — pandas-vectorised backtesting (millisecond speed, thousands of parameter combos)**

- **Supported timeframes: M15, H1, H4, D1 using OANDA historical data**

- **Walk-forward optimisation: in-sample / out-of-sample rolling windows**

- **Monte Carlo simulation: robustness testing with random trade sequence shuffling**

#### **Performance Metrics**

- **Win rate, profit factor, Sharpe ratio, Calmar ratio**

- **Maximum drawdown (absolute and %), recovery factor**

- **Average R:R achieved vs expected, expectancy per trade**

- **Best/worst months, session breakdown (Asian/London/NY)**

| **Performance Note** Agent 17 runs pure Python vectorbt calculations with zero LLM dependency — this makes it 10x faster than any LLM-assisted backtester. LLMs are used only to synthesise the narrative interpretation of backtest results. |
| - |


| **DEPARTMENT 6  SMC / ICT Analysis** |
| - |


**The SMC/ICT Analysis department implements the complete Inner Circle Trader Smart Money Concepts methodology — the highest-weight analytical layer at 40% in Signal Fusion. It reads institutional footprints in the market through order blocks, fair value gaps, liquidity sweeps, structure breaks, and kill zone timing to generate precision entry and exit levels.**

| **18** | **Order Blocks & Fair Value Gap Agent** Detect and track institutional order blocks and fair value gaps across all monitored pairs and timeframes — classifying their validity, calculating magnet strength, and generating limit entry orders at optimal retracement levels. |
| :-: | - |

#### **SMC Concepts Implemented**

| **Concept** | **Definition** | **Entry Logic** | **Timeframes** |
| - | - | - | - |
| Bullish Order Block | Last bearish candle before significant bullish move (100+ pips) | Limit long at 50–61.8% OB retracement | M15, H1, H4, D1 |
| Bearish Order Block | Last bullish candle before significant bearish move | Limit short at 50–61.8% OB retracement | M15, H1, H4, D1 |
| Bullish FVG | 3-candle imbalance: candle 3 low \> candle 1 high | Limit long at 50% gap fill | All TFs |
| Bearish FVG | 3-candle imbalance: candle 3 high \< candle 1 low | Limit short at 50% gap fill | All TFs |
| Mitigation Block | OB that has been partially tested — reduced validity | Reduce position size | H1, H4 |
| Breaker Block | Failed OB that flips: bearish OB becomes support | Aggressive entry with tight stop | H1, H4 |

#### **Python Package**

pip install smartmoneyconcepts  \# github.com/joshyattridge/smart-money-concepts

#### **Registered Strategies**

| **ID** | **Strategy** | **ICT Tier** | **Target Pips** |
| - | - | - | - |
| R1-030 / STRAT\_030 | Order Block Trading (ICT) | All tiers | 30–500 |
| R2-008 | Order Block Trading (extended) | Intraday + swing | 25–150 |
| R2-009 | Breaker Block Trading | Aggressive reversal | 30–80 |
| STRAT\_027 | Fair Value Gap Trading (ICT) | All tiers | 25–300 |
| R2-004 | Fair Value Gap Trading (extended) | Scalp + swing | 20–100 |
| ICT-02 | PD Array FVG Scalp | Scalping | 25 pips |
| ICT-08 | Discount-Premium Position | Position | 300–500 pips |

#### **LLM Model**

**codellama:34b — OB/FVG identification code generation and mitigation logic**


| **19** | **Market Structure Agent** Monitor and classify market structure across all timeframes — identifying Break of Structure (BOS), Change of Character (CHoCH), Market Structure Shift (MSS), and Higher High / Lower Low sequences — to establish trend direction and reversal probability. |
| :-: | - |

#### **Structure Concepts**

| **Concept** | **Trigger** | **Implication** | **Action** |
| - | - | - | - |
| BOS — Bullish | Price closes above prior swing high | Trend continuation long | Add to long bias |
| BOS — Bearish | Price closes below prior swing low | Trend continuation short | Add to short bias |
| CHoCH — Bullish | First BOS opposite to downtrend direction | Early reversal signal | Reduce short, watch for long |
| CHoCH — Bearish | First BOS opposite to uptrend direction | Early reversal signal | Reduce long, watch for short |
| MSS | Structure break on lower timeframe during HTF pullback | LTF entry trigger | Execute limit order |
| HH/HL sequence | Series of higher highs and higher lows | Confirmed uptrend | Bias long setups only |
| LH/LL sequence | Series of lower highs and lower lows | Confirmed downtrend | Bias short setups only |

#### **Registered Strategies**

| **ID** | **Strategy** | **ICT Tier** |
| - | - | - |
| STRAT\_028 | Break of Structure (ICT) | All tiers |
| STRAT\_029 | Change of Character (ICT) | All tiers |
| R2-005 | Break of Structure Trading (extended) | Short-term + swing |
| R2-006 | Change of Character (ChoCh) Reversal | Swing |
| R2-007 | Market Structure Shift (MSS) Reversal | Swing |
| ICT-05 | CHoCH Momentum Swing | Swing — 75–100 pips |
| ICT-07 | HTF Structure Break | Position — 200–300 pips |

#### **LLM Model**

**codellama:34b — structure detection algorithm generation for novel market conditions**


| **20** | **Liquidity Analysis Agent** Map institutional liquidity pools — equal highs/lows, buy-side and sell-side liquidity, stop hunt patterns, and the Power of Three (AMD) cycle — to anticipate where price will sweep before reversing. |
| :-: | - |

#### **Liquidity Concepts**

- **Buy-Side Liquidity (BSL): equal highs, previous day/week highs — where longs have stops**

- **Sell-Side Liquidity (SSL): equal lows, previous day/week lows — where shorts have stops**

- **Liquidity Grab / Stop Hunt: price sweeps beyond BSL/SSL then reverses (STRAT\_010)**

- **Power of Three (AMD): Accumulation → Manipulation (sweep) → Distribution (true move)**

- **Optimal Trade Entry (OTE): Fibonacci 0.62–0.79 retracement after displacement**

- **Premium zone: above equilibrium (0.5 fib) — sell setups only**

- **Discount zone: below equilibrium (0.5 fib) — buy setups only**

#### **Registered Strategies**

| **ID** | **Strategy** | **ICT Tier** | **Target** |
| - | - | - | - |
| R2-010 | Liquidity Grab / Stop Hunt Trading | Scalp + Short-term | 20–50 pips |
| R2-011 | Optimal Trade Entry (OTE) with Fibonacci | All tiers | 50–300 pips |
| R2-012 | Power of Three (AMD) Cycle Trading | Intraday + swing | 30–100 pips |
| R2-014 | Premium and Discount Zone Trading | All tiers | 30–200 pips |
| ICT-01 | Micro-Sweep Scalp | Scalping | 20 pips |
| ICT-06 | Sell-Side Redistribution Swing | Swing | 75–100 pips |

#### **LLM Model**

**codellama:34b — liquidity pool mapping code and AMD cycle detection**


| **21** | **Kill Zone & Session Agent** Manage time-based trading precision — identifying active ICT kill zones, session-specific liquidity conditions, BTMM three-day cycle positioning, and Silver Bullet setups — ensuring entries are timed to institutional activity windows. |
| :-: | - |

#### **Kill Zone Schedule**

| **Kill Zone** | **EST Time** | **UTC Time** | **Pairs / Focus** |
| - | - | - | - |
| Asian Kill Zone | 20:00–00:00 | 01:00–05:00 | JPY pairs, AUD/NZD pairs |
| London Open KZ | 03:00–05:00 | 08:00–10:00 | EUR, GBP, CHF pairs — highest probability |
| New York AM KZ | 07:00–10:00 | 12:00–15:00 | USD pairs — overlap with London |
| New York PM KZ | 13:30–16:00 | 18:30–21:00 | USD pairs — Afternoon NY session |
| London Close KZ | 10:00–12:00 | 15:00–17:00 | EUR, GBP — retracements common |
| Silver Bullet Long | 10:00–11:00 EST | 15:00–16:00 | 3-candle FVG setup — 30 pip target |
| Silver Bullet Short | 14:00–15:00 EST | 19:00–20:00 | 3-candle FVG setup — 30 pip target |

#### **Registered Strategies**

| **ID** | **Strategy** | **Session** |
| - | - | - |
| R2-013 | Killzone / Time-Based Trading | All kill zones |
| R2-028 | BTMM Three-Day Cycle Strategy | London + NY |
| ICT-03 | Kill-Zone Pulse (30–50 pip) | London Open, NY AM |
| ICT-04 | Weekly Bias Expansion (50 pip) | NY AM Tue/Wed |
| **Kill Zone Guard** Agent 21 issues a STANDBY flag outside active kill zones. The SMC pipeline (Agent 18/19/20) will only generate executable signals during valid kill zones, reducing false signals by ~40% and conserving API compute during dead sessions. |

#### **LLM Model**

**mistral:7b — session classification and BTMM cycle tracking**


# **2. Signal Fusion Layer**


**The Signal Fusion Layer is the most critical component added in v4. It sits between the six analysis departments and the risk manager, preventing any single agent from executing a trade in isolation. No trade enters the risk pipeline unless the composite confidence score meets threshold AND no hard veto is active.**

| **⚠️ Architecture Requirement** Signal Fusion is mandatory. If signal\_fusion.py is not running, all order endpoints on the REST API server will return 503. This cannot be bypassed. |
| - |

## **2.1 Department Weights**

| **Department** | **Agent(s)** | **Weight** | **Rationale** |
| - | - | - | - |
| SMC/ICT Analysis | 18–21 | 40% | Highest-precision institutional setups — primary entry logic |
| Technical Analysis | 05–07 | 25% | Confirms structure and momentum alignment |
| Fundamental Analysis | 01–04 | 20% | Macro regime and directional bias context |
| Sentiment Analysis | 08–10 | 10% | Positioning extremes and news risk flags |
| Intermarket Analysis | 11–13 | 3% | Cross-asset confirmation and regime overlay |
| Quantitative/Systematic | 14–17 | 2% | Factor scores and execution quality |

## **2.2 Fusion Logic**

\# signal\_fusion.py

@dataclass

class FusedSignal:

    symbol:               str

    direction:            str           \# LONG / SHORT / NEUTRAL

    composite\_confidence: float         \# 0.0 → 1.0

    smc\_score:            float         \# Agent 18-21 — weight: 0.40

    technical\_score:      float         \# Agent 05-07  — weight: 0.25

    fundamental\_score:    float         \# Agent 01-04  — weight: 0.20

    sentiment\_score:      float         \# Agent 08-10  — weight: 0.10

    intermarket\_score:    float         \# Agent 11-13  — weight: 0.03

    quant\_score:          float         \# Agent 14-17  — weight: 0.02

    components\_agreeing:  int           \# How many depts agree on direction

    veto\_active:          bool          \# Any agent veto = no trade

    veto\_reason:          str           \# Human-readable veto explanation


## **2.3 Hard Veto Rules**

| **Veto Trigger** | **Agent** | **Action** |
| - | - | - |
| High-impact news within 15 minutes | Agent 10 (News) | Block trade — wait for blackout to clear |
| Macro regime = STAGFLATION + direction = LONG | Agent 01 (Macro) | Block long — macro conflict |
| Daily drawdown \> 2.5% | Risk Manager | Halt all new trades for remainder of day |
| Open trades \>= 5 concurrent | Risk Manager | No new entries until a position closes |
| Spread \> 3x average | Risk Manager (spread gate) | Block trade — market conditions abnormal |
| Signal age \> 4 hours | Signal Fusion | Signal expires — discard and re-analyse |
| Composite confidence \< 0.75 | Signal Fusion | Below minimum threshold — no trade |
| Kill zone not active | Agent 21 (Session) | Standby — wait for next kill zone |

## **2.4 Minimum Trade Criteria**

**A trade signal passes Signal Fusion and enters the risk pipeline only when ALL of the following are satisfied:**

- **Composite confidence score ≥ 0.75**

- **SMC/ICT score ≥ 0.65 — primary engine must agree**

- **At least 3 of 6 departments agree on direction**

- **No veto\_active flags from any agent**

- **Active kill zone confirmed by Agent 21**

- **Market regime is TRENDING or TRANSITIONING (not RANGING for breakout strategies)**


# **3. Risk Management & Safety Gates**


## **3.1 Hard Risk Rules**

| **Rule** | **Value** | **Action on Breach** |
| - | - | - |
| Max risk per trade | 1% of account equity | Size capped — trade proceeds smaller |
| Max daily drawdown | 3% | Halt all trading — manual restart required |
| Max concurrent positions | 5 | New signals queued until a position closes |
| Max correlation overlap | 80% | Block — cannot open two positions \>80% correlated |
| Minimum R:R ratio | 1.5:1 | Setup rejected if TP/SL geometry \<1.5 |
| Pre-news block | 15 minutes before | No new entries during event window |
| Post-news block | 15 minutes after | No new entries — wait for spread normalisation |
| Max spread multiplier | 3x average | Block — execution quality compromised |
| Signal max age | 4 hours | Signal expires — discard, re-analyse required |
| Minimum confidence score | 0.75 | Below threshold — fusion rejects signal |
| Max monthly drawdown | 8% | Trading suspended — Telegram alert to operator |

## **3.2 Seven-Gate Risk Pipeline**

**Every signal from Signal Fusion passes through exactly 7 gates in order. The first gate that fails terminates evaluation immediately — later gates are not checked. Gates are sequenced from fastest-failing (binary checks) to most compute-intensive (position sizing math).**

| **Gate** | **Check** | **Fail = ?** |
| - | - | - |
| Gate 1 — Halt Check | Is trading halted? (daily DD, monthly DD, manual halt) | Immediate reject |
| Gate 2 — Drawdown Check | Current daily drawdown \< 3%? | Halt for day |
| Gate 3 — News Block | High-impact event within ±15 min? | Queue until clear |
| Gate 4 — Concurrent Trades | Open positions \< 5? | Queue until slot opens |
| Gate 5 — Correlation Check | New position \<80% correlated with existing? | Reject setup |
| Gate 6 — R:R Validation | TP/SL geometry achieves min 1.5:1 R:R? | Reject setup |
| Gate 7 — Spread Check | Current spread \< 3x average? (last check before order) | Reject — re-queue in 5 min |

## **3.3 Position Sizing**

def calculate\_position\_size(account\_equity, risk\_pct, sl\_pips, pip\_value):

    risk\_amount = account\_equity \* risk\_pct          \# e.g. 10000 \* 0.01 = $100

    position\_size = risk\_amount / (sl\_pips \* pip\_value)

    return round(position\_size, 2)                   \# Lots

## **3.4 Kill Switch**

\# Emergency stop — closes all positions, halts all agents

paperclipai org halt-all

ctrader positions close-all

vault kv put secret/trading/status mode=halted

\# Sends Telegram: ⛔ EMERGENCY HALT — all positions closed

## **3.5 Watchdog Process**

**The watchdog runs as an independent systemd service — separate from Paperclip, n8n, and the cTrader API server. If the main system goes offline for 30 minutes, it closes all positions autonomously and sends an alert.**

\# watchdog.py — systemd service independent of all other components

def watchdog\_loop():

    last\_heartbeat = time.time()

    while True:

        time.sleep(60)

        try:

            r = requests.get('http://localhost:9009/health', timeout=5)

            if r.status\_code == 200: last\_heartbeat = time.time()

        except: pass

        if time.time() - last\_heartbeat \> 1800:   \# 30 min offline

            ctrader.close\_all\_positions()

            telegram.send('⛔ WATCHDOG: 30min offline — all positions closed')


# **4. Market Regime Filter**


**The Market Regime Filter runs before any analytical department is invoked. SMC performs very differently in trending vs ranging markets — in low-ADX environments, order blocks get swept repeatedly with no follow-through. The regime filter prevents false signals by classifying market conditions and adjusting which strategies are eligible.**

## **4.1 Regime Classification**

def get\_market\_regime(ohlcv: pd.DataFrame) -\> str:

    adx      = calculate\_adx(ohlcv, period=14)

    atr\_ratio = calculate\_atr(ohlcv, 14) / ohlcv\['close'\].iloc\[-1\]

    bb\_width  = calculate\_bb\_width(ohlcv, 20, 2)


    if adx.iloc\[-1\] \> 25 and atr\_ratio \> 0.007:

        return 'TRENDING'       \# SMC OB + BOS setups — high probability

    elif adx.iloc\[-1\] \< 20 and bb\_width \< 0.015:

        return 'RANGING'        \# Mean reversion only — no breakout trades

    else:

        return 'TRANSITIONING'  \# Reduce position size, wait for clarity

## **4.2 Strategy Eligibility by Regime**

| **Regime** | **Eligible Strategies** | **Blocked Strategies** | **Position Size Modifier** |
| - | - | - | - |
| TRENDING | SMC OB/BOS, Breakout, Momentum, Trend Following, Kill Zone setups | Mean reversion, Range Trading | 100% (full size) |
| RANGING | Mean Reversion FVG fills, Bollinger Bands, Range Trading, Pairs Trading | All breakout + trend-following strategies | 75% (reduced) |
| TRANSITIONING | SMC FVG fills only, Conservative position entries | OB breakouts, Strong trend-following | 50% (wait for clarity) |


# **5. cTrader Live Execution**


## **5.1 Dual Connection Architecture**

**AgentFinance v4 uses a Docker REST API wrapper (port 9009) to isolate Twisted (cTrader's async framework) from the main Python asyncio application. This prevents reactor conflicts and allows the execution layer to be independently restarted without affecting analysis agents.**

| **Component** | **Tech** | **Port** | **Purpose** |
| - | - | - | - |
| ctrader\_api\_server.py | FastAPI + Twisted | 9009 | REST wrapper for all cTrader operations |
| Main application | Python asyncio | — | Analysis, fusion, risk pipeline |
| Docker container | Isolated process | — | Twisted reactor isolation |
| n8n webhook | HTTP POST | 5678 | Order trigger from workflow engine |

## **5.2 REST API Authentication**

| **⚠️ Security — Critical Before Live Trading** The REST API server MUST have authentication enabled before connecting to any live account. The demo account can run without auth for testing but live deployment requires API key on all /orders/\* endpoints. |
| - |

\# Add to ctrader\_api\_server.py

from fastapi.security import APIKeyHeader

from fastapi import Security, HTTPException


API\_KEY\_HEADER = APIKeyHeader(name='X-API-Key')


async def verify\_api\_key(api\_key: str = Security(API\_KEY\_HEADER)):

    if api\_key != os.getenv('REST\_API\_KEY'):

        raise HTTPException(status\_code=403, detail='Invalid API key')


\# Apply to all /orders/\* endpoints — leave /health and /status open

## **5.3 Position Management**

| **Event** | **Action** | **Trigger** |
| - | - | - |
| Entry | Market or limit order at OB/FVG zone | Signal Fusion → Risk Pipeline pass |
| TP1 hit (50% target) | Close 50% of position | Automatic via cTrader stop |
| After TP1 | Move SL to breakeven | Workflow node on TP1 confirmation |
| After breakeven | Activate trailing stop (15 pips) | trail\_stop() monitoring loop |
| TP2 hit (100% target) | Close remaining 50% | Automatic via cTrader stop |
| Stop Loss hit | Full position closed | Automatic via cTrader stop |
| Daily DD 3% | Close all positions — halt trading | Risk gate emergency stop |

## **5.4 Trailing Stop Logic**

def trail\_stop(position, current\_price, trail\_pips=15):

    '''Trail stop after TP1 — keep 15 pips behind price.'''

    if position.tp1\_hit and position.sl\_at\_breakeven:

        if position.direction == 'BUY':

            new\_sl = current\_price - (trail\_pips \* pip\_size)

            if new\_sl \> position.current\_sl:

                amend\_position(position.id, new\_sl=new\_sl)

        else:

            new\_sl = current\_price + (trail\_pips \* pip\_size)

            if new\_sl \< position.current\_sl:

                amend\_position(position.id, new\_sl=new\_sl)


# **6. n8n Workflow Blueprints**


**n8n serves as the orchestration layer — triggering analysis cycles, executing trades, managing positions, and distributing intelligence. All workflows are imported as JSON and run on the self-hosted n8n instance at port 5678.**

## **6.1 Core Trading Workflows**

| **Workflow** | **Trigger** | **Key Nodes** | **Output** |
| - | - | - | - |
| workflow\_market\_scan.json | Cron: every 15 min during sessions | Regime filter → 6 dept analysis → Signal Fusion → Risk gates → cTrader order | Trade execution + Telegram signal alert |
| workflow\_position\_monitor.json | Cron: every 5 min | Check open positions → TP1 hit? → Move SL → Trail stop activation | Position amendments via cTrader API |
| workflow\_economic\_calendar.json | Cron: daily 06:00 UTC | Fetch FF JSON → Parse events → Store in Supabase → Alert upcoming high-impact | Telegram daily calendar digest |
| workflow\_daily\_briefing.json | Cron: 07:00 UTC daily | COT data → Macro check → Regime check → Compile briefing → Notion save | Telegram morning briefing |
| workflow\_weekly\_performance.json | Cron: Sunday 18:00 UTC | Pull closed trades → Calculate metrics → Strategy breakdown → Live vs backtest | Telegram weekly P&L + Notion journal |
| workflow\_watchdog.json | systemd service | Heartbeat check every 60s → 30-min offline threshold → Close all positions | Emergency Telegram alert + position closure |

## **6.2 Economic Calendar — Forex Factory JSON**

**The Investing.com scraper is replaced with the Forex Factory JSON feed — free, reliable, machine-readable, and stable for years:**

import feedparser


\# Forex Factory JSON calendar — free, no registration required

url = 'https://nfs.faireconomy.media/ff\_calendar\_thisweek.json'

calendar = requests.get(url).json()

\# Returns: date, time, currency, event, impact, forecast, previous


\# Filter high-impact events

high\_impact = \[e for e in calendar if e\['impact'\] == 'High'\]


# **7. Data Sources & API Configuration**


## **7.1 Data Source Map**

| **Asset Class** | **OHLCV Data** | **Fundamentals** | **Sentiment** | **News** |
| - | - | - | - | - |
| Forex | OANDA API (WebSocket) | Central bank websites, CFTC COT | OANDA SSI, CFTC positioning | NewsAPI, FF Calendar |
| Commodities | Polygon.io | EIA, USDA WASDE, World Bank | CFTC COT | NewsAPI |
| Indices | Polygon.io | FRED (VIX, A/D ratio) | CBOE put/call ratios | NewsAPI |
| Equities | Polygon.io | Financial MCP Server (SEC) | SEC filings, COT data | Earnings calendar |
| Crypto | Financial MCP | On-chain analytics | Crypto Fear & Greed Index | NewsAPI |

## **7.2 Redis Caching Strategy**

**Redis is installed in the base setup and is now actively used. The caching layer reduces API calls by approximately 85% per 15-minute analysis cycle across all 20+ monitored pairs.**

| **Data Type** | **Cache TTL** | **Key Pattern** | **Rationale** |
| - | - | - | - |
| M15 OHLCV | 2 minutes | ohlcv:\{symbol\}:M15 | New candle every 15 min — 2 min is safe |
| H1 OHLCV | 10 minutes | ohlcv:\{symbol\}:H1 | Candle doesn't change within the hour |
| H4 OHLCV | 10 minutes | ohlcv:\{symbol\}:H4 | H4 data is very stable mid-candle |
| D1 OHLCV | 60 minutes | ohlcv:\{symbol\}:D1 | Daily data — safe to cache for 1 hour |
| COT report | 7 days | cot:\{symbol\}:weekly | Released weekly — immutable once released |
| SMC analysis | 15 minutes | smc:\{symbol\}:\{tf\} | Avoid re-computation within scan cycle |
| News sentiment | 5 minutes | news:\{currency\}:sentiment | News changes frequently |
| Correlation matrix | 4 hours | correlation:matrix | Correlations are stable intraday |

## **7.3 Data Fetcher Structure**

**The monolithic data\_fetcher.py has been split into a thin orchestrator and four source modules — each independently testable and replaceable:**

| **Module** | **Lines** | **Responsibility** |
| - | - | - |
| data\_fetcher.py | ~150 | Thin orchestrator — dispatches to source modules, manages Redis cache |
| sources/oanda\_client.py | ~300 | All OANDA REST + WebSocket logic, session management |
| sources/polygon\_client.py | ~250 | All Polygon.io REST logic, ticker normalisation |
| sources/fred\_client.py | ~200 | FRED API + COT report parsing + economic calendar |
| sources/news\_client.py | ~200 | NewsAPI + Forex Factory JSON + FinBERT NLP pipeline |
| sources/cache.py | ~100 | Redis TTL caching layer — get/set/invalidate |

## **7.4 API Keys — Vault Configuration**

\# Store all trading API keys in Vault

vault kv put secret/trading/apis \\

  polygon-key=YOUR\_KEY \\

  oanda-api=YOUR\_KEY \\

  oanda-account=YOUR\_ACCOUNT \\

  newsapi-key=YOUR\_KEY \\

  fred-api-key=YOUR\_KEY \\

  tradingeconomics-key=YOUR\_KEY \\

  rest-api-key=YOUR\_KEY         \# For ctrader\_api\_server.py auth


# **8. Installation on Kali Linux**


## **8.1 LLM Model Assignments by Agent**

**Model selection is right-sized per agent type — CodeLLama 34B only for agents that generate Python/analysis code; lightweight models for classification and scoring tasks:**

| **Agent** | **Name** | **Model** | **Reason** |
| - | - | - | - |
| 01 | Macro Economics | llama3.1:8b | Economic analysis and narrative prose |
| 02 | Forex Fundamentals | llama3.1:8b | CB policy synthesis and scoring |
| 03 | Commodities Fundamental | mistral:7b | Scoring task — 7B sufficient |
| 04 | Equity Fundamentals | llama3.1:8b | Financial statement analysis |
| 05 | Price Action & Patterns | codellama:34b | Pattern detection code generation |
| 06 | Indicator-Based Analysis | mistral:7b | Rule-based scoring — no complex code |
| 07 | Trend Analysis | llama3.1:8b | Elliott Wave narrative interpretation |
| 08 | COT Positioning | mistral:7b | Data parsing and percentile scoring |
| 09 | Market Sentiment | mistral:7b | Sentiment aggregation — binary scoring |
| 10 | News Sentiment & Events | mistral:7b | News classification — binary task |
| 11 | Bond-Equity Intermarket | llama3.1:8b | Intermarket narrative synthesis |
| 12 | Commodity-Currency | mistral:7b | Correlation scoring task |
| 13 | Global Correlations | mistral:7b | Regime classification task |
| 14 | Statistical Arbitrage | codellama:34b | Cointegration + dynamic hedging code |
| 15 | Factor Model | mistral:7b | Factor scoring and composite ranking |
| 16 | Algorithmic Execution | None (pure Python) | Order routing math — no LLM needed |
| 17 | Backtesting & Walk-Forward | None (pure Python) | Vectorbt calculations — no LLM needed |
| 18 | Order Blocks & FVG | codellama:34b | OB/FVG identification code generation |
| 19 | Market Structure | codellama:34b | BOS/CHoCH detection algorithm generation |
| 20 | Liquidity Analysis | codellama:34b | Liquidity pool mapping code |
| 21 | Kill Zone & Session | mistral:7b | Session classification and cycle tracking |

## **8.2 Full v4 Installation Script**

\#!/bin/bash

\# install-agentfinance-v4.sh

echo '=== AgentFinance v4 Installation ==='


\# 1. Core dependencies

sudo apt update && sudo apt install -y \\

  golang-go python3-pip python3-venv git curl \\

  redis-server postgresql-client jq systemd


\# 2. Python environment

python3 -m venv ~/agency/trading/venv

source ~/agency/trading/venv/bin/activate


pip install \\

  smartmoneyconcepts \\

  pandas numpy scipy statsmodels \\

  vectorbt ta-lib \\

  requests aiohttp websockets \\

  ctrader-open-api \\

  redis feedparser \\

  transformers torch          \# FinBERT on-device NLP


\# 3. Go indicator library (cinar/indicator — 80+ indicators)

git clone https://github.com/cinar/indicator ~/agency/indicator

cd ~/agency/indicator && go build -o ~/agency/bin/indicator ./cmd/...


\# 4. Verify SMC package

python3 -c "from smartmoneyconcepts import smc; print('SMC package ready')"


\# 5. Redis — enable and start

sudo systemctl enable redis-server && sudo systemctl start redis-server


\# 6. Install Paperclip agents

cp ~/agency/v4/agents/\*.yaml ~/agency/paperclip/agents/


\# 7. Install watchdog as systemd service

cp ~/agency/v4/watchdog.service /etc/systemd/system/

sudo systemctl enable agentfinance-watchdog

sudo systemctl start agentfinance-watchdog


\# 8. n8n — import v4 workflows via UI at http://localhost:5678


echo '=== v4 Installation Complete ==='

echo '21 agents | 6 departments | Signal Fusion | Watchdog active'


# **9. Strategy Registry Summary**


**79 trading strategies have been formally extracted from source documents, classified by taxonomy, and mapped to the analytical department responsible for their signal generation. Each strategy includes full signal specification, risk management details, and independence assessment.**

## **9.1 Registry Sources**

| **Registry** | **Source Books / Documents** | **Strategies** |
| - | - | - |
| Registry 1 | Harry Boxer, Kathy Lien, John Murphy, ICT/SMC documents, Price Action, News Trading | 30 strategies |
| Registry 2 | Algorithmic Trading Methods (Kissell), High Probability Trading Strategies (Miner) | 21 strategies |
| Registry 3 | VIX Trading, SMC/ICT extended, Price Action Patterns, BTMM, Intraday Strategies | 28 strategies |

## **9.2 Strategy Distribution by Department**

| **Department** | **\# Strategies** | **Primary Strategy Types** |
| - | - | - |
| Fundamental Analysis (Dept 1) | 10 | Carry Trade, Macro Event, CB Intervention, Bond Spreads, Pairing Strong/Weak |
| Technical Analysis (Dept 2) | 22 | MA Crossover, MACD, Bollinger, Divergence, Patterns, Elliott Wave, MTF |
| Sentiment Analysis (Dept 3) | 8 | VIX strategies, COT Sentiment, News Trading, Fear & Greed |
| Intermarket Analysis (Dept 4) | 6 | Intermarket Analysis, Commodity Leading Indicator, Risk Reversals, Option Vol |
| Quantitative/Systematic (Dept 5) | 21 | VWAP, TWAP, POV, IS, SOR, Stat Arb, Pairs Trading, Market Making, Factor |
| SMC/ICT Analysis (Dept 6) | 12 | Order Blocks, FVG, BOS, CHoCH, MSS, Liquidity Grab, AMD, OTE, Kill Zones, BTMM |

## **9.3 ICT Strategy Tier Map**

| **ICT Strategy** | **Tier** | **Target** | **Holding Period** | **Win Rate (est.)** |
| - | - | - | - | - |
| ICT-01 — Micro-Sweep Scalp | Scalping | 20 pips | Intraday | 55–65% |
| ICT-02 — PD Array FVG Scalp | Scalping | 25 pips | Intraday | 55–65% |
| ICT-03 — Kill-Zone Pulse | Short-term | 30–50 pips | 1–3 days | 58–65% |
| ICT-04 — Weekly Bias Expansion | Short-term | 50 pips | 2–5 days | 58–65% |
| ICT-05 — CHoCH Momentum Swing | Swing | 75–100 pips | 2–5 days | 60–68% |
| ICT-06 — Sell-Side Redistribution | Swing | 75–100 pips | 2–7 days | 60–68% |
| ICT-07 — HTF Structure Break | Position | 200–300 pips | 1–4 weeks | 62–72% |
| ICT-08 — Discount-Premium Position | Position | 300–500 pips | 2–8 weeks | 62–72% |

## **9.4 Strategy Taxonomy Classification**

**Every strategy in all three registries is classified across 7 dimensions. The taxonomy ensures that signals from different departments can be combined in the Fusion Layer without double-counting correlated signals from strategies that share the same underlying logic.**

| **Dimension** | **Values** |
| - | - |
| Philosophy | Fundamental / Technical / Quantitative / Behavioral / Risk-Based |
| Time Horizon | Ultra-Short / Short / Medium / Long / Permanent |
| Data Source | Price & Volume / Fundamental / Macro / Alternative / Order Book / Sentiment |
| Directional Exposure | Long-Only / Short-Only / Long-Short / Market Neutral / Relative Value |
| Decision Process | Discretionary / Systematic / Model-Driven / Hybrid (Quantamental) |
| Asset Class | Equities / Fixed Income / Commodities / FX / Options / Crypto |
| Risk Management | Stop-Loss Based / Position Sizing / Hedging / Diversification |


# **10. Dashboard & Monitoring**


**The React/Vite dashboard has been extended from 7 to 8 tabs, adding a Performance tab with an equity curve — the single most important visual for assessing whether the system is generating alpha over time.**

## **10.1 Dashboard Tabs**

| **Tab** | **Content** | **Data Source** |
| - | - | - |
| 1 — Overview | System status, regime, active positions count, daily P&L | Supabase + cTrader API |
| 2 — Signals | Live signal feed from all 6 departments + fusion score | Redis signal cache |
| 3 — Positions | Open positions, current P&L, SL/TP levels, trailing stop status | cTrader API |
| 4 — Analysis | Department-by-department score breakdown per pair | Signal Fusion output |
| 5 — Regime | Current ADX, ATR, BB Width, regime classification per pair | Market Regime Filter |
| 6 — Strategy | Active strategy breakdown, which ICT tier is running | Signal Fusion metadata |
| 7 — Feed | Telegram-style chronological alert feed | n8n webhook events |
| 8 — Performance | Equity curve, drawdown chart, win rate, profit factor, Sharpe ratio | Supabase trade log |

## **10.2 Equity Curve Component**

// Recharts equity curve — data from Supabase trade log

import \{ LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine \} from 'recharts';


function EquityCurve(\{ trades \}) \{

  const curve = trades.reduce((acc, t) =\> \{

    const prev = acc\[acc.length - 1\]?.equity ?? 10000;

    acc.push(\{ date: t.close\_time, equity: prev + t.pnl \});

    return acc;

  \}, \[\]);


  return (

    \<LineChart data=\{curve\} width=\{800\} height=\{300\}\>

      \<Line dataKey='equity' stroke='\#22C984' dot=\{false\} strokeWidth=\{1.5\} /\>

      \<ReferenceLine y=\{10000\} stroke='\#384A62' strokeDasharray='4 4' /\>

      \<XAxis dataKey='date' /\>\<YAxis /\>\<Tooltip /\>

    \</LineChart\>

  );

\}


# **11. Enhancement Roadmap**


| **Phase** | **Items** | **Timeline** |
| - | - | - |
| Phase 1 — v4.0 (Now) | Deploy all 21 agents · Install SMC + indicator engines · Configure cTrader demo · Activate Signal Fusion · Enable Redis caching · Deploy watchdog | Immediate |
| Phase 2 — v4.1 | Multi-TF live dashboard with regime overlay · Alert consolidation ranking by quality · Auto-journal: every trade documented with entry reasoning | 4–6 weeks |
| Phase 3 — v4.2 | ML signal filter: XGBoost trained on historical fusion scores · Portfolio optimiser: Kelly Criterion + correlation-adjusted sizing · Multi-broker: IBKR for equities | 8–12 weeks |
| Phase 4 — v4.3 | Adaptive parameters: agents auto-adjust based on recent performance · Walk-forward re-optimisation every 4 weeks · Full Swahili language support for Telegram alerts | 16+ weeks |

## **11.1 Improvements Priority Summary**

| **\#** | **Improvement** | **Impact** | **Status** |
| - | - | - | - |
| 1 | Signal Fusion Layer (6-department confluence) | Trading edge — very high | v4.0 — build now |
| 2 | REST API authentication on /orders/\* | Security — critical before live | v4.0 — implement now |
| 3 | Redis OHLCV caching (85% call reduction) | Reliability, cost savings | v4.0 — activate now |
| 4 | Market Regime Filter (ADX/ATR/BB) | Signal quality uplift | v4.0 — implement now |
| 5 | Watchdog systemd service | Position safety | v4.0 — deploy now |
| 6 | Right-sized LLM models per agent | Speed + resource efficiency | v4.0 — config update |
| 7 | Split data\_fetcher.py into 4 modules | Maintainability | v4.1 |
| 8 | Equity curve dashboard tab | P&L visibility | v4.0 — quick win |
| 9 | FF JSON calendar replaces Investing.com | Reliability | v4.0 — quick win |
| 10 | Trailing stop after TP1 (15-pip trail) | Profit capture | v4.0 — implement |
| 11 | Prose agent model upgrade (llama3.1:70b if VRAM allows) | Analysis quality | v4.1 |
| 12 | XGBoost fusion score filter (trained on historical signals) | False positive reduction | v4.2 |
