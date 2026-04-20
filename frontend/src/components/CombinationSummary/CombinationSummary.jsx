import { useState, useEffect } from 'react';
import { getCombinationProbability } from '../../services/apiClient';
import RiskIndicator from '../RiskIndicator/RiskIndicator';
import styles from './CombinationSummary.module.css';

export default function CombinationSummary({ combinationId, selectionsCount }) {
  const [prob, setProb] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!combinationId || selectionsCount < 2) { setProb(null); return; }
    setLoading(true);
    getCombinationProbability(combinationId)
      .then(setProb)
      .catch(() => setProb(null))
      .finally(() => setLoading(false));
  }, [combinationId, selectionsCount]);

  if (selectionsCount < 2) {
    return <div className={styles.info}>Agrega al menos 2 partidos para ver la probabilidad</div>;
  }
  if (loading) return <div className={styles.loading}>Calculando...</div>;
  if (!prob) return null;

  return (
    <div className={styles.summary}>
      <div className={styles.totalProb}>
        <span className={styles.probValue}>{Math.round(prob.total_probability)}%</span>
        <span className={styles.probLabel}>Probabilidad total</span>
      </div>
      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: `${prob.total_probability}%` }} />
      </div>
      <RiskIndicator level={prob.risk_level} message={prob.message} />
    </div>
  );
}
