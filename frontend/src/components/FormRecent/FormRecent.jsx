import styles from './FormRecent.module.css';
export default function FormRecent({ form, playerName }) {
  if (!form || form.length === 0) return null;
  const wins = form.filter(r => r === 'W').length;
  const streak = form.reduceRight((acc, r) => { if (acc.done) return acc; if (r === acc.type || !acc.type) return { type: r, count: acc.count + 1, done: false }; return { ...acc, done: true }; }, { type: null, count: 0, done: false });
  return (
    <div className={styles.form}>
      <div className={styles.pills}>{form.map((r, i) => <span key={i} className={`${styles.pill} ${r === 'W' ? styles.win : styles.loss}`}>{r}</span>)}</div>
      <div className={styles.info}><span>{wins}/{form.length} victorias</span>{streak.count > 1 && <span className={styles.streak}>{streak.count} {streak.type === 'W' ? 'victorias' : 'derrotas'} seguidas</span>}</div>
    </div>
  );
}
