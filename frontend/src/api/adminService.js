import axiosClient from './axiosClient.js';

const adminService = {
  getAllUsers: (params) => axiosClient.get('/users/', { params }),
  updateUser: (userId, userData) => axiosClient.put(`/users/${userId}`, userData),
  deleteUser: (userId) => axiosClient.delete(`/users/${userId}`),
  createUser: (userData) => axiosClient.post('/users/', userData),
};

export default adminService;