import { useCombination } from '../../context/CombinationContext';
import CombinationSummary from '../../components/CombinationSummary/CombinationSummary';
import SelectionCard from '../../components/SelectionCard/SelectionCard';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './CombinationPage.module.css';

export default function CombinationPage() {
  const { combination, createCombination, removeMatch, deleteCombination } = useCombination();

  if (!combination) {
    return <div className={styles.page}><EmptyState icon="🎾" title="No tienes una combinada activa" message="Crea una para empezar a seleccionar partidos" action="Crear combinada" onAction={createCombination} /></div>;
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Mi combinada</h1>
      <CombinationSummary combinationId={combination.id} selectionsCount={combination.selections?.length || 0} />
      <div className={styles.selections}>
        {combination.selections?.map(s => <SelectionCard key={s.id} selection={s} onRemove={() => removeMatch(s.match_id)} />)}
      </div>
      <button className={styles.deleteBtn} onClick={deleteCombination}>Eliminar combinada</button>
    </div>
  );
}
