/**
 * Guest middleware for redirecting authenticated users
 * 
 * Redirects authenticated users away from guest-only pages like login/signup
 * to the main application
 */

export default defineNuxtRouteMiddleware(() => {
  const user = useSupabaseUser()
  
  // If user is authenticated, redirect away from guest pages
  if (user.value) {
    return navigateTo('/')
  }
})