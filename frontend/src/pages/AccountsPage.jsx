import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { FiPlus, FiTrash2, FiKey } from 'react-icons/fi';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import ChartSpinner from '../components/common/ChartSpinner';
// import accountService from '../api/accountService'; // Assuming a future service

const AccountsPage = () => {
    // In a real system, this data would be fetched from the /accounts API endpoint
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);

    const mockAccounts = [
        { id: 'uuid-1', account_name: "My Primary Binance", exchange_name: "Binance", is_active: true },
        { id: 'uuid-2', account_name: "MT5 Demo Account", exchange_name: "MetaTrader5", is_active: true },
        { id: 'uuid-3', account_name: "LMAX FIX Connection", exchange_name: "FIXBroker", is_active: false },
    ];

    const fetchAccounts = useCallback(async () => {
        setLoading(true);
        try {
            // const response = await accountService.getAccounts();
            // setAccounts(response.data);
            setAccounts(mockAccounts); // Using mock data
        } catch (error) {
            toast.error("Failed to load connection accounts.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAccounts();
    }, [fetchAccounts]);


    const tableHeaders = [
        { key: 'name', label: 'Account Name' },
        { key: 'exchange', label: 'Exchange/Broker' },
        { key: 'status', label: 'Status' },
        { key: 'actions', label: 'Actions' },
    ];

    if (loading) return <ChartSpinner text="Loading connections..." />;

    return (
        <div className="p-6 animate-fadeIn">
            <div className="flex justify-between items-center mb-4">
                <div>
                    <h2 className="text-xl font-bold text-text-primary">Exchange & Broker Connections</h2>
                    <p className="text-sm text-text-secondary mt-1">
                        Securely manage your API keys for all trading venues.
                    </p>
                </div>
                <Button size="sm"><FiPlus className="mr-2"/> Add New Connection</Button>
            </div>

            <div className="mt-6">
                <Table headers={tableHeaders}>
                    {accounts.map(acc => (
                        <tr key={acc.id} className="hover:bg-dark-tertiary">
                            <td className="px-6 py-4 font-medium text-sm text-text-primary">{acc.account_name}</td>
                            <td className="px-6 py-4 text-sm text-text-secondary">{acc.exchange_name}</td>
                            <td className="px-6 py-4">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${acc.is_active ? 'bg-success/20 text-success' : 'bg-gray-500/20 text-gray-400'}`}>
                                    {acc.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td className="px-6 py-4">
                                <button className="p-2 text-text-secondary hover:text-danger" title="Delete Connection">
                                    <FiTrash2 className="h-4 w-4" />
                                </button>
                            </td>
                        </tr>
                    ))}
                </Table>
            </div>
        </div>
    );
};

export default AccountsPage;