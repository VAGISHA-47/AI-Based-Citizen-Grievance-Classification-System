import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './apps/Login';
import { CitizenLayout } from './apps/citizen/CitizenLayout';
import { Home as CitizenHome } from './apps/citizen/Home';
import { FileComplaint } from './apps/citizen/FileComplaint';
import { TrackComplaint } from './apps/citizen/TrackComplaint';
import { Profile } from './apps/citizen/Profile';
import { ProtectedRoute } from './components/shared/ProtectedRoute';

/**
 * Citizen-only frontend application
 * Runs on port 5174
 * Handles complaint filing, tracking, and profile management
 */
function AppCitizen() {
  console.log('%c✅ CITIZEN APP MOUNTED', 'color: #00CED1; font-size: 14px; font-weight: bold');
  
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
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppCitizen;
