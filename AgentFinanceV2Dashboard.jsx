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
];

const AGENTS = [
  {id:1, dept:"public",  num:"01", name:"SEC filings analyst",           role:"Regulatory filing intelligence",          skill:"sec-analyst-master",        skills:16, status:"active",  runs:34,   last:"2m",  tags:["10-K","10-Q","8-K","S-1","covenants"],       cmds:["/sec:10k","/sec:10q","/sec:8k","/sec:s1","/sec:covenant"],     mission:"Citation-rich analysis of all SEC filings — risk factors, MDA narratives, debt covenants, and governance quality for any public company."},
  {id:2, dept:"public",  num:"02", name:"Transcripts analyst",           role:"Earnings call intelligence",              skill:"earnings-analyst-master",    skills:14, status:"active",  runs:18,   last:"8m",  tags:["guidance","sentiment","Q&A","management"],   cmds:["/transcript:full","/transcript:guidance","/transcript:sentiment"], mission:"Maximum intelligence from every earnings call — guidance, tone scoring, analyst concerns, and forward-looking signals within 15 min of publication."},
  {id:3, dept:"public",  num:"03", name:"Stock data analyst",            role:"Market data & pricing intelligence",      skill:"market-analyst-master",      skills:19, status:"active",  runs:287,  last:"30s", tags:["quotes","returns","targets","FX","commod."], cmds:["/stock:quote","/stock:returns","/stock:targets","/stock:fx"],   mission:"Real-time market data across equities, indices, commodities, FX, and prediction markets — the always-on pricing layer feeding all investment decisions."},
  {id:4, dept:"public",  num:"04", name:"Financials analyst",            role:"Financial statements deep-dive",          skill:"financial-analyst-master",   skills:17, status:"active",  runs:41,   last:"12m", tags:["income","balance sheet","cash flow","ESG"],  cmds:["/fin:income","/fin:balance","/fin:cashflow","/fin:health"],    mission:"Institutional-grade financial statement analysis — income statements, balance sheets, cash flows, health scores, ESG ratings for any public company."},
  {id:5, dept:"public",  num:"05", name:"Holdings intelligence",         role:"Institutional ownership analysis",        skill:"market-analyst-master",      skills:4,  status:"idle",   runs:9,    last:"4h",  tags:["13-F","activist","crowding","smart money"],  cmds:["/holdings:top","/holdings:changes","/holdings:activist"],      mission:"Track institutional ownership dynamics — who is buying, selling, activist accumulation signals, and smart-money flow for any public equity."},
  {id:6, dept:"public",  num:"06", name:"Crypto market analyst",         role:"Cryptocurrency market intelligence",      skill:"market-analyst-master",      skills:5,  status:"active",  runs:96,   last:"15m", tags:["BTC","ETH","DeFi","dominance","on-chain"],  cmds:["/crypto:prices","/crypto:btc","/crypto:defi","/crypto:dominance"], mission:"Institutional cryptocurrency market intelligence — prices, market structure, BTC dominance, DeFi TVL, and macro correlation analysis."},
  {id:7, dept:"private", num:"07", name:"Private companies analyst",     role:"Private company research",                skill:"financial-analyst-master",   skills:4,  status:"active",  runs:13,   last:"22m", tags:["firmographics","revenue","tech stack"],      cmds:["/private:tearsheet","/private:competitors","/private:team"],   mission:"Research private company targets — firmographics, revenue estimates, technology stack, executive team, and competitive landscape for investment or acquisition."},
  {id:8, dept:"private", num:"08", name:"Funding intelligence",          role:"VC & PE funding analysis",                skill:"financial-growth",           skills:3,  status:"active",  runs:28,   last:"1h",  tags:["rounds","investors","valuation","runway"],   cmds:["/funding:history","/funding:rounds","/funding:investors"],     mission:"Track and analyse private company funding — round history, investor mapping, valuation step-ups, runway estimates, and sector trend analysis."},
  {id:9, dept:"private", num:"09", name:"Private funds analyst",         role:"Fund manager due diligence",              skill:"financial-analyst-master",   skills:4,  status:"idle",   runs:4,    last:"6h",  tags:["IRR","TVPI","strategy","LP base"],           cmds:["/funds:profile","/funds:performance","/funds:compare"],        mission:"Research PE, VC, hedge funds, and credit managers — fund strategy, AUM, track record, team composition, and LP base for manager due diligence."},
  {id:10,dept:"private", num:"10", name:"Deals intelligence",            role:"M&A, IPO & transaction analytics",        skill:"sec-analyst-master",         skills:5,  status:"active",  runs:19,   last:"45m", tags:["M&A","IPO","S-1","comps","multiples"],       cmds:["/deals:ma","/deals:ipo","/deals:comps","/deals:multiples"],    mission:"Comprehensive M&A and capital markets transaction intelligence — deal flow, multiples, IPO pipeline, precedent transactions, and acquirer strategy."},
  {id:11,dept:"private", num:"11", name:"Investors intelligence",        role:"Investor profiling & networks",           skill:"market-analyst-master",      skills:4,  status:"idle",   runs:7,    last:"3h",  tags:["GP profile","portfolio","active sectors"],   cmds:["/investors:profile","/investors:portfolio","/investors:active"], mission:"Comprehensive intelligence on investors — mandate, portfolio overlap, deal history, key personnel, and relationship mapping for co-investment and fundraising."},
  {id:12,dept:"private", num:"12", name:"Private debt analyst",          role:"Credit & direct lending intelligence",    skill:"sec-debt-covenant",          skills:5,  status:"idle",   runs:3,    last:"8h",  tags:["covenants","maturity wall","Z-score"],       cmds:["/debt:borrower","/debt:covenants","/debt:credit-score"],       mission:"Analyse private credit markets — direct lending, leveraged loans, covenants, maturity walls, and borrower credit quality for credit investment decisions."},
  {id:13,dept:"research",num:"13", name:"Web intelligence agent",        role:"Structured web data extraction",          skill:"earnings-competitive-review",skills:3,  status:"active",  runs:52,   last:"18m", tags:["hiring","pricing","press","regulatory"],     cmds:["/scrape:company","/scrape:jobs","/scrape:pricing"],            mission:"Extract structured intelligence from public websites — job postings as growth signals, pricing intelligence, product announcements, regulatory filings."},
  {id:14,dept:"research",num:"14", name:"Deep research agent",           role:"Multi-source synthesis — all 66 skills",  skill:"All 4 masters",              skills:66, status:"running", runs:2,    last:"now", tags:["initiation","thesis","bull/bear","DCF"],     cmds:["/research:full","/research:thesis","/research:bull","/research:valuation"], mission:"Full-spectrum institutional research by orchestrating all agents — SEC, earnings, financials, market data, private + web synthesised into IC-grade reports."},
  {id:15,dept:"ops",     num:"15", name:"Portfolio monitor",             role:"Real-time portfolio risk & alerts",       skill:"market-analyst-master",      skills:5,  status:"active",  runs:1840, last:"30s", tags:["P&L","risk","beta","VaR","catalysts"],       cmds:["/portfolio:status","/portfolio:pnl","/portfolio:risk"],        mission:"24/7 monitoring of all portfolio positions — price moves, earnings surprises, rating changes, financial health signals, and catalyst tracking."},
  {id:16,dept:"ops",     num:"16", name:"Investment report writer",      role:"Institutional research report authoring", skill:"All 4 masters",              skills:66, status:"active",  runs:5,    last:"35m", tags:["initiation","earnings note","IC memo"],      cmds:["/report:initiation","/report:earnings-note","/report:ic-memo"], mission:"Goldman Sachs-style institutional research — initiations of coverage, earnings notes, investment committee memos, and sector primers."},
  {id:17,dept:"ops",     num:"17", name:"Compliance monitor",           role:"Investment compliance & governance",       skill:"sec-risk-factors",           skills:4,  status:"active",  runs:288,  last:"5m",  tags:["13-F","5% trigger","ESG","position limits"], cmds:["/comply:positions","/comply:13f","/comply:5pct-watch"],        mission:"Continuous investment compliance — position limits, insider restrictions, 13-F obligations, 5% filing triggers, ESG mandates, and breach prevention."},
  {id:18,dept:"ops",     num:"18", name:"Finance intelligence supervisor",role:"Chief orchestrator — all 18 agents",    skill:"All 4 masters",              skills:66, status:"active",  runs:144,  last:"1m",  tags:["briefing","IC pipeline","orchestration"],    cmds:["/intel:briefing","/intel:status","/intel:priorities"],         mission:"Orchestrate all 18 agents — morning briefings, research workflows, IC agenda management, portfolio targets, and highest-conviction opportunity identification."},
];

