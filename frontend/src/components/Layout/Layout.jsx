import Navbar from '../Navbar/Navbar';
import styles from './Layout.module.css';

export default function Layout({ children }) {
  return (
    <div className={styles.layout}>
      <Navbar />
      <main className={styles.main}>{children}</main>
      <footer className={styles.footer}>
        OddsEngine © 2026 — Pontificia Universidad Javeriana — Fundamentos de Ingeniería de Software
      </footer>
    </div>
  );
}
