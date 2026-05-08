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
import { OfficerJurisdictionSetup } from './apps/officer/OfficerJurisdictionSetup';
import { ProtectedRoute } from './components/shared/ProtectedRoute';

function App() {
  const hostname = window.location.hostname;
  const isOfficerDomain = hostname.startsWith('officer.');
  
  if (isOfficerDomain) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/officer/login" replace />} />
          <Route path="/login" element={<Navigate to="/officer/login" replace />} />
          <Route path="/officer/login" element={<OfficerLogin />} />
          <Route path="/officer/setup-location" element={<ProtectedRoute role="officer"><OfficerJurisdictionSetup /></ProtectedRoute>} />
          <Route path="/officer" element={<ProtectedRoute role="officer"><OfficerLayout /></ProtectedRoute>}>
            <Route index element={<OfficerDashboard />} />
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

  // Default to Citizen App (handles citizen.jansetu.in or localhost)
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
        <Route path="/officer/setup-location" element={<ProtectedRoute role="officer"><OfficerJurisdictionSetup /></ProtectedRoute>} />
        <Route path="/officer" element={<ProtectedRoute role="officer"><OfficerLayout /></ProtectedRoute>}>
          <Route index element={<OfficerDashboard />} />
          <Route path="queue" element={<Queue />} />
          <Route path="escalations" element={<Escalations />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="profile" element={<OfficerProfile />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
