import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  base: "/app/",
  optimizeDeps: {
    exclude: ["codemirror",],
  },
  build: {
    chunkSizeWarningLimit: 1024
  },
});
