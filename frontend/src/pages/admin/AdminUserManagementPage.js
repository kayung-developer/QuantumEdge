import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from 'services/api';
import toast from 'react-hot-toast';
import Skeleton from 'components/core/Skeleton';

const AdminUserManagementPage = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [size] = useState(15);
    const navigate = useNavigate();

    const fetchUsers = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await api.get('/admin/users', { params: { page, size } });
            setUsers(data.users);
            setTotal(data.total);
        } catch (error) {
            toast.error("Failed to fetch users.");
        } finally {
            setLoading(false);
        }
    }, [page, size]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    const handleRowClick = (userId) => {
        navigate(`/admin/users/${userId}`);
    };

    const totalPages = Math.ceil(total / size);

    return (
        <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-light-text dark:text-dark-text mb-6">User Management</h1>
            <div className="bg-white dark:bg-dark-card rounded-xl shadow-md border border-light-border dark:border-dark-border overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-light-border dark:divide-dark-border">
                        <thead className="bg-gray-50 dark:bg-gray-800/50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subscription</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-dark-card divide-y divide-light-border dark:divide-dark-border">
                            {loading ? (
                                [...Array(8)].map((_, i) => (
                                    <tr key={i}>
                                        <td colSpan="5" className="px-6 py-4"><Skeleton className="h-10 w-full" /></td>
                                    </tr>
                                ))
                            ) : (
                                users.map(user => (
                                    <tr
                                        key={user.id}
                                        onClick={() => handleRowClick(user.id)}
                                        className="hover:bg-gray-50 dark:hover:bg-dark-border/20 cursor-pointer transition-colors"
                                    >
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900 dark:text-white">{user.full_name}</div>
                                            <div className="text-sm text-gray-500 dark:text-dark-text-secondary">{user.email}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-dark-text-secondary">{user.role}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-dark-text-secondary">{user.subscription?.plan || 'N/A'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-dark-text-secondary">{new Date(user.created_at).toLocaleDateString()}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                {/* Pagination Controls */}
                <div className="px-6 py-3 flex items-center justify-between border-t border-light-border dark:border-dark-border">
                    <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                        Showing <span className="font-medium">{(page - 1) * size + 1}</span> to <span className="font-medium">{Math.min(page * size, total)}</span> of <span className="font-medium">{total}</span> results
                    </p>
                    <div className="space-x-2">
                        <button onClick={() => setPage(p => p - 1)} disabled={page <= 1} className="px-4 py-2 text-sm font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed border dark:border-dark-border">Previous</button>
                        <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages} className="px-4 py-2 text-sm font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed border dark:border-dark-border">Next</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminUserManagementPage;