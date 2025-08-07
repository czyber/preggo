import type { User, Session } from '@supabase/supabase-js'
import type { components } from '@/types/api'

// Type aliases for cleaner code
type UserProfile = components['schemas']['UserResponse'] | null
type LoginRequest = components['schemas']['LoginRequest']
type RegisterRequest = components['schemas']['RegisterRequest']

interface AuthState {
  user: User | null
  userProfile: UserProfile
  session: Session | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

/**
 * Unified authentication composable for Preggo app
 * 
 * Integrates Supabase auth with FastAPI user profiles, providing:
 * - Session persistence across browser refreshes
 * - Automatic token refresh with proper scheduling
 * - Cross-tab session synchronization
 * - Integration with existing FastAPI backend
 * - Unified auth state management
 */
export const useAuth = () => {
  const supabase = useSupabase()
  
  // Persistent auth state using Nuxt's useState for SSR compatibility
  const authState = useState<AuthState>('auth.state', () => ({
    user: null,
    userProfile: null,
    session: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }))

  // Computed properties for easier access
  const user = computed(() => authState.value.user)
  const userProfile = computed(() => authState.value.userProfile)
  const session = computed(() => authState.value.session)
  const isAuthenticated = computed(() => authState.value.isAuthenticated)
  const loading = computed(() => authState.value.loading)
  const error = computed(() => authState.value.error)
  const isLoggedIn = computed(() => authState.value.isAuthenticated && authState.value.user !== null)

  // Token refresh interval reference
  let tokenRefreshInterval: NodeJS.Timeout | null = null
  
  // Guard flags to prevent infinite loops
  let isInitializing = false
  let lastProfileFetch = 0
  const PROFILE_FETCH_DEBOUNCE = 5000 // 5 seconds

  /**
   * Initialize auth state from existing session with enhanced recovery
   */
  const initialize = async (): Promise<void> => {
    // Prevent multiple concurrent initializations
    if (isInitializing) {
      console.log('🔄 Auth initialization already in progress, skipping...')
      return
    }
    
    try {
      isInitializing = true
      authState.value.loading = true
      authState.value.error = null
      
      console.log('🚀 Starting auth initialization...')

      // Get current session from Supabase
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      
      if (sessionError) {
        console.warn('Session retrieval error:', sessionError)
        await clearAuthState()
        return
      }

      if (session?.user) {
        // Check if session is expired
        const now = Math.floor(Date.now() / 1000)
        const expiresAt = session.expires_at || 0
        
        if (expiresAt > 0 && now >= expiresAt) {
          console.log('Session expired, attempting refresh...')
          try {
            await refreshSession()
            return // refreshSession will handle state setup if successful
          } catch (refreshError) {
            console.warn('Session refresh failed during initialization:', refreshError)
            await clearAuthState()
            return
          }
        }
        
        // Session is valid, set up auth state
        await setAuthState(session.user, session)
        
        // Try to fetch user profile, but don't fail initialization if it fails
        try {
          await fetchUserProfile()
        } catch (profileError) {
          console.warn('Failed to fetch user profile during initialization:', profileError)
          // Continue with initialization even if profile fetch fails
        }
        
        setupTokenRefresh()
      } else {
        // No session found, check for stored session as fallback
        if (process.client) {
          try {
            const storedSession = localStorage.getItem('supabase-session')
            if (storedSession) {
              const parsedSession = JSON.parse(storedSession)
              // Validate stored session structure
              if (parsedSession?.user && parsedSession?.expires_at) {
                const now = Math.floor(Date.now() / 1000)
                if (parsedSession.expires_at > now) {
                  console.log('Restoring session from storage...')
                  await setAuthState(parsedSession.user, parsedSession)
                  await fetchUserProfile()
                  setupTokenRefresh()
                  return
                }
              }
            }
          } catch (storageError) {
            console.warn('Failed to restore session from storage:', storageError)
          }
        }
        
        await clearAuthState()
      }
    } catch (err) {
      console.error('Auth initialization error:', err)
      authState.value.error = 'Failed to initialize authentication'
      await clearAuthState()
    } finally {
      authState.value.loading = false
      isInitializing = false
      console.log('✅ Auth initialization completed')
    }
  }

  /**
   * Sign up with email and password using Supabase
   */
  const signUp = async (registerData: RegisterRequest): Promise<void> => {
    authState.value.loading = true
    authState.value.error = null

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email: registerData.email,
        password: registerData.password,
        options: {
          data: {
            first_name: registerData.first_name,
            last_name: registerData.last_name
          }
        }
      })

