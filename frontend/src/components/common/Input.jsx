import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { FiAlertCircle } from 'react-icons/fi';

/**
 * A flexible and reusable input component designed to work seamlessly with react-hook-form.
 * It handles labels, icons, and error states gracefully.
 */
const Input = forwardRef(
  ({ id, label, type = 'text', icon: Icon, error, className, ...props }, ref) => {
    const inputContainerClasses = "relative";

    const inputClasses = clsx(
      'w-full bg-dark-surface border rounded-md shadow-sm transition-colors duration-200',
      'placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-brand-primary',
      'py-2 pr-4 text-text-primary',
      {
        'border-dark-secondary focus:border-brand-primary': !error,
        'border-danger focus:border-danger focus:ring-danger': error,
        'pl-10': Icon,
        'pl-4': !Icon,
      },
      props.disabled && 'bg-dark-background cursor-not-allowed text-text-disabled'
    );

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        <div className={inputContainerClasses}>
          {Icon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <Icon className="h-5 w-5 text-text-secondary" aria-hidden="true" />
            </div>
          )}
          <input
            id={id}
            name={id}
            type={type}
            ref={ref}
            className={clsx(inputClasses, className)}
            {...props}
          />
          {error && (
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <FiAlertCircle className="h-5 w-5 text-danger" aria-hidden="true" />
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-danger" id={`${id}-error`}>
            {error.message}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;