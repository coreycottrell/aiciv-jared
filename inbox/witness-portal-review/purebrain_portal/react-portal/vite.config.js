import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/react/',
  build: {
    outDir: 'dist',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8097',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8097',
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
