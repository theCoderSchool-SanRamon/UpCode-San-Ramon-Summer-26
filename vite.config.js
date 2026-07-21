// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  // Register the Vue plugin to compile Single File Components (.vue)
  plugins: [vue()],
  
  // Configure path aliases (e.g., using '@' to point to the 'src' directory)
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  // Development server settings
  server: {
    host: false,
    port: 3000,       // Change the default port if needed
    open: false,       // Automatically open the app in your browser on start
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Proxy API calls to your backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
