import { useState, useEffect } from 'react';
import SignalCard from '../components/SignalCard';
import DebateOutcome, { Signal } from '../components/DebateOutcome';

// Mock signals data (would come from API in real app)
const generateMockSignals = (): Signal[] => {
  const signals: Signal[] = [
    {
      id: 'sig-001',
      symbol: 'EURUSD',
      strategy: 'ICT-02 PD Array FVG',
      direction: 'LONG',
      status: 'approved',
      entryPrice: 1.0875,
      targetPrice: 1.0920,
      stopLoss: 1.0840,
      confidence: 82,
      votes: { bull: 2, bear: 0, neutral: 1 },
      confluenceCount: 5,
      timeRemaining: '12m remaining',
      sector: 'forex',
      createdAt: '2026-04-29T14:30:00Z',
      debateArguments: [
        {
          role: 'bull',
          argument: 'Strong bullish momentum with confirmed FVG at 1.0860-1.0865. OTE 70.5% zone aligned with kill zone entry. Order block quality rank 2.',
          timestamp: '14:32:15',
          keyPoints: ['FVG strength: 2/5', 'OB quality: rank 2', 'Kill zone: London Open active'],
        },
        {
          role: 'bear',
          argument: 'HTF structure shows potential bearish divergence. Recent high at 1.0890 may act as resistance. Recommend caution on position size.',
          timestamp: '14:33:22',
          keyPoints: ['HTF resistance: 1.0890', 'Potential divergence', 'Reduce size to 75%'],
        },
        {
          role: 'neutral',
          argument: 'Risk assessment complete. Spread within normal range (1.2 pips). No high-impact news within 30 min. Checklist score: 8/9.',
          timestamp: '14:34:10',
          keyPoints: ['Spread: 1.2 pips', 'News window: clear', 'Checklist: 8/9'],
        },
        {
          role: 'fund_manager',
          argument: 'APPROVED - LONG EURUSD. Strong confluence from 5 departments. FVG and OB quality meet threshold. Confidence: 82%. Position size: 100%.',
          timestamp: '14:35:00',
          keyPoints: ['Decision: APPROVED', 'Confidence: 82%', 'Size: 100%'],
        },
      ],
    },
    {
      id: 'sig-002',
      symbol: 'XAUUSD',
      strategy: 'ICT-08 Discount Premium',
      direction: 'LONG',
      status: 'pending',
      entryPrice: 2342.50,
      targetPrice: 2380.00,
      stopLoss: 2320.00,
      confidence: 71,
      votes: { bull: 2, bear: 1, neutral: 0 },
      confluenceCount: 4,
      timeRemaining: '45m remaining',
      sector: 'commodities',
      createdAt: '2026-04-29T14:15:00Z',
    },
    {
      id: 'sig-003',
      symbol: 'BTCUSD',
      strategy: 'ICT-01 Micro Sweep',
      direction: 'SHORT',
      status: 'rejected',
      entryPrice: 64100,
      targetPrice: 63500,
      stopLoss: 64800,
      confidence: 58,
      votes: { bull: 1, bear: 2, neutral: 0 },
      confluenceCount: 2,
      timeRemaining: 'expired',
      sector: 'crypto',
      createdAt: '2026-04-29T13:45:00Z',
    },
    {
      id: 'sig-004',
      symbol: 'GBPUSD',
      strategy: 'ICT-05 CHoCH Momentum',
      direction: 'LONG',
      status: 'approved',
      entryPrice: 1.2680,
      targetPrice: 1.2750,
      stopLoss: 1.2620,
      confidence: 78,
      votes: { bull: 2, bear: 0, neutral: 1 },
      confluenceCount: 4,
      timeRemaining: '3h 20m remaining',
      sector: 'forex',
      createdAt: '2026-04-29T12:00:00Z',
    },
    {
      id: 'sig-005',
      symbol: 'SPX',
      strategy: 'ICT-07 HTF Structure',
      direction: 'NO_TRADE',
      status: 'pending',
      entryPrice: 5125.00,
      confidence: 45,
      votes: { bull: 1, bear: 1, neutral: 1 },
      confluenceCount: 2,
      timeRemaining: '1h remaining',
      sector: 'indices',
      createdAt: '2026-04-29T14:00:00Z',
    },
    {
      id: 'sig-006',
      symbol: 'ETHUSD',
      strategy: 'Breakout Trading',
      direction: 'LONG',
      status: 'expired',
      entryPrice: 3480.00,
      targetPrice: 3550.00,
      stopLoss: 3420.00,
      confidence: 62,
      votes: { bull: 1, bear: 1, neutral: 1 },
      confluenceCount: 3,
      timeRemaining: 'expired',
      sector: 'crypto',
      createdAt: '2026-04-29T10:30:00Z',
    },
    {
      id: 'sig-007',
      symbol: 'XTIUSD',
      strategy: 'ICT-03 Kill Zone Pulse',
      direction: 'SHORT',
      status: 'approved',
      entryPrice: 77.80,
      targetPrice: 76.50,
      stopLoss: 78.90,
      confidence: 85,
      votes: { bull: 0, bear: 3, neutral: 0 },
      confluenceCount: 6,
      timeRemaining: '25m remaining',
      sector: 'commodities',
      createdAt: '2026-04-29T14:25:00Z',
    },
    {
      id: 'sig-008',
      symbol: 'AUDJPY',
      strategy: 'ICT-04 Weekly Bias',
      direction: 'LONG',
      status: 'pending',
      entryPrice: 98.20,
      targetPrice: 99.00,
      stopLoss: 97.50,
      confidence: 69,
      votes: { bull: 2, bear: 0, neutral: 1 },
      confluenceCount: 4,
      timeRemaining: '2h remaining',
      sector: 'forex',
      createdAt: '2026-04-29T13:00:00Z',
    },
  ];
  return signals;
};

