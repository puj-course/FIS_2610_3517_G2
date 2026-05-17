import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

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
          <NavLink
            to="/history"
            className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
          >
            Historial
          </NavLink>
        </nav>

        <div className={styles.auth}>
          {isAuthenticated ? (
            <>
              <span className={styles.username}>{user?.username}</span>
              <button onClick={handleLogout} className={styles.logoutBtn}>
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={styles.authLink}>
                Ingresar
              </NavLink>
              <NavLink to="/register" className={styles.registerBtn}>
                Registrarse
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
