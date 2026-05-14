import styles from './ProbabilityBreakdown.module.css';

export default function ProbabilityBreakdown({ probability }) {
  if (!probability) return <div className={styles.empty}>Sin datos de probabilidad</div>;
  const { player_home_probability, player_away_probability, factors, confidence, message } = probability;
  const confidenceClass = confidence === 'alta' ? styles.high : confidence === 'media' ? styles.mid : styles.low;
  return (
    <div className={styles.breakdown}>
      <div className={styles.mainProb}>
        <div className={styles.probPlayer}>
          <span className={styles.probValue}>{Math.round(player_home_probability)}%</span>
          <span className={styles.probLabel}>Local</span>
        </div>
        <div className={styles.probVs}>VS</div>
        <div className={styles.probPlayer}>
          <span className={styles.probValue}>{Math.round(player_away_probability)}%</span>
          <span className={styles.probLabel}>Visitante</span>
        </div>
      </div>
      <div className={`${styles.confidence} ${confidenceClass}`}>
        Confianza: {confidence}
      </div>
      {factors && factors.length > 0 && (
        <div className={styles.factors}>
          <h4>Desglose de factores</h4>
          {factors.map((f, i) => (
            <div key={i} className={styles.factor}>
              <span className={styles.factorName}>{f.name}</span>
              <div className={styles.factorBar}>
                <div className={styles.factorFill} style={{ width: `${f.weight * 100}%` }} />
              </div>
              <span className={styles.factorWeight}>{(f.weight * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      )}
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
}
