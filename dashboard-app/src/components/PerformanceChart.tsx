// Performance Chart Component
// Displays equity curve and performance metrics over time

export interface PerformanceDataPoint {
  date: string;
  equity: number;
  dailyPnL: number;
  cumulativePnL: number;
}

export interface PerformanceMetrics {
  period: 'day' | 'week' | 'month' | 'year';
  startEquity: number;
  endEquity: number;
  totalReturn: number;
  volatility: number;
  bestDay: number;
  worstDay: number;
  tradingDays: number;
}

interface PerformanceChartProps {
  data: PerformanceDataPoint[];
  metrics: PerformanceMetrics;
  height?: number;
}

const formatCurrency = (value: number): string => {
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(1)}k`;
  }
  return `$${value.toFixed(0)}`;
};

const formatPercent = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

export default function PerformanceChart({ data, metrics, height = 300 }: PerformanceChartProps) {
  // Calculate SVG dimensions
  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartWidth = 800;
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Find min/max values for scaling
  const equityValues = data.map(d => d.equity);
  const minEquity = Math.min(...equityValues) * 0.98;
  const maxEquity = Math.max(...equityValues) * 1.02;
  const equityRange = maxEquity - minEquity;

  // Scale functions
  const scaleX = (index: number) => padding.left + (index / (data.length - 1)) * innerWidth;
  const scaleY = (value: number) => padding.top + innerHeight - ((value - minEquity) / equityRange) * innerHeight;

  // Generate path for equity curve
  const generatePath = (): string => {
    if (data.length === 0) return '';
    
    const points = data.map((d, i) => `${scaleX(i)},${scaleY(d.equity)}`);
    return `M ${points.join(' L ')}`;
  };

  // Generate area fill path
  const generateAreaPath = (): string => {
    if (data.length === 0) return '';
    
    const linePath = generatePath();
    const lastX = scaleX(data.length - 1);
    const firstX = scaleX(0);
    const bottomY = padding.top + innerHeight;
    
    return `${linePath} L ${lastX},${bottomY} L ${firstX},${bottomY} Z`;
  };

  // Generate Y-axis labels
  const yAxisLabels = () => {
    const steps = 5;
    const labels = [];
    for (let i = 0; i <= steps; i++) {
      const value = minEquity + (equityRange * i) / steps;
      labels.push({
        value,
        y: scaleY(value),
      });
    }
    return labels;
  };

  // Generate X-axis labels (dates)
  const xAxisLabels = () => {
    if (data.length === 0) return [];
    
    const labelCount = Math.min(6, data.length);
    const step = Math.floor(data.length / labelCount);
    const labels = [];
    
    for (let i = 0; i < data.length; i += step) {
      labels.push({
        date: data[i].date,
        x: scaleX(i),
      });
    }
    
    // Always include last point
    if (labels[labels.length - 1].x !== scaleX(data.length - 1)) {
      labels.push({
        date: data[data.length - 1].date,
        x: scaleX(data.length - 1),
      });
    }
    
    return labels;
  };

  // Determine if equity is positive overall
  const isPositive = data.length > 0 && data[data.length - 1].equity >= data[0].equity;
  const curveColor = isPositive ? 'var(--accent-green)' : 'var(--accent-red)';
  const areaColor = isPositive ? 'rgba(0, 186, 124, 0.15)' : 'rgba(244, 33, 46, 0.15)';

  return (
    <div className="performance-chart">
      {/* Chart Header */}
      <div className="chart-header">
        <div className="chart-title">Equity Curve</div>
        <div className="chart-metrics">
          <div className="chart-metric">
            <span className="metric-label">Total Return</span>
            <span className={`metric-value ${metrics.totalReturn >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(metrics.totalReturn)}
            </span>
          </div>
          <div className="chart-metric">
            <span className="metric-label">Volatility</span>
            <span className="metric-value">{metrics.volatility.toFixed(2)}%</span>
          </div>
          <div className="chart-metric">
            <span className="metric-label">Trading Days</span>
            <span className="metric-value">{metrics.tradingDays}</span>
          </div>
        </div>
      </div>

      {/* SVG Chart */}
      <div className="chart-container">
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="equity-chart">
          {/* Grid lines */}
          {yAxisLabels().map((label, i) => (
            <g key={`grid-${i}`}>
              <line
                x1={padding.left}
                y1={label.y}
                x2={chartWidth - padding.right}
                y2={label.y}
                stroke="var(--border-color)"
                strokeWidth="1"
                strokeDasharray="4,4"
                opacity="0.5"
              />
              <text
                x={padding.left - 10}
                y={label.y + 4}
                textAnchor="end"
                fill="var(--text-secondary)"
                fontSize="11"
              >
                {formatCurrency(label.value)}
              </text>
            </g>
          ))}

          {/* Area fill */}
          <path
            d={generateAreaPath()}
            fill={areaColor}
          />

          {/* Equity curve line */}
          <path
            d={generatePath()}
            fill="none"
            stroke={curveColor}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Start point */}
          {data.length > 0 && (
            <circle
              cx={scaleX(0)}
              cy={scaleY(data[0].equity)}
              r="4"
              fill={curveColor}
            />
          )}

          {/* End point */}
          {data.length > 0 && (
            <circle
              cx={scaleX(data.length - 1)}
              cy={scaleY(data[data.length - 1].equity)}
              r="4"
              fill={curveColor}
            />
          )}

          {/* X-axis labels */}
          {xAxisLabels().map((label, i) => (
            <text
              key={`x-${i}`}
              x={label.x}
              y={chartHeight - 10}
              textAnchor="middle"
              fill="var(--text-secondary)"
              fontSize="11"
            >
              {label.date}
            </text>
          ))}
        </svg>
      </div>

      {/* Performance Stats */}
      <div className="chart-stats">
        <div className="chart-stat">
          <span className="stat-label">Best Day</span>
          <span className="stat-value positive">+{formatCurrency(metrics.bestDay)}</span>
        </div>
        <div className="chart-stat">
          <span className="stat-label">Worst Day</span>
          <span className="stat-value negative">{formatCurrency(metrics.worstDay)}</span>
        </div>
        <div className="chart-stat">
          <span className="stat-label">Start</span>
          <span className="stat-value">{formatCurrency(metrics.startEquity)}</span>
        </div>
        <div className="chart-stat">
          <span className="stat-label">End</span>
          <span className="stat-value">{formatCurrency(metrics.endEquity)}</span>
        </div>
      </div>
    </div>
  );
}

