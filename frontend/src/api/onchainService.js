import axiosClient from './axiosClient.js';

const onchainService = {
  trackWhales: (tokenSymbol) => axiosClient.get(`/onchain/whale-tracker/${tokenSymbol}`),
};

export default onchainService;