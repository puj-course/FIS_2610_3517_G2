import { useState, useEffect } from 'react';
import { getCombinationResult } from '../services/apiClient';

export default function useCombinationResult(combinationId) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!combinationId) return;
    setLoading(true);
    getCombinationResult(combinationId)
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [combinationId]);

  return { result, loading, error, refresh: () => {
    setLoading(true);
    getCombinationResult(combinationId).then(setResult).catch((err) => setError(err.message)).finally(() => setLoading(false));
  }};
}
