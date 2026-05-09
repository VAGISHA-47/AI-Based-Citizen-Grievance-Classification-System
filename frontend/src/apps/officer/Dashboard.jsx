import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { GlassCard } from '../../components/ui/GlassCard';
import CountUpBase from 'react-countup';
const CountUp = CountUpBase.default || CountUpBase;

const fallbackComplaints = [
  { id: '#CMP-8925', title: 'Major pothole causing traffic jam on NH-44', cat: 'Roads', dept: 'PWD', citizen: 'Rahul Sharma', priority: 'high', slaHours: 0.25, status: 'urgent', critical: true },
  { id: '#CMP-8924', title: 'Streetlight not working near school zone', cat: 'Infrastructure', dept: 'BESCOM', citizen: 'Priya Nair', priority: 'medium', slaHours: 4.5, status: 'in_progress', critical: false },
  { id: '#CMP-8922', title: 'Water supply disruption in residential area', cat: 'Utilities', dept: 'BWSSB', citizen: 'Anil Desai', priority: 'high', slaHours: 8, status: 'assigned', critical: false },
  { id: '#CMP-8920', title: 'Garbage not collected for 3 consecutive days', cat: 'Sanitation', dept: 'BBMP', citizen: 'Suresh Rao', priority: 'low', slaHours: 22, status: 'submitted', critical: false },
];

const escalations = [
  { id: '#CMP-8899', reason: 'SLA breached by 4 days', level: 3 },
  { id: '#CMP-8910', reason: 'Citizen complaint escalated', level: 2 },
  { id: '#CMP-8918', reason: 'No response from officer', level: 1 },
];

function SLATimer({ hours }) {
  const color = hours < 1 ? 'var(--color-urgent-text)' : hours < 24 ? 'var(--color-warning-text)' : 'var(--color-accent)';
  const className = hours < 1 ? 'timer-breach' : hours < 24 ? 'timer-warning' : 'timer-normal';
  const label = hours < 1
    ? `${Math.round(hours * 60)}m left`
    : hours < 24
      ? `${hours.toFixed(1)}h left`
      : `${Math.round(hours)}h`;
  return (
    <span className={`mono queue-card__sla ${className}`} style={{ color }}>
      ⏱ {label}
    </span>
  );
}

function PriorityBorder({ priority }) {
  const color = priority === 'high' ? 'var(--color-urgent-text)' : priority === 'medium' ? 'var(--color-warning-text)' : 'var(--color-success-text)';
  return (
    <div style={{
      position: 'absolute', left: 0, top: 0, bottom: 0,
      width: 4, background: color, borderRadius: '4px 0 0 4px'
    }} />
  );
}

const DEPT_BARS = [
  { label: 'Resolution Time', pct: 40 },
  { label: 'Citizen Rating',  pct: 35 },
  { label: 'Backlog',         pct: 25 },
];

const FILTERS = ['All (142)', 'High Priority (28)', 'SLA Warning (18)'];

