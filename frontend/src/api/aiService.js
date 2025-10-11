import axiosClient from './axiosClient.js';

const aiService = {
  detectChartPatterns: ({ symbol, timeframe, limit }) => axiosClient.get(`/ai/patterns/${symbol}`, { params: { timeframe, limit } }),
  getRegisteredModels: () => axiosClient.get('/ai/models'),
};

export default aiService;