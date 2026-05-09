import React from 'react';
import { Card } from '../../components/ui/Card';
import { User, Mail, Building, Settings, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export function OfficerProfile() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <Card className="glass" style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <div style={{ width: '100px', height: '100px', background: 'var(--color-card-solid)', border: '2px solid rgba(255,255,255,0.06)', borderRadius: 'var(--radius-full)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <User size={48} color="#26878F" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Insp. Ramesh Kumar</h2>
          <div style={{ display: 'flex', gap: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Building size={16} /> Dept of Utilities</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Mail size={16} /> ramesh.k@jansetu.gov</span>
          </div>
        </div>
      </Card>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <Card className="glass" style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Complaints Handled</span>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--teal-primary)', marginTop: '0.5rem' }}>1,402</div>
        </Card>
        <Card className="glass" style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Avg Resolution Time</span>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--status-low)', marginTop: '0.5rem' }}>14h</div>
        </Card>
        <Card className="glass" style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Rating Score</span>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#B45309', marginTop: '0.5rem' }}>4.8<span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/5</span></div>
        </Card>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div>
          <h3 className="section-title">Activity Log</h3>
          <Card className="glass">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.5rem' }}>
                <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-primary)' }}>Resolved Complaint #CMP-8915</p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Today, 02:45 PM</span>
              </div>
              <div style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.5rem' }}>
                <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-primary)' }}>Reassigned Complaint #CMP-8918 to Junior Officer</p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Today, 11:30 AM</span>
              </div>
              <div>
                <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', color: 'var(--text-primary)' }}>Marked Complaint #CMP-8921 as In Progress</p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Yesterday, 04:15 PM</span>
              </div>
            </div>
          </Card>
        </div>

        <div>
          <h3 className="section-title">Settings</h3>
          <Card className="glass" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button className="ui-button ui-button--ghost" style={{ justifyContent: 'flex-start', padding: '0.75rem' }}>
              <Settings size={18} /> Profile Settings
            </button>
            <button className="ui-button ui-button--ghost" style={{ justifyContent: 'flex-start', padding: '0.75rem' }}>
              <Mail size={18} /> Notifications
            </button>
            <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)', margin: '0.5rem 0' }}></div>
            <button className="ui-button ui-button--ghost" style={{ justifyContent: 'flex-start', padding: '0.75rem', color: 'var(--status-high)' }} onClick={() => { logout(); navigate('/officer/login'); }}>
              <LogOut size={18} /> Logout
            </button>
          </Card>
        </div>
      </div>
    </div>
  );
}
