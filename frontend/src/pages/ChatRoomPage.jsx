import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import { FiSend, FiUsers, FiChevronLeft } from 'react-icons/fi';
import Button from '../components/common/Button';
import useAuth from '../hooks/useAuth';
import { clsx } from 'clsx';
import { format } from 'date-fns';

const ChatRoomPage = () => {
    const { roomId } = useParams();
    const { user } = useAuth();
    const { messages, participants, isConnected, sendMessage } = useChat(roomId);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    // In a real system, you'd fetch room details via an API
    const roomName = "Crypto Day Traders";

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        if (input.trim()) {
            sendMessage({ message: input });
            setInput('');
        }
    };

    const renderMessage = (msg) => {
        if (msg.type === 'user_join' || msg.type === 'user_leave') {
            return (
                <div key={msg.id} className="text-center text-xs text-text-secondary my-2">
                    {msg.user_name} has {msg.type === 'user_join' ? 'joined' : 'left'} the room.
                </div>
            );
        }

        const isMe = msg.sender_name === (user.full_name || user.email);
        return (
            <div key={msg.id} className={clsx("flex flex-col", isMe ? "items-end" : "items-start")}>
                <div className={clsx("p-3 rounded-lg max-w-lg", isMe ? "bg-brand-primary text-white" : "bg-dark-tertiary")}>
                    {!isMe && <p className="text-xs font-bold text-brand-primary mb-1">{msg.sender_name}</p>}
                    <p className="text-sm">{msg.content}</p>
                </div>
                <p className="text-xs text-text-secondary mt-1">{format(new Date(msg.timestamp), 'p')}</p>
            </div>
        );
    };

    return (
        <div className="p-6 flex flex-col h-[calc(100vh-8rem)]">
            <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                    <Link to="/trade-rooms" className="mr-4 p-2 hover:bg-dark-surface rounded-full"><FiChevronLeft /></Link>
                    <h1 className="text-2xl font-bold">{roomName}</h1>
                </div>
                <div className="flex items-center text-sm text-text-secondary">
                    <FiUsers className="mr-2"/> {participants.length} Participants
                    <div className={clsx("w-2 h-2 rounded-full ml-2", isConnected ? "bg-success" : "bg-danger")}></div>
                </div>
            </div>
            <div className="flex-grow bg-dark-surface border border-dark-secondary rounded-lg flex flex-col p-4 overflow-y-auto">
                <div className="flex-grow space-y-4 pr-2">
                    {messages.map(renderMessage)}
                    <div ref={messagesEndRef} />
                </div>
                <div className="mt-4 flex items-center space-x-2 border-t border-dark-secondary pt-4">
                    <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && isConnected && handleSend()} placeholder={isConnected ? "Type a message..." : "Connecting..."} className="w-full bg-dark-background p-2 rounded-md focus:ring-2 focus:ring-brand-primary" disabled={!isConnected} />
                    <Button onClick={handleSend} disabled={!isConnected}><FiSend /></Button>
                </div>
            </div>
        </div>
    );
};

export default ChatRoomPage;