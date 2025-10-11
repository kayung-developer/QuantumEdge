import React from 'react';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { SettingsProvider } from './contexts/SettingsContext'; // Import the new provider
import useAuth from './hooks/useAuth';
import AppRoutes from './routes/AppRoutes';
import SplashScreen from './components/common/SplashScreen';

const AppContent = () => {
    const { isInitialized } = useAuth();
    return isInitialized ? <AppRoutes /> : <SplashScreen />;
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <SettingsProvider> {/* Add the SettingsProvider here */}
          <>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 5000,
                style: {
                  margin: '10px',
                  background: '#161B22',
                  color: '#E6EDF3',
                  border: '1px solid #30363D',
                },
              }}
            />
            <AppContent />
          </>
        </SettingsProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;