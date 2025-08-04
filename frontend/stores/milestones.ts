import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
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

export const useMilestonesStore = defineStore('milestones', () => {
  // State as refs
  const milestones = ref<Milestone[]>([])
  const appointments = ref<Appointment[]>([])
  const importantDates = ref<ImportantDate[]>([])
  const weeklyChecklists = ref<WeeklyChecklist[]>([])
  const currentMilestone = ref<Milestone | null>(null)
  const currentAppointment = ref<Appointment | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getMilestoneById = computed(() => (id: string) => {
    return milestones.value.find(milestone => milestone.id === id)
  })
  
  const getAppointmentById = computed(() => (id: string) => {
    return appointments.value.find(appointment => appointment.id === id)
  })
  
  const completedMilestones = computed(() => {
    return milestones.value.filter(milestone => milestone.completed)
  })
  
  const pendingMilestones = computed(() => {
    return milestones.value.filter(milestone => !milestone.completed)
  })
  
  const upcomingAppointments = computed(() => {
    const now = new Date()
    return appointments.value.filter(appointment => 
      new Date(appointment.appointment_date) > now && !appointment.cancelled
    ).sort((a, b) => 
      new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime()
    )
  })
  
  const pastAppointments = computed(() => {
    const now = new Date()
    return appointments.value.filter(appointment => 
      new Date(appointment.appointment_date) <= now || appointment.completed
    ).sort((a, b) => 
      new Date(b.appointment_date).getTime() - new Date(a.appointment_date).getTime()
    )
  })
  
  const milestonesByWeek = computed(() => (week: number) => {
    return milestones.value.filter(milestone => milestone.week === week)
  })
  
  const milestonesByType = computed(() => (type: string) => {
    return milestones.value.filter(milestone => milestone.type === type)
  })

  // Actions as functions
  async function fetchMilestones(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyMilestones(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch milestones: ${apiError}`)
      }
      
      milestones.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching milestones:', err)
    } finally {
      loading.value = false
    }
  }

  async function createMilestone(milestoneData: MilestoneCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createMilestone(milestoneData)
      
      if (apiError) {
        throw new Error(`Failed to create milestone: ${apiError}`)
      }
      
      if (data) {
        milestones.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating milestone:', err)
      throw err
    }
  }

  async function updateMilestone(milestoneId: string, milestoneData: MilestoneUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateMilestone(milestoneId, milestoneData)
      
      if (apiError) {
        throw new Error(`Failed to update milestone: ${apiError}`)
      }
      
      if (data) {
        const index = milestones.value.findIndex(milestone => milestone.id === milestoneId)
        if (index !== -1) {
          milestones.value[index] = data
        }
        
        // Update current milestone if it's the one being updated
        if (currentMilestone.value?.id === milestoneId) {
          currentMilestone.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating milestone:', err)
      throw err
    }
  }

  async function deleteMilestone(milestoneId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deleteMilestone(milestoneId)
      
      if (apiError) {
        throw new Error(`Failed to delete milestone: ${apiError}`)
      }
      
      milestones.value = milestones.value.filter(milestone => milestone.id !== milestoneId)
      
      // Clear current milestone if it was deleted
      if (currentMilestone.value?.id === milestoneId) {
        currentMilestone.value = null
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting milestone:', err)
      throw err
    }
  }

  async function fetchAppointments(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyAppointments(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch appointments: ${apiError}`)
      }
      
      appointments.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching appointments:', err)
    } finally {
      loading.value = false
    }
  }

  async function createAppointment(appointmentData: AppointmentCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createAppointment(appointmentData)
      
      if (apiError) {
        throw new Error(`Failed to create appointment: ${apiError}`)
      }
      
      if (data) {
        appointments.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating appointment:', err)
      throw err
    }
  }

  async function updateAppointment(appointmentId: string, appointmentData: AppointmentUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateAppointment(appointmentId, appointmentData)
      
      if (apiError) {
        throw new Error(`Failed to update appointment: ${apiError}`)
      }
      
      if (data) {
        const index = appointments.value.findIndex(appointment => appointment.id === appointmentId)
        if (index !== -1) {
          appointments.value[index] = data
        }
        
        // Update current appointment if it's the one being updated
        if (currentAppointment.value?.id === appointmentId) {
          currentAppointment.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating appointment:', err)
      throw err
    }
  }

  async function deleteAppointment(appointmentId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deleteAppointment(appointmentId)
      
      if (apiError) {
        throw new Error(`Failed to delete appointment: ${apiError}`)
      }
      
      appointments.value = appointments.value.filter(appointment => appointment.id !== appointmentId)
      
      // Clear current appointment if it was deleted
      if (currentAppointment.value?.id === appointmentId) {
        currentAppointment.value = null
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting appointment:', err)
      throw err
    }
  }

  async function fetchWeeklyChecklists(pregnancyId: string, week?: number) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getWeeklyChecklists(pregnancyId, week)
      
      if (apiError) {
        throw new Error(`Failed to fetch weekly checklists: ${apiError}`)
      }
      
      weeklyChecklists.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching weekly checklists:', err)
    } finally {
      loading.value = false
    }
  }

  async function createWeeklyChecklist(checklistData: WeeklyChecklist) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createWeeklyChecklist(checklistData)
      
      if (apiError) {
        throw new Error(`Failed to create weekly checklist: ${apiError}`)
      }
      
      if (data) {
        weeklyChecklists.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating weekly checklist:', err)
      throw err
    }
  }

  async function updateWeeklyChecklist(checklistId: string, checklistData: WeeklyChecklistUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateWeeklyChecklist(checklistId, checklistData)
      
      if (apiError) {
        throw new Error(`Failed to update weekly checklist: ${apiError}`)
      }
      
      if (data) {
        const index = weeklyChecklists.value.findIndex(checklist => checklist.id === checklistId)
        if (index !== -1) {
          weeklyChecklists.value[index] = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating weekly checklist:', err)
      throw err
    }
  }

  function setCurrentMilestone(milestone: Milestone) {
    currentMilestone.value = milestone
  }

  function setCurrentAppointment(appointment: Appointment) {
    currentAppointment.value = appointment
  }

  function reset() {
    milestones.value = []
    appointments.value = []
    importantDates.value = []
    weeklyChecklists.value = []
    currentMilestone.value = null
    currentAppointment.value = null
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    milestones,
    appointments,
    importantDates,
    weeklyChecklists,
    currentMilestone,
    currentAppointment,
    loading,
    error,
    
    // Computed
    getMilestoneById,
    getAppointmentById,
    completedMilestones,
    pendingMilestones,
    upcomingAppointments,
    pastAppointments,
    milestonesByWeek,
    milestonesByType,
    
    // Actions
    fetchMilestones,
    createMilestone,
    updateMilestone,
    deleteMilestone,
    fetchAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment,
    fetchWeeklyChecklists,
    createWeeklyChecklist,
    updateWeeklyChecklist,
    setCurrentMilestone,
    setCurrentAppointment,
    reset
  }
})