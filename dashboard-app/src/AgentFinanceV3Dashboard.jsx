import { useState, useEffect } from "react";

/* ─── DESIGN TOKENS ─────────────────────────────────────────────────────────── */
const T = {
  bg:        "#07080D",
  surface:   "#0D0F1A",
  card:      "#111422",
  cardHov:   "#151929",
  border:    "rgba(255,255,255,0.07)",
  borderLt:  "rgba(255,255,255,0.13)",
  gold:      "#C9A84C",
  goldLt:    "#E2C47A",
  goldDim:   "rgba(201,168,76,0.14)",
  green:     "#22C984",
  greenDim:  "rgba(34,201,132,0.11)",
  blue:      "#4A8FFF",
  blueDim:   "rgba(74,143,255,0.11)",
  red:       "#FF4B6B",
  redDim:    "rgba(255,75,107,0.11)",
  amber:     "#F59E0B",
  amberDim:  "rgba(245,158,11,0.11)",
  purple:    "#A78BFA",
  purpleDim: "rgba(167,139,250,0.11)",
  cyan:      "#22D3EE",
  cyanDim:   "rgba(34,211,238,0.11)",
  txt:       "#E8ECF4",
  txtMid:    "#8B93A8",
  txtDim:    "#4A5168",
  mono:      "'JetBrains Mono','Fira Code','Cascadia Code',monospace",
  sans:      "'DM Sans','Mona Sans',system-ui,sans-serif",
  serif:     "'Fraunces','Playfair Display',Georgia,serif",
};

const DEPTS = [
  { id:"public",  label:"Public markets",  color:T.blue,   dim:T.blueDim,   icon:"◈" },
  { id:"private", label:"Private markets", color:T.green,  dim:T.greenDim,  icon:"◉" },
  { id:"research",label:"Research",        color:T.amber,  dim:T.amberDim,  icon:"◎" },
  { id:"ops",     label:"Operations",      color:T.purple, dim:T.purpleDim, icon:"◆" },
  { id:"asset",   label:"Asset classes",  color:T.cyan,   dim:T.cyanDim,   icon:"◇" },
  { id:"strategy",label:"Strategy engine", color:T.gold,   dim:T.goldDim,   icon:"◐" },
  { id:"automation",label:"Automation",    color:T.red,    dim:T.redDim,    icon:"◒" },
];

/* ─── V3 AGENT DATA ─────────────────────────────────────────────────────────── */
const AGENTS = [
  // Department 1: Public Markets (01-06)
  {id:1,  dept:"public",    num:"01", name:"SEC filings analyst",          role:"Regulatory filing intelligence",          skill:"sec-analyst-master",      skills:16, status:"active",  runs:34,   last:"2m",  tags:["10-K","10-Q","8-K","S-1","covenants"],              cmds:["/sec:10k","/sec:10q","/sec:8k","/sec:s1","/sec:covenant"],      mission:"Citation-rich analysis of all SEC filings — risk factors, MDA narratives, debt covenants, and governance quality for any public company."},
  {id:2,  dept:"public",    num:"02", name:"Transcripts analyst",          role:"Earnings call intelligence",              skill:"earnings-analyst-master",  skills:14, status:"active",  runs:18,   last:"8m",  tags:["guidance","sentiment","Q&A","management"],           cmds:["/transcript:full","/transcript:guidance","/transcript:sentiment"], mission:"Maximum intelligence from every earnings call — guidance, tone scoring, analyst concerns, and forward-looking signals within 15 min of publication."},
  {id:3,  dept:"public",    num:"03", name:"Stock data analyst",           role:"Market data & pricing intelligence",      skill:"market-analyst-master",    skills:19, status:"active",  runs:287,  last:"30s", tags:["quotes","returns","targets","FX","commod."],           cmds:["/stock:quote","/stock:returns","/stock:targets","/stock:fx"],    mission:"Real-time market data across equities, indices, commodities, FX, and prediction markets — the always-on pricing layer feeding all investment decisions."},
  {id:4,  dept:"public",    num:"04", name:"Financials analyst",           role:"Financial statements deep-dive",            skill:"financial-analyst-master", skills:17, status:"active",  runs:41,   last:"12m", tags:["income","balance sheet","cash flow","ESG"],            cmds:["/fin:income","/fin:balance","/fin:cashflow","/fin:health"],     mission:"Institutional-grade financial statement analysis — income statements, balance sheets, cash flows, health scores, ESG ratings for any public company."},
  {id:5,  dept:"public",    num:"05", name:"Holdings intelligence",        role:"Institutional ownership analysis",          skill:"market-analyst-master",   skills:4,  status:"idle",   runs:9,    last:"4h",  tags:["13-F","activist","crowding","smart money"],           cmds:["/holdings:top","/holdings:changes","/holdings:activist"],       mission:"Track institutional ownership dynamics — who is buying, selling, activist accumulation signals, and smart-money flow for any public equity."},
  {id:6,  dept:"public",    num:"06", name:"Crypto market analyst",         role:"Cryptocurrency market intelligence",       skill:"market-analyst-master",   skills:5,  status:"active",  runs:96,   last:"15m", tags:["BTC","ETH","DeFi","dominance","on-chain"],           cmds:["/crypto:prices","/crypto:btc","/crypto:defi","/crypto:dominance"], mission:"Institutional cryptocurrency market intelligence — prices, market structure, BTC dominance, DeFi TVL, and macro correlation analysis."},
  // Department 2: Private Markets (07-12)
  {id:7,  dept:"private",   num:"07", name:"Private companies analyst",    role:"Private company research",                 skill:"financial-analyst-master",skills:4,  status:"active",  runs:13,   last:"22m", tags:["firmographics","revenue","tech stack"],               cmds:["/private:tearsheet","/private:competitors","/private:team"],    mission:"Research private company targets — firmographics, revenue estimates, technology stack, executive team, and competitive landscape for investment or acquisition."},
  {id:8,  dept:"private",   num:"08", name:"Funding intelligence",         role:"VC & PE funding analysis",                 skill:"financial-growth",        skills:3,  status:"active",  runs:28,   last:"1h",  tags:["rounds","investors","valuation","runway"],            cmds:["/funding:history","/funding:rounds","/funding:investors"],      mission:"Track and analyse private company funding — round history, investor mapping, valuation step-ups, runway estimates, and sector trend analysis."},
  {id:9,  dept:"private",   num:"09", name:"Private funds analyst",         role:"Fund manager due diligence",               skill:"financial-analyst-master",skills:4,  status:"idle",   runs:4,    last:"6h",  tags:["IRR","TVPI","strategy","LP base"],                  cmds:["/funds:profile","/funds:performance","/funds:compare"],       mission:"Research PE, VC, hedge funds, and credit managers — fund strategy, AUM, track record, team composition, and LP base for manager due diligence."},
  {id:10, dept:"private",   num:"10", name:"Deals intelligence",            role:"M&A, IPO & transaction analytics",         skill:"sec-analyst-master",      skills:5,  status:"active",  runs:19,   last:"45m", tags:["M&A","IPO","S-1","comps","multiples"],              cmds:["/deals:ma","/deals:ipo","/deals:comps","/deals:multiples"],   mission:"Comprehensive M&A and capital markets transaction intelligence — deal flow, multiples, IPO pipeline, precedent transactions, and acquirer strategy."},
  {id:11, dept:"private",   num:"11", name:"Investors intelligence",       role:"Investor profiling & networks",            skill:"market-analyst-master",  skills:4,  status:"idle",   runs:7,    last:"3h",  tags:["GP profile","portfolio","active sectors"],            cmds:["/investors:profile","/investors:portfolio","/investors:active"], mission:"Comprehensive intelligence on investors — mandate, portfolio overlap, deal history, key personnel, and relationship mapping for co-investment and fundraising."},
  {id:12, dept:"private",   num:"12", name:"Private debt analyst",         role:"Credit & direct lending intelligence",     skill:"sec-debt-covenant",      skills:5,  status:"idle",   runs:3,    last:"8h",  tags:["covenants","maturity wall","Z-score"],                cmds:["/debt:borrower","/debt:covenants","/debt:credit-score"],    mission:"Analyse private credit markets — direct lending, leveraged loans, covenants, maturity walls, and borrower credit quality for credit investment decisions."},
  // Department 3: Research (13-14)
  {id:13, dept:"research",  num:"13", name:"Web intelligence agent",       role:"Structured web data extraction",           skill:"earnings-competitive-review",skills:3,status:"active",runs:52, last:"18m", tags:["hiring","pricing","press","regulatory"],              cmds:["/scrape:company","/scrape:jobs","/scrape:pricing"],          mission:"Extract structured intelligence from public websites — job postings as growth signals, pricing intelligence, product announcements, regulatory filings."},
  {id:14, dept:"research",  num:"14", name:"Deep research agent",           role:"Multi-source synthesis — all 66+ skills",  skill:"All v2+v3 masters",       skills:93, status:"running",runs:2,   last:"now", tags:["initiation","thesis","bull/bear","DCF"],               cmds:["/research:full","/research:thesis","/research:bull","/research:valuation"], mission:"Full-spectrum institutional research by orchestrating all agents — SEC, earnings, financials, market data, private + web synthesised into IC-grade reports."},
  // Department 7: Operations (15-18)
  {id:15, dept:"ops",       num:"15", name:"Portfolio monitor",            role:"Real-time portfolio risk & alerts",        skill:"market-analyst-master",   skills:5,  status:"active",  runs:1840, last:"30s", tags:["P&L","risk","beta","VaR","catalysts"],              cmds:["/portfolio:status","/portfolio:pnl","/portfolio:risk"],      mission:"24/7 monitoring of all portfolio positions — price moves, earnings surprises, rating changes, financial health signals, and catalyst tracking."},
  {id:16, dept:"ops",       num:"16", name:"Investment report writer",    role:"Institutional research report authoring",  skill:"All v2+v3 masters",       skills:93, status:"active",  runs:5,    last:"35m", tags:["initiation","earnings note","IC memo"],               cmds:["/report:initiation","/report:earnings-note","/report:ic-memo"], mission:"Goldman Sachs-style institutional research — initiations of coverage, earnings notes, investment committee memos, and sector primers."},
  {id:17, dept:"ops",       num:"17", name:"Compliance monitor",          role:"Investment compliance & governance",        skill:"sec-risk-factors",        skills:4,  status:"active",  runs:288,  last:"5m",  tags:["13-F","5% trigger","ESG","position limits"],         cmds:["/comply:positions","/comply:13f","/comply:5pct-watch"],     mission:"Continuous investment compliance — position limits, insider restrictions, 13-F obligations, 5% filing triggers, ESG mandates, and breach prevention."},
  {id:18, dept:"ops",       num:"18", name:"Finance intelligence supervisor",role:"Chief orchestrator — all 28 agents",   skill:"All v2+v3 masters",       skills:93, status:"active",  runs:144,  last:"1m",  tags:["briefing","IC pipeline","orchestration"],             cmds:["/intel:briefing","/intel:status","/intel:priorities"],      mission:"Orchestrate all 28 agents — morning briefings, research workflows, IC agenda management, portfolio targets, and highest-conviction opportunity identification."},
  // Department 4: Asset Class Intelligence (19-21)
  {id:19, dept:"asset",     num:"19", name:"Forex intelligence agent",    role:"FX market analysis & kill zone timing",   skill:"forex-smc",              skills:9,  status:"active",  runs:52,   last:"2m",  tags:["EURUSD","GBPUSD","USDJPY","kill zones","COT"],      cmds:["/fx:scan","/fx:kill-zones","/fx:cot","/fx:pairs"],           mission:"Institutional-grade forex analysis — SMC structure, kill zone timing, COT positioning, and central bank divergence for 28 major/minor pairs."},
  {id:20, dept:"asset",     num:"20", name:"Commodities intelligence agent",role:"Precious metals, energy, agriculture",     skill:"commodities-smc",        skills:9,  status:"active",  runs:31,   last:"5m",  tags:["XAUUSD","WTI","natural gas","EIA","WASDE"],         cmds:["/commod:gold","/commod:oil","/commod:seasonality","/commod:report"], mission:"Analyse all commodity markets — supply/demand fundamentals, seasonality, COT, geopolitics, and SMC structure for directional trade setups."},
  {id:21, dept:"asset",     num:"21", name:"Indices intelligence agent",    role:"Global equity indices & breadth analysis", skill:"indices-breadth",        skills:9,  status:"active",  runs:28,   last:"3m",  tags:["SPX","NDX","VIX","breadth","sectors"],             cmds:["/index:spx","/index:breadth","/index:vix","/index:sectors"], mission:"Monitor and analyse all major global equity indices — SMC structure, market breadth, VIX regime, sector rotation, and macro regime for directional bias."},
  // Department 5: Trading Strategy Engine (22-26)
  {id:22, dept:"strategy",  num:"22", name:"SMC strategy agent",           role:"Smart Money Concepts — order blocks, FVGs, BOS/CHoCH", skill:"smc-confluence",  skills:9,  status:"active",  runs:89,   last:"1m",  tags:["order blocks","FVGs","BOS","CHoCH","liquidity"],     cmds:["/smc:scan","/smc:ob","/smc:fvg","/smc:kill-zones","/smc:report"], mission:"Apply complete ICT/SMC methodology across all instruments — order blocks, fair value gaps, break of structure, change of character, liquidity sweeps, and kill zone timing for high-probability setups."},
  {id:23, dept:"strategy",  num:"23", name:"Technical analysis agent",    role:"80+ indicators — trend, momentum, volume",  skill:"tech-confluence",        skills:9,  status:"active",  runs:67,   last:"2m",  tags:["RSI","MACD","Bollinger","Ichimoku","ADX"],         cmds:["/tech:scan","/tech:rsi","/tech:macd","/tech:bb","/tech:report"], mission:"Apply 80+ technical indicators across all monitored instruments — trend, momentum, volatility, and volume signals for quantitative trade confirmation."},
  {id:24, dept:"strategy",  num:"24", name:"Fundamental analysis agent",   role:"Macro regime, central banks, economic data",skill:"fundamental-regime",    skills:3,  status:"active",  runs:24,   last:"10m", tags:["CPI","NFP","Fed","ECB","GDP","PMI"],               cmds:["/macro:regime","/macro:calendar","/macro:rates","/macro:report"], mission:"Monitor and interpret macroeconomic data releases — interest rates, inflation, employment, GDP, and central bank communications that drive asset class direction."},
  {id:25, dept:"strategy",  num:"25", name:"Sentiment intelligence agent", role:"COT, Fear & Greed, options, social media",  skill:"sentiment-composite",    skills:3,  status:"active",  runs:42,   last:"4m",  tags:["COT","F&G Index","put/call","retail SSI","Twitter"],   cmds:["/sentiment:cot","/sentiment:fear-greed","/sentiment:composite"], mission:"Aggregate sentiment signals from all sources — COT institutional positioning, Fear & Greed Index, options market, retail positioning, and social media into a composite score for contrarian trade opportunities."},
  {id:26, dept:"strategy",  num:"26", name:"News intelligence agent",     role:"NLP sentiment, breaking news, geopolitical",skill:"news-nlp",              skills:3,  status:"active",  runs:58,   last:"1m",  tags:["earnings","M&A","central banks","geopolitical","FDA"],   cmds:["/news:scan","/news:macro","/news:breaking","/news:alerts"],    mission:"Monitor all financial news sources for market-moving events — NLP sentiment analysis locally, earnings surprises, geopolitical shocks, and regulatory changes with trade alerts."},
  // Department 6: Trading Automation (27-28)
  {id:27, dept:"automation",num:"27", name:"Strategy backtesting agent",   role:"Historical backtests, Monte Carlo, walk-forward",skill:"backtest-combined", skills:3,status:"active",runs:19, last:"15m",tags:["vectorbt","Monte Carlo","walk-forward","optimisation"],    cmds:["/backtest:run","/backtest:compare","/backtest:montecarlo","/backtest:report"], mission:"Backtest any combination of SMC, technical, and fundamental strategies on historical data — generating performance metrics, Monte Carlo simulations, walk-forward validation, and parameter optimisation."},
  {id:28, dept:"automation",num:"28", name:"Live trading executor agent", role:"cTrader execution — orders, risk, positions",skill:"smc-silver-bullet",    skills:9,  status:"active",  runs:38,   last:"3m",  tags:["cTrader","orders","stop loss","take profit","trailing"],   cmds:["/trade:execute","/trade:positions","/trade:risk-check","/trade:halt"], mission:"Execute approved trade setups on live markets via cTrader CLI — managing order entry, SL/TP, partial closes, trailing stops, and position monitoring with strict 1% risk per trade safety gates."},
];

