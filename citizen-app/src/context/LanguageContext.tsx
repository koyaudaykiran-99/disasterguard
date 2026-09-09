import React, { createContext, useContext, useState, useEffect } from 'react';

export type SupportedLanguage = 'te' | 'en' | 'hi';

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  languageNames: Record<SupportedLanguage, { native: string; label: string }>;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = 'disasterguard_language_pref';

export const LANGUAGE_NAMES: Record<SupportedLanguage, { native: string; label: string }> = {
  te: { native: 'తెలుగు', label: 'Telugu' },
  en: { native: 'English', label: 'English' },
  hi: { native: 'हिन्दी', label: 'Hindi' },
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'te' || saved === 'en' || saved === 'hi') {
        return saved;
      }
    } catch (e) {
      console.warn('[LanguageProvider] Read failed:', e);
    }
    return 'te'; // Default to Telugu as primary emergency language
  });

  const setLanguage = (lang: SupportedLanguage) => {
    setLanguageState(lang);
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      console.warn('[LanguageProvider] Save failed:', e);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, languageNames: LANGUAGE_NAMES }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};