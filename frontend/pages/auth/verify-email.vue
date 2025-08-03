<template>
  <BaseCard variant="celebration" class="w-full">
    <div class="space-y-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center space-y-6">
        <div class="flex justify-center">
          <div class="relative">
            <div class="w-16 h-16 border-4 border-light-coral/20 border-t-light-coral rounded-full animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-6 h-6 text-light-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="space-y-2">
          <h2 class="text-2xl font-primary font-semibold text-gray-800">
            Verifying your email
          </h2>
          <p class="text-gray-600 font-secondary">
            Please wait while we confirm your email address...
          </p>
        </div>
      </div>
      
      <!-- Success State -->
      <div v-else-if="success" class="text-center space-y-6">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-gentle-mint/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-gentle-mint" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-2xl font-primary font-semibold text-gray-800">
            Email verified successfully!
          </h2>
          <p class="text-gray-600 font-secondary">
            Welcome to Preggo! Your email has been confirmed and your account is now active.
          </p>
        </div>
        
        <BaseAlert
          variant="celebration"
          title="Your pregnancy journey begins now!"
          description="You can now sign in and start tracking your pregnancy milestones, symptoms, and special moments."
        />
        
        <BaseButton
          variant="celebration"
          size="lg"
          class="w-full"
          @click="router.push('/auth/login?message=email-verified')"
        >
          Continue to sign in
        </BaseButton>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center space-y-6">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-2xl font-primary font-semibold text-gray-800">
            Verification failed
          </h2>
          <p class="text-gray-600 font-secondary">
            {{ error }}
          </p>
        </div>
        
        <BaseAlert
          variant="destructive"
          title="Don't worry, we can help!"
          description="If your verification link has expired or isn't working, we can send you a new one."
        />
        
        <div class="space-y-3">
          <BaseButton
            variant="supportive"
            size="lg"
            class="w-full"
            @click="resendVerification"
            :disabled="resendLoading || resendCooldown > 0"
          >
            {{ resendLoading ? 'Sending...' : resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Send new verification email' }}
          </BaseButton>
          
          <BaseButton
            variant="outline"
            size="default"
            class="w-full"
            @click="router.push('/auth/login')"
          >
            Back to login
          </BaseButton>
        </div>
      </div>
      
      <!-- Manual Verification Request -->
      <div v-else class="text-center space-y-6">
        <div class="flex justify-center">
          <div class="w-16 h-16 bg-soft-pink/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-soft-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"></path>
            </svg>
          </div>
        </div>
        
        <div class="space-y-3">
          <h2 class="text-2xl font-primary font-semibold text-gray-800">
            Verify your email
          </h2>
          <p class="text-gray-600 font-secondary">
            Enter your email address to receive a verification link and activate your Preggo account.
          </p>
        </div>
        
        <form class="space-y-4" @submit.prevent="handleManualVerification">
          <BaseInput
            id="email"
            v-model="email"
            type="email"
            label="Email address"
            placeholder="Enter your email address"
            autocomplete="email"
            variant="celebration"
            :error="emailError"
            required
          />
          
          <BaseButton
            type="submit"
            variant="celebration"
            size="lg"
            class="w-full"
            :disabled="manualLoading || !isEmailValid"
          >
            {{ manualLoading ? 'Sending verification...' : 'Send verification email' }}
          </BaseButton>
        </form>
      </div>
      
      <!-- Help section -->
      <div class="bg-light-coral/10 rounded-xl p-4 space-y-2">
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-light-coral flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h4 class="font-primary font-medium text-gray-800 text-sm">Having trouble?</h4>
        </div>
        <ul class="text-xs text-gray-600 font-secondary space-y-1 ml-6">
          <li>• Check your spam or junk folder</li>
          <li>• Make sure you're using the correct email address</li>
          <li>• Verification links expire after 24 hours</li>
          <li>• Contact support if you continue having issues</li>
        </ul>
        <NuxtLink 
          to="/support"
          class="inline-flex items-center text-xs font-medium text-light-coral hover:text-light-coral/80 transition-colors ml-6"
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

// State management
const loading = ref(false)
const success = ref(false)
const error = ref('')

// Manual verification form
const email = ref('')
const emailError = ref('')
const manualLoading = ref(false)

// Resend functionality
const resendLoading = ref(false)
const resendCooldown = ref(0)
let resendTimer: NodeJS.Timeout | null = null

// Get verification token from URL
const verificationToken = computed(() => route.query.token as string)
const routeEmail = computed(() => route.query.email as string)

// Email validation
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

const isEmailValid = computed(() => {
  return email.value.trim() && !emailError.value
})

// Verify email with token
const verifyEmailToken = async (token: string) => {
  loading.value = true
  error.value = ''
  
  try {
    const api = useApi()
    const { data, error: apiError } = await api.verifyEmail({
      token
    })
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    success.value = true
  } catch (err) {
    console.error('Email verification error:', err)
    if (err instanceof Error) {
      if (err.message.includes('expired')) {
        error.value = 'This verification link has expired. Please request a new verification email.'
      } else if (err.message.includes('invalid') || err.message.includes('not found')) {
        error.value = 'This verification link is invalid or has already been used.'
      } else if (err.message.includes('already verified')) {
        error.value = 'This email address has already been verified. You can sign in now.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'Unable to verify email. Please try again or request a new verification link.'
    }
  } finally {
    loading.value = false
  }
}

// Manual verification request
const handleManualVerification = async () => {
  error.value = ''
  validateEmail()
  
  if (!isEmailValid.value) {
    return
  }
  
  manualLoading.value = true
  
  try {
    const api = useApi()
    const { error: apiError } = await api.sendVerificationEmail({
      email: email.value.trim()
    })
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    success.value = true
    startResendCooldown()
  } catch (err) {
    console.error('Send verification error:', err)
    if (err instanceof Error) {
      if (err.message.includes('already verified')) {
        error.value = 'This email is already verified. You can sign in now.'
      } else if (err.message.includes('not found')) {
        error.value = 'No account found with this email address. Please sign up first.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'Unable to send verification email. Please try again.'
    }
  } finally {
    manualLoading.value = false
  }
}

// Resend verification
const resendVerification = async () => {
  if (resendCooldown.value > 0) return
  
  const emailToUse = routeEmail.value || email.value
  if (!emailToUse) {
    error.value = 'Please provide an email address to resend verification.'
    return
  }
  
  resendLoading.value = true
  error.value = ''
  
  try {
    const api = useApi()
    const { error: apiError } = await api.sendVerificationEmail({
      email: emailToUse
    })
    
    if (apiError) {
      throw new Error(apiError)
    }
    
    success.value = true
    error.value = ''
    startResendCooldown()
  } catch (err) {
    console.error('Resend verification error:', err)
    error.value = 'Failed to resend verification email. Please try again.'
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

// Initialize page
onMounted(async () => {
  // Pre-fill email from route if available
  if (routeEmail.value) {
    email.value = routeEmail.value
  }
  
  // If we have a verification token, try to verify immediately
  if (verificationToken.value) {
    await verifyEmailToken(verificationToken.value)
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
/* State transition animations */
.state-enter-active,
.state-leave-active {
  transition: all 0.4s ease;
}

.state-enter-from,
.state-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Success celebration animation */
@keyframes celebrate {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.success-celebration {
  animation: celebrate 0.6s ease-in-out;
}

/* Loading pulse effect */
.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>