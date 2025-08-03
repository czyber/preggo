import { defineStore } from 'pinia'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type Milestone = components['schemas']['MilestoneResponse']
type MilestoneCreate = components['schemas']['MilestoneCreate']
type MilestoneUpdate = components['schemas']['MilestoneUpdate']
type Appointment = components['schemas']['AppointmentResponse']
type AppointmentCreate = components['schemas']['AppointmentCreate']
type AppointmentUpdate = components['schemas']['AppointmentUpdate']
type ImportantDate = components['schemas']['ImportantDateCreate']
type WeeklyChecklist = components['schemas']['WeeklyChecklistCreate']
type WeeklyChecklistUpdate = components['schemas']['WeeklyChecklistUpdate']

export const useMilestonesStore = defineStore('milestones', {
  state: () => ({
    milestones: [] as Milestone[],
    appointments: [] as Appointment[],
    importantDates: [] as ImportantDate[],
    weeklyChecklists: [] as WeeklyChecklist[],
    currentMilestone: null as Milestone | null,
    currentAppointment: null as Appointment | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getMilestoneById: (state) => (id: string) => {
      return state.milestones.find(milestone => milestone.id === id)
    },
    
    getAppointmentById: (state) => (id: string) => {
      return state.appointments.find(appointment => appointment.id === id)
    },
    
    completedMilestones: (state) => {
      return state.milestones.filter(milestone => milestone.completed)
    },
    
    pendingMilestones: (state) => {
      return state.milestones.filter(milestone => !milestone.completed)
    },
    
    upcomingAppointments: (state) => {
      const now = new Date()
      return state.appointments.filter(appointment => 
        new Date(appointment.appointment_date) > now && !appointment.cancelled
      ).sort((a, b) => 
        new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime()
      )
    },
    
    pastAppointments: (state) => {
      const now = new Date()
      return state.appointments.filter(appointment => 
        new Date(appointment.appointment_date) <= now || appointment.completed
      ).sort((a, b) => 
        new Date(b.appointment_date).getTime() - new Date(a.appointment_date).getTime()
      )
    },
    
    milestonesByWeek: (state) => (week: number) => {
      return state.milestones.filter(milestone => milestone.week === week)
    },
    
    milestonesByType: (state) => (type: string) => {
      return state.milestones.filter(milestone => milestone.type === type)
    },
  },

  actions: {
    async fetchMilestones(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyMilestones(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch milestones: ${error}`)
        }
        
        this.milestones = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching milestones:', err)
      } finally {
        this.loading = false
      }
    },

    async createMilestone(milestoneData: MilestoneCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createMilestone(milestoneData)
        
        if (error) {
          throw new Error(`Failed to create milestone: ${error}`)
        }
        
        if (data) {
          this.milestones.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating milestone:', err)
        throw err
      }
    },

    async updateMilestone(milestoneId: string, milestoneData: MilestoneUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateMilestone(milestoneId, milestoneData)
        
        if (error) {
          throw new Error(`Failed to update milestone: ${error}`)
        }
        
        if (data) {
          const index = this.milestones.findIndex(milestone => milestone.id === milestoneId)
          if (index !== -1) {
            this.milestones[index] = data
          }
          
          // Update current milestone if it's the one being updated
          if (this.currentMilestone?.id === milestoneId) {
            this.currentMilestone = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating milestone:', err)
        throw err
      }
    },

    async deleteMilestone(milestoneId: string) {
      try {
        const api = useApi()
        const { error } = await api.deleteMilestone(milestoneId)
        
        if (error) {
          throw new Error(`Failed to delete milestone: ${error}`)
        }
        
        this.milestones = this.milestones.filter(milestone => milestone.id !== milestoneId)
        
        // Clear current milestone if it was deleted
        if (this.currentMilestone?.id === milestoneId) {
          this.currentMilestone = null
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting milestone:', err)
        throw err
      }
    },

    async fetchAppointments(pregnancyId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPregnancyAppointments(pregnancyId)
        
        if (error) {
          throw new Error(`Failed to fetch appointments: ${error}`)
        }
        
        this.appointments = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching appointments:', err)
      } finally {
        this.loading = false
      }
    },

    async createAppointment(appointmentData: AppointmentCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createAppointment(appointmentData)
        
        if (error) {
          throw new Error(`Failed to create appointment: ${error}`)
        }
        
        if (data) {
          this.appointments.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating appointment:', err)
        throw err
      }
    },

    async updateAppointment(appointmentId: string, appointmentData: AppointmentUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateAppointment(appointmentId, appointmentData)
        
        if (error) {
          throw new Error(`Failed to update appointment: ${error}`)
        }
        
        if (data) {
          const index = this.appointments.findIndex(appointment => appointment.id === appointmentId)
          if (index !== -1) {
            this.appointments[index] = data
          }
          
          // Update current appointment if it's the one being updated
          if (this.currentAppointment?.id === appointmentId) {
            this.currentAppointment = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating appointment:', err)
        throw err
      }
    },

    async deleteAppointment(appointmentId: string) {
      try {
        const api = useApi()
        const { error } = await api.deleteAppointment(appointmentId)
        
        if (error) {
          throw new Error(`Failed to delete appointment: ${error}`)
        }
        
        this.appointments = this.appointments.filter(appointment => appointment.id !== appointmentId)
        
        // Clear current appointment if it was deleted
        if (this.currentAppointment?.id === appointmentId) {
          this.currentAppointment = null
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting appointment:', err)
        throw err
      }
    },

    async fetchWeeklyChecklists(pregnancyId: string, week?: number) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getWeeklyChecklists(pregnancyId, week)
        
        if (error) {
          throw new Error(`Failed to fetch weekly checklists: ${error}`)
        }
        
        this.weeklyChecklists = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching weekly checklists:', err)
      } finally {
        this.loading = false
      }
    },

    async createWeeklyChecklist(checklistData: WeeklyChecklist) {
      try {
        const api = useApi()
        const { data, error } = await api.createWeeklyChecklist(checklistData)
        
        if (error) {
          throw new Error(`Failed to create weekly checklist: ${error}`)
        }
        
        if (data) {
          this.weeklyChecklists.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating weekly checklist:', err)
        throw err
      }
    },

    async updateWeeklyChecklist(checklistId: string, checklistData: WeeklyChecklistUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateWeeklyChecklist(checklistId, checklistData)
        
        if (error) {
          throw new Error(`Failed to update weekly checklist: ${error}`)
        }
        
        if (data) {
          const index = this.weeklyChecklists.findIndex(checklist => checklist.id === checklistId)
          if (index !== -1) {
            this.weeklyChecklists[index] = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating weekly checklist:', err)
        throw err
      }
    },

    setCurrentMilestone(milestone: Milestone) {
      this.currentMilestone = milestone
    },

    setCurrentAppointment(appointment: Appointment) {
      this.currentAppointment = appointment
    },

    reset() {
      this.milestones = []
      this.appointments = []
      this.importantDates = []
      this.weeklyChecklists = []
      this.currentMilestone = null
      this.currentAppointment = null
      this.loading = false
      this.error = null
    }
  }
})