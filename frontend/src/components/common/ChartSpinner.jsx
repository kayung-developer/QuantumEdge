import React from 'react';

/**
 * A loading spinner specifically designed to be an overlay for chart areas
 * or content panels while data is being fetched.
 */
const ChartSpinner = ({ text = "Loading data..." }) => {
  return (
    <div className="absolute inset-0 bg-dark-surface bg-opacity-70 flex flex-col items-center justify-center z-10 animate-fadeIn">
      <div
        className="w-8 h-8 border-4 border-dark-secondary border-t-brand-primary rounded-full animate-spin"
      ></div>
      <span className="mt-4 text-sm text-text-secondary">{text}</span>
    </div>
  );
};

export default ChartSpinner;