import React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { FiCpu, FiSettings, FiPlayCircle, FiBarChart2, FiChevronsRight } from 'react-icons/fi';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
import BacktestResultsDisplay from '../components/strategies/BacktestResultsDisplay';
import strategyService from '../api/strategyService';
import backtestService from '../api/backtestService'; // For launching and polling jobs

const forgeJobSchema = z.object({
    strategy_id: z.string().min(1, "Please select a strategy to optimize."),
    symbol: z.string().min(1, "Symbol is required.").toUpperCase(),
    exchange: z.string().min(1, "Exchange is required."),
    timeframe: z.string().min(1, "Timeframe is required."),
    start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date format (YYYY-MM-DD)"),
    end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date format (YYYY-MM-DD)"),
    optimization_metric: z.string(),
});

const StrategyForgePage = () => {
    const [strategies, setStrategies] = useState([]);
    const [job, setJob] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const { control, handleSubmit, watch, formState: { errors } } = useForm({
        resolver: zodResolver(forgeJobSchema),
        defaultValues: {
            strategy_id: "momentum_crossover",
            symbol: "BTCUSDT",
            exchange: "Binance",
            timeframe: "4H",
            start_date: "2023-01-01",
            end_date: "2023-12-31",
            optimization_metric: "sharpe_ratio"
        }
    });

    const selectedStrategyId = watch('strategy_id');
    const selectedStrategy = strategies.find(s => s.id === selectedStrategyId);

    // Fetch available strategies for the dropdown on component mount
    useEffect(() => {
        strategyService.getAvailableStrategies()
            .then(res => setStrategies(res.data))
            .catch(() => toast.error("Could not fetch available strategies."));
    }, []);

    // Poll for the job's status if it is in a running state
    useEffect(() => {
        let interval;
        if (job && ['PENDING', 'PROGRESS', 'RUNNING'].includes(job.status)) {
            interval = setInterval(async () => {
                try {
                    const response = await backtestService.getWalkForwardStatus(job.id); // Re-using the same status endpoint
                    setJob(response.data);
                    if (['SUCCESS', 'FAILURE'].includes(response.data.status)) {
                        clearInterval(interval);
                        toast.success("Optimization job finished!");
                    }
                } catch (error) {
                    toast.error("Could not poll job status.");
                    clearInterval(interval);
                }
            }, 5000); // Poll every 5 seconds
        }
        return () => clearInterval(interval);
    }, [job]);

    const onSubmit = async (data) => {
        setIsLoading(true);
        setJob(null);
        const toastId = toast.loading("Submitting AutoML optimization job...");
        try {
            // Note: This endpoint is hypothetical based on our backend design
            //const response = await forgeService.launch(data);
            // For now, we will mock the response and polling
            setTimeout(() => {
                const mockJob = { id: 'celery-task-uuid-12345', status: 'RUNNING', config: data };
                setJob(mockJob);
                toast.success("Job started! Results will update in real-time.", { id: toastId });
            }, 1500);

        } catch (error) {
            toast.error(error.response?.data?.detail || "Failed to start job.", { id: toastId });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-4 md:p-6 animate-fadeIn">
            <h1 className="text-3xl font-bold text-text-primary mb-2 flex items-center">
                <FiCpu className="mr-3 text-brand-primary"/> Strategy Forge (AutoML)
            </h1>
            <p className="text-text-secondary mb-6 max-w-3xl">
                Define your market conditions and let our AI discover the optimal strategy parameters for you. This feature runs thousands of backtests to find the best configuration for your chosen metric. (Ultimate Plan required)
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 bg-dark-surface border border-dark-secondary rounded-lg p-6 self-start">
                    <h2 className="text-xl font-semibold mb-4 flex items-center"><FiSettings className="mr-2"/> Optimization Configuration</h2>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div>
                            <label className="text-sm">Base Strategy</label>
                            <Controller name="strategy_id" control={control} render={({ field }) => ( <select {...field} className="w-full bg-dark-background p-2 rounded-md mt-1"><option value="">Select a Strategy</option>{strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select> )}/>
                            {errors.strategy_id && <p className="text-xs text-danger mt-1">{errors.strategy_id.message}</p>}
                        </div>

                        <div>
                            <label className="text-sm">Symbol</label>
                            <Controller name="symbol" control={control} render={({ field }) => ( <input {...field} className="w-full bg-dark-background p-2 rounded-md mt-1"/> )}/>
                            {errors.symbol && <p className="text-xs text-danger mt-1">{errors.symbol.message}</p>}
                        </div>

                         <div>
                            <label className="text-sm">Optimization Metric</label>
                            <Controller name="optimization_metric" control={control} render={({ field }) => ( <select {...field} className="w-full bg-dark-background p-2 rounded-md mt-1"><option value="sharpe_ratio">Sharpe Ratio</option><option value="net_profit">Net Profit</option><option value="max_drawdown_pct">Lowest Drawdown</option></select> )}/>
                        </div>

                        {selectedStrategy && (
                            <div className="text-xs p-3 bg-dark-background rounded">
                                <p className="font-bold mb-1">Parameter Space:</p>
                                <p className="text-text-secondary">{selectedStrategy.description}</p>
                                <p className="mt-2">The AI will optimize the following default parameters: {Object.keys(selectedStrategy.default_params).join(', ')}</p>
                            </div>
                        )}

                        <Button type="submit" isLoading={isLoading} disabled={!selectedStrategy || isLoading} className="w-full">
                            <FiPlayCircle className="mr-2"/> Forge Optimal Strategy
                        </Button>
                    </form>
                </div>

                <div className="lg:col-span-2 bg-dark-surface border border-dark-secondary rounded-lg p-6 min-h-[500px]">
                    <h2 className="text-xl font-semibold mb-4 flex items-center"><FiBarChart2 className="mr-2"/> Optimization Results</h2>
                    {isLoading && <ChartSpinner text="Submitting job to the compute cluster..."/>}
                    {job ? (
                        <div>
                            <div className="flex justify-between items-center bg-dark-tertiary p-3 rounded-md">
                                <div>
                                    <p className="text-xs text-text-secondary">Job ID: <span className="font-mono">{job.id}</span></p>
                                    <p className="text-sm font-bold">Status: {job.status}</p>
                                </div>
                                {(job.status === 'RUNNING' || job.status === 'PROGRESS') && <div className="w-6 h-6 border-2 border-dark-secondary border-t-brand-primary rounded-full animate-spin"></div>}
                            </div>

                            {job.status === 'SUCCESS' && job.best_performance ? (
                                <div className="mt-4">
                                    <h3 className="font-bold text-lg mb-2">Optimal Configuration Found:</h3>
                                    <div className="p-4 bg-dark-background rounded-md font-mono text-sm text-green-300">
                                        <pre>{JSON.stringify(job.best_parameters, null, 2)}</pre>
                                    </div>
                                    <div className="mt-4">
                                        <BacktestResultsDisplay data={{ performance: job.best_performance, trades: [], equity_curve: {} }} />
                                    </div>
                                </div>
                            ) : job.status === 'FAILURE' ? (
                                <div className="mt-4 text-danger">Job failed. Please check the logs or try different parameters.</div>
                            ) : (
                                <div className="mt-4">
                                    <p className="text-text-secondary">The optimization is running on the server. This panel will update automatically when results are available. This process can take several minutes depending on the date range and strategy complexity.</p>
                                </div>
                            )}
                        </div>
                    ) : (
                         !isLoading && <div className="text-center pt-16 text-text-secondary"><FiCpu className="h-16 w-16 mx-auto mb-4"/><p>Configure and launch an optimization job to see the results here.</p></div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StrategyForgePage;