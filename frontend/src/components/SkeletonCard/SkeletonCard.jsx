import styles from './SkeletonCard.module.css';
export default function SkeletonCard() {
  return (
    <div className={styles.skeleton}>
      <div className={styles.line + ' ' + styles.wide} />
      <div className={styles.line + ' ' + styles.medium} />
      <div className={styles.line + ' ' + styles.narrow} />
    </div>
  );
}
