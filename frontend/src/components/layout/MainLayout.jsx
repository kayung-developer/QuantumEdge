import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

/**
 * The main layout component for the authenticated section of the application.
 * It combines the Sidebar, Header, and a main content area where all
 * pages are rendered via the React Router's <Outlet>.
 */
const MainLayout = () => {
  return (
    <div className="flex h-screen bg-dark-background text-text-primary overflow-hidden">
      {/* Static sidebar for navigation */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Sticky header */}
        <Header />

        {/* Scrollable main content */}
        <main
          id="tour-step-3-main-content"
          className="flex-1 overflow-x-hidden overflow-y-auto bg-dark-background p-4 md:p-6 lg:p-8"
        >
          {/* A max-width container for content to improve readability on large screens */}
          <div className="w-full max-w-screen-2xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;