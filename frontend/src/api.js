import axios from 'axios';

// Get API URL from environment variables with fallback
function getApiUrl() {
  // Check if import.meta is defined (for Vite and modern bundlers)
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Fallback for Node.js environments
  if (typeof process !== 'undefined' && process.env && process.env.VITE_API_URL) {
    return process.env.VITE_API_URL;
  }
  return 'http://localhost:8001/api';
}

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for API calls
api.interceptors.request.use(
  config => {
    // You can modify request config here (add headers, etc)
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Handle 401 - Unauthorized errors (token expired)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      // You could implement token refresh logic here
      // For now, just redirect to login
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Set auth token for API requests
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

// Auth API services
export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/users/me')
};

// User API services
export const userApi = {
  updateProfile: (data) => {
    // Check if data is FormData
    const isFormData = data instanceof FormData;
    return api.patch('/users/me', data, {
      headers: isFormData ? {
        'Content-Type': 'multipart/form-data'
      } : {
        'Content-Type': 'application/json'
      }
    });
  },
  uploadProfilePicture: (formData) => api.post('/users/profile-picture', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
};

// Face recognition API services
export const faceApi = {
  uploadEmbedding: (data) => api.post('/face/upload', data),
  verifyFace: (data) => api.post('/face/verify', data)
};

// Test API services
export const testApi = {
  getTests: () => api.get('/tests'),
  getTest: (id) => api.get(`/tests/${id}`),
  getInstructorTests: (instructorId) => api.get(`/instructors/${instructorId}/tests`),
  createTest: (data) => api.post('/tests', data),
  updateTest: (id, data) => api.put(`/tests/${id}`, data),
  deleteTest: (id) => api.delete(`/tests/${id}`),
  submitTest: (id, answers) => api.post(`/tests/${id}/submit`, answers)
};

// Attendance API services
export const attendanceApi = {
  markAttendance: (data) => api.post('/attendance', data),
  getAttendanceHistory: (params) => api.get('/attendance/history', { params }),
  getAttendanceStats: () => api.get('/attendance/stats')
};