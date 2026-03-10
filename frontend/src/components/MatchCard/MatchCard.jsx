import { useNavigate } from 'react-router-dom';
import { useCombination } from '../../context/CombinationContext';
import styles from './MatchCard.module.css';

/**
 * Tarjeta individual de un partido.
 * Muestra: jugadores, torneo, superficie, fecha, estado, botón agregar.
 */
export default function MatchCard({ match }) {
  const navigate = useNavigate();
  const { isMatchInCombination, addMatch, combination } = useCombination();
  const isAdded = isMatchInCombination(match.id);

  const statusConfig = {
    upcoming: { label: 'Próximo', className: styles.upcoming },
    live: { label: '● EN VIVO', className: styles.live },
    finished: { label: 'Finalizado', className: styles.finished },
    cancelled: { label: 'Cancelado', className: styles.cancelled },
  };

  const surfaceEmoji = {
    hard: '🔵',
    clay: '🟠',
    grass: '🟢',
    carpet: '🟣',
  };

  const status = statusConfig[match.status] || statusConfig.upcoming;

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CO', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleCardClick = () => {
    navigate(`/matches/${match.id}`);
  };

  const handleAddClick = (e) => {
    e.stopPropagation();
    if (!isAdded) {
      addMatch(match.id);
    }
  };

  return (
    <div className={styles.card} onClick={handleCardClick}>
      {/* Status badge */}
      <div className={styles.topRow}>
        <span className={`${styles.badge} ${status.className}`}>
          {status.label}
        </span>
        <span className={styles.surface}>
          {surfaceEmoji[match.tournament?.surface] || '🎾'} {match.tournament?.surface}
        </span>
      </div>

      {/* Players */}
      <div className={styles.players}>
        <div className={styles.player}>
          <span className={styles.playerName}>{match.player_home?.name}</span>
          <span className={styles.country}>{match.player_home?.country}</span>
        </div>

        <div className={styles.vs}>
          {match.status === 'finished' && match.score ? (
            <span className={styles.score}>{match.score}</span>
          ) : (
            <span className={styles.vsText}>VS</span>
          )}
        </div>

        <div className={`${styles.player} ${styles.playerRight}`}>
          <span className={styles.playerName}>{match.player_away?.name}</span>
          <span className={styles.country}>{match.player_away?.country}</span>
        </div>
      </div>

      {/* Tournament & Date */}
      <div className={styles.info}>
        <span className={styles.tournament}>{match.tournament?.name}</span>
        <span className={styles.date}>{formatDate(match.date)}</span>
      </div>

      {/* Add to combination button */}
      <button
        className={`${styles.addBtn} ${isAdded ? styles.added : ''}`}
        onClick={handleAddClick}
        disabled={isAdded || !combination}
        title={!combination ? 'Primero crea una combinada' : isAdded ? 'Ya agregado' : 'Agregar a combinada'}
      >
        {isAdded ? '✓ Agregado' : '+ Agregar'}
      </button>
    </div>
  );
}
