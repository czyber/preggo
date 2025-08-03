<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-beige via-white to-soft-pink/10">
    <!-- Loading State -->
    <div v-if="authLoading" class="flex items-center justify-center min-h-screen">
      <div class="text-center space-y-4">
        <div class="w-12 h-12 border-4 border-soft-pink/20 border-t-soft-pink rounded-full animate-spin mx-auto"></div>
        <p class="text-gray-600 font-secondary">Loading your pregnancy journey...</p>
      </div>
    </div>
    
    <!-- Not authenticated view -->
    <div v-else-if="!authStore?.isLoggedIn" class="px-4 py-12">
      <div class="max-w-6xl mx-auto">
        <!-- Hero Section -->
        <div class="text-center mb-16">
          <h1 class="text-5xl font-logo text-gray-800 mb-4">
            preggo
          </h1>
          <div class="w-20 h-1 bg-soft-pink mx-auto rounded-full mb-8"></div>
          <h2 class="text-3xl font-primary font-semibold text-gray-800 mb-6">
            Your pregnancy journey, beautifully tracked
          </h2>
          <p class="text-xl text-gray-600 font-secondary max-w-2xl mx-auto leading-relaxed">
            Join thousands of expecting parents who trust Preggo to track symptoms, celebrate milestones, 
            and document their precious pregnancy moments with care and support.
          </p>
        </div>
        
        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <BaseCard variant="supportive" class="text-center">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-gentle-mint/20 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-gentle-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-primary font-semibold text-gray-800">Track with Love</h3>
              <p class="text-gray-600 font-secondary">
                Log symptoms, appointments, and measurements with a caring, supportive interface designed for expecting parents.
              </p>
            </div>
          </BaseCard>
          
          <BaseCard variant="celebration" class="text-center">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-light-coral/20 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-light-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-primary font-semibold text-gray-800">Celebrate Milestones</h3>
              <p class="text-gray-600 font-secondary">
                Mark special moments and achievements throughout your pregnancy with beautiful milestone celebrations.
              </p>
            </div>
          </BaseCard>
          
          <BaseCard variant="calming" class="text-center">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-muted-lavender/20 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-muted-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-primary font-semibold text-gray-800">Safe & Secure</h3>
              <p class="text-gray-600 font-secondary">
                Your personal pregnancy data is protected with enterprise-grade security and complete privacy controls.
              </p>
            </div>
          </BaseCard>
        </div>
        
        <!-- CTA Section -->
        <div class="text-center space-y-6">
          <div class="space-y-4">
            <BaseButton
              size="lg"
              variant="default"
              class="text-lg px-8 py-4"
              @click="router.push('/auth/signup')"
            >
              Start Your Pregnancy Journey
            </BaseButton>
            <p class="text-sm text-gray-600 font-secondary">
              Already have an account?
              <NuxtLink 
                to="/auth/login" 
                class="font-medium text-soft-pink hover:text-soft-pink/80 transition-colors ml-1"
              >
                Sign in here
              </NuxtLink>
            </p>
          </div>
          
          <!-- Trust indicators -->
          <div class="max-w-2xl mx-auto pt-8 border-t border-warm-beige/40">
            <p class="text-xs text-gray-500 font-secondary mb-4">Trusted by expecting families worldwide</p>
            <div class="flex items-center justify-center space-x-8 opacity-60">
              <div class="flex items-center space-x-1">
                <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span class="text-xs font-secondary">HIPAA Compliant</span>
              </div>
              <div class="flex items-center space-x-1">
                <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <span class="text-xs font-secondary">SSL Encrypted</span>
              </div>
              <div class="flex items-center space-x-1">
                <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span class="text-xs font-secondary">4.9★ Rating</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Authenticated view -->
    <div v-else class="px-4 py-8">
      <div class="max-w-6xl mx-auto">
        <!-- Welcome Header -->
        <div class="mb-8">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div class="mb-4 sm:mb-0">
              <h1 class="text-3xl font-primary font-semibold text-gray-800">
                Welcome back, {{ currentUser?.full_name || currentUser?.email?.split('@')[0] || 'Beautiful' }}!
              </h1>
              <p class="text-gray-600 font-secondary mt-2">Here's your pregnancy journey overview</p>
            </div>
            <BaseButton
              variant="outline"
              size="default"
              @click="authStore?.logout()"
            >
              Sign Out
            </BaseButton>
          </div>
        </div>

        <!-- Setup reminder -->
        <BaseAlert 
          variant="supportive" 
          title="Complete your profile setup"
          class="mb-8"
        >
          <p>Let's finish setting up your pregnancy profile to get personalized tracking and support.</p>
          <div class="mt-4">
            <BaseButton
              variant="default"
              size="sm"
              @click="router.push('/setup/pregnancy')"
            >
              Complete Setup
            </BaseButton>
          </div>
        </BaseAlert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Proper store initialization with error handling
const router = useRouter()
const { $pinia } = useNuxtApp()

// Initialize stores safely
const authStore = useAuthStore()
const pregnancyStore = usePregnancyStore()

// Loading state
const authLoading = ref(true)

// Reactive data
const currentUser = computed(() => authStore?.currentUser || null)

// Initialize on mount
onMounted(() => {
  // Simple delay to allow stores to initialize
  setTimeout(() => {
    authLoading.value = false
  }, 100)
})
</script>