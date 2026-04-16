import styles from './RiskIndicator.module.css';

export default function RiskIndicator({ level, message }) {
  const config = {
    low: { icon: '✅', label: 'Riesgo bajo', className: styles.low },
    medium: { icon: '⚠️', label: 'Riesgo medio', className: styles.medium },
    high: { icon: '❌', label: 'Riesgo alto', className: styles.high },
  };
  const c = config[level] || config.medium;
  return (
    <div className={`${styles.indicator} ${c.className}`}>
      <span className={styles.icon}>{c.icon}</span>
      <div>
        <div className={styles.label}>{c.label}</div>
        {message && <div className={styles.message}>{message}</div>}
      </div>
    </div>
  );
}
