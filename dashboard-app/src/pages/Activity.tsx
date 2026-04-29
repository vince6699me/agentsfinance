import { useState } from 'react';
import ActivityFeed, { ActivityEvent } from '../components/ActivityFeed';

// Activity page props
interface ActivityPageProps {
  // Add any props needed for integration
}

// Statistics for activity
interface ActivityStats {
  totalEvents: number;
  agentEvents: number;
  tradeEvents: number;
  signalEvents: number;
  systemEvents: number;
  avgConfidence: number;
  totalPnL: number;
}

export default function ActivityPage({}: ActivityPageProps) {
  const [selectedEvent, setSelectedEvent] = useState<ActivityEvent | null>(null);
  const stats: ActivityStats = {
    totalEvents: 156,
    agentEvents: 42,
    tradeEvents: 28,
    signalEvents: 35,
    systemEvents: 51,
    avgConfidence: 78,
    totalPnL: 247.50
  };
  
  // Handle event click from feed
  const handleEventClick = (event: ActivityEvent) => {
    setSelectedEvent(event);
  };
  
  return (
    <div className="activity-page">
      <header className="page-header">
        <h1 className="page-title">📋 Activity Feed</h1>
        <p className="page-subtitle">
          Real-time agent, trade, and system activity updates
        </p>
      </header>
      
      {/* Stats Overview */}
      <div className="activity-stats">
        <div className="stat-card">
          <div className="stat-label">Total Events</div>
          <div className="stat-value">{stats.totalEvents}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Agent Activities</div>
          <div className="stat-value type-agent">{stats.agentEvents}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Trades</div>
          <div className="stat-value type-trade">{stats.tradeEvents}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Signals</div>
          <div className="stat-value type-signal">{stats.signalEvents}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total P&L</div>
          <div className={`stat-value ${stats.totalPnL >= 0 ? 'green' : 'red'}`}>
            {stats.totalPnL >= 0 ? '+' : ''}${stats.totalPnL.toFixed(2)}
          </div>
        </div>
      </div>
      
      {/* Main Content Grid */}
      <div className="activity-content">
        {/* Activity Feed */}
        <section className="feed-section">
          <ActivityFeed 
            maxItems={100}
            autoScroll={true}
            onEventClick={handleEventClick}
          />
        </section>
        
        {/* Event Details Panel */}
        <aside className="event-details-panel">
          <h3 className="panel-title">Event Details</h3>
          
          {selectedEvent ? (
            <div className="event-details">
              <div className="detail-header">
                <span className="detail-type">{selectedEvent.type.toUpperCase()}</span>
                <span className="detail-time">
                  {selectedEvent.timestamp.toLocaleString()}
                </span>
              </div>
              
              <div className="detail-title">{selectedEvent.title}</div>
              <div className="detail-message">{selectedEvent.message}</div>
              
              {selectedEvent.metadata && (
                <div className="detail-metadata">
                  {selectedEvent.metadata.agentId && (
                    <div className="detail-row">
                      <span className="detail-label">Agent</span>
                      <span className="detail-value">{selectedEvent.metadata.agentId}</span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.instrument && (
                    <div className="detail-row">
                      <span className="detail-label">Instrument</span>
                      <span className="detail-value">{selectedEvent.metadata.instrument}</span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.sector && (
                    <div className="detail-row">
                      <span className="detail-label">Sector</span>
                      <span className="detail-value">{selectedEvent.metadata.sector}</span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.confidence !== undefined && (
                    <div className="detail-row">
                      <span className="detail-label">Confidence</span>
                      <span className="detail-value confidence">
                        {selectedEvent.metadata.confidence}%
                      </span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.strategy && (
                    <div className="detail-row">
                      <span className="detail-label">Strategy</span>
                      <span className="detail-value">{selectedEvent.metadata.strategy}</span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.action && (
                    <div className="detail-row">
                      <span className="detail-label">Action</span>
                      <span className="detail-value">{selectedEvent.metadata.action}</span>
                    </div>
                  )}
                  
                  {selectedEvent.metadata.pnl !== undefined && (
                    <div className="detail-row">
                      <span className="detail-label">P&L</span>
                      <span className={`detail-value ${selectedEvent.metadata.pnl >= 0 ? 'positive' : 'negative'}`}>
                        {selectedEvent.metadata.pnl >= 0 ? '+' : ''}${selectedEvent.metadata.pnl}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="no-event-selected">
              <p>Select an event from the feed</p>
              <p className="hint">Click on any event to view its details</p>
            </div>
          )}
          
          {/* Legend */}
          <div className="event-legend">
            <h4>Event Types</h4>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-icon">🤖</span>
                <span>Agent</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">💹</span>
                <span>Trade</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">📈</span>
                <span>Signal</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">🔍</span>
                <span>Scanner</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">🔬</span>
                <span>Analysis</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">⚖️</span>
                <span>Debate</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">🛡️</span>
                <span>Risk</span>
              </div>
              <div className="legend-item">
                <span className="legend-icon">⚙️</span>
                <span>System</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}