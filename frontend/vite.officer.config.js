import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import fs from 'fs'
import path from 'path'

// Custom Vite plugin to serve the correct HTML in dev mode
function serveCorrectHtmlPlugin() {
  return {
    name: 'serve-officer-html',
    configureServer(server) {
      return () => {
        server.middlewares.use((req, res, next) => {
          // Serve correct HTML for dev mode
          if (req.url === '/' || req.url === '/index.html') {
            const filePath = path.resolve(__dirname, 'index-officer.html')
            const content = fs.readFileSync(filePath, 'utf-8')
            res.setHeader('Content-Type', 'text/html')
            console.log('🟣 OFFICER: Serving index-officer.html')
            return res.end(content)
          }
          next()
        })
      }
    },
  }
}

export default defineConfig({
  root: process.cwd(),
  
  build: {
    rollupOptions: {
      input: 'index-officer.html',
    },
  },

  plugins: [
    serveCorrectHtmlPlugin(),
    react(),

    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false,
      includeAssets: ['favicon.svg', 'icons/*.svg'],

      manifest: {
        name: 'JanSetu Officer',
        short_name: 'JanSetu Officer',
        description: 'Smart AI-powered civic grievance management dashboard for authorities',
        theme_color: '#7C3AED',
        background_color: '#F5F3FF',
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

  optimizeDeps: {
    include: ['react-countup'],
  },

  server: {
    port: 5175,
    strictPort: false,
    host: '0.0.0.0',
  },
})
