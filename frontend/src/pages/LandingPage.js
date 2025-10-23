import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Logo, ArrowRightIcon } from 'components/core/Icons';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg text-gray-800 dark:text-dark-text">
      {/* Header */}
      <header className="py-4 px-8 flex justify-between items-center">
        <Logo className="h-10 w-auto text-primary" />
        <Link to="/login" className="px-6 py-2 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-colors">
          Launch App
        </Link>
      </header>

      {/* Hero Section */}
      <main className="text-center py-20 px-4">
        <motion.h1
          className="text-5xl md:text-7xl font-extrabold"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          Automate. Analyze. <span className="text-primary">Ascend.</span>
        </motion.h1>
        <motion.p
          className="mt-6 max-w-2xl mx-auto text-lg text-gray-500 dark:text-dark-text-secondary"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Unleash the power of AI-driven, automated trading with QuantumEdge. Connect your MT5 account and let our advanced strategies work for you 24/7.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Link to="/register" className="mt-10 inline-flex items-center px-8 py-4 bg-secondary text-white font-bold text-lg rounded-xl shadow-lg hover:bg-green-600 transition-transform hover:scale-105">
            Start Your Free Trial <ArrowRightIcon className="ml-2 h-6 w-6" />
          </Link>
        </motion.div>
      </main>
    </div>
  );
};

export default LandingPage;