<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-beige via-white to-soft-pink/20 flex items-center justify-center">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-soft-pink/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gentle-mint/10 rounded-full blur-3xl"></div>
    </div>
    
    <BaseCard variant="celebration" class="w-full max-w-md mx-4 text-center">
      <!-- Loading State -->
      <div v-if="loading" class="space-y-6">
        <div class="flex justify-center">
          <div class="relative">
            <div class="w-16 h-16 border-4 border-light-coral/20 border-t-light-coral rounded-full animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-6 h-6 text-light-coral" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-xl font-primary font-semibold text-gray-800">
            Welcome to your pregnancy journey!
          </h2>
          <p class="text-gray-600 font-secondary">
            We're setting up your account and getting everything ready for you...
          </p>
        </div>
        
        <!-- Progress dots -->
        <div class="flex justify-center space-x-2">
          <div class="w-2 h-2 bg-light-coral rounded-full animate-pulse"></div>
          <div class="w-2 h-2 bg-light-coral/60 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
          <div class="w-2 h-2 bg-light-coral/40 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
        </div>
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="space-y-6">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-gentle-mint/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-gentle-mint" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-xl font-primary font-semibold text-gray-800">
            Welcome aboard!
          </h2>
          <p class="text-gray-600 font-secondary">
            Your account is ready. Let's start your pregnancy journey together!
          </p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="space-y-6">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-xl font-primary font-semibold text-gray-800">
            Something went wrong
          </h2>
          <p class="text-gray-600 font-secondary">
            {{ error }}
          </p>
        </div>
        
        <BaseButton
          variant="default"
          size="lg"
          class="w-full"
          @click="router.push('/auth/login')"
        >
          Try signing in again
        </BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  auth: false
})

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const loading = ref(true)
const success = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    // Show loading state for a pleasant UX
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Handle OAuth callback parameters
    const { access_token, refresh_token, error: authError } = route.query
    
    if (authError) {
      throw new Error(authError as string)
    }
    
    if (access_token) {
      // OAuth success - update auth store
      try {
        await auth.initialize()
        if (auth.isLoggedIn.value) {
          success.value = true
          
          // Wait a moment to show success state
          await new Promise(resolve => setTimeout(resolve, 1500))
          
          // Check if user needs to complete setup
          const user = auth.currentUser.value
          if (!user?.is_profile_complete) {
            await router.push('/setup/profile')
          } else if (!user?.has_pregnancy_data) {
            await router.push('/setup/pregnancy')
          } else {
            await router.push('/')
          }
        } else {
          throw new Error('Failed to authenticate user')
        }
      } catch (err) {
        console.error('OAuth callback error:', err)
        throw new Error('Authentication failed. Please try signing in again.')
      }
    } else {
      // Regular callback - check if user is authenticated
      try {
        await auth.initialize()
        if (auth.isLoggedIn.value) {
          success.value = true
          await new Promise(resolve => setTimeout(resolve, 1000))
          await router.push('/')
        } else {
          throw new Error('No active session found')
        }
      } catch (err) {
        console.error('Session check error:', err)
        await router.push('/auth/login?message=session-expired')
      }
    }
  } catch (err) {
    console.error('Callback error:', err)
    if (err instanceof Error) {
      if (err.message.includes('access_denied')) {
        error.value = 'Authentication was cancelled. Please try again to continue with your pregnancy journey.'
      } else if (err.message.includes('email_not_confirmed')) {
        error.value = 'Please check your email and confirm your account before signing in.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'An unexpected error occurred during authentication. Please try again.'
    }
  } finally {
    loading.value = false
  }
})
</script>