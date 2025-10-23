import React from 'react';
import { motion } from 'framer-motion';
import { CheckIcon } from '@heroicons/react/24/solid';

const PricingCard = ({ plan, isCurrent = false, recommended = false, onChoosePlan }) => {
  return (
    <motion.div
      className={`relative p-8 rounded-xl border ${recommended ? 'border-primary shadow-primary/20' : 'border-light-border dark:border-dark-border'} bg-white dark:bg-dark-card shadow-lg flex flex-col`}
      whileHover={{ y: -10, boxShadow: "0 25px 50px -12px rgb(0 0 0 / 0.25)" }}
    >
      {recommended && (
        <div className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-white text-sm font-semibold rounded-full">
          Recommended
        </div>
      )}
      <h3 className="text-2xl font-semibold text-center">{plan.name}</h3>
      <p className="text-center mt-4">
        <span className="text-4xl font-bold">${plan.price}</span>
        {plan.price > 0 && <span className="text-gray-500">/mo</span>}
      </p>
      <ul className="mt-8 space-y-4 flex-grow">
        {plan.features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <CheckIcon className="h-6 w-6 text-success flex-shrink-0 mr-2" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
      <button
        disabled={isCurrent}
        onClick={() => onChoosePlan(plan)} // Pass the selected plan up to the parent
        className={`w-full mt-8 py-3 px-6 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
          isCurrent
            ? 'bg-gray-200 text-gray-500 dark:bg-dark-border dark:text-dark-text-secondary'
            : recommended
            ? 'bg-primary text-white hover:bg-primary-700'
            : 'bg-primary/10 text-primary hover:bg-primary/20 dark:hover:bg-primary/30'
        }`}
      >
        {isCurrent ? 'Current Plan' : 'Choose Plan'}
      </button>
    </motion.div>
  );
};

export default PricingCard;