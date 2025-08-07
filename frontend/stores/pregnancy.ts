import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { components } from '@/types/api'

// Type aliases for cleaner code
type Pregnancy = components['schemas']['PregnancyResponse']
type PregnancyCreate = components['schemas']['PregnancyCreate']
type PregnancyUpdate = components['schemas']['PregnancyUpdate']

export const usePregnancyStore = defineStore('pregnancy', () => {
  // State as refs
  const pregnancies = ref<Pregnancy[]>([])
  const currentPregnancy = ref<Pregnancy | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getPregnancyById = computed(() => (id: string) => {
    return pregnancies.value.find(pregnancy => pregnancy.id === id)
  })
  
  const activePregnancies = computed(() => {
    return pregnancies.value.filter(pregnancy => pregnancy.status === 'active')
  })
  
  const completedPregnancies = computed(() => {
    return pregnancies.value.filter(pregnancy => pregnancy.status === 'completed')
  })
  
  const currentWeek = computed(() => {
    if (!currentPregnancy.value) return null
    return currentPregnancy.value.pregnancy_details.current_week
  })
  
  const dueDate = computed(() => {
    if (!currentPregnancy.value) return null
    return currentPregnancy.value.pregnancy_details.due_date
  })
  
  const babyInfo = computed(() => {
    if (!currentPregnancy.value) return []
    return currentPregnancy.value.pregnancy_details.expected_babies
  })

  // Actions as functions
  async function fetchPregnancies() {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getUserPregnancies()
      
      if (apiError) {
        throw new Error(`Failed to fetch pregnancies: ${apiError}`)
      }
      
      pregnancies.value = data || []
      
      // Set current pregnancy to the first active one
      const activePregnancy = pregnancies.value.find(p => p.status === 'active')
      if (activePregnancy) {
        currentPregnancy.value = activePregnancy
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching pregnancies:', err)
    } finally {
      loading.value = false
    }
  }

  // Utility function to calculate pregnancy details
  function calculatePregnancyDetails(formData: any): components['schemas']['PregnancyDetails-Input'] {
    const dueDate = new Date(formData.due_date)
    const today = new Date()
    
    // Calculate conception date
    let conceptionDate: Date
    if (formData.conception_date) {
      conceptionDate = new Date(formData.conception_date)
    } else {
      // Estimate conception date (due date - 280 days)
      conceptionDate = new Date(dueDate.getTime() - 280 * 24 * 60 * 60 * 1000)
    }
    
    // Calculate days pregnant
    const daysPregant = Math.floor((today.getTime() - conceptionDate.getTime()) / (1000 * 60 * 60 * 24))
    
    // Calculate current week and day
    const currentWeek = Math.max(0, Math.min(Math.floor(daysPregant / 7), 42))
    const currentDay = Math.max(0, daysPregant % 7)
    
    // Determine trimester
    let trimester: number
    if (currentWeek <= 12) {
      trimester = 1
    } else if (currentWeek <= 26) {
      trimester = 2
    } else {
      trimester = 3
    }
    
    return {
      due_date: formData.due_date,
      conception_date: formData.conception_date || conceptionDate.toISOString().split('T')[0],
      current_week: currentWeek,
      current_day: currentDay,
      trimester: trimester,
      is_multiple: false,
      expected_babies: [],
      risk_level: 'low' as const
    }
  }

  async function createPregnancy(formData: any) {
    try {
      // Transform form data to match backend expectations
      const pregnancyData: PregnancyCreate = {
        pregnancy_details: calculatePregnancyDetails(formData),
        preferences: null,
        partner_ids: null
      }
      
      const api = useApi()
      const { data, error: apiError } = await api.createPregnancy(pregnancyData)
      
      if (apiError) {
        throw new Error(`Failed to create pregnancy: ${apiError}`)
      }
      
      if (data) {
        pregnancies.value.push(data)
        // Set as current pregnancy if it's active
        if (data.status === 'active') {
          currentPregnancy.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating pregnancy:', err)
      throw err
    }
  }

  async function updatePregnancy(pregnancyId: string, pregnancyData: PregnancyUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updatePregnancy(pregnancyId, pregnancyData)
      
      if (apiError) {
        throw new Error(`Failed to update pregnancy: ${apiError}`)
      }
      
      if (data) {
        const index = pregnancies.value.findIndex(pregnancy => pregnancy.id === pregnancyId)
        if (index !== -1) {
          pregnancies.value[index] = data
        }
        
        // Update current pregnancy if it's the one being updated
        if (currentPregnancy.value?.id === pregnancyId) {
          currentPregnancy.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating pregnancy:', err)
      throw err
    }
  }

  async function deletePregnancy(pregnancyId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deletePregnancy(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to delete pregnancy: ${apiError}`)
      }
      
      pregnancies.value = pregnancies.value.filter(pregnancy => pregnancy.id !== pregnancyId)
      
      // Clear current pregnancy if it was deleted
      if (currentPregnancy.value?.id === pregnancyId) {
        currentPregnancy.value = null
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting pregnancy:', err)
      throw err
    }
  }

  async function fetchPregnancyById(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancy(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch pregnancy: ${apiError}`)
      }
      
      if (data) {
        // Update in pregnancies array if it exists
        const index = pregnancies.value.findIndex(pregnancy => pregnancy.id === pregnancyId)
        if (index !== -1) {
          pregnancies.value[index] = data
        } else {
          pregnancies.value.push(data)
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching pregnancy:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentPregnancy(pregnancy: Pregnancy) {
    currentPregnancy.value = pregnancy
  }

  function reset() {
    pregnancies.value = []
    currentPregnancy.value = null
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    pregnancies,
    currentPregnancy,
    loading,
    error,
    
    // Computed
    getPregnancyById,
    activePregnancies,
    completedPregnancies,
    currentWeek,
    dueDate,
    babyInfo,
    
    // Actions
    fetchPregnancies,
    createPregnancy,
    updatePregnancy,
    deletePregnancy,
    fetchPregnancyById,
    setCurrentPregnancy,
    reset
  }
})
