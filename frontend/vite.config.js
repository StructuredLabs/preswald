import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
  build: {
    outDir: path.join(path.dirname(__dirname), 'preswald', 'static'),
    emptyOutDir: true,
  },
  publicDir: 'public',
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8501', // Forward API requests to FastAPI
    },
  },
});
