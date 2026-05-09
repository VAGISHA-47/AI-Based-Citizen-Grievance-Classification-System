import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { BottomNav } from '../../components/shared/Navbar';
import { CitizenSidebar } from '../../components/shared/CitizenSidebar';
import { PWAInstallBanner } from '../../components/shared/PWAInstallBanner';
import { AmbientBackground } from '../../components/ui/AmbientBackground';
import { ThemeToggle } from '../../components/ui/ThemeToggle';
import { Bell } from 'lucide-react';
import './Citizen.css';

function PageHeader({ title, subtitle }) {
  const getGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <header className="citizen-page-header">
      <div className="citizen-page-header__left">
        <h1>{title || `${getGreeting()}, Rahul`}</h1>
        <div className="citizen-page-header__subtitle">
          {subtitle || `${new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })} · 2 complaints active`}
        </div>
      </div>
      <div className="citizen-page-header__right">
        <ThemeToggle />
        <div className="header-bell" title="Notifications">
          <span className="header-bell__dot" />
          <Bell size={18} />
        </div>
        <div className="header-avatar">R</div>
      </div>
    </header>
  );
}

export function CitizenLayout() {
  const location = useLocation();

  const getPageMeta = () => {
    if (location.pathname.includes('/file'))    return { title: 'File a Complaint', subtitle: 'Help us improve your neighborhood' };
    if (location.pathname.includes('/track'))   return { title: 'Track Status',       subtitle: 'Live updates on your complaints' };
    if (location.pathname.includes('/profile')) return { title: 'My Profile',         subtitle: 'Manage your account and settings' };
    return null;
  };

  const meta = getPageMeta();

  return (
    <div className="citizen-app">
      {/* Aurora orbs — subtle civic breathing background */}
      <AmbientBackground showSpotlight={false} />

      <CitizenSidebar />
      <main className="citizen-main">
        <PageHeader title={meta?.title} subtitle={meta?.subtitle} />
        <div className="citizen-main-content">
          <Outlet />
        </div>
      </main>
      <BottomNav />
      <PWAInstallBanner />
    </div>
  );
}
