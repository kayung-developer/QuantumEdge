import React from 'react';
import { SiQuantconnect } from 'react-icons/si';

/**
 * A full-page loading indicator used by route guards (e.g., PrivateRoute)
 * while checking authentication status.
 */
const FullPageSpinner = () => {
  return (
    <div className="flex items-center justify-center h-screen w-full bg-dark-background">
      <div className="flex flex-col items-center">
        <SiQuantconnect className="h-12 w-12 text-brand-primary mb-4 animate-pulse" />
        <div
          className="w-10 h-10 border-4 border-dark-secondary border-t-brand-primary rounded-full animate-spin"
        ></div>
        <span className="mt-4 text-text-secondary">Loading Environment...</span>
      </div>
    </div>
  );
};

export default FullPageSpinner;