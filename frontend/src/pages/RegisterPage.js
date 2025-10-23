import React, { useState, useEffect } from 'react';
import { useAuth } from 'contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // --- THE REDIRECT FIX ---
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    // Simple password validation
    if (password.length < 8) {
        toast.error("Password must be at least 8 characters long.");
        return;
    }

    setLoading(true);
    try {
      await register(email, password, fullName);
      toast.success(t('register.success'));
      // The useEffect will handle the redirect to the dashboard.
    } catch (error) {
      const errorCode = error.response?.data?.detail || error.code || 'unknown';
      toast.error(t('register.error', { message: errorCode }));
      console.error("Registration failed:", error);
    } finally {
      setLoading(false);
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
        {t('register.title')}
      </h2>
      <p className="text-center text-light-text-secondary dark:text-dark-text-secondary mb-8">
        {t('register.subtitle')}
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="fullName" className="sr-only">
            {t('register.fullNameLabel')}
          </label>
          <input
            id="fullName" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)}
            placeholder={t('register.fullNameLabel')}
            className="appearance-none block w-full px-4 py-3 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
          />
        </div>
        <div>
          <label htmlFor="email" className="sr-only">
            {t('register.emailLabel')}
          </label>
          <input
            id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)}
            placeholder={t('register.emailLabel')}
            className="appearance-none block w-full px-4 py-3 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
          />
        </div>
        <div>
          <label htmlFor="password" className="sr-only">
            {t('register.passwordLabel')}
          </label>
          <input
            id="password" type="password" autoComplete="new-password" required value={password} onChange={(e) => setPassword(e.target.value)}
            placeholder={t('register.passwordLabel')}
            className="appearance-none block w-full px-4 py-3 border border-gray-300 dark:border-dark-border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
          />
        </div>
        <div>
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-colors"
          >
            {loading ? t('register.loading') : t('register.submitButton')}
          </button>
        </div>
      </form>
      <p className="mt-8 text-center text-sm text-light-text-secondary dark:text-dark-text-secondary">
        {t('register.hasAccount')}{' '}
        <Link to="/login" className="font-medium text-primary hover:text-primary-500 hover:underline">
          {t('register.signIn')}
        </Link>
      </p>
    </motion.div>
  );
};

export default RegisterPage;