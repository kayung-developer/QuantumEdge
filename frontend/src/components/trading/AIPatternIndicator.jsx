import React from 'react';
import useAIStore from '../../store/aiStore';
import { FiCpu, FiBarChart2 } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * A banner component displayed on the trading page that shows the results
 * of the real-time Computer Vision chart pattern analysis.
 */
const AIPatternIndicator = () => {
  const { patterns, isLoadingPatterns } = useAIStore();

  const renderContent = () => {
    if (isLoadingPatterns) {
      return (
        <div className="flex items-center text-text-secondary animate-pulse">
          <FiCpu className="mr-2 animate-spin" />
          <span>AI is analyzing market patterns...</span>
        </div>
      );
    }

    if (patterns.length === 0) {
      return (
        <div className="flex items-center text-text-secondary">
          <FiBarChart2 className="mr-2" />
          <span>No significant patterns detected in the current view.</span>
        </div>
      );
    }

    const pattern = patterns[0]; // Display the most prominent detected pattern

    return (
      <div className="flex items-center flex-wrap">
        <FiCpu className="mr-2 text-brand-primary flex-shrink-0" />
        <span className="font-bold mr-2">AI Analysis:</span>
        <span className="text-yellow-400 font-semibold mr-1">{pattern.pattern_type}</span>
        <span className="text-text-secondary mr-2">detected</span>
        <span className="hidden md:inline mr-2 text-text-secondary">| Confidence:</span>
        <span className="font-mono bg-dark-tertiary px-2 py-1 rounded-md text-sm">
          {(pattern.confidence_score * 100).toFixed(1)}%
        </span>
         <span className="hidden lg:inline text-text-secondary mx-2">| Recommendation:</span>
         <span className="hidden lg:inline font-semibold">{pattern.recommended_action}</span>
      </div>
    );
  };

  return (
    <AnimatePresence>
      <motion.div
        key={patterns[0]?.pattern_type || 'no-pattern'} // Change key to re-animate on new pattern
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        className="h-full w-full bg-dark-tertiary/60 border border-dark-secondary rounded-md px-4 py-2 text-sm flex items-center"
      >
        {renderContent()}
      </motion.div>
    </AnimatePresence>
  );
};

export default AIPatternIndicator;