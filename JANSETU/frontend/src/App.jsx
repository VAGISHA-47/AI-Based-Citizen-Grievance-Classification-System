import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './apps/Login';
import { CitizenLayout } from './apps/citizen/CitizenLayout';
import { Home as CitizenHome } from './apps/citizen/Home';
import { FileComplaint } from './apps/citizen/FileComplaint';
import { TrackComplaint } from './apps/citizen/TrackComplaint';
import { Profile } from './apps/citizen/Profile';

import { OfficerLayout } from './apps/officer/OfficerLayout';
import { Dashboard as OfficerDashboard } from './apps/officer/Dashboard';
import { Queue } from './apps/officer/Queue';
import { Analytics } from './apps/officer/Analytics';

import { Escalations } from './apps/officer/Escalations';
import { OfficerProfile } from './apps/officer/OfficerProfile';
import { OfficerLogin } from './apps/officer/OfficerLogin';
import { ProtectedRoute } from './components/shared/ProtectedRoute';

// Helper function to check if accessing officer routes
function isOfficerPath(pathname) {
  return pathname.startsWith('/officer');
}

// Catch-all route component that redirects based on path
function CatchAllRoute() {
  const pathname = window.location.pathname;
  if (isOfficerPath(pathname)) {
    return <Navigate to="/officer/login" replace />;
  }
  return <Navigate to="/login" replace />;
}

function App() {
  const hostname = window.location.hostname;
  const port = window.location.port;
  const pathname = window.location.pathname;
  
  // Officer portal: subdomain (officer.*) OR port (5174/5175) OR path starts with /officer
  const isOfficerDomain = hostname.startsWith('officer.') || port === '5174' || port === '5175' || pathname.startsWith('/officer');
  
  if (isOfficerDomain) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/officer/login" replace />} />
          <Route path="/login" element={<Navigate to="/officer/login" replace />} />
          <Route path="/officer/login" element={<OfficerLogin />} />
          <Route path="/officer" element={<ProtectedRoute role="officer"><OfficerLayout /></ProtectedRoute>}>
            <Route index element={<OfficerDashboard />} />
            <Route path="dashboard" element={<OfficerDashboard />} />
            <Route path="queue" element={<Queue />} />
            <Route path="escalations" element={<Escalations />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="profile" element={<OfficerProfile />} />
          </Route>
          <Route path="*" element={<Navigate to="/officer/login" replace />} />
        </Routes>
      </BrowserRouter>
    );
  }

  // Default to Citizen App
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/citizen" element={<ProtectedRoute role="citizen"><CitizenLayout /></ProtectedRoute>}>
          <Route index element={<CitizenHome />} />
          <Route path="file" element={<FileComplaint />} />
          <Route path="track" element={<TrackComplaint />} />
          <Route path="profile" element={<Profile />} />
        </Route>
        
        {/* Local Dev Access to Officer App fallback if not using subdomains */}
        <Route path="/officer/login" element={<OfficerLogin />} />
        <Route path="/officer" element={<ProtectedRoute role="officer"><OfficerLayout /></ProtectedRoute>}>
          <Route index element={<OfficerDashboard />} />
          <Route path="dashboard" element={<OfficerDashboard />} />
          <Route path="queue" element={<Queue />} />
          <Route path="escalations" element={<Escalations />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="profile" element={<OfficerProfile />} />
        </Route>
        
        {/* Wildcard: If trying to access /officer/* without proper setup, redirect to /officer/login */}
        <Route path="*" element={<CatchAllRoute />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
