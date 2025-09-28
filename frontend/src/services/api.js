import axios from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);

    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to the server. Please check if the API is running.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// Health check
export const checkAPIHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('API health check failed');
  }
};

// Question Answering API
export const askQuestion = async (data) => {
  const response = await api.post('/ask_review/ask', data);
  return response.data;
};

export const getSimilarReviews = async (query, topK = 5) => {
  const response = await api.get('/ask_review/similar', {
    params: { query, top_k: topK }
  });
  return response.data;
};

export const getQAStats = async () => {
  const response = await api.get('/ask_review/stats');
  return response.data;
};

// Recommendations API
export const getRecommendations = async (data) => {
  const response = await api.post('/recommend/products', data);
  return response.data;
};

export const getRecommendationsByQuery = async (query, topK = 10, minSimilarity = 0.3) => {
  const response = await api.get('/recommend/products', {
    params: { query, top_k: topK, min_similarity: minSimilarity }
  });
  return response.data;
};

export const getRecommendationsByProduct = async (productId, topK = 10) => {
  const response = await api.get('/recommend/products', {
    params: { product_id: productId, top_k: topK }
  });
  return response.data;
};

export const getRecommendationsByCategory = async (category, topK = 10) => {
  const response = await api.get('/recommend/products', {
    params: { category, top_k: topK }
  });
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/recommend/categories');
  return response.data.categories || [];
};

export const getRecommendationStats = async () => {
  const response = await api.get('/recommend/stats');
  return response.data;
};

// Utility functions
export const formatError = (error) => {
  if (error.response) {
    return error.response.data?.detail || error.response.data?.error || 'Server error occurred';
  } else if (error.request) {
    return 'Unable to connect to the server. Please check your connection.';
  } else {
    return error.message || 'An unexpected error occurred';
  }
};

export const isAPIHealthy = async () => {
  try {
    await checkAPIHealth();
    return true;
  } catch (error) {
    return false;
  }
};

export default api;
