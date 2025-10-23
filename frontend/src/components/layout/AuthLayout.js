import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Logo } from 'components/core/Icons';
import ThemeToggle from 'components/core/ThemeToggle';
import LanguageSwitcher from 'components/core/LanguageSwitcher';

const AuthLayout = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-light-bg dark:bg-dark-bg p-4 transition-colors duration-300 relative overflow-hidden">
      {/* Aurora Background */}
      <div className="absolute inset-0 bg-aurora-gradient aurora-background opacity-20 dark:opacity-30" />

      <div className="absolute top-4 right-4 flex items-center space-x-4 z-10">
        <LanguageSwitcher />
        <ThemeToggle />
      </div>

      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, type: 'spring', stiffness: 100 }}
        className="w-full max-w-md z-10"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <Logo className="h-14 w-auto text-primary" />
          </Link>
        </div>
        <div className="glass-card p-8">
          <Outlet />
        </div>
      </motion.div>
    </div>
  );
};

export default AuthLayout;