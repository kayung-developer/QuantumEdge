import { useState, useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

const WEBSOCKET_URL = `${import.meta.env.VITE_API_BASE_URL.replace('http', 'ws')}/assistant/ws`;

/**
 * A custom hook to manage the complex state and lifecycle of the
 * AI Research Assistant's WebSocket connection.
 *
 * @returns {object} An object containing:
 *   - messages: Array of conversation messages.
 *   - isConnected: Boolean indicating the WebSocket connection status.
 *   - isThinking: Boolean indicating if the AI is currently processing a response.
 *   - sendMessage: Function to send a query to the AI assistant.
 */
export const useAssistant = () => {
    const [messages, setMessages] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const ws = useRef(null);

    const connect = useCallback(() => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            console.error("No auth token found for assistant WebSocket connection.");
            return;
        }

        // Prevent multiple connections
        if (ws.current && ws.current.readyState === WebSocket.OPEN) return;

        ws.current = new WebSocket(`${WEBSOCKET_URL}?token=${token}`);

        ws.current.onopen = () => {
            console.log("Assistant WebSocket connected.");
            setIsConnected(true);
            setMessages([{ sender: 'ai', text: 'Hello! How can I help you with your research today? (e.g., "Run a backtest for smc_order_block on BTCUSDT")', id: uuidv4() }]);
        };

        ws.current.onmessage = (event) => {
            setMessages(prev => [...prev, { sender: 'ai', text: event.data, id: uuidv4() }]);
            setIsThinking(false);
        };

        ws.current.onerror = (error) => {
            console.error("Assistant WebSocket error:", error);
            toast.error("AI Assistant connection failed.");
            setIsConnected(false);
            setIsThinking(false);
        };

        ws.current.onclose = () => {
            console.log("Assistant WebSocket disconnected.");
            setIsConnected(false);
            setIsThinking(false);
        };
    }, []);

    useEffect(() => {
        // Initiate connection on mount
        connect();

        // Cleanup function to close the connection when the component unmounts
        return () => {
            ws.current?.close();
        };
    }, [connect]);

    const sendMessage = (message) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            setMessages(prev => [...prev, { sender: 'user', text: message, id: uuidv4() }]);
            setIsThinking(true);
            ws.current.send(message);
        } else {
            toast.error("Cannot send message. AI Assistant is not connected.");
            // Optionally, try to reconnect
            connect();
        }
    };

    return { messages, isConnected, isThinking, sendMessage };
};