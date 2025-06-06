import { defineConfig } from "vite";
import path from "path";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  base: "./",
  build: {
    target: 'esnext',
    outDir: path.join(path.dirname(__dirname), "preswald", "static"),
    emptyOutDir: true,
  },
  publicDir: "public",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": "http://localhost:8501", // Forward API requests to FastAPI
    },
  },
  worker: {
    format: 'es',          // "es" enables top-level await
  },
});
