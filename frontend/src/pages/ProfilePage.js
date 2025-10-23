import React from 'react';
import { useAuth } from 'contexts/AuthContext';
import { useTranslation } from 'react-i18next';

const ProfilePage = () => {
    const { user } = useAuth();
    const { t } = useTranslation();

    if (!user) return null;

    return (
        <div className="animate-fade-in max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-light-text dark:text-dark-text mb-8">{t('profile.title')}</h1>
            <div className="glass-card p-8">
                <div className="space-y-6">
                    <div>
                        <label className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{t('profile.fullName')}</label>
                        <p className="text-lg font-semibold">{user.full_name}</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{t('profile.email')}</label>
                        <p className="text-lg font-semibold">{user.email}</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{t('profile.role')}</label>
                        <p className="text-lg font-semibold capitalize">{user.role}</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{t('profile.memberSince')}</label>
                        <p className="text-lg font-semibold">{new Date(user.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="border-t border-white/20 dark:border-dark-border/20 pt-6">
                        <label className="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">{t('profile.subscription')}</label>
                        <p className="text-lg font-semibold capitalize">{user.subscription?.plan || 'N/A'}</p>
                         {user.subscription?.end_date && <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">Renews on {new Date(user.subscription.end_date).toLocaleDateString()}</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;