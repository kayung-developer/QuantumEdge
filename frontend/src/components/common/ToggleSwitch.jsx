import React from 'react';
import { Switch } from '@headlessui/react';
import { clsx } from 'clsx';

/**
 * A styled, accessible toggle switch component, often used for boolean settings.
 * @param {boolean} enabled - The current state of the switch.
 * @param {function} onChange - Callback function when the switch is toggled.
 * @param {string} [leftLabel] - Optional label to the left of the switch.
 * @param {string} [rightLabel] - Optional label to the right of the switch.
 */
const ToggleSwitch = ({ enabled, onChange, leftLabel, rightLabel }) => {
    return (
        <div className="flex items-center justify-center space-x-4">
            {leftLabel && <span className={clsx("font-medium text-sm", enabled ? 'text-text-secondary' : 'text-text-primary transition-colors')}>{leftLabel}</span>}
            <Switch
                checked={enabled}
                onChange={onChange}
                className={clsx(
                    'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
                    'focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-offset-2 focus:ring-offset-dark-background',
                    enabled ? 'bg-brand-primary' : 'bg-dark-secondary'
                )}
            >
                <span className="sr-only">Use setting</span>
                <span
                    aria-hidden="true"
                    className={clsx(
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                        enabled ? 'translate-x-5' : 'translate-x-0'
                    )}
                />
            </Switch>
             {rightLabel && <span className={clsx("font-medium text-sm", enabled ? 'text-text-primary transition-colors' : 'text-text-secondary')}>{rightLabel}</span>}
        </div>
    );
};

export default ToggleSwitch;