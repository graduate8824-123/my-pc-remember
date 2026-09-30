

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],

  server: {
    host: '127.0.0.1',

    // Keep Vite HMR on the normal connection.
    hmr: true,
  },

  resolve: {
    alias: {
      '@': '.',
    },
  },
});