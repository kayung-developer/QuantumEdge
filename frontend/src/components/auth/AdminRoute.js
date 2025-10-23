import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';
import NotFoundPage from 'pages/NotFoundPage';

const AdminRoute = () => {
  const { user, loading } = useAuth();

  if (loading) {
    // AuthProvider already handles the initial loading state with a splash screen.
    return null;
  }

  // Check if the user is authenticated and has the 'superuser' role.
  if (user && user.role === 'superuser') {
    return <Outlet />;
  }

  // If the user is authenticated but not a superuser, show a 404 page
  // to obscure the existence of the admin panel.
  if (user && user.role !== 'superuser') {
    return <NotFoundPage />;
  }

  // If not authenticated at all, redirect to login.
  return <Navigate to="/login" replace />;
};

export default AdminRoute;