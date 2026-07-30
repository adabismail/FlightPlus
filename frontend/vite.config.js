import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// During local `npm run dev`, proxy API calls to the Django dev server so the
// browser never hits CORS. In Docker, Nginx handles this instead.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
