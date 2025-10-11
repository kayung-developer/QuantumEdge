import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    // --- CORRECT: Import ONLY 'Lu' icons from 'react-icons/lu' ---
    LuLayoutDashboard,
    LuSettings,
    LuLogOut,
    LuUsers,
    LuFlaskConical,
    LuCpu,
    LuStepForward,
    LuBriefcase,
    LuLink
} from 'react-icons/lu';
import {
    // --- CORRECT: Import ONLY 'Fi' icons from 'react-icons/fi' ---
    FiBarChart2,
    FiShoppingBag,
    FiGitBranch,
    FiMessageSquare
} from 'react-icons/fi';
import { SiQuantconnect } from "react-icons/si";
import useAuth from '../../hooks/useAuth.js';
import { clsx } from 'clsx';

const Sidebar = () => {
    const { user, logout } = useAuth();
    const { t } = useTranslation();

    const navConfig = [
        // --- PRIMARY VIEWS ---
        { type: 'link', name: "Dashboard", href: '/dashboard', icon: LuLayoutDashboard },
        { type: 'link', name: "AI Smart Trading", href: '/trading', icon: FiBarChart2, id: 'tour-step-4-trading-link' },
        { type: 'link', name: "Portfolio", href: '/portfolio', icon: LuBriefcase },
        { type: 'link', name: "On-Chain", href: '/on-chain-intelligence', icon: LuLink },

        // --- ECOSYSTEM ---
        { type: 'heading', name: 'ECOSYSTEM' },
        { type: 'link', name: "Trade Rooms", href: '/trade-rooms', icon: FiMessageSquare },
        { type: 'link', name: "Marketplace", href: '/marketplace', icon: FiShoppingBag },
        { type: 'link', name: "My Strategies", href: '/my-strategies', icon: FiGitBranch },

        // --- ADVANCED TOOLS ---
        { type: 'heading', name: 'STUDIOS' },
        { type: 'link', name: "Strategy Studio", href: '/strategy-studio', icon: LuFlaskConical },
        { type: 'link', name: "Walk-Forward Studio", href: '/walk-forward-studio', icon: LuStepForward },
        { type: 'link', name: "Adaptive Studio", href: '/adaptive-studio', icon: LuCpu },

        // --- MANAGEMENT ---
        { type: 'heading', name: 'MANAGEMENT' },
        { type: 'link', name: "Settings", href: '/settings/profile', icon: LuSettings },
    ];

    if (user?.is_superuser) {
        navConfig.push({ type: 'link', name: "Admin Panel", href: '/admin/users', icon: LuUsers });
    }

    const NavItem = ({ item }) => {
        if (item.type === 'heading') { return <p className="px-4 pt-4 pb-2 text-xs font-semibold text-text-secondary uppercase tracking-wider">{item.name}</p>; }
        const baseClasses = 'flex items-center px-4 py-2.5 text-sm font-medium rounded-md transition-colors duration-200 mx-2';
        const inactiveClasses = 'text-text-secondary hover:bg-dark-tertiary hover:text-text-primary';
        const activeClasses = 'bg-brand-primary/20 text-brand-primary';
        return ( <NavLink to={item.href} className={({ isActive }) => isActive || (item.href !== '/dashboard' && window.location.pathname.startsWith(item.href)) ? clsx(baseClasses, activeClasses) : clsx(baseClasses, inactiveClasses) } end={item.href === '/dashboard'} id={item.id}> <item.icon className="h-5 w-5 mr-3 flex-shrink-0" /> <span>{item.name}</span> </NavLink> );
    };

    return (
        <aside id="tour-step-1-sidebar" className="w-64 flex-shrink-0 bg-dark-surface border-r border-dark-secondary flex flex-col">
            <div className="h-16 flex items-center justify-center px-4 border-b border-dark-secondary flex-shrink-0"><Link to="/" className="flex items-center text-xl font-bold text-text-primary"><SiQuantconnect className="h-7 w-7 text-brand-primary mr-2" /><span>AuraQuant</span></Link></div>
            <nav className="flex-1 py-4 space-y-1 overflow-y-auto">{navConfig.map((item, index) => (<NavItem key={`${item.name}-${index}`} item={item} />))}</nav>
            <div className="px-4 py-4 border-t border-dark-secondary flex-shrink-0"><div className="flex items-center"><div className="w-10 h-10 rounded-full bg-dark-tertiary flex items-center justify-center font-bold text-brand-primary flex-shrink-0">{user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}</div><div className="ml-3 overflow-hidden"><p className="text-sm font-semibold text-text-primary truncate">{user?.full_name || 'User'}</p><p className="text-xs text-text-secondary truncate">{user?.email}</p></div></div><button onClick={logout} className="w-full flex items-center mt-4 px-4 py-2 text-sm font-medium text-text-secondary rounded-md hover:bg-dark-tertiary hover:text-danger"><LuLogOut className="h-5 w-5 mr-3" /><span>{t('header.logout')}</span></button></div>
        </aside>
    );
};

export default Sidebar;