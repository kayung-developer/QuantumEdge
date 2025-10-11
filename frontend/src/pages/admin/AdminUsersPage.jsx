import React from 'react';
import UserManagementTable from '../../components/admin/UserManagementTable';
import { FiUsers } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

/**
 * The main page for the administrator's user management panel.
 * It provides a title and description for the user management table.
 */
const AdminUsersPage = () => {
    const { t } = useTranslation();

    return (
        <div className="animate-fadeIn p-4 md:p-6">
            <div className="flex items-center mb-6">
                <FiUsers className="h-8 w-8 text-brand-primary mr-3" />
                <h1 className="text-3xl font-bold text-text-primary">
                    {t('admin.userManagement.title')}
                </h1>
            </div>

            <p className="text-text-secondary mb-6 max-w-2xl">
                {t('admin.userManagement.description')}
            </p>

            <div className="bg-dark-surface border border-dark-secondary rounded-lg p-6">
                 <UserManagementTable />
            </div>
        </div>
    );
};

export default AdminUsersPage;