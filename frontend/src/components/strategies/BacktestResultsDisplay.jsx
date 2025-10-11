import React from 'react';
import { Tab } from '@headlessui/react';
import { clsx } from 'clsx';
import EquityCurveChart from './EquityCurveChart';
import PerformanceMetrics from './PerformanceMetrics';
import Table from '../common/Table';
import { format } from 'date-fns';
import { FiBarChart2, FiActivity, FiClipboard } from 'react-icons/fi';

/**
 * A comprehensive, multi-tabbed component to display all results from a
 * backtesting run. It organizes the data into a summary, an equity curve chart,
 * and a detailed trade-by-trade log.
 *
 * @param {object} data - The full results object from the backtesting API.
 */
const BacktestResultsDisplay = ({ data }) => {
    if (!data || !data.performance) {
        return <p className="text-text-secondary">No performance data available for this backtest.</p>;
    }

    const { performance, equity_curve, trades, parameters } = data;

    const tradeHistoryHeaders = [
        { key: 'entry_time', label: 'Entry Time' }, { key: 'type', label: 'Type' },
        { key: 'entry_price', label: 'Entry Price' }, { key: 'exit_time', label: 'Exit Time' },
        { key: 'exit_price', label: 'Exit Price' }, { key: 'profit', label: 'Profit ($)' },
        { key: 'status', label: 'Exit Reason' },
    ];

    return (
        <div className="w-full h-full flex flex-col">
            <Tab.Group>
                <Tab.List className="flex space-x-1 rounded-xl bg-dark-background p-1 mb-4">
                    <Tab className={({ selected }) => clsx('flex items-center justify-center w-full rounded-lg py-2.5 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary shadow' : 'text-text-secondary hover:bg-white/[0.12]')}><FiBarChart2 className="mr-2"/>Summary</Tab>
                    <Tab className={({ selected }) => clsx('flex items-center justify-center w-full rounded-lg py-2.5 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary shadow' : 'text-text-secondary hover:bg-white/[0.12]')}><FiActivity className="mr-2"/>Equity Curve</Tab>
                    <Tab className={({ selected }) => clsx('flex items-center justify-center w-full rounded-lg py-2.5 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary shadow' : 'text-text-secondary hover:bg-white/[0.12]')}><FiClipboard className="mr-2"/>Trade Log</Tab>
                </Tab.List>
                <Tab.Panels className="flex-grow h-0">
                    <Tab.Panel className="h-full focus:outline-none overflow-y-auto">
                        <PerformanceMetrics data={performance} />
                    </Tab.Panel>
                    <Tab.Panel className="h-full focus:outline-none">
                        <EquityCurveChart data={equity_curve} initialCapital={performance.initial_capital} />
                    </Tab.Panel>
                    <Tab.Panel className="h-full focus:outline-none overflow-y-auto">
                        {trades && trades.length > 0 ? (
                             <Table headers={tradeHistoryHeaders}>
                                {trades.map((trade, index) => (
                                    <tr key={index} className="hover:bg-dark-tertiary text-sm font-mono">
                                        <td className="px-4 py-2 text-text-secondary">{trade.entry_time ? format(new Date(trade.entry_time), 'yyyy.MM.dd HH:mm') : 'N/A'}</td>
                                        <td className={clsx("px-4 py-2 font-bold", trade.type === 'BUY' ? 'text-success' : 'text-danger')}>{trade.type}</td>
                                        <td className="px-4 py-2">{trade.entry_price?.toFixed(2)}</td>
                                        <td className="px-4 py-2 text-text-secondary">{trade.exit_time ? format(new Date(trade.exit_time), 'yyyy.MM.dd HH:mm') : 'N/A'}</td>
                                        <td className="px-4 py-2">{trade.exit_price?.toFixed(2) || 'N/A'}</td>
                                        <td className={clsx("px-4 py-2", trade.profit >= 0 ? 'text-success' : 'text-danger')}>{trade.profit?.toFixed(2)}</td>
                                        <td className="px-4 py-2 text-text-secondary">{trade.status}</td>
                                    </tr>
                                ))}
                            </Table>
                        ) : (
                            <p className="text-center text-text-secondary p-8">No trades were executed in this backtest.</p>
                        )}
                    </Tab.Panel>
                </Tab.Panels>
            </Tab.Group>
        </div>
    );
};

export default BacktestResultsDisplay;