import React from 'react';
import { useAuth } from 'contexts/AuthContext';
import ThemeToggle from 'components/core/ThemeToggle';
import LanguageSwitcher from 'components/core/LanguageSwitcher';
import { UserCircleIcon, Cog6ToothIcon, CreditCardIcon, ArrowLeftOnRectangleIcon } from '@heroicons/react/24/outline'; // Upgraded Icons
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';

const Header = () => {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success(t('logout.success'));
      navigate('/login');
    } catch (error) {
      toast.error(t('logout.error'));
      console.error("Logout failed:", error);
    }
  };

  return (
    <header className="bg-light-card/80 dark:bg-dark-card/80 backdrop-blur-lg border-b border-light-border/50 dark:border-dark-border/50 p-4 flex justify-end items-center sticky top-0 z-20">
      <div className="flex items-center space-x-6">
        <LanguageSwitcher />
        <ThemeToggle />

        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center space-x-2 p-2 rounded-full hover:bg-light-bg dark:hover:bg-dark-bg/50 transition-colors">
            <UserCircleIcon className="h-8 w-8 text-light-text-secondary dark:text-dark-text-secondary" />
            <div className="hidden md:block text-left">
              <p className="font-semibold text-sm text-light-text dark:text-dark-text">{user?.full_name}</p>
              <p className="text-xs text-light-text-secondary dark:text-dark-text-secondary">{user?.email}</p>
            </div>
          </Menu.Button>
          <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right bg-white dark:bg-dark-card divide-y divide-gray-100 dark:divide-dark-border rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              <div className="px-1 py-1 ">
                <Menu.Item>
                  {({ active }) => (
                    <Link
                      to="/profile"
                      className={`${
                        active ? 'bg-primary text-white' : 'text-gray-900 dark:text-dark-text'
                      } group flex w-full items-center rounded-md px-2 py-2 text-sm transition-colors`}
                    >
                      <Cog6ToothIcon className="mr-2 h-5 w-5" />
                      {t('header.profile')}
                    </Link>
                  )}
                </Menu.Item>
                 <Menu.Item>
                  {({ active }) => (
                    <Link
                      to="/billing"
                      className={`${
                        active ? 'bg-primary text-white' : 'text-gray-900 dark:text-dark-text'
                      } group flex w-full items-center rounded-md px-2 py-2 text-sm transition-colors`}
                    >
                      <CreditCardIcon className="mr-2 h-5 w-5" />
                      {t('header.billing')}
                    </Link>
                  )}
                </Menu.Item>
              </div>
              <div className="px-1 py-1">
                <Menu.Item>
                  {({ active }) => (
                    <button
                      onClick={handleLogout}
                      className={`${
                        active ? 'bg-danger text-white' : 'text-gray-900 dark:text-dark-text'
                      } group flex w-full items-center rounded-md px-2 py-2 text-sm transition-colors`}
                    >
                      <ArrowLeftOnRectangleIcon className="mr-2 h-5 w-5" />
                      {t('header.logout')}
                    </button>
                  )}
                </Menu.Item>
              </div>
            </Menu.Items>
          </Transition>
        </Menu>
      </div>
    </header>
  );
};

export default Header;