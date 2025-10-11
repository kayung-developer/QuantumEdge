import axiosClient from './axiosClient.js';

const strategyService = {
  /**
   * Fetches the list of all available trading strategies.
   */
  getAvailableStrategies: () => {
    return axiosClient.get('/strategies/');
  },

  /**
   * Submits a request to run a new backtest.
   * @param {object} backtestConfig - The configuration for the backtest.
   */
  runBacktest: (backtestConfig) => {
    return axiosClient.post('/strategies/run-backtest', backtestConfig);
  },
};

export default strategyService;