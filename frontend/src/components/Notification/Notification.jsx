import { useNotification } from '../../context/NotificationContext';
import styles from './Notification.module.css';

/**
 * Toast notifications — se renderea en la esquina inferior derecha.
 * Se monta una sola vez en App.jsx.
 */
export default function Notification() {
  const { notifications, dismiss } = useNotification();

  if (notifications.length === 0) return null;

  return (
    <div className={styles.container}>
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`${styles.toast} ${styles[n.type]}`}
          onClick={() => dismiss(n.id)}
        >
          <span className={styles.icon}>
            {n.type === 'success' && '✓'}
            {n.type === 'error' && '✕'}
            {n.type === 'info' && 'ℹ'}
          </span>
          <span className={styles.message}>{n.message}</span>
        </div>
      ))}
    </div>
  );
}
