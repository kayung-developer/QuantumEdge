import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-dark-bg">
      <div className="text-center">
        <h1 className="text-9xl font-extrabold text-primary">404</h1>
        <p className="text-2xl md:text-3xl font-light text-gray-800 dark:text-dark-text mt-4">
          Sorry, we couldn't find this page.
        </p>
        <p className="mt-4 text-gray-500 dark:text-dark-text-secondary">
          But don't worry, you can find plenty of other things on our homepage.
        </p>
        <Link
          to="/dashboard"
          className="mt-6 inline-block px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-colors"
        >
          Back to Homepage
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;