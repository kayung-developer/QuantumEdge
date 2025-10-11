import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';
import { FiCpu, FiSave, FiPlay, FiPause, FiAlertTriangle } from 'react-icons/fi';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
import RegimeStrategyCard from '../components/adaptive/RegimeStrategyCard';
import adaptiveService from '../api/adaptiveService';
import strategyService from '../api/strategyService';
import ToggleSwitch from '../components/common/ToggleSwitch';

const AdaptiveStudioPage = () => {
    const { t } = useTranslation();
    const [portfolio, setPortfolio] = useState(null);
    const [availableStrategies, setAvailableStrategies] = useState([]);
    const [regimeMap, setRegimeMap] = useState({});
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    // Mocking the regimes that our trained model has. In a real system, this
    // could also come from an API endpoint describing the trained model.
    const regimes = [{ id: 0 }, { id: 1 }, { id: 2 }, { id: 3 }];

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [strategiesRes, portfolioRes] = await Promise.all([
                strategyService.getAvailableStrategies(),
                adaptiveService.getPortfolio() // Fetches all for the user
            ]);
            setAvailableStrategies(strategiesRes.data);

            // For now, find the first portfolio (assuming one per user)
            const userPortfolio = portfolioRes.data.length > 0 ? portfolioRes.data[0] : null;
            setPortfolio(userPortfolio);
            if (userPortfolio) {
                setRegimeMap(userPortfolio.regime_strategy_map || {});
            }

        } catch (error) {
            toast.error("Failed to load studio data.");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleStrategyChange = (regimeId, strategyId) => {
        setRegimeMap(prev => ({ ...prev, [regimeId]: strategyId }));
    };

    const handleSaveChanges = async () => {
        setIsSaving(true);
        try {
            if (portfolio) {
                // Update existing portfolio
                const updated = await adaptiveService.updatePortfolio(portfolio.id, {
                    regime_strategy_map: regimeMap
                });
                setPortfolio(updated.data);
                toast.success("Portfolio saved successfully!");
            } else {
                // Create new portfolio
                const newPortfolio = await adaptiveService.createPortfolio({
                    name: "Default Adaptive Portfolio",
                    symbol: "BTCUSDT",
                    regime_strategy_map: regimeMap,
                });
                setPortfolio(newPortfolio.data);
                toast.success("Portfolio created successfully!");
            }
        } catch (error) {
            toast.error("Failed to save portfolio.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleToggleActivation = async () => {
        if (!portfolio) {
            toast.error("You must save the portfolio before activating it.");
            return;
        }
        setIsSaving(true);
        try {
            const updated = await adaptiveService.togglePortfolioActivation(portfolio.id);
            setPortfolio(updated.data);
            toast.success(`Portfolio ${updated.data.is_active ? 'activated' : 'deactivated'} successfully!`);
        } catch (error) {
            toast.error("Failed to change portfolio status.");
        } finally {
            setIsSaving(false);
        }
    };

    if (loading) {
        return <ChartSpinner text="Loading Adaptive Studio..." />;
    }

    return (
        <div className="p-4 md:p-6 animate-fadeIn">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary flex items-center">
                        <FiCpu className="mr-3 text-brand-primary"/>
                        Adaptive Deployment Studio
                    </h1>
                    <p className="text-text-secondary mt-2 max-w-2xl">
                        Visually map your best strategies to different market regimes. When activated, the platform will automatically switch strategies for you as market conditions change.
                    </p>
                </div>
                {portfolio && (
                    <div className="flex-shrink-0">
                         <ToggleSwitch
                            enabled={portfolio.is_active}
                            onChange={handleToggleActivation}
                            leftLabel="Inactive"
                            rightLabel="Active"
                        />
                    </div>
                )}
            </div>

            <div className="mt-6 bg-dark-surface p-6 rounded-lg border border-dark-secondary">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-xl font-bold">BTCUSDT Regime Mapping</h2>
                        <p className="text-sm text-text-secondary">Assign a strategy to each market regime. The AI will handle the switching.</p>
                    </div>
                    <Button onClick={handleSaveChanges} isLoading={isSaving} disabled={isSaving}>
                        <FiSave className="mr-2"/>
                        Save Changes
                    </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {regimes.map(regime => (
                        <RegimeStrategyCard
                            key={regime.id}
                            regime={regime}
                            allStrategies={availableStrategies}
                            selectedStrategy={regimeMap[regime.id]}
                            onStrategyChange={handleStrategyChange}
                        />
                    ))}
                </div>
            </div>

            <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-700 rounded-lg text-yellow-300 text-sm">
                <div className="flex items-start">
                    <FiAlertTriangle className="h-5 w-5 mr-3 flex-shrink-0"/>
                    <div>
                        <h4 className="font-bold">Live Trading Zone</h4>
                        <p>Activating an adaptive portfolio will enable fully automated, live trading on your connected account according to the rules you define above. The system will manage positions based on regime changes. Please monitor your account and understand the risks involved.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdaptiveStudioPage;