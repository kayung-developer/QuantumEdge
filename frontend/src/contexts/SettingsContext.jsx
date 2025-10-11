import React, { createContext, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

// Create the context with a default null value.
const SettingsContext = createContext(null);
const LANGUAGE_STORAGE_KEY = 'auraquant-language';

/**
 * The SettingsProvider component manages non-theme, non-auth user preferences.
 * Its primary role is to manage and persist the application's language setting,
 * integrating with the i18next library.
 */
export const SettingsProvider = ({ children }) => {
  const { i18n } = useTranslation();

  // State for the current language, defaulting to English.
  const [language, setLanguageState] = useState(i18n.language || 'en');

  // Effect to initialize the language from localStorage on first load.
  // This runs once when the application starts.
  useEffect(() => {
    const storedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (storedLanguage && i18n.options.resources[storedLanguage]) {
      // If a valid language is stored, set it as the current language.
      i18n.changeLanguage(storedLanguage);
      setLanguageState(storedLanguage);
    } else {
      // Otherwise, use the language detected by i18next-browser-languagedetector.
      setLanguageState(i18n.language);
    }
  }, [i18n]);

  /**
   * Sets a new language, changes it in the i18next instance, and persists
   * the choice to localStorage.
   * @param {string} newLanguageCode - The new language code to set (e.g., 'es', 'fr').
   */
  const setLanguage = useCallback((newLanguageCode) => {
    if (!i18n.options.resources[newLanguageCode]) {
      console.error(`Invalid language code: ${newLanguageCode}`);
      return;
    }

    // Update the i18next instance, which will cause all components to re-render with new translations.
    i18n.changeLanguage(newLanguageCode);
    // Persist the user's choice for future visits.
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguageCode);
    // Update the local state.
    setLanguageState(newLanguageCode);
  }, [i18n]);

  const contextValue = {
    language,
    setLanguage,
  };

  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
};

export default SettingsContext;