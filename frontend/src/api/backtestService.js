import axiosClient from './axiosClient.js';

const backtestService = {
  launchWalkForward: (config) => axiosClient.post('/walkforward/launch', config),
  getWalkForwardStatus: (jobId) => axiosClient.get(`/walkforward/${jobId}/status`),
};

export default backtestService;