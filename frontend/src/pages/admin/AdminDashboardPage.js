import React from 'react';

const AdminDashboardPage = () => {
  return (
    <div className="animate-fade-in">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">Admin Dashboard</h1>
      <div className="bg-white dark:bg-dark-card p-6 rounded-xl shadow-md border border-gray-200 dark:border-dark-border">
        <p className="text-center text-gray-500 dark:text-dark-text-secondary py-16">
          Welcome, Administrator. Here you can find system-wide statistics and manage the platform.
        </p>
      </div>
    </div>
  );
};

export default AdminDashboardPage;