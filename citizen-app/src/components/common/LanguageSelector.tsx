import React from 'react';
import { useLanguage, SupportedLanguage, LANGUAGE_NAMES } from '../../context/LanguageContext';
import { Globe } from 'lucide-react';

interface LanguageSelectorProps {
  className?: string;
  variant?: 'compact' | 'full';
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className = '',
  variant = 'compact',
}) => {
  const { language, setLanguage } = useLanguage();

  const options: SupportedLanguage[] = ['te', 'en', 'hi'];

  return (
    <div
      className={`inline-flex items-center gap-1 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-1 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm ${className}`}
      role="group"
      aria-label="Select Language"
    >
      <Globe className="w-3.5 h-3.5 text-slate-400 ml-1 mr-0.5 hidden sm:inline" />
      {options.map((code) => {
        const isSelected = language === code;
        return (
          <button
            key={code}
            type="button"
            onClick={() => setLanguage(code)}
            className={`px-2.5 py-1 text-xs font-medium rounded-xl transition-all duration-200 ${
              isSelected
                ? 'bg-red-600 text-white shadow-sm font-semibold scale-105'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
            }`}
          >
            {variant === 'full'
              ? `${LANGUAGE_NAMES[code].native} (${LANGUAGE_NAMES[code].label})`
              : LANGUAGE_NAMES[code].native}
          </button>
        );
      })}
    </div>
  );
};