/* ─── TRADING DATA ──────────────────────────────────────────────────────────── */
const POSITIONS = [
  { id:"#1247", sym:"EURUSD", dir:"BUY", lots:0.10, entry:1.0823, sl:1.0756, tp1:1.0890, tp2:1.0980, pnlPips:67,  pnlPct:0.72, conf:81, strat:"SMC+Tech", age:"2h14m", ob:"H4 Bull OB" },
  { id:"#1248", sym:"XAUUSD", dir:"SELL", lots:0.05, entry:2345.60, sl:2372.00, tp1:2310.00, tp2:2280.00, pnlPips:-18, pnlPct:-0.41, conf:77, strat:"SMC", age:"45m",   ob:"H1 Bear OB" },
  { id:"#1249", sym:"GBPUSD", dir:"BUY",  lots:0.08, entry:1.2678, sl:1.2600, tp1:1.2800, tp2:1.2950, pnlPips:34,  pnlPct:0.28, conf:79, strat:"SMC+Tech", age:"1h02m", ob:"D1 Bull OB" },
];

const PENDING_ORDERS = [
  { id:"#P003", sym:"USDJPY", dir:"BUY",  type:"limit", lots:0.10, price:148.20, sl:147.50, tp:149.80, conf:83, reason:"H4 FVG + OTE Zone", exp:"12:00 UTC" },
  { id:"#P004", sym:"EURUSD", dir:"SELL", type:"limit", lots:0.06, price:1.0920, sl:1.0980, tp:1.0800, conf:76, reason:"D1 Bear OB retest", exp:"Today" },
];

const KILL_ZONES = [
  { name:"Asian",      start:"21:00", end:"04:00", pairs:["AUDJPY","USDJPY","AUDUSD"], status:"active",   color:T.blue,   profitPips:124, trades:14, winRate:71 },
  { name:"London Open", start:"02:50", end:"04:00", pairs:["GBPUSD","EURGBP","EURUSD"], status:"active",   color:T.green,  profitPips:312, trades:28, winRate:68 },
  { name:"London",      start:"03:00", end:"12:00", pairs:["EURUSD","GBPUSD","EURJPY"], status:"active",   color:T.green,  profitPips:287, trades:41, winRate:72 },
  { name:"NY Open",     start:"08:00", end:"12:00", pairs:["EURUSD","GBPUSD","USDJPY"], status:"upcoming", color:T.amber,  profitPips:0,   trades:0,  winRate:0  },
  { name:"London Close",start:"10:30", end:"11:00", pairs:["EURUSD","GBPUSD"],          status:"upcoming", color:T.amber,  profitPips:0,   trades:0,  winRate:0  },
  { name:"NY Close",    start:"16:00", end:"17:00", pairs:["All majors"],              status:"inactive", color:T.txtDim, profitPips:0,   trades:0,  winRate:0  },
];

