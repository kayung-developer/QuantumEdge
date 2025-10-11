import React, { useState, useEffect } from 'react';
import { Tab } from '@headlessui/react';
import { useForm, FormProvider, useFormContext, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { clsx } from 'clsx';
import toast from 'react-hot-toast';

import Input from '../common/Input';
import Button from '../common/Button';
import useMarketDataStore from '../../store/marketDataStore';
import useOrderStore from '../../store/orderStore';
import tradeService from '../../api/tradeService';
import { FiInfo } from 'react-icons/fi';
import ToggleSwitch from '../common/ToggleSwitch';

// --- Zod Schemas for Advanced Validation ---
const manualOrderSchema = z.object({
  orderType: z.enum(['MARKET', 'LIMIT']),
  amount: z.coerce.number({ invalid_type_error: "Must be a number" }).positive('Amount must be positive'),
  price: z.coerce.number().optional(),
}).refine(data => {
    if (data.orderType === 'LIMIT') {
        return data.price && data.price > 0;
    }
    return true;
}, { message: "Price is required for limit orders", path: ['price'] });

const twapOrderSchema = z.object({
    amount: z.coerce.number({ invalid_type_error: "Must be a number" }).positive('Amount must be positive'),
    duration_minutes: z.coerce.number().int().min(1, 'Duration must be at least 1 minute'),
    num_children: z.coerce.number().int().min(2, 'Must split into at least 2 orders'),
});


// --- Reusable Form Content for Manual Orders ---
const ManualOrderForm = ({ side }) => {
    const { t } = useTranslation();
    const { control, register, watch, setValue, formState: { errors } } = useFormContext();
    const orderType = watch('orderType', 'MARKET');
    const amount = watch('amount');
    const price = watch('price');
    const { currentInstrument } = useMarketDataStore();

    // In a real system, this would come from an API call to the account balance
    const mockBalance = { base: 1.5, quote: 100000 };
    const total = (orderType === 'MARKET' ? 65123.45 : price) * amount; // Use mock market price

    const handleSliderChange = (e) => {
        const percent = e.target.value;
        const balanceToUse = side === 0 ? mockBalance.quote / (price || 65123.45) : mockBalance.base;
        const newAmount = (balanceToUse * (percent / 100)).toFixed(6);
        setValue('amount', newAmount, { shouldValidate: true });
    };

    return (
      <div className="flex flex-col flex-grow space-y-4">
        <Controller
          name="orderType"
          control={control}
          defaultValue="MARKET"
          render={({ field }) => (
            <Tab.Group selectedIndex={field.value === 'MARKET' ? 0 : 1} onChange={(i) => field.onChange(i === 0 ? 'MARKET' : 'LIMIT')}>
              <Tab.List className="flex space-x-4 border-b border-dark-secondary">
                <Tab className={({ selected }) => clsx('py-2 px-1 text-sm font-medium focus:outline-none', selected ? 'border-b-2 border-brand-primary text-text-primary' : 'text-text-secondary')}>
                  {t('trading.marketOrder')}
                </Tab>
                <Tab className={({ selected }) => clsx('py-2 px-1 text-sm font-medium focus:outline-none', selected ? 'border-b-2 border-brand-primary text-text-primary' : 'text-text-secondary')}>
                  {t('trading.limitOrder')}
                </Tab>
              </Tab.List>
            </Tab.Group>
          )}
        />

        {orderType === 'LIMIT' && (
          <Input id="price" label={`Price (${currentInstrument.symbol.split('/')[1]})`} type="number" step="any" error={errors.price} {...register('price')} />
        )}
        <Input id="amount" label={`Amount (${currentInstrument.symbol.split('/')[0]})`} type="number" step="any" error={errors.amount} {...register('amount')} />

        <div>
            <input type="range" min="0" max="100" step="1" onChange={handleSliderChange} className="w-full h-1 bg-dark-secondary rounded-lg appearance-none cursor-pointer range-sm" />
            <div className="flex justify-between text-xs text-text-secondary mt-1">
                <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
            </div>
        </div>

        <div className="border-t border-dark-secondary pt-4 space-y-2 text-sm">
            <div className="flex justify-between text-text-secondary"><span>Available</span><span>{side === 0 ? mockBalance.quote.toFixed(2) : mockBalance.base.toFixed(6)} {side === 0 ? currentInstrument.symbol.split('/')[1] : currentInstrument.symbol.split('/')[0]}</span></div>
            <div className="flex justify-between text-text-secondary"><span>Total</span><span className="text-text-primary font-semibold">{isNaN(total) ? '0.00' : total.toFixed(2)} {currentInstrument.symbol.split('/')[1]}</span></div>
        </div>
      </div>
    );
};


// --- Reusable Form Content for Algorithmic (TWAP) Orders ---
const AlgoOrderForm = () => {
    const { t } = useTranslation();
    const { register, formState: { errors } } = useFormContext();

    return (
        <div className="flex flex-col flex-grow space-y-4">
            <div className="p-3 bg-dark-background rounded-md text-sm text-text-secondary flex items-start space-x-2">
                <FiInfo className="h-4 w-4 mt-0.5 flex-shrink-0 text-brand-primary" />
                <span>A TWAP order splits a large order into smaller market orders and executes them over a set time to minimize price impact.</span>
            </div>
            <Input id="amount" label="Total Amount" type="number" step="any" error={errors.amount} {...register('amount')} />
            <Input id="duration_minutes" label="Duration (minutes)" type="number" error={errors.duration_minutes} {...register('duration_minutes')} />
            <Input id="num_children" label="Number of Orders" type="number" error={errors.num_children} {...register('num_children')} />
        </div>
    );
}


// --- Main Order Panel Component ---
const OrderPanel = () => {
    const { t } = useTranslation();
    const { currentInstrument } = useMarketDataStore();
    const { addOrder } = useOrderStore();

    const [side, setSide] = useState(0); // 0: Buy, 1: Sell
    const [mainTab, setMainTab] = useState(0); // 0: Manual, 1: Algorithmic
    const [isPaperTrade, setIsPaperTrade] = useState(true); // Default to paper trading for safety

    const manualMethods = useForm({ resolver: zodResolver(manualOrderSchema), defaultValues: { orderType: 'MARKET', amount: '', price: ''} });
    const algoMethods = useForm({ resolver: zodResolver(twapOrderSchema), defaultValues: { amount: '', duration_minutes: '', num_children: ''} });

    const { formState: { isSubmitting: isManualSubmitting }, reset: resetManual } = manualMethods;
    const { formState: { isSubmitting: isAlgoSubmitting }, reset: resetAlgo } = algoMethods;

    useEffect(() => {
        setSide(initialSide);
    }, [initialSide]);

    const onManualSubmit = async (data) => {
        const orderDetails = {
            exchange: "auto", // Tell backend to use SOR
            symbol: currentInstrument.symbol.replace('/',''),
            order_type: data.orderType,
            side: side === 0 ? 'BUY' : 'SELL',
            quantity: data.amount,
            price: data.orderType === 'LIMIT' ? data.price : undefined,
            is_algorithmic: false,
        };
        await submitOrder(orderDetails, resetManual);
    };

    const onAlgoSubmit = async (data) => {
        const orderDetails = {
            exchange: "auto", // SOR will decide for each child order
            symbol: currentInstrument.symbol.replace('/',''),
            order_type: "MARKET",
            side: side === 0 ? 'BUY' : 'SELL',
            quantity: data.amount,
            is_algorithmic: true,
            algo_params: {
                duration_minutes: data.duration_minutes,
                num_children: data.num_children,
            },
        };
        await submitOrder(orderDetails, resetAlgo);
    };

    const submitOrder = async (orderDetails, resetAction) => {
        const toastId = toast.loading('Submitting order request...');
        try {
            // --- NEW: Add the paper trade flag to the payload ---
            const finalOrderDetails = {
                ...orderDetails,
                is_paper_trade: isPaperTrade,
            };

            const response = await tradeService.createOrder(finalOrderDetails);
            addOrder(response.data);
            toast.success(`[${isPaperTrade ? 'PAPER' : 'LIVE'}] Order accepted for processing.`, { id: toastId });
            resetAction();
            if (onOrderPlaced) {
                onOrderPlaced();
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Order submission failed.', { id: toastId });
        }
    };

    // Reset forms when switching main tabs to avoid state conflicts
    useEffect(() => {
        resetManual();
        resetAlgo();
    }, [mainTab, resetManual, resetAlgo]);

    return (
        <div className="w-full h-full flex flex-col p-4">
            <div className="flex space-x-2 rounded-xl bg-dark-background p-1 mb-4">
                <button onClick={() => setSide(0)} className={clsx('w-full rounded-lg py-2.5 text-sm font-bold', side === 0 ? 'bg-success text-white shadow-md' : 'text-text-secondary hover:bg-dark-tertiary')}>
                    {t('trading.buy')}
                </button>
                <button onClick={() => setSide(1)} className={clsx('w-full rounded-lg py-2.5 text-sm font-bold', side === 1 ? 'bg-danger text-white shadow-md' : 'text-text-secondary hover:bg-dark-tertiary')}>
                    {t('trading.sell')}
                </button>

            </div>

            <Tab.Group selectedIndex={mainTab} onChange={setMainTab}>
                <Tab.List className="flex space-x-1 rounded-xl bg-dark-background p-1">
                    <Tab className={({ selected }) => clsx('w-full rounded-lg py-2 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary hover:bg-white/[0.12]')}>Manual</Tab>
                    <Tab className={({ selected }) => clsx('w-full rounded-lg py-2 text-sm font-medium', selected ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary hover:bg-white/[0.12]')}>Algorithmic (TWAP)</Tab>
                </Tab.List>
                <Tab.Panels className="mt-4 flex-grow">
                    <Tab.Panel className="h-full focus:outline-none">
                        <FormProvider {...manualMethods}>
                            <form onSubmit={manualMethods.handleSubmit(onManualSubmit)} className="flex flex-col h-full">
                                <ManualOrderForm side={side} />
                                <div className="mt-auto pt-4">
                                    <Button type="submit" isLoading={isManualSubmitting} style={{ backgroundColor: side === 0 ? '#22C55E' : '#EF4444' }} className="w-full">
                                        Place {side === 0 ? 'Buy' : 'Sell'} Order
                                    </Button>
                                </div>
                            </form>
                        </FormProvider>
                    </Tab.Panel>
                    <Tab.Panel className="h-full focus:outline-none">
                        <FormProvider {...algoMethods}>
                           <form onSubmit={algoMethods.handleSubmit(onAlgoSubmit)} className="flex flex-col h-full">
                                <AlgoOrderForm />
                                <div className="mt-auto pt-4">
                                    <Button type="submit" isLoading={isAlgoSubmitting} style={{ backgroundColor: side === 0 ? '#22C55E' : '#EF4444' }} className="w-full">
                                        Execute TWAP Strategy
                                    </Button>
                                </div>
                            </form>
                        </FormProvider>
                    </Tab.Panel>
                </Tab.Panels>
            </Tab.Group>
            <div className="mt-auto pt-4 space-y-4">
                 {/* --- NEW: Live/Paper Trading Toggle --- */}
                <div className="flex items-center justify-center p-2 bg-dark-background rounded-lg">
                     <ToggleSwitch
                        enabled={!isPaperTrade} // Toggle is ON for LIVE
                        onChange={(val) => setIsPaperTrade(!val)}
                        leftLabel="Paper"
                        rightLabel="Live"
                    />
                </div>
            </div>
        </div>
    );
};

export default OrderPanel;