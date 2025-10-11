import axiosClient from './axiosClient.js';

const adaptiveService = {
  getPortfolio: () => axiosClient.get('/adaptive/'),
  createPortfolio: (portfolioData) => axiosClient.post('/adaptive/', portfolioData),
  updatePortfolio: (portfolioId, updateData) => axiosClient.put(`/adaptive/${portfolioId}`, updateData),
  togglePortfolioActivation: (portfolioId) => axiosClient.post(`/adaptive/${portfolioId}/activate`),
};

export default adaptiveService;