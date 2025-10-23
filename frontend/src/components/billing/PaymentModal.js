import React, { useState, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { useTranslation } from 'react-i18next';
import api from 'services/api';
import toast from 'react-hot-toast';

// Simple SVG Icons for Payment Methods
const PayPalIcon = () => <svg viewBox="0 0 24 24" className="w-8 h-8"><path fill="#003087" d="M22.59 6.84a.45.45 0 00-.44-.35h-3.32c-1.38 0-2.05.62-2.31 1.77-.14.65-.21 1.4-.23 1.83-.02.43.14 1.14.86 1.14h1.3c2.4 0 4.2-1.74 4.43-3.39z"/><path fill="#009cde" d="M22.75 6.49h-3.76c-1.38 0-2.05.62-2.31 1.77-.14.65-.21 1.4-.23 1.83-.02.43.14 1.14.86 1.14h.54c1.11 0 2.05-.62 2.31-1.77.14-.65.21-1.4.23-1.83.02-.43-.14-1.14-.86-1.14h-.35a.45.45 0 00-.42.56z"/><path fill="#012169" d="M21.24 3.76H7.23c-.3 0-.58.15-.75.4l-4.2 8.44a.8.8 0 00-.04.81.83.83 0 00.79.55h4.28c1.38 0 2.05-.62 2.31-1.77.14-.65.21-1.4.23-1.83.02-.43-.14-1.14-.86-1.14H8.08l1.68-3.37h4.94c2.4 0 4.2 1.74 4.43 3.39a.45.45 0 00.44.35h3.32a.45.45 0 00.44-.35l1.68-3.38c.13-.26 0-.57-.3-.57z"/></svg>;
const PaystackIcon = () => <svg viewBox="0 0 100 100" className="w-8 h-8 rounded-md"><path fill="#09A6A3" d="M0 0h100v100H0z"/><path fill="#fff" d="M30.6 69.4V30.5h10v28.8c0 5.4 3.9 10.1 10 10.1s10-4.7 10-10.1V30.5h10v38.9H60.6V59.3c0-5.4-3.9-10.1-10-10.1s-10 4.7-10 10.1v10.1H30.6z"/></svg>;
const CryptoIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-yellow-500"><path d="M12 24c6.627 0 12-5.373 12-12S18.627 0 12 0 0 5.373 0 12s5.373 12 12 12z"/><path d="M16.6 8.5l-4.6 4.6-4.6-4.6"/><path d="M16.6 15.5l-4.6-4.6-4.6 4.6"/></svg>;
const CardIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-blue-500"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>;


export const PaymentModal = ({ isOpen, onClose, plan }) => {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(false);
    const [cryptoInfo, setCryptoInfo] = useState(null);

    const handlePayment = async (provider) => {
        setLoading(true);
        const toastId = toast.loading(t('payment.initiating'));

        try {
            if (provider === 'paypal') {
                const { data } = await api.post('/payments/initiate/paypal', { plan: plan.name.toLowerCase() });
                if (data && data.approve_url) {
                    window.location.href = data.approve_url; // Redirect to PayPal
                } else { throw new Error("Missing PayPal approval URL."); }
            } else if (provider === 'paystack') {
                const { data } = await api.post('/payments/initiate/paystack', { plan: plan.name.toLowerCase() });
                if (data && data.authorization_url) {
                    window.location.href = data.authorization_url; // Redirect to Paystack
                } else { throw new Error("Missing Paystack authorization URL."); }
            } else if (provider === 'crypto') {
                const { data } = await api.get('/payments/initiate/crypto');
                setCryptoInfo(data); // Show crypto details instead of redirecting
            }
            toast.dismiss(toastId);
        } catch (error) {
            console.error("Payment initiation failed:", error);
            toast.error(t('payment.error.generic'), { id: toastId });
        } finally {
            if (provider !== 'crypto') { // Don't stop loading if showing crypto info
                setLoading(false);
            }
        }
    };

    const paymentOptions = [
        { name: 'PayPal', provider: 'paypal', Icon: PayPalIcon },
        { name: 'Paystack', provider: 'paystack', Icon: PaystackIcon },
        { name: 'Card', provider: 'paystack', Icon: CardIcon }, // Paystack handles cards
        { name: 'Crypto', provider: 'crypto', Icon: CryptoIcon },
    ];

    // Reset crypto info when modal is closed
    const handleClose = () => {
        setCryptoInfo(null);
        setLoading(false);
        onClose();
    }

    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-30" onClose={handleClose}>
                <Transition.Child as={Fragment} /* ... backdrop ... */>
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
                </Transition.Child>
                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4 text-center">
                        <Transition.Child as={Fragment} /* ... panel transition ... */>
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-dark-card p-6 text-left align-middle shadow-xl transition-all">
                                <Dialog.Title as="h3" className="text-xl font-bold leading-6 text-gray-900 dark:text-white">
                                    {cryptoInfo ? "Pay with Crypto" : `Checkout: ${plan?.name} Plan`}
                                </Dialog.Title>

                                {cryptoInfo ? (
                                    <div className="mt-4 space-y-4 text-sm">
                                        <p className="text-gray-500">To complete your payment, send the required amount to the address below. You MUST include the memo.</p>
                                        <div>
                                            <label className="font-semibold">Network:</label>
                                            <p className="font-mono p-2 bg-gray-100 dark:bg-dark-bg rounded">{cryptoInfo.network}</p>
                                        </div>
                                        <div>
                                            <label className="font-semibold">Address:</label>
                                            <p className="font-mono p-2 bg-gray-100 dark:bg-dark-bg rounded break-words">{cryptoInfo.wallet_address}</p>
                                        </div>
                                        <div>
                                            <label className="font-semibold text-danger">Memo/Destination Tag (Required):</label>
                                            <p className="font-mono p-2 bg-gray-100 dark:bg-dark-bg rounded">{cryptoInfo.memo}</p>
                                        </div>
                                        <p className="text-xs text-yellow-600">After sending, please allow time for manual confirmation by an administrator. Your plan will be upgraded upon verification.</p>
                                    </div>
                                ) : (
                                    <div className="mt-4">
                                        <p className="text-sm text-gray-500 dark:text-dark-text-secondary">Please select your preferred payment method.</p>
                                        <div className="mt-6 space-y-3">
                                            {paymentOptions.map(({ name, provider, Icon }) => (
                                                <button
                                                    key={name}
                                                    onClick={() => handlePayment(provider)}
                                                    disabled={loading}
                                                    className="w-full flex items-center p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-border/20 dark:border-dark-border disabled:opacity-50 transition-colors"
                                                >
                                                    <Icon />
                                                    <span className="ml-4 font-semibold">{name}</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                <div className="mt-6">
                                    <button type="button" onClick={handleClose} className="w-full px-4 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600">
                                        {cryptoInfo ? "Done" : "Cancel"}
                                    </button>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};