import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import FullPageSpinner from '../components/common/FullPageSpinner';

/**
 * A route guard component that protects routes requiring any authenticated user.
 *
 * This component performs two main checks:
 * 1. Checks if the authentication state has been initialized. This prevents a common
 *    bug where a user is briefly redirected to the login page on a page refresh
 *    before their token has been validated.
 * 2. Checks if the user is authenticated. If they are, it renders the child component.
 *    If not, it redirects them to the login page, saving the location they were
 *    trying to access so they can be sent there after a successful login.
 */
const PrivateRoute = ({ children }) => {
  const { isAuthenticated, isInitialized } = useAuth();
  const location = useLocation();

  // 1. Show a full-page spinner while the initial authentication check is running.
  if (!isInitialized) {
    return <FullPageSpinner />;
  }

  // 2. If the check is complete and the user is authenticated, render the page.
  if (isAuthenticated) {
    return children;
  }

  // 3. If the check is complete and the user is not authenticated, redirect to login.
  return <Navigate to="/login" state={{ from: location }} replace />;
};

export default PrivateRoute;