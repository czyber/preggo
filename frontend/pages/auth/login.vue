<template>
  <BaseCard variant="warm" class="w-full">
    <div class="space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-primary font-semibold text-gray-800">
          Welcome back
        </h2>
        <p class="text-gray-600 font-secondary">
          Continue your pregnancy journey with us
        </p>
      </div>
      
      <!-- Error Alert -->
      <BaseAlert 
        v-if="error" 
        variant="destructive" 
        :description="error"
        dismissible
        @dismiss="error = ''"
      />
      
      <!-- Login Form -->
      <form class="space-y-5" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            id="email"
            v-model="email"
            type="email"
            label="Email address"
            placeholder="Enter your email"
            autocomplete="email"
            variant="default"
            :error="emailError"
            required
          />
          
          <BaseInput
            id="password"
            v-model="password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            autocomplete="current-password"
            variant="default"
            :error="passwordError"
            required
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
              class="h-4 w-4 text-soft-pink focus:ring-soft-pink/50 border-warm-beige rounded"
            />
            <label for="remember-me" class="text-sm text-gray-600 font-secondary">
              Remember me
            </label>
          </div>

          <NuxtLink 
            to="/auth/forgot-password" 
            class="text-sm font-medium text-soft-pink hover:text-soft-pink/80 transition-colors"
          >
            Forgot password?
          </NuxtLink>
        </div>

        <BaseButton
          type="submit"
          variant="default"
          size="lg"
          class="w-full"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Signing in...' : 'Sign in to your account' }}
        </BaseButton>
      </form>

      <!-- Sign up link -->
      <div class="text-center pt-4 border-t border-warm-beige/40">
        <p class="text-sm text-gray-600 font-secondary">
          New to Preggo?
          <NuxtLink 
            to="/auth/signup" 
            class="font-medium text-soft-pink hover:text-soft-pink/80 transition-colors ml-1"
          >
            Create your account
          </NuxtLink>
        </p>
      </div>
      
      <!-- OAuth Options (for future implementation) -->
      <div class="space-y-3">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-warm-beige/40"></div>
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-card px-2 text-gray-500 font-secondary">Or continue with</span>
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-3">
          <BaseButton
            variant="outline"
            size="default"
            class="w-full"
            disabled
          >
            <svg class="w-4 h-4 mr-2" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="default"
            class="w-full"
            disabled
          >
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            Facebook
          </BaseButton>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'guest',
  middleware: 'guest'
})

const auth = useAuth()
const router = useRouter()

// Form state
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = computed(() => auth.loading.value)
const error = ref('')

// Form validation
const emailError = ref('')
const passwordError = ref('')

const isFormValid = computed(() => {
  return email.value.trim() && 
         password.value.trim() && 
         !emailError.value && 
         !passwordError.value
})

// Validate email format
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    emailError.value = 'Email is required'
  } else if (!emailRegex.test(email.value)) {
    emailError.value = 'Please enter a valid email address'
  } else {
    emailError.value = ''
  }
}

// Validate password
const validatePassword = () => {
  if (!password.value.trim()) {
    passwordError.value = 'Password is required'
  } else if (password.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters'
  } else {
    passwordError.value = ''
  }
}

// Watch for input changes to validate
watch(email, validateEmail)
watch(password, validatePassword)

const handleSubmit = async () => {
  // Clear previous errors
  error.value = ''
  
  // Validate form
  validateEmail()
  validatePassword()
  
  if (!isFormValid.value) {
    error.value = 'Please correct the errors above'
    return
  }

  try {
    await auth.login({
      email: email.value.trim(),
      password: password.value
    })

    // Show success message briefly
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Successful login, redirect to dashboard
    await router.push('/')
  } catch (err) {
    if (err instanceof Error) {
      if (err.message.includes('Invalid credentials')) {
        error.value = 'Invalid email or password. Please try again.'
      } else if (err.message.includes('Email not confirmed')) {
        error.value = 'Please check your email and confirm your account before signing in.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'An unexpected error occurred. Please try again.'
    }
    console.error('Login error:', err)
  }
}

// Redirect if already authenticated
onMounted(async () => {
  try {
    // Initialize auth state
    await auth.initialize()
    
    // Check if user is already authenticated
    if (auth.isLoggedIn.value) {
      await router.push('/')
      return
    }
  } catch (err) {
    // User is not authenticated, stay on login page
    console.log('User not authenticated, staying on login page')
  }
})
</script>
