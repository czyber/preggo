
<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-beige via-white to-gentle-mint/10 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-primary font-semibold text-gray-800 mb-2">
          Set up your pregnancy
        </h1>
        <p class="text-gray-600 font-secondary">
          Tell us about your pregnancy so we can provide personalized tracking and support
        </p>
      </div>
      
      <!-- Progress Indicator -->
      <div class="mb-8">
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center">
            <div class="w-8 h-8 bg-gentle-mint rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span class="ml-2 text-sm font-secondary text-gray-600">Pregnancy Setup</span>
          </div>
          <div class="w-16 h-0.5 bg-gray-300"></div>
          <div class="flex items-center opacity-50">
            <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span class="text-xs font-medium text-gray-600">2</span>
            </div>
            <span class="ml-2 text-sm font-secondary text-gray-600">Profile</span>
          </div>
        </div>
      </div>
      
      <!-- Setup Form -->
      <BaseCard variant="supportive" class="w-full">
        <div class="space-y-6">
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
            <!-- Due Date or LMP Selection -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 font-primary mb-3">
                  How would you like to calculate your due date?
                </label>
                <div class="space-y-3">
                  <label class="flex items-center space-x-3 p-3 border border-gentle-mint/30 rounded-xl hover:bg-gentle-mint/5 cursor-pointer transition-colors">
                    <input
                      v-model="dateMethod"
                      type="radio"
                      value="due_date"
                      class="h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-gray-300"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">I know my due date</div>
                      <div class="text-sm text-gray-600 font-secondary">Calculated by your healthcare provider</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center space-x-3 p-3 border border-gentle-mint/30 rounded-xl hover:bg-gentle-mint/5 cursor-pointer transition-colors">
                    <input
                      v-model="dateMethod"
                      type="radio"
                      value="lmp"
                      class="h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-gray-300"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">I know my last menstrual period</div>
                      <div class="text-sm text-gray-600 font-secondary">We'll calculate your due date (typical 28-day cycle)</div>
                    </div>
                  </label>
                  
                  <label class="flex items-center space-x-3 p-3 border border-gentle-mint/30 rounded-xl hover:bg-gentle-mint/5 cursor-pointer transition-colors">
                    <input
                      v-model="dateMethod"
                      type="radio"
                      value="conception"
                      class="h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-gray-300"
                    />
                    <div>
                      <div class="font-medium text-gray-800 font-secondary">I know my conception date</div>
                      <div class="text-sm text-gray-600 font-secondary">From IVF, fertility tracking, or other methods</div>
                    </div>
                  </label>
                </div>
              </div>
              
              <!-- Date Input -->
              <div v-if="dateMethod">
                <BaseInput
                  v-if="dateMethod === 'due_date'"
                  id="due-date"
                  v-model="dueDate"
                  type="date"
                  label="Your due date"
                  variant="supportive"
                  :error="dueDateError"
                  hint="This date is provided by your healthcare provider"
                  required
                />
                
                <BaseInput
                  v-else-if="dateMethod === 'lmp'"
                  id="lmp-date"
                  v-model="lmpDate"
                  type="date"
                  label="First day of your last menstrual period"
                  variant="supportive"
                  :error="lmpDateError"
                  hint="We'll calculate your due date as 40 weeks from this date"
                  required
                />
                
                <BaseInput
                  v-else-if="dateMethod === 'conception'"
                  id="conception-date"
                  v-model="conceptionDate"
                  type="date"
                  label="Conception date"
                  variant="supportive"
                  :error="conceptionDateError"
                  hint="We'll calculate your due date as 38 weeks from this date"
                  required
                />
              </div>
              
              <!-- Calculated Due Date Display -->
              <div v-if="calculatedDueDate && dateMethod !== 'due_date'" class="bg-gentle-mint/10 rounded-xl p-4">
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5 text-gentle-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="font-medium text-gray-800 font-secondary">Calculated due date:</span>
                  <span class="font-semibold text-gentle-mint">{{ formatDate(calculatedDueDate) }}</span>
                </div>
                <p class="text-xs text-gray-600 font-secondary mt-1">This is an estimate and may be adjusted by your healthcare provider</p>
              </div>
            </div>
            
            <!-- Current Week Display -->
            <div v-if="currentWeek" class="bg-light-coral/10 rounded-xl p-4">
              <div class="text-center space-y-2">
                <div class="text-2xl font-primary font-bold text-light-coral">
                  Week {{ currentWeek.weeks }}, Day {{ currentWeek.days }}
                </div>
                <div class="text-sm text-gray-600 font-secondary">
                  You're in your {{ getTrimaster() }} trimester
                </div>
              </div>
            </div>
            
            <!-- Optional Information -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 font-primary mb-2">
                  Is this your first pregnancy? (Optional)
                </label>
                <div class="flex space-x-4">
                  <label class="flex items-center space-x-2">
                    <input
                      v-model="isFirstPregnancy"
                      type="radio"
                      :value="true"
                      class="h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-gray-300"
                    />
                    <span class="font-secondary text-gray-700">Yes, my first</span>
                  </label>
                  <label class="flex items-center space-x-2">
                    <input
                      v-model="isFirstPregnancy"
                      type="radio"
                      :value="false"
                      class="h-4 w-4 text-gentle-mint focus:ring-gentle-mint/50 border-gray-300"
                    />
                    <span class="font-secondary text-gray-700">No, I have other children</span>
                  </label>
                </div>
              </div>
              
              <BaseInput
                id="healthcare-provider"
                v-model="healthcareProvider"
                type="text"
                label="Healthcare provider name (Optional)"
                placeholder="Dr. Smith, ABC Medical Center"
                variant="supportive"
                hint="We'll never contact them - this is just for your records"
              />
              
              <div>
                <label for="notes" class="block text-sm font-medium text-gray-700 font-primary mb-2">
                  Any notes about your pregnancy? (Optional)
                </label>
                <textarea
                  id="notes"
                  v-model="notes"
                  rows="3"
                  class="w-full px-4 py-3 border border-gentle-mint/30 rounded-xl focus:ring-2 focus:ring-gentle-mint/50 focus:border-gentle-mint bg-gentle-mint/5 font-secondary"
                  placeholder="Twins, high-risk, special considerations..."
                ></textarea>
              </div>
            </div>
            
            <!-- Submit Button -->
            <div class="flex flex-col sm:flex-row gap-4 pt-4">
              <BaseButton
                type="button"
                variant="outline"
                size="lg"
                class="flex-1"
                @click="router.push('/')"
              >
                Skip for now
              </BaseButton>
              <BaseButton
                type="submit"
                variant="supportive"
                size="lg"
                class="flex-1"
                :disabled="loading || !isFormValid"
              >
                {{ loading ? 'Setting up...' : 'Continue to Profile' }}
              </BaseButton>
            </div>
          </form>
          
          <!-- Help Section -->
          <div class="bg-gentle-mint/10 rounded-xl p-4 space-y-2">
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-gentle-mint flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h4 class="font-primary font-medium text-gray-800 text-sm">Need help with dates?</h4>
            </div>
            <ul class="text-xs text-gray-600 font-secondary space-y-1 ml-6">
              <li>• Due dates are estimates - only about 5% of babies arrive exactly on their due date</li>
              <li>• If you're unsure, your healthcare provider can give you the most accurate date</li>
              <li>• You can always update this information later in your settings</li>
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
const pregnancyStore = usePregnancyStore()

