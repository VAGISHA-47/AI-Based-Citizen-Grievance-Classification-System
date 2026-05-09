import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export function ProtectedRoute({ children, role }) {
  const token = useAuthStore((s) => s.token) || localStorage.getItem('jansetu_token');
  const activeRole = useAuthStore((s) => s.role) || localStorage.getItem('jansetu_role');

  if (!token && !activeRole) {
    if (role === 'officer') {
      return <Navigate to="/officer/login" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  if (activeRole !== role) {
    // Redirect to their respective dashboard if they try to access the wrong role's routes
    return <Navigate to={activeRole === 'officer' ? '/officer' : '/citizen'} replace />;
  }

  return children;
}
