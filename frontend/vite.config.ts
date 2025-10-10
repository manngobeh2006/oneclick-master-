import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuration for both development and production
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: "http://api:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  define: {
    // Make API URL configurable for production
    'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
  }
});

