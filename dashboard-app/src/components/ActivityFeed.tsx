import { useState, useEffect, useRef } from 'react';

// Activity event types
export type ActivityEventType = 
  | 'agent' 
  | 'trade' 
  | 'signal' 
  | 'system' 
  | 'scan' 
  | 'analysis'
  | 'debate'
  | 'risk';

// Activity event interface
export interface ActivityEvent {
  id: string;
  type: ActivityEventType;
  title: string;
  message: string;
  timestamp: Date;
  metadata?: {
    agentId?: string;
    instrument?: string;
    sector?: string;
    confidence?: number;
    pnl?: number;
    action?: string;
    strategy?: string;
  };
}

// Activity feed props
interface ActivityFeedProps {
  maxItems?: number;
  autoScroll?: boolean;
  filter?: ActivityEventType[];
  onEventClick?: (event: ActivityEvent) => void;
}

// Generate unique ID
const generateId = (): string => {
  return Math.random().toString(36).substring(2, 11);
};

// Format timestamp
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
};

// Get type icon
const getTypeIcon = (type: ActivityEventType): string => {
  const icons: Record<ActivityEventType, string> = {
    agent: '🤖',
    trade: '💹',
    signal: '📈',
    system: '⚙️',
    scan: '🔍',
    analysis: '🔬',
    debate: '⚖️',
    risk: '🛡️'
  };
  return icons[type] || '📋';
};

// Get type color class
const getTypeColorClass = (type: ActivityEventType): string => {
  const colors: Record<ActivityEventType, string> = {
    agent: 'type-agent',
    trade: 'type-trade',
    signal: 'type-signal',
    system: 'type-system',
    scan: 'type-scan',
    analysis: 'type-analysis',
    debate: 'type-debate',
    risk: 'type-risk'
  };
  return colors[type] || 'type-default';
};

// Generate mock activity events
const generateMockEvents = (count: number): ActivityEvent[] => {
  const events: ActivityEvent[] = [];
  const agents = [
    { id: 'T1-A1', name: 'Macro Intelligence' },
    { id: 'T1-A2', name: 'News NLP' },
    { id: 'T1-A3', name: 'Sector Data' },
    { id: 'T2-A1', name: 'Forex Scanner' },
    { id: 'T2-A2', name: 'Commodities Scanner' },
    { id: 'T2-A5', name: 'Crypto Scanner' },
    { id: 'T3-A18', name: 'Order Block & FVG' },
    { id: 'T3-A19', name: 'Market Structure' },
    { id: 'T3-A20', name: 'Liquidity' },
    { id: 'T3-A21', name: 'Kill Zone' },
    { id: 'Bull', name: 'Bull Analyst' },
    { id: 'Bear', name: 'Bear Analyst' },
    { id: 'Neutral', name: 'Neutral Analyst' },
    { id: 'FM', name: 'Fund Manager' },
    { id: 'Risk', name: 'Risk Manager' },
    { id: 'T6-A1', name: 'Forex Trader' },
    { id: 'T6-A5', name: 'Crypto Trader' },
    { id: 'T8-A1', name: 'Meta-Evaluation' }
  ];
  
  const instruments = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'XTIUSD',
    'SPX', 'NDX', 'BTCUSD', 'ETHUSD', 'AAPL'
  ];
  
  const strategies = [
    'ICT-01 Micro-Sweep', 'ICT-02 PD Array FVG', 'ICT-03 Kill-Zone Pulse',
    'ICT-05 CHoCH Momentum', 'ICT-07 HTF Structure', 'ICT-08 Discount-Premium',
    'STRAT-003 Divergence', 'STRAT-004 MA Crossover', 'COT-001 Report'
  ];
  
  const actions = [
    'detected', 'confirmed', 'approved', 'rejected', 'executed',
    'entered', 'exited', 'updated', 'scanned', 'analyzed'
  ];
  
  const eventTemplates = [
    { type: 'agent' as ActivityEventType, title: 'Agent Activity', getMessage: () => `${actions[Math.floor(Math.random() * actions.length)]} setup` },
    { type: 'scan' as ActivityEventType, title: 'Scanner', getMessage: () => `found opportunity` },
    { type: 'signal' as ActivityEventType, title: 'Signal', getMessage: () => `signal generated` },
    { type: 'analysis' as ActivityEventType, title: 'Analysis', getMessage: () => `analysis complete` },
    { type: 'debate' as ActivityEventType, title: 'Debate', getMessage: () => `debate concluded` },
    { type: 'trade' as ActivityEventType, title: 'Trade', getMessage: () => `trade ${actions[Math.floor(Math.random() * actions.length)]}` },
    { type: 'risk' as ActivityEventType, title: 'Risk', getMessage: () => `gate check passed` },
    { type: 'system' as ActivityEventType, title: 'System', getMessage: () => `system event` }
  ];
  
  const now = new Date();
  
  for (let i = 0; i < count; i++) {
    const template = eventTemplates[Math.floor(Math.random() * eventTemplates.length)];
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const instrument = instruments[Math.floor(Math.random() * instruments.length)];
    const strategy = strategies[Math.floor(Math.random() * strategies.length)];
    const action = actions[Math.floor(Math.random() * actions.length)];
    
    let title = template.title;
    let message = template.getMessage();
    
    if (template.type === 'agent') {
      title = agent.name;
      message = `${action} on ${instrument}`;
    } else if (template.type === 'signal' || template.type === 'analysis') {
      message = `${strategy} on ${instrument}`;
    } else if (template.type === 'trade') {
      const pnl = (Math.random() - 0.3) * 100;
      message = `${action === 'entered' ? 'opened' : action === 'exited' ? 'closed' : action} position on ${instrument}`;
      events.push({
        id: generateId(),
        type: template.type,
        title,
        message,
        timestamp: new Date(now.getTime() - i * 60000),
        metadata: { 
          instrument, 
          pnl: Number(pnl.toFixed(2)),
          action: action === 'entered' ? 'LONG' : 'SHORT'
        }
      });
      continue;
    } else if (template.type === 'scan') {
      message = `${instrument} in ${['forex', 'commodities', 'crypto', 'indices'][Math.floor(Math.random() * 4)]} sector`;
    }
    
    events.push({
      id: generateId(),
      type: template.type,
      title,
      message,
      timestamp: new Date(now.getTime() - i * 60000),
      metadata: {
        agentId: agent.id,
        instrument,
        confidence: Math.floor(Math.random() * 30) + 70,
        strategy
      }
    });
  }
  
  return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

