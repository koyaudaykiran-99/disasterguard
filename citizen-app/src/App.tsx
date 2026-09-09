import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Shell } from './components/navigation/Shell';
import { Home } from './pages/Home';
import { MapPage } from './pages/Map';
import { AlertsPage } from './pages/Alerts';
import { EmergencyPage } from './pages/Emergency';
import { SheltersPage } from './pages/Shelters';
import { HospitalsPage } from './pages/Hospitals';
import { ProfilePage } from './pages/Profile';
import { LanguageProvider } from './context/LanguageContext';

const AnimatedRoutes: React.FC = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/emergency" element={<EmergencyPage />} />
        <Route path="/shelters" element={<SheltersPage />} />
        <Route path="/hospitals" element={<HospitalsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*" element={<Home />} />
      </Routes>
    </AnimatePresence>
  );
};

export const App: React.FC = () => {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Shell>
          <AnimatedRoutes />
        </Shell>
      </BrowserRouter>
    </LanguageProvider>
  );
};

export default App;