const SMC_SETUPS = [
  { sym:"EURUSD", tf:"H1", bias:"BULLISH", conf:82, ob:"H4 Bull OB at 1.0795", fvg:"M15 FVG 1.0808-1.0812", kills:"London active", age:"8m",  action:"EXECUTE", actColor:T.green },
  { sym:"XAUUSD", tf:"H4", bias:"BEARISH", conf:79, ob:"D1 Bear OB at 2368", fvg:"H1 FVG 2348-2352",        kills:"Asian closing", age:"23m", action:"WATCH",   actColor:T.amber },
  { sym:"GBPUSD", tf:"H1", bias:"BULLISH", conf:76, ob:"H4 Bull OB at 1.2642", fvg:"M15 FVG 1.2665-1.2669", kills:"London active", age:"2m",  action:"EXECUTE", actColor:T.green },
  { sym:"USDJPY", tf:"H4", bias:"NEUTRAL", conf:68, ob:"D1 Bull OB at 147.80", fvg:"H1 FVG 148.05-148.12", kills:"NY open wait", age:"1h",  action:"PENDING", actColor:T.txtMid },
];

const ACCOUNT = {
  broker:"Pepperstone", accountId:"#46729678", mode:"DEMO",
  equity:10427.50, balance:10500.00, margin:1248.30, marginLevel:834.8,
  dailyPnl:127.50, dailyPnlPct:1.24, monthlyPnl:427.50, monthlyPnlPct:4.27,
  openPositions:3, maxPositions:5, openLots:0.23, maxLots:1.00,
  winRate:72.4, profitFactor:2.31, totalTrades:38, drawdown:1.82,
  bestSession:"London", bestDay:"Wednesday", sharpeRatio:2.14,
};

const BACKTEST_RESULTS = [
  { strat:"Conservative SMC", symbol:"EURUSD", tf:"H4", period:"2024-01-01 to 2024-12-31", winRate:71.2, pf:2.47, sharpe:2.31, mdd:-3.2, trades:312, ret:38.4, annualized:38.4 },
  { strat:"Balanced SMC+Tech",symbol:"EURUSD",tf:"H1", period:"2024-01-01 to 2024-12-31", winRate:63.8, pf:1.98, sharpe:1.87, mdd:-5.1, trades:587, ret:31.2, annualized:31.2 },
  { strat:"Scalp Silver Bullet",symbol:"GBPUSD",tf:"M15",period:"2024-01-01 to 2024-12-31",winRate:65.4, pf:2.12, sharpe:2.05, mdd:-2.8, trades:412, ret:24.6, annualized:41.8 },
];

const WEEKLY_PERF = [
  { day:"Monday",    pips:42,  trades:4, winRate:75 },
  { day:"Tuesday",   pips:-18, trades:5, winRate:60 },
  { day:"Wednesday", pips:87,  trades:6, winRate:83 },
  { day:"Thursday",  pips:31,  trades:3, winRate:67 },
  { day:"Friday",    pips:15,  trades:2, winRate:50 },
];

/* ─── V3 SKILL CATEGORIES ───────────────────────────────────────────────────── */
const SKILL_CATS_V3 = {
  "SMC Trading":[
    {n:"smc-order-blocks",d:"Identify institutional order block zones",master:false},
    {n:"smc-fair-value-gaps",d:"Detect and track FVG imbalance zones",master:false},
    {n:"smc-bos-choch",d:"Break of Structure & Change of Character",master:false},
    {n:"smc-liquidity",d:"Liquidity sweep and stop hunt detection",master:false},
    {n:"smc-kill-zones",d:"ICT session timing for entry precision",master:false},
    {n:"smc-confluence",d:"Multi-factor SMC confluence scoring",master:true},
    {n:"smc-silver-bullet",d:"ICT Silver Bullet 3-candle FVG setup",master:false},
    {n:"smc-judas-swing",d:"False breakout detection at market open",master:false},
    {n:"smc-power-of-3",d:"AMD: Accumulation/Manipulation/Distribution",master:false},
  ],
  "Technical Analysis":[
    {n:"tech-rsi",d:"RSI overbought/oversold with divergence",master:false},
    {n:"tech-macd",d:"MACD crossovers and histogram analysis",master:false},
    {n:"tech-bollinger",d:"Bollinger Band squeeze and breakout",master:false},
    {n:"tech-ichimoku",d:"Full Ichimoku cloud system",master:false},
    {n:"tech-adx",d:"ADX trend strength measurement",master:false},
    {n:"tech-momentum",d:"ROC, CCI, Williams %R, MFI",master:false},
    {n:"tech-volume",d:"OBV, VWAP, CMF, volume profile",master:false},
    {n:"tech-divergence",d:"Hidden and regular price/indicator divergence",master:false},
    {n:"tech-confluence",d:"Multi-indicator confluence scoring",master:true},
  ],
  "Fundamental":[
    {n:"fundamental-regime",d:"Macro regime classification (Goldilocks/Recession/etc)",master:false},
    {n:"fundamental-calendar",d:"Economic calendar and data surprise scoring",master:false},
    {n:"fundamental-rates",d:"Central bank rate decisions and Fed policy",master:false},
  ],
  "Sentiment":[
    {n:"sentiment-cot",d:"CFTC COT report — commercial vs speculator positioning",master:false},
    {n:"sentiment-fear-greed",d:"CNN Fear & Greed Index extremes",master:false},
    {n:"sentiment-composite",d:"Weighted composite sentiment score",master:true},
  ],
  "News & Events":[
    {n:"news-nlp",d:"Local FinBERT NLP sentiment on headlines",master:false},
    {n:"news-events",d:"Scheduled economic event impact analysis",master:false},
    {n:"news-breaking",d:"Breaking news alert and trade impact scoring",master:false},
  ],
  "Backtesting":[
    {n:"backtest-smc",d:"SMC strategy backtest with vectorbt",master:false},
    {n:"backtest-technical",d:"Technical indicator strategy backtest",master:false},
    {n:"backtest-combined",d:"Combined SMC + Tech strategy backtest",master:true},
  ],
  "Forex Trading":[
    {n:"forex-smc",d:"SMC on forex major/minor/exotic pairs",master:false},
    {n:"forex-cot",d:"COT analysis for currency futures",master:false},
    {n:"forex-sessions",d:"Session-aware pair selection and timing",master:false},
  ],
  "Commodities Trading":[
    {n:"commodities-smc",d:"SMC structure on gold, oil, agriculture",master:false},
    {n:"commodities-fundamentals",d:"EIA, WASDE, supply/demand analysis",master:false},
    {n:"commodities-seasonality",d:"10-year seasonal performance patterns",master:false},
  ],
  "Indices Trading":[
    {n:"indices-breadth",d:"Advance/decline, new highs/lows breadth",master:false},
    {n:"indices-vix",d:"VIX regime classification and signals",master:false},
    {n:"indices-sectors",d:"S&P 500 sector rotation analysis",master:false},
  ],
};

/* ─── CSS ───────────────────────────────────────────────────────────────────── */
const globalCSS = `
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=JetBrains+Mono:wght@400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:#07080D;color:#E8ECF4;font-family:'DM Sans',system-ui,sans-serif;font-size:13px;line-height:1.5;-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#4A5168;border-radius:2px}

@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
@keyframes pulseGlow{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.65)}}
@keyframes pingRing{0%{transform:scale(1);opacity:.7}100%{transform:scale(2.4);opacity:0}}
@keyframes fadeSlideUp{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes softGlow{0%,100%{box-shadow:0 0 0 0 rgba(201,168,76,0)}50%{box-shadow:0 0 10px 1px rgba(201,168,76,.18)}}
@keyframes glowPulse{0%,100%{opacity:.7}50%{opacity:1}}

.af-card{background:#111422;border:1px solid rgba(255,255,255,.07);border-radius:10px;transition:border-color .18s,background .18s}
.af-card:hover{border-color:rgba(255,255,255,.13);background:#151929}

.af-agent{border:1px solid rgba(255,255,255,.07);border-radius:9px;background:#111422;overflow:hidden;cursor:pointer;transition:border-color .18s;animation:fadeSlideUp .22s ease both}
.af-agent:hover{border-color:rgba(255,255,255,.13)}
.af-agent.open{border-color:rgba(201,168,76,.28)}

.af-tab{background:transparent;border:none;padding:8px 16px;font-family:inherit;font-size:12px;font-weight:400;color:#8B93A8;cursor:pointer;border-bottom:2px solid transparent;transition:color .15s,border-color .15s;letter-spacing:.02em}
.af-tab.on{color:#C9A84C;border-bottom-color:#C9A84C;font-weight:500}
.af-tab:hover:not(.on){color:#E8ECF4}

.af-pill{background:transparent;border:1px solid rgba(255,255,255,.07);border-radius:20px;padding:4px 11px;font-family:inherit;font-size:11px;color:#8B93A8;cursor:pointer;transition:all .15s}
.af-pill.on{background:rgba(201,168,76,.1);border-color:rgba(201,168,76,.38);color:#C9A84C}
.af-pill:hover:not(.on){border-color:rgba(255,255,255,.13);color:#E8ECF4}

.af-action{background:#C9A84C;border:none;border-radius:6px;padding:7px 14px;font-family:inherit;font-size:12px;font-weight:500;color:#0A0800;cursor:pointer;transition:opacity .15s,transform .1s;white-space:nowrap}
.af-action:hover{opacity:.86}
.af-action:active{transform:scale(.97)}

.af-input{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:6px;padding:7px 11px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#E8ECF4;outline:none;text-transform:uppercase;letter-spacing:.05em;transition:border-color .15s;width:100px}
.af-input::placeholder{color:#4A5168;text-transform:none;letter-spacing:0}
.af-input:focus{border-color:rgba(201,168,76,.42)}

.af-search{background:#0D0F1A;border:1px solid rgba(255,255,255,.08);border-radius:7px;padding:8px 12px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#E8ECF4;outline:none;transition:border-color .15s;width:100%}
.af-search::placeholder{color:#4A5168}
.af-search:focus{border-color:rgba(201,168,76,.4)}

.af-skill-row:nth-child(even){background:rgba(255,255,255,.018)}
.af-skill-row:hover{background:rgba(255,255,255,.04)}
.af-feed-row{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.06);animation:fadeSlideUp .2s ease both}
.af-feed-row:last-child{border-bottom:none}

.badge-trading{font-family:'JetBrains Mono',monospace;font-size:9px;padding:1px 6px;border-radius:10px;letter-spacing:.05em;font-weight:500}
.badge-buy{background:rgba(34,201,132,.12);color:#22C984;border:1px solid rgba(34,201,132,.25)}
.badge-sell{background:rgba(255,75,107,.12);color:#FF4B6B;border:1px solid rgba(255,75,107,.25)}
.badge-active{background:rgba(34,201,132,.12);color:#22C984;border:1px solid rgba(34,201,132,.25);animation:glowPulse 1.5s ease-in-out infinite}
.badge-upcoming{background:rgba(245,158,11,.12);color:#F59E0B;border:1px solid rgba(245,158,11,.25)}
`;

