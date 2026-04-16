import styles from './ResultCard.module.css';
export default function ResultCard({ probability, selectionsCount }) {
  const pct = Math.round(probability || 0);
  const level = pct > 50 ? 'high' : pct > 20 ? 'mid' : 'low';
  return (
    <div className={`${styles.card} ${styles[level]}`}>
      <div className={styles.pct}>{pct}%</div>
      <div className={styles.label}>Probabilidad combinada</div>
      <div className={styles.count}>{selectionsCount} partidos seleccionados</div>
    </div>
  );
}
