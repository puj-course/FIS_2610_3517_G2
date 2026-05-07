import { NavLink } from 'react-router-dom';
import styles from './Navbar.module.css';

export default function Navbar() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <NavLink to="/" className={styles.logo}>
          <span className={styles.logoIcon}>🎾</span>
          <span className={styles.logoText}>OddsEngine</span>
        </NavLink>

        <nav className={styles.nav}>
          <NavLink
            to="/"
            className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
          >
            Partidos
          </NavLink>
          <NavLink
            to="/combination"
            className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
          >
            Mi Combinada
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
