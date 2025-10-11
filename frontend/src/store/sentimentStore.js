import { create } from 'zustand';
import { produce } from 'immer';

const useSentimentStore = create((set, get) => ({
  liveFeed: [],
  historicalData: [],
  eventSource: null,

  /**
   * Connects to the real-time sentiment SSE stream for a given symbol.
   * @param {string} symbol - The trading symbol (e.g., 'BTCUSDT').
   */
  connect: (symbol) => {
    // Disconnect from any existing stream first
    get().disconnect();

    const token = localStorage.getItem('accessToken');
    const url = `${import.meta.env.VITE_API_BASE_URL}/sentiment/stream/${symbol}?token=${token}`;

    const newEventSource = new EventSource(url);

    newEventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      set(produce(draft => {
        // Keep the live feed to a manageable size (e.g., latest 20 headlines)
        draft.liveFeed.unshift(newData);
        if (draft.liveFeed.length > 20) {
          draft.liveFeed.pop();
        }
      }));
    };

    newEventSource.onerror = (err) => {
      console.error("EventSource failed:", err);
      newEventSource.close();
    };

    set({ eventSource: newEventSource });
  },

  /**
   * Disconnects from the current SSE stream.
   */
  disconnect: () => {
    const { eventSource } = get();
    if (eventSource) {
      eventSource.close();
      set({ eventSource: null, liveFeed: [] });
    }
  },
}));

export default useSentimentStore;