export default function ActivityFeed({ 
  maxItems = 50, 
  autoScroll = true, 
  filter = [],
  onEventClick 
}: ActivityFeedProps) {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [filterType, setFilterType] = useState<ActivityEventType | 'all'>('all');
  const feedRef = useRef<HTMLDivElement>(null);
  
  // Initialize with mock events on mount
  useEffect(() => {
    const initialEvents = generateMockEvents(maxItems);
    setEvents(initialEvents);
  }, [maxItems]);
  
  // Auto-scroll to top when new events arrive
  useEffect(() => {
    if (autoScroll && !isPaused && feedRef.current) {
      feedRef.current.scrollTop = 0;
    }
  }, [events, autoScroll, isPaused]);
  
  // Simulate real-time updates
  useEffect(() => {
    if (isPaused) return;
    
    const interval = setInterval(() => {
      const newEvent = generateMockEvents(1)[0];
      setEvents(prev => [newEvent, ...prev.slice(0, maxItems - 1)]);
    }, 3000 + Math.random() * 4000); // Random interval 3-7 seconds
    
    return () => clearInterval(interval);
  }, [isPaused, maxItems]);
  
  // Filter events
  const filteredEvents = events.filter(event => {
    if (filterType !== 'all' && event.type !== filterType) return false;
    if (filter.length > 0 && !filter.includes(event.type)) return false;
    return true;
  });
  
  // Handle event click
  const handleEventClick = (event: ActivityEvent) => {
    if (onEventClick) {
      onEventClick(event);
    }
  };
  
  // Clear all events
  const clearEvents = () => {
    setEvents([]);
  };
  
  return (
    <div className="activity-feed">
      {/* Header */}
      <div className="feed-header">
        <div className="feed-controls">
          <select 
            className="feed-filter"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as ActivityEventType | 'all')}
          >
            <option value="all">All Events</option>
            <option value="agent">Agents</option>
            <option value="trade">Trades</option>
            <option value="signal">Signals</option>
            <option value="scan">Scanner</option>
            <option value="analysis">Analysis</option>
            <option value="debate">Debate</option>
            <option value="risk">Risk</option>
            <option value="system">System</option>
          </select>
          
          <button 
            className={`feed-pause-btn ${isPaused ? 'paused' : ''}`}
            onClick={() => setIsPaused(!isPaused)}
            title={isPaused ? 'Resume feed' : 'Pause feed'}
          >
            {isPaused ? '▶' : '⏸'}
          </button>
          
          <button 
            className="feed-clear-btn"
            onClick={clearEvents}
            title="Clear feed"
          >
            🗑️
          </button>
        </div>
        
        <div className="feed-status">
          <span className={`status-indicator ${isPaused ? 'paused' : 'active'}`}></span>
          <span className="status-text">
            {isPaused ? 'Paused' : 'Live'}
          </span>
          <span className="event-count">{filteredEvents.length} events</span>
        </div>
      </div>
      
      {/* Feed list */}
      <div className="feed-list" ref={feedRef}>
        {filteredEvents.length === 0 ? (
          <div className="feed-empty">
            <p>No activity events to display</p>
            <p className="empty-hint">Events will appear here in real-time</p>
          </div>
        ) : (
          filteredEvents.map((event, index) => (
            <div 
              key={event.id}
              className={`feed-event ${getTypeColorClass(event.type)} ${index === 0 ? 'newest' : ''}`}
              onClick={() => handleEventClick(event)}
              style={{ 
                animationDelay: index === 0 ? '0ms' : undefined 
              }}
            >
              <div className="event-icon">
                {getTypeIcon(event.type)}
              </div>
              
              <div className="event-content">
                <div className="event-header">
                  <span className="event-title">{event.title}</span>
                  <span className="event-time">{formatTime(event.timestamp)}</span>
                </div>
                
                <div className="event-message">
                  {event.message}
                </div>
                
                {event.metadata && (
                  <div className="event-metadata">
                    {event.metadata.instrument && (
                      <span className="meta-item">
                        📊 {event.metadata.instrument}
                      </span>
                    )}
                    {event.metadata.confidence !== undefined && (
                      <span className="meta-item">
                        📈 {event.metadata.confidence}%
                      </span>
                    )}
                    {event.metadata.pnl !== undefined && (
                      <span className={`meta-item ${event.metadata.pnl >= 0 ? 'positive' : 'negative'}`}>
                        {event.metadata.pnl >= 0 ? '+' : ''}${event.metadata.pnl}
                      </span>
                    )}
                    {event.metadata.strategy && (
                      <span className="meta-item">
                        🎯 {event.metadata.strategy}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}