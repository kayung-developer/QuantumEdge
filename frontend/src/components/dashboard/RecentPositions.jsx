import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { FiArrowUpRight, FiArrowDownLeft, FiActivity } from 'react-icons/fi';
import { clsx } from 'clsx';
import { Link } from 'react-router-dom';
import Button from '../common/Button';

/**
 * A widget to display a compact list of the user's most recently opened positions.
 * @param {Array<object>} positions - A list of position objects from the dashboard summary.
 */
const RecentPositions = ({ positions }) => {
    return (
        <div className="bg-dark-surface border border-dark-secondary rounded-lg p-5 h-full flex flex-col">
            <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Open Positions</h3>
            {(!positions || positions.length === 0) ? (
                <div className="flex-grow flex flex-col items-center justify-center text-text-secondary">
                    <FiActivity className="h-12 w-12 mb-4"/>
                    <p>You have no open positions.</p>
                </div>
            ) : (
                <>
                    <ul className="space-y-4 flex-grow">
                        {positions.map((pos) => (
                            <li key={pos.ticket} className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className={clsx("p-2 rounded-full mr-3", pos.type === 'BUY' ? "bg-success/20" : "bg-danger/20")}>
                                        {pos.type === 'BUY' ? <FiArrowUpRight className="text-success" /> : <FiArrowDownLeft className="text-danger" />}
                                    </div>
                                    <div>
                                        <p className="font-bold text-text-primary">{pos.symbol}</p>
                                        <p className="text-xs text-text-secondary">
                                            Opened {formatDistanceToNow(new Date(pos.time), { addSuffix: true })}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                     <p className={clsx("font-semibold font-mono", pos.profit >= 0 ? "text-success" : "text-danger")}>
                                        {pos.profit >= 0 ? '+' : ''}{pos.profit.toFixed(2)}
                                    </p>
                                     <p className="text-xs text-text-secondary">Vol: {pos.volume}</p>
                                </div>
                            </li>
                        ))}
                    </ul>
                    <div className="mt-4 border-t border-dark-secondary pt-4">
                        <Link to="/trading">
                           <Button variant="secondary" size="sm" className="w-full">View All Positions</Button>
                        </Link>
                    </div>
                </>
            )}
        </div>
    );
};

export default RecentPositions;