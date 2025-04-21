import axios from 'axios';

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

export const api = axios.create({
  baseURL: getApiUrl(),
});

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}