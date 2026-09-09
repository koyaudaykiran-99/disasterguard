import React, { createContext, useContext, useState } from 'react';
import { UserProfile } from '../types/disaster';

interface AuthContextType {
  user: UserProfile;
  isAuthenticated: boolean;
  toggleReducedMotion: () => void;
  toggleNotifications: () => void;
  updateUserRole: (role: UserProfile['role']) => void;
}

const defaultUser: UserProfile = {
  name: 'Officer Alex Mercer',
  email: 'alex.mercer@disasterguard.gov',
  role: 'DISPATCH_OFFICER',
  badgeNumber: 'DG-78902',
  station: 'Central Command Alpha - Sector 4',
  prefersReducedMotion: false,
  notificationsEnabled: true,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile>(defaultUser);

  const toggleReducedMotion = () => {
    setUser((prev) => ({ ...prev, prefersReducedMotion: !prev.prefersReducedMotion }));
  };

  const toggleNotifications = () => {
    setUser((prev) => ({ ...prev, notificationsEnabled: !prev.notificationsEnabled }));
  };

  const updateUserRole = (role: UserProfile['role']) => {
    setUser((prev) => ({ ...prev, role }));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: true,
        toggleReducedMotion,
        toggleNotifications,
        updateUserRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