type SectorFilter = 'all' | 'forex' | 'commodities' | 'indices' | 'crypto' | 'stocks';
type StatusFilter = 'all' | 'pending' | 'approved' | 'rejected' | 'expired';

export default function Signals() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [sectorFilter, setSectorFilter] = useState<SectorFilter>('all');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    setSignals(generateMockSignals());
    setLastUpdate(new Date().toLocaleTimeString());
  }, []);

  const filteredSignals = signals.filter((signal) => {
    const matchesSector = sectorFilter === 'all' || signal.sector === sectorFilter;
    const matchesStatus = statusFilter === 'all' || signal.status === statusFilter;
    return matchesSector && matchesStatus;
  });

  const stats = {
    total: signals.length,
    pending: signals.filter((s) => s.status === 'pending').length,
    approved: signals.filter((s) => s.status === 'approved').length,
    rejected: signals.filter((s) => s.status === 'rejected').length,
    avgConfidence: Math.round(
      signals.reduce((acc, s) => acc + s.confidence, 0) / signals.length
    ),
  };

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">📈 Signals</h1>
        <p className="page-subtitle">
          Trade signals with debate outcomes • Last updated: {lastUpdate}
        </p>
      </header>

      {/* Stats Grid */}
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-label">Total Signals</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending</div>
          <div className="stat-value" style={{ color: 'var(--accent-gold)' }}>
            {stats.pending}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Approved</div>
          <div className="stat-value green">{stats.approved}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Confidence</div>
          <div className="stat-value" style={{ color: 'var(--accent-blue)' }}>
            {stats.avgConfidence}%
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="signals-filters">
        <div className="filter-group">
          <label className="filter-label">Sector</label>
          <div className="filter-buttons">
            {(['all', 'forex', 'commodities', 'indices', 'crypto', 'stocks'] as SectorFilter[]).map(
              (sector) => (
                <button
                  key={sector}
                  className={`filter-btn ${sectorFilter === sector ? 'active' : ''}`}
                  onClick={() => setSectorFilter(sector)}
                >
                  {sector === 'all' ? 'All Sectors' : sector.charAt(0).toUpperCase() + sector.slice(1)}
                </button>
              )
            )}
          </div>
        </div>
        <div className="filter-group">
          <label className="filter-label">Status</label>
          <div className="filter-buttons">
            {(['all', 'pending', 'approved', 'rejected', 'expired'] as StatusFilter[]).map(
              (status) => (
                <button
                  key={status}
                  className={`filter-btn ${statusFilter === status ? 'active' : ''}`}
                  onClick={() => setStatusFilter(status)}
                >
                  {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Signals Grid */}
      <div className="signals-container">
        <div className="signals-grid">
          {filteredSignals.map((signal) => (
            <SignalCard
              key={signal.id}
              signal={signal}
              onClick={() => setSelectedSignal(signal)}
            />
          ))}
        </div>
        {filteredSignals.length === 0 && (
          <div className="no-signals">
            <p>No signals match the selected filters.</p>
          </div>
        )}
      </div>

      {/* Debate Outcome Modal */}
      {selectedSignal && (
        <div className="modal-overlay" onClick={() => setSelectedSignal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Signal Details: {selectedSignal.symbol}</h2>
              <button className="modal-close" onClick={() => setSelectedSignal(null)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <DebateOutcome signal={selectedSignal} expanded={true} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}