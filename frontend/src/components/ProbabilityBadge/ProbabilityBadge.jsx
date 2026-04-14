import styles from './ProbabilityBadge.module.css';

export default function ProbabilityBadge({ probability, playerName, loading }) {
  if (loading) return <span className={styles.badge + ' ' + styles.loading}>...</span>;
  if (probability == null) return <span className={styles.badge + ' ' + styles.na}>N/A</span>;
  const pct = Math.round(probability);
  let colorClass = styles.low;
  if (pct >= 60) colorClass = styles.high;
  else if (pct >= 30) colorClass = styles.mid;
  return (
    <span className={`${styles.badge} ${colorClass}`} title={`${playerName}: ${pct}% probabilidad`}>
      {pct}%
    </span>
  );
}
