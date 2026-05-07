import { Component } from 'react';
export default class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          <h2 style={{ color: '#f87171', marginBottom: '8px' }}>Algo salió mal</h2>
          <p>{this.state.error?.message || 'Error inesperado'}</p>
          <button onClick={() => window.location.reload()} style={{ marginTop: '16px', padding: '8px 20px', background: 'var(--primary)', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>Recargar</button>
        </div>
      );
    }
    return this.props.children;
  }
}
