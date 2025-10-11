import axiosClient from './axiosClient.js';

const signalService = {
  getPendingSignals: () => axiosClient.get('/signals/pending'),
  actionSignal: (signalId, action) => axiosClient.post(`/signals/${signalId}/action`, action),
};

export default signalService;