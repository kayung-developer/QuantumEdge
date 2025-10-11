import React, { lazy, Suspense } from 'react';
import { useRoutes, Navigate } from 'react-router-dom';

import PrivateRoute from './PrivateRoute.jsx';
import AdminRoute from './AdminRoute.jsx';
import MainLayout from '../components/layout/MainLayout.jsx';
import FullPageSpinner from '../components/common/FullPageSpinner.jsx';

const Loadable = (Component) => (props) => (
  <Suspense fallback={<FullPageSpinner />}>
    <Component {...props} />
  </Suspense>
);

// --- Page Components ---
const LoginPage = Loadable(lazy(() => import('../pages/Login.jsx')));
const RegisterPage = Loadable(lazy(() => import('../pages/RegisterPage.jsx')));
const DashboardPage = Loadable(lazy(() => import('../pages/Dashboard.jsx')));
const TradingPage = Loadable(lazy(() => import('../pages/Trading.jsx')));
const PortfolioPage = Loadable(lazy(() => import('../pages/PortfolioPage.jsx')));
const OnChainPage = Loadable(lazy(() => import('../pages/OnChainPage.jsx')));
const TradeRoomsPage = Loadable(lazy(() => import('../pages/TradeRoomsPage.jsx')));
const ChatRoomPage = Loadable(lazy(() => import('../pages/ChatRoomPage.jsx')));
const MarketplacePage = Loadable(lazy(() => import('../pages/MarketplacePage.jsx')));
const MyStrategiesPage = Loadable(lazy(() => import('../pages/MyStrategiesPage.jsx')));
const StrategyStudioPage = Loadable(lazy(() => import('../pages/StrategyStudioPage.jsx')));
const AdaptiveStudioPage = Loadable(lazy(() => import('../pages/AdaptiveStudioPage.jsx')));
const WalkForwardPage = Loadable(lazy(() => import('../pages/WalkForwardPage.jsx')));
const StrategyForgePage = Loadable(lazy(() => import('../pages/StrategyForgePage.jsx')));
const SettingsPage = Loadable(lazy(() => import('../pages/SettingsPage.jsx')));
const AccountsPage = Loadable(lazy(() => import('../pages/AccountsPage.jsx')));
const ReportsPage = Loadable(lazy(() => import('../pages/ReportsPage.jsx')));
const ProfileSettingsPage = Loadable(lazy(() => import('../pages/ProfileSettingsPage.jsx')));
const NotFoundPage = Loadable(lazy(() => import('../pages/NotFound.jsx')));
const AdminUsersPage = Loadable(lazy(() => import('../pages/admin/AdminUsersPage.jsx')));

const AppRoutes = () => {
  const routes = useRoutes([
    {
      path: '/',
      element: <PrivateRoute><MainLayout /></PrivateRoute>,
      children: [
        // --- CORRECTED: Use `index: true` for the default route ---
        { index: true, element: <Navigate to="/dashboard" replace /> },

        { path: 'dashboard', element: <DashboardPage /> },
        { path: 'trading', element: <TradingPage /> },
        { path: 'portfolio', element: <PortfolioPage /> },
        { path: 'on-chain-intelligence', element: <OnChainPage /> },
        { path: 'trade-rooms', element: <TradeRoomsPage /> },
        { path: 'trade-rooms/:roomId', element: <ChatRoomPage /> },
        { path: 'marketplace', element: <MarketplacePage /> },
        { path: 'my-strategies', element: <MyStrategiesPage /> },
        { path: 'strategy-studio', element: <StrategyStudioPage /> },
        { path: 'adaptive-studio', element: <AdaptiveStudioPage /> },
        { path: 'walk-forward-studio', element: <WalkForwardPage /> },
        { path: 'strategy-forge', element: <StrategyForgePage />},
        {
          path: 'settings',
          element: <SettingsPage />,
          children: [
            // --- CORRECTED: Use `index: true` for the default nested route ---
            { index: true, element: <Navigate to="profile" replace /> },
            { path: 'profile', element: <ProfileSettingsPage /> },
            { path: 'accounts', element: <AccountsPage /> },
            { path: 'reports', element: <ReportsPage /> },
          ]
        },
      ],
    },
    {
      path: '/admin',
      element: <AdminRoute><MainLayout /></AdminRoute>,
      children: [
        { index: true, element: <Navigate to="users" replace /> },
        { path: 'users', element: <AdminUsersPage /> }
      ]
    },
    {
      path: '/login',
      element: <LoginPage />,
    },
    {
      path: '/register', // <-- ADD THIS ENTIRE ROUTE OBJECT
      element: <RegisterPage />,
    },
    {
      path: '*',
      element: <NotFoundPage />,
    },
  ]);

  return routes;
};

export default AppRoutes;