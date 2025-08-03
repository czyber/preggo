// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/supabase',
    '@nuxtjs/google-fonts',
    '@vueuse/nuxt'
  ],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      appName: process.env.NUXT_PUBLIC_APP_NAME || 'Preggo',
      appVersion: process.env.NUXT_PUBLIC_APP_VERSION || '0.1.0'
    }
  },
  supabase: {
    // We use Supabase for auth only, but integrate with our FastAPI backend for data
    redirectOptions: {
      login: '/auth/login',
      callback: '/auth/callback',
      exclude: ['/', '/auth/signup'],
      include: undefined,
      cookieRedirect: false
    },
    cookieOptions: {
      maxAge: 60 * 60 * 8, // 8 hours
      sameSite: 'lax',
      secure: true
    },
    clientOptions: {
      auth: {
        flowType: 'pkce',
        detectSessionInUrl: true,
        persistSession: true,
        autoRefreshToken: true
      }
    }
  },
  ssr: true,
  typescript: {
    strict: true
  },
  // Remove global auth middleware - we'll apply it per page as needed
  googleFonts: {
    families: {
      Poppins: [300, 400, 500, 600, 700],
      Roboto: [300, 400, 500, 700]
    },
    display: 'swap',
    preload: true
  }
})