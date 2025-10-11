import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FiUsers, FiPlus } from 'react-icons/fi';
import Button from '../components/common/Button';
import ChartSpinner from '../components/common/ChartSpinner';
// import collaborationService from '../api/collaborationService';

const TradeRoomsPage = () => {
    const [rooms, setRooms] = useState([]);
    const [loading, setLoading] = useState(true);

    // Mock data, would be fetched from the API
    const mockRooms = [
        { id: '1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed', name: "Crypto Day Traders", members: 128, description: "Active discussion on BTC and ETH intraday moves." },
        { id: '3e9c8c4a-5c2e-4b8a-8c8d-3f4b5c6d7e8f', name: "SMC Disciples", members: 72, description: "Advanced chat for Smart Money Concepts and order flow." },
        { id: 'a1b2c3d4-e5f6-7890-1234-567890abcdef', name: "Forex Majors", members: 215, description: "High-level analysis of EUR/USD, GBP/USD, and USD/JPY." },
    ];

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                // const response = await collaborationService.getPublicRooms();
                // setRooms(response.data);
                setRooms(mockRooms);
            } catch (error) {
                toast.error("Could not fetch trade rooms.");
            } finally {
                setLoading(false);
            }
        };
        fetchRooms();
    }, []);

    if (loading) return <ChartSpinner text="Loading Trade Rooms..." />;

    return (
        <div className="p-6 animate-fadeIn">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-text-primary flex items-center"><FiUsers className="mr-3"/> Trade Rooms</h1>
                <Button size="sm"><FiPlus className="mr-2"/> Create New Room</Button>
            </div>

            <p className="text-text-secondary mb-6 max-w-2xl">
                Join public rooms to collaborate with other traders, share insights, and discuss market-moving events in real-time.
            </p>

            <div className="space-y-4">
                {rooms.map(room => (
                    <div key={room.id} className="bg-dark-surface p-4 rounded-lg border border-dark-secondary transition-all hover:border-brand-primary/50">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-lg text-text-primary">{room.name}</h3>
                                <p className="text-sm text-text-secondary">{room.description}</p>
                            </div>
                            <div className="flex items-center space-x-6">
                                <span className="text-sm text-text-secondary flex items-center">
                                    <FiUsers className="mr-2"/> {room.members} Members
                                </span>
                                <Link to={`/trade-rooms/${room.id}`}>
                                    <Button size="sm">Join Room</Button>
                                </Link>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TradeRoomsPage;