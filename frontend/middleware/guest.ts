/**
 * Guest middleware for redirecting authenticated users
 * 
 * Redirects authenticated users away from guest-only pages like login/signup
 * to the main application
 */

export default defineNuxtRouteMiddleware(() => {
  // Skip authentication check on server-side rendering
  if (process.server) return
  
  const auth = useAuth()
  
  // If user is authenticated, redirect away from guest pages
  if (auth.isAuthenticated.value) {
    return navigateTo('/')
  }
})