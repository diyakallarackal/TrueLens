import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 180s timeout for video processing
});

export const checkHealth = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'offline', error: error.message };
  }
};

export const getCapabilities = async () => {
  try {
    const response = await api.get('/api/capabilities');
    return response.data;
  } catch (error) {
    console.error('Capabilities check failed:', error);
    return {
      image_analysis: true,
      audio_analysis: true,
      video_analysis: true,
      content_credentials: true,
      external_reverse_search: false,
    };
  }
};

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeAudio = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/analyze/audio', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeVideo = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/analyze/video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getHistory = async (limit = 30, offset = 0, mediaType = null) => {
  let url = `/api/history?limit=${limit}&offset=${offset}`;
  if (mediaType) {
    url += `&media_type=${mediaType}`;
  }
  const response = await api.get(url);
  return response.data;
};

export const getHistoryDetail = async (analysisId) => {
  const response = await api.get(`/api/history/${analysisId}`);
  return response.data;
};

export const deleteHistoryItem = async (analysisId) => {
  const response = await api.delete(`/api/history/${analysisId}`);
  return response.data;
};

export default api;
