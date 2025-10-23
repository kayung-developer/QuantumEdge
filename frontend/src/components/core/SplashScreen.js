import React from 'react';
import { Logo } from './Icons';

const SplashScreen = () => {
  return (
    <div className="fixed inset-0 bg-gray-50 dark:bg-dark-bg flex flex-col items-center justify-center z-50">
      <div className="relative">
        <Logo className="h-20 w-auto text-primary animate-pulse" />
        <div className="absolute -inset-2 border-4 border-primary/20 rounded-full animate-ping"></div>
      </div>
      <p className="mt-8 text-lg font-medium text-gray-600 dark:text-dark-text-secondary">
        Initializing QuantumEdge...
      </p>
    </div>
  );
};

export default SplashScreen;