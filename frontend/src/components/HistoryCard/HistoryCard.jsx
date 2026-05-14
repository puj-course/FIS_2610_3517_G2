import { useNavigate } from 'react-router-dom';
import styles from './HistoryCard.module.css';

export default function HistoryCard({ combination }) {
  const navigate = useNavigate();
  const { id, selections, status, created_at, total_probability } = combination;

  const handleNavigate = () => navigate(`/combination/${id}/result`);

  return (
    <div
      className={styles.card}
      onClick={handleNavigate}
      onKeyDown={(e) => e.key === 'Enter' && handleNavigate()}
      role="button"
      tabIndex={0}
    >
      <div className={styles.header}>
        <span className={`${styles.badge} ${styles[status]}`}>{status === 'completed' ? 'Completada' : 'Activa'}</span>
        <span className={styles.date}>{new Date(created_at).toLocaleDateString()}</span>
      </div>
      <div className={styles.body}>
        <span className={styles.count}>{selections?.length || 0} partidos</span>
        {total_probability != null && <span className={styles.prob}>{Math.round(total_probability)}%</span>}
      </div>
    </div>
  );
}