/* ─── HELPERS ─────────────────────────────────────────────────────────────────── */
const getDept = id => DEPTS.find(d => d.id === id) || DEPTS[0];
const totalRuns = AGENTS.reduce((s, a) => s + a.runs, 0);
const activeCount = AGENTS.filter(a => a.status !== "idle").length;

function Dot({ status, size = 7 }) {
  const colors = { active: T.green, running: T.amber, idle: T.txtDim };
  const c = colors[status] || T.txtDim;
  return (
    <span style={{ position:"relative", display:"inline-flex", alignItems:"center", justifyContent:"center", width:size, height:size, flexShrink:0 }}>
      {status === "running" && (
        <span style={{ position:"absolute", inset:0, borderRadius:"50%", background:c, animation:"pingRing 1.2s ease-out infinite" }} />
      )}
      <span style={{ width:size, height:size, borderRadius:"50%", background:c, display:"block", animation: status === "active" ? "pulseGlow 2.4s ease-in-out infinite" : "none" }} />
    </span>
  );
}

function Bar({ value, max, color }) {
  return (
    <div style={{ height:3, background:"rgba(255,255,255,.05)", borderRadius:2, overflow:"hidden" }}>
      <div style={{ width:String(Math.min(100, Math.round(value/max*100))) + "%", height:"100%", background:color, borderRadius:2, transition:"width .6s ease" }} />
    </div>
  );
}

/* ─── TICKER ─────────────────────────────────────────────────────────────────── */
const FX_TICKER = [
  {t:"EURUSD",v:"+0.62%",up:true},{t:"GBPUSD",v:"+0.38%",up:true},{t:"USDJPY",v:"-0.24%",up:false},
  {t:"XAUUSD",v:"+1.14%",up:true},{t:"XAGUSD",v:"+0.87%",up:true},{t:"WTI",v:"+0.53%",up:true},
  {t:"SPX",v:"+0.29%",up:true},{t:"NDX",v:"+0.45%",up:true},{t:"BTC",v:"+2.31%",up:true},
  {t:"ETH",v:"+1.87%",up:true},{t:"USDCAD",v:"-0.11%",up:false},{t:"AUDUSD",v:"+0.18%",up:true},
];

function Ticker() {
  const items = [...FX_TICKER, ...FX_TICKER];
  return (
      <div style={{ height:28, background:T.surface, borderBottom:"1px solid " + T.border, overflow:"hidden", display:"flex", alignItems:"center", position:"sticky", top:0, zIndex:50 }}>
      <div style={{ display:"flex", animation:"ticker 20s linear infinite", whiteSpace:"nowrap" }}>
        {items.map((item, i) => (
          <span key={i} style={{ display:"inline-flex", alignItems:"center", gap:5, padding:"0 18px", borderRight:"1px solid " + T.border }}>
            <span style={{ fontFamily:T.mono, fontSize:10, fontWeight:500, color:T.txtMid, letterSpacing:".05em" }}>{item.t}</span>
            <span style={{ fontFamily:T.mono, fontSize:10, color:item.up ? T.green : T.red }}>{item.v}</span>
          </span>
        ))}
      </div>
      <div style={{ position:"absolute", right:0, width:80, height:"100%", background:"linear-gradient(to right, transparent, " + T.surface + ")", pointerEvents:"none" }} />
    </div>
  );
}

/* ─── STAT CARD ───────────────────────────────────────────────────────────────── */
function StatCard({ label, value, sub, color }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"14px 16px" }}>
      <div style={{ fontSize:9, color:T.txtDim, letterSpacing:".09em", textTransform:"uppercase", fontWeight:500, marginBottom:6 }}>{label}</div>
      <div style={{ fontSize:24, fontWeight:300, fontFamily:T.serif, color: color || T.gold, lineHeight:1 }}>{value}</div>
      {sub && <div style={{ fontSize:10, color:T.txtDim, marginTop:5 }}>{sub}</div>}
    </div>
  );
}

/* ─── TRADING STAT CARD ─────────────────────────────────────────────────────── */
function TradingCard({ label, value, sub, color, delta, deltaLabel }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"14px 16px" }}>
      <div style={{ fontSize:9, color:T.txtDim, letterSpacing:".09em", textTransform:"uppercase", fontWeight:500, marginBottom:6 }}>{label}</div>
      <div style={{ fontSize:22, fontWeight:300, fontFamily:T.serif, color: color || T.gold, lineHeight:1 }}>{value}</div>
      {delta !== undefined && (
        <div style={{ display:"flex", alignItems:"center", gap:6, marginTop:4 }}>
          <span style={{ fontFamily:T.mono, fontSize:11, color:delta >= 0 ? T.green : T.red }}>
            {delta >= 0 ? "+" : ""}{delta}{deltaLabel || ""}
          </span>
          <span style={{ fontSize:10, color:T.txtDim }}>{sub}</span>
        </div>
      )}
    </div>
  );
}

