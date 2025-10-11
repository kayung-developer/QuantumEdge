import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

/**
 * A reusable card component for displaying a single, important statistic on the dashboard.
 * @param {React.ReactNode} icon - The icon to display.
 * @param {string} title - The title of the statistic.
 * @param {string} value - The main value to display.
 * @param {string} [change] - Optional change value (e.g., "+1.5%").
 * @param {string} [changeColor] - Tailwind CSS color class for the change text (e.g., 'text-success').
 */
const StatCard = ({ icon, title, value, change, changeColor }) => {
  return (
    <motion.div
      className="bg-dark-surface border border-dark-secondary rounded-lg p-5 flex items-center space-x-4"
      whileHover={{ translateY: -5, boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)" }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex-shrink-0 bg-dark-tertiary p-3 rounded-full">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-text-secondary">{title}</p>
        <div className="flex items-baseline space-x-2">
          <p className="text-2xl font-bold text-text-primary">{value}</p>
          {change && (
            <span className={clsx('text-sm font-semibold', changeColor)}>
              {change}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default StatCard;