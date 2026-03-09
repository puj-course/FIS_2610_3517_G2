import { useState, useEffect, useCallback } from 'react';
import { getMatches } from '../services/apiClient';

/**
 * Hook para obtener y filtrar partidos del backend.
 *
 * Uso:
 *   const { matches, loading, error, filterByStatus } = useMatches();
 */
export default function useMatches() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState(null);

  const fetchMatches = useCallback(async (status) => {
    setLoading(true);
    setError(null);
    try {
      const filters = {};
      if (status) filters.status = status;
      const data = await getMatches(filters);
      setMatches(data);
    } catch (err) {
      setError(err.message);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMatches(statusFilter);
  }, [statusFilter, fetchMatches]);

  const filterByStatus = (status) => {
    setStatusFilter(status || null);
  };

  const refresh = () => fetchMatches(statusFilter);

  return { matches, loading, error, filterByStatus, statusFilter, refresh };
}
