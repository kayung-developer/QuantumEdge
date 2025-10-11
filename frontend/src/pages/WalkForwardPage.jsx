import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import { FiPlayCircle, FiSettings, FiBarChart2 } from 'react-icons/fi';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
import backtestService from '../api/backtestService';
import strategyService from '../api/strategyService';
// We will create a new component to visualize these specific results
// import WalkForwardResultsDisplay from '../components/strategies/WalkForwardResultsDisplay';

const WalkForwardPage = () => {
    const [strategies, setStrategies] = useState([]);
    const [job, setJob] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const { control, handleSubmit, watch } = useForm({
        defaultValues: {
            strategy_id: "momentum_crossover",
            symbol: "BTCUSDT",
            exchange: "Binance",
            timeframe: "4H",
            start_date: "2023-01-01",
            end_date: "2023-12-31",
            training_period_days: 90,
            testing_period_days: 30,
            optimization_metric: "sharpe_ratio"
        }
    });

    // Fetch available strategies for the dropdown
    useEffect(() => {
        strategyService.getAvailableStrategies().then(res => setStrategies(res.data));
    }, []);

    // Poll for job status if a job is running
    useEffect(() => {
        let interval;
        if (job && (job.status === 'PENDING' || job.status === 'PROGRESS' || job.status === 'RUNNING')) {
            interval = setInterval(async () => {
                try {
                    const response = await backtestService.getWalkForwardStatus(job.id);
                    setJob(response.data);
                    if (response.data.status === 'SUCCESS' || response.data.status === 'FAILURE') {
                        clearInterval(interval);
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
        const toastId = toast.loading("Submitting Walk-Forward Analysis job...");
        try {
            const response = await backtestService.launchWalkForward(data);
            setJob(response.data);
            toast.success("Job started successfully! Results will update automatically.", { id: toastId });
        } catch (error) {
            toast.error(error.response?.data?.detail || "Failed to start job.", { id: toastId });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="animate-fadeIn p-4 md:p-6">
            <h1 className="text-3xl font-bold text-text-primary mb-6">Walk-Forward Optimization Studio</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 bg-dark-surface border border-dark-secondary rounded-lg p-6 self-start">
                    <h2 className="text-xl font-semibold mb-4 flex items-center"><FiSettings className="mr-2"/> Configuration</h2>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {/* Form Inputs for config */}
                        <label>Strategy</label>
                        <Controller name="strategy_id" control={control} render={({ field }) => ( <select {...field} className="w-full bg-dark-background p-2 rounded-md"> {strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)} </select> )}/>
                        <label>Symbol</label>
                        <Controller name="symbol" control={control} render={({ field }) => ( <input {...field} type="text" className="w-full bg-dark-background p-2 rounded-md"/> )}/>
                        <label>Training Period (Days)</label>
                        <Controller name="training_period_days" control={control} render={({ field }) => ( <input {...field} type="number" className="w-full bg-dark-background p-2 rounded-md"/> )}/>
                        <label>Testing Period (Days)</label>
                        <Controller name="testing_period_days" control={control} render={({ field }) => ( <input {...field} type="number" className="w-full bg-dark-background p-2 rounded-md"/> )}/>

                        <Button type="submit" isLoading={isLoading} className="w-full">
                            <FiPlayCircle className="mr-2"/> Start Walk-Forward Analysis
                        </Button>
                    </form>
                </div>

                <div className="lg:col-span-2 bg-dark-surface border border-dark-secondary rounded-lg p-6 min-h-[500px]">
                    <h2 className="text-xl font-semibold mb-4 flex items-center"><FiBarChart2 className="mr-2"/> Analysis Results</h2>
                    {job ? (
                        <div>
                            <p>Job ID: <span className="font-mono text-xs">{job.id}</span></p>
                            <p>Status: <span className="font-bold">{job.status}</span></p>
                            {/* Placeholder for results display component */}
                            {/* {job.status === 'SUCCESS' && <WalkForwardResultsDisplay data={job.results} />} */}
                            {(job.status === 'PENDING' || job.status === 'PROGRESS') && <ChartSpinner text="Analysis in progress..."/>}
                        </div>
                    ) : (
                         <p className="text-text-secondary">Configure and run an analysis to see the results here.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WalkForwardPage;