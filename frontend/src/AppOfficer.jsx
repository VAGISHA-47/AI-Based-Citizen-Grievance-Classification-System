import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { OfficerLayout } from './apps/officer/OfficerLayout';
import { Dashboard as OfficerDashboard } from './apps/officer/Dashboard';
import { Queue } from './apps/officer/Queue';
import { Analytics } from './apps/officer/Analytics';
import { Escalations } from './apps/officer/Escalations';
import { OfficerProfile } from './apps/officer/OfficerProfile';
import { OfficerLogin } from './apps/officer/OfficerLogin';
import { OfficerJurisdictionSetup } from './apps/officer/OfficerJurisdictionSetup';
import { ProtectedRoute } from './components/shared/ProtectedRoute';

/**
 * Officer/Authority-only frontend application
 * Runs on port 5175
 * Handles complaint management, analytics, and jurisdiction setup
 */
function AppOfficer() {
  console.log('%c🟣 OFFICER APP MOUNTED', 'color: #7C3AED; font-size: 14px; font-weight: bold');
  
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

export default AppOfficer;
