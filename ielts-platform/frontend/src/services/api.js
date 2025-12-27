// Frontend API Service - IELTS Master Platform
// Save as: frontend/src/services/api.js

import axios from 'axios';
import { useState, useEffect, useCallback } from 'react';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// API Service Functions
// ============================================

// Reading Tests
export const readingAPI = {
  getAll: (params) => api.get('/reading', { params }),
  getById: (id) => api.get(`/reading/${id}`),
  submitAnswer: (id, answers) => api.post(`/reading/${id}/submit`, { answers }),
};

// Listening Tests
export const listeningAPI = {
  getAll: (params) => api.get('/listening', { params }),
  getById: (id) => api.get(`/listening/${id}`),
  submitAnswer: (id, answers) => api.post(`/listening/${id}/submit`, { answers }),
};

// Writing Tasks
export const writingAPI = {
  getAll: (params) => api.get('/writing', { params }),
  getById: (id) => api.get(`/writing/${id}`),
  submit: (id, essay) => api.post(`/writing/${id}/submit`, { essay }),
};

// Speaking Tests
export const speakingAPI = {
  getAll: (params) => api.get('/speaking', { params }),
  getById: (id) => api.get(`/speaking/${id}`),
  submitRecording: (id, audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    return api.post(`/speaking/${id}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Full Mock Tests
export const testsAPI = {
  getAll: (params) => api.get('/tests', { params }),
  getById: (id) => api.get(`/tests/${id}`),
  submit: (id, answers) => api.post(`/tests/${id}/submit`, { answers }),
};

// AI Services
export const aiAPI = {
  analyzeWriting: (text, taskType) => 
    api.post('/ai/analyze-writing', { text, taskType }),
  analyzeSpeaking: (transcript, questionType) => 
    api.post('/ai/analyze-speaking', { transcript, questionType }),
  chat: (message, conversationHistory = []) => 
    api.post('/ai/chat', { message, conversationHistory }),
};

// User Progress
export const userAPI = {
  getProgress: (userId) => api.get(`/user/${userId}/progress`),
  updateProgress: (userId, data) => api.put(`/user/${userId}/progress`, data),
  saveTestResult: (userId, result) => api.post(`/user/${userId}/test-result`, result),
  getAchievements: (userId) => api.get(`/user/${userId}/achievements`),
  updateStreak: (userId) => api.post(`/user/${userId}/streak`),
};

// Vocabulary
export const vocabularyAPI = {
  getAll: (params) => api.get('/vocabulary', { params }),
  getById: (id) => api.get(`/vocabulary/${id}`),
  addWord: (word) => api.post('/vocabulary', word),
  updateWord: (id, updates) => api.put(`/vocabulary/${id}`, updates),
  deleteWord: (id) => api.delete(`/vocabulary/${id}`),
  getReviewWords: () => api.get('/vocabulary/review'),
};

// Database Seeding
export const seedDatabase = () => api.post('/seed');

// ============================================
// Custom React Hooks
// ============================================

// Generic fetch hook
export function useApi(apiFunction, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiFunction();
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  useEffect(() => {
    fetchData();
  }, [...dependencies, fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Hook for fetching tests by type
export function useTests(type, params = {}) {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTests = async () => {
      try {
        setLoading(true);
        let response;
        switch (type) {
          case 'reading':
            response = await readingAPI.getAll(params);
            break;
          case 'listening':
            response = await listeningAPI.getAll(params);
            break;
          case 'writing':
            response = await writingAPI.getAll(params);
            break;
          case 'speaking':
            response = await speakingAPI.getAll(params);
            break;
          case 'full':
            response = await testsAPI.getAll(params);
            break;
          default:
            throw new Error('Invalid test type');
        }
        setTests(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTests();
  }, [type, JSON.stringify(params)]);

  return { tests, loading, error };
}

// Hook for single test
export function useTest(type, id) {
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;

    const fetchTest = async () => {
      try {
        setLoading(true);
        let response;
        switch (type) {
          case 'reading':
            response = await readingAPI.getById(id);
            break;
          case 'listening':
            response = await listeningAPI.getById(id);
            break;
          case 'writing':
            response = await writingAPI.getById(id);
            break;
          case 'speaking':
            response = await speakingAPI.getById(id);
            break;
          case 'full':
            response = await testsAPI.getById(id);
            break;
          default:
            throw new Error('Invalid test type');
        }
        setTest(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTest();
  }, [type, id]);

  return { test, loading, error };
}

// Hook for user progress
export function useProgress(userId) {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProgress = useCallback(async () => {
    if (!userId) return;
    try {
      setLoading(true);
      const response = await userAPI.getProgress(userId);
      setProgress(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  const updateProgress = async (data) => {
    try {
      const response = await userAPI.updateProgress(userId, data);
      setProgress(response.data);
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  return { progress, loading, error, updateProgress, refetch: fetchProgress };
}

// Hook for AI chat
export function useAIChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (message) => {
    try {
      setLoading(true);
      setError(null);
      
      // Add user message immediately
      const userMessage = { role: 'user', content: message };
      setMessages(prev => [...prev, userMessage]);
      
      // Get AI response
      const response = await aiAPI.chat(message, messages);
      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
      
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  return { messages, loading, error, sendMessage, clearChat };
}

// Hook for writing analysis
export function useWritingAnalysis() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeWriting = async (text, taskType = 'task2') => {
    try {
      setLoading(true);
      setError(null);
      const response = await aiAPI.analyzeWriting(text, taskType);
      setAnalysis(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { analysis, loading, error, analyzeWriting };
}

// Hook for speaking analysis
export function useSpeakingAnalysis() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeSpeaking = async (transcript, questionType = 'part2') => {
    try {
      setLoading(true);
      setError(null);
      const response = await aiAPI.analyzeSpeaking(transcript, questionType);
      setAnalysis(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { analysis, loading, error, analyzeSpeaking };
}

// Hook for vocabulary with spaced repetition
export function useVocabulary() {
  const [words, setWords] = useState([]);
  const [reviewWords, setReviewWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWords = useCallback(async () => {
    try {
      setLoading(true);
      const [allWords, review] = await Promise.all([
        vocabularyAPI.getAll(),
        vocabularyAPI.getReviewWords(),
      ]);
      setWords(allWords.data);
      setReviewWords(review.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWords();
  }, [fetchWords]);

  const addWord = async (word) => {
    const response = await vocabularyAPI.addWord(word);
    setWords(prev => [...prev, response.data]);
    return response.data;
  };

  const updateWord = async (id, updates) => {
    const response = await vocabularyAPI.updateWord(id, updates);
    setWords(prev => prev.map(w => w.id === id ? response.data : w));
    return response.data;
  };

  const deleteWord = async (id) => {
    await vocabularyAPI.deleteWord(id);
    setWords(prev => prev.filter(w => w.id !== id));
  };

  return { words, reviewWords, loading, error, addWord, updateWord, deleteWord, refetch: fetchWords };
}

// Export default api instance for custom requests
export default api;
