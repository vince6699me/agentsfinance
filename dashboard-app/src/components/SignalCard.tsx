import { Signal, SignalStatus } from './DebateOutcome';

interface SignalCardProps {
  signal: Signal;
  onClick?: () => void;
}

const getStatusColor = (status: SignalStatus): string => {
  switch (status) {
    case 'approved':
      return 'var(--accent-green)';
    case 'rejected':
      return 'var(--accent-red)';
    case 'pending':
      return 'var(--accent-gold)';
    case 'expired':
      return 'var(--text-secondary)';
    default:
      return 'var(--text-secondary)';
  }
};

const getStatusLabel = (status: SignalStatus): string => {
  switch (status) {
    case 'approved':
      return 'Approved';
    case 'rejected':
      return 'Rejected';
    case 'pending':
      return 'Pending';
    case 'expired':
      return 'Expired';
    default:
      return status;
  }
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return 'var(--accent-green)';
  if (confidence >= 65) return 'var(--accent-gold)';
  return 'var(--accent-red)';
};

const getDirectionIcon = (direction: string): string => {
  switch (direction) {
    case 'LONG':
      return '🟢';
    case 'SHORT':
      return '🔴';
    default:
      return '⚪';
  }
};

const getDirectionColor = (direction: string): string => {
  switch (direction) {
    case 'LONG':
      return 'var(--accent-green)';
    case 'SHORT':
      return 'var(--accent-red)';
    default:
      return 'var(--text-secondary)';
  }
};

export default function SignalCard({ signal, onClick }: SignalCardProps) {
  const confidenceColor = getConfidenceColor(signal.confidence);
  const directionColor = getDirectionColor(signal.direction);

  return (
    <div className="signal-card" onClick={onClick}>
      {/* Header */}
      <div className="signal-header">
        <div className="signal-instrument">
          <span className="signal-symbol">{signal.symbol}</span>
          <span className="signal-strategy">{signal.strategy}</span>
        </div>
        <span
          className="signal-status"
          style={{ color: getStatusColor(signal.status), borderColor: getStatusColor(signal.status) }}
        >
          {getStatusLabel(signal.status)}
        </span>
      </div>

      {/* Direction and Price */}
      <div className="signal-direction-row">
        <div className="signal-direction">
          <span className="direction-icon">{getDirectionIcon(signal.direction)}</span>
          <span className="direction-label" style={{ color: directionColor }}>
            {signal.direction}
          </span>
        </div>
        <div className="signal-price">
          <span className="entry-price">Entry: {signal.entryPrice.toFixed(signal.entryPrice < 10 ? 4 : 2)}</span>
          {signal.targetPrice && (
            <span className="target-price">Target: {signal.targetPrice.toFixed(signal.targetPrice < 10 ? 4 : 2)}</span>
          )}
        </div>
      </div>

      {/* Confidence Score */}
      <div className="signal-confidence">
        <div className="confidence-header">
          <span className="confidence-label">Confidence</span>
          <span className="confidence-value" style={{ color: confidenceColor }}>
            {signal.confidence}%
          </span>
        </div>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{
              width: `${signal.confidence}%`,
              backgroundColor: confidenceColor,
            }}
          />
        </div>
      </div>

      {/* Bull/Bear/Neutral Votes */}
      <div className="signal-votes">
        <div className="vote-item bull">
          <span className="vote-icon">🐂</span>
          <span className="vote-label">Bull</span>
          <span className="vote-count">{signal.votes.bull}</span>
          <div className="vote-bar">
            <div
              className="vote-fill"
              style={{ width: `${(signal.votes.bull / 3) * 100}%` }}
            />
          </div>
        </div>
        <div className="vote-item bear">
          <span className="vote-icon">🐻</span>
          <span className="vote-label">Bear</span>
          <span className="vote-count">{signal.votes.bear}</span>
          <div className="vote-bar">
            <div
              className="vote-fill"
              style={{ width: `${(signal.votes.bear / 3) * 100}%` }}
            />
          </div>
        </div>
        <div className="vote-item neutral">
          <span className="vote-icon">⚪</span>
          <span className="vote-label">Neutral</span>
          <span className="vote-count">{signal.votes.neutral}</span>
          <div className="vote-bar">
            <div
              className="vote-fill"
              style={{ width: `${(signal.votes.neutral / 3) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="signal-meta">
        <span className="meta-item">
          <span className="meta-icon">⏱️</span>
          {signal.timeRemaining}
        </span>
        <span className="meta-item">
          <span className="meta-icon">📊</span>
          {signal.confluenceCount}/6 depts
        </span>
        <span className="meta-item">
          <span className="meta-icon">🏷️</span>
          {signal.sector}
        </span>
      </div>
    </div>
  );
}