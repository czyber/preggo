<template>
  <BaseCard variant="calming" class="w-full">
    <div class="space-y-6">
      <!-- Header -->
      <div class="text-center space-y-2">
        <h2 class="text-2xl font-primary font-semibold text-gray-800">
          Create new password
        </h2>
        <p class="text-gray-600 font-secondary">
          Choose a secure password to keep your pregnancy journey safe and private.
        </p>
      </div>
      
      <!-- Success Alert -->
      <BaseAlert 
        v-if="success" 
        variant="success" 
        title="Password updated successfully!"
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
      
      <!-- Token Validation Error -->
      <BaseAlert 
        v-if="tokenError" 
        variant="destructive" 
        title="Invalid or expired reset link"
        :description="tokenError"
      >
        <template #footer>
          <div class="flex flex-col sm:flex-row gap-3 mt-4">
            <BaseButton
              variant="outline"
              size="sm"
              class="flex-1"
              @click="router.push('/auth/forgot-password')"
            >
              Request new link
            </BaseButton>
            <BaseButton
              variant="default"
              size="sm"
              class="flex-1"
              @click="router.push('/auth/login')"
            >
              Back to login
            </BaseButton>
          </div>
        </template>
      </BaseAlert>
      
      <!-- Reset Form -->
      <form v-if="!success && !tokenError" class="space-y-5" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            id="password"
            v-model="password"
            type="password"
            label="New password"
            placeholder="Create a secure password"
            autocomplete="new-password"
            variant="calming"
            :error="passwordError"
            hint="Password must be at least 8 characters with letters and numbers"
            required
          />
          
          <BaseInput
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            label="Confirm new password"
            placeholder="Confirm your new password"
            autocomplete="new-password"
            variant="calming"
            :error="confirmPasswordError"
            required
          />
        </div>

        <!-- Password Strength Indicator -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm font-secondary text-gray-600">Password strength:</span>
            <span class="text-sm font-medium" :class="passwordStrengthColor">
              {{ passwordStrengthText }}
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all duration-300"
              :class="passwordStrengthBarColor"
              :style="{ width: `${passwordStrengthPercent}%` }"
            ></div>
          </div>
        </div>

        <BaseButton
          type="submit"
          variant="calming"
          size="lg"
          class="w-full"
          :disabled="loading || !isFormValid"
        >
          {{ loading ? 'Updating password...' : 'Update password' }}
        </BaseButton>
      </form>
      
      <!-- Success Actions -->
      <div v-if="success" class="space-y-4">
        <BaseButton
          variant="calming"
          size="lg"
          class="w-full"
          @click="router.push('/auth/login')"
        >
          Continue to sign in
        </BaseButton>
      </div>

      <!-- Back to login -->
      <div v-if="!success && !tokenError" class="text-center pt-4 border-t border-muted-lavender/20">
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
      
      <!-- Security note -->
      <div class="bg-muted-lavender/10 rounded-xl p-4 space-y-2">
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-muted-lavender flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          <h4 class="font-primary font-medium text-gray-800 text-sm">Security tips</h4>
        </div>
        <ul class="text-xs text-gray-600 font-secondary space-y-1 ml-6">
          <li>• Choose a unique password you don't use elsewhere</li>
          <li>• Include a mix of letters, numbers, and symbols</li>
          <li>• Consider using a password manager</li>
          <li>• Never share your password with anyone</li>
        </ul>
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
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const tokenError = ref('')

// Form validation
const passwordError = ref('')
const confirmPasswordError = ref('')

// Get reset token from URL
const resetToken = computed(() => route.query.token as string)

// Password strength calculation
const passwordStrength = computed(() => {
  if (!password.value) return 0
  
  let strength = 0
  const checks = [
    password.value.length >= 8,
    /[a-z]/.test(password.value),
    /[A-Z]/.test(password.value),
    /\d/.test(password.value),
    /[!@#$%^&*(),.?":{}|<>]/.test(password.value),
    password.value.length >= 12
  ]
  
  strength = checks.filter(Boolean).length
  return Math.min(strength, 5)
})

const passwordStrengthPercent = computed(() => {
  return (passwordStrength.value / 5) * 100
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'Too weak'
  if (strength <= 2) return 'Weak'
  if (strength <= 3) return 'Fair'
  if (strength <= 4) return 'Good'
  return 'Strong'
})

const passwordStrengthColor = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'text-red-500'
  if (strength <= 2) return 'text-red-500'
  if (strength <= 3) return 'text-orange-500'
  if (strength <= 4) return 'text-blue-500'
  return 'text-green-500'
})

const passwordStrengthBarColor = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'bg-gray-300'
  if (strength <= 2) return 'bg-red-400'
  if (strength <= 3) return 'bg-orange-400'
  if (strength <= 4) return 'bg-blue-400'
  return 'bg-green-400'
})

// Form validation functions
const validatePassword = () => {
  if (!password.value) {
    passwordError.value = 'Password is required'
  } else if (password.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
  } else if (!/(?=.*[a-z])/.test(password.value)) {
    passwordError.value = 'Password must contain at least one lowercase letter'
  } else if (!/(?=.*\d)/.test(password.value)) {
    passwordError.value = 'Password must contain at least one number'
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
watch(password, () => {
  validatePassword()
  // Re-validate confirm password when password changes
  if (confirmPassword.value) {
    validateConfirmPassword()
  }
})
watch(confirmPassword, validateConfirmPassword)

const isFormValid = computed(() => {
  return password.value &&
         confirmPassword.value &&
         password.value === confirmPassword.value &&
         passwordStrength.value >= 2 &&
         !passwordError.value &&
         !confirmPasswordError.value
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  
  // Validate all fields
  validatePassword()
  validateConfirmPassword()
  
  if (!isFormValid.value) {
    error.value = 'Please correct the errors above'
    return
  }

  if (!resetToken.value) {
    tokenError.value = 'Missing reset token. Please use the link from your email.'
    return
  }

  loading.value = true

  try {
    // This would typically call an API endpoint to reset the password
    const api = useApi()
    const { data, error: apiError } = await api.resetPassword({
      token: resetToken.value,
      password: password.value
    })
    
    if (apiError) {
      throw new Error(apiError)
    }

    success.value = 'Your password has been successfully updated! You can now sign in with your new password.'
  } catch (err) {
    console.error('Password reset error:', err)
    if (err instanceof Error) {
      if (err.message.includes('expired') || err.message.includes('invalid')) {
        tokenError.value = 'This reset link has expired or is invalid. Please request a new password reset link.'
      } else if (err.message.includes('weak password')) {
        error.value = 'Password is too weak. Please choose a stronger password.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = 'Unable to reset password. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

// Validate token on mount
onMounted(async () => {
  if (!resetToken.value) {
    tokenError.value = 'No reset token provided. Please use the link from your password reset email.'
    return
  }

  // Optionally validate token with backend
  try {
    const api = useApi()
    const { error: validationError } = await api.validateResetToken({
      token: resetToken.value
    })
    
    if (validationError) {
      tokenError.value = 'This reset link has expired or is invalid. Please request a new password reset link.'
    }
  } catch (err) {
    console.error('Token validation error:', err)
    tokenError.value = 'Unable to validate reset link. Please request a new password reset link.'
  }
})
</script>

<style scoped>
/* Password strength animations */
.password-strength-bar {
  transition: width 0.3s ease, background-color 0.3s ease;
}

/* Form animations */
.form-enter-active,
.form-leave-active {
  transition: all 0.3s ease;
}

.form-enter-from,
.form-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>