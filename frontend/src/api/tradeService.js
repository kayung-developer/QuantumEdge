import axiosClient from './axiosClient.js';

const tradeService = {
  createOrder: (orderData) => axiosClient.post('/trade/order', orderData),
  getOrderStatus: (orderId) => axiosClient.get(`/trade/order/${orderId}`),
  // Note: These endpoints need to be updated to accept an `exchange` parameter
  // in the API to be truly multi-exchange capable from the UI.
  getOpenPositions: () => axiosClient.get('/trade/positions'),
  getTradeHistory: (params) => axiosClient.get('/trade/history', { params }),
};

export default tradeService;