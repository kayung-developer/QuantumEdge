import React from 'react';
import ToggleSwitch from '../components/common/ToggleSwitch';
import Button from '../components/common/Button';

const AlertSettingsPage = () => {
    // In a real system, this state would be fetched from and saved to the user's profile
    const [alertConfig, setAlertConfig] = React.useState({
        trade_confirmations: true,
        ai_signal_generated: true,
        risk_violation: true,
        slack_enabled: false,
        telegram_enabled: true,
    });

    const handleToggle = (key) => {
        setAlertConfig(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="p-6 animate-fadeIn max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Notification Settings</h1>

            <div className="space-y-6 bg-dark-surface p-6 rounded-lg">
                <h2 className="text-xl font-semibold border-b border-dark-secondary pb-2">Event Alerts</h2>
                <div className="flex justify-between items-center">
                    <label>AI Signal Generated</label>
                    <ToggleSwitch enabled={alertConfig.ai_signal_generated} onChange={() => handleToggle('ai_signal_generated')} />
                </div>
                <div className="flex justify-between items-center">
                    <label>Trade Execution Confirmation</label>
                    <ToggleSwitch enabled={alertConfig.trade_confirmations} onChange={() => handleToggle('trade_confirmations')} />
                </div>
                 <div className="flex justify-between items-center">
                    <label>Risk Rule Violation</label>
                    <ToggleSwitch enabled={alertConfig.risk_violation} onChange={() => handleToggle('risk_violation')} />
                </div>

                <h2 className="text-xl font-semibold border-b border-dark-secondary pb-2 pt-4">Channels</h2>
                <div className="flex justify-between items-center">
                    <label>Enable Slack Notifications</label>
                    <ToggleSwitch enabled={alertConfig.slack_enabled} onChange={() => handleToggle('slack_enabled')} />
                </div>
                 <div className="flex justify-between items-center">
                    <label>Enable Telegram Notifications</label>
                    <ToggleSwitch enabled={alertConfig.telegram_enabled} onChange={() => handleToggle('telegram_enabled')} />
                </div>
                <div className="pt-4 flex justify-end">
                    <Button>Save Preferences</Button>
                </div>
            </div>
        </div>
    );
};

export default AlertSettingsPage;