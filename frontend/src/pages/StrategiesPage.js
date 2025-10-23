import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import api from 'services/api';
import toast from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';
import Joyride, { STATUS } from 'react-joyride';

import { PlusIcon, SquaresPlusIcon } from '@heroicons/react/24/solid';
import Skeleton from 'components/core/Skeleton';
import StrategyCard from 'components/strategies/StrategyCard';
import StrategyModal from 'components/strategies/StrategyModal';
import ConfirmDeleteModal from 'components/strategies/ConfirmDeleteModal';

const StrategiesPage = () => {
  const { t } = useTranslation();
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [currentStrategy, setCurrentStrategy] = useState(null); // Used for editing
  const [strategyToDelete, setStrategyToDelete] = useState(null);
  const [runTour, setRunTour] = useState(false);

  // Fetches all strategies for the current user from the backend
  const fetchStrategies = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/strategies');
      setStrategies(data);
      // Automatically start the onboarding tour if the user has no strategies
      if (data.length === 0 && !localStorage.getItem('strategy_tour_completed')) {
        setTimeout(() => setRunTour(true), 1000); // Delay tour to allow page to render
      }
    } catch (error) {
      toast.error('Failed to fetch your strategies. Please try again.');
      console.error("Fetch strategies error:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch on component mount
  useEffect(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  // --- Modal State Handlers ---
  const handleOpenModal = (strategy = null) => {
    setCurrentStrategy(strategy);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setCurrentStrategy(null);
  };

  const handleOpenDeleteModal = (strategy) => {
    setStrategyToDelete(strategy);
    setIsDeleteModalOpen(true);
  };

  const handleCloseDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setStrategyToDelete(null);
  };

  // --- API ACTION HANDLERS (DEFINITIVE FIXES) ---

  /**
   * Handles the creation or updating of a strategy.
   * Uses toast.promise for robust UI feedback.
   */
  const handleFormSubmit = async (payload) => {
    const isUpdating = !!currentStrategy;

    const apiCall = isUpdating
      ? api.put(`/strategies/${currentStrategy.id}`, payload)
      : api.post('/strategies', payload);

    toast.promise(
        apiCall,
        {
            loading: isUpdating ? 'Updating strategy...' : 'Creating strategy...',
            success: (response) => {
                fetchStrategies(); // Refresh the list of strategies
                handleCloseModal(); // Close the modal only on success
                return `Strategy successfully ${isUpdating ? 'updated' : 'created'}!`;
            },
            error: (err) => {
                // This will display the specific error message from the backend
                // (e.g., "MT5 not connected", "Invalid Symbol", "Premium feature").
                // The modal will remain open for the user to correct any issues.
                return err.response?.data?.detail || 'An unknown error occurred.';
            }
        }
    );
  };

  /**
   * Handles toggling a strategy's status between 'active' and 'inactive'.
   */
  const handleToggleStatus = async (strategy, newIsEnabled) => {
    const newStatus = newIsEnabled ? 'active' : 'inactive';
    const originalStatus = strategy.status;

    // Optimistically update the UI for a snappy user experience
    setStrategies(prev => prev.map(s => s.id === strategy.id ? { ...s, status: newStatus } : s));

    try {
      await api.patch(`/strategies/${strategy.id}/status?status=${newStatus}`);
      toast.success(`Strategy is now ${newStatus}.`);
    } catch (error) {
      // If the API call fails, revert the optimistic UI update
      setStrategies(prev => prev.map(s => s.id === strategy.id ? { ...s, status: originalStatus } : s));
      toast.error(error.response?.data?.detail || `Failed to set status to ${newStatus}.`);
    }
  };

  /**
   * Handles the permanent deletion of a strategy.
   */
  const handleDeleteConfirm = async () => {
    if (!strategyToDelete) return;

    toast.promise(
        api.delete(`/strategies/${strategyToDelete.id}`),
        {
            loading: 'Deleting strategy...',
            success: () => {
                // On success, filter out the deleted strategy from the local state
                setStrategies(prev => prev.filter(s => s.id !== strategyToDelete.id));
                handleCloseDeleteModal();
                return 'Strategy deleted successfully.';
            },
            error: (err) => {
                return err.response?.data?.detail || 'Failed to delete strategy.';
            }
        }
    );
  };

  // --- Onboarding Tour Configuration ---
  const tourSteps = [
    { target: '#add-strategy-btn', content: t('tour.strategies.step1'), disableBeacon: true },
    { target: '#strategy-modal-form', content: t('tour.strategies.step2') },
    { target: '#strategy-card-toggle', content: t('tour.strategies.step3') }
  ];

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
      localStorage.setItem('strategy_tour_completed', 'true');
    }
  };

  // --- Dynamic Content Rendering ---
  const renderContent = () => {
    if (loading) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-72" />)}
        </div>
      );
    }
    if (strategies.length === 0) {
      return (
        <div className="text-center py-20 glass-card">
          <SquaresPlusIcon className="mx-auto h-16 w-16 text-primary/70" />
          <h3 className="mt-4 text-xl font-semibold text-light-text dark:text-dark-text">{t('strategies.placeholder')}</h3>
          <p className="mt-2 text-light-text-secondary dark:text-dark-text-secondary">Click the button below to configure your first automated strategy.</p>
          <button id="add-strategy-btn" onClick={() => handleOpenModal(null)} className="mt-6 inline-flex items-center px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-all duration-300 transform hover:scale-105">
            <PlusIcon className="h-5 w-5 mr-2" />
            {t('strategies.add')}
          </button>
        </div>
      );
    }
    return (
      <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {strategies.map((strategy, index) => (
            // Add a special ID for the first card's toggle for the tour
            <div id={index === 0 ? 'strategy-card-toggle' : undefined}>
                <StrategyCard
                  key={strategy.id}
                  strategy={strategy}
                  onToggleStatus={handleToggleStatus}
                  onEdit={handleOpenModal}
                  onDelete={handleOpenDeleteModal}
                />
            </div>
          ))}
        </AnimatePresence>
      </motion.div>
    );
  };

  return (
    <div className="animate-fade-in">
      <Joyride
        steps={tourSteps}
        run={runTour}
        continuous
        showProgress
        showSkipButton
        callback={handleJoyrideCallback}
        styles={{ options: { zIndex: 10000 } }}
      />

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-light-text dark:text-dark-text">{t('strategies.title')}</h1>
        <button id="add-strategy-btn" onClick={() => handleOpenModal(null)} className="inline-flex items-center px-4 py-2 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-all duration-300 transform hover:scale-105">
          <PlusIcon className="h-5 w-5 mr-2" />
          {t('strategies.add')}
        </button>
      </div>

      {renderContent()}

      {/* The modal is wrapped in a div for the tour to target */}
      <div id="strategy-modal-form">
        <StrategyModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSubmit={handleFormSubmit}
          strategy={currentStrategy}
        />
      </div>

      <ConfirmDeleteModal
        isOpen={isDeleteModalOpen}
        onClose={handleCloseDeleteModal}
        onConfirm={handleDeleteConfirm}
        strategy={strategyToDelete}
      />
    </div>
  );
};

export default StrategiesPage;