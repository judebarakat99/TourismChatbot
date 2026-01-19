import { useState, useEffect } from 'react';
import { Language } from '@/lib/translations';

/**
 * Custom hook to manage language state with multi-tab synchronization
 * 
 * This hook centralizes all language management logic that was previously
 * duplicated across multiple page components. It provides:
 * - Automatic language loading from localStorage on component mount
 * - Multi-tab synchronization via storage events (when user changes language in another tab)
 * - Same-tab language updates via custom 'languageChanged' events
 * - Automatic RTL/LTR document direction updates based on selected language
 * 
 * Benefits:
 * - Eliminates code duplication across Home, Settings, Account, and Help pages
 * - Ensures consistent language behavior throughout the application
 * - Simplifies page components to single-line language declarations
 * - Maintains proper event listener cleanup to prevent memory leaks
 * 
 * @returns {Language} Current language code ('en' for English, 'ar' for Arabic)
 * 
 * @example
 * const language = useLanguage();
 * return <div>{t('key', language)}</div>;
 */
export const useLanguage = (): Language => {
  const [language, setLanguage] = useState<Language>('en');

  useEffect(() => {
    // 1. Load previously saved language from localStorage on initial mount
    const savedLanguage = (localStorage.getItem('language') as Language) || 'en';
    setLanguage(savedLanguage);
    updateDocumentDirection(savedLanguage);

    // 2. Handle storage events: triggered when language changes in another browser tab
    // This ensures all open tabs stay synchronized when user changes language
    const handleStorageChange = () => {
      const newLanguage = (localStorage.getItem('language') as Language) || 'en';
      setLanguage(newLanguage);
      updateDocumentDirection(newLanguage);
    };

    // 3. Handle custom 'languageChanged' events: triggered when language changes on same tab
    // This event is dispatched from Settings page after user selects a new language
    const handleLanguageChanged = (event: Event) => {
      const customEvent = event as CustomEvent<{ language: Language }>;
      const newLanguage = customEvent.detail.language;
      setLanguage(newLanguage);
      updateDocumentDirection(newLanguage);
    };

    // Setup event listeners for both synchronization methods
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('languageChanged', handleLanguageChanged);

    // Cleanup: Remove event listeners when component unmounts to prevent memory leaks
    // This is critical for single-page applications where pages are not fully unloaded
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('languageChanged', handleLanguageChanged);
    };
  }, []); // Empty dependency array: this effect runs only once on component mount

  return language;
};

/**
 * Update HTML document direction for RTL (Right-to-Left) language support
 * 
 * The 'dir' attribute on the html element controls text direction and is
 * essential for proper rendering of Arabic text and RTL-aware UI layouts.
 * 
 * @param {Language} language - Language code to determine direction
 *        - 'ar' (Arabic): Sets direction to 'rtl' (right-to-left)
 *        - 'en' (English): Sets direction to 'ltr' (left-to-right)
 */
const updateDocumentDirection = (language: Language): void => {
  document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
};
