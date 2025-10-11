import { useContext } from 'react';
import ThemeContext from '../contexts/ThemeContext.jsx';

/**
 * A custom hook that provides a convenient shortcut to access the ThemeContext.
 * It ensures that the hook is used within a component tree that is wrapped
 * by a ThemeProvider.
 *
 * @returns {object} The theme context value:
 *   - theme: string ('light' or 'dark')
 *   - setTheme: function
 *
 * @example
 * const { theme, setTheme } = useTheme();
 */
const useTheme = () => {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider component tree.');
  }

  return context;
};

export default useTheme;