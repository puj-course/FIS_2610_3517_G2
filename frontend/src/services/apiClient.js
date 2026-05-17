import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const msg = error.response.data?.error?.message || error.response.data?.detail || 'Error del servidor';
      return Promise.reject(new Error(msg));
    }
    if (error.request) {
      return Promise.reject(new Error('No se pudo conectar con el servidor'));
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
  const { data } = await api.post(`/combinations/${combinationId}/matches`, { match_id: matchId });
  return data;
};

export const removeMatchFromCombination = async (combinationId, matchId) => {
  const { data } = await api.delete(`/combinations/${combinationId}/matches/${matchId}`);
  return data;
};

// ==================== GUARDAR COMBINADA ====================
/**
 * Persiste la combinada activa en la base de datos.
 * Llama a POST /api/combinations/{id}/save
 */
export const saveCombination = async (combinationId) => {
  const { data } = await api.post(`/combinations/${combinationId}/save`);
  return data;
};

// ==================== COMPLETAR COMBINADA ====================
export const completeCombination = async (combinationId) => {
  const { data } = await api.post(`/combinations/${combinationId}/complete`);
  return data;
};

// ==================== ESTADÍSTICAS ====================
export const getMatchStats = async (matchId) => {
  const { data } = await api.get(`/matches/${matchId}/stats`);
  return data;
};

// ==================== PROBABILIDAD ====================
export const getMatchProbability = async (matchId) => {
  const { data } = await api.get(`/matches/${matchId}/probability`);
  return data;
};

export const getCombinationProbability = async (combinationId) => {
  const { data } = await api.get(`/combinations/${combinationId}/probability`);
  return data;
};

export const getCombinationResult = async (combinationId) => {
  const { data } = await api.get(`/combinations/${combinationId}/result`);
  return data;
};

// ==================== HISTORIAL ====================
export const getCombinationHistory = async () => {
  const { data } = await api.get('/combinations/history');
  return data;
};

// ==================== EXPORTAR ====================
export const exportCombinationResult = async (combinationId) => {
  const { data } = await api.get(`/combinations/${combinationId}/export`);
  return data;
};

export default api;
