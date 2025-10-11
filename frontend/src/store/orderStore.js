import { create } from 'zustand';
import { produce } from 'immer';
import tradeService from '../api/tradeService.js';

const useOrderStore = create((set, get) => ({
  orders: [], // Holds all orders in an active state
  trackedOrderIds: new Set(), // Prevents duplicate polling intervals
  pollingInterval: null,

  /**
   * Adds a new order to the store after it's been created.
   * @param {object} newOrder - The order object returned from the createOrder API call.
   */
  addOrder: (newOrder) => {
    set(produce((draft) => {
      // Avoid adding duplicates
      if (!draft.orders.some(o => o.id === newOrder.id)) {
        draft.orders.push(newOrder);
      }
    }));
    get().startPolling(); // Ensure polling is active
  },

  /**
   * The core function to poll for updates on all active orders.
   */
  pollOrders: async () => {
    const { orders } = get();
    const activeOrders = orders.filter(o => !['FILLED', 'CANCELED', 'REJECTED', 'ERROR'].includes(o.status));

    if (activeOrders.length === 0) {
      get().stopPolling();
      return;
    }

    // Create a batch of requests to update all active orders
    const updatePromises = activeOrders.map(order => tradeService.getOrderStatus(order.id));

    try {
        const results = await Promise.allSettled(updatePromises);

        set(produce(draft => {
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    const updatedOrder = result.value.data;
                    const orderIndex = draft.orders.findIndex(o => o.id === updatedOrder.id);
                    if (orderIndex !== -1) {
                        // Update the order in the store with the latest status
                        draft.orders[orderIndex] = updatedOrder;
                    }
                } else {
                    // Handle cases where a specific order poll fails
                    console.error(`Failed to update status for order ${activeOrders[index].id}:`, result.reason);
                }
            });
        }));
    } catch (error) {
        console.error("Error during order polling:", error);
    }
  },

  /**
   * Starts the background polling interval if it's not already running.
   */
  startPolling: () => {
    const { pollingInterval } = get();
    if (pollingInterval) return; // Already running

    const interval = setInterval(get().pollOrders, 3000); // Poll every 3 seconds
    set({ pollingInterval: interval });
    console.log("Order polling started.");
  },

  /**
   * Stops the background polling interval.
   */
  stopPolling: () => {
    const { pollingInterval } = get();
    if (pollingInterval) {
      clearInterval(pollingInterval);
      set({ pollingInterval: null });
      console.log("Order polling stopped.");
    }
  },
}));

export default useOrderStore;