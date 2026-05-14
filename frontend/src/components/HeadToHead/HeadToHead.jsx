import styles from './HeadToHead.module.css';

export default function HeadToHead({ headToHead }) {
  if (!headToHead) {
    return <div className={styles.empty}>Primer enfrentamiento entre estos jugadores</div>;
  }
  const { player1_name, player2_name, player1_wins, player2_wins, total_matches, last_matches } = headToHead;
  const p1Pct = total_matches > 0 ? (player1_wins / total_matches) * 100 : 50;
  return (
    <div className={styles.h2h}>
      <div className={styles.score}>
        <div className={styles.player}><span className={styles.name}>{player1_name}</span><span className={styles.wins}>{player1_wins}</span></div>
        <div className={styles.divider}><span className={styles.total}>{total_matches} partidos</span></div>
        <div className={styles.player}><span className={styles.wins}>{player2_wins}</span><span className={styles.name}>{player2_name}</span></div>
      </div>
      <div className={styles.bar}>
        <div className={styles.barP1} style={{ width: `${p1Pct}%` }} />
      </div>
      {last_matches && last_matches.length > 0 && (
        <div className={styles.history}>
          <h4 className={styles.historyTitle}>Últimos enfrentamientos</h4>
          {last_matches.map((m, i) => (
            <div key={i} className={styles.match}>
              <span className={styles.date}>{m.date}</span>
              <span className={styles.tournament}>{m.tournament}</span>
              <span className={styles.matchScore}>{m.score}</span>
              <span className={styles.winner}>{m.winner}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