/* ─── ACCOUNT SUMMARY ────────────────────────────────────────────────────────── */
function AccountSummary({ acct }) {
  const pnlColor = acct.dailyPnl >= 0 ? T.green : T.red;
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"16px 18px", marginBottom:16 }}>
      <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", flexWrap:"wrap", gap:12 }}>
        {/* Left: broker + account */}
        <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <span style={{ fontFamily:T.mono, fontSize:11, color:T.txtMid }}>{acct.broker}</span>
            <span style={{ fontSize:9, padding:"2px 7px", borderRadius:10, background:T.cyanDim, color:T.cyan, border:"1px solid rgba(34,211,238,.25)", fontFamily:T.mono, letterSpacing:".05em" }}>
              {acct.mode}
            </span>
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>{acct.accountId}</span>
          </div>
          <div style={{ display:"flex", alignItems:"baseline", gap:10 }}>
            <span style={{ fontFamily:T.serif, fontSize:28, fontWeight:300, color:T.gold, lineHeight:1 }}>
              ${acct.equity.toLocaleString("en", { minimumFractionDigits: 2 })}
            </span>
            <div style={{ display:"flex", flexDirection:"column", gap:1 }}>
              <span style={{ fontFamily:T.mono, fontSize:12, color:T.txtMid }}>Balance: ${acct.balance.toLocaleString("en", { minimumFractionDigits: 2 })}</span>
              <span style={{ fontFamily:T.mono, fontSize:12, color:pnlColor }}>
                Daily: {acct.dailyPnl >= 0 ? "+" : ""}${acct.dailyPnl.toFixed(2)} ({acct.dailyPnl >= 0 ? "+" : ""}{acct.dailyPnlPct.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>

        {/* Middle: metrics */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"0 20px" }}>
          {[
            { l:"Margin", v:`$${acct.margin.toLocaleString()}`, sub:`${acct.marginLevel.toFixed(1)}% level` },
            { l:"Open Positions", v:`${acct.openPositions}/${acct.maxPositions}`, sub:`${acct.openLots.toFixed(2)} lots` },
            { l:"Win Rate", v:`${acct.winRate}%`, sub:`${acct.totalTrades} trades` },
          ].map(m => (
            <div key={m.l} style={{ textAlign:"center" }}>
              <div style={{ fontSize:9, color:T.txtDim, letterSpacing:".07em", textTransform:"uppercase", marginBottom:3 }}>{m.l}</div>
              <div style={{ fontFamily:T.mono, fontSize:15, fontWeight:500, color:T.txt }}>{m.v}</div>
              <div style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>{m.sub}</div>
            </div>
          ))}
        </div>

        {/* Right: mini risk bar */}
        <div style={{ display:"flex", flexDirection:"column", gap:5, minWidth:120 }}>
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:T.txtDim }}>
            <span>Positions</span>
            <span style={{ fontFamily:T.mono, color:T.txtMid }}>{acct.openPositions}/{acct.maxPositions}</span>
          </div>
          <Bar value={acct.openPositions} max={acct.maxPositions} color={acct.openPositions < 4 ? T.green : T.amber} />
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:T.txtDim }}>
            <span>Drawdown</span>
            <span style={{ fontFamily:T.mono, color:T.red }}>-{acct.drawdown}%</span>
          </div>
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:T.txtDim }}>
            <span>Profit Factor</span>
            <span style={{ fontFamily:T.mono, color:T.green }}>{acct.profitFactor}</span>
          </div>
          <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:T.txtDim }}>
            <span>Sharpe</span>
            <span style={{ fontFamily:T.mono, color:T.blue }}>{acct.sharpeRatio}</span>
          </div>
        </div>
      </div>

      {/* Safety gates status row */}
      <div style={{ display:"flex", gap:8, marginTop:12, paddingTop:12, borderTop:"1px solid rgba(255,255,255,.05)", flexWrap:"wrap" }}>
        {[
          { l:"Daily Loss", v:`-${acct.drawdown}%`, ok: acct.drawdown < 3, warn: acct.drawdown >= 2 },
          { l:"Max Positions", v:`${acct.openPositions}/${acct.maxPositions}`, ok: acct.openPositions < 5 },
          { l:"Margin Level", v:`${acct.marginLevel.toFixed(0)}%`, ok: acct.marginLevel > 300 },
          { l:"Spread Guard", v:"OK", ok: true },
          { l:"News Block", v:"Clear", ok: true },
        ].map(g => (
          <span key={g.l} style={{ fontFamily:T.mono, fontSize:9, padding:"3px 8px", borderRadius:5, background: g.ok ? T.greenDim : g.warn ? T.amberDim : T.redDim, color: g.ok ? T.green : g.warn ? T.amber : T.red, border:"1px solid " + (g.ok ? "rgba(34,201,132,.25)" : g.warn ? "rgba(245,158,11,.25)" : "rgba(255,75,107,.25)") }}>
            {g.l}: {g.v} {g.ok ? "✓" : g.warn ? "⚠" : "✗"}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── OPEN POSITIONS TABLE ───────────────────────────────────────────────────── */
function PositionsTable({ positions }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase" }}>Open Positions</span>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>{positions.length} of 5 max</span>
      </div>
      <div style={{ overflowX:"auto" }}>
        <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:T.mono, fontSize:11 }}>
          <thead>
            <tr style={{ borderBottom:"1px solid rgba(255,255,255,.05)" }}>
              {["ID","Symbol","Dir","Lots","Entry","SL","TP1","TP2","P&L","Conf","Age"].map(h => (
                <th key={h} style={{ padding:"7px 12px", textAlign:"right", fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".07em", fontWeight:400 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {positions.map(p => {
              const pnlCol = p.pnlPips >= 0 ? T.green : T.red;
              const dirCol = p.dir === "BUY" ? T.green : T.red;
              return (
                <tr key={p.id} style={{ borderBottom:"1px solid rgba(255,255,255,.04)", transition:"background .15s" }}
                  onMouseOver={e => e.currentTarget.style.background = "rgba(255,255,255,.03)"}
                  onMouseOut={e => e.currentTarget.style.background = "transparent"}>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.txtDim }}>{p.id}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.txt, fontWeight:500 }}>{p.sym}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right" }}>
                    <span className={`badge-trading badge-${p.dir.toLowerCase()}`}>{p.dir}</span>
                  </td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.txtMid }}>{p.lots.toFixed(2)}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.txtMid }}>{typeof p.entry === "number" && p.entry > 100 ? p.entry.toFixed(2) : p.entry.toFixed(4)}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.red }}>{typeof p.sl === "number" && p.sl > 100 ? p.sl.toFixed(2) : p.sl.toFixed(4)}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.green }}>{typeof p.tp1 === "number" && p.tp1 > 100 ? p.tp1.toFixed(2) : p.tp1.toFixed(4)}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.green }}>{typeof p.tp2 === "number" && p.tp2 > 100 ? p.tp2.toFixed(2) : p.tp2.toFixed(4)}</td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:pnlCol, fontWeight:500 }}>
                    {p.pnlPips >= 0 ? "+" : ""}{p.pnlPips} pips · {p.pnlPips >= 0 ? "+" : ""}{p.pnlPct.toFixed(2)}%
                  </td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:p.conf >= 80 ? T.gold : T.txtMid }}>
                    <span style={{ background:T.goldDim, padding:"1px 5px", borderRadius:3, border:"1px solid rgba(201,168,76,.2)" }}>{p.conf}%</span>
                  </td>
                  <td style={{ padding:"8px 12px", textAlign:"right", color:T.txtDim }}>{p.age}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {/* Total P&L */}
      <div style={{ display:"flex", justifyContent:"flex-end", alignItems:"center", gap:12, padding:"10px 16px", borderTop:"1px solid rgba(255,255,255,.05)" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>Total Open P&L:</span>
        <span style={{ fontFamily:T.mono, fontSize:14, fontWeight:500, color:T.green }}>
          +{positions.filter(p=>p.pnlPips>0).reduce((s,p)=>s+p.pnlPips,0) - Math.abs(positions.filter(p=>p.pnlPips<0).reduce((s,p)=>s+p.pnlPips,0))} pips
        </span>
      </div>
    </div>
  );
}

/* ─── PENDING ORDERS ─────────────────────────────────────────────────────────── */
function PendingOrders({ orders }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtMid, letterSpacing:".07em", textTransform:"uppercase" }}>Pending Orders</span>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, marginLeft:8 }}>{orders.length} active</span>
      </div>
      {orders.map(o => (
        <div key={o.id} style={{ display:"flex", alignItems:"center", gap:14, padding:"10px 16px", borderBottom:"1px solid rgba(255,255,255,.04)", flexWrap:"wrap" }}>
          <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, minWidth:40 }}>{o.id}</span>
          <span style={{ fontFamily:T.mono, fontSize:12, color:T.txt, fontWeight:500 }}>{o.sym}</span>
          <span className={`badge-trading badge-${o.dir.toLowerCase()}`}>{o.type === "limit" ? "LMT" : "STP"} {o.dir}</span>
          <span style={{ fontFamily:T.mono, fontSize:11, color:T.txtMid }}>{o.lots.toFixed(2)} lots @ {o.price.toFixed(4)}</span>
          <span style={{ fontFamily:T.mono, fontSize:10, color:T.red }}>SL {o.sl.toFixed(4)}</span>
          <span style={{ fontFamily:T.mono, fontSize:10, color:T.green }}>TP {o.tp.toFixed(4)}</span>
          <span style={{ fontSize:10, color:T.txtDim, flex:1 }}>{o.reason}</span>
          <span style={{ fontFamily:T.mono, fontSize:9, color:T.amber, background:T.amberDim, padding:"2px 6px", borderRadius:4 }}>Exp: {o.exp}</span>
          <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, background:T.goldDim, padding:"2px 6px", borderRadius:4 }}>{o.conf}%</span>
        </div>
      ))}
    </div>
  );
}

/* ─── KILL ZONES PANEL ───────────────────────────────────────────────────────── */
function KillZonesPanel({ zones }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase" }}>Kill Zones — EST</span>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, marginLeft:8 }}>
          {zones.filter(z=>z.status==="active").length} active
        </span>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:0 }}>
        {zones.map(z => (
          <div key={z.name} style={{ padding:"12px 14px", borderRight:"1px solid rgba(255,255,255,.05)", borderBottom:"1px solid rgba(255,255,255,.05)" }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:6 }}>
              <span style={{ fontSize:11, fontWeight:500, color:z.color }}>{z.name}</span>
              <span className={`badge-trading ${z.status === "active" ? "badge-active" : z.status === "upcoming" ? "badge-upcoming" : ""}`}
                style={{ fontSize:8, padding:"1px 5px" }}>
                {z.status.toUpperCase()}
              </span>
            </div>
            <div style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim, marginBottom:6 }}>
              {z.start} – {z.end}
            </div>
            {z.status !== "inactive" && (
              <>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:9, marginBottom:2 }}>
                  <span style={{ color:T.txtDim }}>Pips</span>
                  <span style={{ fontFamily:T.mono, color:z.profitPips >= 0 ? T.green : T.red }}>
                    {z.profitPips >= 0 ? "+" : ""}{z.profitPips}
                  </span>
                </div>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:9, marginBottom:2 }}>
                  <span style={{ color:T.txtDim }}>Trades</span>
                  <span style={{ fontFamily:T.mono, color:T.txtMid }}>{z.trades}</span>
                </div>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:9 }}>
                  <span style={{ color:T.txtDim }}>Win Rate</span>
                  <span style={{ fontFamily:T.mono, color:z.winRate >= 60 ? T.green : T.amber }}>{z.winRate}%</span>
                </div>
                <Bar value={z.winRate} max={100} color={z.color} />
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── SMC SETUPS PANEL ───────────────────────────────────────────────────────── */
function SMCSetupsPanel({ setups }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase" }}>SMC Setups — Live Scan</span>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.green }}>● Scanning 15 pairs</span>
      </div>
      {setups.map((s, i) => (
        <div key={i} style={{ padding:"11px 16px", borderBottom:i < setups.length-1 ? "1px solid rgba(255,255,255,.04)" : "none" }}>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:6, flexWrap:"wrap", gap:6 }}>
            <div style={{ display:"flex", alignItems:"center", gap:10 }}>
              <span style={{ fontFamily:T.mono, fontSize:13, fontWeight:500, color:T.txt }}>{s.sym}</span>
              <span style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>{s.tf}</span>
              <span style={{ fontFamily:T.mono, fontSize:10, padding:"2px 6px", borderRadius:4, background:s.bias === "BULLISH" ? T.greenDim : s.bias === "BEARISH" ? T.redDim : T.amberDim, color:s.bias === "BULLISH" ? T.green : s.bias === "BEARISH" ? T.red : T.amber }}>
                {s.bias}
              </span>
              <span style={{ fontFamily:T.mono, fontSize:10, background:T.goldDim, color:T.gold, padding:"2px 6px", borderRadius:4, border:"1px solid rgba(201,168,76,.2)" }}>
                {s.conf}%
              </span>
            </div>
            <span style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>{s.age} ago</span>
          </div>
          <div style={{ fontSize:11, color:T.txtMid, marginBottom:6 }}>
            <span style={{ color:T.txtDim }}>OB: </span>{s.ob} &nbsp;|&nbsp;
            <span style={{ color:T.txtDim }}>FVG: </span>{s.fvg} &nbsp;|&nbsp;
            <span style={{ color:T.txtDim }}>Session: </span>{s.kills}
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <button style={{ background:s.actColor, border:"none", borderRadius:5, padding:"4px 12px", fontFamily:T.mono, fontSize:10, color:"#000", fontWeight:600, cursor:"pointer", transition:"opacity .15s" }}>
              {s.action}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── BACKTEST RESULTS ───────────────────────────────────────────────────────── */
function BacktestResults({ results }) {
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase" }}>Backtest Results — 2024</span>
      </div>
      <div style={{ overflowX:"auto" }}>
        <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:T.mono, fontSize:10 }}>
          <thead>
            <tr style={{ borderBottom:"1px solid rgba(255,255,255,.05)" }}>
              {["Strategy","Symbol","TF","Period","Win Rate","PF","Sharpe","MDD","Trades","Return"].map(h => (
                <th key={h} style={{ padding:"6px 10px", textAlign:"right", fontSize:8, color:T.txtDim, textTransform:"uppercase", letterSpacing:".07em", fontWeight:400 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} style={{ borderBottom:"1px solid rgba(255,255,255,.03)" }}>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.txt, fontWeight:500 }}>{r.strat}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.txtMid }}>{r.symbol}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.txtDim }}>{r.tf}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.txtDim, fontSize:9 }}>{r.period}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:r.winRate >= 65 ? T.green : r.winRate >= 55 ? T.amber : T.red }}>{r.winRate}%</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:r.pf >= 2 ? T.green : T.amber }}>{r.pf}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.blue }}>{r.sharpe}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.red }}>-{r.mdd}%</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.txtMid }}>{r.trades}</td>
                <td style={{ padding:"7px 10px", textAlign:"right", color:T.green, fontWeight:500 }}>+{r.ret}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ─── WEEKLY PERFORMANCE ────────────────────────────────────────────────────── */
