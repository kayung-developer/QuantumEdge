import React, { useState, useRef, useEffect } from 'react';
import { useAssistant } from '../hooks/useAssistant';
import { FiSend, FiUser, FiCpu } from 'react-icons/fi';
import Button from '../components/common/Button';
import Markdown from 'react-markdown';
import { clsx } from 'clsx';
import remarkGfm from 'remark-gfm'; // For tables

const AssistantPage = () => {
    const { messages, isConnected, isThinking, sendMessage } = useAssistant();
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (input.trim()) {
            sendMessage(input);
            setInput('');
        }
    };

    const suggestionPrompts = [
        "Run a backtest for smc_order_block on BTCUSDT from 2023-01-01 to 2023-06-30 on the 4H timeframe.",
        "Get me the historical price for ETHUSDT for the last 30 days on the 1D timeframe.",
        "Compare the Sharpe ratio of momentum_crossover vs bb_mean_reversion on EURUSD for 2023."
    ];

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] p-4">
            <h1 className="text-3xl font-bold text-text-primary mb-4 flex items-center">
                <FiCpu className="mr-3 text-brand-primary"/> AI Research Assistant
            </h1>
            <div className="flex-grow bg-dark-surface border border-dark-secondary rounded-lg flex flex-col p-4 overflow-y-auto">
                <div className="flex-grow space-y-6">
                    {messages.map((msg) => (
                        <div key={msg.id} className={clsx("flex items-start space-x-4", msg.sender === 'user' && 'justify-end')}>
                            {msg.sender === 'ai' && <div className="p-2 bg-dark-tertiary rounded-full"><FiCpu className="h-5 w-5 text-brand-primary flex-shrink-0"/></div>}
                            <div className={clsx('p-4 rounded-lg max-w-2xl prose prose-sm prose-invert max-w-none', msg.sender === 'ai' ? 'bg-dark-tertiary' : 'bg-brand-primary text-white')}>
                                <Markdown remarkPlugins={[remarkGfm]}>{msg.text}</Markdown>
                            </div>
                            {msg.sender === 'user' && <div className="p-2 bg-dark-tertiary rounded-full"><FiUser className="h-5 w-5 text-text-secondary flex-shrink-0"/></div>}
                        </div>
                    ))}
                    {isThinking && (
                        <div className="flex items-start space-x-4">
                           <div className="p-2 bg-dark-tertiary rounded-full"><FiCpu className="h-5 w-5 text-brand-primary flex-shrink-0"/></div>
                           <div className="p-4 rounded-lg bg-dark-tertiary flex items-center space-x-2">
                                <div className="w-2 h-2 bg-text-secondary rounded-full animate-pulse [animation-delay:-0.3s]"></div>
                                <div className="w-2 h-2 bg-text-secondary rounded-full animate-pulse [animation-delay:-0.15s]"></div>
                                <div className="w-2 h-2 bg-text-secondary rounded-full animate-pulse"></div>
                           </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {messages.length <= 1 && !isThinking && (
                    <div className="my-4">
                        <p className="text-sm text-text-secondary mb-2">Try asking something like:</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                            {suggestionPrompts.slice(0, 3).map((prompt, i) => (
                                <button key={i} onClick={() => setInput(prompt)} className="p-2 text-left bg-dark-tertiary rounded hover:bg-dark-secondary/50 text-xs text-text-secondary">
                                    "{prompt}"
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="mt-4 flex items-center space-x-2 border-t border-dark-secondary pt-4">
                    <input
                        type="text" value={input} onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !isThinking && handleSend()}
                        placeholder={isConnected ? "Ask me anything..." : "Connecting to assistant..."}
                        className="w-full bg-dark-background border border-dark-secondary rounded-md p-2 focus:ring-2 focus:ring-brand-primary"
                        disabled={!isConnected || isThinking}
                    />
                    <Button onClick={handleSend} disabled={!isConnected || isThinking} isLoading={isThinking}>
                        <FiSend />
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default AssistantPage;