// Generate mock performance data
export function generateMockPerformanceData(days: number = 30): { data: PerformanceDataPoint[], metrics: PerformanceMetrics } {
  const data: PerformanceDataPoint[] = [];
  let equity = 100000;
  const startEquity = equity;
  
  // Generate dates for the past N days
  const today = new Date();
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    
    // Random daily P&L with slight positive bias
    const dailyReturn = (Math.random() - 0.45) * 0.03; // Slight positive bias
    const dailyPnL = equity * dailyReturn;
    equity += dailyPnL;
    
    data.push({
      date: dateStr,
      equity: equity,
      dailyPnL: dailyPnL,
      cumulativePnL: equity - startEquity,
    });
  }

  const dailyPnLs = data.map(d => d.dailyPnL);
  const bestDay = Math.max(...dailyPnLs);
  const worstDay = Math.min(...dailyPnLs);
  const avgDailyReturn = dailyPnLs.reduce((a, b) => a + b, 0) / dailyPnLs.length;
  const stdDev = Math.sqrt(dailyPnLs.map(x => Math.pow(x - avgDailyReturn, 2)).reduce((a, b) => a + b, 0) / dailyPnLs.length);
  const volatility = (stdDev / startEquity) * 100;

  const metrics: PerformanceMetrics = {
    period: 'month',
    startEquity: startEquity,
    endEquity: equity,
    totalReturn: ((equity - startEquity) / startEquity) * 100,
    volatility: volatility,
    bestDay: bestDay,
    worstDay: worstDay,
    tradingDays: days + 1,
  };

  return { data, metrics };
}