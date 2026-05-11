import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Necesario para que Docker exponga el servidor al host
    host: '0.0.0.0',
    proxy: {
      '/api': {
        // En Docker: apunta al servicio "backend" de docker-compose
        // En local sin Docker: apunta a localhost:8000
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
