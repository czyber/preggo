<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-beige via-white to-muted-lavender/10 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-primary font-semibold text-gray-800 mb-2">
          Complete your profile
        </h1>
        <p class="text-gray-600 font-secondary">
          Help us personalize your pregnancy journey with a few more details
        </p>
      </div>
      
      <!-- Progress Indicator -->
      <div class="mb-8">
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center opacity-50">
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span class="ml-2 text-sm font-secondary text-gray-600">Pregnancy</span>
          </div>
          <div class="w-16 h-0.5 bg-gray-300"></div>
          <div class="flex items-center">
            <div class="w-8 h-8 bg-muted-lavender rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span class="ml-2 text-sm font-secondary text-gray-600">Profile Setup</span>
          </div>
        </div>
      </div>
      
      <!-- Profile Form -->
      <BaseCard variant="calming" class="w-full">
        <div class="space-y-6">
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
          
          <!-- Form -->
          <form class="space-y-6" @submit.prevent="handleSubmit">
            <!-- Basic Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-primary font-semibold text-gray-800">Personal Information</h3>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <BaseInput
                  id="first-name"
                  v-model="firstName"
                  type="text"
                  label="First name"
                  placeholder="Your first name"
                  variant="calming"
                  :error="firstNameError"
                  required
                />
                
                <BaseInput
                  id="last-name"
                  v-model="lastName"
                  type="text"
                  label="Last name"
                  placeholder="Your last name"
                  variant="calming"
                  :error="lastNameError"
                  required
                />
              </div>
              
              <BaseInput
                id="phone"
                v-model="phone"
                type="tel"
                label="Phone number (Optional)"
                placeholder="+1 (555) 123-4567"
                variant="calming"
                :error="phoneError"
                hint="For appointment reminders and emergency contacts"
              />
            </div>
            
            <!-- Birth Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-primary font-semibold text-gray-800">Birth Information</h3>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <BaseInput
                  id="birth-date"
                  v-model="birthDate"
                  type="date"
                  label="Date of birth (Optional)"
                  variant="calming"
                  :error="birthDateError"
                  hint="Helps us provide age-appropriate guidance"
                />
                
                <div>
                  <label for="height" class="block text-sm font-medium text-gray-700 font-primary mb-2">
                    Height (Optional)
                  </label>
                  <div class="flex space-x-2">
                    <BaseInput
                      id="height-feet"
                      v-model="heightFeet"
                      type="number"
                      placeholder="5"
                      variant="calming"
                      class="flex-1"
                      min="3"
                      max="8"
                    />
                    <span class="flex items-center text-gray-500 font-secondary">ft</span>
                    <BaseInput
                      id="height-inches"
                      v-model="heightInches"
                      type="number"
                      placeholder="6"
                      variant="calming"
                      class="flex-1"
                      min="0"
                      max="11"
                    />
                    <span class="flex items-center text-gray-500 font-secondary">in</span>
                  </div>
                  <p class="text-xs text-gray-600 font-secondary mt-1">For BMI calculations and weight tracking</p>
                </div>
              </div>
            </div>
            
            <!-- Preferences -->
            <div class="space-y-4">
              <h3 class="text-lg font-primary font-semibold text-gray-800">Preferences</h3>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 font-primary mb-3">
                  Preferred measurement units
                </label>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <label class="flex items-center space-x-3 p-3 border border-muted-lavender/30 rounded-xl hover:bg-muted-lavender/5 cursor-pointer transition-colors">
                    <input
                      v-model="measurementSystem"
                      type="radio"
                      value="imperial"
                      class="h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">Imperial</div>
                      <div class="text-sm text-gray-600 font-secondary">Pounds, feet, inches</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center space-x-3 p-3 border border-muted-lavender/30 rounded-xl hover:bg-muted-lavender/5 cursor-pointer transition-colors">
                    <input
                      v-model="measurementSystem"
                      type="radio"
                      value="metric"
                      class="h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">Metric</div>
                      <div class="text-sm text-gray-600 font-secondary">Kilograms, centimeters</div>
                    </div>
                  </label>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 font-primary mb-3">
                  Notification preferences
                </label>
                <div class="space-y-3">
                  <label class="flex items-center space-x-3">
                    <input
                      v-model="notificationPreferences"
                      type="checkbox"
                      value="weekly_updates"
                      class="h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300 rounded"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">Weekly development updates</div>
                      <div class="text-sm text-gray-600 font-secondary">Learn about your baby's growth each week</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center space-x-3">
                    <input
                      v-model="notificationPreferences"
                      type="checkbox"
                      value="appointment_reminders"
                      class="h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300 rounded"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">Appointment reminders</div>
                      <div class="text-sm text-gray-600 font-secondary">Get notified about upcoming appointments</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center space-x-3">
                    <input
                      v-model="notificationPreferences"
                      type="checkbox"
                      value="milestone_celebrations"
                      class="h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300 rounded"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">Milestone celebrations</div>
                      <div class="text-sm text-gray-600 font-secondary">Celebrate special pregnancy moments</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
            
            <!-- Emergency Contact (Optional) -->
            <div class="space-y-4">
              <h3 class="text-lg font-primary font-semibold text-gray-800">Emergency Contact (Optional)</h3>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <BaseInput
                  id="emergency-name"
                  v-model="emergencyContactName"
                  type="text"
                  label="Contact name"
                  placeholder="Partner, family member, or friend"
                  variant="calming"
                />
                
                <BaseInput
                  id="emergency-phone"
                  v-model="emergencyContactPhone"
                  type="tel"
                  label="Contact phone"
                  placeholder="+1 (555) 123-4567"
                  variant="calming"
                />
              </div>
              
              <BaseInput
                id="emergency-relationship"
                v-model="emergencyContactRelationship"
                type="text"
                label="Relationship"
                placeholder="Partner, mother, sister, friend"
                variant="calming"
              />
            </div>
            
            <!-- Privacy Agreement -->
            <div class="bg-muted-lavender/10 rounded-xl p-4 space-y-3">
              <div class="flex items-start space-x-3">
                <input
                  id="privacy-agreement"
                  v-model="acceptedPrivacy"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-muted-lavender focus:ring-muted-lavender/50 border-gray-300 rounded"
                  required
                />
                <label for="privacy-agreement" class="text-sm text-gray-700 font-secondary leading-relaxed">
                  I understand that my personal health information will be stored securely and used only to provide 
                  personalized pregnancy tracking services. I can update or delete my information at any time.
                  <NuxtLink to="/privacy" class="text-muted-lavender hover:text-muted-lavender/80 underline ml-1">
                    Read our Privacy Policy
                  </NuxtLink>
                </label>
              </div>
            </div>
            
            <!-- Submit Button -->
            <div class="flex flex-col sm:flex-row gap-4 pt-4">
              <BaseButton
                type="button"
                variant="outline"
                size="lg"
                class="flex-1"
                @click="handleSkip"
              >
                Skip for now
              </BaseButton>
              <BaseButton
                type="submit"
                variant="calming"
                size="lg"
                class="flex-1"
                :disabled="loading || !isFormValid"
              >
                {{ loading ? 'Saving profile...' : 'Complete Setup' }}
              </BaseButton>
            </div>
          </form>
          
          <!-- Help Section -->
          <div class="bg-muted-lavender/10 rounded-xl p-4 space-y-2">
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-muted-lavender flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
              <h4 class="font-primary font-medium text-gray-800 text-sm">Your privacy matters</h4>
            </div>
            <ul class="text-xs text-gray-600 font-secondary space-y-1 ml-6">
              <li>• All information is stored securely and encrypted</li>
              <li>• You can edit or delete any information at any time</li>
              <li>• We never share your data with third parties without permission</li>
              <li>• Optional fields help us provide better recommendations</li>
            </ul>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const router = useRouter()
