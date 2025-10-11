import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import FullPageSpinner from '../components/common/FullPageSpinner';
import NotFoundPage from '../pages/NotFound';

/**
 * A route guard component that protects routes requiring administrator (superuser) privileges.
 *
 * This component performs a multi-level check:
 * 1. Checks if the authentication state has been initialized. If not, it shows a loading spinner
 *    to prevent premature redirects.
 * 2. Checks if a user is authenticated. If not, it redirects them to the login page.
 * 3. Checks if the authenticated user has the `is_superuser` flag. If not, it renders
 *    a 404 Not Found page. This is a crucial security practice to prevent non-admin
 *    users from even knowing that an admin path exists.
 * 4. If all checks pass, it renders the intended child component.
 */
const AdminRoute = ({ children }) => {
  const { isAuthenticated, isInitialized, user } = useAuth();
  const location = useLocation();

  // 1. Wait for the authentication check to complete.
  if (!isInitialized) {
    return <FullPageSpinner />;
  }

  // 2. Redirect to login if the user is not authenticated.
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 3. Render a 404 page if the user is authenticated but is not a superuser.
  if (user && !user.is_superuser) {
    return <NotFoundPage />;
  }

  // 4. Render the protected content if the user is an authenticated superuser.
  return children;
};

export default AdminRoute;