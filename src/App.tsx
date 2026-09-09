import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { AuthProvider } from './context/AuthContext';
import { DisasterProvider } from './context/DisasterContext';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardPage } from './pages/DashboardPage';
import { AlertsPage } from './pages/AlertsPage';
import { MapPage } from './pages/MapPage';
import { EmergencyPage } from './pages/EmergencyPage';
import { SafeZonesPage } from './pages/SafeZonesPage';
import { ProfilePage } from './pages/ProfilePage';
import { AIAssistantPage } from './pages/AIAssistantPage';

export const AppContent: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>('/dashboard');

  // Sync hash routing if browser changes
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash && ['/dashboard', '/ai-assistant', '/alerts', '/map', '/emergency', '/safe-zones', '/profile'].includes(hash)) {
        setCurrentPath(hash);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigateTo = (path: string) => {
    setCurrentPath(path);
    window.location.hash = path;
  };

  const renderCurrentPage = () => {
    switch (currentPath) {
      case '/ai-assistant':
        return <AIAssistantPage key="/ai-assistant" />;
      case '/alerts':
        return <AlertsPage key="/alerts" />;
      case '/map':
        return <MapPage key="/map" />;
      case '/emergency':
        return <EmergencyPage key="/emergency" />;
      case '/safe-zones':
        return <SafeZonesPage key="/safe-zones" />;
      case '/profile':
        return <ProfilePage key="/profile" />;
      case '/dashboard':
      default:
        return <DashboardPage key="/dashboard" />;
    }
  };

  return (
    <div className="flex min-h-screen bg-command-bg text-gray-100 font-sans selection:bg-blue-600 selection:text-white">
      {/* Sidebar */}
      <Sidebar currentPath={currentPath} onNavigate={navigateTo} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-x-hidden">
          <AnimatePresence mode="wait">
            {renderCurrentPage()}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <DisasterProvider>
        <AppContent />
      </DisasterProvider>
    </AuthProvider>
  );
}
