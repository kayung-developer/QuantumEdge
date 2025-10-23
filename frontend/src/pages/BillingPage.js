import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from 'contexts/AuthContext';
import PricingCard from 'components/billing/PricingCard';
import { PaymentModal } from 'components/billing/PaymentModal'; // Import the new modal

const BillingPage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = [
    { name: 'Freemium', price: 0, features: ['1 Active Strategy', 'Basic Analytics', 'Community Support'] },
    { name: 'Basic', price: 19, features: ['5 Active Strategies', 'Advanced Analytics', 'Email Support'], recommended: false },
    { name: 'Premium', price: 49, features: ['15 Active Strategies', 'AI Signal Confirmation', 'Backtesting Engine', 'Priority Support'], recommended: true },
    { name: 'Ultimate', price: 99, features: ['30 Active Strategies', 'All Premium Features', 'API Access', 'Dedicated Support'], recommended: false },
  ];

  const currentPlanName = user?.subscription?.plan || 'freemium';

  const handleChoosePlan = (plan) => {
    setSelectedPlan(plan);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedPlan(null);
  };

  return (
    <>
      <div className="animate-fade-in">
        <h1 className="text-3xl font-bold text-light-text dark:text-dark-text mb-2">{t('billing.title')}</h1>
        <p className="text-gray-500 dark:text-dark-text-secondary mb-8">{t('billing.subtitle')}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map(plan => (
            <PricingCard
              key={plan.name}
              plan={plan}
              isCurrent={plan.name.toLowerCase() === currentPlanName}
              recommended={plan.recommended}
              onChoosePlan={handleChoosePlan} // Pass the handler
            />
          ))}
        </div>
      </div>

      {/* Render the modal, controlled by this page's state */}
      <PaymentModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        plan={selectedPlan}
      />
    </>
  );
};

export default BillingPage;