// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
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
  typescript: {
    strict: true
  },
  // Remove global auth middleware - we'll apply it per page as needed
  googleFonts: {
    families: {
      Poppins: [300, 400, 500, 600, 700],
      Roboto: [300, 400, 500, 700],
      Lato: [400]
    },
    display: 'swap',
    preload: true
  }
})
