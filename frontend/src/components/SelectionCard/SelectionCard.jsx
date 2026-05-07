import styles from './SelectionCard.module.css';

/**
 * Card individual dentro del CombinationPanel.
 * Muestra la selección (partido) con botón para eliminar.
 */
export default function SelectionCard({ selection, onRemove }) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
  };

  return (
    <div className={styles.card}>
      <div className={styles.content}>
        <div className={styles.matchup}>
          <span className={styles.player}>{selection.player_home_name}</span>
          <span className={styles.vs}>vs</span>
          <span className={styles.player}>{selection.player_away_name}</span>
        </div>
        <div className={styles.meta}>
          <span>{selection.tournament_name}</span>
          <span>·</span>
          <span>{formatDate(selection.match_date)}</span>
        </div>
      </div>
      <button
        className={styles.removeBtn}
        onClick={() => onRemove(selection.match_id)}
        title="Eliminar de la combinada"
      >
        ✕
      </button>
    </div>
  );
}
