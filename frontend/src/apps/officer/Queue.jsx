import React, { useState, useEffect } from 'react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { GlassCard } from '../../components/ui/GlassCard';
import { RefreshCw } from 'lucide-react';

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
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const highPriorityCount = complaints.filter(
    (c) => (c.priority || '').toLowerCase() === 'high'
  ).length;
  const warningCount = complaints.filter(
    (c) => Number(c.sla_days ?? 5) * 24 < 24
  ).length;
  const filters = [
    `All (${complaints.length})`,
    `High Priority (${highPriorityCount})`,
    `SLA Warning (${warningCount})`,
  ];

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const response = await fetch('/officer/assigned', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('jansetu_token')}`,
        },
      });
      const data = await response.json().catch(() => []);
      if (Array.isArray(data)) {
        setComplaints(data);
        console.log('[QUEUE] Loaded:', data.length);
      }
    } catch (err) {
      console.error('[QUEUE] Error:', err);
    } finally {
      setLoading(false);
      setLastRefresh(new Date());
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleResolve = async (complaintId) => {
    if (!window.confirm(
      'Mark this complaint as resolved?'
    )) return;

    try {
      const res = await fetch(
        `/officer/${complaintId}/resolve`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('jansetu_token')}`,
          },
          body: JSON.stringify({
            resolution: 'Resolved by officer'
          })
        }
      );
      const data = await res.json();
      if (data.status === 'resolved') {
        alert('✅ Complaint resolved!');
        setComplaints((prev) =>
          prev.map((c) =>
            c.complaint_id === complaintId
              ? { ...c, status: 'resolved' }
              : c
          )
        );
      }
    } catch (err) {
      alert('Failed to resolve. Try again.');
    }
  };

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
        {filters.map((f, i) => (
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
          complaints.map((complaint) => (
          <GlassCard layer={2} hoverEffect={true} key={complaint.complaint_id} className={`queue-card ${(complaint.priority || '').toLowerCase() === 'high' ? 'critical' : ''}`} style={{
            borderLeft: `4px solid ${(complaint.priority || '').toLowerCase() === 'high' ? 'var(--status-high)' : (complaint.priority || '').toLowerCase() === 'medium' ? 'var(--status-med)' : 'var(--status-low)'}`,
          }}>
            {(complaint.priority || '').toLowerCase() === 'high' && <div className="active-badge">ACTIVE</div>}

            <div style={{ paddingLeft: 4 }}>
              <div className="queue-card__row-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="queue-card__id">{complaint.tracking_token || `#${complaint.complaint_id}`}</span>
                  <Badge variant={(complaint.priority || 'medium').toLowerCase()}>{(complaint.priority || 'medium').toUpperCase()}</Badge>
                </div>
                <SLATimer hours={Number(complaint.sla_days ?? 5) * 24} />
              </div>

              <div className="queue-card__title">{complaint.text_original || 'No description provided'}</div>

              <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
                <Badge>{complaint.category || 'General'}</Badge>
                <span style={{ fontSize: 12, color: 'var(--color-text-secondary)', alignSelf: 'center' }}>
                  {complaint.created_at ? new Date(complaint.created_at).toLocaleString() : 'Unknown time'}
                </span>
              </div>

              <div className="queue-card__row-bottom">
                <span>🆔 {complaint.complaint_id}</span>
                <span style={{
                  fontSize: 11, fontWeight: 700, padding: '2px 8px',
                  borderRadius: 20, background: 'rgba(0, 201, 167, 0.1)',
                  color: 'var(--teal-primary)', textTransform: 'uppercase',
                  letterSpacing: '0.04em'
                }}>
                  {(complaint.status || 'submitted').replace('_', ' ')}
                </span>
              </div>

              <div className="queue-card__actions" style={{ paddingTop: 16 }}>
                <Button variant="outline" size="sm">View</Button>
                <Button variant="outline" size="sm">Update</Button>
                <Button variant="primary" size="sm" onClick={() => handleResolve(complaint.complaint_id)}>Resolve</Button>
              </div>
            </div>
          </GlassCard>
          ))
        )}
      </div>
    </div>
  );
}