      if (signUpError) {
        throw new Error(signUpError.message)
      }

      if (!data.user) {
        throw new Error('No user returned from signup')
      }

      // For email confirmation flow, user won't be immediately authenticated
      if (!data.session) {
        authState.value.error = null
        return
      }

      await setAuthState(data.user, data.session)
      await fetchUserProfile()
      setupTokenRefresh()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed'
      authState.value.error = errorMessage
      console.error('Signup error:', err)
      throw new Error(errorMessage)
    } finally {
      authState.value.loading = false
    }
  }

  /**
   * Sign in with email and password using Supabase
   */
  const signIn = async (loginData: LoginRequest): Promise<void> => {
    authState.value.loading = true
    authState.value.error = null

    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email: loginData.email,
        password: loginData.password
      })

      if (signInError) {
        throw new Error(signInError.message)
      }

      if (!data.user || !data.session) {
        throw new Error('Invalid login response')
      }

      await setAuthState(data.user, data.session)
      await fetchUserProfile()
      setupTokenRefresh()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed'
      authState.value.error = errorMessage
      console.error('Login error:', err)
      throw new Error(errorMessage)
    } finally {
      authState.value.loading = false
    }
  }

  /**
   * Sign out and clear all auth state
   */
  const signOut = async (): Promise<void> => {
    try {
      authState.value.loading = true
      
      // Sign out from Supabase
      const { error } = await supabase.auth.signOut()
      if (error) {
        console.warn('Supabase signout error:', error)
      }

      // Clear local state regardless of Supabase response
      await clearAuthState()
      clearTokenRefresh()
    } catch (err) {
      console.error('Logout error:', err)
      // Clear local state even if signout fails
      await clearAuthState()
      clearTokenRefresh()
    } finally {
      authState.value.loading = false
    }
  }

  /**
   * Fetch user profile from FastAPI backend
   */
  const fetchUserProfile = async (): Promise<void> => {
    // Debounce profile fetches to prevent rapid successive calls
    const now = Date.now()
    if (now - lastProfileFetch < PROFILE_FETCH_DEBOUNCE) {
      console.log('🔄 Profile fetch debounced, skipping...')
      return
    }
    lastProfileFetch = now
    
    try {
      if (!authState.value.session?.access_token) {
        return
      }
      
      console.log('📡 Fetching user profile...')

      const api = useApi()
      const { data, error: apiError } = await api.getCurrentUser()
      
      if (apiError) {
        console.warn('Failed to fetch user profile:', apiError)
        return
      }
      
      if (data) {
        authState.value.userProfile = data
      }
    } catch (err) {
      console.warn('Error fetching user profile:', err)
      // Don't throw here - profile fetch failing shouldn't break auth
    }
  }

  /**
   * Update user profile in FastAPI backend
   */
  const updateUserProfile = async (userData: components['schemas']['UserUpdate']): Promise<void> => {
    try {
      authState.value.loading = true
      authState.value.error = null

      const api = useApi()
      const { data, error: apiError } = await api.updateCurrentUser(userData)
      
      if (apiError) {
        throw new Error(`Failed to update profile: ${apiError}`)
      }
      
      if (data) {
        authState.value.userProfile = data
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update profile'
      authState.value.error = errorMessage
      console.error('Profile update error:', err)
      throw new Error(errorMessage)
    } finally {
      authState.value.loading = false
    }
  }

  /**
   * Refresh the current session
   */
  const refreshSession = async (): Promise<void> => {
    try {
      const { data, error } = await supabase.auth.refreshSession()
      
      if (error) {
        console.warn('Session refresh error:', error)
        await clearAuthState()
        return
      }

      if (data.session && data.user) {
        await setAuthState(data.user, data.session)
        await fetchUserProfile()
        setupTokenRefresh() // Schedule next refresh
      } else {
        console.warn('No session returned from refresh')
        await clearAuthState()
      }
    } catch (err) {
      console.error('Session refresh failed:', err)
      await clearAuthState()
    }
  }

  /**
   * Set auth state for authenticated user
   */
  const setAuthState = async (newUser: User, newSession: Session): Promise<void> => {
    authState.value.user = newUser
    authState.value.session = newSession
    authState.value.isAuthenticated = true
    authState.value.error = null

    // Store session in browser storage for persistence
    if (process.client) {
      try {
        localStorage.setItem('supabase-session', JSON.stringify(newSession))
      } catch (err) {
        console.warn('Failed to store session in localStorage:', err)
      }
    }
  }

  /**
   * Clear all auth state and browser storage
   */
  const clearAuthState = async (): Promise<void> => {
    authState.value.user = null
    authState.value.userProfile = null
    authState.value.session = null
    authState.value.isAuthenticated = false
    authState.value.error = null

    // Clear browser storage comprehensively
    if (process.client) {
      try {
        // Clear custom session storage
        localStorage.removeItem('supabase-session')
        
        // Clear Supabase's default storage keys
        // These are the keys Supabase typically uses for session persistence
        const supabaseKeys = [
          'sb-auth-token',
          'supabase.auth.token',
          'supabase-auth-token'
        ]
        
        // Try to get the Supabase URL to construct proper storage keys
        const config = useRuntimeConfig()
        const supabaseUrl = config.public.supabaseUrl
        
        if (supabaseUrl) {
          // Extract project reference from URL for more specific cleanup
          const urlParts = supabaseUrl.match(/https:\/\/([^.]+)\.supabase\.co/)
          if (urlParts && urlParts[1]) {
            const projectRef = urlParts[1]
            supabaseKeys.push(`sb-${projectRef}-auth-token`)
          }
        }
        
        // Clear all potential Supabase storage keys
        supabaseKeys.forEach(key => {
          localStorage.removeItem(key)
          sessionStorage.removeItem(key)
        })
        
        // Clear any other auth-related storage
        const allKeys = Object.keys(localStorage)
        allKeys.forEach(key => {
          if (key.includes('supabase') || key.includes('auth') || key.includes('session')) {
            localStorage.removeItem(key)
          }
        })
        
        const allSessionKeys = Object.keys(sessionStorage)
        allSessionKeys.forEach(key => {
          if (key.includes('supabase') || key.includes('auth') || key.includes('session')) {
            sessionStorage.removeItem(key)
          }
        })
        
      } catch (err) {
        console.warn('Failed to clear browser storage:', err)
      }
    }
  }

  /**
   * Setup automatic token refresh with optimal scheduling
   */
  const setupTokenRefresh = (): void => {
    clearTokenRefresh()
    
    if (!authState.value.session?.expires_at) {
      return
    }

    const expiresAt = authState.value.session.expires_at * 1000
    const now = Date.now()
    const timeUntilExpiry = expiresAt - now
    
    // Don't set up refresh if session expires in less than 1 minute
    if (timeUntilExpiry < 60 * 1000) {
      console.warn('Session expires very soon, not setting up refresh')
      return
    }
    
    // Calculate optimal refresh time:
    // - If session lasts more than 1 hour: refresh 10 minutes before expiry
    // - If session lasts 30-60 minutes: refresh 5 minutes before expiry  
    // - If session lasts less than 30 minutes: refresh at 75% of lifetime
    let refreshBuffer: number
    if (timeUntilExpiry > 60 * 60 * 1000) { // More than 1 hour
      refreshBuffer = 10 * 60 * 1000 // 10 minutes
    } else if (timeUntilExpiry > 30 * 60 * 1000) { // 30-60 minutes
      refreshBuffer = 5 * 60 * 1000 // 5 minutes
    } else { // Less than 30 minutes
      refreshBuffer = timeUntilExpiry * 0.25 // 25% before expiry (75% of lifetime)
    }
    
    const refreshAt = expiresAt - refreshBuffer
    const timeUntilRefresh = refreshAt - now

    if (timeUntilRefresh > 0) {
      console.log(`Token refresh scheduled in ${Math.round(timeUntilRefresh / 1000 / 60)} minutes`)
      tokenRefreshInterval = setTimeout(async () => {
        console.log('Refreshing token...')
        await refreshSession()
        // refreshSession will call setupTokenRefresh again if successful
      }, timeUntilRefresh)
    } else {
      // If we're past the refresh time, refresh immediately
      console.log('Token needs immediate refresh')
      refreshSession()
    }
  }

  /**
   * Clear token refresh interval
   */
  const clearTokenRefresh = (): void => {
    if (tokenRefreshInterval) {
      clearTimeout(tokenRefreshInterval)
      tokenRefreshInterval = null
    }
  }

  /**
   * Reset auth state and errors
   */
  const reset = (): void => {
    authState.value.error = null
    authState.value.loading = false
  }

  /**
   * Get auth state debug information for troubleshooting
   */
  const getDebugInfo = () => {
    const session = authState.value.session
    return {
      isAuthenticated: authState.value.isAuthenticated,
      hasUser: !!authState.value.user,
      hasProfile: !!authState.value.userProfile,
      hasSession: !!session,
      sessionExpiry: session?.expires_at ? new Date(session.expires_at * 1000) : null,
      timeUntilExpiry: session?.expires_at ? 
        Math.max(0, (session.expires_at * 1000) - Date.now()) : null,
      refreshScheduled: !!tokenRefreshInterval,
      loading: authState.value.loading,
      error: authState.value.error
    }
  }

  // Listen for Supabase auth changes for cross-tab synchronization
  if (process.client) {
    supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('Auth state change:', event, session?.user?.id)
      
      switch (event) {
        case 'SIGNED_IN':
          if (session?.user) {
            await setAuthState(session.user, session)
            await fetchUserProfile()
            setupTokenRefresh()
          }
          break
          
        case 'SIGNED_OUT':
          await clearAuthState()
          clearTokenRefresh()
          break
          
        case 'TOKEN_REFRESHED':
          if (session?.user) {
            await setAuthState(session.user, session)
            setupTokenRefresh()
          }
          break
          
        case 'USER_UPDATED':
          if (session?.user) {
            authState.value.user = session.user
            await fetchUserProfile()
          }
          break
      }
    })
  }

  // Cleanup on unmount
  onBeforeUnmount(() => {
    clearTokenRefresh()
  })

  return {
    // State
    user: readonly(user),
    userProfile: readonly(userProfile),
    session: readonly(session),
    isAuthenticated: readonly(isAuthenticated),
    loading: readonly(loading),
    error: readonly(error),
    
    // Computed
    isLoggedIn: readonly(isLoggedIn),
    
    // Actions
    initialize,
    signUp,
    signIn,
    signOut,
    updateUserProfile,
    refreshSession,
    reset,
    
    // Debug utilities
    getDebugInfo,
    
    // Legacy compatibility with existing auth store
    register: signUp,
    login: signIn,
    logout: signOut,
    getCurrentUser: fetchUserProfile,
    updateUser: updateUserProfile,
    currentUser: userProfile,
    userPreferences: computed(() => userProfile.value?.preferences || null)
  }
}
