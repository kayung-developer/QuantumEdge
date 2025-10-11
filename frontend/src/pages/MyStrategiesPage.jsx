import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { FiPlus, FiEye, FiEdit, FiArchive } from 'react-icons/fi';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import { clsx } from 'clsx';
// import marketplaceService from '../api/marketplaceService';

const MyStrategiesPage = () => {
    // In a real system, this data would be fetched from a dedicated API endpoint
    // like `/marketplace/my-strategies`
    const [myStrategies, setMyStrategies] = useState([
        { id: 'uuid-1', name: "SMC Pro Trader", version: 2, status: "APPROVED", monthly_subs: 125, earnings: 12375.00 },
        { id: 'uuid-2', name: "ETH Vol Scalper", version: 1, status: "PENDING", monthly_subs: 0, earnings: 0.00 },
        { id: 'uuid-3', name: "Gold Trend Follower", version: 1, status: "REJECTED", monthly_subs: 0, earnings: 0.00 },
        { id: 'uuid-4', name: "Momentum King", version: 3, status: "ARCHIVED", monthly_subs: 0, earnings: 0.00 },
    ]);
    const [loading, setLoading] = useState(false);

    const tableHeaders = [
        { key: 'name', label: 'Strategy Name' },
        { key: 'version', label: 'Version' },
        { key: 'status', label: 'Status' },
        { key: 'subscribers', label: 'Subscribers' },
        { key: 'total_earnings', label: 'Total Earnings (USD)' },
        { key: 'actions', label: 'Actions' },
    ];

    const StatusBadge = ({ status }) => {
        const styleMap = {
            PRIVATE: "bg-gray-500/20 text-gray-400",
            PENDING: "bg-yellow-500/20 text-yellow-400 animate-pulse",
            APPROVED: "bg-success/20 text-success",
            REJECTED: "bg-danger/20 text-danger",
            ARCHIVED: "bg-gray-600/50 text-gray-500",
        };
        return <span className={clsx("px-2 inline-flex text-xs leading-5 font-semibold rounded-full", styleMap[status])}>{status}</span>;
    };

    return (
        <div className="p-6 animate-fadeIn">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">My Published Strategies</h1>
                <Button size="sm" onClick={() => toast.info("Navigate to the IDE to create and publish a new strategy.")}>
                    <FiPlus className="mr-2"/> Publish New Strategy
                </Button>
            </div>

            <p className="text-text-secondary mb-6 max-w-2xl">
                Manage your strategies submitted to the AuraQuant Marketplace. Track their review status, view performance, and see your earnings.
            </p>

            <Table headers={tableHeaders}>
                {myStrategies.map((strat) => (
                    <tr key={strat.id} className="hover:bg-dark-tertiary">
                        <td className="px-6 py-4 font-medium">{strat.name}</td>
                        <td className="px-6 py-4 text-center">{strat.version}</td>
                        <td className="px-6 py-4"><StatusBadge status={strat.status} /></td>
                        <td className="px-6 py-4 text-center font-mono">{strat.monthly_subs}</td>
                        <td className="px-6 py-4 text-right font-mono text-success">${strat.earnings.toFixed(2)}</td>
                        <td className="px-6 py-4 space-x-2 text-center">
                            <button className="p-2 text-text-secondary hover:text-brand-primary" title="View on Marketplace"><FiEye /></button>
                            <button className="p-2 text-text-secondary hover:text-yellow-400" title="Edit Submission"><FiEdit /></button>
                            <button className="p-2 text-text-secondary hover:text-danger" title="Archive Strategy"><FiArchive /></button>
                        </td>
                    </tr>
                ))}
            </Table>
        </div>
    );
};

export default MyStrategiesPage;