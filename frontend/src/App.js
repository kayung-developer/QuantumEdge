import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { AuthProvider } from 'contexts/AuthContext';
import { ThemeProvider } from 'contexts/ThemeContext';
import { WebSocketProvider } from 'contexts/WebSocketContext';

import ProtectedRoute from 'components/auth/ProtectedRoute';
import AdminRoute from 'components/auth/AdminRoute';
import MainLayout from 'components/layout/MainLayout'; // MainLayout can be reused
import AuthLayout from 'components/layout/AuthLayout';

import DashboardPage from 'pages/DashboardPage';
import StrategiesPage from 'pages/StrategiesPage';
import BacktestPage from 'pages/BacktestPage';
import LoginPage from 'pages/LoginPage';
import RegisterPage from 'pages/RegisterPage';
import NotFoundPage from 'pages/NotFoundPage';
import LandingPage from 'pages/LandingPage';
import BillingPage from 'pages/BillingPage';
import PaymentSuccessPage from 'pages/PaymentSuccessPage';
import PaymentCancelPage from 'pages/PaymentCancelPage';
import AdminDashboardPage from 'pages/admin/AdminDashboardPage';
import AdminUserManagementPage from 'pages/admin/AdminUserManagementPage';
import AdminPaymentsPage from 'pages/admin/AdminPaymentsPage';
import ProfilePage from 'pages/ProfilePage';
import AdminUserDetailPage from 'pages/admin/AdminUserDetailPage';


function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
      <WebSocketProvider>
        <Router>
          <Routes>
            {/* Public landing page */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/payment/success" element={<PaymentSuccessPage />} />
            <Route path="/payment/cancel" element={<PaymentCancelPage />} />

            {/* Authentication Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Protected Application Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/strategies" element={<StrategiesPage />} />
                <Route path="/backtest" element={<BacktestPage />} />
                <Route path="/billing" element={<BillingPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>
            </Route>
            <Route element={<AdminRoute />}>
              <Route element={<MainLayout />}> {/* Reusing MainLayout for consistency */}
                <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
                <Route path="/admin/users" element={<AdminUserManagementPage />} />
                <Route path="/admin/users/:userId" element={<AdminUserDetailPage />} />
                <Route path="/admin/payments" element={<AdminPaymentsPage />} />
              </Route>
            </Route>
            {/* 404 Not Found Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
        <Toaster
          position="top-right"
          toastOptions={{
            className: '',
            style: {
              border: '1px solid #713200',
              padding: '16px',
              color: '#713200',
            },
            success: {
                style: {
                    background: '#D1FAE5',
                    color: '#065F46',
                    border: '1px solid #6EE7B7',
                },
            },
            error: {
                style: {
                    background: '#FEE2E2',
                    color: '#991B1B',
                    border: '1px solid #FCA5A5',
                },
            },
          }}
        />
        </WebSocketProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;