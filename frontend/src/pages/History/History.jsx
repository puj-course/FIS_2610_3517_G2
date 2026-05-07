import { useState, useEffect } from 'react';
import { getCombinationHistory } from '../../services/apiClient';
import HistoryCard from '../../components/HistoryCard/HistoryCard';
import EmptyState from '../../components/EmptyState/EmptyState';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import styles from './History.module.css';

export default function History() {
  const [combinations, setCombinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCombinationHistory().then(setCombinations).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className={styles.loading}>Cargando historial...</div>;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Historial de combinadas</h1>
      {combinations.length === 0 ? (
        <EmptyState icon="📋" title="Sin historial" message="Aún no has creado ninguna combinada" />
      ) : (
        <div className={styles.grid}>{combinations.map(c => <HistoryCard key={c.id} combination={c} />)}</div>
      )}
    </div>
  );
}
