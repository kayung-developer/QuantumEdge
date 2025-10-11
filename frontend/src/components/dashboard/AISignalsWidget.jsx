import React, { useState, useEffect, useCallback } from 'react';
// --- Other imports ---
import signalService from '../../api/signalService';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCpu, FiCheck, FiX, FiTrendingUp, FiTrendingDown, FiClock, FiActivity } from 'react-icons/fi';
import Button from '../common/Button';
import { formatDistanceToNow } from 'date-fns';
import ChartSpinner from '../common/ChartSpinner';

// A self-contained card for a single AI signal, handling its own actions.
const AISignalCard = ({ signal, onAction }) => {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleAction = async (action_type) => {
        setIsSubmitting(true);
        const toastId = toast.loading(`Submitting action: ${action_type}...`);
        try {
            await signalService.actionSignal(signal.id, { action_type });
            toast.success(`Signal ${action_type.toLowerCase()}ed successfully!`, { id: toastId });
            onAction(signal.id); // Notify parent to remove this card from the UI
        } catch (error) {
            toast.error(error.response?.data?.detail || `Failed to ${action_type.toLowerCase()} signal.`, { id: toastId });
        } finally {
            // No need to set isSubmitting to false, as the component will be removed.
        }
    };

    const isBuy = signal.side === 'BUY';

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 50, scale: 0.3 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: -50, transition: { duration: 0.2 } }}
            className="bg-dark-tertiary/60 p-4 rounded-lg border border-dark-secondary"
        >
            <div className="flex justify-between items-start">
                <div>
                    <div className="flex items-center space-x-2">
                        {isBuy ? <FiTrendingUp className="text-success"/> : <FiTrendingDown className="text-danger"/>}
                        <span className="font-bold text-lg text-text-primary">{signal.side} {signal.symbol}</span>
                    </div>
                    <p className="text-xs text-text-secondary">{signal.rationale}</p>
                </div>
                <span className="font-mono text-sm bg-dark-background px-2 py-1 rounded">
                    {(signal.confidence_score * 100).toFixed(1)}%
                </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center my-4 text-sm border-y border-dark-secondary py-2">
                <div><p className="text-text-secondary text-xs">Entry</p><p className="font-mono">{signal.entry_price.toFixed(2)}</p></div>
                <div><p className="text-text-secondary text-xs">Stop Loss</p><p className="font-mono">{signal.stop_loss.toFixed(2)}</p></div>
                <div><p className="text-text-secondary text-xs">Take Profit</p><p className="font-mono">{signal.take_profit.toFixed(2)}</p></div>
            </div>
            <div className="flex justify-between items-center">
                 <div className="text-xs text-text-secondary flex items-center">
                    <FiClock className="mr-1"/>
                    <span>Expires {formatDistanceToNow(new Date(signal.expires_at), { addSuffix: true })}</span>
                </div>
                <div className="flex space-x-2">
                    <Button onClick={() => handleAction("REJECT")} disabled={isSubmitting} size="sm" variant="secondary" className="bg-danger/20 hover:bg-danger/40 !text-danger"><FiX/></Button>
                    <Button onClick={() => handleAction("APPROVE")} disabled={isSubmitting} size="sm" variant="secondary" className="bg-success/20 hover:bg-success/40 !text-success"><FiCheck/></Button>
                </div>
            </div>
        </motion.div>
    );
};

// The main widget component that fetches and displays a list of signals.
const AISignalsWidget = () => {
    const [signals, setSignals] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchSignals = useCallback(async () => {
        try {
            const response = await signalService.getPendingSignals();
            setSignals(response.data);
        } catch (error) {
            // Don't show toast on a polling component to avoid spamming user
            console.error("Failed to fetch AI signals:", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSignals();
        const interval = setInterval(fetchSignals, 15000); // Poll for new signals every 15 seconds
        return () => clearInterval(interval);
    }, [fetchSignals]);

    const handleAction = (signalId) => {
        setSignals(prev => prev.filter(s => s.id !== signalId));
    };

    return (
        <div className="bg-dark-surface border border-dark-secondary rounded-lg p-5 h-full flex flex-col">
             <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center">
                <FiCpu className="mr-2 text-brand-primary"/>
                AI Trading Signals
            </h3>
            <div className="flex-grow space-y-4 overflow-y-auto pr-2">
                <AnimatePresence>
                    {loading && <ChartSpinner text="Awaiting AI Signals..." />}
                    {!loading && signals.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-center text-text-secondary">
                            <FiCpu className="h-12 w-12 mb-4"/>
                            <p>No new signals from AI models.</p>
                            <p className="text-xs mt-1">The system is actively scanning the markets.</p>
                        </div>
                    )}
                    {signals.map(signal => (
                        <AISignalCard key={signal.id} signal={signal} onAction={handleAction}/>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default AISignalsWidget;