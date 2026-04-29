export type SignalStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export interface Signal {
  id: string;
  symbol: string;
  strategy: string;
  direction: 'LONG' | 'SHORT' | 'NO_TRADE';
  status: SignalStatus;
  entryPrice: number;
  targetPrice?: number;
  stopLoss?: number;
  confidence: number;
  votes: {
    bull: number;
    bear: number;
    neutral: number;
  };
  confluenceCount: number;
  timeRemaining: string;
  sector: string;
  createdAt: string;
  debateArguments?: DebateArgument[];
}

export interface DebateArgument {
  role: 'bull' | 'bear' | 'neutral' | 'fund_manager';
  argument: string;
  timestamp: string;
  keyPoints: string[];
}

interface DebateOutcomeProps {
  signal: Signal;
  expanded?: boolean;
}

const getRoleLabel = (role: string): string => {
  switch (role) {
    case 'bull':
      return '🐂 Bull Analyst';
    case 'bear':
      return '🐻 Bear Analyst';
    case 'neutral':
      return '⚪ Neutral Analyst';
    case 'fund_manager':
      return '👔 Fund Manager';
    default:
      return role;
  }
};

const getRoleColor = (role: string): string => {
  switch (role) {
    case 'bull':
      return 'var(--accent-green)';
    case 'bear':
      return 'var(--accent-red)';
    case 'neutral':
      return 'var(--text-secondary)';
    case 'fund_manager':
      return 'var(--accent-blue)';
    default:
      return 'var(--text-secondary)';
  }
};

export default function DebateOutcome({ signal, expanded = false }: DebateOutcomeProps) {
  const totalVotes = signal.votes.bull + signal.votes.bear + signal.votes.neutral;
  const bullPercent = totalVotes > 0 ? Math.round((signal.votes.bull / totalVotes) * 100) : 0;
  const bearPercent = totalVotes > 0 ? Math.round((signal.votes.bear / totalVotes) * 100) : 0;
  const neutralPercent = totalVotes > 0 ? Math.round((signal.votes.neutral / totalVotes) * 100) : 0;

  return (
    <div className={`debate-outcome ${expanded ? 'expanded' : ''}`}>
      {/* Vote Breakdown */}
      <div className="debate-votes-section">
        <h4 className="debate-section-title">Debate Vote Breakdown</h4>
        <div className="vote-breakdown">
          <div className="vote-bar-container">
            <div className="vote-bar-label">
              <span>🐂 Bull</span>
              <span>{bullPercent}%</span>
            </div>
            <div className="vote-bar-track">
              <div
                className="vote-bar-fill bull"
                style={{ width: `${bullPercent}%` }}
              />
            </div>
          </div>
          <div className="vote-bar-container">
            <div className="vote-bar-label">
              <span>🐻 Bear</span>
              <span>{bearPercent}%</span>
            </div>
            <div className="vote-bar-track">
              <div
                className="vote-bar-fill bear"
                style={{ width: `${bearPercent}%` }}
              />
            </div>
          </div>
          <div className="vote-bar-container">
            <div className="vote-bar-label">
              <span>⚪ Neutral</span>
              <span>{neutralPercent}%</span>
            </div>
            <div className="vote-bar-track">
              <div
                className="vote-bar-fill neutral"
                style={{ width: `${neutralPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Decision */}
      <div className="debate-decision">
        <h4 className="debate-section-title">Fund Manager Decision</h4>
        <div className="decision-box">
          <div className="decision-direction">
            {signal.direction === 'LONG' && <span className="decision-icon long">🟢</span>}
            {signal.direction === 'SHORT' && <span className="decision-icon short">🔴</span>}
            {signal.direction === 'NO_TRADE' && <span className="decision-icon none">⛔</span>}
            <span className="decision-text">{signal.direction.replace('_', ' ')}</span>
          </div>
          <div className="decision-confidence">
            <span className="confidence-label">Confidence:</span>
            <span className={`confidence-score ${signal.confidence >= 80 ? 'high' : signal.confidence >= 65 ? 'medium' : 'low'}`}>
              {signal.confidence}%
            </span>
          </div>
        </div>
      </div>

      {/* Debate Arguments (expanded view) */}
      {expanded && signal.debateArguments && signal.debateArguments.length > 0 && (
        <div className="debate-arguments">
          <h4 className="debate-section-title">Debate Transcript</h4>
          {signal.debateArguments.map((arg, index) => (
            <div key={index} className="argument-card" style={{ borderLeftColor: getRoleColor(arg.role) }}>
              <div className="argument-header">
                <span className="argument-role" style={{ color: getRoleColor(arg.role) }}>
                  {getRoleLabel(arg.role)}
                </span>
                <span className="argument-time">{arg.timestamp}</span>
              </div>
              <p className="argument-text">{arg.argument}</p>
              {arg.keyPoints.length > 0 && (
                <div className="argument-points">
                  {arg.keyPoints.map((point, i) => (
                    <span key={i} className="key-point">• {point}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Confluence Indicator */}
      <div className="confluence-indicator">
        <h4 className="debate-section-title">Department Confluence</h4>
        <div className="confluence-bars">
          {[1, 2, 3, 4, 5, 6].map((dept) => (
            <div
              key={dept}
              className={`confluence-bar ${dept <= signal.confluenceCount ? 'active' : ''}`}
              title={`Department ${dept}`}
            >
              <span className="confluence-dept">D{dept}</span>
            </div>
          ))}
        </div>
        <span className="confluence-count">{signal.confluenceCount}/6 departments</span>
      </div>
    </div>
  );
}