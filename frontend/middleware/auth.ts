/**
 * Authentication middleware for protecting routes
 * 
 * Ensures user is authenticated before accessing protected routes
 * Redirects to login page if not authenticated
 */

export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()
  
  // If user is not authenticated, redirect to login
  if (!user.value) {
    // Store the intended destination for redirect after login
    const redirectTo = to.fullPath !== '/auth/login' ? to.fullPath : undefined
    
    return navigateTo({
      path: '/auth/login',
      query: redirectTo ? { redirect: redirectTo } : {}
    })
  }
})