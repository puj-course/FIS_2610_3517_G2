import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * Envuelve rutas que requieren autenticación.
 * Redirige a /login si no hay sesión activa.
 * Muestra nada mientras se verifica la sesión (loading).
 */
export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null; // Evita flash mientras se verifica el token
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
