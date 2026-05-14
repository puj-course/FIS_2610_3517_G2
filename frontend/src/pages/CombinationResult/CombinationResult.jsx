import { useParams, useNavigate } from 'react-router-dom';
import useCombinationResult from '../../hooks/useCombinationResult';
import ResultCard from '../../components/ResultCard/ResultCard';
import RiskIndicator from '../../components/RiskIndicator/RiskIndicator';
import ProbabilityChart from '../../components/ProbabilityChart/ProbabilityChart';
import ErrorMessage from '../../components/ErrorMessage/ErrorMessage';
import { exportCombinationResult } from '../../services/apiClient';
import styles from './CombinationResult.module.css';

export default function CombinationResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { result, loading, error } = useCombinationResult(id);

  const handleExport = async () => {
    try {
      const data = await exportCombinationResult(id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = `oddsengine_result_${id}.json`; a.click();
    } catch (e) { alert('Error al exportar: ' + e.message); }
  };

  if (loading) return <div className={styles.loading}>Calculando resultado...</div>;
  if (error) return <ErrorMessage message={error} />;
  if (!result) return <ErrorMessage message="Resultado no encontrado" />;

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => navigate('/')}>← Volver</button>
      <h1 className={styles.title}>Resultado de la combinada</h1>
      <ResultCard probability={result.total_probability} selectionsCount={result.selections?.length || 0} />
      <RiskIndicator level={result.risk_level} message={result.message} />
      {result.match_probabilities && <ProbabilityChart matches={result.match_probabilities} />}
      <div className={styles.actions}>
        <button className={styles.exportBtn} onClick={handleExport}>Exportar JSON</button>
        <button className={styles.copyBtn} onClick={() => { navigator.clipboard.writeText(`OddsEngine: ${Math.round(result.total_probability)}% — ${result.risk_level}`); }}>Copiar resumen</button>
      </div>
    </div>
  );
}
