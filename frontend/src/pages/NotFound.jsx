import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-dark-background text-center px-4">
      <h1 className="text-6xl font-bold text-brand-primary">404</h1>
      <h2 className="text-3xl font-semibold text-text-primary mt-4">Page Not Found</h2>
      <p className="text-text-secondary mt-2 max-w-sm">
        Sorry, the page you are looking for does not exist or has been moved.
      </p>
      <Link to="/" className="mt-8">
        <Button variant="primary">
            Go back to Dashboard
        </Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;