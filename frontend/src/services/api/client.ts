import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for logging or global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with an error status
      console.error(
        `API Error [${error.response.status}] ${error.config?.url}:`,
        typeof error.response.data === 'object' 
          ? JSON.stringify(error.response.data, null, 2) 
          : error.response.data || '(empty response body)'
      );
    } else if (error.request) {
      // Request was made but no response received (network error / server down)
      console.error('API Network Error: No response received from', error.config?.url);
    } else {
      // Request setup error
      console.error('API Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
