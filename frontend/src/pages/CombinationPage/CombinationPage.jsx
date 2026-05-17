import { useCombination } from '../../context/CombinationContext';
import CombinationSummary from '../../components/CombinationSummary/CombinationSummary';
import SelectionCard from '../../components/SelectionCard/SelectionCard';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './CombinationPage.module.css';

export default function CombinationPage() {
  const {
    combination,
    loading,
    createCombination,
    removeMatch,
    deleteCombination,
    saveCombination,
  } = useCombination();

  if (!combination) {
    return (
      <div className={styles.page}>
        <EmptyState
          icon="🎾"
          title="No tienes una combinada activa"
          message="Crea una para empezar a seleccionar partidos"
          action="Crear combinada"
          onAction={createCombination}
        />
      </div>
    );
  }

  const hasSelections = (combination.selections?.length || 0) > 0;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Mi combinada</h1>
      <CombinationSummary
        combinationId={combination.id}
        selectionsCount={combination.selections?.length || 0}
      />
      <div className={styles.selections}>
        {combination.selections?.map((s) => (
          <SelectionCard
            key={s.id}
            selection={s}
            onRemove={() => removeMatch(s.match_id)}
          />
        ))}
      </div>

      <div className={styles.actions}>
        {/* Botón guardar combinada en la base de datos */}
        <button
          className={styles.saveBtn}
          onClick={saveCombination}
          disabled={loading || !hasSelections}
          title={!hasSelections ? 'Agrega al menos un partido para guardar' : 'Guardar combinada en la base de datos'}
        >
          {loading ? 'Guardando...' : 'Guardar Combinada'}
        </button>

        <button
          className={styles.deleteBtn}
          onClick={deleteCombination}
          disabled={loading}
        >
          Eliminar combinada
        </button>
      </div>
    </div>
  );
}
