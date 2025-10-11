import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { FiLink, FiArrowRight, FiExternalLink } from 'react-icons/fi';
import onchainService from '../api/onchainService';
import ChartSpinner from '../components/common/ChartSpinner';
import { formatDistanceToNow } from 'date-fns';

const WhaleTrackerWidget = () => {
    const [transfers, setTransfers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTransfers = async () => {
            try {
                // For demonstration, we track USDC. This could be a user-selected token.
                const response = await onchainService.trackWhales('USDC');
                setTransfers(response.data);
            } catch (error) {
                toast.error("Could not load whale tracking data.");
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchTransfers();
        const interval = setInterval(fetchTransfers, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    const formatAddress = (addr) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

    if (loading) return <ChartSpinner text="Scanning blockchain for whale movements..." />;

    return (
        <div className="bg-dark-surface p-6 rounded-lg border border-dark-secondary">
            <h2 className="text-xl font-bold mb-4">Recent USDC Whale Transfers (> $100k)</h2>
            <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {transfers.length === 0 ? (
                    <p className="text-text-secondary text-center py-8">No significant transfers detected in recent blocks.</p>
                ) : (
                    transfers.map(tx => (
                        <div key={tx.transaction_hash} className="p-3 bg-dark-tertiary/50 rounded-md">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3 font-mono text-sm">
                                    <span className="font-bold text-orange-400">{formatAddress(tx.from_whale)}</span>
                                    <FiArrowRight className="text-text-secondary"/>
                                    <span className="text-text-primary">{formatAddress(tx.to_address)}</span>
                                </div>
                                <a href={`https://etherscan.io/tx/${tx.transaction_hash}`} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                                    <FiExternalLink />
                                </a>
                            </div>
                            <div className="mt-2 text-lg font-bold">
                                ${tx.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                <span className="text-sm font-normal text-text-secondary ml-2">USDC</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};


const OnChainPage = () => {
    return (
        <div className="p-6 animate-fadeIn">
            <h1 className="text-3xl font-bold mb-6 flex items-center">
                <FiLink className="mr-3"/>On-Chain Intelligence
            </h1>
            <WhaleTrackerWidget />
        </div>
    );
};

export default OnChainPage;