function WeeklyPerformance({ week }) {
  const totalPips = week.reduce((s, d) => s + d.pips, 0);
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden", marginBottom:16 }}>
      <div style={{ padding:"12px 16px", borderBottom:"1px solid rgba(255,255,255,.06)", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase" }}>Weekly Performance</span>
        <span style={{ fontFamily:T.mono, fontSize:12, color:T.green }}>+{totalPips} pips total</span>
      </div>
      <div style={{ display:"flex", flexDirection:"column", gap:0 }}>
        {week.map((d, i) => (
          <div key={d.day} style={{ display:"flex", alignItems:"center", gap:14, padding:"8px 16px", borderBottom:i < week.length-1 ? "1px solid rgba(255,255,255,.04)" : "none" }}>
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtMid, minWidth:80 }}>{d.day}</span>
            <div style={{ flex:1 }}>
              <Bar value={Math.abs(d.pips)} max={100} color={d.pips >= 0 ? T.green : T.red} />
            </div>
            <span style={{ fontFamily:T.mono, fontSize:11, color:d.pips >= 0 ? T.green : T.red, minWidth:60, textAlign:"right" }}>
              {d.pips >= 0 ? "+" : ""}{d.pips} pips
            </span>
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, minWidth:50, textAlign:"right" }}>
              {d.trades}t · {d.winRate}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── AGENT ROW (v3 with trading dept colors) ───────────────────────────────── */
function AgentRow({ agent, expanded, onToggle, i }) {
  const d = getDept(agent.dept);
  return (
    <div className={`af-agent${expanded ? " open" : ""}`} style={{ animationDelay:String(i * 0.03) + "s" }} onClick={onToggle}>
      <div style={{ display:"flex", alignItems:"center", gap:11, padding:"10px 14px" }}>
        <div style={{ width:32, height:32, borderRadius:7, flexShrink:0, display:"flex", alignItems:"center", justifyContent:"center", background:d.color + "14", border:"1px solid " + d.color + "28", fontFamily:T.mono, fontSize:10, color:d.color, fontWeight:500 }}>{agent.num}</div>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:7 }}>
            <Dot status={agent.status} />
            <span style={{ fontSize:13, fontWeight:500, color:T.txt }}>{agent.name}</span>
            {agent.status === "running" && (
              <span style={{ fontSize:9, padding:"1px 6px", borderRadius:10, background:T.amberDim, color:T.amber, letterSpacing:".05em" }}>LIVE</span>
            )}
          </div>
          <div style={{ fontSize:11, color:T.txtMid, marginTop:1 }}>{agent.role}</div>
        </div>
        <span style={{ fontFamily:T.mono, fontSize:10, color:d.color, background:d.color + "12", padding:"2px 7px", borderRadius:4, border:"1px solid " + d.color + "22", flexShrink:0 }}>{agent.skills} skills</span>
        <div style={{ textAlign:"right", flexShrink:0, minWidth:48 }}>
          <div style={{ fontFamily:T.mono, fontSize:11, color:T.txtMid }}>{agent.runs.toLocaleString()}</div>
          <div style={{ fontSize:10, color:T.txtDim }}>{agent.last}</div>
        </div>
        <div style={{ fontSize:10, color:T.txtDim, flexShrink:0, transform: expanded ? "rotate(180deg)" : "none", transition:"transform .2s" }}>▾</div>
      </div>
      {expanded && (
        <div style={{ borderTop:"1px solid rgba(255,255,255,.06)", padding:"13px 14px 13px 57px", background:"rgba(0,0,0,.2)", animation:"fadeSlideUp .18s ease both" }}>
          <p style={{ fontSize:12, color:T.txtMid, lineHeight:1.75, marginBottom:11 }}>{agent.mission}</p>
          <div style={{ display:"flex", gap:5, flexWrap:"wrap", marginBottom:9 }}>
            <span style={{ fontFamily:T.mono, fontSize:10, padding:"2px 8px", borderRadius:4, background:d.dim, color:d.color, border:"1px solid " + d.color + "28", fontWeight:500 }}>{agent.skill}</span>
          </div>
          <div style={{ display:"flex", gap:4, flexWrap:"wrap", marginBottom:9 }}>
            {agent.tags.map(tag => (
              <span key={tag} style={{ display:"inline-flex", alignItems:"center", padding:"2px 7px", borderRadius:4, fontFamily:T.mono, fontSize:10, background:"rgba(255,255,255,.05)", border:"1px solid rgba(255,255,255,.08)", color:T.txtMid, whiteSpace:"nowrap" }}>{tag}</span>
            ))}
          </div>
          <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
            {agent.cmds.map(c => (
              <span key={c} style={{ display:"inline-flex", fontFamily:T.mono, fontSize:10, padding:"2px 7px", borderRadius:4, background:T.blueDim, border:"1px solid rgba(74,143,255,.22)", color:T.blue, whiteSpace:"nowrap" }}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── FEED ROW ────────────────────────────────────────────────────────────────── */
function FeedRow({ item, i }) {
  const cfg = { ok:{color:T.green,bg:T.greenDim,sym:"✓"}, alert:{color:T.red,bg:T.redDim,sym:"!"}, warn:{color:T.amber,bg:T.amberDim,sym:"⚠"}, info:{color:T.blue,bg:T.blueDim,sym:"i"} }[item.type] || {};
  return (
    <div className="af-feed-row" style={{ animationDelay:String(i * .04) + "s" }}>
      <div style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, minWidth:28, paddingTop:1 }}>{item.t}</div>
      <div style={{ width:16, height:16, borderRadius:"50%", background:cfg.bg, flexShrink:0, display:"flex", alignItems:"center", justifyContent:"center", fontSize:8, color:cfg.color, fontWeight:700 }}>{cfg.sym}</div>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:12, color:T.txt, lineHeight:1.45 }}>
          {item.ev}{item.tk && (
            <span style={{ marginLeft:6, fontFamily:T.mono, fontSize:9, padding:"1px 5px", borderRadius:3, background:cfg.bg, color:cfg.color }}>{item.tk}</span>
          )}
        </div>
        <div style={{ fontSize:10, color:T.txtDim, marginTop:1 }}>{item.ag}</div>
      </div>
    </div>
  );
}

/* ─── TRADING COMMAND PROMPT ─────────────────────────────────────────────────── */
function TradingPrompt({ onRun }) {
  const [cmd, setCmd] = useState("");
  return (
    <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"11px 14px", marginBottom:16, display:"flex", alignItems:"center", gap:10, flexWrap:"wrap" }}>
      <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase", fontWeight:500 }}>Trading</span>
      <input className="af-input" value={cmd} onChange={e => setCmd(e.target.value)} onKeyDown={e => e.key === "Enter" && onRun(cmd)} placeholder="e.g. /smc:scan EURUSD" style={{ width:180 }} />
      <span style={{ fontSize:11, color:T.txtDim, flex:1 }}>
        Run SMC analysis, technical scan, backtest, or trade command
      </span>
      <button className="af-action" onClick={() => onRun(cmd)}>Execute ↗</button>
    </div>
  );
}

/* ─── APP ─────────────────────────────────────────────────────────────────────── */
export default function App() {
  const [tab, setTab]           = useState("trading");
  const [dept, setDept]         = useState("all");
  const [expanded, setExpanded] = useState(null);
  const [skillCat, setSkillCat] = useState("SMC Trading");
  const [search, setSearch]     = useState("");
  const [ticker, setTicker]     = useState("");
  const [feed, setFeed]         = useState([
    {t:"now",  ag:"SMC Strategy Agent",    ev:"BUY signal: EURUSD H1 — Confluence 82% — London kill zone active",  type:"ok",    tk:"EURUSD" },
    {t:"1m",   ag:"Technical Analysis",    ev:"RSI divergence confirmed on GBPUSD H4 — bullish momentum building",  type:"alert", tk:"GBPUSD" },
    {t:"2m",   ag:"Forex Intelligence",    ev:"COT extremes: EUR net shorts at 3-year high — contrarian bullish",   type:"info",  tk:"EURUSD" },
    {t:"3m",   ag:"Live Trading Executor",  ev:"Position #1247: TP1 approached — 28 pips profit locked",            type:"ok",    tk:"EURUSD" },
    {t:"4m",   ag:"Sentiment Agent",        ev:"Fear & Greed: 62 (Greed) — neutral zone, no extreme signals",      type:"info",  tk:null    },
    {t:"5m",   ag:"News Intelligence",      ev:"No high-impact events in next 4 hours — trading window clear",   type:"ok",    tk:null    },
    {t:"8m",   ag:"Kill Zone Monitor",      ev:"London session active — 41 trades, +287 pips MTD",               type:"ok",    tk:null    },
    {t:"10m",  ag:"Risk Manager",           ev:"Daily drawdown: -1.82% — within acceptable range ✓",             type:"ok",    tk:null    },
    {t:"12m",  ag:"Commodities Intelligence",ev:"Gold: Bear OB at $2368 — watching for FVG retest entry",        type:"warn",  tk:"XAUUSD" },
    {t:"15m",  ag:"Backtesting Agent",      ev:"Weekly backtest complete: Conservative SMC 71.2% WR, PF 2.47",    type:"ok",    tk:null    },
  ]);

  const visAgents = dept === "all" ? AGENTS : AGENTS.filter(a => a.dept === dept);
  const allSkills = Object.values(SKILL_CATS_V3).flat();
  const shownSkills = search ? allSkills.filter(s => s.n.includes(search.toLowerCase()) || s.d.toLowerCase().includes(search.toLowerCase())) : SKILL_CATS_V3[skillCat] || [];

  function doResearch() {
    if (!ticker.trim()) return;
    const t = ticker.trim().toUpperCase();
    setFeed(prev => [{t:"now",ag:"Deep research agent",ev:`Deep research initiated: ${t} — all 93 skills queued`,type:"alert",tk:t},...prev.slice(0,9)]);
    setTicker("");
    setTab("feed");
  }

  function handleTradingCmd(cmd) {
    if (!cmd.trim()) return;
    setFeed(prev => [{t:"now",ag:"Trading Command",ev:`Executing: ${cmd}`,type:"alert",tk:null},...prev.slice(0,9)]);
  }

  const TABS = [
    { id:"trading",   l:"Trading" },
    { id:"positions", l:"Positions" },
    { id:"agents",    l:"Agents · 28" },
    { id:"skills",    l:"Skills · 93" },
    { id:"workflows", l:"Workflows" },
    { id:"feed",      l:"Feed" },
  ];

  const tradingAgents = AGENTS.filter(a => ["asset","strategy","automation"].includes(a.dept));
  const intelAgents = AGENTS.filter(a => ["public","private","research","ops"].includes(a.dept));

  return (
    <>
      <style>{globalCSS}</style>
      <Ticker />
      <div style={{ padding:"20px 20px 44px", maxWidth:1100, margin:"0 auto" }}>

        {/* Header */}
        <div style={{ display:"flex", alignItems:"flex-end", justifyContent:"space-between", flexWrap:"wrap", gap:12, marginBottom:22 }}>
          <div>
            <h1 style={{ fontFamily:T.serif, fontWeight:300, fontSize:30, color:T.txt, letterSpacing:"-.01em", lineHeight:1.1, fontStyle:"italic" }}>
              Agent<span style={{ color:T.gold }}>Finance</span>
              <span style={{ fontSize:14, fontFamily:T.sans, fontStyle:"normal", fontWeight:300, color:T.txtDim, marginLeft:9 }}>v3</span>
            </h1>
            <p style={{ fontSize:11, color:T.txtDim, marginTop:4, letterSpacing:".03em" }}>
              autonomous trading automation  ·  SMC + 80+ indicators  ·  cTrader execution  ·  Kali Linux
            </p>
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <Dot status="active" size={6} />
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.green, letterSpacing:".05em" }}>
              {activeCount} agents live · {ACCOUNT.openPositions}/{ACCOUNT.maxPositions} positions
            </span>
          </div>
        </div>

        {/* Stats row */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:10, marginBottom:18 }}>
          <StatCard label="Total agents"    value="28"                    sub="6 departments"                  />
          <StatCard label="Active now"      value={activeCount}           sub="1 running live"                 color={T.green}  />
          <StatCard label="Skills"          value="93"                    sub="12 categories"                  color={T.blue}   />
          <StatCard label="Today's runs"    value={totalRuns.toLocaleString()} sub="all agents"               color={T.purple} />
        </div>

        {/* Tabs */}
        <div style={{ display:"flex", borderBottom:"1px solid " + T.border, marginBottom:18, overflowX:"auto" }}>
          {TABS.map(t => (
            <button key={t.id} className={`af-tab${tab === t.id ? " on" : ""}`} onClick={() => setTab(t.id)}>{t.l}</button>
          ))}
        </div>

        {/* ════ TRADING ════ */}
        {tab === "trading" && (
          <div>
            <TradingPrompt onRun={handleTradingCmd} />

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:16 }}>
              {/* Left: account + positions */}
              <div>
                <AccountSummary acct={ACCOUNT} />
                <PositionsTable positions={POSITIONS} />
                <PendingOrders orders={PENDING_ORDERS} />
              </div>
              {/* Right: setups + zones */}
              <div>
                <SMCSetupsPanel setups={SMC_SETUPS} />
                <KillZonesPanel zones={KILL_ZONES} />
                <WeeklyPerformance week={WEEKLY_PERF} />
              </div>
            </div>

            {/* Trading agent quick-status */}
            <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"14px 16px", marginBottom:16 }}>
              <div style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase", marginBottom:12 }}>Trading Agents — Live Status</div>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8 }}>
                {tradingAgents.map(a => {
                  const d = getDept(a.dept);
                  return (
                    <div key={a.id} style={{ background:T.surface, borderRadius:8, padding:"10px 12px", border:"1px solid " + T.border }}>
                      <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:6 }}>
                        <Dot status={a.status} size={6} />
                        <span style={{ fontFamily:T.mono, fontSize:10, color:d.color }}>{a.num}</span>
                        <span style={{ fontSize:11, fontWeight:500, color:T.txt }}>{a.name.split(" ").slice(0,2).join(" ")}</span>
                      </div>
                      <div style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>{a.runs} runs · {a.last}</div>
                      <div style={{ fontSize:10, color:T.txtDim, marginTop:3 }}>{a.role.split(" —")[0]}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ════ POSITIONS ════ */}
        {tab === "positions" && (
          <div>
            <AccountSummary acct={ACCOUNT} />
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
              <div>
                <PositionsTable positions={POSITIONS} />
              </div>
              <div>
                <PendingOrders orders={PENDING_ORDERS} />
                <WeeklyPerformance week={WEEKLY_PERF} />
                <BacktestResults results={BACKTEST_RESULTS} />
              </div>
            </div>
          </div>
        )}

        {/* ════ AGENTS ════ */}
        {tab === "agents" && (
          <div>
            <div style={{ display:"flex", gap:6, flexWrap:"wrap", marginBottom:14 }}>
              <button className={`af-pill${dept === "all" ? " on" : ""}`} onClick={() => { setDept("all"); setExpanded(null); }}>All · {AGENTS.length}</button>
              {DEPTS.map(d => (
                <button key={d.id} className={`af-pill${dept === d.id ? " on" : ""}`}
                  style={dept === d.id ? { background:d.color + "12", borderColor:d.color + "38", color:d.color } : {}}
                  onClick={() => { setDept(d.id); setExpanded(null); }}>
                  <span style={{ marginRight:4, fontSize:10 }}>{d.icon}</span>
                  {d.label} · {AGENTS.filter(a => a.dept === d.id).length}
                </button>
              ))}
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8, marginBottom:14 }}>
              {DEPTS.map(d => {
                const agents = AGENTS.filter(a => a.dept === d.id);
                const runs = agents.reduce((s, a) => s + a.runs, 0);
                const act = agents.filter(a => a.status !== "idle").length;
                return (
                  <div key={d.id} className="af-card" style={{ padding:"9px 11px", cursor:"pointer" }} onClick={() => { setDept(d.id); setExpanded(null); }}>
                    <div style={{ display:"flex", alignItems:"center", gap:5, marginBottom:6 }}>
                      <span style={{ fontSize:11, color:d.color }}>{d.icon}</span>
                      <span style={{ fontSize:10, color:T.txtMid, fontWeight:500 }}>{d.label}</span>
                    </div>
                    <Bar value={act} max={agents.length} color={d.color} />
                    <div style={{ display:"flex", justifyContent:"space-between", marginTop:5 }}>
                      <span style={{ fontSize:10, color:T.txtDim }}>{act}/{agents.length} active</span>
                      <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>{runs.toLocaleString()} runs</span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div style={{ display:"flex", flexDirection:"column", gap:7 }}>
              {visAgents.map((agent, i) => (
                <AgentRow key={agent.id} agent={agent} i={i} expanded={expanded === agent.id} onToggle={() => setExpanded(expanded === agent.id ? null : agent.id)} />
              ))}
            </div>
            <p style={{ fontSize:10, color:T.txtDim, textAlign:"center", marginTop:12 }}>Click any agent to expand — mission, skills, tags, and commands</p>
          </div>
        )}

        {/* ════ SKILLS ════ */}
        {tab === "skills" && (
          <div>
            <div style={{ display:"flex", gap:10, flexWrap:"wrap", alignItems:"center", marginBottom:14 }}>
              <input className="af-search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name or description…" style={{ maxWidth:300 }} />
              {!search && (
                <div style={{ display:"flex", gap:5, flexWrap:"wrap" }}>
                  {Object.keys(SKILL_CATS_V3).map(cat => (
                    <button key={cat} className={`af-pill${skillCat === cat ? " on" : ""}`} onClick={() => setSkillCat(cat)}>{cat} · {SKILL_CATS_V3[cat].length}</button>
                  ))}
                </div>
              )}
            </div>
            <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em", marginBottom:10 }}>
              {search ? `${shownSkills.length} matching skills` : `${skillCat} — ${shownSkills.length} skills`}
            </div>
            <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden" }}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 2fr 60px", padding:"7px 14px", borderBottom:"1px solid rgba(255,255,255,.06)", background:"rgba(255,255,255,.02)" }}>
                {["Skill name","Description",""].map((h, i) => (
                  <span key={i} style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em" }}>{h}</span>
                ))}
              </div>
              {shownSkills.map((s, i) => (
                <div key={i} className="af-skill-row" style={{ display:"grid", gridTemplateColumns:"1fr 2fr 60px", padding:"7px 14px", alignItems:"center" }}>
                  <span style={{ fontFamily:T.mono, fontSize:10, color: s.master ? T.gold : T.cyan, fontWeight: s.master ? 500 : 400, wordBreak:"break-all" }}>{s.n}</span>
                  <span style={{ fontSize:11, color:T.txtMid }}>{s.d}</span>
                  {s.master ? <span style={{ fontSize:9, padding:"2px 6px", borderRadius:10, background:T.goldDim, color:T.gold, textAlign:"center", border:"1px solid rgba(201,168,76,.25)" }}>master</span> : <span /> }
                </div>
              ))}
            </div>
            <div style={{ marginTop:13, background:T.surface, border:"1px solid " + T.border, borderRadius:8, padding:"9px 14px", display:"flex", alignItems:"center", gap:10 }}>
              <span style={{ fontSize:11, color:T.txtMid }}>Install all 93 skills:</span>
              <code style={{ fontFamily:T.mono, fontSize:10, color:T.gold, background:T.goldDim, padding:"2px 8px", borderRadius:4 }}>
                cp -r agentfinance/skills/* ~/agency/paperclip/skills/
              </code>
            </div>
          </div>
        )}

        {/* ════ WORKFLOWS ════ */}
        {tab === "workflows" && (
          <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
            <div>
              <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em", marginBottom:10 }}>Active trading pipelines</div>
              <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                {[
                  {l:"SMC Signal → Execution", steps:["15-min scan","Kill zone check","SMC confluence ≥75%","Tech confirmation","Risk gate","Telegram alert","cTrader execute"],active:3},
                  {l:"Position Management",    steps:["Webhook from cTrader","TP1 check","Partial close 50%","Trail SL to BE","TP2 → full close","P&L journal","Telegram result"],active:-1},
                  {l:"Morning Intelligence",   steps:["06:00 UTC trigger","Economic calendar","Kill zone schedule","Macro regime","Active positions","Brief compiled","Telegram sent"],active:-1},
                  {l:"Economic Calendar Block", steps:["Cron 30-min","High-impact filter","30-min warning","Trade block","15-min post-release","Block lift"],active:1},
                  {l:"Weekly Performance",     steps:["Sunday 18:00 UTC","Trade pull from DB","Metrics calc","Strategy breakdown","Recommendations","Notion journal","Telegram digest"],active:-1},
                ].map(w => (
                  <div key={w.l} className="af-card" style={{ padding:"12px 14px" }}>
                    <div style={{ display:"flex", alignItems:"center", marginBottom:8 }}>
                      <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase", flex:1 }}>{w.l}</span>
                      <span style={{ fontFamily:T.mono, fontSize:9, color:T.green, background:T.greenDim, padding:"1px 6px", borderRadius:4 }}>active</span>
                    </div>
                    <div style={{ display:"flex", alignItems:"center" }}>
                      {w.steps.map((step, i) => {
                        const done = w.active === -1 || i < w.active;
                        const now  = i === w.active;
                        const col  = done ? T.green : now ? T.gold : T.txtDim;
                        return (
                          <div key={i} style={{ display:"flex", alignItems:"center", flex:1 }}>
                            <div style={{ flex:1, padding:"5px 5px", borderRadius:5, textAlign:"center", fontSize:9, color:col, fontWeight: now ? 500 : 400, background: now ? T.goldDim : done ? T.greenDim : "rgba(255,255,255,.03)", border:"1px solid " + (now ? "rgba(201,168,76,.35)" : done ? "rgba(34,201,132,.25)" : T.border), animation: now ? "softGlow 2s ease-in-out infinite" : "none", lineHeight:1.3 }}>{step}</div>
                            {i < w.steps.length - 1 && <div style={{ width:6, height:1, flexShrink:0, background: done ? T.green : "rgba(255,255,255,.08)" }} />}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em", marginBottom:10 }}>Execution approval gates</div>
              <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, overflow:"hidden" }}>
                {[
                  {g:"Auto ≤$500",    d:"Small positions — fully automated execution",      c:T.green},
                  {g:"Notify",        d:"Signal generated — Telegram alert for info",         c:T.blue},
                  {g:"APPROVE",       d:"≥$500 or confidence <80% — manual confirmation",    c:T.gold},
                  {g:"HALT",          d:"Daily DD ≥3% — emergency stop, close all",          c:T.red},
                  {g:"KILL",          d:"Monthly DD ≥8% — full system shutdown",             c:T.red},
                ].map((row, i) => (
                  <div key={i} style={{ display:"flex", alignItems:"center", gap:14, padding:"9px 14px", borderTop: i === 0 ? "none" : "1px solid rgba(255,255,255,.05)" }}>
                    <div style={{ fontFamily:T.mono, fontSize:10, minWidth:80, color:row.c, background:row.c + "14", padding:"2px 7px", borderRadius:4, textAlign:"center", border:"1px solid " + row.c + "25", flexShrink:0 }}>{row.g}</div>
                    <span style={{ fontSize:11, color:T.txtMid }}>{row.d}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8 }}>
              {[
                {l:"SMC + cTrader",   sub:"Signal → webhook → risk check → cTrader execute",col:T.gold},
                {l:"n8n Orchestration",sub:"5 trading workflows — import from JSON",         col:T.amber},
                {l:"Pepperstone Demo", sub:"Account #46729678 — demo mode active",           col:T.cyan},
              ].map(b => (
                <div key={b.l} style={{ background:T.card, borderRadius:9, padding:"11px 13px", border:"1px solid " + b.col + "22", borderLeft:"3px solid " + b.col }}>
                  <div style={{ fontSize:12, fontWeight:500, color:b.col }}>{b.l}</div>
                  <div style={{ fontSize:11, color:T.txtDim, marginTop:3 }}>{b.sub}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ════ FEED ════ */}
        {tab === "feed" && (
          <div>
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:14 }}>
              <Dot status="active" size={6} />
              <span style={{ fontSize:11, color:T.txtMid }}>live intelligence & trading feed</span>
              <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, marginLeft:"auto" }}>
                {new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit",second:"2-digit"})}
              </span>
            </div>
            <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"4px 14px", marginBottom:20 }}>
              {feed.map((item, i) => <FeedRow key={i} item={item} i={i} />)}
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(2,1fr)", gap:16, marginBottom:16 }}>
              <div>
                <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em", marginBottom:10 }}>Runs by department</div>
                <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"14px" }}>
                  <div style={{ display:"flex", flexDirection:"column", gap:13 }}>
                    {DEPTS.map(d => {
                      const runs = AGENTS.filter(a => a.dept === d.id).reduce((s, a) => s + a.runs, 0);
                      const pct = Math.round(runs / totalRuns * 100);
                      return (
                        <div key={d.id}>
                          <div style={{ display:"flex", justifyContent:"space-between", fontSize:11, marginBottom:5 }}>
                            <span style={{ display:"flex", alignItems:"center", gap:5, color:T.txtMid }}><span style={{ color:d.color }}>{d.icon}</span>{d.label}</span>
                            <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>{runs.toLocaleString()} · {pct}%</span>
                          </div>
                          <div style={{ height:4, background:"rgba(255,255,255,.05)", borderRadius:2 }}>
                            <div style={{ width:String(pct) + "%", height:"100%", background:d.color, borderRadius:2, transition:"width .7s ease" }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
              <div>
                <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase", letterSpacing:".08em", marginBottom:10 }}>Trading performance</div>
                <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"14px", display:"flex", flexDirection:"column", gap:10 }}>
                  {[
                    {l:"Profit Factor",   v:ACCOUNT.profitFactor,  sub:"across 38 trades",     col:T.green},
                    {l:"Win Rate",        v:`${ACCOUNT.winRate}%`, sub:"hit rate",             col:T.blue},
                    {l:"Sharpe Ratio",    v:ACCOUNT.sharpeRatio,   sub:"risk-adjusted",        col:T.amber},
                    {l:"Best Session",    v:ACCOUNT.bestSession,   sub:"London kill zone",     col:T.gold},
                    {l:"Monthly Return",  v:`+${ACCOUNT.monthlyPnlPct.toFixed(2)}%`, sub:"March 2026", col:T.green},
                    {l:"Max Drawdown",    v:`-${ACCOUNT.drawdown}%`, sub:"daily DD",          col:T.red},
                  ].map(m => (
                    <div key={m.l} style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <span style={{ fontSize:11, color:T.txtDim }}>{m.l}</span>
                      <span style={{ fontFamily:T.mono, fontSize:13, fontWeight:500, color:m.col }}>{m.v}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ background:T.card, border:"1px solid " + T.border, borderRadius:10, padding:"11px 14px", marginBottom:16, display:"flex", alignItems:"center", gap:10, flexWrap:"wrap" }}>
              <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em", textTransform:"uppercase", fontWeight:500 }}>Deep research</span>
              <input className="af-input" value={ticker} onChange={e => setTicker(e.target.value.toUpperCase())} onKeyDown={e => e.key === "Enter" && doResearch()} placeholder="e.g. AAPL" />
              <span style={{ fontSize:11, color:T.txtDim, flex:1 }}>Orchestrates all 93 skills → IC-grade report in ~18 min</span>
              <button className="af-action" onClick={doResearch}>Run ↗</button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{ marginTop:32, paddingTop:14, borderTop:"1px solid " + T.border, display:"flex", justifyContent:"space-between", alignItems:"center", flexWrap:"wrap", gap:8 }}>
          <span style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>
            AgentFinance v3 · 28 agents · 93 skills · SMC Engine · cTrader · n8n · Kali Linux · Pepperstone Demo #46729678
          </span>
          <div style={{ display:"flex", alignItems:"center", gap:5 }}>
            <Dot status="active" size={5} />
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.green }}>{activeCount}/28 live</span>
          </div>
        </div>
      </div>
    </>
  );
}
