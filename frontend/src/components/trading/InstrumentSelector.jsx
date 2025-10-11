import React, { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { FiChevronDown } from 'react-icons/fi';
import { clsx } from 'clsx';
import useMarketDataStore from '../../store/marketDataStore';
import { SiBitcoincash, SiEthereum } from 'react-icons/si';
import { FaDollarSign, FaYenSign, FaPoundSign, FaCoins } from 'react-icons/fa';

// A simple utility to get a representative icon for a trading symbol
const getIconForSymbol = (symbol) => {
    if (symbol.includes('BTC')) return <SiBitcoincash className="h-5 w-5 text-yellow-500" />;
    if (symbol.includes('ETH')) return <SiEthereum className="h-5 w-5 text-gray-400" />;
    if (symbol.includes('EUR')) return <FaDollarSign className="h-5 w-5 text-blue-400" />;
    if (symbol.includes('GBP')) return <FaPoundSign className="h-5 w-5 text-red-400" />;
    if (symbol.includes('JPY')) return <FaYenSign className="h-5 w-5 text-green-400" />;
    return <FaCoins className="h-5 w-5 text-gray-500" />;
}

/**
 * A dropdown component that allows the user to select the active trading instrument.
 * It is connected to the global marketDataStore.
 */
const InstrumentSelector = () => {
    const { instruments, currentInstrument, setCurrentInstrument } = useMarketDataStore();

    return (
        <Menu as="div" className="relative inline-block text-left">
            <div>
                <Menu.Button className="inline-flex w-full justify-center items-center rounded-md bg-dark-tertiary px-4 py-2 text-lg font-bold text-text-primary hover:bg-opacity-80 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">
                    <span className="mr-3">{getIconForSymbol(currentInstrument.symbol)}</span>
                    {currentInstrument.symbol}
                    <FiChevronDown className="ml-2 -mr-1 h-5 w-5 text-text-secondary" aria-hidden="true" />
                </Menu.Button>
            </div>
            <Transition as={Fragment} enter="transition ease-out duration-100" enterFrom="transform opacity-0 scale-95" enterTo="transform opacity-100 scale-100" leave="transition ease-in duration-75" leaveFrom="transform opacity-100 scale-100" leaveTo="transform opacity-0 scale-95">
                <Menu.Items className="absolute left-0 mt-2 w-64 origin-top-left divide-y divide-dark-secondary rounded-md bg-dark-surface shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-20">
                    <div className="px-1 py-1 ">
                        {instruments.map((instrument) => (
                            <Menu.Item key={instrument.symbol}>
                                {({ active }) => (
                                    <button
                                        onClick={() => setCurrentInstrument(instrument)}
                                        className={clsx('group flex w-full items-center rounded-md px-2 py-2 text-sm', active ? 'bg-dark-tertiary text-text-primary' : 'text-text-secondary')}
                                    >
                                        <span className="mr-3">{getIconForSymbol(instrument.symbol)}</span>
                                        <div className="flex flex-col items-start">
                                            <span className="font-bold text-text-primary">{instrument.symbol}</span>
                                            <span className="text-xs text-text-secondary">{instrument.description}</span>
                                        </div>
                                    </button>
                                )}
                            </Menu.Item>
                        ))}
                    </div>
                </Menu.Items>
            </Transition>
        </Menu>
    );
};

export default InstrumentSelector;