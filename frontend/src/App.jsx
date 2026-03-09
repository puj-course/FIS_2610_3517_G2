import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Notification from './components/Notification/Notification';
import { NotificationProvider } from './context/NotificationContext';
import { CombinationProvider } from './context/CombinationContext';
import Home from './pages/Home/Home';

/**
 * Placeholder para rutas futuras.
 */
function ComingSoon({ title }) {
  return (
    <div style={{
      textAlign: 'center',
      padding: '4rem 1.5rem',
      color: 'var(--text-secondary)',
    }}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
        {title}
      </h2>
      <p>Próximamente — Sprint 2 y 3</p>
    </div>
  );
}

export default function App() {
  return (
    <NotificationProvider>
      <CombinationProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/matches/:id" element={<ComingSoon title="Detalle del Partido" />} />
            <Route path="/combination" element={<ComingSoon title="Mi Combinada" />} />
            <Route path="/combination/:id/result" element={<ComingSoon title="Resultado de la Combinada" />} />
            <Route path="*" element={<ComingSoon title="404 — Página no encontrada" />} />
          </Routes>
          <Notification />
        </Layout>
      </CombinationProvider>
    </NotificationProvider>
  );
}
