import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5003,
    host: '0.0.0.0',
    hmr: {
      port: 24678,
      host: 'localhost'
    },
    watch: {
      usePolling: true,
      interval: 1000
    },
    proxy: {
      '/api': {
        target: process.env.REACT_APP_API_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material']
        }
      }
    }
  },
  preview: {
    port: 5003,
    host: '0.0.0.0'
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@mui/material', '@mui/icons-material']
  }
})
