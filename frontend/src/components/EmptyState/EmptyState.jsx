import styles from './EmptyState.module.css';
export default function EmptyState({ icon = '📋', title, message, action, onAction }) {
  return (
    <div className={styles.empty}>
      <span className={styles.icon}>{icon}</span>
      <h3 className={styles.title}>{title}</h3>
      {message && <p className={styles.message}>{message}</p>}
      {action && onAction && <button className={styles.button} onClick={onAction}>{action}</button>}
    </div>
  );
}
