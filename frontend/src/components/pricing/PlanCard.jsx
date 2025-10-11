import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiCheck } from 'react-icons/fi';
import toast from 'react-hot-toast';
import Button from '../common/Button';
import paymentService from '../../api/paymentService';
import { clsx } from 'clsx';

/**
 * A reusable UI card component to display a single subscription plan.
 * It shows the plan's name, description, price, and features, and handles
 * the logic for initiating a payment process when a user chooses a plan.
 *
 * @param {object} plan - The plan object data fetched from the backend.
 * @param {string} interval - The currently selected billing interval ('monthly' or 'yearly').
 * @param {boolean} isPopular - A flag to highlight the most popular plan.
 */
const PlanCard = ({ plan, interval, isPopular = false }) => {
    const { t } = useTranslation();
    const [isLoadingProvider, setIsLoadingProvider] = useState(null); // 'paystack' | 'paypal' | null

    const price = interval === 'monthly' ? plan.price_monthly : plan.price_yearly;
    const pricePeriod = interval === 'monthly' ? '/ mo' : '/ yr';
    const originalMonthlyPrice = interval === 'yearly' ? (plan.price_yearly / 12).toFixed(2) : null;

    const handleChoosePlan = async (provider) => {
        setIsLoadingProvider(provider);
        const toastId = toast.loading(`Redirecting to ${provider}...`);

        try {
            // The success and cancel URLs are where the payment gateway will redirect
            // the user after the transaction attempt. Our backend provides these to the gateway.
            const success_url = `${window.location.origin}/payment/status?provider=${provider}&session_id={CHECKOUT_SESSION_ID}`;
            const cancel_url = `${window.location.origin}/pricing`;

            const payload = {
                plan_id: plan.id,
                interval: interval,
                provider: provider.toLowerCase(),
                success_url: success_url,
                cancel_url: cancel_url,
            };

            const response = await paymentService.initiatePayment(payload);
            const { authorization_url } = response.data;

            // Redirect the user's browser to the payment gateway's checkout page.
            window.location.href = authorization_url;

        } catch (error) {
            console.error(`Failed to initiate ${provider} payment:`, error);
            toast.error(error.response?.data?.detail || 'Failed to start payment process. Please try again.', { id: toastId });
            setIsLoadingProvider(null);
        }
    };

    return (
        <div className={clsx(
            "bg-dark-surface border rounded-lg p-6 flex flex-col shadow-lg transform hover:-translate-y-2 transition-transform duration-300 relative",
            isPopular ? "border-brand-primary/80" : "border-dark-secondary"
        )}>
            {isPopular && (
                <div className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2 bg-brand-primary text-white text-xs font-bold px-3 py-1 rounded-full uppercase">
                    Most Popular
                </div>
            )}

            <h3 className="text-xl font-bold text-brand-primary">{plan.name}</h3>
            <p className="text-text-secondary mt-2 flex-grow min-h-[40px]">{plan.description}</p>

            <div className="my-6">
                <span className="text-4xl font-extrabold text-text-primary">${price}</span>
                <span className="text-text-secondary">{pricePeriod}</span>
                {originalMonthlyPrice && (
                     <p className="text-sm text-text-secondary mt-1">(${originalMonthlyPrice}/mo billed annually)</p>
                )}
            </div>

            <ul className="space-y-3 mb-8">
                {plan.features && Object.entries(plan.features).map(([key, value]) => (
                    <li key={key} className="flex items-center text-sm">
                        <FiCheck className="h-5 w-5 text-success mr-2 flex-shrink-0" />
                        <span className="text-text-secondary">{value}</span>
                    </li>
                ))}
            </ul>

            <div className="mt-auto space-y-3">
                 <Button
                    variant="primary"
                    className="w-full"
                    isLoading={isLoadingProvider === 'paystack'}
                    disabled={!!isLoadingProvider}
                    onClick={() => handleChoosePlan('Paystack')}
                >
                    Choose Plan with Paystack
                </Button>
                 <Button
                    variant="secondary"
                    className="w-full"
                    isLoading={isLoadingProvider === 'paypal'}
                    disabled={!!isLoadingProvider}
                    onClick={() => handleChoosePlan('PayPal')}
                >
                    Choose Plan with PayPal
                </Button>
            </div>
        </div>
    );
};

export default PlanCard;