const SKILL_CATS = {
  "Financial statements":[
    {n:"financial-analyst-master",d:"Full equity research — initiation of coverage",master:true},
    {n:"income-statement",d:"Revenue, EBITDA, Net Income, EPS"},{n:"balance-sheet",d:"Assets, liabilities, equity, net debt"},
    {n:"cash-flow-statement",d:"OCF, FCF, investing, financing"},{n:"income-statement-growth",d:"YoY growth — all P&L items"},
    {n:"balance-sheet-growth",d:"YoY growth — all BS items"},{n:"cash-flow-growth",d:"YoY growth — OCF, FCF, net cash"},
    {n:"financial-growth",d:"Comprehensive multi-metric growth"},{n:"financial-metrics-analysis",d:"Margin analysis and trends"},
    {n:"revenue-product-segmentation",d:"Revenue by product segment"},{n:"revenue-geographic-segmentation",d:"Revenue by geography"},
    {n:"analyst-estimates",d:"Consensus Revenue and EPS estimates"},{n:"financial-health-scores",d:"Altman Z-Score, Piotroski F-Score"},
    {n:"historical-financial-ratings",d:"ROA, ROE, DCF, D/E over time"},{n:"ratings-snapshot",d:"Current financial quality rating"},
    {n:"esg-ratings",d:"MSCI ESG, Sustainalytics, industry rank"},{n:"esg-benchmark-comparison",d:"ESG vs sector — MSCI/S&P/CDP"},
  ],
  "Earnings calls":[
    {n:"earnings-analyst-master",d:"Full earnings digest with attribution",master:true},
    {n:"earnings-call-insights",d:"Future guidance and strategic priorities"},{n:"earnings-call-analysis",d:"Full transcript with follow-up questions"},
    {n:"earnings-financial-guidance",d:"Revenue, margin, EPS guidance"},{n:"earnings-revenue-guidance",d:"Detailed revenue projections"},
    {n:"earnings-mgmt-comments",d:"CEO/CFO comment extraction"},{n:"earnings-qa-analysis",d:"Q&A strategic insights and evasions"},
    {n:"earnings-analyst-questions",d:"Analyst themes and concerns"},{n:"earnings-conf-call-sentiment",d:"Management tone scoring"},
    {n:"earnings-competitive-review",d:"Competitive landscape commentary"},{n:"earnings-capital-allocation",d:"Buybacks, dividends, capex, M&A"},
    {n:"earnings-market-expansion",d:"New market and product signals"},{n:"earnings-cost-mgmt",d:"Restructuring and efficiency analysis"},
    {n:"earnings-product-pipeline",d:"R&D, trials, launch timelines"},
  ],
  "SEC filings":[
    {n:"sec-analyst-master",d:"Full due diligence memo style report",master:true},
    {n:"sec-10k-analysis",d:"Annual filing — full analysis"},{n:"sec-10q-analysis",d:"Quarterly filing analysis"},
    {n:"sec-8k-analysis",d:"Material events extraction"},{n:"sec-s1-analysis",d:"IPO registration — risk and cap table"},
    {n:"sec-risk-factors",d:"All risk factors — extraction and categorisation"},{n:"sec-mda-analysis",d:"MDA narrative and strategy signals"},
    {n:"sec-proxy-analysis",d:"Exec comp and governance quality"},{n:"sec-business-desc-analysis",d:"Business model and moat"},
    {n:"sec-footnotes-analysis",d:"Off-balance-sheet, related parties"},{n:"sec-amendments-review",d:"Material filing changes"},
    {n:"sec-annual-comparison",d:"Year-over-year 10-K diff"},{n:"sec-segment-reporting",d:"Segment margins and geography"},
    {n:"sec-cash-flow-review",d:"Cash flow quality and working capital"},{n:"sec-corp-governance",d:"Board and independence"},
    {n:"sec-debt-covenant",d:"Credit terms and covenant headroom"},
  ],
  "Market & pricing":[
    {n:"market-analyst-master",d:"Full stock and market intelligence report",master:true},
    {n:"stock-quote",d:"Real-time price, volume, 52-week range"},{n:"stock-performance",d:"Daily prices and historical trends"},
    {n:"stock-price-change",d:"Total returns 1D to 10Y"},{n:"stock-historical-index",d:"Index end-of-day history"},
    {n:"company-market-cap",d:"Market cap with size classification"},{n:"batch-market-cap",d:"Market cap — multiple companies"},
    {n:"historical-market-cap",d:"Market cap evolution over time"},{n:"price-target-consensus",d:"Consensus, median, high, low targets"},
    {n:"price-target-summary",d:"Analyst price target trend over time"},{n:"stock-grades",d:"Upgrades, downgrades, initiations"},
    {n:"sector-pe-ratios",d:"Sector P/E for valuation benchmarking"},{n:"industry-pe-ratios",d:"Industry P/E for peer comparisons"},
  ],
  "Market intelligence":[
    {n:"sector-performance-snapshot",d:"Sector returns and momentum"},{n:"industry-performance-snapshot",d:"Industry performance within sectors"},
    {n:"commodities-list",d:"Available commodity data list"},{n:"commodities-quote",d:"Gold, oil, gas, copper — live prices"},
    {n:"forex-list",d:"Available FX pair data"},{n:"prediction-markets-analysis",d:"Kalshi markets — 120+ active events"},
  ],
};

