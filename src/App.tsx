import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AuthPage } from './components/Auth/AuthPage';
import { DashboardLayout } from './components/Layout/DashboardLayout';
import { ThemeProvider } from './contexts/ThemeContext';
import { AnimationProvider } from './contexts/AnimationContext';
// AddUser from './components/addUser'
const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  return user ? <DashboardLayout /> : < AuthPage/>;
};

function App() {
  return (
    <AnimationProvider>
      <ThemeProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </ThemeProvider>
    </AnimationProvider>
  );
}

export default App;