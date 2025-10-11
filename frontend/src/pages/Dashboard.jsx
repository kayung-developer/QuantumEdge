import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import useAuth from '../hooks/useAuth';
import toast from 'react-hot-toast';
import dashboardService from '../api/dashboardService';

import SplashScreen from '../components/common/SplashScreen';
import StatCard from '../components/dashboard/StatCard';
import PortfolioChart from '../components/dashboard/PortfolioChart';
import RecentPositions from '../components/dashboard/RecentPositions';
import AISignalsWidget from '../components/dashboard/AISignalsWidget';
import SentimentFeed from '../components/trading/SentimentFeed'; // Import the new component



import { FiDollarSign, FiTrendingUp, FiList, FiClock } from 'react-icons/fi';
import { format } from 'date-fns';

const DashboardPage = () => {
    const { user } = useAuth();
    const { t } = useTranslation();
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                setLoading(true);
                const response = await dashboardService.getSummary();
                setSummary(response.data);
            } catch (err) {
                console.error("Failed to fetch dashboard summary:", err);
                setError("Could not load dashboard data. Please try again later.");
                toast.error("Failed to load dashboard data.");
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, []);

    if (loading) {
        // Use SplashScreen for a better initial loading experience on the main page
        return <SplashScreen />;
    }

    if (error || !summary) {
        return <div className="text-center p-8 text-danger">{error || "An unknown error occurred."}</div>;
    }

    const { market_status, open_positions_count, total_profit_loss, recent_positions, portfolio_history } = summary;
    const isProfit = total_profit_loss >= 0;

    return (
        <div className="animate-fadeIn space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-text-primary">
                    {t('dashboard.welcomeBack', { name: user?.full_name || user?.email })}
                </h1>
                <p className="text-text-secondary mt-1">
                    Here's your account overview as of {format(new Date(market_status.server_time), 'MMMM dd, yyyy HH:mm zzz')}.
                </p>
            </div>

            {/* Stat Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={<FiDollarSign className="h-6 w-6 text-brand-primary" />}
                    title="Account Balance"
                    value={`$${market_status.account_balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />
                 <StatCard
                    icon={<FiTrendingUp className="h-6 w-6 text-brand-primary" />}
                    title="Total Open P/L"
                    value={`${isProfit ? '+' : ''}$${total_profit_loss.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                    changeColor={isProfit ? 'text-success' : 'text-danger'}
                />
                 <StatCard
                    icon={<FiList className="h-6 w-6 text-brand-primary" />}
                    title="Open Positions"
                    value={open_positions_count}
                />
                  <StatCard
                    icon={<FiClock className="h-6 w-6 text-brand-primary" />}
                    title="Account Equity"
                    value={`$${market_status.account_equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                />
            </div>

            {/* Main Content Grid (Chart and Recent Positions) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-dark-surface border border-dark-secondary rounded-lg p-5 h-[400px]">
                    <h3 className="text-lg font-semibold text-text-primary mb-4">Portfolio Performance</h3>
                    <PortfolioChart data={portfolio_history} />
                </div>
                <div className="lg:col-span-1 h-[400px]">
                    <AISignalsWidget />
                </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 h-[400px]">
                    <SentimentFeed />
                </div>
                 <div className="lg:col-span-1 h-[400px]">
                    <RecentPositions positions={recent_positions} />
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;