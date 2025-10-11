import { useContext } from 'react';
import AuthContext from '../contexts/AuthContext.jsx';

/**
 * A custom hook that provides a convenient shortcut to access the AuthContext.
 * It ensures that the hook is used within a component tree that is wrapped
 * by an AuthProvider, throwing an error if it's not.
 *
 * @returns {object} The full authentication context value, including:
 *   - isAuthenticated: boolean
 *   - isInitialized: boolean
 *   - user: object | null
 *   - login: function
 *   - logout: function
 *
 * @example
 * const { isAuthenticated, user, login, logout } = useAuth();
 */
const useAuth = () => {
  const context = useContext(AuthContext);

  // This check is a crucial safeguard. If a developer forgets to wrap a
  // component in AuthProvider, this will provide a clear and immediate error.
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider component tree.');
  }

  return context;
};

export default useAuth;