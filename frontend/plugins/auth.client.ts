/**
 * Auth initialization plugin for client-side
 * 
 * Initializes unified auth state on app startup
 * Ensures consistent auth state across app refresh
 */

export default defineNuxtPlugin(async () => {
  // Only run on client-side
  if (process.server) return

  const auth = useAuth()
  
  try {
    // Initialize auth state from existing session
    await auth.initialize()
  } catch (error) {
    console.warn('Failed to initialize auth on startup:', error)
  }
})