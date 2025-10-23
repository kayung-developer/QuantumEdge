import axios from 'axios';
import toast from 'react-hot-toast';

// Set the base URL from environment variables for flexibility
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add the JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor to handle token expiration and refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check for 401 error and ensure it's not a retry request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark this request as a retry

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          // If no refresh token, logout is inevitable.
          localStorage.removeItem('accessToken');
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Use a new axios instance for the refresh token request to avoid interceptor loop
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
        });

        // Update stored tokens
        localStorage.setItem('accessToken', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);

        // Update the authorization header for the original request and retry it
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);

      } catch (refreshError) {
        // If refresh token fails, clear everything and redirect to login
        console.error("Token refresh failed:", refreshError);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');

        toast.error("Your session has expired. Please log in again.");

        // Use a slight delay to ensure the toast is visible before redirecting
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);

        return Promise.reject(refreshError);
      }
    }

    // For all other errors, just pass them along
    return Promise.reject(error);
  }
);

// THIS IS THE CRUCIAL LINE THAT WAS MISSING OR INCORRECTLY OMITTED.
export default api;