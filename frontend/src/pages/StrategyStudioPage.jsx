import React, { useState, useEffect } from 'react';
import { Tab } from '@headlessui/react';
import { useForm, Controller } from 'react-hook-form';
import toast from 'react-hot-toast';
import { FiPlayCircle, FiSettings, FiCode, FiBarChart2 } from 'react-icons/fi';
import Editor, { loader } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import { clsx } from 'clsx';

import strategyService from '../api/strategyService';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
import BacktestResultsDisplay from '../components/strategies/BacktestResultsDisplay';

const STRATEGY_TEMPLATE = `from app.trading_strategies.strategy_base import Strategy
import pandas_ta as ta

# Your custom strategy class MUST be named "CustomStrategy"
# It must also inherit from the base Strategy class.
class CustomStrategy(Strategy):
    """
    A simple example strategy.
    Buys when the 10-period EMA crosses above the 30-period EMA.
    Sells when the 10-period EMA crosses below the 30-period EMA.
    """

    def init(self):
        """
        Calculate indicators here. They will be available in self.data via
        columns like self.data['fast_ema']
        """
        # Get parameters safely using a helper method
        fast_ema_len = self.get_parameter("fast_ema", 10)
        slow_ema_len = self.get_parameter("slow_ema", 30)

        # pandas_ta automatically adds columns to the DataFrame
        self.data.ta.ema(length=fast_ema_len, append=True, col_names=('fast_ema',))
        self.data.ta.ema(length=slow_ema_len, append=True, col_names=('slow_ema',))

        # It's good practice to drop rows with NaN values after calculations
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        """
        Implement your trading logic for each candle (data point).
        'self.index' refers to the current candle's position in the DataFrame.
        """
        if self.index < 1: # Ensure we have a previous candle to check against
            return

        # Crossover conditions
        bullish_crossover = (self.data['fast_ema'][self.index - 1] < self.data['slow_ema'][self.index - 1] and
                             self.data['fast_ema'][self.index] > self.data['slow_ema'][self.index])

        bearish_crossover = (self.data['fast_ema'][self.index - 1] > self.data['slow_ema'][self.index - 1] and
                             self.data['fast_ema'][self.index] < self.data['slow_ema'][self.index])

        if not self.is_in_position:
            if bullish_crossover:
                # Example risk management: SL at 2% below close, 1.5 R:R
                stop_loss = self.data['close'][self.index] * 0.98
                take_profit = self.data['close'][self.index] * 1.03
                self.buy(sl=stop_loss, tp=take_profit)
        else:
            # Simple exit logic: close position on opposite crossover
            if bearish_crossover:
                self.close_position()
`;

