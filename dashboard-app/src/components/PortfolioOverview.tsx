// Portfolio Overview Component
// Displays portfolio summary with key metrics

export interface PortfolioMetrics {
  totalEquity: number;
  dailyPnL: number;
  weeklyPnL: number;
  monthlyPnL: number;
  openPositions: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  maxDrawdown: number;
  SharpeRatio: number;
}

interface PortfolioOverviewProps {
  metrics: PortfolioMetrics;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

export default function PortfolioOverview({ metrics }: PortfolioOverviewProps) {
  const isPositive = (value: number) => value >= 0;

  return (
    <div className="portfolio-overview">
      {/* Main Equity Card */}
      <div className="portfolio-main-card">
        <div className="portfolio-label">Total Equity</div>
        <div className="portfolio-value">{formatCurrency(metrics.totalEquity)}</div>
        <div className="portfolio-change-row">
          <span className={`portfolio-change ${isPositive(metrics.dailyPnL) ? 'positive' : 'negative'}`}>
            Today: {formatCurrency(metrics.dailyPnL)} ({formatPercent((metrics.dailyPnL / metrics.totalEquity) * 100)})
          </span>
          <span className={`portfolio-change ${isPositive(metrics.weeklyPnL) ? 'positive' : 'negative'}`}>
            This Week: {formatCurrency(metrics.weeklyPnL)}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="portfolio-stats-grid">
        <div className="portfolio-stat">
          <div className="portfolio-stat-label">Open Positions</div>
          <div className="portfolio-stat-value">{metrics.openPositions}</div>
        </div>
        <div className="portfolio-stat">
          <div className="portfolio-stat-label">Win Rate</div>
          <div className="portfolio-stat-value" style={{ color: metrics.winRate >= 50 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
            {metrics.winRate.toFixed(1)}%
          </div>
        </div>
        <div className="portfolio-stat">
          <div className="portfolio-stat-label">Profit Factor</div>
          <div className="portfolio-stat-value" style={{ color: metrics.profitFactor >= 1.5 ? 'var(--accent-green)' : 'var(--accent-gold)' }}>
            {metrics.profitFactor.toFixed(2)}
          </div>
        </div>
        <div className="portfolio-stat">
          <div className="portfolio-stat-label">Sharpe Ratio</div>
          <div className="portfolio-stat-value" style={{ color: metrics.SharpeRatio >= 1 ? 'var(--accent-green)' : 'var(--text-secondary)' }}>
            {metrics.SharpeRatio.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Win/Loss Details */}
      <div className="portfolio-details">
        <div className="portfolio-detail-row">
          <span className="detail-label">Average Win</span>
          <span className="detail-value positive">{formatCurrency(metrics.avgWin)}</span>
        </div>
        <div className="portfolio-detail-row">
          <span className="detail-label">Average Loss</span>
          <span className="detail-value negative">{formatCurrency(metrics.avgLoss)}</span>
        </div>
        <div className="portfolio-detail-row">
          <span className="detail-label">Max Drawdown</span>
          <span className="detail-value negative">{formatCurrency(metrics.maxDrawdown)}</span>
        </div>
        <div className="portfolio-detail-row">
          <span className="detail-label">Monthly P&L</span>
          <span className={`detail-value ${isPositive(metrics.monthlyPnL) ? 'positive' : 'negative'}`}>
            {formatCurrency(metrics.monthlyPnL)}
          </span>
        </div>
      </div>

      {/* Win Rate Bar */}
      <div className="winrate-section">
        <div className="winrate-header">
          <span className="winrate-label">Win Rate Distribution</span>
          <span className="winrate-value">{metrics.winRate.toFixed(1)}%</span>
        </div>
        <div className="winrate-bar">
          <div
            className="winrate-fill"
            style={{
              width: `${metrics.winRate}%`,
              backgroundColor: metrics.winRate >= 50 ? 'var(--accent-green)' : 'var(--accent-red)',
            }}
          />
        </div>
        <div className="winrate-labels">
          <span>0%</span>
          <span>25%</span>
          <span>50%</span>
          <span>75%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}

// Default mock data for preview
export const DEFAULT_PORTFOLIO_METRICS: PortfolioMetrics = {
  totalEquity: 125430.50,
  dailyPnL: 1245.50,
  weeklyPnL: 3890.25,
  monthlyPnL: 12450.00,
  openPositions: 3,
  winRate: 62.5,
  avgWin: 450.00,
  avgLoss: -225.00,
  profitFactor: 2.0,
  maxDrawdown: -3250.00,
  SharpeRatio: 1.45,
};