const authStore = useAuthStore()

// Form state
const firstName = ref('')
const lastName = ref('')
const phone = ref('')
const birthDate = ref('')
const heightFeet = ref('')
const heightInches = ref('')
const measurementSystem = ref('imperial')
const notificationPreferences = ref<string[]>(['weekly_updates', 'milestone_celebrations'])
const emergencyContactName = ref('')
const emergencyContactPhone = ref('')
const emergencyContactRelationship = ref('')
const acceptedPrivacy = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')

// Form validation errors
const firstNameError = ref('')
const lastNameError = ref('')
const phoneError = ref('')
const birthDateError = ref('')

// Pre-fill from existing user data
const currentUser = computed(() => authStore.currentUser)

onMounted(() => {
  const user = currentUser.value
  if (user?.full_name) {
    const nameParts = user.full_name.split(' ')
    firstName.value = nameParts[0] || ''
    lastName.value = nameParts.slice(1).join(' ') || ''
  }
  
  // Pre-fill other available data
  phone.value = user?.phone || ''
  birthDate.value = user?.birth_date || ''
  measurementSystem.value = user?.measurement_system || 'imperial'
  
  if (user?.notification_preferences) {
    notificationPreferences.value = user.notification_preferences
  }
})

// Form validation
const validateForm = () => {
  firstNameError.value = ''
  lastNameError.value = ''
  phoneError.value = ''
  birthDateError.value = ''
  
  if (!firstName.value.trim()) {
    firstNameError.value = 'First name is required'
  } else if (firstName.value.trim().length < 2) {
    firstNameError.value = 'First name must be at least 2 characters'
  }
  
  if (!lastName.value.trim()) {
    lastNameError.value = 'Last name is required'
  } else if (lastName.value.trim().length < 2) {
    lastNameError.value = 'Last name must be at least 2 characters'
  }
  
  if (phone.value && !isValidPhone(phone.value)) {
    phoneError.value = 'Please enter a valid phone number'
  }
  
  if (birthDate.value) {
    const birth = new Date(birthDate.value)
    const today = new Date()
    const age = today.getFullYear() - birth.getFullYear()
    
    if (birth > today) {
      birthDateError.value = 'Birth date cannot be in the future'
    } else if (age < 13 || age > 100) {
      birthDateError.value = 'Please enter a valid birth date'
    }
  }
}

