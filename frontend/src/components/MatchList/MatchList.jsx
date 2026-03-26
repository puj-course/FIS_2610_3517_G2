import MatchCard from '../MatchCard/MatchCard';
import styles from './MatchList.module.css';

/**
 * Lista de partidos con filtros.
 * Recibe matches, loading, error y filterByStatus como props.
 */

const STATUS_OPTIONS = [
  { value: null, label: 'Todos' },
  { value: 'upcoming', label: 'Próximos' },
  { value: 'live', label: 'En Vivo' },
  { value: 'finished', label: 'Finalizados' },
];

export default function MatchList({ matches, loading, error, filterByStatus, statusFilter }) {
  if (error) {
    return (
      <div className={styles.errorState}>
        <span className={styles.errorIcon}>⚠️</span>
        <h3>No se pudo conectar</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Filtros */}
      <div className={styles.filters}>
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt.label}
            className={`${styles.filterBtn} ${statusFilter === opt.value ? styles.filterActive : ''}`}
            onClick={() => filterByStatus(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className={styles.grid}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className={styles.skeleton} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && matches.length === 0 && (
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>🎾</span>
          <h3>No hay partidos disponibles</h3>
          <p>No se encontraron partidos con el filtro seleccionado.</p>
        </div>
      )}

      {/* Match grid */}
      {!loading && matches.length > 0 && (
        <div className={styles.grid}>
          {matches.map((match, idx) => (
            <div key={match.id} style={{ animationDelay: `${idx * 0.06}s` }}>
              <MatchCard match={match} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
