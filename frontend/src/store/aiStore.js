import { create } from 'zustand';
import { produce } from 'immer';
import aiService from '../api/aiService.js';
import toast from 'react-hot-toast';

/**
 * Zustand store for managing the state of AI-driven features, such as
 * real-time chart pattern detections.
 */
const useAIStore = create((set, get) => ({
  patterns: [],
  isLoadingPatterns: false,

  /**
   * Fetches chart pattern detections from the backend for a given instrument.
   * This is typically called after new market data is fetched.
   *
   * @param {object} instrument - The instrument object (e.g., { symbol: 'BTC/USD' }).
   */
  fetchPatterns: async (instrument) => {
    if (!instrument || get().isLoadingPatterns) return;

    set(produce((draft) => {
      draft.isLoadingPatterns = true;
    }));

    try {
      const response = await aiService.detectChartPatterns({
        // The backend API expects the symbol without a slash (e.g., 'BTCUSD').
        symbol: instrument.symbol.replace('/', ''),
        timeframe: '1H', // This could be made dynamic based on user's chart view.
        limit: 200       // Number of recent candles to analyze.
      });
      set(produce((draft) => {
        draft.patterns = response.data;
      }));
    } catch (error) {
      console.error("Failed to fetch chart patterns:", error);
      // We don't show a toast here to avoid spamming the user on a polling/automatic feature.
      set(produce((draft) => {
        draft.patterns = [];
      }));
    } finally {
      set(produce((draft) => {
        draft.isLoadingPatterns = false;
      }));
    }
  },

  /**
   * Clears all detected patterns from the state.
   * This is useful when switching instruments to avoid showing stale data.
   */
  clearPatterns: () => {
    set(produce((draft) => {
      draft.patterns = [];
    }));
  },
}));

export default useAIStore;