import React from 'react';
import { FiTrendingUp, FiTrendingDown, FiZap, FiHelpCircle,  FiZapOff } from 'react-icons/fi';

const RegimeStrategyCard = ({ regime, allStrategies, selectedStrategy, onStrategyChange }) => {
    // These characteristics would ideally be fetched from the backend,
    // which would analyze the trained HMM model's properties.
    const mockRegimeDetails = {
        0: { name: "Low-Volatility Bull", description: "Slow, grinding upward trend.", icon: <FiTrendingUp className="text-success"/> },
        1: { name: "High-Volatility Bull", description: "Strong, explosive upward moves.", icon: <FiZap className="text-success"/> },
        2: { name: "Low-Volatility Bear", description: "Slow, grinding downward trend.", icon: <FiTrendingDown className="text-danger"/> },
        3: { name: "High-Volatility Chop/Bear", description: "Erratic, high-volume sideways or downward moves.", icon: <FiZapOff className="text-yellow-500"/> },
    };

    const details = mockRegimeDetails[regime.id] || { name: "Unknown Regime", description: "No description available.", icon: <FiHelpCircle /> };

    return (
        <div className="bg-dark-tertiary/50 p-4 rounded-lg border border-dark-secondary transition-all hover:border-brand-primary/50">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <div className="text-2xl">{details.icon}</div>
                    <div>
                        <h4 className="font-bold text-text-primary">Regime {regime.id}: {details.name}</h4>
                        <p className="text-xs text-text-secondary">{details.description}</p>
                    </div>
                </div>
            </div>
            <div className="mt-4">
                 <select
                    value={selectedStrategy || ""}
                    onChange={(e) => onStrategyChange(regime.id, e.target.value)}
                    className="w-full bg-dark-background border border-dark-secondary rounded-md p-2 text-sm text-text-primary focus:ring-2 focus:ring-brand-primary focus:border-brand-primary"
                >
                    <option value="">-- Deactivate for this Regime --</option>
                    {allStrategies.map(strategy => (
                        <option key={strategy.id} value={strategy.id}>
                            {strategy.name}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
};

export default RegimeStrategyCard;