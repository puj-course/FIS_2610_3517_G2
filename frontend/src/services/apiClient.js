import axios from 'axios';

/**
 * Cliente HTTP centralizado para comunicación con el backend.
 * Todas las llamadas al backend pasan por aquí.
 */

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor: extraer mensaje de error del backend
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Error del backend con respuesta
      const backendError = error.response.data?.error?.message
        || error.response.data?.detail
        || 'Error del servidor';
      return Promise.reject(new Error(backendError));
    }
    if (error.request) {
      // Sin respuesta del servidor
      return Promise.reject(new Error('No se pudo conectar con el servidor. ¿Está corriendo el backend?'));
    }
    return Promise.reject(error);
  }
);

// ==================== PARTIDOS ====================

export const getMatches = async (filters = {}) => {
  const params = {};
  if (filters.status) params.status = filters.status;
  if (filters.tournament) params.tournament = filters.tournament;
  const { data } = await api.get('/matches', { params });
  return data;
};

export const getMatch = async (matchId) => {
  const { data } = await api.get(`/matches/${matchId}`);
  return data;
};

// ==================== COMBINADAS ====================

export const createCombination = async () => {
  const { data } = await api.post('/combinations');
  return data;
};

export const getCombination = async (combinationId) => {
  const { data } = await api.get(`/combinations/${combinationId}`);
  return data;
};

export const listCombinations = async () => {
  const { data } = await api.get('/combinations');
  return data;
};

export const deleteCombination = async (combinationId) => {
  const { data } = await api.delete(`/combinations/${combinationId}`);
  return data;
};

export const addMatchToCombination = async (combinationId, matchId) => {
  const { data } = await api.post(`/combinations/${combinationId}/matches`, {
    match_id: matchId,
  });
  return data;
};

export const removeMatchFromCombination = async (combinationId, matchId) => {
  const { data } = await api.delete(`/combinations/${combinationId}/matches/${matchId}`);
  return data;
};

export default api;
