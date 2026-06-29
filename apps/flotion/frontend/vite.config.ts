import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// The dev server proxies /api to the FastAPI backend so the browser only ever
// talks to one origin. Override the target with FLOTION_API if the backend runs
// elsewhere.
const API_TARGET = process.env.FLOTION_API || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: API_TARGET, changeOrigin: true },
    },
  },
});
