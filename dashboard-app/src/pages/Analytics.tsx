import { useState, useEffect } from 'react';
import PortfolioOverview, { PortfolioMetrics, DEFAULT_PORTFOLIO_METRICS } from '../components/PortfolioOverview';
import PerformanceChart, { generateMockPerformanceData, PerformanceDataPoint, PerformanceMetrics } from '../components/PerformanceChart';

// Win rate data by strategy
interface StrategyWinRate {
  strategy: string;
  wins: number;
  losses: number;
  total: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
  totalPnL: number;
}

// Sector performance data
interface SectorPerformance {
  sector: string;
  icon: string;
  trades: number;
  winRate: number;
  pnl: number;
  avgTrade: number;
}

export default function Analytics() {
  const [timeframe, setTimeframe] = useState<'day' | 'week' | 'month' | 'year'>('month');
  const [portfolioMetrics, setPortfolioMetrics] = useState<PortfolioMetrics>(DEFAULT_PORTFOLIO_METRICS);
  const [performanceData, setPerformanceData] = useState<PerformanceDataPoint[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [strategyWinRates, setStrategyWinRates] = useState<StrategyWinRate[]>([]);
  const [sectorPerformance, setSectorPerformance] = useState<SectorPerformance[]>([]);

  useEffect(() => {
    // Generate mock performance data based on timeframe
    const days = timeframe === 'day' ? 1 : timeframe === 'week' ? 7 : timeframe === 'month' ? 30 : 365;
    const { data, metrics } = generateMockPerformanceData(days);
    setPerformanceData(data);
    setPerformanceMetrics(metrics);

    // Generate mock portfolio metrics
    setPortfolioMetrics({
      ...DEFAULT_PORTFOLIO_METRICS,
      totalEquity: metrics.endEquity,
      dailyPnL: data[data.length - 1]?.dailyPnL || 0,
      weeklyPnL: data.slice(-7).reduce((sum, d) => sum + d.dailyPnL, 0),
      monthlyPnL: data.slice(-30).reduce((sum, d) => sum + d.dailyPnL, 0),
    });

    // Generate mock strategy win rates
    setStrategyWinRates([
      { strategy: 'ICT-01 Micro-Sweep', wins: 15, losses: 8, total: 23, winRate: 65.2, avgWin: 125, avgLoss: -85, totalPnL: 845 },
      { strategy: 'ICT-02 PD Array FVG', wins: 12, losses: 7, total: 19, winRate: 63.2, avgWin: 150, avgLoss: -90, totalPnL: 720 },
      { strategy: 'ICT-03 Kill-Zone Pulse', wins: 18, losses: 12, total: 30, winRate: 60.0, avgWin: 200, avgLoss: -120, totalPnL: 960 },
      { strategy: 'ICT-05 CHoCH Swing', wins: 8, losses: 5, total: 13, winRate: 61.5, avgWin: 350, avgLoss: -180, totalPnL: 1420 },
      { strategy: 'ICT-07 HTF Structure', wins: 5, losses: 2, total: 7, winRate: 71.4, avgWin: 550, avgLoss: -250, totalPnL: 1750 },
      { strategy: 'MACD Divergence', wins: 10, losses: 8, total: 18, winRate: 55.6, avgWin: 180, avgLoss: -95, totalPnL: 620 },
      { strategy: 'VIX-EMA Crossover', wins: 6, losses: 4, total: 10, winRate: 60.0, avgWin: 220, avgLoss: -140, totalPnL: 520 },
      { strategy: 'Range Trading', wins: 9, losses: 6, total: 15, winRate: 60.0, avgWin: 140, avgLoss: -80, totalPnL: 540 },
    ]);

    // Generate mock sector performance
    setSectorPerformance([
      { sector: 'Forex', icon: '💱', trades: 45, winRate: 64.4, pnl: 2850, avgTrade: 63.3 },
      { sector: 'Commodities', icon: '🥇', trades: 22, winRate: 68.2, pnl: 1920, avgTrade: 87.3 },
      { sector: 'Indices', icon: '📈', trades: 18, winRate: 61.1, pnl: 1150, avgTrade: 63.9 },
      { sector: 'Crypto', icon: '₿', trades: 31, winRate: 58.1, pnl: 980, avgTrade: 31.6 },
      { sector: 'Stocks', icon: '📊', trades: 12, winRate: 66.7, pnl: 720, avgTrade: 60.0 },
    ]);
  }, [timeframe]);

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  return (
    <div className="analytics-page">
      <header className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Performance metrics and trading statistics</p>
      </header>

      {/* Timeframe Selector */}
      <div className="timeframe-selector">
        <span className="timeframe-label">Time Period:</span>
        <div className="timeframe-buttons">
          {(['day', 'week', 'month', 'year'] as const).map((tf) => (
            <button
              key={tf}
              className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
              onClick={() => setTimeframe(tf)}
            >
              {tf.charAt(0).toUpperCase() + tf.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Portfolio Overview */}
      <section className="analytics-section">
        <h2 className="section-title">Portfolio Overview</h2>
        <PortfolioOverview metrics={portfolioMetrics} />
      </section>

      {/* Performance Chart */}
      <section className="analytics-section">
        <h2 className="section-title">Performance</h2>
        {performanceMetrics && (
          <PerformanceChart
            data={performanceData}
            metrics={performanceMetrics}
            height={320}
          />
        )}
      </section>

      {/* Strategy Win Rates */}
      <section className="analytics-section">
        <h2 className="section-title">Strategy Performance</h2>
        <div className="strategy-table">
          <div className="table-header">
            <span>Strategy</span>
            <span>Trades</span>
            <span>Win Rate</span>
            <span>Avg Win</span>
            <span>Avg Loss</span>
            <span>P&L</span>
          </div>
          {strategyWinRates.map((strategy, index) => (
            <div key={index} className="table-row">
              <span className="strategy-name">{strategy.strategy}</span>
              <span className="strategy-trades">{strategy.total}</span>
              <span
                className="strategy-winrate"
                style={{ color: strategy.winRate >= 60 ? 'var(--accent-green)' : strategy.winRate >= 50 ? 'var(--accent-gold)' : 'var(--accent-red)' }}
              >
                {strategy.winRate.toFixed(1)}%
              </span>
              <span className="strategy-avgwin positive">{formatCurrency(strategy.avgWin)}</span>
              <span className="strategy-avgloss negative">{formatCurrency(strategy.avgLoss)}</span>
              <span className={`strategy-pnl ${strategy.totalPnL >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(strategy.totalPnL)}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Sector Performance */}
      <section className="analytics-section">
        <h2 className="section-title">Performance by Sector</h2>
        <div className="sector-grid">
          {sectorPerformance.map((sector, index) => (
            <div key={index} className="sector-card">
              <div className="sector-header">
                <span className="sector-icon">{sector.icon}</span>
                <span className="sector-name">{sector.sector}</span>
              </div>
              <div className="sector-stats">
                <div className="sector-stat">
                  <span className="stat-label">Trades</span>
                  <span className="stat-value">{sector.trades}</span>
                </div>
                <div className="sector-stat">
                  <span className="stat-label">Win Rate</span>
                  <span className="stat-value" style={{ color: sector.winRate >= 60 ? 'var(--accent-green)' : 'var(--accent-gold)' }}>
                    {sector.winRate.toFixed(1)}%
                  </span>
                </div>
                <div className="sector-stat">
                  <span className="stat-label">Total P&L</span>
                  <span className={`stat-value ${sector.pnl >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(sector.pnl)}
                  </span>
                </div>
                <div className="sector-stat">
                  <span className="stat-label">Avg Trade</span>
                  <span className={`stat-value ${sector.avgTrade >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(sector.avgTrade)}
                  </span>
                </div>
              </div>
              <div className="sector-winrate-bar">
                <div
                  className="sector-winrate-fill"
                  style={{
                    width: `${sector.winRate}%`,
                    backgroundColor: sector.winRate >= 60 ? 'var(--accent-green)' : sector.winRate >= 50 ? 'var(--accent-gold)' : 'var(--accent-red)',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Win Rate Tracking */}
      <section className="analytics-section">
        <h2 className="section-title">Win Rate Tracking</h2>
        <div className="winrate-tracking">
          <div className="winrate-card overall">
            <div className="winrate-card-label">Overall Win Rate</div>
            <div className="winrate-card-value" style={{ color: 'var(--accent-green)' }}>
              {portfolioMetrics.winRate.toFixed(1)}%
            </div>
            <div className="winrate-card-subtitle">
              {Math.round(portfolioMetrics.winRate * portfolioMetrics.openPositions / 100)} / {portfolioMetrics.openPositions} trades
            </div>
          </div>
          <div className="winrate-card">
            <div className="winrate-card-label">Average Win</div>
            <div className="winrate-card-value positive">{formatCurrency(portfolioMetrics.avgWin)}</div>
          </div>
          <div className="winrate-card">
            <div className="winrate-card-label">Average Loss</div>
            <div className="winrate-card-value negative">{formatCurrency(portfolioMetrics.avgLoss)}</div>
          </div>
          <div className="winrate-card">
            <div className="winrate-card-label">Profit Factor</div>
            <div className="winrate-card-value" style={{ color: portfolioMetrics.profitFactor >= 1.5 ? 'var(--accent-green)' : 'var(--accent-gold)' }}>
              {portfolioMetrics.profitFactor.toFixed(2)}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}