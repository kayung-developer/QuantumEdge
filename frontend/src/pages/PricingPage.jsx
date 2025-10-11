import React, { useState, useEffect } from 'react';
import paymentService from '../api/paymentService';
import PlanCard from '../components/pricing/PlanCard';
import ChartSpinner from '../components/common/ChartSpinner';
import ToggleSwitch from '../components/common/ToggleSwitch';

const PricingPage = () => {
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [billingInterval, setBillingInterval] = useState('monthly'); // 'monthly' or 'yearly'

    useEffect(() => {
        const fetchPlans = async () => {
            try {
                setLoading(true);
                const response = await paymentService.getPublicPlans();
                setPlans(response.data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch plans:", err);
                setError("Could not load pricing plans. Please try again later.");
            } finally {
                setLoading(false);
            }
        };
        fetchPlans();
    }, []);

    if (loading) return <div className="relative h-64"><ChartSpinner text="Loading plans..." /></div>;
    if (error) return <div className="text-center text-danger p-4 bg-danger/10 rounded-md">{error}</div>;

    return (
        <div className="animate-fadeIn p-4 md:p-8">
            <div className="text-center max-w-3xl mx-auto">
                <h1 className="text-4xl md:text-5xl font-extrabold text-text-primary">
                    Find the Perfect Plan for Your Trading Strategy
                </h1>
                <p className="mt-4 text-lg text-text-secondary">
                    Unlock advanced AI capabilities, multi-exchange connectivity, and robust risk management tools. Choose the plan that fits your needs.
                </p>
            </div>

            <div className="my-10 flex justify-center items-center space-x-4">
                <ToggleSwitch
                    enabled={billingInterval === 'yearly'}
                    onChange={() => setBillingInterval(prev => prev === 'monthly' ? 'yearly' : 'monthly')}
                    leftLabel="Monthly"
                    rightLabel="Yearly"
                />
                <span className="px-3 py-1 text-sm font-semibold text-green-300 bg-success/20 rounded-full">Save 20%</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto mt-8">
                {plans.map((plan) => (
                    <PlanCard key={plan.id} plan={plan} interval={billingInterval} />
                ))}
            </div>
        </div>
    );
};

export default PricingPage;