// Form state
const dateMethod = ref('')
const dueDate = ref('')
const lmpDate = ref('')
const conceptionDate = ref('')
const isFirstPregnancy = ref<boolean | null>(null)
const healthcareProvider = ref('')
const notes = ref('')
const loading = ref(false)
const error = ref('')

// Form validation errors
const dueDateError = ref('')
const lmpDateError = ref('')
const conceptionDateError = ref('')

// Date calculations
const calculatedDueDate = computed(() => {
  if (dateMethod.value === 'due_date' && dueDate.value) {
    return dueDate.value
  } else if (dateMethod.value === 'lmp' && lmpDate.value) {
    const lmp = new Date(lmpDate.value)
    const due = new Date(lmp.getTime() + (280 * 24 * 60 * 60 * 1000)) // 40 weeks
    return due.toISOString().split('T')[0]
  } else if (dateMethod.value === 'conception' && conceptionDate.value) {
    const conception = new Date(conceptionDate.value)
    const due = new Date(conception.getTime() + (266 * 24 * 60 * 60 * 1000)) // 38 weeks
    return due.toISOString().split('T')[0]
  }
  return null
})

const currentWeek = computed(() => {
  if (!calculatedDueDate.value) return null
  
  const today = new Date()
  const due = new Date(calculatedDueDate.value)
  const daysDiff = Math.floor((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  const totalDays = 280 - daysDiff // 40 weeks = 280 days
  
  if (totalDays < 0) return null // Before pregnancy starts
  
  return {
    weeks: Math.floor(totalDays / 7),
    days: totalDays % 7,
    total: totalDays
  }
})

// Form validation
const validateDates = () => {
  dueDateError.value = ''
  lmpDateError.value = ''
  conceptionDateError.value = ''
  
  const today = new Date()
  const minDate = new Date(today.getTime() - (365 * 24 * 60 * 60 * 1000)) // 1 year ago
  const maxDate = new Date(today.getTime() + (365 * 24 * 60 * 60 * 1000)) // 1 year ahead
  
  if (dateMethod.value === 'due_date' && dueDate.value) {
    const due = new Date(dueDate.value)
    if (due < today) {
      dueDateError.value = 'Due date should be in the future'
    } else if (due > maxDate) {
      dueDateError.value = 'Due date seems too far in the future'
    }
  }
  
  if (dateMethod.value === 'lmp' && lmpDate.value) {
    const lmp = new Date(lmpDate.value)
    if (lmp > today) {
      lmpDateError.value = 'Last menstrual period should be in the past'
    } else if (lmp < minDate) {
      lmpDateError.value = 'Date seems too far in the past'
    }
  }
  
  if (dateMethod.value === 'conception' && conceptionDate.value) {
    const conception = new Date(conceptionDate.value)
    if (conception > today) {
      conceptionDateError.value = 'Conception date should be in the past'
    } else if (conception < minDate) {
      conceptionDateError.value = 'Date seems too far in the past'
    }
  }
}

watch([dateMethod, dueDate, lmpDate, conceptionDate], validateDates)

const isFormValid = computed(() => {
  return dateMethod.value && 
         calculatedDueDate.value && 
         !dueDateError.value && 
         !lmpDateError.value && 
         !conceptionDateError.value
})

// Helper methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getTrimaster = () => {
  if (!currentWeek.value) return ''
  const weeks = currentWeek.value.weeks
  if (weeks <= 12) return 'first'
  if (weeks <= 27) return 'second'
  return 'third'
}

const getSourceDate = () => {
  switch (dateMethod.value) {
    case 'due_date':
      return dueDate.value
    case 'lmp':
      return lmpDate.value
    case 'conception':
      return conceptionDate.value
    default:
      return null
  }
}

const handleSubmit = async () => {
  error.value = ''
  validateDates()
  
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields correctly'
    return
  }
  
  loading.value = true
  
  try {
    const pregnancyData = {
      due_date: calculatedDueDate.value,
      last_menstrual_period: dateMethod.value === 'lmp' ? lmpDate.value : null,
      conception_date: dateMethod.value === 'conception' ? conceptionDate.value : null,
      is_first_pregnancy: isFirstPregnancy.value,
      healthcare_provider: healthcareProvider.value.trim() || null,
      notes: notes.value.trim() || null,
      date_method: dateMethod.value,
      source_date: getSourceDate()
    }
    
    // Create pregnancy record using the store
    await pregnancyStore.createPregnancy(pregnancyData)
    
    // Mark user as having pregnancy data
    const authStore = useAuthStore()
    await authStore.updateUser({ has_pregnancy_data: true })
    
    // Redirect to profile setup or dashboard
    const user = authStore.currentUser
    if (!user?.is_profile_complete) {
      await router.push('/setup/profile')
    } else {
      await router.push('/?message=pregnancy-setup-complete')
    }
  } catch (err) {
    console.error('Pregnancy setup error:', err)
    if (err instanceof Error) {
      error.value = err.message
    } else {
      error.value = 'Failed to save pregnancy information. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

// Set reasonable date defaults
onMounted(() => {
  // Set default LMP to about 8 weeks ago (typical time when people find out)
  const defaultLMP = new Date()
  defaultLMP.setDate(defaultLMP.getDate() - 56) // 8 weeks ago
  lmpDate.value = defaultLMP.toISOString().split('T')[0]
})
</script>

<style scoped>
/* Pregnancy-themed styling */
.trimester-indicator {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.1), rgba(178, 223, 219, 0.1));
}

/* Date input styling */
input[type="date"] {
  color-scheme: light;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: opacity(0.7);
}

/* Radio button custom styling */
input[type="radio"]:checked {
  background-color: #B2DFDB;
  border-color: #B2DFDB;
}
</style>
