import React, { useEffect, useState } from 'react';
import { Badge } from '../../components/ui/Badge';
import { GlassCard } from '../../components/ui/GlassCard';
import CountUpBase from 'react-countup';
const CountUp = CountUpBase.default || CountUpBase;

/* ── Simple SVG Bar Chart (no external deps) ─────────────────────── */
function BarChart({ data }) {
  const max = Math.max(...data.map(d => d.value));
  const W = 420, H = 180, BAR_W = 36, GAP = 8;
  return (
    <svg viewBox={`0 0 ${W} ${H + 40}`} width="100%" style={{ overflow: 'visible' }}>
      {data.map((d, i) => {
        const x = i * (BAR_W + GAP) + GAP;
        const barH = (d.value / max) * H;
        const y = H - barH;
        return (
          <g key={d.label}>
            <rect x={x} y={y} width={BAR_W} height={barH}
              rx={4} fill="url(#barGrad)" opacity={0.85}
            />
            <text x={x + BAR_W / 2} y={H + 16} textAnchor="middle"
              fontSize={10} fill="#5C8DA6" fontFamily="Outfit,sans-serif">
              {d.label.slice(0, 6)}
            </text>
            <text x={x + BAR_W / 2} y={y - 4} textAnchor="middle"
              fontSize={11} fill="#26878F" fontWeight="600" fontFamily="Outfit,sans-serif">
              {d.value}
            </text>
          </g>
        );
      })}
      <defs>
        <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--teal-primary)" />
          <stop offset="100%" stopColor="var(--blue-electric)" />
        </linearGradient>
      </defs>
    </svg>
  );
}

/* ── Simple SVG Donut ────────────────────────────────────────────── */
function Donut({ segments }) {
  const total = segments.reduce((s, d) => s + d.value, 0);
  let start = -Math.PI / 2;
  const R = 60, cx = 80, cy = 80, stroke = 28;
  const paths = segments.map(d => {
    const angle = (d.value / total) * 2 * Math.PI;
    const x1 = cx + R * Math.cos(start);
    const y1 = cy + R * Math.sin(start);
    const x2 = cx + R * Math.cos(start + angle);
    const y2 = cy + R * Math.sin(start + angle);
    const large = angle > Math.PI ? 1 : 0;
    const path = `M ${x1} ${y1} A ${R} ${R} 0 ${large} 1 ${x2} ${y2}`;
    start += angle;
    return { ...d, path };
  });
  return (
    <svg viewBox="0 0 160 160" width={160} height={160}>
      {paths.map((p, i) => (
        <path key={i} d={p.path} fill="none" stroke={p.color} strokeWidth={stroke}
          strokeLinecap="butt" style={{ transition: 'opacity 0.2s' }} />
      ))}
      <text x={cx} y={cy - 6} textAnchor="middle" fontSize={22} fontWeight="700"
        fill="#26878F" fontFamily="Outfit,sans-serif">{total}</text>
      <text x={cx} y={cy + 12} textAnchor="middle" fontSize={11}
        fill="#5C8DA6" fontFamily="Outfit,sans-serif">Total</text>
    </svg>
  );
}

const categoryData = [
  { label: 'Roads',    value: 340 },
  { label: 'Utilities',value: 280 },
  { label: 'Sanitation',value: 210 },
  { label: 'Electric', value: 180 },
  { label: 'Lighting', value: 145 },
  { label: 'Health',   value: 90  },
  { label: 'Parks',    value: 39  },
];

const priorityData = [
  { label: 'High',   value: 312, color: 'var(--status-high)' },
  { label: 'Medium', value: 584, color: 'var(--status-med)' },
  { label: 'Low',    value: 388, color: 'var(--status-low)' },
];

const departments = [
  { name: 'Sanitation Dept',    score: 98, rank: 1 },
  { name: 'Utilities Board',    score: 94, rank: 2 },
  { name: 'Infrastructure Div', score: 82, rank: 3 },
  { name: 'Road Safety Dept',   score: 65, rank: 4 },
  { name: 'Public Works Dept',  score: 48, rank: 5 },
];

const rankColor = (r) => r === 1 ? '#D4AF37' : r === 2 ? '#B8B8B8' : r === 3 ? '#CD7F32' : 'var(--color-text-secondary)';

