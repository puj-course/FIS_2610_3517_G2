import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Notification from './components/Notification/Notification';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import { NotificationProvider } from './context/NotificationContext';
import { CombinationProvider } from './context/CombinationContext';
import Home from './pages/Home/Home';
import MatchDetail from './pages/MatchDetail/MatchDetail';
import CombinationPage from './pages/CombinationPage/CombinationPage';
import CombinationResult from './pages/CombinationResult/CombinationResult';
import History from './pages/History/History';
import NotFound from './pages/NotFound/NotFound';

export default function App() {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <CombinationProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/matches/:id" element={<MatchDetail />} />
              <Route path="/combination" element={<CombinationPage />} />
              <Route path="/combination/:id/result" element={<CombinationResult />} />
              <Route path="/history" element={<History />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            <Notification />
          </Layout>
        </CombinationProvider>
      </NotificationProvider>
    </ErrorBoundary>
  );
}
