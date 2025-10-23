import React from 'react';
import { motion } from 'framer-motion';
import { Switch } from '@headlessui/react';
import { STRATEGIES_CONFIG } from 'config/strategies.config';

const StrategyCard = ({ strategy, onToggleStatus, onEdit, onDelete }) => {
  const config = STRATEGIES_CONFIG[strategy.strategy_name];
  const isEnabled = strategy.status === 'active';

  const statusClasses = {
    active: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
    inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    error: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className="bg-white dark:bg-dark-card rounded-xl shadow-md border border-gray-200 dark:border-dark-border p-6 flex flex-col"
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold text-gray-800 dark:text-white">{config?.name || strategy.strategy_name}</h3>
          <p className="text-sm text-gray-500 dark:text-dark-text-secondary">{strategy.symbol} - {strategy.timeframe}</p>
        </div>
        <div className={`px-3 py-1 text-xs font-medium rounded-full ${statusClasses[strategy.status] || statusClasses.inactive}`}>
          {strategy.status}
        </div>
      </div>

      <div className="my-4 space-y-2 text-sm text-gray-600 dark:text-dark-text-secondary">
        {Object.entries(strategy.parameters).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="capitalize">{key.replace('_', ' ')}:</span>
            <span className="font-semibold text-gray-800 dark:text-gray-300">{value}</span>
          </div>
        ))}
      </div>

      <div className="mt-auto pt-4 border-t border-gray-200 dark:border-dark-border flex items-center justify-between">
        <div className="flex items-center">
            <Switch
                checked={isEnabled}
                onChange={() => onToggleStatus(strategy, !isEnabled)}
                className={`${isEnabled ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'}
                relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75`}
            >
                <span className="sr-only">Toggle Strategy</span>
                <span
                aria-hidden="true"
                className={`${isEnabled ? 'translate-x-5' : 'translate-x-0'}
                    pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out`}
                />
            </Switch>
            <span className="ml-3 text-sm font-medium">{isEnabled ? 'Active' : 'Inactive'}</span>
        </div>
        <div className="space-x-2">
          <button onClick={() => onEdit(strategy)} className="px-3 py-1 text-sm font-medium text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded">Edit</button>
          <button onClick={() => onDelete(strategy)} className="px-3 py-1 text-sm font-medium text-red-600 hover:bg-red-100 dark:hover:bg-red-900/50 rounded">Delete</button>
        </div>
      </div>
    </motion.div>
  );
};

export default StrategyCard;