const FEED_DATA = [
  {t:"now", ag:"Transcripts analyst",     ev:"AAPL Q1 2025 earnings digest complete — 14 skills run", type:"ok",   tk:"AAPL"},
  {t:"2m",  ag:"SEC filings analyst",     ev:"New 8-K: MSFT — material acquisition announced",        type:"alert",tk:"MSFT"},
  {t:"5m",  ag:"Portfolio monitor",       ev:"NVDA +4.2% intraday, crossed 3% alert threshold",       type:"alert",tk:"NVDA"},
  {t:"8m",  ag:"Stock data analyst",      ev:"Goldman upgrades META → Buy, PT raised to $620",        type:"info", tk:"META"},
  {t:"12m", ag:"Deep research agent",     ev:"Initiation of coverage complete: AMZN — IC report",     type:"ok",   tk:"AMZN"},
  {t:"18m", ag:"Funding intelligence",    ev:"New Series B: Anthropic competitor raises $180M",       type:"info", tk:null},
  {t:"22m", ag:"Compliance monitor",      ev:"TSLA at 4.5% — approaching 5% filing threshold",        type:"warn", tk:"TSLA"},
  {t:"35m", ag:"Web intelligence",        ev:"Target company job postings +34% — growth signal",      type:"info", tk:null},
  {t:"45m", ag:"Deals intelligence",      ev:"New M&A deal: $12.4B in semiconductor sector",         type:"alert",tk:null},
  {t:"1h",  ag:"Financials analyst",      ev:"GOOG Piotroski F-Score improved to 8/9 — upgrade",     type:"ok",   tk:"GOOG"},
];

const TICKER_ITEMS = [
  {t:"AAPL",v:"+2.4%",up:true},{t:"MSFT",v:"+0.8%",up:true},{t:"NVDA",v:"+4.2%",up:true},
  {t:"META",v:"+1.9%",up:true},{t:"AMZN",v:"-0.6%",up:false},{t:"GOOG",v:"+1.1%",up:true},
  {t:"TSLA",v:"-1.3%",up:false},{t:"JPM",v:"+0.7%",up:true},{t:"BRK.B",v:"+0.3%",up:true},
  {t:"BTC",v:"+3.1%",up:true},{t:"ETH",v:"+2.8%",up:true},{t:"GOLD",v:"+0.4%",up:true},
];

/* ─── CSS-IN-JS STYLE BLOCK ─────────────────────────────────────────────────── */
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

