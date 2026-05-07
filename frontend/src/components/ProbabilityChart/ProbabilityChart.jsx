import styles from './ProbabilityChart.module.css';
export default function ProbabilityChart({ matches }) {
  if (!matches || matches.length === 0) return null;
  return (
    <div className={styles.chart}>
      <h4 className={styles.title}>Probabilidad por partido</h4>
      {matches.map((m, i) => {
        const pct = Math.round(m.probability || 0);
        const level = pct > 60 ? 'high' : pct > 30 ? 'mid' : 'low';
        return (
          <div key={i} className={styles.row}>
            <span className={styles.label}>{m.match_label || `Partido ${i+1}`}</span>
            <div className={styles.bar}><div className={`${styles.fill} ${styles[level]}`} style={{ width: `${pct}%` }} /></div>
            <span className={styles.value}>{pct}%</span>
          </div>
        );
      })}
    </div>
  );
}
