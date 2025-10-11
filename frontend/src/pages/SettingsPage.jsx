import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import { FiUser, FiLink, FiCreditCard, FiDownload } from 'react-icons/fi';

const SettingsPage = () => {
    const location = useLocation();

    // Configuration for the settings navigation tabs
    const navLinks = [
        { name: 'Profile', href: '/settings/profile', icon: FiUser },
        { name: 'Connections', href: '/settings/accounts', icon: FiLink },
        { name: 'Billing', href: '/settings/billing', icon: FiCreditCard },
        { name: 'Reports', href: '/settings/reports', icon: FiDownload },
    ];

    const baseClasses = 'flex items-center px-4 py-2 font-medium text-sm rounded-md transition-colors duration-200';
    const inactiveClasses = 'text-text-secondary hover:bg-dark-tertiary hover:text-text-primary';
    const activeClasses = 'bg-dark-tertiary text-text-primary';

    return (
        <div className="p-4 md:p-6 animate-fadeIn">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-3xl font-bold text-text-primary mb-6">Settings</h1>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {/* --- Left-side Navigation --- */}
                    <div className="md:col-span-1">
                        <nav className="flex flex-col space-y-2">
                            {navLinks.map(link => (
                                <NavLink
                                    key={link.name}
                                    to={link.href}
                                    // Check if the current URL starts with the link's href for active state
                                    className={location.pathname.startsWith(link.href)
                                        ? clsx(baseClasses, activeClasses)
                                        : clsx(baseClasses, inactiveClasses)
                                    }
                                >
                                    <link.icon className="h-5 w-5 mr-3" />
                                    <span>{link.name}</span>
                                </NavLink>
                            ))}
                        </nav>
                    </div>

                    {/* --- Main Content Area --- */}
                    <div className="md:col-span-3">
                        {/* The nested route (Profile, Accounts, Billing, Reports) will be rendered here */}
                        <div className="bg-dark-surface border border-dark-secondary rounded-lg">
                            <Outlet />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;