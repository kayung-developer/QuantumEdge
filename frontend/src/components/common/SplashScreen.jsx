import React from 'react';
import { SiQuantconnect } from 'react-icons/si';
import { motion } from 'framer-motion';

/**
 * A branded, full-screen splash component shown during initial application load
 * while waiting for the first authentication check.
 */
const SplashScreen = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen w-full bg-dark-background">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="flex items-center text-4xl font-bold text-text-primary mb-4"
      >
        <SiQuantconnect className="h-10 w-10 text-brand-primary mr-3" />
        <span>AuraQuant</span>
      </motion.div>
      <div className="flex items-center space-x-2">
        <motion.div
          className="w-3 h-3 rounded-full bg-brand-primary"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut", delay: 0 }}
        ></motion.div>
        <motion.div
          className="w-3 h-3 rounded-full bg-brand-primary"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
        ></motion.div>
        <motion.div
          className="w-3 h-3 rounded-full bg-brand-primary"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut", delay: 0.4 }}
        ></motion.div>
      </div>
      <p className="text-text-secondary mt-4">Initializing Intelligent Trading System...</p>
    </div>
  );
};

export default SplashScreen;