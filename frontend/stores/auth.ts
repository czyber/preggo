import { defineStore } from 'pinia'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type User = components['schemas']['UserResponse']
type LoginRequest = components['schemas']['LoginRequest']
type RegisterRequest = components['schemas']['RegisterRequest']
type AuthResponse = components['schemas']['AuthResponse']

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    currentUser: (state) => state.user,
    
    isLoggedIn: (state) => state.isAuthenticated && state.user !== null,
    
    userRole: (state) => state.user?.role || null,
    
    userPreferences: (state) => state.user?.preferences || null,
  },

  actions: {
    async login(loginData: LoginRequest) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.login(loginData)
        
        if (error) {
          throw new Error(`Login failed: ${error}`)
        }
        
        if (data) {
          this.user = data.user
          this.isAuthenticated = true
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Login failed'
        console.error('Error during login:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async register(registerData: RegisterRequest) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.register(registerData)
        
        if (error) {
          throw new Error(`Registration failed: ${error}`)
        }
        
        if (data) {
          this.user = data.user
          this.isAuthenticated = true
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Registration failed'
        console.error('Error during registration:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async getCurrentUser() {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getCurrentUser()
        
        if (error) {
          throw new Error(`Failed to get current user: ${error}`)
        }
        
        if (data) {
          this.user = data
          this.isAuthenticated = true
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to get user'
        console.error('Error getting current user:', err)
        this.isAuthenticated = false
        this.user = null
      } finally {
        this.loading = false
      }
    },

    async updateUser(userData: components['schemas']['UserUpdate']) {
      try {
        const api = useApi()
        const { data, error } = await api.updateCurrentUser(userData)
        
        if (error) {
          throw new Error(`Failed to update user: ${error}`)
        }
        
        if (data) {
          this.user = data
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to update user'
        console.error('Error updating user:', err)
        throw err
      }
    },

    async logout() {
      try {
        // Clear local auth state
        this.user = null
        this.isAuthenticated = false
        this.error = null
        
        // Optionally call logout endpoint if it exists
        // const api = useApi()
        // await api.logout()
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Logout failed'
        console.error('Error during logout:', err)
        throw err
      }
    },

    reset() {
      this.user = null
      this.isAuthenticated = false
      this.loading = false
      this.error = null
    }
  }
})