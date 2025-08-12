// https://nuxt.com/docs/api/configuration/nuxt-config
import { resolve } from 'path'

export default defineNuxtConfig({
  devtools: { enabled: false }, // Disable devtools for production build
  components: {
    dirs: [
      {
        path: '~/components',
        pathPrefix: false,
        global: true
      }
    ]
  },
  build: {
    transpile: ['estree-walker'], // Force transpilation of problematic packages
  },
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/google-fonts',
    '@vueuse/nuxt'
  ],
  pinia: {
    autoImports: ['defineStore', 'storeToRefs']
  },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      appName: process.env.NUXT_PUBLIC_APP_NAME || 'Preggo',
      appVersion: process.env.NUXT_PUBLIC_APP_VERSION || '0.1.0',
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseAnonKey: process.env.SUPABASE_ANON_KEY
    }
  },
  ssr: false,
  nitro: {
    experimental: {
      wasm: true
    },
    compressPublicAssets: {
      gzip: true,
      brotli: true
    },
    routeRules: {
      // Static assets with long cache headers
      '/images/**': { headers: { 'Cache-Control': 'max-age=31536000, immutable' } },
      '/fonts/**': { headers: { 'Cache-Control': 'max-age=31536000, immutable' } },
      // API routes with shorter cache
      '/api/**': { headers: { 'Cache-Control': 'max-age=300' } },
      // App routes with balanced caching
      '/**': { headers: { 'Cache-Control': 'max-age=3600' } }
    }
  },
  typescript: {
    typeCheck: false // Disable type checking for build
  },
  vite: {
    build: {
      // Optimize bundle splitting for pregnancy app performance
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      },
      target: 'es2020', // Modern target for smaller bundles
      minify: 'esbuild', // Faster minification
      cssMinify: true,
      // Performance budgets
      chunkSizeWarningLimit: 500, // 500KB chunks warning
      assetsInlineLimit: 4096 // 4KB inline limit
    },
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        '@vueuse/core',
        'pinia'
      ],
      exclude: [
        // Exclude heavy components for lazy loading
        './components/feed/MilestoneCelebration.vue',
        './components/feed/VirtualHug.vue'
      ]
    }
  },
  experimental: {
    payloadExtraction: false, // Reduce bundle size
    componentIslands: true // Enable component islands for better performance
  },
  googleFonts: {
    families: {
      Inter: [400, 500, 600, 700],
      Poppins: [400, 500, 600] // Reduce font weights for performance
    },
    display: 'swap',
    preload: true,
    download: true, // Download fonts for better performance
    base64: false, // Don't inline fonts to reduce bundle size
    stylePath: 'css/fonts.css',
    fontsDir: 'fonts',
    overwriting: false
  },
})