const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  const cleanPhone = phone.replace(/[\s\-\(\)]/g, '')
  return phoneRegex.test(cleanPhone) && cleanPhone.length >= 10
}

watch([firstName, lastName, phone, birthDate], validateForm)

const isFormValid = computed(() => {
  return firstName.value.trim() &&
         lastName.value.trim() &&
         acceptedPrivacy.value &&
         !firstNameError.value &&
         !lastNameError.value &&
         !phoneError.value &&
         !birthDateError.value
})

const calculateHeightInCm = (): number | null => {
  if (heightFeet.value && heightInches.value) {
    const feet = parseInt(heightFeet.value)
    const inches = parseInt(heightInches.value)
    return Math.round((feet * 12 + inches) * 2.54)
  }
  return null
}

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  validateForm()
  
  if (!isFormValid.value) {
    error.value = 'Please correct the errors above'
    return
  }
  
  loading.value = true
  
  try {
    const profileData = {
      full_name: `${firstName.value.trim()} ${lastName.value.trim()}`,
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      phone: phone.value.trim() || null,
      birth_date: birthDate.value || null,
      height_cm: calculateHeightInCm(),
      measurement_system: measurementSystem.value,
      notification_preferences: notificationPreferences.value,
      emergency_contact_name: emergencyContactName.value.trim() || null,
      emergency_contact_phone: emergencyContactPhone.value.trim() || null,
      emergency_contact_relationship: emergencyContactRelationship.value.trim() || null,
      is_profile_complete: true,
      privacy_accepted: true,
      privacy_accepted_at: new Date().toISOString()
    }
    
    await authStore.updateUser(profileData)
    
    success.value = 'Profile completed successfully!'
    
    // Wait a moment to show success message
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Redirect to dashboard
    await router.push('/?message=profile-complete')
  } catch (err) {
    console.error('Profile setup error:', err)
    if (err instanceof Error) {
      error.value = err.message
    } else {
      error.value = 'Failed to save profile. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const handleSkip = async () => {
  try {
    // Mark profile as complete with minimal data
    await authStore.updateUser({
      full_name: `${firstName.value.trim() || 'User'} ${lastName.value.trim() || ''}`.trim(),
      is_profile_complete: true
    })
    
    await router.push('/?message=setup-skipped')
  } catch (err) {
    console.error('Skip profile error:', err)
    await router.push('/')
  }
}
</script>

<style scoped>
/* Profile-themed styling */
.profile-setup {
  background: linear-gradient(135deg, rgba(225, 190, 231, 0.1), rgba(255, 243, 224, 0.1));
}

/* Height input styling */
.height-inputs input {
  text-align: center;
}

/* Checkbox and radio styling */
input[type="checkbox"]:checked,
input[type="radio"]:checked {
  background-color: #E1BEE7;
  border-color: #E1BEE7;
}

/* Phone input formatting */
input[type="tel"] {
  font-variant-numeric: tabular-nums;
}

/* Emergency contact section subtle styling */
.emergency-contact {
  border-left: 4px solid rgba(225, 190, 231, 0.3);
  padding-left: 1rem;
}
</style>
