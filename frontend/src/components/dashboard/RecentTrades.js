import React, { useState, useEffect } from 'react';
import api from 'services/api';
import Skeleton from 'components/core/Skeleton';

const RecentTrades = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const { data } = await api.get('/trade/positions');
        setPositions(data.slice(0, 5)); // Get last 5 trades
      } catch (error) {
        console.error("Failed to fetch recent trades:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPositions();
  }, []);

  if (loading) {
    return (
        <div className="space-y-4">
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
        </div>
    );
  }

  if (positions.length === 0) {
    return <p className="text-gray-500 dark:text-dark-text-secondary text-center py-8">No recent trades found.</p>;
  }

  return (
    <div className="space-y-4">
      {positions.map((pos) => (
        <div key={pos.ticket} className="flex justify-between items-center bg-gray-50 dark:bg-dark-bg p-3 rounded-lg">
          <div>
            <p className="font-bold">{pos.symbol}</p>
            <p className={`text-sm font-medium ${pos.type === 'BUY' ? 'text-blue-500' : 'text-pink-500'}`}>{pos.type}</p>
          </div>
          <div>
            <p className={`font-bold text-right ${pos.profit >= 0 ? 'text-secondary' : 'text-danger'}`}>
              {pos.profit.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 dark:text-dark-text-secondary text-right">{new Date(pos.time).toLocaleTimeString()}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecentTrades;