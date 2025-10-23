import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import api from 'services/api';
import Joyride, { STATUS } from 'react-joyride';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import StatCard from 'components/dashboard/StatCard';
import RecentTrades from 'components/dashboard/RecentTrades';
import { useAuth } from 'contexts/AuthContext';
import Skeleton from 'components/core/Skeleton';
import WelcomeScreen from 'components/core/WelcomeScreen';
import TradingChart from 'components/dashboard/TradingChart';

const DashboardPage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [accountInfo, setAccountInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runTour, setRunTour] = useState(!localStorage.getItem('tour_completed'));

  const tourSteps = [
    {
      target: '#tour-step-1',
      content: t('tour.step1'),
      disableBeacon: true,
    },
    {
      target: '#tour-step-2',
      content: t('tour.step2'),
    },
    {
      target: '#tour-step-3',
      content: t('tour.step3'),
    },
    {
      target: '#tour-step-4',
      content: t('tour.step4'),
      placement: 'top',
    },
  ];

  useEffect(() => {
    const fetchAccountInfo = async () => {
      try {
        setLoading(true);
        const response = await api.get('/mt5/account');
        setAccountInfo(response.data);
      } catch (error) {
        console.error("Failed to fetch account info:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAccountInfo();
  }, []);

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
      localStorage.setItem('tour_completed', 'true');
    }
  };

  // Dummy data for the chart
  const equityData = [
    { name: 'Jan', equity: 10000 },
    { name: 'Feb', equity: 10250 },
    { name: 'Mar', equity: 10100 },
    { name: 'Apr', equity: 10500 },
    { name: 'May', equity: 10800 },
    { name: 'Jun', equity: 11200 },
  ];

  return (
    <div className="animate-fade-in">
    <WelcomeScreen />
      <Joyride
        steps={tourSteps}
        run={runTour}
        continuous
        showProgress
        showSkipButton
        callback={handleJoyrideCallback}
        styles={{
            options: {
              zIndex: 10000,
            },
        }}
      />
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6" id="tour-step-1">
        {t('dashboard.welcome', { name: user?.full_name?.split(' ')[0] })}
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6" id="tour-step-2">
        {loading ? (
            <>
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
            </>
        ) : (
          <>
            <StatCard title={t('dashboard.balance')} value={accountInfo?.balance} currency={accountInfo?.currency} />
            <StatCard title={t('dashboard.equity')} value={accountInfo?.equity} currency={accountInfo?.currency} />
            <StatCard title={t('dashboard.profit')} value={accountInfo?.profit} currency={accountInfo?.currency} isProfit={true} />
            <StatCard title={t('dashboard.freeMargin')} value={accountInfo?.margin_free} currency={accountInfo?.currency} />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-dark-card p-6 rounded-xl shadow-md border border-gray-200 dark:border-dark-border" id="tour-step-3">
          <h2 className="text-xl font-semibold mb-4">{t('dashboard.equityCurve')}</h2>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <AreaChart data={equityData}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#4F46E5" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" className="dark:stroke-dark-border" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="equity" stroke="#4F46E5" fillOpacity={1} fill="url(#colorEquity)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
     <div className="glass-card p-4 md:p-6" id="tour-step-3">
        <h2 className="text-xl font-semibold mb-4 text-light-text dark:text-dark-text">Live Market: EURUSD H1</h2>
           <TradingChart symbol="EURUSD" />

      </div>
        <div className="bg-white dark:bg-dark-card p-6 rounded-xl shadow-md border border-gray-200 dark:border-dark-border" id="tour-step-4">
          <h2 className="text-xl font-semibold mb-4">{t('dashboard.recentTrades')}</h2>
          <RecentTrades />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;