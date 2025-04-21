import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

export default function RequireAuth({ children, allowedRoles = [] }) {
  const location = useLocation();
  const { isAuthenticated, user, role } = useSelector(state => state.auth);
  
  // Check if user is authenticated
  if (!isAuthenticated) {
    // Redirect to login page but save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // If specific roles are required, check if user has permission
  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    // User is authenticated but doesn't have the required role
    // Redirect to dashboard with access denied message
    return <Navigate to="/dashboard" replace />;
  }
  
  // User is authenticated and has the required role (if any)
  return children;
}
