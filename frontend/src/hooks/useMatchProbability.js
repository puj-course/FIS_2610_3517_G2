import { useState, useEffect } from 'react';
import { getMatchProbability } from '../services/apiClient';

export default function useMatchProbability(matchId) {
  const [probability, setProbability] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!matchId) return;
    setLoading(true);
    getMatchProbability(matchId)
      .then(setProbability)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [matchId]);

  return { probability, loading, error };
}
