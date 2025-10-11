import React, { useState, useEffect } from 'react';
import useMarketDataStore from '../store/marketDataStore';
import InstrumentSelector from '../components/trading/InstrumentSelector';
import TradesPanel from '../components/trading/TradesPanel';
import AdvancedChart from '../components/charts/AdvancedChart';
import AIPatternIndicator from '../components/trading/AIPatternIndicator';
import OrderBookHeatmap from '../components/trading/OrderBookHeatmap';
import OrderPanel from '../components/trading/OrderPanel';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';

// A sub-component for the trade action buttons
const TradeControlPanel = ({ onBuyClick, onSellClick }) => {
    return (
        <div className="bg-dark-surface border border-dark-secondary rounded-lg p-4 h-full flex flex-col justify-between">
            <div>
                <h3 className="text-sm font-semibold text-text-primary mb-4">New Order</h3>
                <p className="text-xs text-text-secondary">
                    Select an action to open the trade ticket. You can choose between live or paper trading inside the ticket.
                </p>
            </div>
            <div className="space-y-3">
                <Button onClick={onBuyClick} className="w-full bg-success hover:bg-green-600 text-white font-bold">
                    Buy
                </Button>
                <Button onClick={onSellClick} className="w-full bg-danger hover:bg-red-600 text-white font-bold">
                    Sell
                </Button>
            </div>
        </div>
    );
};

/**
 * The main page for the "AI Smart Trading" interface. This is the central hub
 * for manual and AI-assisted trading, combining all the core trading components.
 */
const TradingPage = () => {
    const { fetchKlineToRender, currentInstrument } = useMarketDataStore();
    const [isOrderPanelOpen, setIsOrderPanelOpen] = useState(false);
    const [initialSide, setInitialSide] = useState(0); // 0 for Buy, 1 for Sell

    useEffect(() => {
        // Fetch initial chart data when the component mounts or the instrument changes
        fetchKlineToRender();
    }, [fetchKlineToRender, currentInstrument]);

    const openOrderPanel = (side) => {
        setInitialSide(side);
        setIsOrderPanelOpen(true);
    };

    const closeOrderPanel = () => {
        setIsOrderPanelOpen(false);
    };

    return (
        <>
            <Modal isOpen={isOrderPanelOpen} onClose={closeOrderPanel} title={`New Trade: ${currentInstrument.symbol}`}>
                <OrderPanel
                    initialSide={initialSide}
                    onOrderPlaced={closeOrderPanel}
                />
            </Modal>

            <div className="w-full h-[calc(100vh-8rem)] animate-fadeIn">
                <div className="grid grid-cols-12 grid-rows-12 gap-4 h-full">

                    <div className="col-span-12 lg:col-span-9 row-span-2 bg-dark-surface border border-dark-secondary rounded-lg flex items-center p-4">
                        <InstrumentSelector />
                        <div className="ml-6">
                            <h2 className="text-2xl font-bold text-text-primary">65,123.45</h2>
                            <p className="text-sm text-success">+1,234.56 (+1.90%)</p>
                        </div>
                    </div>

                    <div className="col-span-12 lg:col-span-9 row-span-1">
                        <AIPatternIndicator />
                    </div>

                    <div className="col-span-12 lg:col-span-9 row-span-6 bg-dark-surface border border-dark-secondary rounded-lg p-1">
                        <AdvancedChart />
                    </div>

                    <div className="col-span-12 lg:col-span-3 row-span-9">
                        <OrderBookHeatmap />
                    </div>

                    <div className="col-span-12 lg:col-span-3 row-span-3">
                        <TradeControlPanel
                            onBuyClick={() => openOrderPanel(0)}
                            onSellClick={() => openOrderPanel(1)}
                        />
                    </div>

                    <div className="col-span-12 lg:col-span-9 row-span-3">
                       <TradesPanel />
                    </div>
                </div>
            </div>
        </>
    );
};

export default TradingPage;