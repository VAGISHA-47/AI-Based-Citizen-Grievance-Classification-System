import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../../components/shared/Sidebar';
import { PWAInstallBanner } from '../../components/shared/PWAInstallBanner';
import { OfficerBottomNav } from './OfficerBottomNav';
import { AmbientBackground } from '../../components/ui/AmbientBackground';
import { ThemeToggle } from '../../components/ui/ThemeToggle';
import { Bell, ChevronDown } from 'lucide-react';
import './Officer.css';

const PAGE_LABELS = {
  '/officer':             'Command Center',
  '/officer/queue':       'Complaint Queue',
  '/officer/escalations': 'Escalation Management',
  '/officer/analytics':   'Analytics & Intelligence',
  '/officer/profile':     'Officer Profile',
};

export function OfficerLayout() {
  const location = useLocation();
  const label = PAGE_LABELS[location.pathname] || 'Command Center';

  return (
    <div className="officer-app">
      {/* Aurora orbs + cursor spotlight — officer dashboard only */}
      <AmbientBackground showSpotlight={true} />

      <Sidebar />
      <div className="officer-main">
        {/* Sticky glassmorphic header */}
        <header className="officer-header">
          <div className="officer-header__left">
            <h1>{label}</h1>
          </div>
          <div className="officer-header__right">
            <ThemeToggle />
            <div className="officer-header__bell">
              <span className="officer-header__bell-dot" />
              <Bell size={18} />
            </div>
            <div className="officer-header__officer">
              <div className="officer-header__officer-avatar">R</div>
              Insp. Ramesh Kumar
              <ChevronDown size={14} style={{ color: 'var(--text-secondary)' }} />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="officer-main-content">
          <Outlet />
        </div>
      </div>
      <OfficerBottomNav />
      <PWAInstallBanner />
    </div>
  );
}
