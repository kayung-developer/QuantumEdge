import React, { useState, useEffect, useCallback } from 'react';
import adminService from '../../api/adminService';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import Table from '../common/Table';
import Button from '../common/Button';
import ChartSpinner from '../common/ChartSpinner';
import ConfirmationModal from '../common/ConfirmationModal';
import { FiEdit, FiTrash2, FiCheckCircle, FiXCircle, FiUserPlus } from 'react-icons/fi';

const UserManagementTable = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);

    const fetchUsers = useCallback(async () => {
        try {
            setLoading(true);
            const response = await adminService.getAllUsers({ limit: 200 });
            setUsers(response.data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch users:", err);
            setError("Could not load user data. Please try again later.");
            toast.error("Failed to fetch users.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    const handleDeleteClick = (user) => {
        setSelectedUser(user);
        setIsModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (!selectedUser) return;

        const toastId = toast.loading(`Deleting user ${selectedUser.email}...`);
        try {
            await adminService.deleteUser(selectedUser.id);
            toast.success(`User has been deleted.`, { id: toastId });
            setIsModalOpen(false);
            setSelectedUser(null);
            fetchUsers(); // Refresh the list
        } catch (err) {
            toast.error(err.response?.data?.detail || "Failed to delete user.", { id: toastId });
            setIsModalOpen(false);
            setSelectedUser(null);
        }
    };

    const tableHeaders = [
        { key: 'id', label: 'User ID' }, { key: 'email', label: 'Email' },
        { key: 'fullName', label: 'Full Name' }, { key: 'status', label: 'Status' },
        { key: 'role', label: 'Role' }, { key: 'createdAt', label: 'Date Joined' },
        { key: 'actions', label: 'Actions' },
    ];

    if (loading) return <div className="relative h-64"><ChartSpinner text="Loading users..." /></div>;
    if (error) return <div className="text-center text-danger p-4 bg-danger/10 rounded-md">{error}</div>;

    return (
        <>
            <div className="flex justify-end mb-4">
                <Button size="sm" onClick={() => toast.error('Add user functionality is not yet implemented.')}>
                    <FiUserPlus className="mr-2" />
                    Add New User
                </Button>
            </div>
            <Table headers={tableHeaders}>
                {users.map((user) => (
                    <tr key={user.id} className="hover:bg-dark-tertiary transition-colors text-sm">
                        <td className="px-6 py-4 text-text-secondary">{user.id}</td>
                        <td className="px-6 py-4 font-medium text-text-primary">{user.email}</td>
                        <td className="px-6 py-4 text-text-secondary">{user.full_name || 'N/A'}</td>
                        <td className="px-6 py-4">{user.is_active ? (<span className="flex items-center text-success"><FiCheckCircle className="mr-1.5"/> Active</span>) : (<span className="flex items-center text-danger"><FiXCircle className="mr-1.5"/> Inactive</span>)}</td>
                        <td className="px-6 py-4">{user.is_superuser ? (<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-500/20 text-yellow-400">Admin</span>) : (<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-500/20 text-blue-400">User</span>)}</td>
                        <td className="px-6 py-4 text-text-secondary">{format(new Date(user.created_at), 'MMM dd, yyyy')}</td>
                        <td className="px-6 py-4 font-medium space-x-2">
                            <button className="p-2 text-text-secondary hover:text-brand-primary"><FiEdit className="h-4 w-4" /></button>
                            <button onClick={() => handleDeleteClick(user)} className="p-2 text-text-secondary hover:text-danger"><FiTrash2 className="h-4 w-4" /></button>
                        </td>
                    </tr>
                ))}
            </Table>
            <ConfirmationModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onConfirm={handleConfirmDelete}
                title="Delete User"
                description={`Are you sure you want to permanently delete the user ${selectedUser?.email}? This action cannot be undone.`}
            />
        </>
    );
};

export default UserManagementTable;