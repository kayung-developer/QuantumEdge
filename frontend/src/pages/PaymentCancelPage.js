import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

const PaymentCancelPage = () => {
    const { t } = useTranslation();

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-dark-bg">
            <motion.div
                className="text-center p-10 bg-white dark:bg-dark-card rounded-xl shadow-2xl"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-yellow-100">
                     <svg className="h-12 w-12 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mt-6">{t('payment.cancel.title')}</h1>
                <p className="mt-4 text-gray-500 dark:text-dark-text-secondary">
                    {t('payment.cancel.subtitle')}
                </p>
                <Link
                    to="/billing"
                    className="mt-8 inline-block px-8 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-colors"
                >
                    {t('payment.cancel.button')}
                </Link>
            </motion.div>
        </div>
    );
};

export default PaymentCancelPage;