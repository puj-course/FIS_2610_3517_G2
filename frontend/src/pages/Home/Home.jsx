import useMatches from '../../hooks/useMatches';
import MatchList from '../../components/MatchList/MatchList';
import CombinationPanel from '../../components/CombinationPanel/CombinationPanel';
import styles from './Home.module.css';

/**
 * Página principal — Lista de partidos + Panel de combinada.
 */
export default function Home() {
  const { matches, loading, error, filterByStatus, statusFilter } = useMatches();

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Partidos de Tenis</h1>
        <p className={styles.pageSubtitle}>
          Selecciona partidos para construir tu combinada de apuestas
        </p>
      </div>

      {/* Two-column layout */}
      <div className={styles.columns}>
        <div className={styles.mainCol}>
          <MatchList
            matches={matches}
            loading={loading}
            error={error}
            filterByStatus={filterByStatus}
            statusFilter={statusFilter}
          />
        </div>
        <aside className={styles.sideCol}>
          <CombinationPanel />
        </aside>
      </div>
    </div>
  );
}
