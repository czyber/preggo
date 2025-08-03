import { defineStore } from 'pinia'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type Pregnancy = components['schemas']['PregnancyResponse']
type PregnancyCreate = components['schemas']['PregnancyCreate']
type PregnancyUpdate = components['schemas']['PregnancyUpdate']

export const usePregnancyStore = defineStore('pregnancy', {
  state: () => ({
    pregnancies: [] as Pregnancy[],
    currentPregnancy: null as Pregnancy | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getPregnancyById: (state) => (id: string) => {
      return state.pregnancies.find(pregnancy => pregnancy.id === id)
    },
    
    activePregnancies: (state) => {
      return state.pregnancies.filter(pregnancy => pregnancy.is_active)
    },
    
    completedPregnancies: (state) => {
      return state.pregnancies.filter(pregnancy => !pregnancy.is_active)
    },
    
    currentWeek: (state) => {
      if (!state.currentPregnancy) return null
      return state.currentPregnancy.current_week
    },
    
    dueDate: (state) => {
      if (!state.currentPregnancy) return null
      return state.currentPregnancy.due_date
    },
    
    babyInfo: (state) => {
      if (!state.currentPregnancy) return []
      return state.currentPregnancy.babies
    },
  },

  actions: {
    async fetchPregnancies() {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getUserPregnancies()
        
        if (error) {
          throw new Error(`Failed to fetch pregnancies: ${error}`)
        }
        
        this.pregnancies = data || []
        
        // Set current pregnancy to the first active one
        const activePregnancy = this.pregnancies.find(p => p.is_active)
        if (activePregnancy) {
          this.currentPregnancy = activePregnancy
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching pregnancies:', err)
      } finally {
        this.loading = false
      }
    },

    async createPregnancy(pregnancyData: PregnancyCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createPregnancy(pregnancyData)
        
        if (error) {
          throw new Error(`Failed to create pregnancy: ${error}`)
        }
        
        if (data) {
          this.pregnancies.push(data)
          // Set as current pregnancy if it's active
          if (data.is_active) {
            this.currentPregnancy = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating pregnancy:', err)
        throw err
      }
    },

    async updatePregnancy(pregnancyId: string, pregnancyData: PregnancyUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updatePregnancy(pregnancyId, pregnancyData)
        
        if (error) {
          throw new Error(`Failed to update pregnancy: ${error}`)
        }
        
        if (data) {
          const index = this.pregnancies.findIndex(pregnancy => pregnancy.id === pregnancyId)
          if (index !== -1) {
            this.pregnancies[index] = data
          }
          
          // Update current pregnancy if it's the one being updated
          if (this.currentPregnancy?.id === pregnancyId) {
            this.currentPregnancy = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating pregnancy:', err)
        throw err
      }
    },

    async deletePregnancy(pregnancyId: string) {
      try {
        const api = useApi()
        const { error } = await api.deletePregnancy(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to delete pregnancy: ${error}`)
        }
        
        this.pregnancies = this.pregnancies.filter(pregnancy => pregnancy.id !== pregnancyId)
        
        // Clear current pregnancy if it was deleted
        if (this.currentPregnancy?.id === pregnancyId) {
          this.currentPregnancy = null
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting pregnancy:', err)
        throw err
      }
    },

    async fetchPregnancyById(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancy(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch pregnancy: ${error}`)
        }
        
        if (data) {
          // Update in pregnancies array if it exists
          const index = this.pregnancies.findIndex(pregnancy => pregnancy.id === pregnancyId)
          if (index !== -1) {
            this.pregnancies[index] = data
          } else {
            this.pregnancies.push(data)
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching pregnancy:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    setCurrentPregnancy(pregnancy: Pregnancy) {
      this.currentPregnancy = pregnancy
    },

    reset() {
      this.pregnancies = []
      this.currentPregnancy = null
      this.loading = false
      this.error = null
    }
  }
})