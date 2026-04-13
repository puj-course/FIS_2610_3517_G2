import styles from './StatsComparison.module.css';

function StatBar({ label, homeValue, awayValue, homeName, awayName }) {
  const total = homeValue + awayValue || 1;
  const homeWidth = (homeValue / total) * 100;
  const awayWidth = (awayValue / total) * 100;
  return (
    <div className={styles.statRow}>
      <div className={styles.playerValue}>{homeValue.toFixed(1)}%</div>
      <div className={styles.barContainer}>
        <div className={styles.barHome} style={{ width: `${homeWidth}%` }} />
        <span className={styles.barLabel}>{label}</span>
        <div className={styles.barAway} style={{ width: `${awayWidth}%` }} />
      </div>
      <div className={styles.playerValue}>{awayValue.toFixed(1)}%</div>
    </div>
  );
}

export default function StatsComparison({ playerHomeStats, playerAwayStats, surface }) {
  if (!playerHomeStats || !playerAwayStats) {
    return <div className={styles.empty}>No hay estadísticas disponibles</div>;
  }
  return (
    <div className={styles.comparison}>
      <div className={styles.header}>
        <span className={styles.playerName}>{playerHomeStats.player_name}</span>
        <span className={styles.vs}>VS</span>
        <span className={styles.playerName}>{playerAwayStats.player_name}</span>
      </div>
      <StatBar label="Win rate general" homeValue={playerHomeStats.overall_win_rate} awayValue={playerAwayStats.overall_win_rate} />
      <StatBar label={`Win rate ${surface}`} homeValue={playerHomeStats.surface_win_rate} awayValue={playerAwayStats.surface_win_rate} />
      <StatBar label="Forma reciente" homeValue={playerHomeStats.recent_win_rate} awayValue={playerAwayStats.recent_win_rate} />
      <div className={styles.extra}>
        <div><strong>{playerHomeStats.total_matches}</strong> partidos</div>
        <div className={styles.extraLabel}>Total partidos</div>
        <div><strong>{playerAwayStats.total_matches}</strong> partidos</div>
      </div>
      <div className={styles.extra}>
        <div><strong>{playerHomeStats.titles}</strong> títulos</div>
        <div className={styles.extraLabel}>Títulos</div>
        <div><strong>{playerAwayStats.titles}</strong> títulos</div>
      </div>
    </div>
  );
}
