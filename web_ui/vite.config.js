import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/run_sse': 'http://localhost:8000',
      '/apps': 'http://localhost:8000',
      '/debug': 'http://localhost:8000',
    }
  }
})
