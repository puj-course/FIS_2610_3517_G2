import { useState } from 'react';
import { useCombination } from '../../context/CombinationContext';
import SelectionCard from '../SelectionCard/SelectionCard';
import styles from './CombinationPanel.module.css';

/**
 * Panel lateral que muestra la combinada activa.
 * Dos estados: sin combinada (botón crear) y con combinada (lista de selecciones).
 */
export default function CombinationPanel() {
  const {
    combination,
    loading,
    createCombination,
    removeMatch,
    deleteCombination,
    saveCombination,
  } = useCombination();

  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleDelete = () => {
    if (confirmDelete) {
      deleteCombination();
      setConfirmDelete(false);
    } else {
      setConfirmDelete(true);
      setTimeout(() => setConfirmDelete(false), 3000);
    }
  };

  const selections = combination?.selections || [];

  // Estado 1: No hay combinada activa
  if (!combination) {
    return (
      <div className={styles.panel}>
        <div className={styles.header}>
          <h3 className={styles.title}>Mi Combinada</h3>
        </div>
        <div className={styles.emptyState}>
          <span className={styles.emptyIcon}>📋</span>
          <p className={styles.emptyText}>No tienes una combinada activa</p>
          <button
            className={styles.createBtn}
            onClick={createCombination}
            disabled={loading}
          >
            {loading ? 'Creando...' : '+ Crear Combinada'}
          </button>
        </div>
      </div>
    );
  }

  // Estado 2: Combinada activa
  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h3 className={styles.title}>Mi Combinada</h3>
        <span className={styles.badge}>{selections.length}</span>
      </div>

      <div className={styles.body}>
        {selections.length === 0 ? (
          <div className={styles.emptySelections}>
            <p>Tu combinada está vacía.</p>
            <p className={styles.hint}>Selecciona partidos para agregarlos.</p>
          </div>
        ) : (
          <div className={styles.selectionList}>
            {selections.map((sel) => (
              <SelectionCard
                key={sel.match_id}
                selection={sel}
                onRemove={removeMatch}
              />
            ))}
          </div>
        )}
      </div>

      <div className={styles.footer}>
        {/* Botón guardar combinada en la base de datos */}
        <button
          className={styles.saveBtn}
          onClick={saveCombination}
          disabled={loading || selections.length === 0}
          title={selections.length === 0 ? 'Agrega al menos un partido para guardar' : 'Guardar combinada en la base de datos'}
        >
          {loading ? 'Guardando...' : 'Guardar Combinada'}
        </button>

        <button
          className={`${styles.deleteBtn} ${confirmDelete ? styles.confirmDelete : ''}`}
          onClick={handleDelete}
          disabled={loading}
        >
          {confirmDelete ? '¿Confirmar eliminación?' : 'Eliminar Combinada'}
        </button>
      </div>
    </div>
  );
}
