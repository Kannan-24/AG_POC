import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  demoLogin: (username) => apiClient.post('/auth/demo-login', { username }),
  getCurrentUser: () => apiClient.get('/auth/me'),
  getUserPermissions: () => apiClient.get('/auth/me/permissions'),
};

// Cases API
export const casesAPI = {
  getAll: () => apiClient.get('/cases'),
  getById: (caseId) => apiClient.get(`/cases/${caseId}`),
  create: (data) => apiClient.post('/cases', data),
  update: (caseId, data) => apiClient.patch(`/cases/${caseId}`, data),
  reassign: (caseId, assignedTo) => apiClient.post(`/cases/${caseId}/reassign`, { assigned_to: assignedTo }),
  sign: (caseId) => apiClient.post(`/cases/${caseId}/sign`),
};

// Users API
export const usersAPI = {
  getAll: () => apiClient.get('/users'),
};

// Roles API
export const rolesAPI = {
  getAll: () => apiClient.get('/roles'),
  getPermissions: (roleId) => apiClient.get(`/roles/${roleId}/permissions`),
};

// Audit API
export const auditAPI = {
  getLog: () => apiClient.get('/audit'),
};

// Tenant API
export const tenantAPI = {
  get: () => apiClient.get('/tenant'),
  getConfiguration: () => apiClient.get('/tenant/configuration'),
  updateConfiguration: (data) => apiClient.patch('/tenant/configuration', data),
};

export default apiClient;
