const envBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();

const API_BASE_URL = (envBaseUrl || (import.meta.env.DEV
  ? 'http://localhost:8000'
  : 'https://jansetu-backend.onrender.com')).replace(/\/$/, '');

export default API_BASE_URL;
