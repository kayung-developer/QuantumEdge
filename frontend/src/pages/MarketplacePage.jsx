import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { FiShoppingBag, FiAward } from 'react-icons/fi';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
// import marketplaceService from '../api/marketplaceService';

// This is a self-contained, robust component for displaying a single strategy.
const StrategyCard = ({ strategy }) => {
    // Safely access nested properties with optional chaining and provide defaults
    const performance = strategy.verified_performance_summary || {};
    const netProfit = performance.net_profit ?? 0;
    const sharpeRatio = performance.sharpe_ratio ?? 0;
    const maxDrawdown = performance.max_drawdown_pct ?? 0;

    return (
        <div className="bg-dark-surface p-6 rounded-lg border border-dark-secondary hover:border-brand-primary/80 transition-all duration-300 flex flex-col hover:shadow-2xl hover:-translate-y-1">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-xl font-bold text-text-primary">{strategy.name || "Unnamed Strategy"}</h3>
                    <p className="text-sm text-text-secondary">by {strategy.author_name || "Anonymous"}</p>
                </div>
                <span className="flex-shrink-0 px-3 py-1 text-sm font-bold text-green-300 bg-success/20 rounded-full">
                    ${strategy.subscription_price_monthly}/mo
                </span>
            </div>
            <p className="text-sm text-text-secondary my-4 h-20 overflow-hidden text-ellipsis">
                {strategy.description || "No description provided."}
            </p>
            <div className="border-t border-dark-secondary pt-4 mt-auto">
                <h4 className="text-xs font-semibold uppercase text-text-secondary mb-2 flex items-center">
                    <FiAward className="mr-2"/> Verified Performance (1Y)
                </h4>
                <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                        <p className={`font-bold text-lg ${netProfit >= 0 ? 'text-success' : 'text-danger'}`}>{netProfit >= 0 ? '+' : ''}{netProfit.toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
                        <p className="text-xs text-text-secondary">Net Profit ($)</p>
                    </div>
                    <div>
                        <p className="font-bold text-lg text-text-primary">{sharpeRatio.toFixed(2)}</p>
                        <p className="text-xs text-text-secondary">Sharpe Ratio</p>
                    </div>
                    <div>
                        <p className="font-bold text-lg text-danger">{maxDrawdown.toFixed(1)}%</p>
                        <p className="text-xs text-text-secondary">Max Drawdown</p>
                    </div>
                </div>
            </div>
             <div className="mt-4">
                <Button className="w-full">View Details & Subscribe</Button>
            </div>
        </div>
    );
};


const MarketplacePage = () => {
    const [strategies, setStrategies] = useState([]);
    const [loading, setLoading] = useState(true);

    // Mock data for display, ensuring all fields are present
    const mockStrategies = [
        { id: 1, name: "SMC Pro Trader", author_name: "QuantMaster", description: "An advanced SMC strategy focusing on high-probability order blocks and liquidity sweeps after a confirmed break of structure.", subscription_price_monthly: 99, verified_performance_summary: { net_profit: 15234, sharpe_ratio: 1.88, max_drawdown_pct: 8.5 }},
        { id: 2, name: "Volatility Breakout", author_name: "JaneDoe", description: "Trades breakouts during high volatility periods identified by contracting Bollinger Bands and high ATR. Best for trending markets.", subscription_price_monthly: 49, verified_performance_summary: { net_profit: 8765, sharpe_ratio: 1.21, max_drawdown_pct: 14.2 }},
        { id: 3, name: "Mean Reversion King", author_name: "ReversalBot", description: "A counter-trend strategy that uses RSI and Stochastic oscillators to identify oversold and overbought conditions in range-bound markets.", subscription_price_monthly: 79, verified_performance_summary: { net_profit: 11050, sharpe_ratio: 1.55, max_drawdown_pct: 6.9 }},
    ];

    useEffect(() => {
        // In a real system:
        // marketplaceService.getLiveStrategies()
        //   .then(res => setStrategies(res.data))
        //   .catch(() => toast.error("Failed to load marketplace."))
        //   .finally(() => setLoading(false));

        // Using mock data:
        setTimeout(() => {
            setStrategies(mockStrategies);
            setLoading(false);
        }, 1000); // Simulate network delay
    }, []);

    if (loading) return <ChartSpinner text="Loading Strategy Marketplace..." />;

    return (
        <div className="p-6 animate-fadeIn">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-text-primary flex items-center">
                    <FiShoppingBag className="mr-3"/> Strategy Marketplace
                </h1>
                <Button>Publish Your Strategy</Button>
            </div>

            <p className="text-text-secondary mb-6 max-w-3xl">
                Discover, analyze, and subscribe to top-performing strategies created by other traders. All performance metrics are verified by the AuraQuant backtesting engine on standardized data to ensure transparency and authenticity.
            </p>

            {strategies.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {strategies.map(s => <StrategyCard key={s.id} strategy={s} />)}
                </div>
            ) : (
                <div className="text-center py-20 bg-dark-surface rounded-lg">
                    <p className="text-text-secondary">The marketplace is currently empty. Be the first to publish a strategy!</p>
                </div>
            )}
        </div>
    );
};

export default MarketplacePage;