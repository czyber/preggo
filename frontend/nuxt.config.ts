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
    transpile: ['estree-walker'] // Force transpilation of problematic packages
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
    }
  },
  typescript: {
    strict: true
  },
  // Remove global auth middleware - we'll apply it per page as needed
  googleFonts: {
    families: {
      Inter: [400, 500, 600, 700],
      Poppins: [300, 400, 500, 600, 700],
      Roboto: [300, 400, 500, 700],
      Lato: [400]
    },
    display: 'swap',
    preload: true
  }
})
