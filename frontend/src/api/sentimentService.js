import axiosClient from './axiosClient.js';

const sentimentService = {
  /**
   * Fetches historical sentiment data for a given symbol.
   * @param {string} symbol - The trading symbol (e.g., 'BTCUSDT').
   */
  getHistorical: (symbol) => {
    return axiosClient.get(`/sentiment/historical/${symbol}`);
  },

  /**
   * NOTE: The real-time stream will be handled directly using the browser's
   * EventSource API, not through axios, as it's a persistent connection.
   */
};

export default sentimentService;