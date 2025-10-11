import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { FiSearch, FiBell, FiSun, FiMoon, FiSettings, FiLogOut, FiChevronDown, FiGlobe } from 'react-icons/fi';
import useAuth from '../../hooks/useAuth';
import useTheme from '../../hooks/useTheme';
import { clsx } from 'clsx';
import Button from '../common/Button';

// A list of supported languages for the i18n dropdown.
const languages = [
  { code: 'en', name: 'English' }, { code: 'es', name: 'Español' },
  { code: 'fr', name: 'Français' }, { code: 'zh', name: '中文' },
  { code: 'ja', name: '日本語' }, { code: 'ko', name: '한국어' },
  { code: 'ru', name: 'Русский' }, { code: 'it', name: 'Italiano' },
  { code: 'fi', name: 'Suomi' },
];

/**
 * The main application header, displayed on top of the content area for logged-in users.
 * It contains global search, quick actions, and the user profile menu.
 */
const Header = () => {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  // In a real system, this would be derived from the user's subscription status.
  const hasActiveSubscription = true;

  return (
    <header id="tour-step-2-header" className="h-16 bg-dark-surface border-b border-dark-secondary flex-shrink-0 flex items-center justify-between px-4 md:px-6">
      {/* Left side: Global Search */}
      <div className="relative">
        <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-text-secondary" />
        <input
          type="text"
          placeholder={t('header.searchPlaceholder')}
          className="bg-dark-background border border-dark-secondary rounded-md pl-10 pr-4 py-2 text-sm w-48 sm:w-64 md:w-80 focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-all"
        />
      </div>

      {/* Right side: Actions and User Menu */}
      <div className="flex items-center space-x-2 md:space-x-4">
        {!hasActiveSubscription && (
          <Link to="/pricing">
            <Button size="sm" className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:opacity-90">
              Upgrade Plan
            </Button>
          </Link>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 rounded-full hover:bg-dark-tertiary text-text-secondary hover:text-text-primary transition-colors"
          title="Toggle theme"
        >
            {theme === 'dark' ? <FiSun className="h-5 w-5" /> : <FiMoon className="h-5 w-5" />}
        </button>

        {/* Notifications Button */}
        <button className="p-2 rounded-full hover:bg-dark-tertiary text-text-secondary hover:text-text-primary transition-colors" title="Notifications">
          <FiBell className="h-5 w-5" />
        </button>

        {/* Language Switcher Dropdown */}
        <Menu as="div" className="relative">
          <Menu.Button className="p-2 rounded-full hover:bg-dark-tertiary text-text-secondary hover:text-text-primary transition-colors" title="Change language">
            <FiGlobe className="h-5 w-5" />
          </Menu.Button>
          <Transition as={Fragment} enter="transition ease-out duration-100" enterFrom="transform opacity-0 scale-95" enterTo="transform opacity-100 scale-100" leave="transition ease-in duration-75" leaveFrom="transform opacity-100 scale-100" leaveTo="transform opacity-0 scale-95">
            <Menu.Items className="absolute right-0 mt-2 w-40 origin-top-right rounded-md bg-dark-surface shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
              <div className="py-1">{languages.map((lang) => ( <Menu.Item key={lang.code}>{({ active }) => ( <button onClick={() => changeLanguage(lang.code)} className={clsx('group flex w-full items-center rounded-md px-2 py-2 text-sm', i18n.resolvedLanguage === lang.code ? 'bg-brand-primary/20 text-brand-primary' : 'text-text-secondary', active && 'bg-dark-tertiary' )}>{lang.name}</button> )}</Menu.Item> ))}</div>
            </Menu.Items>
          </Transition>
        </Menu>

        {/* User Profile Dropdown */}
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center space-x-2 p-1 rounded-full hover:bg-dark-tertiary transition-colors">
            <div className="w-8 h-8 rounded-full bg-dark-tertiary flex items-center justify-center font-bold text-brand-primary flex-shrink-0">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
            </div>
            <span className="hidden md:inline text-sm font-medium text-text-primary truncate max-w-[150px]">{user?.full_name || user?.email}</span>
            <FiChevronDown className="hidden md:inline h-4 w-4 text-text-secondary" />
          </Menu.Button>
          <Transition as={Fragment} enter="transition ease-out duration-100" enterFrom="transform opacity-0 scale-95" enterTo="transform opacity-100 scale-100" leave="transition ease-in duration-75" leaveFrom="transform opacity-100 scale-100" leaveTo="transform opacity-0 scale-95">
            <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right divide-y divide-dark-secondary rounded-md bg-dark-surface shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
              <div className="px-1 py-1"><Menu.Item>{({ active }) => ( <Link to="/settings/profile" className={clsx('group flex w-full items-center rounded-md px-2 py-2 text-sm', active ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary')}><FiSettings className="mr-2 h-5 w-5" aria-hidden="true" />{t('header.accountSettings')}</Link> )}</Menu.Item></div>
              <div className="px-1 py-1"><Menu.Item>{({ active }) => ( <button onClick={logout} className={clsx('group flex w-full items-center rounded-md px-2 py-2 text-sm', active ? 'bg-dark-tertiary text-danger' : 'text-text-secondary')}><FiLogOut className="mr-2 h-5 w-5" aria-hidden="true" />{t('header.logout')}</button> )}</Menu.Item></div>
            </Menu.Items>
          </Transition>
        </Menu>
      </div>
    </header>
  );
};

export default Header;