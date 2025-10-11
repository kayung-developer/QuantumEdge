import React, { useState, useEffect, useMemo } from 'react';
import orderBookService from '../../api/orderBookService';
import useMarketDataStore from '../../store/marketDataStore';
import { motion } from 'framer-motion';

const OrderBookHeatmap = () => {
    const { currentInstrument } = useMarketDataStore();
    const [orderBook, setOrderBook] = useState({ bids: [], asks: [] });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!currentInstrument) return;

        const symbol = currentInstrument.symbol.replace('/', '');

        const fetchBook = async () => {
            try {
                const response = await orderBookService.getSnapshot(symbol);
                setOrderBook(response.data);
            } catch (error) {
                // Don't show toast errors for a rapidly polling component
                console.error("Failed to fetch order book snapshot");
            } finally {
                setIsLoading(false);
            }
        };

        const interval = setInterval(fetchBook, 1000); // Poll every second for new snapshots
        return () => clearInterval(interval);
    }, [currentInstrument]);

    const { bids, asks, maxCumulative } = useMemo(() => {
        let cumulativeBids = 0;
        const processedBids = orderBook.bids.map(([price, qty]) => {
            cumulativeBids += parseFloat(qty);
            return { price: parseFloat(price), qty: parseFloat(qty), cumulative: cumulativeBids };
        });

        let cumulativeAsks = 0;
        const processedAsks = orderBook.asks.map(([price, qty]) => {
            cumulativeAsks += parseFloat(qty);
            return { price: parseFloat(price), qty: parseFloat(qty), cumulative: cumulativeAsks };
        });

        const maxCumulative = Math.max(cumulativeBids, cumulativeAsks, 1); // Avoid division by zero
        return { bids: processedBids, asks: processedAsks.reverse(), maxCumulative };
    }, [orderBook]);

    const Row = ({ type, price, qty, cumulative }) => {
        const width = (cumulative / maxCumulative) * 100;
        const isBid = type === 'bid';

        return (
            <div className="relative grid grid-cols-3 text-xs font-mono h-5 items-center">
                <motion.div
                    className={`absolute h-full ${isBid ? 'bg-success/20 right-0' : 'bg-danger/20 left-0'}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${width}%` }}
                    transition={{ duration: 0.2, ease: "easeInOut" }}
                />
                <span className={`z-10 ${isBid ? 'text-success' : 'text-danger'}`}>{price.toFixed(2)}</span>
                <span className="z-10 text-right">{qty.toFixed(4)}</span>
                <span className="z-10 text-right text-text-secondary">{cumulative.toFixed(4)}</span>
            </div>
        );
    };

    return (
        <div className="bg-dark-surface border border-dark-secondary rounded-lg p-2 h-full flex flex-col">
            <h3 className="text-sm font-semibold text-text-primary mb-2 px-2">Order Book</h3>
            <div className="grid grid-cols-3 text-xs text-text-secondary px-2 mb-1">
                <span>Price (USD)</span><span className="text-right">Amount</span><span className="text-right">Total</span>
            </div>
            <div className="flex-grow overflow-y-auto">
                {/* Asks (Sell Orders) */}
                <div className="flex flex-col-reverse">
                    {asks.slice(0, 20).map(ask => <Row key={ask.price} type="ask" {...ask} />)}
                </div>

                {/* Spread */}
                <div className="text-center font-bold text-lg my-1 py-1 border-y border-dark-secondary">
                    {asks.length > 0 && bids.length > 0 ? (asks[0].price - bids[0].price).toFixed(2) : '-'}
                </div>

                {/* Bids (Buy Orders) */}
                <div>
                    {bids.slice(0, 20).map(bid => <Row key={bid.price} type="bid" {...bid} />)}
                </div>
            </div>
        </div>
    );
};

export default OrderBookHeatmap;