<template>
  <BaseCard variant="supportive" class="w-full">
    <div class="space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-primary font-semibold text-gray-800">
          Start your journey
        </h2>
        <p class="text-gray-600 font-secondary">
          Create your account to begin tracking your pregnancy with support and care
        </p>
      </div>
      
      <!-- Success Alert -->
      <BaseAlert 
        v-if="success" 
        variant="success" 
        :description="success"
        dismissible
        @dismiss="success = ''"
      />
      
      <!-- Error Alert -->
      <BaseAlert 
        v-if="error" 
        variant="destructive" 
        :description="error"
        dismissible
        @dismiss="error = ''"
      />
      
      <!-- Signup Form -->
      <form class="space-y-5" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            id="full-name"
            v-model="fullName"
            type="text"
            label="Full name"
            placeholder="Enter your full name"
            autocomplete="name"
            variant="supportive"
            :error="fullNameError"
            required
          />
          
          <BaseInput
            id="email"
            v-model="email"
            type="email"
            label="Email address"
            placeholder="Enter your email"
            autocomplete="email"
            variant="supportive"
            :error="emailError"
            required
          />
          
          <BaseInput
            id="password"
            v-model="password"
            type="password"
            label="Password"
            placeholder="Create a password (min. 6 characters)"
            autocomplete="new-password"
            variant="supportive"
            :error="passwordError"
            hint="Choose a secure password with at least 6 characters"
            required
          />
          
          <BaseInput
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            label="Confirm password"
            placeholder="Confirm your password"
            autocomplete="new-password"
            variant="supportive"
            :error="confirmPasswordError"
            required
          />
        </div>

        <!-- Terms Agreement -->
        <div class="flex items-start space-x-3">
          <input
            id="agree-terms"
            v-model="agreeTerms"
            type="checkbox"
            class="mt-1 h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-warm-beige rounded"
            required
          />
          <label for="agree-terms" class="text-sm text-gray-700 font-secondary leading-relaxed">
            I agree to Preggo's 
            <NuxtLink to="/terms" class="text-gentle-mint hover:text-gentle-mint/80 underline">
              Terms of Service
            </NuxtLink>
            and 
            <NuxtLink to="/privacy" class="text-gentle-mint hover:text-gentle-mint/80 underline">
              Privacy Policy
            </NuxtLink>
          </label>
        </div>

        <BaseButton
          type="submit"
          variant="supportive"
          size="lg"
          class="w-full"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Creating your account...' : 'Create your Preggo account' }}
        </BaseButton>
      </form>

      <!-- Sign in link -->
      <div class="text-center pt-4 border-t border-gentle-mint/20">
        <p class="text-sm text-gray-600 font-secondary">
          Already have an account?
          <NuxtLink 
            to="/auth/login" 
            class="font-medium text-gentle-mint hover:text-gentle-mint/80 transition-colors ml-1"
          >
            Sign in instead
          </NuxtLink>
        </p>
      </div>
      
      <!-- OAuth Options (for future implementation) -->
      <div class="space-y-3">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gentle-mint/20"></div>
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-card px-2 text-gray-500 font-secondary">Or sign up with</span>
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

// Using unified auth composable and comprehensive form validation
const auth = useAuth()
const router = useRouter()

// Form state
const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreeTerms = ref(false)
const loading = computed(() => auth.loading.value)
const error = ref('')
const success = ref('')

// Form validation errors
const fullNameError = ref('')
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

// Form validation functions
const validateFullName = () => {
  if (!fullName.value.trim()) {
    fullNameError.value = 'Full name is required'
  } else if (fullName.value.trim().length < 2) {
    fullNameError.value = 'Full name must be at least 2 characters'
  } else {
    fullNameError.value = ''
  }
}

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

const validatePassword = () => {
  if (!password.value) {
    passwordError.value = 'Password is required'
  } else if (password.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters'
  } else if (!/(?=.*[a-z])/.test(password.value)) {
    passwordError.value = 'Password should contain at least one lowercase letter'
  } else if (!/(?=.*\d)/.test(password.value)) {
    passwordError.value = 'Password should contain at least one number'
  } else {
    passwordError.value = ''
  }
}

const validateConfirmPassword = () => {
  if (!confirmPassword.value) {
    confirmPasswordError.value = 'Please confirm your password'
  } else if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match'
  } else {
    confirmPasswordError.value = ''
  }
}

// Watch for input changes to validate
watch(fullName, validateFullName)
watch(email, validateEmail)
watch(password, () => {
  validatePassword()
  // Re-validate confirm password when password changes
  if (confirmPassword.value) {
    validateConfirmPassword()
  }
})
watch(confirmPassword, validateConfirmPassword)

const isFormValid = computed(() => {
  return fullName.value.trim() &&
         email.value.trim() &&
         password.value &&
         confirmPassword.value &&
         password.value === confirmPassword.value &&
         agreeTerms.value &&
         !fullNameError.value &&
         !emailError.value &&
         !passwordError.value &&
         !confirmPasswordError.value
})

const handleSubmit = async () => {
  // Clear previous messages
  error.value = ''
  success.value = ''
  
  // Validate all fields
  validateFullName()
  validateEmail()
  validatePassword()
  validateConfirmPassword()
  
  if (!isFormValid.value) {
    error.value = 'Please correct the errors above'
    return
  }

  try {
    // Split full name into first and last name
    const nameParts = fullName.value.trim().split(' ')
    const firstName = nameParts[0] || ''
    const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : ''

    await auth.register({
      email: email.value.trim(),
      password: password.value,
      first_name: firstName,
      last_name: lastName
    })

    success.value = 'Welcome to Preggo! Please check your email to confirm your account before signing in.'
    
    // Clear form
    fullName.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    agreeTerms.value = false

    // Redirect to login page after a delay
    setTimeout(() => {
      router.push('/auth/login?message=account-created')
    }, 4000)
  } catch (err) {
    if (err instanceof Error) {
      if (err.message.includes('already registered')) {
        error.value = 'An account with this email already exists. Please sign in instead.'
      } else if (err.message.includes('invalid email')) {
        error.value = 'Please enter a valid email address.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'An unexpected error occurred. Please try again.'
    }
    console.error('Signup error:', err)
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
    // User is not authenticated, stay on signup page
    console.log('User not authenticated, staying on signup page')
  }
})
</script>