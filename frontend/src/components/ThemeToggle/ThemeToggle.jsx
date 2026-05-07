import { useState, useEffect } from 'react';
import styles from './ThemeToggle.module.css';

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <button className={styles.toggle} onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')} aria-label="Cambiar tema" title={theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
