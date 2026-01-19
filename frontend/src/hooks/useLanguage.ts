import { useState, useEffect } from 'react';
import { Language } from '@/lib/translations';

/**
 * Custom hook to manage language state with multi-tab synchronization
 * - Loads language from localStorage on mount
 * - Listens for storage changes (cross-tab language sync)
 * - Listens for custom 'languageChanged' events (same-tab updates)
 * - Automatically updates document direction for RTL/LTR
 * @returns Current language state
 */
export const useLanguage = (): Language => {
  const [language, setLanguage] = useState<Language>('en');

  useEffect(() => {
    // Load language from localStorage on component mount
    const savedLanguage = (localStorage.getItem('language') as Language) || 'en';
    setLanguage(savedLanguage);
    updateDocumentDirection(savedLanguage);

    // Handle storage changes from other tabs
    const handleStorageChange = () => {
      const newLanguage = (localStorage.getItem('language') as Language) || 'en';
      setLanguage(newLanguage);
      updateDocumentDirection(newLanguage);
    };

    // Handle custom language change events (same tab)
    const handleLanguageChanged = (event: Event) => {
      const customEvent = event as CustomEvent<{ language: Language }>;
      const newLanguage = customEvent.detail.language;
      setLanguage(newLanguage);
      updateDocumentDirection(newLanguage);
    };

    // Setup event listeners
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('languageChanged', handleLanguageChanged);

    // Cleanup event listeners
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('languageChanged', handleLanguageChanged);
    };
  }, []);

  return language;
};

/**
 * Update document direction based on language
 * @param language - Language code ('en' or 'ar')
 */
const updateDocumentDirection = (language: Language): void => {
  document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
};
