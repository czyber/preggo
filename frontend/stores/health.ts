import { defineStore } from 'pinia'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type PregnancyHealth = components['schemas']['PregnancyHealthCreate']
type PregnancyHealthUpdate = components['schemas']['PregnancyHealthUpdate']
type HealthAlert = components['schemas']['HealthAlertResponse']
type HealthAlertCreate = components['schemas']['HealthAlertCreate']
type HealthAlertUpdate = components['schemas']['HealthAlertUpdate']
type SymptomTracking = components['schemas']['SymptomTrackingCreate']
type WeightEntry = components['schemas']['WeightEntryCreate']
type MoodEntry = components['schemas']['MoodEntryCreate']

export const useHealthStore = defineStore('health', {
  state: () => ({
    pregnancyHealth: null as PregnancyHealth | null,
    healthAlerts: [] as HealthAlert[],
    symptoms: [] as SymptomTracking[],
    weightEntries: [] as WeightEntry[],
    moodEntries: [] as MoodEntry[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getHealthAlertById: (state) => (id: string) => {
      return state.healthAlerts.find(alert => alert.id === id)
    },
    
    activeHealthAlerts: (state) => {
      return state.healthAlerts.filter(alert => alert.is_active)
    },
    
    criticalHealthAlerts: (state) => {
      return state.healthAlerts.filter(alert => 
        alert.severity === 'critical' && alert.is_active
      )
    },
    
    recentSymptoms: (state) => (days: number = 7) => {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - days)
      
      return state.symptoms.filter(symptom => 
        new Date(symptom.date) >= cutoffDate
      ).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    },
    
    recentWeightEntries: (state) => (limit: number = 10) => {
      return [...state.weightEntries]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, limit)
    },
    
    recentMoodEntries: (state) => (days: number = 7) => {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - days)
      
      return state.moodEntries.filter(mood => 
        new Date(mood.date) >= cutoffDate
      ).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    },
    
    averageMoodRating: (state) => (days: number = 7) => {
      const recentMoods = state.moodEntries.filter(mood => {
        const cutoffDate = new Date()
        cutoffDate.setDate(cutoffDate.getDate() - days)
        return new Date(mood.date) >= cutoffDate
      })
      
      if (recentMoods.length === 0) return null
      
      const sum = recentMoods.reduce((acc, mood) => acc + mood.mood_score, 0)
      return sum / recentMoods.length
    },
    
    weightTrend: (state) => {
      if (state.weightEntries.length < 2) return null
      
      const sorted = [...state.weightEntries]
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      
      const latest = sorted[sorted.length - 1]
      const previous = sorted[sorted.length - 2]
      
      return latest.weight - previous.weight
    },
  },

  actions: {
    async fetchPregnancyHealth(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyHealth(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch pregnancy health: ${error}`)
        }
        
        this.pregnancyHealth = data || null
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching pregnancy health:', err)
      } finally {
        this.loading = false
      }
    },

    async createPregnancyHealth(healthData: PregnancyHealth) {
      try {
        const api = useApi()
        const { data, error } = await api.createPregnancyHealth(healthData)
        
        if (error) {
          throw new Error(`Failed to create pregnancy health: ${error}`)
        }
        
        if (data) {
          this.pregnancyHealth = data
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating pregnancy health:', err)
        throw err
      }
    },

    async updatePregnancyHealth(healthId: string, healthData: PregnancyHealthUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updatePregnancyHealth(healthId, healthData)
        
        if (error) {
          throw new Error(`Failed to update pregnancy health: ${error}`)
        }
        
        if (data) {
          this.pregnancyHealth = data
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating pregnancy health:', err)
        throw err
      }
    },

    async fetchHealthAlerts(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyHealthAlerts(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch health alerts: ${error}`)
        }
        
        this.healthAlerts = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching health alerts:', err)
      } finally {
        this.loading = false
      }
    },

    async createHealthAlert(alertData: HealthAlertCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createHealthAlert(alertData)
        
        if (error) {
          throw new Error(`Failed to create health alert: ${error}`)
        }
        
        if (data) {
          this.healthAlerts.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating health alert:', err)
        throw err
      }
    },

    async updateHealthAlert(alertId: string, alertData: HealthAlertUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateHealthAlert(alertId, alertData)
        
        if (error) {
          throw new Error(`Failed to update health alert: ${error}`)
        }
        
        if (data) {
          const index = this.healthAlerts.findIndex(alert => alert.id === alertId)
          if (index !== -1) {
            this.healthAlerts[index] = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating health alert:', err)
        throw err
      }
    },

    async fetchSymptoms(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancySymptoms(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch symptoms: ${error}`)
        }
        
        this.symptoms = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching symptoms:', err)
      } finally {
        this.loading = false
      }
    },

    async trackSymptom(symptomData: SymptomTracking) {
      try {
        const api = useApi()
        const { data, error } = await api.trackSymptom(symptomData)
        
        if (error) {
          throw new Error(`Failed to track symptom: ${error}`)
        }
        
        if (data) {
          this.symptoms.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error tracking symptom:', err)
        throw err
      }
    },

    async fetchWeightEntries(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyWeights(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch weight entries: ${error}`)
        }
        
        this.weightEntries = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching weight entries:', err)
      } finally {
        this.loading = false
      }
    },

    async createWeightEntry(weightData: WeightEntry) {
      try {
        const api = useApi()
        const { data, error } = await api.createWeightEntry(weightData)
        
        if (error) {
          throw new Error(`Failed to create weight entry: ${error}`)
        }
        
        if (data) {
          this.weightEntries.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating weight entry:', err)
        throw err
      }
    },

    async fetchMoodEntries(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyMoods(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch mood entries: ${error}`)
        }
        
        this.moodEntries = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching mood entries:', err)
      } finally {
        this.loading = false
      }
    },

    async createMoodEntry(moodData: MoodEntry) {
      try {
        const api = useApi()
        const { data, error } = await api.createMoodEntry(moodData)
        
        if (error) {
          throw new Error(`Failed to create mood entry: ${error}`)
        }
        
        if (data) {
          this.moodEntries.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating mood entry:', err)
        throw err
      }
    },

    reset() {
      this.pregnancyHealth = null
      this.healthAlerts = []
      this.symptoms = []
      this.weightEntries = []
      this.moodEntries = []
      this.loading = false
      this.error = null
    }
  }
})