import React, { useState, useEffect, useMemo } from 'react';
import { Tab, Disclosure } from '@headlessui/react';
import { clsx } from 'clsx';
import { FiActivity, FiArchive, FiClock, FiChevronRight, FiGitMerge } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

import tradeService from '../../api/tradeService';
import useOrderStore from '../../store/orderStore';
import Table from '../common/Table';
import ChartSpinner from '../common/ChartSpinner';

// --- Sub-component for Open Positions (Complete) ---
const PositionsTable = () => {
    const [positions, setPositions] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const fetchPositions = async () => { try { const response = await tradeService.getOpenPositions(); setPositions(response.data); } catch (error) { console.error(error); toast.error("Could not load open positions."); } finally { setLoading(false); } };
        fetchPositions(); const interval = setInterval(fetchPositions, 5000); return () => clearInterval(interval);
    }, []);
    const headers = [{ key: 'symbol', label: 'Symbol' }, { key: 'type', label: 'Type' }, { key: 'volume', label: 'Volume' }, { key: 'open_price', label: 'Open Price' }, { key: 'profit', label: 'Profit' }];
    if (loading) return <ChartSpinner text="Loading positions..." />;
    if (positions.length === 0) return <p className="p-4 text-center text-text-secondary">No open positions.</p>;
    return ( <Table headers={headers}>{positions.map(pos => ( <tr key={pos.ticket} className="hover:bg-dark-tertiary text-sm"><td className="px-4 py-2 font-bold">{pos.symbol}</td><td className={`px-4 py-2 font-bold ${pos.type === 'BUY' ? 'text-success' : 'text-danger'}`}>{pos.type}</td><td className="px-4 py-2 font-mono">{pos.volume}</td><td className="px-4 py-2 font-mono">{pos.price_open.toFixed(2)}</td><td className={`px-4 py-2 font-mono ${pos.profit >= 0 ? 'text-success' : 'text-danger'}`}>{pos.profit.toFixed(2)}</td></tr> ))}</Table> );
};

// --- Sub-component for Orchestrated Orders (Complete) ---
const OrdersTable = () => {
    const { orders, startPolling } = useOrderStore();
    useEffect(() => { startPolling(); }, [startPolling]);

    const { parentOrders, regularOrders, childOrdersByParent } = useMemo(() => {
        const parentOrders = orders.filter(o => o.is_algorithmic);
        const regularOrders = orders.filter(o => !o.is_algorithmic && !o.parent_order_id);
        const childOrdersByParent = orders.reduce((acc, o) => { if (o.parent_order_id) { if (!acc[o.parent_order_id]) acc[o.parent_order_id] = []; acc[o.parent_order_id].push(o); } return acc; }, {});
        return { parentOrders, regularOrders, childOrdersByParent };
    }, [orders]);

    const headers = [{ key: 'mode', label: 'Mode' }, { key: 'exchange', label: 'Exchange' }, { key: 'symbol', label: 'Symbol' }, { key: 'type', label: 'Type' }, { key: 'side', label: 'Side' }, { key: 'price', label: 'Price' }, { key: 'amount', label: 'Amount' }, { key: 'filled', label: 'Filled' }, { key: 'status', label: 'Status' }];

    const StatusBadge = ({ status }) => { const styleMap = { PENDING_SUBMIT: "bg-gray-500/20 text-gray-400", SUBMITTED: "bg-blue-500/20 text-blue-400 animate-pulse", ACCEPTED: "bg-yellow-500/20 text-yellow-400", PARTIALLY_FILLED: "bg-purple-500/20 text-purple-400", FILLED: "bg-success/20 text-success", CANCELED: "bg-gray-600/50 text-gray-500", REJECTED: "bg-danger/20 text-danger", ERROR: "bg-danger/40 text-danger" }; return <span className={clsx("px-2 inline-flex text-xs leading-5 font-semibold rounded-full", styleMap[status])}>{status.replace('_', ' ')}</span>; };

    // --- THIS IS THE COMPLETE, UNABRIDGED OrderRow COMPONENT ---
    const OrderRow = ({ order }) => (
        <tr className="hover:bg-dark-tertiary font-mono text-xs">
            <td className="px-4 py-2 text-center"><span className={clsx("font-sans font-bold text-xs px-2 py-0.5 rounded-full", order.is_paper_trade ? "bg-blue-500/20 text-blue-400" : "bg-orange-500/20 text-orange-400")}>{order.is_paper_trade ? "PAPER" : "LIVE"}</span></td>
            <td className="px-4 py-2 text-text-secondary">{order.exchange}</td>
            <td className="px-4 py-2 font-sans font-bold text-text-primary">{order.symbol}</td>
            <td className="px-4 py-2 text-text-secondary">{order.order_type}</td>
            <td className={clsx("px-4 py-2 font-bold", order.side === 'BUY' ? 'text-success' : 'text-danger')}>{order.side}</td>
            <td className="px-4 py-2 text-text-primary">{order.price?.toFixed(2) || 'Market'}</td>
            <td className="px-4 py-2 text-text-primary">{order.quantity_requested}</td>
            <td className="px-4 py-2 text-text-secondary">{order.quantity_filled}</td>
            <td className="px-4 py-2"><StatusBadge status={order.status} /></td>
        </tr>
    );

    const ParentOrderDisclosure = ({ order }) => {
        const children = childOrdersByParent[order.id] || [];
        const filledChildren = children.filter(c => c.status === 'FILLED').length;
        const totalChildren = order.metadata?.algo_params?.num_children || children.length || 1;
        const progress = (filledChildren / totalChildren) * 100;
        return ( <tbody className="bg-dark-tertiary/20"><Disclosure as="tr" key={order.id}>{({ open }) => (<><td className="px-2 py-1" colSpan={9}><Disclosure.Button className="w-full flex justify-between items-center text-left p-2 rounded-md hover:bg-dark-tertiary"><div className="flex items-center space-x-3"><FiChevronRight className={clsx("h-5 w-5", { "rotate-90": open })} /><FiGitMerge className="h-5 w-5 text-brand-primary" /><div><p className="font-bold text-text-primary text-sm">TWAP {order.side} {order.symbol}</p><p className="text-xs text-text-secondary">Total: {order.quantity_requested}, Progress: {filledChildren}/{totalChildren}</p></div></div><div className="w-1/3 flex items-center space-x-2"><div className="w-full bg-dark-background rounded-full h-2"><div className="bg-brand-primary h-2 rounded-full" style={{ width: `${progress}%` }}></div></div><span className="text-xs font-mono">{progress.toFixed(0)}%</span></div></Disclosure.Button></td></>)}</Disclosure>{children.map(child => <OrderRow order={child} key={child.id} />)}</tbody> );
    };

    if (orders.length === 0) return <p className="p-4 text-center text-text-secondary">No open orders.</p>;
    return ( <Table headers={headers}>{parentOrders.map(order => <ParentOrderDisclosure order={order} key={order.id} />)}{regularOrders.map(order => <OrderRow order={order} key={order.id} />)}</Table> );
};

