import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, currency, isProfit = false }) => {
  const formattedValue = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(value || 0);

  const profitColor = value > 0 ? 'text-secondary' : value < 0 ? 'text-danger' : 'text-gray-500';

  return (
    <motion.div
        className="bg-white dark:bg-dark-card p-6 rounded-xl shadow-md border border-gray-200 dark:border-dark-border"
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 300 }}
    >
      <h3 className="text-md font-medium text-gray-500 dark:text-dark-text-secondary">{title}</h3>
      <p className={`text-3xl font-bold mt-2 ${isProfit ? profitColor : 'text-gray-800 dark:text-white'}`}>
        {formattedValue}
      </p>
    </motion.div>
  );
};

export default StatCard;