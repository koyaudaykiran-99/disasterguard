import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService, AuthTokenResponse, SafetyProfileData } from '../services/auth/authService';
import { useLanguage } from './LanguageContext';

export interface UserSession {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
}

interface AuthContextType {
  user: UserSession | null;
  token: string | null;
  safetyProfile: SafetyProfileData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (emailOrPhone: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (
    name: string,
    emailOrPhone: string,
    password: string,
    safetyProfile?: SafetyProfileData
  ) => Promise<void>;
  logout: () => void;
  updateSafetyProfile: (profile: Partial<SafetyProfileData>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'dg_citizen_token';
const USER_KEY = 'dg_citizen_user';
const SAFETY_KEY = 'dg_citizen_safety';
const REMEMBER_KEY = 'dg_citizen_remember';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserSession | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [safetyProfile, setSafetyProfile] = useState<SafetyProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { setLanguage } = useLanguage();

  // Restore session on mount
  useEffect(() => {
    try {
      const isRemembered = localStorage.getItem(REMEMBER_KEY) === 'true';
      const storage = isRemembered ? localStorage : sessionStorage;

      const savedToken = storage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
      const savedUser = storage.getItem(USER_KEY) || localStorage.getItem(USER_KEY);
      const savedSafety = localStorage.getItem(SAFETY_KEY);

      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }

      if (savedSafety) {
        const parsedSafety: SafetyProfileData = JSON.parse(savedSafety);
        setSafetyProfile(parsedSafety);
        if (parsedSafety.preferredLanguage) {
          setLanguage(parsedSafety.preferredLanguage);
        }
      }
    } catch (e) {
      console.warn('[Auth] Failed to restore session from storage:', e);
    } finally {
      setIsLoading(false);
    }
  }, [setLanguage]);

  const login = useCallback(
    async (emailOrPhone: string, password: string, rememberMe: boolean = true) => {
      setIsLoading(true);
      try {
        const res: AuthTokenResponse = await authService.login(emailOrPhone, password);
        const userSession: UserSession = {
          id: res.user_id,
          name: res.name,
          email: res.email,
          role: res.role,
        };

        setToken(res.access_token);
        setUser(userSession);

        const storage = rememberMe ? localStorage : sessionStorage;
        storage.setItem(TOKEN_KEY, res.access_token);
        storage.setItem(USER_KEY, JSON.stringify(userSession));
        localStorage.setItem(REMEMBER_KEY, rememberMe ? 'true' : 'false');
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const register = useCallback(
    async (
      name: string,
      emailOrPhone: string,
      password: string,
      profileData?: SafetyProfileData
    ) => {
      setIsLoading(true);
      try {
        const res: AuthTokenResponse = await authService.register(
          name,
          emailOrPhone,
          password,
          profileData?.emergencyContactPhone
        );

        const userSession: UserSession = {
          id: res.user_id,
          name: res.name,
          email: res.email,
          role: res.role,
        };

        setToken(res.access_token);
        setUser(userSession);

        // Store session (default remember on registration)
        localStorage.setItem(TOKEN_KEY, res.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(userSession));
        localStorage.setItem(REMEMBER_KEY, 'true');

        if (profileData) {
          setSafetyProfile(profileData);
          localStorage.setItem(SAFETY_KEY, JSON.stringify(profileData));
          if (profileData.preferredLanguage) {
            setLanguage(profileData.preferredLanguage);
          }
        }
      } finally {
        setIsLoading(false);
      }
    },
    [setLanguage]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
    localStorage.removeItem(REMEMBER_KEY);
  }, []);

  const updateSafetyProfile = useCallback((profileUpdate: Partial<SafetyProfileData>) => {
    setSafetyProfile((prev) => {
      const updated: SafetyProfileData = {
        emergencyContactName: profileUpdate.emergencyContactName ?? prev?.emergencyContactName ?? '',
        emergencyContactPhone: profileUpdate.emergencyContactPhone ?? prev?.emergencyContactPhone ?? '',
        preferredLanguage: profileUpdate.preferredLanguage ?? prev?.preferredLanguage ?? 'te',
        locationGranted: profileUpdate.locationGranted ?? prev?.locationGranted ?? false,
      };
      localStorage.setItem(SAFETY_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        safetyProfile,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        updateSafetyProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