// --- Sub-component for Trade History (Complete) ---
const HistoryTable = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(endDate.getDate() - 30); // Fetch last 30 days

                const response = await tradeService.getTradeHistory({
                    start_date: startDate.toISOString(),
                    end_date: endDate.toISOString(),
                });
                setHistory(response.data);
            } catch (error) {
                console.error("Failed to fetch trade history:", error);
                toast.error("Could not load trade history.");
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const headers = [
        { key: 'time', label: 'Time' }, { key: 'symbol', label: 'Symbol' },
        { key: 'type', label: 'Type' }, { key: 'volume', label: 'Volume' },
        { key: 'price', label: 'Price' }, { key: 'profit', label: 'Profit' },
    ];

    if (loading) return <ChartSpinner text="Loading history..." />;
    if (history.length === 0) return <p className="p-4 text-center text-text-secondary">No trade history found in the last 30 days.</p>;

    return (
        <Table headers={headers}>
             {history.map(deal => (
                <tr key={deal.ticket} className="hover:bg-dark-tertiary text-sm">
                    <td className="px-4 py-2 text-xs text-text-secondary">{format(new Date(deal.time), 'yyyy.MM.dd HH:mm')}</td>
                    <td className="px-4 py-2 font-bold">{deal.symbol}</td>
                    <td className={`px-4 py-2 font-bold ${deal.type === 'BUY' ? 'text-success' : 'text-danger'}`}>{deal.type}</td>
                    <td className="px-4 py-2 font-mono">{deal.volume}</td>
                    <td className="px-4 py-2 font-mono">{deal.price.toFixed(2)}</td>
                    <td className={`px-4 py-2 font-mono ${deal.profit >= 0 ? 'text-success' : 'text-danger'}`}>{deal.profit.toFixed(2)}</td>
                </tr>
            ))}
        </Table>
    );
};


// --- Main Trades Panel Component ---
const TradesPanel = () => {
    const { t } = useTranslation();
    const tabs = [ { name: t('trading.positions'), icon: FiActivity, component: <PositionsTable /> }, { name: t('trading.openOrders'), icon: FiClock, component: <OrdersTable /> }, { name: t('trading.tradeHistory'), icon: FiArchive, component: <HistoryTable /> } ];
    return ( <div className="w-full h-full bg-dark-surface border border-dark-secondary rounded-lg flex flex-col"><Tab.Group><Tab.List className="flex space-x-1 rounded-t-lg bg-dark-background p-1 flex-shrink-0">{tabs.map((tab) => ( <Tab key={tab.name} className={({ selected }) => clsx('w-full rounded-lg py-2.5 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary shadow' : 'text-text-secondary hover:bg-white/[0.12]')}> <span className="flex items-center justify-center"><tab.icon className="w-4 h-4 mr-2" />{tab.name}</span> </Tab> ))}</Tab.List><Tab.Panels className="flex-grow overflow-y-auto">{tabs.map((tab, idx) => ( <Tab.Panel key={idx} className="h-full w-full focus:outline-none"><div className="relative h-full w-full">{tab.component}</div></Tab.Panel> ))}</Tab.Panels></Tab.Group></div> );
};

export default TradesPanel;