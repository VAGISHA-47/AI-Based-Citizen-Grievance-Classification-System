import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export function ProtectedRoute({ children, role }) {
  const { user } = useAuthStore();

  if (!user) {
    if (role === 'officer') {
      return <Navigate to="/officer/login" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  if (user.role !== role) {
    // Redirect to their respective dashboard if they try to access the wrong role's routes
    return <Navigate to={user.role === 'officer' ? '/officer' : '/citizen'} replace />;
  }

  return children;
}
