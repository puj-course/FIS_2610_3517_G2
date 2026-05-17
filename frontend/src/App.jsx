import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Notification from './components/Notification/Notification';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import { NotificationProvider } from './context/NotificationContext';
import { CombinationProvider } from './context/CombinationContext';
import { AuthProvider } from './context/AuthContext';
import Home from './pages/Home/Home';
import MatchDetail from './pages/MatchDetail/MatchDetail';
import CombinationPage from './pages/CombinationPage/CombinationPage';
import CombinationResult from './pages/CombinationResult/CombinationResult';
import History from './pages/History/History';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import NotFound from './pages/NotFound/NotFound';

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <NotificationProvider>
          <CombinationProvider>
            <Layout>
              <Routes>
                {/* Rutas públicas */}
                <Route path="/" element={<Home />} />
                <Route path="/matches/:id" element={<MatchDetail />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Rutas protegidas */}
                <Route path="/combination" element={
                  <ProtectedRoute><CombinationPage /></ProtectedRoute>
                } />
                <Route path="/combination/:id/result" element={
                  <ProtectedRoute><CombinationResult /></ProtectedRoute>
                } />
                <Route path="/history" element={
                  <ProtectedRoute><History /></ProtectedRoute>
                } />

                <Route path="*" element={<NotFound />} />
              </Routes>
              <Notification />
            </Layout>
          </CombinationProvider>
        </NotificationProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
