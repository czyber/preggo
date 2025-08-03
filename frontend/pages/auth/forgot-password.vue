<template>
  <BaseCard variant="calming" class="w-full">
    <div class="space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-primary font-semibold text-gray-800">
          Reset your password
        </h2>
        <p class="text-gray-600 font-secondary">
          Don't worry, it happens! Enter your email and we'll send you a link to reset your password.
        </p>
      </div>
      
      <!-- Success Alert -->
      <BaseAlert 
        v-if="success" 
        variant="success" 
        :title="successTitle"
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
      
      <!-- Reset Form -->
      <form v-if="!success" class="space-y-5" @submit.prevent="handleSubmit">
        <BaseInput
          id="email"
          v-model="email"
          type="email"
          label="Email address"
          placeholder="Enter the email associated with your account"
          autocomplete="email"
          variant="calming"
          :error="emailError"
          hint="We'll send password reset instructions to this email"
          required
        />

        <BaseButton
          type="submit"
          variant="calming"
          size="lg"
          class="w-full"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Sending reset link...' : 'Send password reset link' }}
        </BaseButton>
      </form>
      
      <!-- Success Actions -->
      <div v-if="success" class="space-y-4">
        <BaseButton
          variant="calming"
          size="lg"
          class="w-full"
          @click="resendEmail"
          :disabled="resendLoading || resendCooldown > 0"
        >
          {{ resendLoading ? 'Sending...' : resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend email' }}
        </BaseButton>
        
        <div class="text-center">
          <p class="text-sm text-gray-600 font-secondary">
            Didn't receive the email? Check your spam folder or try a different email address.
          </p>
        </div>
      </div>

      <!-- Back to login -->
      <div class="text-center pt-4 border-t border-muted-lavender/20">
        <p class="text-sm text-gray-600 font-secondary">
          Remember your password?
          <NuxtLink 
            to="/auth/login" 
            class="font-medium text-muted-lavender hover:text-muted-lavender/80 transition-colors ml-1"
          >
            Sign in instead
          </NuxtLink>
        </p>
      </div>
      
      <!-- Help section -->
      <div class="bg-muted-lavender/10 rounded-xl p-4 space-y-2">
        <h4 class="font-primary font-medium text-gray-800 text-sm">Need help?</h4>
        <p class="text-xs text-gray-600 font-secondary leading-relaxed">
          If you're still having trouble accessing your account, please contact our support team. 
          We're here to help you continue your pregnancy journey safely.
        </p>
        <NuxtLink 
          to="/support"
          class="inline-flex items-center text-xs font-medium text-muted-lavender hover:text-muted-lavender/80 transition-colors"
        >
          Contact Support
          <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
          </svg>
        </NuxtLink>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'guest',
  auth: false
})

const router = useRouter()
const route = useRoute()

// Form state
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const successTitle = ref('')

// Resend functionality
const resendLoading = ref(false)
const resendCooldown = ref(0)
let resendTimer: NodeJS.Timeout | null = null

// Form validation
const emailError = ref('')

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

watch(email, validateEmail)

const isFormValid = computed(() => {
  return email.value.trim() && !emailError.value
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  
  validateEmail()
  
  if (!isFormValid.value) {
    error.value = 'Please enter a valid email address'
    return
  }

  loading.value = true

  try {
    // This would typically call an API endpoint to send password reset email
    const api = useApi()
    const { data, error: apiError } = await api.sendPasswordReset({
      email: email.value.trim()
    })
    
    if (apiError) {
      throw new Error(apiError)
    }

    successTitle.value = 'Reset link sent!'
    success.value = `We've sent password reset instructions to ${email.value}. Please check your email and follow the link to reset your password.`
    
    // Start resend cooldown
    startResendCooldown()
  } catch (err) {
    console.error('Password reset error:', err)
    if (err instanceof Error) {
      if (err.message.includes('User not found')) {
        error.value = 'No account found with this email address. Please check your email or create a new account.'
      } else if (err.message.includes('rate limit')) {
        error.value = 'Too many reset attempts. Please wait a few minutes before trying again.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'Unable to send reset email. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const resendEmail = async () => {
  if (resendCooldown.value > 0) return
  
  resendLoading.value = true
  error.value = ''
  
  try {
    const api = useApi()
    const { error: apiError } = await api.sendPasswordReset({
      email: email.value.trim()
    })
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    success.value = `Reset instructions sent again to ${email.value}. Please check your email.`
    startResendCooldown()
  } catch (err) {
    console.error('Resend error:', err)
    error.value = 'Failed to resend email. Please try again.'
  } finally {
    resendLoading.value = false
  }
}

const startResendCooldown = () => {
  resendCooldown.value = 60 // 60 seconds cooldown
  resendTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(resendTimer!)
      resendTimer = null
    }
  }, 1000)
}

// Check for pre-filled email from route query
onMounted(() => {
  const routeEmail = route.query.email as string
  if (routeEmail && typeof routeEmail === 'string') {
    email.value = routeEmail
  }
})

// Cleanup timer on unmount
onUnmounted(() => {
  if (resendTimer) {
    clearInterval(resendTimer)
  }
})
</script>

<style scoped>
/* Additional pregnancy-themed animations */
.success-enter-active,
.success-leave-active {
  transition: all 0.3s ease;
}

.success-enter-from,
.success-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>