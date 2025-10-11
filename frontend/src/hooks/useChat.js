import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

const WEBSOCKET_BASE_URL = `${import.meta.env.VITE_API_BASE_URL.replace('http', 'ws')}/collaboration/rooms`;

/**
 * A custom hook to manage the WebSocket connection and state for a specific Trade Room.
 *
 * @param {string} roomId - The UUID of the trade room to connect to.
 * @returns {object} An object containing:
 *   - messages: Array of chat messages.
 *   - participants: Array of user names currently in the room.
 *   - isConnected: Boolean indicating connection status.
 *   - sendMessage: Function to send a chat message.
 */
export const useChat = (roomId) => {
    const [messages, setMessages] = useState([]);
    const [participants, setParticipants] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef(null);

    const connect = useCallback(() => {
        if (!roomId) return;

        const token = localStorage.getItem('accessToken');
        if (!token) {
            console.error("No auth token found for chat WebSocket connection.");
            return;
        }

        if (ws.current && ws.current.readyState === WebSocket.OPEN) return;

        const socketUrl = `${WEBSOCKET_BASE_URL}/${roomId}/ws?token=${token}`;
        ws.current = new WebSocket(socketUrl);

        ws.current.onopen = () => {
            console.log(`Chat WebSocket connected for room ${roomId}.`);
            setIsConnected(true);
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messageWithId = { ...data, id: uuidv4() };

            // Handle system messages (like joins/leaves) vs. user chat messages
            if (data.type === 'user_join') {
                setParticipants(prev => [...new Set([...prev, data.user_name])]); // Use Set to avoid duplicates
                setMessages(prev => [...prev, messageWithId]);
            } else if (data.type === 'user_leave') {
                setParticipants(prev => prev.filter(name => name !== data.user_name));
                setMessages(prev => [...prev, messageWithId]);
            } else if (data.type === 'new_message') {
                setMessages(prev => [...prev, messageWithId]);
            }
        };

        ws.current.onerror = (error) => {
            console.error(`Chat WebSocket error for room ${roomId}:`, error);
            toast.error("Connection to trade room lost.");
            setIsConnected(false);
        };

        ws.current.onclose = () => {
            console.log("Chat WebSocket disconnected.");
            setIsConnected(false);
        };
    }, [roomId]);

    useEffect(() => {
        connect();
        return () => {
            ws.current?.close();
        };
    }, [connect]);

    const sendMessage = (messagePayload) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(messagePayload));
        } else {
            toast.error("Not connected to the trade room.");
        }
    };

    return { messages, participants, isConnected, sendMessage };
};