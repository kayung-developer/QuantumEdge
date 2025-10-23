import React from 'react';
import { useTheme } from 'contexts/ThemeContext';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { SunIcon, MoonIcon, SystemIcon } from './Icons';

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();

  const themes = [
    { name: 'light', icon: SunIcon },
    { name: 'dark', icon: MoonIcon },
    { name: 'system', icon: SystemIcon },
  ];

  const CurrentIcon = themes.find(t => t.name === theme)?.icon || SystemIcon;

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <Menu.Button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <CurrentIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
        </Menu.Button>
      </div>
      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 mt-2 w-36 origin-top-right bg-white dark:bg-dark-card divide-y divide-gray-100 dark:divide-dark-border rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="px-1 py-1">
            {themes.map(({ name, icon: Icon }) => (
              <Menu.Item key={name}>
                {({ active }) => (
                  <button
                    onClick={() => setTheme(name)}
                    className={`${
                      active || theme === name ? 'bg-primary text-white' : 'text-gray-900 dark:text-dark-text'
                    } group flex w-full items-center rounded-md px-2 py-2 text-sm capitalize`}
                  >
                    <Icon className="mr-2 h-5 w-5" />
                    {name}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
};

export default ThemeToggle;