.af-card{
  background:#111422;
  border:1px solid rgba(255,255,255,.07);
  border-radius:10px;
  transition:border-color .18s,background .18s;
}
.af-card:hover{border-color:rgba(255,255,255,.13);background:#151929}

.af-agent{
  border:1px solid rgba(255,255,255,.07);
  border-radius:9px;background:#111422;
  overflow:hidden;cursor:pointer;
  transition:border-color .18s;
  animation:fadeSlideUp .22s ease both;
}
.af-agent:hover{border-color:rgba(255,255,255,.13)}
.af-agent.open{border-color:rgba(201,168,76,.28)}

.af-tab{
  background:transparent;border:none;
  padding:8px 16px;font-family:inherit;
  font-size:12px;font-weight:400;
  color:#8B93A8;cursor:pointer;
  border-bottom:2px solid transparent;
  transition:color .15s,border-color .15s;
  letter-spacing:.02em;
}
.af-tab.on{color:#C9A84C;border-bottom-color:#C9A84C;font-weight:500}
.af-tab:hover:not(.on){color:#E8ECF4}

.af-pill{
  background:transparent;
  border:1px solid rgba(255,255,255,.07);
  border-radius:20px;padding:4px 11px;
  font-family:inherit;font-size:11px;
  color:#8B93A8;cursor:pointer;
  transition:all .15s;
}
.af-pill.on{background:rgba(201,168,76,.1);border-color:rgba(201,168,76,.38);color:#C9A84C}
.af-pill:hover:not(.on){border-color:rgba(255,255,255,.13);color:#E8ECF4}

.af-action{
  background:#C9A84C;border:none;
  border-radius:6px;padding:7px 14px;
  font-family:inherit;font-size:12px;font-weight:500;
  color:#0A0800;cursor:pointer;
  transition:opacity .15s,transform .1s;
  white-space:nowrap;
}
.af-action:hover{opacity:.86}
.af-action:active{transform:scale(.97)}

.af-input{
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08);
  border-radius:6px;padding:7px 11px;
  font-family:'JetBrains Mono',monospace;font-size:12px;
  color:#E8ECF4;outline:none;
  text-transform:uppercase;letter-spacing:.05em;
  transition:border-color .15s;
  width:100px;
}
.af-input::placeholder{color:#4A5168;text-transform:none;letter-spacing:0}
.af-input:focus{border-color:rgba(201,168,76,.42)}

.af-search{
  background:#0D0F1A;
  border:1px solid rgba(255,255,255,.08);
  border-radius:7px;padding:8px 12px;
  font-family:'JetBrains Mono',monospace;font-size:12px;
  color:#E8ECF4;outline:none;
  transition:border-color .15s;width:100%;
}
.af-search::placeholder{color:#4A5168}
.af-search:focus{border-color:rgba(201,168,76,.4)}

.af-skill-row:nth-child(even){background:rgba(255,255,255,.018)}
.af-skill-row:hover{background:rgba(255,255,255,.04)}
.af-feed-row{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.06);animation:fadeSlideUp .2s ease both}
.af-feed-row:last-child{border-bottom:none}
`;

/* ─── HELPERS ─────────────────────────────────────────────────────────────────── */
const getDept = id => DEPTS.find(d => d.id === id) || DEPTS[0];
const totalRuns = AGENTS.reduce((s, a) => s + a.runs, 0);
const activeCount = AGENTS.filter(a => a.status !== "idle").length;

function Dot({ status, size = 7 }) {
  const colors = { active: T.green, running: T.amber, idle: T.txtDim };
  const c = colors[status] || T.txtDim;
  return (
    <span style={{ position:"relative", display:"inline-flex", alignItems:"center",
      justifyContent:"center", width:size, height:size, flexShrink:0 }}>
      {status === "running" && (
        <span style={{ position:"absolute", inset:0, borderRadius:"50%",
          background:c, animation:"pingRing 1.2s ease-out infinite" }} />
      )}
      <span style={{ width:size, height:size, borderRadius:"50%", background:c, display:"block",
        animation: status === "active" ? "pulseGlow 2.4s ease-in-out infinite" : "none" }} />
    </span>
  );
}

function Bar({ value, max, color }) {
  return (
    <div style={{ height:3, background:"rgba(255,255,255,.05)", borderRadius:2, overflow:"hidden" }}>
      <div style={{ width:`${Math.min(100, Math.round(value/max*100))}%`, height:"100%",
        background:color, borderRadius:2, transition:"width .6s ease" }} />
    </div>
  );
}

/* ─── TICKER ─────────────────────────────────────────────────────────────────── */
function Ticker() {
  const items = [...TICKER_ITEMS, ...TICKER_ITEMS];
  return (
    <div style={{ height:28, background:T.surface, borderBottom:`1px solid ${T.border}`,
      overflow:"hidden", display:"flex", alignItems:"center", position:"sticky", top:0, zIndex:50 }}>
      <div style={{ display:"flex", animation:"ticker 22s linear infinite", whiteSpace:"nowrap" }}>
        {items.map((item, i) => (
          <span key={i} style={{ display:"inline-flex", alignItems:"center", gap:5,
            padding:"0 18px", borderRight:`1px solid ${T.border}` }}>
            <span style={{ fontFamily:T.mono, fontSize:10, fontWeight:500,
              color:T.txtMid, letterSpacing:".05em" }}>{item.t}</span>
            <span style={{ fontFamily:T.mono, fontSize:10,
              color:item.up ? T.green : T.red }}>{item.v}</span>
          </span>
        ))}
      </div>
      <div style={{ position:"absolute", right:0, width:80, height:"100%",
        background:`linear-gradient(to right, transparent, ${T.surface})`,
        pointerEvents:"none" }} />
    </div>
  );
}

/* ─── STAT CARD ───────────────────────────────────────────────────────────────── */
function StatCard({ label, value, sub, color }) {
  return (
    <div style={{ background:T.card, border:`1px solid ${T.border}`, borderRadius:10,
      padding:"14px 16px" }}>
      <div style={{ fontSize:9, color:T.txtDim, letterSpacing:".09em",
        textTransform:"uppercase", fontWeight:500, marginBottom:6 }}>{label}</div>
      <div style={{ fontSize:24, fontWeight:300, fontFamily:T.serif,
        color: color || T.gold, lineHeight:1 }}>{value}</div>
      {sub && <div style={{ fontSize:10, color:T.txtDim, marginTop:5 }}>{sub}</div>}
    </div>
  );
}

/* ─── AGENT ROW ───────────────────────────────────────────────────────────────── */
function AgentRow({ agent, expanded, onToggle, i }) {
  const d = getDept(agent.dept);
  return (
    <div className={`af-agent${expanded ? " open" : ""}`}
      style={{ animationDelay:`${i * 0.03}s` }} onClick={onToggle}>
      <div style={{ display:"flex", alignItems:"center", gap:11, padding:"10px 14px" }}>

        <div style={{ width:32, height:32, borderRadius:7, flexShrink:0,
          display:"flex", alignItems:"center", justifyContent:"center",
          background:`${d.color}14`, border:`1px solid ${d.color}28`,
          fontFamily:T.mono, fontSize:10, color:d.color, fontWeight:500 }}>{agent.num}</div>

        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:7 }}>
            <Dot status={agent.status} />
            <span style={{ fontSize:13, fontWeight:500, color:T.txt }}>{agent.name}</span>
            {agent.status === "running" && (
              <span style={{ fontSize:9, padding:"1px 6px", borderRadius:10,
                background:T.amberDim, color:T.amber, letterSpacing:".05em" }}>LIVE</span>
            )}
          </div>
          <div style={{ fontSize:11, color:T.txtMid, marginTop:1 }}>{agent.role}</div>
        </div>

        <span style={{ fontFamily:T.mono, fontSize:10, color:d.color,
          background:`${d.color}12`, padding:"2px 7px", borderRadius:4,
          border:`1px solid ${d.color}22`, flexShrink:0 }}>{agent.skills} skills</span>

        <div style={{ textAlign:"right", flexShrink:0, minWidth:48 }}>
          <div style={{ fontFamily:T.mono, fontSize:11, color:T.txtMid }}>{agent.runs.toLocaleString()}</div>
          <div style={{ fontSize:10, color:T.txtDim }}>{agent.last}</div>
        </div>

        <div style={{ fontSize:10, color:T.txtDim, flexShrink:0,
          transform: expanded ? "rotate(180deg)" : "none",
          transition:"transform .2s" }}>▾</div>
      </div>

      {expanded && (
        <div style={{ borderTop:`1px solid rgba(255,255,255,.06)`,
          padding:"13px 14px 13px 57px",
          background:"rgba(0,0,0,.2)",
          animation:"fadeSlideUp .18s ease both" }}>
          <p style={{ fontSize:12, color:T.txtMid, lineHeight:1.75, marginBottom:11 }}>{agent.mission}</p>
          <div style={{ display:"flex", gap:5, flexWrap:"wrap", marginBottom:9 }}>
            <span style={{ fontFamily:T.mono, fontSize:10, padding:"2px 8px", borderRadius:4,
              background:d.dim, color:d.color, border:`1px solid ${d.color}28`, fontWeight:500 }}>
              {agent.skill}
            </span>
          </div>
          <div style={{ display:"flex", gap:4, flexWrap:"wrap", marginBottom:9 }}>
            {agent.tags.map(tag => (
              <span key={tag} style={{ display:"inline-flex", alignItems:"center",
                padding:"2px 7px", borderRadius:4, fontFamily:T.mono, fontSize:10,
                background:"rgba(255,255,255,.05)", border:`1px solid rgba(255,255,255,.08)`,
                color:T.txtMid, whiteSpace:"nowrap" }}>{tag}</span>
            ))}
          </div>
          <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
            {agent.cmds.map(c => (
              <span key={c} style={{ display:"inline-flex", fontFamily:T.mono, fontSize:10,
                padding:"2px 7px", borderRadius:4, background:T.blueDim,
                border:`1px solid rgba(74,143,255,.22)`, color:T.blue,
                whiteSpace:"nowrap" }}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── PIPELINE ────────────────────────────────────────────────────────────────── */
function Pipeline({ label, steps, active }) {
  return (
    <div className="af-card" style={{ padding:"12px 14px" }}>
      <div style={{ fontSize:10, fontWeight:500, color:T.txtDim, letterSpacing:".07em",
        textTransform:"uppercase", marginBottom:10 }}>{label}</div>
      <div style={{ display:"flex", alignItems:"center" }}>
        {steps.map((step, i) => {
          const done = active === -1 || i < active;
          const now  = i === active;
          const col  = done ? T.green : now ? T.gold : T.txtDim;
          return (
            <div key={i} style={{ display:"flex", alignItems:"center", flex:1 }}>
              <div style={{ flex:1, padding:"5px 5px", borderRadius:5, textAlign:"center",
                fontSize:10, color:col, fontWeight: now ? 500 : 400,
                background: now ? T.goldDim : done ? T.greenDim : "rgba(255,255,255,.03)",
                border:`1px solid ${now ? "rgba(201,168,76,.35)" : done ? "rgba(34,201,132,.25)" : T.border}`,
                animation: now ? "softGlow 2s ease-in-out infinite" : "none",
                lineHeight:1.3 }}>{step}</div>
              {i < steps.length - 1 && (
                <div style={{ width:7, height:1, flexShrink:0,
                  background: done ? T.green : "rgba(255,255,255,.08)" }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ─── FEED ROW ────────────────────────────────────────────────────────────────── */
function FeedRow({ item, i }) {
  const cfg = {
    ok:    { color:T.green,  bg:T.greenDim,  sym:"✓" },
    alert: { color:T.red,    bg:T.redDim,    sym:"!" },
    warn:  { color:T.amber,  bg:T.amberDim,  sym:"⚠" },
    info:  { color:T.blue,   bg:T.blueDim,   sym:"i" },
  }[item.type] || {};
  return (
    <div className="af-feed-row" style={{ animationDelay:`${i * .04}s` }}>
      <div style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, minWidth:28, paddingTop:1 }}>{item.t}</div>
      <div style={{ width:16, height:16, borderRadius:"50%", background:cfg.bg, flexShrink:0,
        display:"flex", alignItems:"center", justifyContent:"center",
        fontSize:8, color:cfg.color, fontWeight:700 }}>{cfg.sym}</div>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:12, color:T.txt, lineHeight:1.45 }}>
          {item.ev}
          {item.tk && (
            <span style={{ marginLeft:6, fontFamily:T.mono, fontSize:9, padding:"1px 5px",
              borderRadius:3, background:cfg.bg, color:cfg.color }}>{item.tk}</span>
          )}
        </div>
        <div style={{ fontSize:10, color:T.txtDim, marginTop:1 }}>{item.ag}</div>
      </div>
    </div>
  );
}

/* ─── APP ─────────────────────────────────────────────────────────────────────── */
export default function App() {
  const [tab, setTab]         = useState("agents");
  const [dept, setDept]       = useState("all");
  const [expanded, setExpanded] = useState(null);
  const [skillCat, setSkillCat] = useState("Financial statements");
  const [search, setSearch]   = useState("");
  const [ticker, setTicker]   = useState("");
  const [feed, setFeed]       = useState(FEED_DATA);

  const visAgents = dept === "all" ? AGENTS : AGENTS.filter(a => a.dept === dept);
  const allSkills = Object.values(SKILL_CATS).flat();
  const shownSkills = search
    ? allSkills.filter(s => s.n.includes(search.toLowerCase()) || s.d.toLowerCase().includes(search.toLowerCase()))
    : SKILL_CATS[skillCat] || [];

  function doResearch() {
    if (!ticker.trim()) return;
    const t = ticker.trim().toUpperCase();
    setFeed(prev => [
      { t:"now", ag:"Deep research agent", ev:`Deep research initiated: ${t} — all 66 skills queued`, type:"alert", tk:t },
      ...prev.slice(0, 9)
    ]);
    setTicker("");
    setTab("feed");
  }

  const TABS = [
    { id:"agents",    l:"Agents" },
    { id:"skills",    l:"Skills · 66" },
    { id:"workflows", l:"Workflows" },
    { id:"feed",      l:"Intelligence feed" },
  ];

  return (
    <>
      <style>{globalCSS}</style>

      {/* ── Sticky ticker ── */}
      <Ticker />

      <div style={{ padding:"20px 20px 44px", maxWidth:900, margin:"0 auto" }}>

        {/* ── Header ── */}
        <div style={{ display:"flex", alignItems:"flex-end", justifyContent:"space-between",
          flexWrap:"wrap", gap:12, marginBottom:22 }}>
          <div>
            <h1 style={{ fontFamily:T.serif, fontWeight:300, fontSize:30, color:T.txt,
              letterSpacing:"-.01em", lineHeight:1.1, fontStyle:"italic" }}>
              Agent<span style={{ color:T.gold }}>Finance</span>
              <span style={{ fontSize:14, fontFamily:T.sans, fontStyle:"normal",
                fontWeight:300, color:T.txtDim, marginLeft:9 }}>v2</span>
            </h1>
            <p style={{ fontSize:11, color:T.txtDim, marginTop:4, letterSpacing:".03em" }}>
              autonomous financial intelligence agency  ·  financial MCP server  ·  Kali Linux
            </p>
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:6 }}>
            <Dot status="active" size={6} />
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.green, letterSpacing:".05em" }}>
              {activeCount} agents live
            </span>
          </div>
        </div>

        {/* ── Stats ── */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:10, marginBottom:18 }}>
          <StatCard label="Total agents"  value="18"                  sub="4 departments"    />
          <StatCard label="Active now"    value={activeCount}         sub="1 running live"   color={T.green} />
          <StatCard label="Skills"        value="66"                  sub="5 categories"     color={T.blue} />
          <StatCard label="Today's runs"  value={totalRuns.toLocaleString()} sub="all agents" color={T.purple} />
        </div>

        {/* ── Research prompt ── */}
        <div style={{ background:T.card, border:`1px solid ${T.border}`, borderRadius:10,
          padding:"11px 14px", marginBottom:16,
          display:"flex", alignItems:"center", gap:10, flexWrap:"wrap" }}>
          <span style={{ fontFamily:T.mono, fontSize:10, color:T.gold, letterSpacing:".07em",
            textTransform:"uppercase", fontWeight:500 }}>Deep research</span>
          <input className="af-input" value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === "Enter" && doResearch()}
            placeholder="e.g. NVDA" />
          <span style={{ fontSize:11, color:T.txtDim, flex:1 }}>
            Orchestrates all 66 skills → IC-grade initiation report in ~18 min
          </span>
          <button className="af-action" onClick={doResearch}>Run ↗</button>
        </div>

        {/* ── Tabs ── */}
        <div style={{ display:"flex", borderBottom:`1px solid ${T.border}`, marginBottom:18 }}>
          {TABS.map(t => (
            <button key={t.id} className={`af-tab${tab === t.id ? " on" : ""}`}
              onClick={() => setTab(t.id)}>{t.l}</button>
          ))}
        </div>

        {/* ════ AGENTS ════ */}
        {tab === "agents" && (
          <div>
            {/* filter pills */}
            <div style={{ display:"flex", gap:6, flexWrap:"wrap", marginBottom:14 }}>
              <button className={`af-pill${dept === "all" ? " on" : ""}`}
                onClick={() => { setDept("all"); setExpanded(null); }}>
                All · {AGENTS.length}
              </button>
              {DEPTS.map(d => (
                <button key={d.id}
                  className={`af-pill${dept === d.id ? " on" : ""}`}
                  style={dept === d.id ? { background:`${d.color}12`, borderColor:`${d.color}38`, color:d.color } : {}}
                  onClick={() => { setDept(d.id); setExpanded(null); }}>
                  <span style={{ marginRight:4, fontSize:10 }}>{d.icon}</span>
                  {d.label} · {AGENTS.filter(a => a.dept === d.id).length}
                </button>
              ))}
            </div>

            {/* dept mini-overview */}
            {dept === "all" && (
              <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8, marginBottom:14 }}>
                {DEPTS.map(d => {
                  const agents = AGENTS.filter(a => a.dept === d.id);
                  const runs   = agents.reduce((s, a) => s + a.runs, 0);
                  const act    = agents.filter(a => a.status !== "idle").length;
                  return (
                    <div key={d.id} className="af-card"
                      style={{ padding:"9px 11px", cursor:"pointer" }}
                      onClick={() => { setDept(d.id); setExpanded(null); }}>
                      <div style={{ display:"flex", alignItems:"center", gap:5, marginBottom:6 }}>
                        <span style={{ fontSize:11, color:d.color }}>{d.icon}</span>
                        <span style={{ fontSize:10, color:T.txtMid, fontWeight:500 }}>{d.label}</span>
                      </div>
                      <Bar value={act} max={agents.length} color={d.color} />
                      <div style={{ display:"flex", justifyContent:"space-between", marginTop:5 }}>
                        <span style={{ fontSize:10, color:T.txtDim }}>{act}/{agents.length} active</span>
                        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>{runs.toLocaleString()}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div style={{ display:"flex", flexDirection:"column", gap:7 }}>
              {visAgents.map((agent, i) => (
                <AgentRow key={agent.id} agent={agent} i={i}
                  expanded={expanded === agent.id}
                  onToggle={() => setExpanded(expanded === agent.id ? null : agent.id)} />
              ))}
            </div>
            <p style={{ fontSize:10, color:T.txtDim, textAlign:"center", marginTop:12 }}>
              Click any agent to expand — mission, master skill, tags, and commands
            </p>
          </div>
        )}

        {/* ════ SKILLS ════ */}
        {tab === "skills" && (
          <div>
            <div style={{ display:"flex", gap:10, flexWrap:"wrap", alignItems:"center", marginBottom:14 }}>
              <input className="af-search" value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search by name or description…"
                style={{ maxWidth:300 }} />
              {!search && (
                <div style={{ display:"flex", gap:5, flexWrap:"wrap" }}>
                  {Object.keys(SKILL_CATS).map(cat => (
                    <button key={cat} className={`af-pill${skillCat === cat ? " on" : ""}`}
                      onClick={() => setSkillCat(cat)}>
                      {cat} · {SKILL_CATS[cat].length}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
              letterSpacing:".08em", marginBottom:10 }}>
              {search ? `${shownSkills.length} matching skills` : `${skillCat} — ${shownSkills.length} skills`}
            </div>

            <div style={{ background:T.card, border:`1px solid ${T.border}`,
              borderRadius:10, overflow:"hidden" }}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 2fr 60px",
                padding:"7px 14px", borderBottom:`1px solid rgba(255,255,255,.06)`,
                background:"rgba(255,255,255,.02)" }}>
                {["Skill name","Description",""].map((h, i) => (
                  <span key={i} style={{ fontSize:9, color:T.txtDim,
                    textTransform:"uppercase", letterSpacing:".08em" }}>{h}</span>
                ))}
              </div>
              {shownSkills.map((s, i) => (
                <div key={i} className="af-skill-row"
                  style={{ display:"grid", gridTemplateColumns:"1fr 2fr 60px",
                    padding:"7px 14px", alignItems:"center" }}>
                  <span style={{ fontFamily:T.mono, fontSize:10,
                    color: s.master ? T.gold : T.blue, fontWeight: s.master ? 500 : 400,
                    wordBreak:"break-all" }}>{s.n}</span>
                  <span style={{ fontSize:11, color:T.txtMid }}>{s.d}</span>
                  {s.master
                    ? <span style={{ fontSize:9, padding:"2px 6px", borderRadius:10,
                        background:T.goldDim, color:T.gold, textAlign:"center",
                        border:`1px solid rgba(201,168,76,.25)` }}>master</span>
                    : <span />
                  }
                </div>
              ))}
            </div>

            <div style={{ marginTop:13, background:T.surface, border:`1px solid ${T.border}`,
              borderRadius:8, padding:"9px 14px", display:"flex", alignItems:"center", gap:10 }}>
              <span style={{ fontSize:11, color:T.txtMid }}>Install all 66 skills:</span>
              <code style={{ fontFamily:T.mono, fontSize:10, color:T.gold,
                background:T.goldDim, padding:"2px 8px", borderRadius:4 }}>
                npx skills add OctagonAI/skills
              </code>
            </div>
          </div>
        )}

        {/* ════ WORKFLOWS ════ */}
        {tab === "workflows" && (
          <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
            <div>
              <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
                letterSpacing:".08em", marginBottom:10 }}>Active pipelines</div>
              <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                <Pipeline label="Earnings intelligence pipeline"
                  steps={["Transcript published","14 skills run","Digest assembled","PM alerted","Note drafted"]}
                  active={2} />
                <Pipeline label="Deep research orchestration"
                  steps={["Idea flagged","SEC + Earnings + Fin","Web intel added","Synthesis","IC report"]}
                  active={4} />
                <Pipeline label="Morning intelligence briefing"
                  steps={["06:00 UTC trigger","All agents polled","Items ranked","Brief compiled","Telegram sent"]}
                  active={-1} />
              </div>
            </div>

            <div>
              <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
                letterSpacing:".08em", marginBottom:10 }}>Investment approval gates</div>
              <div style={{ background:T.card, border:`1px solid ${T.border}`,
                borderRadius:10, overflow:"hidden" }}>
                {[
                  {g:"Auto",      d:"Routine data retrieval, analysis, internal briefings",     c:T.txtMid},
                  {g:"Notify",    d:"Material events, earnings surprises, filing alerts",         c:T.blue},
                  {g:"IC review", d:"New investment ideas, significant position analysis",        c:T.purple},
                  {g:"IC approve",d:"Entry/exit decisions, position sizing, strategy changes",   c:T.amber},
                  {g:"Legal",     d:"MNPI flag, 5%+ threshold, 13-F filing obligations",         c:T.red},
                ].map((row, i) => (
                  <div key={i} style={{ display:"flex", alignItems:"center", gap:14, padding:"9px 14px",
                    borderTop: i === 0 ? "none" : `1px solid rgba(255,255,255,.05)` }}>
                    <div style={{ fontFamily:T.mono, fontSize:10, minWidth:76, color:row.c,
                      background:`${row.c}14`, padding:"2px 7px", borderRadius:4,
                      textAlign:"center", border:`1px solid ${row.c}25`, flexShrink:0 }}>{row.g}</div>
                    <span style={{ fontSize:11, color:T.txtMid }}>{row.d}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
                letterSpacing:".08em", marginBottom:10 }}>Architecture layers</div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
                {[
                  {l:"Financial MCP server",sub:"Live SEC, earnings, market, private markets",col:T.blue},
                  {l:"OpenClaw / OpenCode", sub:"Local AI — source code never leaves server", col:T.green},
                  {l:"n8n webhooks",         sub:"Distribution — alerts, reports, approvals",  col:T.amber},
                  {l:"Paperclip",            sub:"Orchestration — gates, budget, audit trail", col:T.purple},
                ].map(b => (
                  <div key={b.l} style={{ background:T.card, borderRadius:9, padding:"11px 13px",
                    border:`1px solid ${b.col}22`, borderLeft:`3px solid ${b.col}` }}>
                    <div style={{ fontSize:12, fontWeight:500, color:b.col }}>{b.l}</div>
                    <div style={{ fontSize:11, color:T.txtDim, marginTop:3 }}>{b.sub}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ════ FEED ════ */}
        {tab === "feed" && (
          <div>
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:14 }}>
              <Dot status="active" size={6} />
              <span style={{ fontSize:11, color:T.txtMid }}>live intelligence feed</span>
              <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim, marginLeft:"auto" }}>
                {new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}
              </span>
            </div>

            <div style={{ background:T.card, border:`1px solid ${T.border}`,
              borderRadius:10, padding:"4px 14px", marginBottom:20 }}>
              {feed.map((item, i) => <FeedRow key={i} item={item} i={i} />)}
            </div>

            <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
              letterSpacing:".08em", marginBottom:10 }}>Runs today by department</div>
            <div style={{ background:T.card, border:`1px solid ${T.border}`,
              borderRadius:10, padding:"14px" }}>
              <div style={{ display:"flex", flexDirection:"column", gap:13 }}>
                {DEPTS.map(d => {
                  const runs = AGENTS.filter(a => a.dept === d.id).reduce((s, a) => s + a.runs, 0);
                  const pct  = Math.round(runs / totalRuns * 100);
                  return (
                    <div key={d.id}>
                      <div style={{ display:"flex", justifyContent:"space-between",
                        fontSize:11, marginBottom:5 }}>
                        <span style={{ display:"flex", alignItems:"center", gap:5, color:T.txtMid }}>
                          <span style={{ color:d.color }}>{d.icon}</span>{d.label}
                        </span>
                        <span style={{ fontFamily:T.mono, fontSize:10, color:T.txtDim }}>
                          {runs.toLocaleString()} · {pct}%
                        </span>
                      </div>
                      <div style={{ height:4, background:"rgba(255,255,255,.05)", borderRadius:2 }}>
                        <div style={{ width:`${pct}%`, height:"100%", background:d.color,
                          borderRadius:2, transition:"width .7s ease" }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:10, marginTop:14 }}>
              {[
                {l:"Earnings turnaround", v:"14 min", s:"transcript → PM digest"},
                {l:"Deep research time",  v:"~18 min", s:"idea → IC-grade report"},
                {l:"Morning briefing",    v:"06:00 UTC", s:"daily, all agents polled"},
              ].map(m => (
                <div key={m.l} style={{ background:T.card, border:`1px solid ${T.border}`,
                  borderRadius:9, padding:"11px 13px" }}>
                  <div style={{ fontSize:9, color:T.txtDim, textTransform:"uppercase",
                    letterSpacing:".08em", marginBottom:5 }}>{m.l}</div>
                  <div style={{ fontSize:20, fontWeight:300, fontFamily:T.serif,
                    color:T.gold, lineHeight:1 }}>{m.v}</div>
                  <div style={{ fontSize:10, color:T.txtDim, marginTop:5 }}>{m.s}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Footer ── */}
        <div style={{ marginTop:32, paddingTop:14, borderTop:`1px solid ${T.border}`,
          display:"flex", justifyContent:"space-between", alignItems:"center",
          flexWrap:"wrap", gap:8 }}>
          <span style={{ fontFamily:T.mono, fontSize:9, color:T.txtDim }}>
            AgentKits Finance v2 · 18 agents · 66 skills · financial MCP · Paperclip · OpenClaw · n8n · Kali Linux
          </span>
          <div style={{ display:"flex", alignItems:"center", gap:5 }}>
            <Dot status="active" size={5} />
            <span style={{ fontFamily:T.mono, fontSize:10, color:T.green }}>{activeCount}/18 live</span>
          </div>
        </div>

      </div>
    </>
  );
}
