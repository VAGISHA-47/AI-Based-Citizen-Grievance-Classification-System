import React, { useState, useEffect } from 'react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { GlassCard } from '../../components/ui/GlassCard';
import { TrendingUp, TrendingDown, AlertTriangle, Clock, RefreshCw } from 'lucide-react';

// Fallback complaints (shown while loading or if API fails)
const DEFAULT_QUEUE = [
  { id: '#CMP-8925', title: 'Major pothole causing traffic jam on NH-44',    cat: 'Roads',          dept: 'PWD',    citizen: 'Rahul Sharma',  priority: 'high',   slaHours: 0.25, status: 'submitted',      critical: true },
];

const FILTERS = ['All (142)', 'High Priority (28)', 'SLA Warning (18)'];

function SLATimer({ hours }) {
  const color = hours < 1 ? 'var(--status-high)' : hours < 24 ? 'var(--status-med)' : 'var(--text-secondary)';
  const className = hours < 1 ? 'timer-breach' : hours < 24 ? 'timer-warning' : 'timer-normal';
  const label = hours < 1
    ? `${Math.round(hours * 60)}m`
    : hours < 24
      ? `${hours.toFixed(1)}h`
      : `${Math.round(hours)}h`;
  return <span className={`mono queue-card__sla ${className}`} style={{ color, textShadow: hours < 1 ? '0 0 12px rgba(255, 77, 109, 0.4)' : 'none' }}>⏱ {label}</span>;
}


export function Queue() {
  const [activeFilter, setActiveFilter] = useState(0);
  const [complaints, setComplaints] = useState(DEFAULT_QUEUE);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const { default: API_BASE_URL } = await import('../../config/api');
      const response = await fetch(`${API_BASE_URL}/grievances/queue`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json().catch(() => []);
      console.log("[QUEUE] Fetched complaints:", data);
      if (Array.isArray(data) && data.length > 0) {
        setComplaints(data);
      }
    } catch (err) {
      console.error("[QUEUE] Failed to fetch:", err);
    } finally {
      setLoading(false);
      setLastRefresh(new Date());
    }
  };

  useEffect(() => {
    // Fetch on mount
    fetchComplaints();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchComplaints, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animate-fade-in">
      {/* Refresh Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Complaint Queue</h2>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
            Last updated: {lastRefresh.toLocaleTimeString()} · {complaints.length} active
          </div>
        </div>
        <button
          onClick={fetchComplaints}
          disabled={loading}
          style={{
            background: 'rgba(0, 201, 167, 0.1)',
            border: '1px solid rgba(0, 201, 167, 0.3)',
            color: 'var(--teal-primary)',
            padding: '8px 12px',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        {FILTERS.map((f, i) => (
          <button key={i} className={`filter-tab ${activeFilter === i ? 'active' : ''}`} onClick={() => setActiveFilter(i)}>
            {f}
          </button>
        ))}
      </div>

      {/* Queue */}
      <div style={{ maxWidth: 800 }}>
        {complaints.length === 0 ? (
          <GlassCard layer={2} style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              No complaints in queue right now.
            </div>
          </GlassCard>
        ) : (
          complaints.map(c => (
          <GlassCard layer={2} hoverEffect={true} key={c.id} className={`queue-card ${c.critical ? 'critical' : ''}`} style={{
            borderLeft: `4px solid ${c.priority === 'high' ? 'var(--status-high)' : c.priority === 'medium' ? 'var(--status-med)' : 'var(--status-low)'}`,
          }}>
            {c.critical && <div className="active-badge">ACTIVE</div>}

            <div style={{ paddingLeft: 4 }}>
              <div className="queue-card__row-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="queue-card__id">{c.id}</span>
                  <Badge variant={c.priority}>{c.priority.toUpperCase()}</Badge>
                </div>
                <SLATimer hours={c.slaHours} />
              </div>

              <div className="queue-card__title">{c.title}</div>

              <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
                <Badge>{c.cat}</Badge>
                <span style={{ fontSize: 12, color: 'var(--color-text-secondary)', alignSelf: 'center' }}>{c.dept}</span>
              </div>

              <div className="queue-card__row-bottom">
                <span>👤 {c.citizen}</span>
                <span style={{
                  fontSize: 11, fontWeight: 700, padding: '2px 8px',
                  borderRadius: 20, background: 'rgba(0, 201, 167, 0.1)',
                  color: 'var(--teal-primary)', textTransform: 'uppercase',
                  letterSpacing: '0.04em'
                }}>
                  {c.status.replace('_', ' ')}
                </span>
              </div>

              <div className="queue-card__actions" style={{ paddingTop: 16 }}>
                <Button variant="outline" size="sm">View</Button>
                <Button variant="outline" size="sm">Update</Button>
                <Button variant="primary" size="sm">Resolve</Button>
              </div>
            </div>
          </GlassCard>
          ))
        )}
      </div>
    </div>
  );
}
