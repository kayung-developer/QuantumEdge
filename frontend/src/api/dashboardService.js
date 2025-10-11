import axiosClient from './axiosClient.js';

const dashboardService = {
  getSummary: () => axiosClient.get('/dashboard/summary'),
};

export default dashboardService;