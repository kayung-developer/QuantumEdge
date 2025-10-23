import React, { useState, useEffect, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { useForm, Controller } from 'react-hook-form';
import { STRATEGIES_CONFIG } from 'config/strategies.config';
import { InformationCircleIcon } from '@heroicons/react/24/outline';
import MultiSelect from 'components/core/MultiSelect';
import { useAuth } from 'contexts/AuthContext';
import { Link } from 'react-router-dom';


const availableTimeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1'];
const StrategyModal = ({ isOpen, onClose, onSubmit, strategy }) => {
  const { user } = useAuth();
  const isEditing = !!strategy;

  // --- THE DEFINITIVE FIX: INTERNAL STATE GUARD ---
  // This state prevents the onClose event from firing during the initial render/transition phase.
  //const [isReady, setIsReady] = useState(false);
  const [isReadyToClose, setIsReadyToClose] = useState(false);

  useEffect(() => {
    let timer;
    if (isOpen) {
      // Set a delay before the modal can be closed by clicking the backdrop.
      // This prevents any stray click events during the opening transition from closing it.
      timer = setTimeout(() => setIsReadyToClose(true), 500); // Increased delay for absolute safety
    } else {
      setIsReadyToClose(false);
    }
    return () => clearTimeout(timer);
  }, [isOpen]);

  // Guarded close handler
  const handleClose = () => {
    // Only allow the modal to be closed if it's in a "ready" state.
    if (isReadyToClose) {
                onClose(); // Only call the real close function if ready
     }
  };
  // --- END OF FIX ---

  const {
    register,
    handleSubmit,
    watch,
    reset,
    control,
    formState: { errors },
  } = useForm();

  const selectedStrategyName = watch("strategy_name", isEditing ? strategy.strategy_name : Object.keys(STRATEGIES_CONFIG)[0]);
  const selectedStrategyConfig = STRATEGIES_CONFIG[selectedStrategyName];

  const hasPremiumAccess = ['premium', 'ultimate', 'business'].includes(user?.subscription?.plan) || user?.role === 'superuser';
  const isSelectedStrategyPremium = selectedStrategyConfig?.isPremium;
  const isCreationDisabled = isSelectedStrategyPremium && !hasPremiumAccess;

  // Effect to reset the form to its default or editing state whenever the modal is opened
  useEffect(() => {
    if (isOpen) {
      if (isEditing && strategy) {
        // Populate form with existing strategy data for editing
        reset({
          strategy_name: strategy.strategy_name,
          symbol: strategy.symbol,
          timeframe: strategy.timeframe,
          ...strategy.parameters,
        });
      } else {
        // Set default values for a new strategy
        const defaultKey = Object.keys(STRATEGIES_CONFIG)[0];
        const defaultConfig = STRATEGIES_CONFIG[defaultKey];
        const defaultParams = defaultConfig.parameters.reduce((acc, param) => {
          acc[param.name] = param.defaultValue;
          return acc;
        }, {});
        reset({
          strategy_name: defaultKey,
          symbol: 'EURUSD',
          timeframe: 'H1',
          ...defaultParams,
        });
      }
    }
  }, [isOpen, isEditing, strategy, reset]);

  // Prepares and sends the data to the parent component's submit handler
  const handleFormSubmit = (data) => {
    const { strategy_name, symbol, timeframe, ...parameters } = data;
    const cleanedParameters = Object.fromEntries(Object.entries(parameters).filter(([_, v]) => v != null));
    const payload = {
      strategy_name,
      symbol: symbol.toUpperCase(),
      timeframe,
      parameters: cleanedParameters,
    };
    onSubmit(payload);
  };

  // Dynamically renders the correct input fields based on the selected strategy's configuration
  const renderParameterFields = () => {
    if (!selectedStrategyConfig) return null;

    return selectedStrategyConfig.parameters.map(param => {
      if (param.type === 'multiselect') {
        return (
          <div key={param.name} className="col-span-2">
            <label className="flex items-center text-sm font-medium text-gray-700 dark:text-dark-text-secondary">{param.label}</label>
            <Controller
              name={`parameters.${param.name}`}
              control={control}
              defaultValue={param.defaultValue}
              rules={{ required: `${param.label} is required.` }}
              render={({ field }) => (
                <MultiSelect
                  options={param.options}
                  value={field.value}
                  onChange={field.onChange}
                />
              )}
            />
            {errors.parameters?.[param.name] && <span className="text-xs text-danger mt-1">{errors.parameters[param.name].message}</span>}
          </div>
        );
      }

      return (
        <div key={param.name}>
          <label htmlFor={`parameters.${param.name}`} className="flex items-center text-sm font-medium text-gray-700 dark:text-dark-text-secondary">
            {param.label || param.name}
            {param.tooltip && (
              <span className="ml-1 group relative">
                <InformationCircleIcon className="h-4 w-4 text-gray-400" />
                <span className="absolute bottom-full z-10 mb-2 w-48 p-2 text-xs text-white bg-gray-900 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                  {param.tooltip}
                </span>
              </span>
            )}
          </label>
          <input
            id={`parameters.${param.name}`}
            type={param.type}
            step={param.step || (param.type === 'number' ? 'any' : undefined)}
            {...register(`parameters.${param.name}`, {
              required: `${param.label || param.name} is required.`,
              valueAsNumber: param.type === 'number',
            })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-dark-border rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-white/50 dark:bg-dark-card/50"
          />
          {errors.parameters?.[param.name] && <span className="text-xs text-danger mt-1">{errors.parameters[param.name].message}</span>}
        </div>
      );
    });
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      {/* --- DEFINITIVE FIX PART 2: Manual Close Control --- */}
      {/* We pass an empty function to onClose to disable Headless UI's default closing behavior. */}
      <Dialog as="div" className="relative z-30" onClose={() => {}}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
          leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
        >
          {/* We add our OWN onClick handler to the overlay. */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => {
              if (isReadyToClose) {
                onClose(); // Only call the real close function if ready
              }
            }}
          />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white dark:bg-dark-card p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title as="h3" className="text-xl font-bold leading-6 text-gray-900 dark:text-white">
                  {isEditing ? 'Edit Strategy' : 'Create New Strategy'}
                </Dialog.Title>

                <form onSubmit={handleSubmit(handleFormSubmit)} className="mt-6 space-y-4">
                  <div>
                    <label htmlFor="strategy_name" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Strategy Type</label>
                    <select
                      id="strategy_name"
                      {...register("strategy_name")}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-800 dark:border-dark-border focus:ring-primary focus:border-primary"
                      disabled={isEditing}
                    >
                      {Object.entries(STRATEGIES_CONFIG).map(([key, config]) => {
                        const isOptionDisabled = config.isPremium && !hasPremiumAccess;
                        return (
                          <option key={key} value={key} disabled={isOptionDisabled} className={isOptionDisabled ? 'text-gray-400' : ''}>
                            {config.name} {config.isPremium ? '⭐' : ''} {isOptionDisabled ? '(Upgrade Required)' : ''}
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="symbol" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Symbol</label>
                      <input id="symbol" {...register("symbol", { required: "Symbol is required." })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-800 dark:border-dark-border focus:ring-primary focus:border-primary" />
                      {errors.symbol && <span className="text-xs text-danger mt-1">{errors.symbol.message}</span>}
                    </div>
                    <div>
                      <label htmlFor="timeframe" className="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">Timeframe</label>
                      <select
                                id="timeframe"
                                {...register("timeframe", { required: true })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm dark:bg-gray-800 dark:border-dark-border focus:ring-primary focus:border-primary"
                            >
                                {availableTimeframes.map(tf => <option key={tf} value={tf}>{tf}</option>)}
                            </select>
                    </div>
                  </div>

                  <hr className="dark:border-dark-border/50 my-2" />
                  <h4 className="text-md font-semibold text-light-text dark:text-dark-text">Parameters</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {renderParameterFields()}
                  </div>

                  {isCreationDisabled && !isEditing && (
                    <div className="mt-4 p-4 bg-yellow-100/50 dark:bg-yellow-900/20 border border-yellow-400/50 rounded-lg text-center text-sm text-yellow-800 dark:text-yellow-300">
                      This is a premium strategy. Please <Link to="/billing" className="font-bold underline hover:text-yellow-600" onClick={onClose}>upgrade your plan</Link> to create it.
                    </div>
                  )}

                  <div className="mt-8 flex justify-end space-x-4">
                    <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">Cancel</button>
                    <button
                      type="submit"
                      disabled={isCreationDisabled && !isEditing}
                      className="px-6 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-700 rounded-md shadow-sm transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed dark:disabled:bg-gray-600"
                    >
                      {isEditing ? 'Save Changes' : 'Create Strategy'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default StrategyModal;