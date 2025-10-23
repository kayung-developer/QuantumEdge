import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import FeedbackWidget from 'components/core/FeedbackWidget';

const MainLayout = () => {
  return (
    <div className="flex h-screen bg-gray-100 dark:bg-dark-bg text-gray-800 dark:text-dark-text">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 dark:bg-dark-bg p-6">
          <div className="container mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
     <FeedbackWidget />
    </div>
  );
};

export default MainLayout;