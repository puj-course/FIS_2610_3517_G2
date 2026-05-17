import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import {
  createCombination as apiCreate,
  getCombination as apiGet,
  deleteCombination as apiDelete,
  addMatchToCombination as apiAddMatch,
  removeMatchFromCombination as apiRemoveMatch,
  saveCombination as apiSave,
} from '../services/apiClient';
import { useNotification } from './NotificationContext';

const STORAGE_KEY = 'oddsengine_combination_id';

const CombinationContext = createContext(null);

export function CombinationProvider({ children }) {
  const [combination, setCombination] = useState(null);
  const [loading, setLoading] = useState(false);
  const { showSuccess, showError, showInfo } = useNotification();

  // Al montar, recuperar la combinada persistida desde localStorage
  useEffect(() => {
    const savedId = localStorage.getItem(STORAGE_KEY);
    if (!savedId) return;

    setLoading(true);
    apiGet(savedId)
      .then((data) => {
        setCombination(data);
      })
      .catch(() => {
        // Si la combinada ya no existe en el backend, limpiar
        localStorage.removeItem(STORAGE_KEY);
      })
      .finally(() => setLoading(false));
  }, []);

  // Cada vez que cambia la combinada, sincronizar el id en localStorage
  useEffect(() => {
    if (combination?.id) {
      localStorage.setItem(STORAGE_KEY, combination.id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [combination]);

  const createCombination = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiCreate();
      setCombination(data);
      showSuccess('¡Combinada creada! Agrega partidos para comenzar.');
      return data;
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [showSuccess, showError]);

  const addMatch = useCallback(async (matchId) => {
    if (!combination) {
      showError('Primero crea una combinada');
      return;
    }
    setLoading(true);
    try {
      const data = await apiAddMatch(combination.id, matchId);
      setCombination(data);
      showSuccess(data.message || 'Partido agregado');
      return data;
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [combination, showSuccess, showError]);

  const removeMatch = useCallback(async (matchId) => {
    if (!combination) return;
    setLoading(true);
    try {
      const data = await apiRemoveMatch(combination.id, matchId);
      setCombination(data);
      showSuccess(data.message || 'Partido eliminado');
      return data;
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [combination, showSuccess, showError]);

  const deleteCombination = useCallback(async () => {
    if (!combination) return;
    setLoading(true);
    try {
      await apiDelete(combination.id);
      setCombination(null);
      showInfo('Combinada eliminada');
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [combination, showInfo, showError]);

  // Guardar (persistir) la combinada en la base de datos
  const saveCombination = useCallback(async () => {
    if (!combination) return;
    setLoading(true);
    try {
      const data = await apiSave(combination.id);
      showSuccess(data.message || '¡Combinada guardada correctamente!');
      return data;
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }, [combination, showSuccess, showError]);

  const isMatchInCombination = useCallback((matchId) => {
    if (!combination) return false;
    return combination.selections?.some((s) => s.match_id === matchId) || false;
  }, [combination]);

  return (
    <CombinationContext.Provider
      value={{
        combination,
        loading,
        createCombination,
        addMatch,
        removeMatch,
        deleteCombination,
        saveCombination,
        isMatchInCombination,
      }}
    >
      {children}
    </CombinationContext.Provider>
  );
}

export function useCombination() {
  const ctx = useContext(CombinationContext);
  if (!ctx) throw new Error('useCombination debe usarse dentro de CombinationProvider');
  return ctx;
}