export function Dashboard() {
  const [activeFilter, setActiveFilter] = useState(0);
  const [complaints, setComplaints] = useState([]);

  useEffect(() => {
    const loadComplaints = async () => {
      try {
        const { getAssignedComplaints } = await import('../../services/api');
        const data = await getAssignedComplaints();
        setComplaints(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load complaints:', err);
      }
    };
    loadComplaints();
  }, []);

  const visibleComplaints = (complaints.length ? complaints : fallbackComplaints).map((c) => ({
    id: c.id || (c.complaint_id ? `#${c.complaint_id}` : '#CMP-0000'),
    title: c.title || c.text_original || 'Complaint',
    cat: c.cat || c.category || 'General',
    dept: c.dept || c.department || 'JanSetu',
    citizen: c.citizen || c.citizen_name || 'Citizen',
    priority: (c.priority || 'medium').toString().toLowerCase(),
    slaHours: Number(c.slaHours ?? c.sla_hours ?? 24),
    status: (c.status || 'assigned').toString().toLowerCase(),
    critical: Boolean(c.critical || Number(c.slaHours ?? c.sla_hours ?? 24) < 1),
  }));

  return (
    <div className="animate-fade-in">

      {/* KPI Strip */}
      <div className="kpi-grid stagger-children" style={{ marginBottom: 28 }}>
        {[
          { label: 'Total Complaints', value: '1,284', trend: '+12%', up: true  },
          { label: 'Active Cases',     value: '142',   trend: '-5%',  up: false },
          { label: 'SLA Breaches',     value: '18',    trend: '⚠ Alert', up: false, red: true },
          { label: 'Resolved Today',   value: '45',    trend: '+8%',  up: true, green: true },
        ].map((k, i) => (
          <GlassCard key={i} layer={3} className="kpi-card animate-fade-up">
            <span className="kpi-card__label">{k.label}</span>
            <span className="kpi-card__value" style={{ color: k.red ? 'var(--color-urgent-text)' : k.green ? 'var(--color-success-text)' : 'var(--color-accent)' }}>
              {k.value === '18' ? (
                <CountUp end={18} duration={1.2} />
              ) : k.value === '142' ? (
                <CountUp end={142} duration={1.2} />
              ) : k.value === '45' ? (
                <CountUp end={45} duration={1.2} />
              ) : (
                <CountUp end={1284} duration={1.2} separator="," />
              )}
            </span>
            <span className="kpi-card__trend" style={{ color: k.up ? 'var(--color-success-text)' : k.red ? 'var(--color-urgent-text)' : 'var(--color-warning-text)' }}>
              {k.up ? <TrendingUp size={14}/> : k.red ? <AlertTriangle size={14}/> : <TrendingDown size={14}/>}
              {k.trend}
            </span>
          </GlassCard>
        ))}
      </div>

      {/* Main 2-col layout */}
      <div className="dashboard-columns">

        {/* ── Left: Complaint Queue ── */}
        <div>
          {/* Filter tabs */}
          <div className="filter-tabs">
            {FILTERS.map((f, i) => (
              <button key={i} className={`filter-tab ${activeFilter === i ? 'active' : ''}`} onClick={() => setActiveFilter(i)}>
                {f}
              </button>
            ))}
          </div>

          {/* Queue Cards */}
          {visibleComplaints.map(c => (
            <GlassCard key={c.id} layer={2} className={`queue-card priority-border-${c.priority} ${c.critical ? 'critical' : ''}`}>
              {c.critical && <div className="active-badge">ACTIVE</div>}
              <PriorityBorder priority={c.priority} />
              <div style={{ paddingLeft: 8 }}>
                <div className="queue-card__row-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="queue-card__id">{c.id}</span>
                    <Badge variant={c.priority}>{c.priority.toUpperCase()}</Badge>
                  </div>
                  <SLATimer hours={c.slaHours} />
                </div>
                <div className="queue-card__title">{c.title}</div>
                <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                  <Badge>{c.cat}</Badge>
                  <span style={{ fontSize: 12, color: 'var(--color-text-secondary)', alignSelf: 'center' }}>{c.dept}</span>
                </div>
                <div className="queue-card__row-bottom">
                  <span>👤 {c.citizen}</span>
                  <span style={{
                    fontSize: 11, fontWeight: 600, padding: '2px 8px',
                    borderRadius: 20, background: 'rgba(38, 135, 143, 0.1)',
                    color: 'var(--color-accent)', textTransform: 'uppercase'
                  }}>
                    {c.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="queue-card__actions">
                  <button className="queue-action-btn">View</button>
                  <button className="queue-action-btn">Update</button>
                  <button className="queue-action-btn primary">Resolve</button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>

        {/* ── Right: Insight Panel ── */}
        <div>
          {/* Dept Score */}
          <GlassCard layer={2} className="insight-card">
            <div className="section-label">Dept Score</div>
            <div style={{ fontSize: 40, fontWeight: 700, color: 'var(--color-accent)', lineHeight: 1, marginBottom: 4 }}>
              <CountUp end={78} duration={1.2} />
            </div>
            <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 16 }}>Rank 2 of 18 departments</div>
            {DEPT_BARS.map(d => (
              <div key={d.label} className="dept-bar-row">
                <span className="dept-bar-label">{d.label}</span>
                <div className="dept-bar-track">
                  <div className="dept-bar-fill" style={{ width: `${d.pct}%` }} />
                </div>
                <span className="dept-bar-pct">{d.pct}%</span>
              </div>
            ))}
          </GlassCard>

          {/* Escalations */}
          <GlassCard layer={2} className="insight-card">
            <div className="section-label">Escalations</div>
            {escalations.map(e => (
              <div key={e.id} className="escalation-item">
                <span className={`escalation-level esc-l${e.level}`}>L{e.level}</span>
                <div style={{ flex: 1 }}>
                  <div className="mono" style={{ fontSize: 12, color: 'var(--color-text-primary)', fontWeight: 600 }}>{e.id}</div>
                  <div style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>{e.reason}</div>
                </div>
              </div>
            ))}
          </GlassCard>

          {/* Today Stats */}
          <GlassCard layer={2} className="insight-card">
            <div className="section-label">Today</div>
            <div className="today-stats">
              <div className="today-stat">
                <span className="today-stat__num"><CountUp end={28} /></span>
                <div className="today-stat__label">Opened</div>
              </div>
              <div className="today-stat">
                <span className="today-stat__num"><CountUp end={12} /></span>
                <div className="today-stat__label">Resolved</div>
              </div>
              <div className="today-stat">
                <span className="today-stat__num">2.1h</span>
                <div className="today-stat__label">Avg Resp.</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
