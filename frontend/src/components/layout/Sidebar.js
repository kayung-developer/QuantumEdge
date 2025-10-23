import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from 'contexts/AuthContext';
import api from 'services/api';

// --- Core Components & Icons ---
import { Logo } from 'components/core/Icons';
import ChangelogModal from 'components/core/ChangelogModal';
import {
    ChartPieIcon,
    CpuChipIcon,
    CreditCardIcon,
    UsersIcon,
    PresentationChartLineIcon,
    ShieldCheckIcon,
    BeakerIcon
} from '@heroicons/react/24/outline'; // Added ShieldCheckIcon


const Sidebar = () => {
    const { t } = useTranslation();
    const { user } = useAuth();

    const [version, setVersion] = useState('');
    const [isChangelogOpen, setIsChangelogOpen] = useState(false);

    useEffect(() => {
        api.get('/system/version')
           .then(res => setVersion(res.data.version))
           .catch(err => console.error("Could not fetch system version:", err));
    }, []);

    // --- Navigation Items Definition ---
    const userNavItems = [
        { to: '/dashboard', label: t('sidebar.dashboard'), Icon: ChartPieIcon },
        { to: '/strategies', label: t('sidebar.strategies'), Icon: CpuChipIcon },
        { to: '/backtest', label: t('sidebar.backtest'), Icon: BeakerIcon },
        { to: '/billing', label: t('sidebar.billing'), Icon: CreditCardIcon },
    ];

    const adminNavItems = [
        { to: '/admin/dashboard', label: t('sidebar.adminDashboard'), Icon: PresentationChartLineIcon },
        { to: '/admin/users', label: t('sidebar.userManagement'), Icon: UsersIcon },
        { to: '/admin/payments', label: t('sidebar.payments'), Icon: CreditCardIcon },
    ];

    // --- Styling Classes ---
    const navLinkClasses = "flex items-center px-4 py-3 text-light-text-secondary dark:text-dark-text-secondary hover:bg-gray-200/50 dark:hover:bg-dark-border/20 rounded-lg transition-colors duration-200";
    const activeLinkClasses = "bg-primary/10 text-primary dark:bg-primary/20 font-semibold";

    // A superuser's default dashboard should be the admin one.
    const dashboardPath = user?.role === 'superuser' ? '/admin/dashboard' : '/dashboard';

    return (
        <>
            <aside className="w-64 bg-white dark:bg-dark-card border-r border-light-border dark:border-dark-border flex-shrink-0 flex flex-col">
                {/* Logo Section */}
                <div className="h-20 flex items-center justify-center border-b border-light-border dark:border-dark-border">
                    <Link to={dashboardPath} className="flex items-center gap-2">
                        <Logo className="h-10 w-auto text-primary" />
                        <span className="font-bold text-xl text-light-text dark:text-dark-text">QuantumEdge</span>
                    </Link>
                </div>

                {/* Navigation Section */}
                <nav className="flex-1 p-4 overflow-y-auto">
                    {/* --- THE FIX IS HERE: ALWAYS RENDER USER ITEMS --- */}
                    <p className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">Menu</p>
                    <ul className="space-y-1">
                        {userNavItems.map(({ to, label, Icon }) => (
                            <li key={to}>
                                <NavLink
                                    to={to}
                                    end={to === '/dashboard'}
                                    className={({ isActive }) => `${navLinkClasses} ${isActive ? activeLinkClasses : ''}`}
                                >
                                    <Icon className="h-6 w-6 mr-3" />
                                    <span>{label}</span>
                                </NavLink>
                            </li>
                        ))}
                    </ul>

                    {/* --- CONDITIONALLY RENDER ADMIN ITEMS --- */}
                    {user?.role === 'superuser' && (
                        <div className="mt-6">
                            <p className="px-4 py-2 text-xs font-semibold text-yellow-500/80 uppercase tracking-wider flex items-center">
                                <ShieldCheckIcon className="h-4 w-4 mr-2" />
                                Administrator
                            </p>
                            <ul className="space-y-1">
                                {adminNavItems.map(({ to, label, Icon }) => (
                                    <li key={to}>
                                        <NavLink
                                            to={to}
                                            end={to === '/admin/dashboard'}
                                            className={({ isActive }) => `${navLinkClasses} ${isActive ? activeLinkClasses : ''}`}
                                        >
                                            <Icon className="h-6 w-6 mr-3" />
                                            <span>{label}</span>
                                        </NavLink>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {/* --- END OF FIX --- */}
                </nav>

                {/* Footer Section */}
                <div className="p-4 border-t border-light-border dark:border-dark-border text-center text-xs text-light-text-secondary dark:text-dark-text-secondary space-y-1 flex-shrink-0">
                    <p>Version {version}</p>
                    <button onClick={() => setIsChangelogOpen(true)} className="text-primary hover:underline">
                        What's New
                    </button>
                </div>
            </aside>

            <ChangelogModal isOpen={isChangelogOpen} onClose={() => setIsChangelogOpen(false)} />
        </>
    );
};

export default Sidebar;