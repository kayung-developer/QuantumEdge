import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import useAuth from '../hooks/useAuth';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import { FiMail, FiLock } from 'react-icons/fi';

const LoginPage = () => {
  const { t } = useTranslation();
  const { login, isAuthenticated } = useAuth();

  const loginSchema = z.object({
    email: z.string().email(t('validation.invalidEmail')).min(1, t('validation.emailRequired')),
    password: z.string().min(6, t('validation.passwordMinLength')).min(1, t('validation.passwordRequired')),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    try {
      await login(data.email, data.password);
    } catch (error) {
      console.error("Login page caught error:", error);
    }
  };

  if (isAuthenticated) return <Navigate to="/" />;

  return (
    <div className="flex items-center justify-center min-h-screen bg-dark-background p-4">
      <div className="w-full max-w-md mx-auto">
        <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-primary">{t('login.title')}</h1>
            <p className="text-text-secondary mt-2">{t('login.subtitle')}</p>
        </div>

        <div className="bg-dark-surface p-8 rounded-lg shadow-xl border border-dark-secondary">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Input
              id="email"
              label={t('login.emailLabel')}
              type="email"
              icon={FiMail}
              error={errors.email}
              {...register('email')}
              placeholder="you@example.com"
            />
            <Input
              id="password"
              label={t('login.passwordLabel')}
              type="password"
              icon={FiLock}
              error={errors.password}
              {...register('password')}
              placeholder="••••••••"
            />

            <div className="flex items-center justify-between">
                <div className="text-sm">
                    <a href="#" className="font-medium text-brand-primary hover:text-blue-400">
                        {t('login.forgotPassword')}
                    </a>
                </div>
            </div>

            <Button type="submit" variant="primary" className="w-full" isLoading={isSubmitting}>
              {t('login.signIn')}
            </Button>
          </form>

            <p className="mt-6 text-center text-sm text-text-secondary">
                {t('login.noAccount')}{' '}
                <Link to="/register" className="font-medium text-brand-primary hover:text-blue-400">
                    {t('login.signUp')}
                </Link>
            </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;