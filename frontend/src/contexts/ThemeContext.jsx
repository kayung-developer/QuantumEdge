import React, { createContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext(null);
const THEME_STORAGE_KEY = 'auraquant-theme';

/**
 * The ThemeProvider component manages the application's visual theme (light/dark).
 * It persists the user's choice in localStorage and applies the correct
 * class to the root HTML element to activate Tailwind CSS's dark mode.
 */
export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState('dark'); // Default to dark theme

  // Effect to apply the theme class to the <html> element on load and when theme changes.
  useEffect(() => {
    const root = window.document.documentElement;
    const isDark = theme === 'dark';

    root.classList.remove(isDark ? 'light' : 'dark');
    root.classList.add(theme);
  }, [theme]);

  // Effect to initialize the theme from localStorage or system preference on first load.
  useEffect(() => {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);

    // Check if the stored theme is one of our valid options.
    if (storedTheme && ['light', 'dark'].includes(storedTheme)) {
      setThemeState(storedTheme);
    } else {
      // If no valid theme is stored, fall back to the user's system preference.
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setThemeState(prefersDark ? 'dark' : 'light');
    }
  }, []);

  /**
   * Sets a new theme and persists it to localStorage.
   * @param {string} newTheme - The new theme to set ('light' or 'dark').
   */
  const setTheme = useCallback((newTheme) => {
    if (!['light', 'dark'].includes(newTheme)) {
      console.error(`Invalid theme value: ${newTheme}`);
      return;
    }

    window.localStorage.setItem(THEME_STORAGE_KEY, newTheme);
    setThemeState(newTheme);
  }, []);

  const contextValue = {
    theme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;