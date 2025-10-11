import React, { useEffect } from 'react';
import useSentimentStore from '../../store/sentimentStore';
import useMarketDataStore from '../../store/marketDataStore';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { FiRss } from 'react-icons/fi';

const SentimentFeed = () => {
    const { liveFeed, connect, disconnect } = useSentimentStore();
    const { currentInstrument } = useMarketDataStore();

    useEffect(() => {
        if (currentInstrument) {
            connect(currentInstrument.symbol.replace('/', ''));
        }
        return () => disconnect(); // Disconnect when component unmounts
    }, [currentInstrument, connect, disconnect]);

    return (
        <div className="bg-dark-surface border border-dark-secondary rounded-lg p-4 h-full flex flex-col">
            <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center">
                <FiRss className="mr-2 text-brand-primary"/>
                Live News & Sentiment Feed
            </h3>
            <div className="flex-grow overflow-y-auto space-y-3 pr-2">
                <AnimatePresence>
                    {liveFeed.length === 0 && (
                        <p className="text-text-secondary text-center pt-10">Listening for news...</p>
                    )}
                    {liveFeed.map((item, index) => (
                        <motion.div
                            key={item.headline + index}
                            layout
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-3 bg-dark-tertiary/50 rounded-md"
                        >
                            <div className="flex justify-between items-start">
                                <p className="text-sm text-text-primary pr-4">{item.headline}</p>
                                <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                                    item.sentiment_label === 'positive' ? 'bg-success/20 text-success' :
                                    item.sentiment_label === 'negative' ? 'bg-danger/20 text-danger' :
                                    'bg-gray-500/20 text-text-secondary'
                                }`}>
                                    {item.sentiment_label}
                                </span>
                            </div>
                            <p className="text-xs text-text-secondary mt-1">
                                {item.source} - {formatDistanceToNow(new Date(item.published_at), { addSuffix: true })}
                            </p>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default SentimentFeed;