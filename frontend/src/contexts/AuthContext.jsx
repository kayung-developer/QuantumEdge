import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import axiosClient from '../api/axiosClient';
import toast from 'react-hot-toast';

// Create the context with a default null value.
const AuthContext = createContext(null);

const initialState = {
  isAuthenticated: false,
  isInitialized: false, // Tracks if the initial token check has completed.
  user: null,
};

/**
 * The AuthProvider component is a wrapper that provides authentication state
 * and functions (login, logout) to the entire application. It handles session
 * persistence by checking localStorage for a valid JWT on initial load.
 */
export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState(initialState);

  /**
   * Performs the initial authentication check on application startup.
   * It looks for a token in localStorage, validates it, and fetches user data if valid.
   * This function is memoized with useCallback to prevent re-creation on every render.
   */
  const initializeAuth = useCallback(async () => {
    try {
      const accessToken = window.localStorage.getItem('accessToken');

      if (accessToken) {
        // Decode token to check expiration without an API call first.
        const decodedToken = jwtDecode(accessToken);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp > currentTime) {
          // Token is present and not expired, now verify with the backend and fetch user data.
          const response = await axiosClient.get('/users/me');
          setAuthState({
            isAuthenticated: true,
            isInitialized: true,
            user: response.data,
          });
        } else {
          // Token is expired, clear it.
          window.localStorage.removeItem('accessToken');
          setAuthState({ ...initialState, isInitialized: true });
        }
      } else {
        // No token found.
        setAuthState({ ...initialState, isInitialized: true });
      }
    } catch (err) {
      console.error('Auth initialization error:', err);
      // If any error occurs (e.g., malformed token), reset to a clean, unauthenticated state.
      window.localStorage.removeItem('accessToken');
      setAuthState({ ...initialState, isInitialized: true });
    }
  }, []);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  /**
   * Handles user login by calling the backend, storing the received token,
   * and fetching the user's profile data.
   */
  const login = async (email, password) => {
    try {
      // The backend expects form-data for the token endpoint.
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await axiosClient.post('/login/access-token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const { access_token } = response.data;
      window.localStorage.setItem('accessToken', access_token);

      // After setting the token, our axios interceptor will use it for the next request.
      const userResponse = await axiosClient.get('/users/me');
      setAuthState({
        isAuthenticated: true,
        isInitialized: true,
        user: userResponse.data,
      });
      toast.success('Login successful!');
      // Navigation is handled by the LoginPage component upon successful promise resolution.
    } catch (error) {
      console.error('Login failed:', error);
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
      throw error; // Re-throw to allow the form to handle the loading state.
    }
  };

  /**
   * Handles user logout by clearing the token and resetting the auth state.
   */
  const logout = useCallback(() => {
    window.localStorage.removeItem('accessToken');
    setAuthState({ ...initialState, isInitialized: true });
    toast.success('You have been logged out.');
    // The redirect to /login is handled automatically by the PrivateRoute component
    // when it detects that isAuthenticated is now false.
  }, []);

  const contextValue = {
    ...authState,
    initializeAuth, // Expose for re-fetching user data after updates
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;