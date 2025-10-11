import { create } from 'zustand';
import { produce } from 'immer';
import useAIStore from './aiStore.js'; // Import the AI store to trigger analysis

// --- MOCK DATA GENERATION ---
// In a real application, this data would come from the backend's market_service.
const mockInstruments = [
    { symbol: 'BTC/USD', description: 'Bitcoin / US Dollar', type: 'Crypto' },
    { symbol: 'ETH/USD', description: 'Ethereum / US Dollar', type: 'Crypto' },
    { symbol: 'EUR/USD', description: 'Euro / US Dollar', type: 'Forex' },
    { symbol: 'GBP/JPY', description: 'British Pound / Japanese Yen', type: 'Forex' },
    { symbol: 'XAU/USD', description: 'Gold / US Dollar', type: 'Commodity' },
];

const generateMockCandles = (count = 500) => {
    let price = 65000 + Math.random() * 2000 - 1000;
    const data = [];
    const now = new Date();
    for (let i = 0; i < count; i++) {
        const time = new Date(now.getTime() - (count - i) * 60 * 60 * 1000).getTime() / 1000; // Hourly candles
        const open = price;
        const close = open + (Math.random() - 0.48) * 500;
        const high = Math.max(open, close) + Math.random() * 200;
        const low = Math.min(open, close) - Math.random() * 200;
        price = close;
        data.push({ time, open, high, low, close, volume: Math.random() * 1000 + 100 });
    }
    return data;
};

/**
 * Zustand store for managing global market data state, including the
 * selected instrument and its corresponding kline (candlestick) data.
 */
const useMarketDataStore = create((set, get) => ({
  instruments: mockInstruments,
  currentInstrument: mockInstruments[0],
  kline: {
    data: [],
    loading: true,
    timeframe: '1H',
  },

  // --- ACTIONS ---

  /**
   * Sets the active trading instrument, clears old data, and fetches new data.
   * @param {object} instrument - The new instrument object to set.
   */
  setCurrentInstrument: (instrument) => {
    set(produce((draft) => {
      draft.currentInstrument = instrument;
      draft.kline.loading = true; // Set loading state for the chart
      draft.kline.data = [];      // Clear old data immediately
    }));

    // Clear any AI patterns from the previous instrument
    useAIStore.getState().clearPatterns();

    // Trigger the data fetch for the new instrument
    get().fetchKlineToRender();
  },

  /**
   * Fetches historical candlestick data for the current instrument.
   * In a real system, this would make an API call to `/market/klines/...`.
   */
  fetchKlineToRender: async () => {
    const { currentInstrument } = get();
    console.log(`Fetching kline data for ${currentInstrument.symbol}...`);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 800));

    const mockData = generateMockCandles();

    set(produce((draft) => {
      draft.kline.data = mockData;
      draft.kline.loading = false;
    }));

    // After successfully fetching new market data, trigger the AI analysis on it.
    useAIStore.getState().fetchPatterns(currentInstrument);
  },

  /**
   * Simulates a real-time update to the latest candle.
   * In a real app, this would be called by a WebSocket event handler.
   */
  updateLastCandle: () => {
    set(produce(draft => {
      if (draft.kline.data.length === 0) return;

      const lastCandle = draft.kline.data[draft.kline.data.length - 1];
      const newClose = lastCandle.close + (Math.random() - 0.5) * 50;
      const newHigh = Math.max(lastCandle.high, newClose);
      const newLow = Math.min(lastCandle.low, newClose);

      // This creates a new object for the last candle to ensure React re-renders.
      draft.kline.data[draft.kline.data.length - 1] = {
        ...lastCandle,
        close: newClose,
        high: newHigh,
        low: newLow,
        volume: lastCandle.volume + (Math.random() * 10),
      };
    }));
  },
}));

// Simulate real-time price ticks every 2 seconds to make the chart feel live
setInterval(() => {
    useMarketDataStore.getState().updateLastCandle();
}, 2000);

export default useMarketDataStore;