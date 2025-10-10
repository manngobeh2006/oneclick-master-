import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy any request that starts with /api to the FastAPI container named "api"
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
  }
});

