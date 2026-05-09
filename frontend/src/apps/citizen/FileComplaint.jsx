import React, { useState, useEffect } from 'react';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { GlassCard } from '../../components/ui/GlassCard';
import { Check, MapPin, Mic, Upload, Zap, CheckCircle, Loader } from 'lucide-react';
import './FileComplaint.css';

// ── 3-step flow: Details → Location → Review ──────────────────────
const STEPS = [
  { label: 'Details',  icon: '📝' },
  { label: 'Location', icon: '📍' },
  { label: 'Review',   icon: '🔍' },
];

const LANGUAGES = ['English', 'हिन्दी', 'मराठी', 'தமிழ்', 'తెలుగు', 'বাংলা', 'ಕನ್ನಡ'];

const CATEGORIES = [
  'Road & Infrastructure', 'Water Supply', 'Sanitation', 'Electricity',
  'Street Lighting', 'Public Health', 'Parks & Recreation', 'Other',
];

const AUTH_SIGNALS = [
  { label: 'AI Confidence',    value: 94 },
  { label: 'Media Validation', value: 87 },
  { label: 'Reputation',       value: 78 },
  { label: 'Geo Match',        value: 91 },
  { label: 'Novelty Score',    value: 82 },
];

export function FileComplaint() {
  const [step, setStep]             = useState(0);
  const [lang, setLang]             = useState('English');
  const [text, setText]             = useState('');
  const [wordCount, setWordCount]   = useState(0);
  const [gps, setGps]               = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [submitted, setSubmitted]   = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setWordCount(text.trim() ? text.trim().split(/\s+/).length : 0);
  }, [text]);

  const captureGPS = () => {
    setGpsLoading(true);
    setTimeout(() => {
      setGps({ lat: 12.9716, lng: 77.5946, address: 'MG Road, Bangalore, Karnataka 560001' });
      setGpsLoading(false);
    }, 1500);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    await new Promise(r => setTimeout(r, 2000));
    setSubmitting(false);
    setSubmitted(true);
  };

  const authTotal = Math.round(AUTH_SIGNALS.reduce((s, a) => s + a.value, 0) / AUTH_SIGNALS.length);

  // ── Success screen ────────────────────────────────────────────────
  if (submitted) {
    return (
      <div className="file-complaint-page">
        <GlassCard layer={2} className="form-card">
          <div className="submit-success">
            <div className="submit-success__checkmark">
              <CheckCircle size={36} color="#2D6A4F" />
            </div>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>Complaint Filed!</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              Your complaint has been submitted and is being processed by our AI engine.
            </p>
            <div className="submit-success__id">#CMP-9001</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center', fontSize: 13, color: 'var(--text-secondary)' }}>
              <span>📱</span> SMS confirmation sent to +91 98765 43210
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'center' }}>
              <Button variant="primary" onClick={() => { setSubmitted(false); setStep(0); setText(''); setGps(null); }}>
                File Another
              </Button>
              <Button variant="outline">Track This Complaint</Button>
            </div>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="file-complaint-page animate-fade-in">

      {/* Step Indicator */}
      <div className="step-indicator">
        {STEPS.map((s, i) => (
          <div key={s.label} className={`step-item ${i < step ? 'done' : i === step ? 'active' : ''}`}>
            <div className="step-circle">
              {i < step ? <Check size={16} strokeWidth={3} /> : i + 1}
            </div>
            <span className="step-label">{s.label}</span>
          </div>
        ))}
      </div>

      {/* ── Step 0: Details ── */}
      {step === 0 && (
        <GlassCard layer={2} className="form-card animate-fade-in">
          <div className="section-label">Complaint Details</div>

          {/* Category */}
          <div className="form-group">
            <label className="form-label">Category</label>
            <select className="form-select">
              <option value="">Select a category…</option>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label">Describe the issue</label>
            <textarea
              className="form-textarea"
              placeholder="Describe the problem in detail. Include what happened, when it started, and how it affects you…"
              value={text}
              onChange={e => setText(e.target.value)}
            />
            <div className="word-count">{wordCount} words</div>
          </div>

          {/* AI Live Preview */}
          {wordCount >= 10 && (
            <div className="ai-preview-card">
              <div className="ai-preview-card__header">
                <Zap size={14} /> AI Reading Your Complaint
              </div>
              <div className="ai-preview-card__row">
                <span className="ai-preview-card__label">Category</span>
                <Badge>Road Safety</Badge>
              </div>
              <div className="ai-preview-card__row">
                <span className="ai-preview-card__label">Priority</span>
                <Badge variant="high">High</Badge>
              </div>
              <div className="ai-preview-card__row">
                <span className="ai-preview-card__label">Confidence</span>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--teal-primary)' }}>94%</span>
              </div>
            </div>
          )}

          {/* Filing Language */}
          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
              Filing Language
            </div>
            <div className="lang-row">
              {LANGUAGES.map(l => (
                <button key={l} className={`lang-chip ${lang === l ? 'active' : ''}`} onClick={() => setLang(l)}>{l}</button>
              ))}
            </div>
          </div>

          <div className="step-nav">
            <Button variant="primary" onClick={() => setStep(1)} style={{ flex: 1 }}>
              Next: Location →
            </Button>
          </div>
        </GlassCard>
      )}

      {/* ── Step 1: Location ── */}
      {step === 1 && (
        <GlassCard layer={2} className="form-card animate-fade-in">
          <div className="section-label">Location &amp; Evidence</div>

          {/* GPS Card */}
          <div className={`gps-card ${gps ? 'captured' : ''}`}>
            <div className="gps-card__icon">
              <MapPin size={22} />
            </div>
            <div className="gps-card__info">
              <div className="gps-card__title">
                {gps ? gps.address : 'Capture your location'}
              </div>
              <div className="gps-card__sub">
                {gps
                  ? `${gps.lat.toFixed(4)}°N, ${gps.lng.toFixed(4)}°E · Zone: Bangalore South ✓`
                  : "We'll use GPS to match the right municipal zone"}
              </div>
            </div>
            {!gps && (
              <Button variant="primary" onClick={captureGPS} style={{ flexShrink: 0 }}>
                {gpsLoading ? <><Loader size={14} style={{ animation: 'spin 0.8s linear infinite' }} /> Detecting…</> : 'Capture GPS'}
              </Button>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Manual Address (optional)</label>
            <input className="form-input" placeholder="Street, Area, City" defaultValue={gps?.address || ''} />
          </div>

          {/* Upload Zone */}
          <div className="upload-zone">
            <div className="upload-zone__icon"><Upload size={22} /></div>
            <div className="upload-zone__title">Attach Evidence</div>
            <div className="upload-zone__sub">Drop photos or videos · JPG, PNG, MP4 · Max 50 MB</div>
          </div>

          <Button variant="outline" style={{ width: '100%' }}>
            <Mic size={16} /> Record Voice Note
          </Button>

          <div className="step-nav">
            <Button variant="outline" onClick={() => setStep(0)}>← Back</Button>
            <Button variant="primary" onClick={() => setStep(2)} style={{ flex: 1 }}>
              Next: Review →
            </Button>
          </div>
        </GlassCard>
      )}

      {/* ── Step 2: Review ── */}
      {step === 2 && (
        <GlassCard layer={2} className="form-card animate-fade-in">
          <div className="section-label">Review &amp; AI Analysis</div>

          {/* Summary */}
          <div style={{
            background: 'rgba(0,157,196,0.04)', border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 14, padding: 16, marginBottom: 20
          }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
              <Badge>Road Safety</Badge>
              <Badge variant="high">High</Badge>
              <Badge variant="active">{lang}</Badge>
              {gps && (
                <Badge style={{ background: 'rgba(45,106,79,0.1)', color: 'var(--status-low)', border: '1px solid rgba(45,106,79,0.2)' }}>
                  📍 GPS Captured
                </Badge>
              )}
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
              {text || 'Pothole on main road causing traffic congestion and risk of accidents near junction…'}
            </p>
          </div>

          {/* Auth Score */}
          <div className="section-label" style={{ marginBottom: 12 }}>Authentication Score</div>
          {AUTH_SIGNALS.map(s => (
            <div key={s.label} className="auth-bar-row">
              <span className="auth-bar-label">{s.label}</span>
              <div className="auth-bar-track">
                <div className="auth-bar-fill" style={{ width: `${s.value}%` }} />
              </div>
              <span className="auth-bar-value">{s.value}%</span>
            </div>
          ))}

          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '14px 16px', background: 'rgba(0,157,196,0.06)',
            borderRadius: 12, marginTop: 16, marginBottom: 20
          }}>
            <div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>Total Auth Score</div>
              <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--teal-primary)' }}>{authTotal}/100</div>
            </div>
            <Badge variant="active" style={{ fontSize: 13, padding: '6px 14px' }}>ACCEPTED</Badge>
          </div>

          <div style={{
            display: 'flex', justifyContent: 'space-between', padding: '12px 16px',
            background: 'rgba(45,106,79,0.06)', borderRadius: 12, marginBottom: 20,
            border: '1px solid rgba(45,106,79,0.15)'
          }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Expected SLA Resolution</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--status-low)' }}>~2.8 days</span>
          </div>

          <div className="step-nav">
            <Button variant="outline" onClick={() => setStep(1)}>← Back</Button>
            <Button variant="primary" onClick={handleSubmit} style={{ flex: 1 }} disabled={submitting}>
              {submitting
                ? <><Loader size={16} style={{ animation: 'spin 0.8s linear infinite' }} /> Submitting…</>
                : 'Submit to JanSetu AI →'
              }
            </Button>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
