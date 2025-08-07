import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { components } from '@/types/api'

// Type aliases for cleaner code
type PregnancyHealth = components['schemas']['PregnancyHealthCreate']
type PregnancyHealthUpdate = components['schemas']['PregnancyHealthUpdate']
type HealthAlert = components['schemas']['HealthAlertResponse']
type HealthAlertCreate = components['schemas']['HealthAlertCreate']
type HealthAlertUpdate = components['schemas']['HealthAlertUpdate']
type SymptomTracking = components['schemas']['SymptomTrackingCreate']
type WeightEntry = components['schemas']['WeightEntryCreate']
type MoodEntry = components['schemas']['MoodEntryCreate']

export const useHealthStore = defineStore('health', () => {
  // State as refs
  const pregnancyHealth = ref<PregnancyHealth | null>(null)
  const healthAlerts = ref<HealthAlert[]>([])
  const symptoms = ref<SymptomTracking[]>([])
  const weightEntries = ref<WeightEntry[]>([])
  const moodEntries = ref<MoodEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getHealthAlertById = computed(() => (id: string) => {
    return healthAlerts.value.find(alert => alert.id === id)
  })
  
  const activeHealthAlerts = computed(() => {
    return healthAlerts.value.filter(alert => alert.is_active)
  })
  
  const criticalHealthAlerts = computed(() => {
    return healthAlerts.value.filter(alert => 
      alert.severity === 'critical' && alert.is_active
    )
  })
  
  const recentSymptoms = computed(() => (days: number = 7) => {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - days)
    
    return symptoms.value.filter(symptom => 
      new Date(symptom.date) >= cutoffDate
    ).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  })
  
  const recentWeightEntries = computed(() => (limit: number = 10) => {
    return [...weightEntries.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, limit)
  })
  
  const recentMoodEntries = computed(() => (days: number = 7) => {
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - days)
    
    return moodEntries.value.filter(mood => 
      new Date(mood.date) >= cutoffDate
    ).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  })
  
  const averageMoodRating = computed(() => (days: number = 7) => {
    const recentMoods = moodEntries.value.filter(mood => {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - days)
      return new Date(mood.date) >= cutoffDate
    })
    
    if (recentMoods.length === 0) return null
    
    const sum = recentMoods.reduce((acc, mood) => acc + mood.mood_score, 0)
    return sum / recentMoods.length
  })
  
  const weightTrend = computed(() => {
    if (weightEntries.value.length < 2) return null
    
    const sorted = [...weightEntries.value]
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    
    const latest = sorted[sorted.length - 1]
    const previous = sorted[sorted.length - 2]
    
    return latest.weight - previous.weight
  })

  // Actions as functions
  async function fetchPregnancyHealth(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyHealth(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch pregnancy health: ${apiError}`)
      }
      
      pregnancyHealth.value = data || null
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching pregnancy health:', err)
    } finally {
      loading.value = false
    }
  }

  async function createPregnancyHealth(healthData: PregnancyHealth) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createPregnancyHealth(healthData)
      
      if (apiError) {
        throw new Error(`Failed to create pregnancy health: ${apiError}`)
      }
      
      if (data) {
        pregnancyHealth.value = data
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating pregnancy health:', err)
      throw err
    }
  }

  async function updatePregnancyHealth(healthId: string, healthData: PregnancyHealthUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updatePregnancyHealth(healthId, healthData)
      
      if (apiError) {
        throw new Error(`Failed to update pregnancy health: ${apiError}`)
      }
      
      if (data) {
        pregnancyHealth.value = data
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating pregnancy health:', err)
      throw err
    }
  }

  async function fetchHealthAlerts(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyHealthAlerts(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch health alerts: ${apiError}`)
      }
      
      healthAlerts.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching health alerts:', err)
    } finally {
      loading.value = false
    }
  }

  async function createHealthAlert(alertData: HealthAlertCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createHealthAlert(alertData)
      
      if (apiError) {
        throw new Error(`Failed to create health alert: ${apiError}`)
      }
      
      if (data) {
        healthAlerts.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating health alert:', err)
      throw err
    }
  }

  async function updateHealthAlert(alertId: string, alertData: HealthAlertUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateHealthAlert(alertId, alertData)
      
      if (apiError) {
        throw new Error(`Failed to update health alert: ${apiError}`)
      }
      
      if (data) {
        const index = healthAlerts.value.findIndex(alert => alert.id === alertId)
        if (index !== -1) {
          healthAlerts.value[index] = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating health alert:', err)
      throw err
    }
  }

  async function fetchSymptoms(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancySymptoms(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch symptoms: ${apiError}`)
      }
      
      symptoms.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching symptoms:', err)
    } finally {
      loading.value = false
    }
  }

  async function trackSymptom(symptomData: SymptomTracking) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.trackSymptom(symptomData)
      
      if (apiError) {
        throw new Error(`Failed to track symptom: ${apiError}`)
      }
      
      if (data) {
        symptoms.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error tracking symptom:', err)
      throw err
    }
  }

  async function fetchWeightEntries(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyWeights(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch weight entries: ${apiError}`)
      }
      
      weightEntries.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching weight entries:', err)
    } finally {
      loading.value = false
    }
  }

  async function createWeightEntry(weightData: WeightEntry) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createWeightEntry(weightData)
      
      if (apiError) {
        throw new Error(`Failed to create weight entry: ${apiError}`)
      }
      
      if (data) {
        weightEntries.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating weight entry:', err)
      throw err
    }
  }

  async function fetchMoodEntries(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyMoods(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch mood entries: ${apiError}`)
      }
      
      moodEntries.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching mood entries:', err)
    } finally {
      loading.value = false
    }
  }

  async function createMoodEntry(moodData: MoodEntry) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createMoodEntry(moodData)
      
      if (apiError) {
        throw new Error(`Failed to create mood entry: ${apiError}`)
      }
      
      if (data) {
        moodEntries.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating mood entry:', err)
      throw err
    }
  }

  function reset() {
    pregnancyHealth.value = null
    healthAlerts.value = []
    symptoms.value = []
    weightEntries.value = []
    moodEntries.value = []
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    pregnancyHealth,
    healthAlerts,
    symptoms,
    weightEntries,
    moodEntries,
    loading,
    error,
    
    // Computed
    getHealthAlertById,
    activeHealthAlerts,
    criticalHealthAlerts,
    recentSymptoms,
    recentWeightEntries,
    recentMoodEntries,
    averageMoodRating,
    weightTrend,
    
    // Actions
    fetchPregnancyHealth,
    createPregnancyHealth,
    updatePregnancyHealth,
    fetchHealthAlerts,
    createHealthAlert,
    updateHealthAlert,
    fetchSymptoms,
    trackSymptom,
    fetchWeightEntries,
    createWeightEntry,
    fetchMoodEntries,
    createMoodEntry,
    reset
  }
})