export function Analytics() {
  const [analyticsData, setAnalyticsData] = useState([]);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const { getAnalytics } = await import('../../services/api');
        const data = await getAnalytics();
        setAnalyticsData(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      }
    };
    loadAnalytics();
  }, []);

  return (
    <div className="animate-fade-in">

      {analyticsData.length > 0 && (
        <GlassCard layer={1} style={{ padding: 12, marginBottom: 16 }}>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            Live analytics records loaded: {analyticsData.length}
          </div>
        </GlassCard>
      )}

      {/* Auth Engine KPIs */}
      <div className="kpi-grid" style={{ marginBottom: 24 }}>
        {[
          { label: 'Accepted',       value: 89.6, suffix: '%', color: 'var(--status-low)' },
          { label: 'Needs Review',   value: 6.3,  suffix: '%', color: 'var(--status-med)' },
          { label: 'Rejected',       value: 4.1,  suffix: '%', color: 'var(--status-high)' },
          { label: 'Clusters Found', value: 117,  suffix: '',  color: 'var(--teal-primary)' },
        ].map((k, i) => (
          <GlassCard key={i} layer={1} hoverEffect={true} style={{ padding: '20px 24px' }}>
            <span className="kpi-card__label">{k.label}</span>
            <span className="kpi-card__value" style={{ color: k.color }}>
              <CountUp end={k.value} decimals={k.value % 1 !== 0 ? 1 : 0} duration={2} suffix={k.suffix} />
            </span>
          </GlassCard>
        ))}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>

        {/* Bar Chart */}
        <GlassCard layer={1} style={{ padding: 24 }}>
          <div className="section-label" style={{ marginBottom: 16 }}>Complaints by Category</div>
          <BarChart data={categoryData} />
        </GlassCard>

        {/* Donut */}
        <GlassCard layer={1} style={{ padding: 24 }}>
          <div className="section-label" style={{ marginBottom: 16 }}>Priority Distribution</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <Donut segments={priorityData} />
            <div style={{ flex: 1 }}>
              {priorityData.map(p => (
                <div key={p.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ width: 12, height: 12, borderRadius: 3, background: p.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, flex: 1, color: 'var(--text-secondary)' }}>{p.label}</span>
                  <span style={{ fontSize: 14, fontWeight: 700, color: p.color }}>{p.value}</span>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Geo Heatmap placeholder */}
      <GlassCard layer={1} style={{ padding: 24, marginBottom: 24 }}>
        <div className="section-label" style={{ marginBottom: 12 }}>Geo-Intelligence Heatmap</div>
        <div style={{
          height: 280, borderRadius: 14, overflow: 'hidden',
          background: 'radial-gradient(circle at center, rgba(38,135,143,0.15) 0%, rgba(6,11,24,1) 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative', border: '1px solid rgba(255,255,255,0.06)'
        }}>
          {/* Simulated complaint circles */}
          {[
            { x: '20%', y: '30%', size: 60, opacity: 0.8, label: '34' },
            { x: '50%', y: '45%', size: 80, opacity: 0.9, label: '51' },
            { x: '70%', y: '25%', size: 40, opacity: 0.6, label: '18' },
            { x: '35%', y: '65%', size: 50, opacity: 0.7, label: '24' },
            { x: '80%', y: '60%', size: 30, opacity: 0.5, label: '11' },
          ].map((c, i) => (
            <div key={i} style={{
              position: 'absolute', left: c.x, top: c.y,
              width: c.size, height: c.size, borderRadius: '50%',
              background: `rgba(255, 77, 109, ${c.opacity * 0.5})`,
              border: `2px solid rgba(255, 77, 109, ${c.opacity})`,
              boxShadow: `0 0 20px rgba(255, 77, 109, ${c.opacity * 0.4})`,
              transform: 'translate(-50%, -50%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: 'var(--status-high)'
            }}>{c.label}</div>
          ))}
          <span style={{ position: 'absolute', bottom: 12, left: 12, fontSize: 11, color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.1)', padding: '4px 10px', borderRadius: 20, backdropFilter: 'blur(8px)' }}>
            📍 Bangalore City
          </span>
        </div>
        <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
          {[
            { color: 'var(--status-high)', label: 'Critical >30' },
            { color: 'var(--status-med)', label: 'Moderate 15–30' },
            { color: 'var(--status-low)', label: 'Low <15' },
          ].map(l => (
            <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: l.color, boxShadow: `0 0 8px ${l.color}` }} />
              {l.label}
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Department Leaderboard */}
      <GlassCard layer={1} style={{ padding: 24 }}>
        <div className="section-label" style={{ marginBottom: 16 }}>Accountability Leaderboard</div>
        {departments.map((d, i) => (
          <div key={d.name} style={{
            display: 'flex', alignItems: 'center', gap: 14,
            padding: '10px 12px', borderRadius: 12,
            marginBottom: 8,
            background: d.rank === 5 ? 'rgba(255, 77, 109, 0.04)' : 'transparent',
            border: d.rank === 5 ? '1px solid rgba(255, 77, 109, 0.12)' : 'none'
          }}>
            <span style={{ fontWeight: 700, fontSize: 16, minWidth: 24, color: rankColor(d.rank) }}>
              {d.rank === 1 ? '🥇' : d.rank === 2 ? '🥈' : d.rank === 3 ? '🥉' : d.rank}
            </span>
            <span style={{ flex: 1, fontSize: 14, fontWeight: 500, color: d.rank === 5 ? 'var(--status-high)' : 'var(--text-primary)' }}>
              {d.name}
            </span>
            <div style={{ width: 120 }}>
              <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${d.score}%`, background: d.score < 70 ? 'linear-gradient(90deg, var(--status-high), var(--status-med))' : 'linear-gradient(135deg, var(--teal-primary), var(--blue-electric))', borderRadius: 3, transition: 'width 0.8s ease-out' }} />
              </div>
            </div>
            <span style={{ fontSize: 14, fontWeight: 700, color: d.score < 70 ? 'var(--status-high)' : 'var(--teal-primary)', minWidth: 48, textAlign: 'right' }}>
              {d.score}%
              {d.rank === 5 && ' ↓'}
            </span>
          </div>
        ))}
      </GlassCard>
    </div>
  );
}