const StrategyStudioPage = () => {
    const [strategies, setStrategies] = useState([]);
    const [backtestResult, setBacktestResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [userCode, setUserCode] = useState(STRATEGY_TEMPLATE);
    const [selectedTabIndex, setSelectedTabIndex] = useState(0);

    // Form for pre-built strategies
    const prebuiltForm = useForm();
    const { control: prebuiltControl, handleSubmit: handlePrebuiltSubmit, watch: watchPrebuilt, reset: resetPrebuilt } = prebuiltForm;
    const selectedPrebuiltStrategyId = watchPrebuilt('strategy_id');
    const selectedPrebuiltStrategy = strategies.find(s => s.id === selectedPrebuiltStrategyId);

    // Form for custom code strategies
    const customForm = useForm({
        defaultValues: {
            symbol: 'BTCUSDT', exchange: 'Binance', timeframe: '1H',
            start_date: '2023-01-01', end_date: '2023-12-31',
            parameters: '{\n  "fast_ema": 10,\n  "slow_ema": 30\n}'
        }
    });
    const { control: customControl, handleSubmit: handleCustomSubmit } = customForm;

    // Configure Monaco Editor theme on initial mount
    useEffect(() => {
        loader.init().then(monaco => {
            monaco.editor.defineTheme('auraquant-dark', {
                base: 'vs-dark', inherit: true, rules: [],
                colors: { 'editor.background': '#161B22' },
            });
        });
    }, []);

    // Fetch available strategies on mount
    useEffect(() => {
        strategyService.getAvailableStrategies()
            .then(res => setStrategies(res.data))
            .catch(() => toast.error("Could not fetch available strategies."));
    }, []);

    // Update pre-built form when a new strategy is selected from the dropdown
    useEffect(() => {
        if (selectedPrebuiltStrategy) {
            resetPrebuilt({
                strategy_id: selectedPrebuiltStrategy.id,
                symbol: 'BTCUSDT', exchange: 'Binance', timeframe: '1H',
                start_date: '2023-01-01', end_date: '2023-12-31',
                parameters: selectedPrebuiltStrategy.default_params
            });
        }
    }, [selectedPrebuiltStrategy, resetPrebuilt]);

    const onPrebuiltSubmit = async (data) => {
        const payload = { ...data, parameters: Object.fromEntries( Object.entries(data.parameters).map(([key, value]) => [key, parseFloat(value)]) ) };
        runBacktest(() => strategyService.runBacktest(payload));
    };

    const onCustomSubmit = async (data) => {
        try {
            const params = JSON.parse(data.parameters);
            const payload = { ...data, parameters: params, user_code: userCode };
            // Note: This requires a new API endpoint and service function for custom code
            // runBacktest(() => strategyService.runCustomBacktest(payload));
            toast.error("Custom backtest API endpoint is not yet implemented."); // Placeholder
        } catch (e) {
            toast.error("Parameters must be valid JSON.");
        }
    };

    const runBacktest = async (apiCall) => {
        setIsLoading(true);
        setBacktestResult(null);
        const toastId = toast.loading("Running backtest... This may take a moment.");
        try {
            const response = await apiCall();
            setBacktestResult(response.data);
            toast.success("Backtest complete!", { id: toastId });
        } catch (error) {
            toast.error(error.response?.data?.detail || "Backtest failed.", { id: toastId });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="animate-fadeIn p-4 md:p-6">
            <h1 className="text-3xl font-bold text-text-primary mb-6">Strategy Studio</h1>
            <Tab.Group selectedIndex={selectedTabIndex} onChange={setSelectedTabIndex}>
                <Tab.List className="flex space-x-1 rounded-xl bg-dark-surface p-1 max-w-sm mb-6">
                    <Tab className={({ selected }) => clsx('w-full rounded-lg py-2 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary hover:bg-white/[0.12]')}>Pre-Built Strategies</Tab>
                    <Tab className={({ selected }) => clsx('w-full rounded-lg py-2 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary hover:bg-white/[0.12]')}>Custom Code IDE</Tab>
                </Tab.List>
                <Tab.Panels>
                    {/* --- TAB 1: PRE-BUILT STRATEGIES --- */}
                    <Tab.Panel><div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1 bg-dark-surface border border-dark-secondary rounded-lg p-6 self-start">
                            <h2 className="text-xl font-semibold mb-4 flex items-center"><FiSettings className="mr-2"/> Configuration</h2>
                            <form onSubmit={handlePrebuiltSubmit(onPrebuiltSubmit)} className="space-y-4">
                                <Controller name="strategy_id" control={prebuiltControl} render={({ field }) => ( <select {...field} className="w-full bg-dark-background p-2 rounded-md"><option value="">Select a Strategy</option>{strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select> )}/>
                                {selectedPrebuiltStrategy && (<>
                                    <div className="text-xs p-2 bg-dark-background rounded">{selectedPrebuiltStrategy.description}</div>
                                    <div className="space-y-2 border-t border-dark-secondary pt-4">
                                        <h3 className="font-semibold">Parameters</h3>
                                        {Object.entries(selectedPrebuiltStrategy.default_params).map(([key, value]) => (<div key={key}><label className="text-sm text-text-secondary">{key}</label><Controller name={`parameters.${key}`} control={prebuiltControl} defaultValue={value} render={({ field }) => ( <input {...field} type="number" step="any" className="w-full bg-dark-background p-2 rounded-md mt-1"/> )}/></div>))}
                                    </div>
                                </>)}
                                <Button type="submit" isLoading={isLoading} disabled={!selectedPrebuiltStrategy} className="w-full"><FiPlayCircle className="mr-2"/> Run Backtest</Button>
                            </form>
                        </div>
                        <div className="lg:col-span-2 bg-dark-surface border border-dark-secondary rounded-lg p-6 min-h-[500px]"><h2 className="text-xl font-semibold mb-4 flex items-center"><FiBarChart2 className="mr-2"/> Backtest Results</h2>{isLoading ? <ChartSpinner text="Executing strategy..."/> : backtestResult ? <BacktestResultsDisplay data={backtestResult} /> : <div className="flex flex-col items-center justify-center h-full text-center text-text-secondary"><FiPlayCircle className="h-16 w-16 mb-4"/><p>Configure and run a backtest to see the results here.</p></div>}</div>
                    </div></Tab.Panel>
                     {/* --- TAB 2: CUSTOM CODE IDE --- */}
                    <Tab.Panel><div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 h-[600px] border border-dark-secondary rounded-lg overflow-hidden"><Editor height="100%" language="python" theme="auraquant-dark" value={userCode} onChange={(value) => setUserCode(value)} options={{ minimap: { enabled: false } }}/></div>
                        <div className="lg:col-span-1 bg-dark-surface border border-dark-secondary rounded-lg p-6 self-start">
                            <h2 className="text-xl font-semibold mb-4 flex items-center"><FiSettings className="mr-2"/> Configuration</h2>
                            <form onSubmit={handleCustomSubmit(onCustomSubmit)} className="space-y-4">
                                <label className="text-sm text-text-secondary">Symbol</label><Controller name="symbol" control={customControl} render={({ field }) => <input {...field} className="w-full bg-dark-background p-2 rounded-md mt-1"/>} />
                                <label className="text-sm text-text-secondary">Parameters (JSON)</label><Controller name="parameters" control={customControl} render={({ field }) => ( <textarea {...field} rows={4} className="w-full font-mono text-sm bg-dark-background p-2 rounded-md"/> )}/>
                                <Button type="submit" isLoading={isLoading} className="w-full"><FiPlayCircle className="mr-2"/> Run Custom Backtest</Button>
                            </form>
                        </div>
                    </div></Tab.Panel>
                </Tab.Panels>
            </Tab.Group>
            {selectedTabIndex === 1 && ( <div className="mt-6 bg-dark-surface border border-dark-secondary rounded-lg p-6 min-h-[300px]"><h2 className="text-xl font-semibold mb-4">Custom Backtest Results</h2>{isLoading ? <ChartSpinner text="Executing your custom strategy..."/> : backtestResult ? <BacktestResultsDisplay data={backtestResult} /> : <div className="text-center text-text-secondary pt-8">Your custom backtest results will appear here.</div>}</div> )}
        </div>
    );
};

export default StrategyStudioPage;