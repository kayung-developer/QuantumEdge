import React, { useState, useEffect, useCallback } from 'react';
import api from 'services/api';
import toast from 'react-hot-toast';
import Skeleton from 'components/core/Skeleton';

const AdminPaymentsPage = () => {
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    // Add pagination state if needed

    const fetchPayments = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await api.get('/admin/payments'); // Add pagination params later
            setPayments(data.payments);
        } catch (error) {
            toast.error("Failed to fetch payment records.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPayments();
    }, [fetchPayments]);

    return (
        <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Payment Transactions</h1>
            <div className="bg-white dark:bg-dark-card rounded-xl shadow-md border border-gray-200 dark:border-dark-border overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                         <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transaction ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gateway</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            </tr>
                        </thead>
                         <tbody className="bg-white dark:bg-dark-card divide-y divide-gray-200 dark:divide-dark-border">
                            {loading ? (
                                [...Array(5)].map((_, i) => (
                                    <tr key={i}>
                                        <td colSpan="6" className="px-6 py-4"><Skeleton className="h-8 w-full" /></td>
                                    </tr>
                                ))
                            ) : (
                                payments.map(p => (
                                    <tr key={p.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">{p.gateway_reference}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">{p.user_id}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">{new Intl.NumberFormat().format(p.amount)} {p.currency}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{p.gateway}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{p.status}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(p.created_at).toLocaleString()}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminPaymentsPage;