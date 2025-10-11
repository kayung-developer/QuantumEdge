import axiosClient from './axiosClient.js';

const paymentService = {
  getPublicPlans: () => axiosClient.get('/plans/'),
  initiatePayment: (data) => axiosClient.post('/payments/initiate', data),
  verifyPayment: (provider, reference) => axiosClient.get(`/payments/verify/${provider}/${reference}`),
};

export default paymentService;