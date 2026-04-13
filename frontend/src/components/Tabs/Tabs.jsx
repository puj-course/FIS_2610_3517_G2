import { useState } from 'react';
import styles from './Tabs.module.css';

export default function Tabs({ tabs, defaultTab = 0 }) {
  const [active, setActive] = useState(defaultTab);
  return (
    <div className={styles.tabs}>
      <div className={styles.tabList}>
        {tabs.map((tab, i) => (
          <button key={i} className={`${styles.tab} ${active === i ? styles.active : ''}`} onClick={() => setActive(i)}>
            {tab.label}
          </button>
        ))}
      </div>
      <div className={styles.tabContent}>{tabs[active]?.content}</div>
    </div>
  );
}
