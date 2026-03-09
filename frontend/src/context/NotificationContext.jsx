import { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext(null);

let notificationId = 0;

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((message, type = 'info') => {
    const id = ++notificationId;
    setNotifications((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 3500);

    return id;
  }, []);

  const showSuccess = useCallback((msg) => addNotification(msg, 'success'), [addNotification]);
  const showError = useCallback((msg) => addNotification(msg, 'error'), [addNotification]);
  const showInfo = useCallback((msg) => addNotification(msg, 'info'), [addNotification]);

  const dismiss = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, showSuccess, showError, showInfo, dismiss }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error('useNotification debe usarse dentro de NotificationProvider');
  return ctx;
}
