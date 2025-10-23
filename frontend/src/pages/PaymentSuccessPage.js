import React, { useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const PaymentSuccessPage = () => {
    const { t } = useTranslation();
    const [searchParams] = useSearchParams();

    useEffect(() => {
        // Here you could make an API call to your backend to verify the transaction
        // using the token or paymentId from the URL query parameters.
        // For example: api.post('/payments/verify/paypal', { orderID: searchParams.get('token') });
        toast.success(t('payment.success.toast'));
    }, [searchParams, t]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-dark-bg">
            <motion.div
                className="text-center p-10 bg-white dark:bg-dark-card rounded-xl shadow-2xl"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, type: 'spring' }}
            >
                <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-green-100">
                    <svg className="h-16 w-16 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mt-6">{t('payment.success.title')}</h1>
                <p className="mt-4 text-gray-500 dark:text-dark-text-secondary">
                    {t('payment.success.subtitle')}
                </p>
                <Link
                    to="/dashboard"
                    className="mt-8 inline-block px-8 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-colors"
                >
                    {t('payment.success.button')}
                </Link>
            </motion.div>
        </div>
    );
};

export default PaymentSuccessPage;