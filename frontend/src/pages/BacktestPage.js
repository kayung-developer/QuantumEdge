import React, { useState, useEffect, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import api from 'services/api';
import toast from 'react-hot-toast';
import { STRATEGIES_CONFIG } from 'config/strategies.config';
import { PlayCircleIcon, BeakerIcon } from '@heroicons/react/24/solid';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from 'contexts/WebSocketContext';
import MultiSelect from 'components/core/MultiSelect';

// ==============================================================================
// SUB-COMPONENT: MetricCard
// Displays a single performance metric from the backtest results.
// ==============================================================================
const MetricCard = ({ title, value, unit = '', className = '' }) => {
    const colorClass = () => {
        if (title.toLowerCase().includes('drawdown')) {
            return value > 20 ? 'text-danger' : value > 10 ? 'text-warning' : 'text-light-text dark:text-dark-text';
        }
        if (title.toLowerCase().includes('win rate')) {
            return value > 50 ? 'text-success' : value > 40 ? 'text-warning' : 'text-danger';
        }
        if (title.toLowerCase().includes('sharpe')) {
            return value > 1 ? 'text-success' : value > 0.5 ? 'text-yellow-500' : 'text-warning';
        }
        return 'text-light-text dark:text-dark-text';
    };

    return (
        <div className={`bg-light-bg dark:bg-dark-bg/50 p-4 rounded-lg text-center ${className}`}>
            <p className="text-sm text-light-text-secondary dark:text-dark-text-secondary">{title}</p>
            <p className={`text-2xl font-bold ${colorClass()}`}>
                {value}<span className="text-lg font-medium">{unit}</span>
            </p>
        </div>
    );
};

// ==============================================================================
// SUB-COMPONENT: BacktestResults
// Displays the full report of a completed backtest.
// ==============================================================================
const BacktestResults = ({ results }) => {
    const isProfitable = results.total_return_pct > 0;
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
        >
            <h2 className="text-2xl font-bold text-center text-light-text dark:text-dark-text">Backtest Results</h2>
            <div className={`p-6 rounded-xl text-center shadow-inner ${isProfitable ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                <p className="text-sm font-semibold uppercase tracking-wider">Total Return</p>
                <p className="text-5xl font-extrabold">{results.total_return_pct.toFixed(2)}%</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard title="Sharpe Ratio" value={results.sharpe_ratio ? results.sharpe_ratio.toFixed(2) : 'N/A'} />
                <MetricCard title="Win Rate" value={results.win_rate_pct ? results.win_rate_pct.toFixed(2) : 'N/A'} unit="%" />
                <MetricCard title="Max Drawdown" value={results.max_drawdown_pct ? results.max_drawdown_pct.toFixed(2) : 'N/A'} unit="%" />
                <MetricCard title="Total Trades" value={results.total_trades || 0} />
            </div>
            {/* Optional: Add a section to display the trade log or an equity curve chart */}
        </motion.div>
    );
};

// ==============================================================================
// MAIN COMPONENT: BacktestPage
// The complete, stateful page for configuring and running backtests.
// ==============================================================================
const availableTimeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1'];
const BacktestPage = () => {
    const { t } = useTranslation();
    const { lastMessage } = useWebSocket();
    const [isLoading, setIsLoading] = useState(false);
    const [backtestResult, setBacktestResult] = useState(null);
    const [lastStartedBacktestId, setLastStartedBacktestId] = useState(null);

    const { register, handleSubmit, watch, control, reset } = useForm({
        defaultValues: {
            strategy_name: Object.keys(STRATEGIES_CONFIG)[0],
            symbol: 'EURUSD',
            timeframe: 'H1',
        }
    });

    const selectedStrategyName = watch('strategy_name');
    const selectedStrategyConfig = STRATEGIES_CONFIG[selectedStrategyName];

    // Effect to reset parameters when the selected strategy changes
    useEffect(() => {
        if (selectedStrategyConfig) {
            const defaultParams = selectedStrategyConfig.parameters.reduce((acc, param) => {
                acc[param.name] = param.defaultValue;
                return acc;
            }, {});
            // Keep existing values for symbol/timeframe if they exist, otherwise use defaults
            reset(currentValues => ({
                ...currentValues,
                strategy_name: selectedStrategyName,
                parameters: defaultParams,
            }));
        }
    }, [selectedStrategyName, selectedStrategyConfig, reset]);

    // This function fetches the full results from the API
    const fetchResult = useCallback(async (resultId) => {
        try {
            const { data } = await api.get(`/backtest/${resultId}`);
            setBacktestResult(data);
            setIsLoading(false);
            toast.success('Backtest results loaded!');
        } catch (error) {
            if (error.response?.status === 202) {
                // If the backtest is still running, poll again after a delay.
                toast('Backtest is still running, checking again in 10 seconds...', { id: 'backtest-poll' });
                setTimeout(() => fetchResult(resultId), 10000);
            } else {
                toast.error(error.response?.data?.detail || "Failed to fetch backtest results.");
                setIsLoading(false);
            }
        }
    }, []);

    // This effect listens for the WebSocket notification to trigger the result fetch
    useEffect(() => {
        // This function will only run if lastMessage or lastStartedBacktestId changes.
        if (lastMessage?.type === 'backtest_complete' && lastMessage.data.id === lastStartedBacktestId) {

            toast.dismiss(); // Dismiss any "running" or "polling" toasts

            if (lastMessage.data.status === 'completed') {
                // The WebSocket message is our trigger. Now, fetch the full results.
                const toastId = toast.loading("Backtest finished! Fetching detailed results...");

                // Call the fetch function directly.
                // We define it inside to ensure it has the latest scope.
                const getResults = async () => {
                    try {
                        const { data } = await api.get(`/backtest/${lastStartedBacktestId}`);
                        setBacktestResult(data);
                        setIsLoading(false); // Stop the main page loader
                        toast.success('Backtest results loaded!', { id: toastId });
                    } catch (error) {
                        // Handle polling for "still running" status
                        if (error.response?.status === 202) {
                            toast('Backtest results are being prepared, checking again in 10s...', { id: toastId });
                            setTimeout(() => getResults(), 10000);
                        } else {
                            toast.error(error.response?.data?.detail || "Failed to fetch backtest results.", { id: toastId });
                            setIsLoading(false);
                        }
                    }
                };

                getResults();

            } else { // If the WebSocket message reports a failure
                toast.error(`Backtest failed on server: ${lastMessage.data.error || 'Unknown error'}`);
                setIsLoading(false);
            }

            // Clear the ID to prevent this effect from re-running for the same message
            setLastStartedBacktestId(null);
        }
    }, [lastMessage, lastStartedBacktestId]); // <-- fetchResult is REMOVED from dependencies

    // Main function to start the backtest
    const onRunBacktest = async (data) => {
        setIsLoading(true);
        setBacktestResult(null);
        const toastId = toast.loading("Submitting backtest job to the server...");

        const { strategy_name, symbol, timeframe, parameters } = data;
        const payload = { strategy_name, symbol, timeframe, parameters };

        try {
            const { data: response } = await api.post('/backtest', payload);
            setLastStartedBacktestId(response.result_id);
            toast.success("Backtest is running on the server. You will be notified upon completion.", { id: toastId });
        } catch (error) {
            toast.error(error.response?.data?.detail || "Backtest failed to start.", { id: toastId });
            setIsLoading(false);
        }
    };

    return (
        <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-light-text dark:text-dark-text mb-6">{t('sidebar.backtest')}</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 overflow-y-auto">
                {/* --- Configuration Panel --- */}
                <form onSubmit={handleSubmit(onRunBacktest)} className="lg:col-span-1 glass-card p-6 space-y-4">
                    <h2 className="text-xl font-semibold">Configuration</h2>

                    <div>
                        <label className="block text-sm font-medium">Strategy</label>
                        <select {...register("strategy_name")} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-dark-bg/50 dark:border-dark-border focus:ring-primary focus:border-primary">
                            {Object.entries(STRATEGIES_CONFIG).map(([key, config]) => (
                                <option key={key} value={key}>{config.name} {config.isPremium ? '⭐' : ''}</option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium">Symbol</label>
                            <input {...register("symbol", { required: true })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-dark-bg/50 dark:border-dark-border focus:ring-primary focus:border-primary" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium">Timeframe</label>
                            <select
                                {...register("timeframe", { required: true })}
                                defaultValue="H1"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-dark-bg/50 dark:border-dark-border focus:ring-primary focus:border-primary"
                            >
                                {availableTimeframes.map(tf => <option key={tf} value={tf}>{tf}</option>)}
                            </select>
                        </div>
                    </div>

                    <hr className="dark:border-dark-border/50"/>
                    <h3 className="font-semibold">Parameters</h3>
                    <div className="space-y-3">
                        {selectedStrategyConfig?.parameters.map(param => (
                            param.type === 'multiselect' ? (
                                <div key={param.name}>
                                    <label className="block text-sm font-medium">{param.label}</label>
                                    <Controller name={`parameters.${param.name}`} control={control} render={({ field }) => (
                                        <MultiSelect options={param.options} value={field.value || []} onChange={field.onChange} />
                                    )} />
                                </div>
                            ) : (
                                <div key={param.name}>
                                    <label className="block text-sm font-medium">{param.label}</label>
                                    <input
                                        type={param.type}
                                        step={param.step || 'any'}
                                        {...register(`parameters.${param.name}`, { valueAsNumber: param.type === 'number' })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-dark-bg/50 dark:border-dark-border focus:ring-primary focus:border-primary"
                                    />
                                </div>
                            )
                        ))}
                    </div>

                    <button type="submit" disabled={isLoading} className="w-full mt-4 inline-flex items-center justify-center px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:bg-primary-700 transition-all duration-300 transform hover:scale-105 disabled:bg-gray-400 disabled:scale-100 disabled:cursor-not-allowed">
                        <PlayCircleIcon className="h-6 w-6 mr-2"/>
                        {isLoading ? "Running Backtest..." : "Run Backtest"}
                    </button>
                </form>

                {/* --- Results Panel --- */}
                <div className="lg:col-span-2 bg-white dark:bg-dark-card rounded-xl p-6 border dark:border-dark-border min-h-[500px] flex items-center justify-center">
                    <AnimatePresence mode="wait">
                        {isLoading && (
                            <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center justify-center h-full text-center">
                                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                                <p className="mt-4 font-semibold text-light-text-secondary dark:text-dark-text-secondary">Simulating Historical Performance...</p>
                                <p className="text-sm text-gray-400">(This can take several minutes)</p>
                            </motion.div>
                        )}
                        {backtestResult && (
                             <motion.div key="results" className="w-full">
                                <BacktestResults results={backtestResult} />
                             </motion.div>
                        )}
                        {!isLoading && !backtestResult && (
                             <motion.div key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex items-center justify-center h-full text-center">
                                <div>
                                    <BeakerIcon className="mx-auto h-16 w-16 text-gray-300 dark:text-gray-600"/>
                                    <h3 className="mt-2 text-lg font-medium text-light-text dark:text-dark-text">Ready to Test</h3>
                                    <p className="mt-1 text-sm text-gray-500">Configure a strategy and run a backtest to see its historical performance.</p>
                                </div>
                             </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default BacktestPage;