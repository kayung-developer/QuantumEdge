import React from 'react';
import { clsx } from 'clsx';
import { FiTrendingUp, FiTrendingDown, FiDollarSign, FiPercent, FiHash, FiCheckCircle, FiShield } from 'react-icons/fi';

// A reusable metric display component
const Metric = ({ title, value, unit = '', isPositive, isNeutral = false, icon }) => {
    const valueColor = isNeutral ? 'text-text-primary' : (isPositive ? 'text-success' : 'text-danger');

    return (
        <div className="bg-dark-tertiary/50 p-4 rounded-lg flex items-start space-x-3">
            <div className="flex-shrink-0 text-text-secondary mt-1">{icon}</div>
            <div>
                <p className="text-sm text-text-secondary">{title}</p>
                <p className={clsx("text-xl font-bold font-mono", valueColor)}>
                    {value}{unit}
                </p>
            </div>
        </div>
    );
};

/**
 * A component to display a grid of key performance indicators (KPIs) from a backtest.
 * @param {object} data - The 'performance' object from the backtest results.
 */
const PerformanceMetrics = ({ data }) => {
    if (!data) return null;

    const formatValue = (val, decimals = 2) => {
        if (val === null || val === undefined || isNaN(val)) return 'N/A';
        return val.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    }

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <Metric
                title="Net Profit"
                value={`$${formatValue(data.net_profit)}`}
                isPositive={data.net_profit >= 0}
                icon={<FiDollarSign />}
            />
            <Metric
                title="Sharpe Ratio"
                value={formatValue(data.sharpe_ratio)}
                isPositive={data.sharpe_ratio >= 1}
                icon={<FiTrendingUp />}
            />
            <Metric
                title="Max Drawdown"
                value={formatValue(data.max_drawdown_pct)}
                unit="%"
                isPositive={false} // Drawdown is always a negative metric
                icon={<FiTrendingDown />}
            />
            <Metric
                title="Profit Factor"
                value={formatValue(data.profit_factor)}
                isPositive={data.profit_factor >= 1}
                icon={<FiCheckCircle />}
            />
            <Metric
                title="Total Trades"
                value={data.total_trades}
                isNeutral
                icon={<FiHash />}
            />
            <Metric
                title="Win Rate"
                value={formatValue(data.win_rate_pct)}
                unit="%"
                isPositive={data.win_rate_pct >= 50}
                icon={<FiPercent />}
            />
            <Metric
                title="Avg. Win"
                value={`$${formatValue(data.average_win_usd)}`}
                isPositive
                icon={<div className="text-success"><FiTrendingUp /></div>}
            />
            <Metric
                title="Avg. Loss"
                value={`$${formatValue(data.average_loss_usd)}`}
                isPositive={false}
                icon={<div className="text-danger"><FiTrendingDown /></div>}
            />
        </div>
    );
};

export default PerformanceMetrics;