import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

if (!API_BASE_URL) {
  console.error("VITE_API_BASE_URL is not set. Please check your .env file.");
}

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attaches the JWT token to every outgoing request.
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        const decodedToken = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
          console.error("Access token has expired. Logging out.");
          localStorage.removeItem('accessToken');
          window.location.href = '/login';
          return Promise.reject(new Error('Token expired'));
        }

        config.headers['Authorization'] = `Bearer ${token}`;
      } catch (error) {
        console.error("Invalid token found. Clearing token.", error);
        localStorage.removeItem('accessToken');
        return Promise.reject(new Error('Invalid token'));
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handles global API errors, particularly 401 Unauthorized.
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;

    // If the server responds with 401, it means the token is invalid or expired.
    // Force a logout and redirect to the login page.
    if (response && response.status === 401) {
      localStorage.removeItem('accessToken');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;