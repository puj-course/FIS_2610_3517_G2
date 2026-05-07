import { useNavigate } from 'react-router-dom';
import styles from './NotFound.module.css';
export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className={styles.page}>
      <div className={styles.code}>404</div>
      <h1 className={styles.title}>Página no encontrada</h1>
      <p className={styles.message}>La página que buscas no existe o fue movida</p>
      <button className={styles.button} onClick={() => navigate('/')}>Volver al inicio</button>
    </div>
  );
}
