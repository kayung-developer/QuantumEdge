import React from 'react';

const Skeleton = ({ className }) => {
  return (
    <div className={`relative overflow-hidden bg-gray-200 dark:bg-gray-700 rounded-lg ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-300/50 dark:via-gray-600/50 to-transparent animate-shimmer" />
    </div>
  );
};

export default Skeleton;