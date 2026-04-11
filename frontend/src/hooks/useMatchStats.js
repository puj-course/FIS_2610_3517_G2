import { useState, useEffect } from 'react';
import { getMatchStats } from '../services/apiClient';

export default function useMatchStats(matchId) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!matchId) return;
    setLoading(true);
    setError(null);
    getMatchStats(matchId)
      .then(setStats)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [matchId]);

  return { stats, loading, error };
}
