import React from 'react';
import { clsx } from 'clsx';
import { CgSpinner } from 'react-icons/cg';

/**
 * A highly reusable and themeable button component with variants, sizes, and a loading state.
 * It forms the base for all interactive actions in the application.
 *
 * @param {string} variant - 'primary' for main actions, 'secondary' for alternative actions.
 * @param {string} size - 'sm', 'md', or 'lg'.
 * @param {boolean} isLoading - If true, disables the button and shows a loading spinner.
 * @param {React.ReactNode} children - The content of the button (text, icons).
 * @param {object} props - Any other native button attributes (e.g., onClick, type, disabled, className).
 */
const Button = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-background transition-colors duration-200 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-brand-primary text-white hover:bg-blue-500 focus:ring-brand-primary disabled:bg-brand-primary/50',
    secondary: 'bg-dark-secondary text-text-primary hover:bg-gray-600 focus:ring-dark-secondary disabled:bg-dark-secondary/50 disabled:text-text-disabled',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const finalClassName = clsx(
    baseStyles,
    variantStyles[variant],
    sizeStyles[size],
    className
  );

  return (
    <button
      className={finalClassName}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <>
          <CgSpinner className="animate-spin h-5 w-5 mr-2" />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;