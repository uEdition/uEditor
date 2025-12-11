import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  base: "/app/",
  optimizeDeps: {
    exclude: ["codemirror",],
  },
  build: {
    chunkSizeWarningLimit: 1024
  },
});
