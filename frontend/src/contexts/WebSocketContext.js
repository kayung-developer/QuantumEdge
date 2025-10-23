import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const { isAuthenticated } = useAuth();
    const [accountData, setAccountData] = useState(null);
    const [lastMessage, setLastMessage] = useState(null);
    const webSocketRef = useRef(null); // Use useRef to hold the WebSocket instance

    useEffect(() => {
        // This effect's only job is to manage the WebSocket connection lifecycle.
        // It runs ONLY when `isAuthenticated` changes.

        if (isAuthenticated) {
            // --- CONNECT ---
            const token = localStorage.getItem('accessToken');
            if (!token) return;

            const wsUrl = (process.env.REACT_APP_API_BASE_URL.replace(/^http/, 'ws')) + '/ws?token=' + token;
            const socket = new WebSocket(wsUrl);
            webSocketRef.current = socket; // Store the instance in the ref

            socket.onopen = () => console.log('WebSocket Connected');

            socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    setLastMessage(message);

                    if (message.type === 'account_update') {
                        setAccountData(message.data);
                    } else if (message.type === 'trade_executed') {
                        toast.success(`Trade Executed: ${message.data.action} ${message.data.symbol}`, { icon: '🚀' });
                    } else if (message.type === 'subscription_updated') {
                        toast.success('Your subscription has been updated! Refreshing...', { duration: 4000 });
                        setTimeout(() => window.location.reload(), 4000);
                    }
                } catch (e) {
                    console.error("Failed to parse WebSocket message:", e);
                }
            };

            socket.onerror = (error) => console.error('WebSocket Error:', error);

            socket.onclose = () => {
                console.log('WebSocket Disconnected');
                // Optional: You could add reconnect logic here if desired.
            };

        } else {
            // --- DISCONNECT ---
            if (webSocketRef.current) {
                webSocketRef.current.close();
                webSocketRef.current = null;
            }
        }

        // Cleanup function to run when the component unmounts or `isAuthenticated` changes
        return () => {
            if (webSocketRef.current) {
                webSocketRef.current.close();
                webSocketRef.current = null;
            }
        };
    }, [isAuthenticated]); // The ONLY dependency is the authentication state.

    const value = { accountData, lastMessage };

    return (
        <WebSocketContext.Provider value={value}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    return useContext(WebSocketContext);
};