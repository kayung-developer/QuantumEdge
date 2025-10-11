import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import paymentService from '../api/paymentService';
import { FiCheckCircle, FiXCircle, FiLoader } from 'react-icons/fi';
import Button from '../components/common/Button';
import useAuth from '../hooks/useAuth';

const PaymentStatusPage = () => {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
    const [message, setMessage] = useState('');
    const { initializeAuth } = useAuth(); // We need to re-fetch user data to update subscription status

    useEffect(() => {
        const verify = async () => {
            const provider = searchParams.get('provider');
            // Paystack uses 'reference', PayPal uses 'token' (which is the order ID).
            const reference = searchParams.get('reference') || searchParams.get('token');

            if (!provider || !reference) {
                setStatus('error');
                setMessage('Invalid payment URL. Missing provider or reference ID.');
                return;
            }

            try {
                const response = await paymentService.verifyPayment(provider, reference);
                setStatus('success');
                setMessage(response.data.message || 'Payment successful and subscription activated!');
                // Re-initialize auth context to fetch updated user data (including new subscription)
                await initializeAuth();
            } catch (err) {
                setStatus('error');
                setMessage(err.response?.data?.detail || 'An error occurred while verifying your payment. Please contact support.');
                console.error('Payment verification failed:', err);
            }
        };

        verify();
    }, [searchParams, initializeAuth]);

    const StatusDisplay = () => {
        switch (status) {
            case 'success':
                return (
                    <>
                        <FiCheckCircle className="h-16 w-16 text-success mx-auto" />
                        <h1 className="mt-4 text-3xl font-bold text-text-primary">Payment Successful!</h1>
                        <p className="mt-2 text-text-secondary">{message}</p>
                        <Link to="/dashboard" className="mt-8">
                            <Button>Go to Dashboard</Button>
                        </Link>
                    </>
                );
            case 'error':
                return (
                    <>
                        <FiXCircle className="h-16 w-16 text-danger mx-auto" />
                        <h1 className="mt-4 text-3xl font-bold text-text-primary">Payment Failed</h1>
                        <p className="mt-2 text-text-secondary">{message}</p>
                        <Link to="/pricing" className="mt-8">
                            <Button variant="secondary">Try Again</Button>
                        </Link>
                    </>
                );
            default: // 'loading'
                return (
                    <>
                        <FiLoader className="h-16 w-16 text-brand-primary mx-auto animate-spin" />
                        <h1 className="mt-4 text-3xl font-bold text-text-primary">Verifying Payment...</h1>
                        <p className="mt-2 text-text-secondary">Please wait, we are confirming your transaction.</p>
                    </>
                );
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-dark-background">
            <div className="text-center p-8 bg-dark-surface rounded-lg shadow-xl max-w-lg mx-auto">
                <StatusDisplay />
            </div>
        </div>
    );
};

export default PaymentStatusPage;