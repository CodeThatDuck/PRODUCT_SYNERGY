import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Allow connections from outside the container
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://product-synergy-backend:8000',
        changeOrigin: true,
      }
    }
  },
  // publicDir defaults to 'public' folder inside frontend/ — correct for this project
})

// Made with Bob
