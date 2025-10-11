import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import useAuth from '../hooks/useAuth.js';
import Input from '../components/common/Input.jsx';
import Button from '../components/common/Button.jsx';
import { FiUser, FiMail, FiLock } from 'react-icons/fi';
import axiosClient from '../api/axiosClient.js'; // We can use axiosClient directly for this one-off call

// Define the validation schema using Zod, including password confirmation
const registerSchema = z.object({
  full_name: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email('Invalid email address').min(1, 'Email is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine(data => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"], // Point the error to the confirmation field
});

const RegisterPage = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data) => {
    const toastId = toast.loading("Creating your account...");
    try {
      // We don't need a dedicated service for this single call.
      // We send only the fields the backend 'UserCreate' schema expects.
      await axiosClient.post('/users/', {
        full_name: data.full_name,
        email: data.email,
        password: data.password,
      });

      toast.success("Account created successfully! Please log in.", { id: toastId });
      // Redirect the user to the login page after successful registration
      navigate('/login');

    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.', { id: toastId });
      console.error("Registration failed:", error);
    }
  };

  // If the user is already authenticated, redirect them away from the register page
  if (isAuthenticated) {
    return <Navigate to="/dashboard" />;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-dark-background p-4">
      <div className="w-full max-w-md mx-auto">
        <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-primary">Create Your AuraQuant Account</h1>
            <p className="text-text-secondary mt-2">Start your journey into intelligent trading.</p>
        </div>

        <div className="bg-dark-surface p-8 rounded-lg shadow-xl border border-dark-secondary">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
             <Input
              id="full_name"
              label="Full Name"
              type="text"
              icon={FiUser}
              error={errors.full_name}
              {...register('full_name')}
              placeholder="John Doe"
            />
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
            <Input
              id="confirm_password"
              label="Confirm Password"
              type="password"
              icon={FiLock}
              error={errors.confirm_password}
              {...register('confirm_password')}
              placeholder="••••••••"
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isSubmitting}
            >
              Create Account
            </Button>
          </form>

            <p className="mt-6 text-center text-sm text-text-secondary">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-brand-primary hover:text-blue-400">
                    Sign In
                </Link>
            </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;