import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from 'services/api';
import toast from 'react-hot-toast';
import Skeleton from 'components/core/Skeleton';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';
import { STRATEGIES_CONFIG } from 'config/strategies.config';

const AdminUserDetailPage = () => {
    const { userId } = useParams();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchUserDetails = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await api.get(`/admin/users/${userId}/details`);
            setUser(data);
        } catch (error) {
            toast.error("Failed to fetch user details.");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        fetchUserDetails();
    }, [fetchUserDetails]);

    const handleImpersonate = async () => {
        toast.loading("Initiating impersonation...");
        try {
            const { data } = await api.post(`/admin/users/impersonate/${userId}`);
            localStorage.setItem('accessToken', data.access_token);
            // In a real app, you might want a more sophisticated way to handle refresh tokens during impersonation
            localStorage.removeItem('refreshToken');
            toast.dismiss();
            toast.success(`Now impersonating ${user.full_name}. Redirecting...`);
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } catch (error) {
            toast.dismiss();
            toast.error("Impersonation failed.");
        }
    };

    if (loading) {
        return (
            <div className="space-y-4">
                <Skeleton className="h-12 w-1/3" />
                <Skeleton className="h-64 w-full" />
                <Skeleton className="h-48 w-full" />
            </div>
        );
    }

    if (!user) {
        return <p>User not found.</p>;
    }

    return (
        <div className="animate-fade-in">
            <Link to="/admin/users" className="inline-flex items-center gap-2 text-sm text-primary hover:underline mb-6">
                <ArrowLeftIcon className="h-4 w-4" />
                Back to User Management
            </Link>

            <div className="flex justify-between items-start mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-light-text dark:text-dark-text">{user.full_name}</h1>
                    <p className="text-light-text-secondary dark:text-dark-text-secondary">{user.email}</p>
                </div>
                <div className="flex space-x-2">
                    {/* Placeholder for Edit/Deactivate modals */}
                    <button className="px-4 py-2 text-sm font-medium rounded-md border dark:border-dark-border">Edit</button>
                    <button onClick={handleImpersonate} className="px-4 py-2 text-sm font-medium text-white bg-warning hover:bg-yellow-600 rounded-md">Impersonate</button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* User Info & Subscription */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white dark:bg-dark-card rounded-xl p-6 border dark:border-dark-border">
                        <h3 className="font-semibold mb-4">User Details</h3>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between"><span className="text-gray-500">User ID:</span><span className="font-mono text-xs">{user.id}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Role:</span><span className="font-semibold">{user.role}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Status:</span><span className={`font-semibold ${user.is_active ? 'text-success' : 'text-danger'}`}>{user.is_active ? 'Active' : 'Inactive'}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Joined:</span><span>{new Date(user.created_at).toLocaleString()}</span></div>
                        </div>
                    </div>
                    <div className="bg-white dark:bg-dark-card rounded-xl p-6 border dark:border-dark-border">
                        <h3 className="font-semibold mb-4">Subscription</h3>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between"><span className="text-gray-500">Plan:</span><span className="font-semibold capitalize">{user.subscription?.plan || 'N/A'}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Start Date:</span><span>{user.subscription ? new Date(user.subscription.start_date).toLocaleDateString() : 'N/A'}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">End Date:</span><span>{user.subscription?.end_date ? new Date(user.subscription.end_date).toLocaleDateString() : 'N/A'}</span></div>
                        </div>
                    </div>
                </div>

                {/* Strategies & Payments */}
                <div className="lg:col-span-2 space-y-6">
                     <div className="bg-white dark:bg-dark-card rounded-xl p-6 border dark:border-dark-border">
                        <h3 className="font-semibold mb-4">Active Strategies ({user.user_strategies.length})</h3>
                        <div className="space-y-3">
                            {user.user_strategies.length > 0 ? user.user_strategies.map(strat => {
                                const Icon = STRATEGIES_CONFIG[strat.strategy_name]?.Icon || (() => null);
                                return (
                                <div key={strat.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-bg/50 rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <Icon className="h-6 w-6 text-primary"/>
                                        <div>
                                            <p className="font-semibold">{STRATEGIES_CONFIG[strat.strategy_name]?.name}</p>
                                            <p className="text-sm text-gray-500">{strat.symbol} - {strat.timeframe}</p>
                                        </div>
                                    </div>
                                    <span className={`px-2 py-1 text-xs rounded-full ${strat.status === 'active' ? 'bg-success/10 text-success' : 'bg-gray-200 text-gray-600'}`}>{strat.status}</span>
                                </div>
                            )}) : <p className="text-sm text-gray-500 text-center py-4">No strategies configured.</p>}
                        </div>
                    </div>
                     <div className="bg-white dark:bg-dark-card rounded-xl p-6 border dark:border-dark-border">
                        <h3 className="font-semibold mb-4">Payment History</h3>
                         {user.payments.length > 0 ? (
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b dark:border-dark-border">
                                        <th className="text-left pb-2 font-medium text-gray-500">Date</th>
                                        <th className="text-left pb-2 font-medium text-gray-500">Amount</th>
                                        <th className="text-left pb-2 font-medium text-gray-500">Gateway</th>
                                        <th className="text-left pb-2 font-medium text-gray-500">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {user.payments.map(p => (
                                    <tr key={p.id} className="border-b dark:border-dark-border/50">
                                        <td className="py-2">{new Date(p.created_at).toLocaleDateString()}</td>
                                        <td className="py-2">{p.amount} {p.currency}</td>
                                        <td className="py-2 capitalize">{p.gateway}</td>
                                        <td className="py-2 capitalize">{p.status}</td>
                                    </tr>
                                    ))}
                                </tbody>
                            </table>
                         ) : <p className="text-sm text-gray-500 text-center py-4">No payment history.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminUserDetailPage;