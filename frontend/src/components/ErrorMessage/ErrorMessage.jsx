import styles from './ErrorMessage.module.css';
export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className={styles.error}>
      <span className={styles.icon}>⚠️</span>
      <p className={styles.message}>{message || 'Ha ocurrido un error'}</p>
      {onRetry && <button className={styles.retry} onClick={onRetry}>Reintentar</button>}
    </div>
  );
}
