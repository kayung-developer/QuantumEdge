import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    // You can return a loader here, but AuthProvider already shows a splash screen
    return null;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;