import axiosClient from './axiosClient.js';

const orderBookService = {
  getSnapshot: (symbol) => axiosClient.get(`/orderbook/${symbol}`),
};

export default orderBookService;