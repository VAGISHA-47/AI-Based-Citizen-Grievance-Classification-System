import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../../components/ui/Badge';
import { FileText, Activity, Zap, CheckCircle, AlertCircle, Loader, ArrowRight, Plus } from 'lucide-react';
import { GlassCard } from '../../components/ui/GlassCard';
import CountUpBase from 'react-countup';
const CountUp = CountUpBase.default || CountUpBase;
import './Citizen.css';

const complaints = [
  { id: '#CMP-8921', title: 'Pothole on Main Street causing accidents', category: 'Roads', dept: 'PWD', status: 'in_progress', date: '2 days ago', icon: '🛣️', priority: 'high', slaHours: 4 },
  { id: '#CMP-8920', title: 'Water Supply Disruption – Ward 4', category: 'Utilities', dept: 'BWSSB', status: 'assigned', date: '3 days ago', icon: '💧', priority: 'high', slaHours: 18 },
  { id: '#CMP-8915', title: 'Streetlight malfunction near school', category: 'Infrastructure', dept: 'BESCOM', status: 'resolved', date: 'Oct 12', icon: '💡', priority: 'medium' },
  { id: '#CMP-8902', title: 'Garbage collection missed for 3 days', category: 'Sanitation', dept: 'BBMP', status: 'submitted', date: 'Oct 10', icon: '🗑️', priority: 'low' },
];

const statusMap = {
  submitted:   { label: 'Submitted',   color: '#6BA9B6', bg: 'rgba(107, 169, 182, 0.1)',  icon: <Loader size={12}/> },
  processing:  { label: 'Processing',  color: '#C89B2D', bg: 'rgba(200, 155, 45, 0.1)',  icon: <Loader size={12}/> },
  assigned:    { label: 'Assigned',    color: '#26878F', bg: 'rgba(38,135,143,0.1)',   icon: <Zap size={12}/> },
  in_progress: { label: 'In Progress', color: '#26878F', bg: 'rgba(38,135,143,0.12)',  icon: <Activity size={12}/> },
  resolved:    { label: 'Resolved',    color: '#2F8F5B', bg: 'rgba(47, 143, 91, 0.1)',   icon: <CheckCircle size={12}/> },
  rejected:    { label: 'Rejected',    color: '#C44B3A', bg: 'rgba(196, 75, 58, 0.1)',   icon: <AlertCircle size={12}/> },
};

function StatusPill({ status }) {
  const s = statusMap[status] || statusMap.submitted;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      fontSize: 11, fontWeight: 600, padding: '3px 8px',
      borderRadius: 20, color: s.color, background: s.bg,
      textTransform: 'uppercase', letterSpacing: '0.06em',
      whiteSpace: 'nowrap'
    }}>
      {s.icon} {s.label}
    </span>
  );
}

function SLATimer({ hours }) {
  if (!hours) return null;
  const color = hours < 2 ? '#C44B3A' : hours < 24 ? '#C89B2D' : 'var(--color-accent)';
  const pulse = hours < 2;
  return (
    <span className="mono" style={{
      fontSize: 11, color, fontWeight: 600,
      animation: pulse ? 'pulse 1.5s ease-in-out infinite' : 'none'
    }}>
      ⏱ {hours}h left
    </span>
  );
}

export function Home() {
  const navigate = useNavigate();

  return (
    <div className="animate-fade-in">

      {/* Quick Stats */}
      <div className="quick-stats-grid stagger-children" style={{ marginBottom: 24 }}>
        <GlassCard layer={2} className="stat-mini-card animate-fade-up">
          <span className="stat-mini-card__num" style={{ color: 'var(--teal-primary)' }}><CountUp end={12} duration={1.2} /></span>
          <span className="stat-mini-card__label">Filed</span>
        </GlassCard>
        <GlassCard layer={2} className="stat-mini-card animate-fade-up">
          <span className="stat-mini-card__num" style={{ color: 'var(--status-low)' }}><CountUp end={8} duration={1.2} /></span>
          <span className="stat-mini-card__label">Resolved</span>
        </GlassCard>
        <GlassCard layer={2} className="stat-mini-card animate-fade-up">
          <span className="stat-mini-card__num" style={{ color: 'var(--status-med)' }}><CountUp end={4} duration={1.2} /></span>
          <span className="stat-mini-card__label">Pending</span>
        </GlassCard>
      </div>

      {/* ── Primary Action Cards ─────────────────────────────────── */}
      <div className="home-desktop-grid" style={{ marginBottom: 28 }}>

        {/* File Complaint Card */}
        <GlassCard layer={3}
          className="action-hero-card action-hero-card--primary"
          onClick={() => navigate('/citizen/file')}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && navigate('/citizen/file')}
        >
          <div className="action-hero-card__icon">
            <Plus size={28} strokeWidth={2} />
          </div>
          <div className="action-hero-card__body">
            <div className="action-hero-card__title">File a Complaint</div>
            <div className="action-hero-card__sub">Report any civic issue near you. Takes under 2 minutes.</div>
          </div>
          <div className="action-hero-card__arrow">
            <ArrowRight size={20} />
          </div>
        </GlassCard>

        {/* Track Status Card */}
        <GlassCard layer={2}
          className="action-hero-card action-hero-card--outline"
          onClick={() => navigate('/citizen/track')}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && navigate('/citizen/track')}
        >
          <div className="action-hero-card__icon action-hero-card__icon--outline">
            <Activity size={28} strokeWidth={2} />
          </div>
          <div className="action-hero-card__body">
            <div className="action-hero-card__title">Track Status</div>
            <div className="action-hero-card__sub">Live updates on your filed complaints and SLA timers.</div>
          </div>
          <div className="action-hero-card__arrow action-hero-card__arrow--outline">
            <ArrowRight size={20} />
          </div>
        </GlassCard>
      </div>

      {/* Complaints List */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="section-label" style={{ marginBottom: 0 }}>Your Complaints</div>
          <button
            onClick={() => navigate('/citizen/track')}
            style={{ fontSize: 13, color: 'var(--color-accent)', fontWeight: 500, background: 'none', border: 'none', cursor: 'pointer' }}
          >
            View all →
          </button>
        </div>

        <div className="complaints-grid stagger-children">
          {complaints.map((c) => (
            <GlassCard layer={2} key={c.id} className="complaint-card animate-fade-up" onClick={() => navigate('/citizen/track')}>
              <div className="complaint-card__icon">
                <span style={{ fontSize: 20 }}>{c.icon}</span>
              </div>
              <div className="complaint-card__body">
                <div className="complaint-card__title">{c.title}</div>
                <div className="complaint-card__meta">{c.category} · {c.dept}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="complaint-card__id">{c.id}</span>
                  <span style={{ fontSize: 11, color: 'var(--color-text-secondary)' }}>· {c.date}</span>
                </div>
              </div>
              <div className="complaint-card__right">
                <StatusPill status={c.status} />
                <SLATimer hours={c.slaHours} />
              </div>
            </GlassCard>
          ))}
        </div>
      </div>

    </div>
  );
}
