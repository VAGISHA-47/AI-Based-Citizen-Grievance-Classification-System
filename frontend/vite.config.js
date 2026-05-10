import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),

    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false,          // manual per-domain registration
      includeAssets: ['favicon.svg', 'icons/*.svg'],

      manifest: {
        name: 'JanSetu',
        short_name: 'JanSetu',
        description: 'Smart AI-powered civic grievance system for India',
        theme_color: '#009DC4',
        background_color: '#E1F5FE',
        display: 'standalone',
        orientation: 'portrait-primary',
        start_url: '/',
        scope: '/',
        icons: [
          { src: '/icons/icon-192.svg', sizes: '192x192', type: 'image/svg+xml', purpose: 'any maskable' },
          { src: '/icons/icon-512.svg', sizes: '512x512', type: 'image/svg+xml', purpose: 'any maskable' },
        ],
      },

      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,svg,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            urlPattern: /^https:\/\/api\.jansetu\.in\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'jansetu-api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 5 },
              networkTimeoutSeconds: 10,
            },
          },
        ],
      },

      devOptions: {
        enabled: true,
        type: 'module',
      },
    }),
  ],

  // Force Vite to properly pre-bundle react-countup (fixes CJS/ESM interop crash)
  optimizeDeps: {
    include: ['react-countup'],
  },

  server: {
    port: 5173,
    middlewareMode: false,
    // Custom middleware to inject portal detection via data attribute
    async configResolved(config) {
      return config;
    },
  },
})
