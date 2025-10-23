import React, { useState, useEffect } from 'react';
import { useAuth } from 'contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

// Google Icon SVG component for the button
const GoogleIcon = (props) => (
    <svg {...props} viewBox="0 0 48 48">
        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"></path>
        <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"></path>
        <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"></path>
        <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.574l6.19,5.238C43.021,36.251,44,34,44,30C44,22.659,43.862,21.35,43.611,20.083z"></path>
    </svg>
);

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const { login, loginWithGoogle, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // --- THE REDIRECT FIX ---
  // This effect checks the global authentication state. If it becomes true
  // at any point while this component is mounted, it will redirect.
  useEffect(() => {
    if (isAuthenticated) {
      // Use replace to prevent the user from going "back" to the login page
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading || googleLoading) return; // Prevent multiple submissions
    setLoading(true);
    try {
      await login(email, password);
      toast.success(t('login.success'));
      // No navigate() call needed here; the useEffect will handle it.
    } catch (error) {
      const errorCode = error.code || 'unknown';
      toast.error(t('login.error', { message: errorCode }));
      console.error("Email/Password login failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (loading || googleLoading) return;
    setGoogleLoading(true);
    try {
        await loginWithGoogle();
        toast.success(t('login.success'));
        // No navigate() call needed here either.
    } catch (error) {
        const errorCode = error.code || 'unknown';
        toast.error(t('login.error', { message: errorCode }));
        console.error("Google login failed:", error);
    } finally {
        setGoogleLoading(false);
    }
  };

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 },
  };

  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold text-center text-light-text dark:text-dark-text mb-2">
        {t('login.title')}
      </h2>
      <p className="text-center text-light-text-secondary dark:text-dark-text-secondary mb-8">
        {t('login.subtitle')}
      </p>

      <div className="space-y-4">
        <button
          type="button"
          onClick={handleGoogleLogin}
          disabled={googleLoading || loading}
          className="w-full flex justify-center items-center gap-3 py-3 px-4 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm text-sm font-medium text-gray-700 dark:text-dark-text bg-white/50 dark:bg-dark-card/50 hover:bg-gray-50 dark:hover:bg-dark-border/20 disabled:opacity-50 transition-colors"
        >
          <GoogleIcon className="h-5 w-5" />
          {googleLoading ? "Signing in..." : "Sign in with Google"}
        </button>

        <div className="my-6 flex items-center">
          <div className="flex-grow border-t border-gray-300 dark:border-dark-border"></div>
          <span className="flex-shrink mx-4 text-xs uppercase text-gray-400">OR</span>
          <div className="flex-grow border-t border-gray-300 dark:border-dark-border"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="sr-only">
              {t('login.emailLabel')}
            </label>
            <input
              id="email" name="email" type="email" autoComplete="email" required
              value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder={t('login.emailLabel')}
              className="appearance-none block w-full px-4 py-3 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
            />
          </div>

          <div>
            <label htmlFor="password" className="sr-only">
              {t('login.passwordLabel')}
            </label>
            <input
              id="password" name="password" type="password" autoComplete="current-password" required
              value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder={t('login.passwordLabel')}
              className="appearance-none block w-full px-4 py-3 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || googleLoading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-colors"
            >
              {loading ? t('login.loading') : t('login.submitButton')}
            </button>
          </div>
        </form>
      </div>

      <p className="mt-8 text-center text-sm text-light-text-secondary dark:text-dark-text-secondary">
        {t('login.noAccount')}{' '}
        <Link to="/register" className="font-medium text-primary hover:text-primary-500 hover:underline">
          {t('login.signUp')}
        </Link>
      </p>
    </motion.div>
  );
};

export default LoginPage;