import React, { useEffect, useState } from 'react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { GlassCard } from '../../components/ui/GlassCard';
import { TrendingUp, TrendingDown, AlertTriangle, Clock } from 'lucide-react';
import { getAssignedComplaints } from '../../services/api';

const queueComplaints = [
  { id: '#CMP-8925', title: 'Major pothole causing traffic jam on NH-44',    cat: 'Roads',          dept: 'PWD',    citizen: 'Rahul Sharma',  priority: 'high',   slaHours: 0.25, status: 'urgent',      critical: true },
  { id: '#CMP-8924', title: 'Streetlight not working near school zone',       cat: 'Infrastructure', dept: 'BESCOM', citizen: 'Priya Nair',    priority: 'medium', slaHours: 4.5,  status: 'in_progress', critical: false },
  { id: '#CMP-8923', title: 'Water supply disruption in Koramangala',         cat: 'Utilities',      dept: 'BWSSB',  citizen: 'Anil Desai',    priority: 'high',   slaHours: 8,    status: 'assigned',    critical: false },
  { id: '#CMP-8922', title: 'Garbage not collected for 3 consecutive days',   cat: 'Sanitation',     dept: 'BBMP',   citizen: 'Suresh Rao',    priority: 'low',    slaHours: 22,   status: 'submitted',   critical: false },
  { id: '#CMP-8921', title: 'Park bench broken in Cubbon Park',               cat: 'Parks',          dept: 'BBMP',   citizen: 'Meera Pillai',  priority: 'low',    slaHours: 40,   status: 'submitted',   critical: false },
  { id: '#CMP-8920', title: 'Sewer line overflow near bus stop',              cat: 'Sanitation',     dept: 'BWSSB',  citizen: 'Vikram Singh',  priority: 'high',   slaHours: 2,    status: 'in_progress', critical: false },
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
  const [items, setItems] = useState(queueComplaints);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await getAssignedComplaints();
        if (response?.grievances?.length) {
          setItems(response.grievances);
        }
      } catch {
        // keep static fallback
      }
    };

    load();
  }, []);

  return (
    <div className="animate-fade-in">
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
        {items.map(c => (
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
        ))}
      </div>
    </div>
  );
}
