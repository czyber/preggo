import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type FamilyGroup = components['schemas']['FamilyGroupResponse']
type FamilyGroupCreate = components['schemas']['FamilyGroupCreate']
type FamilyGroupUpdate = components['schemas']['FamilyGroupUpdate']
type FamilyMember = components['schemas']['FamilyMemberResponse']
type FamilyMemberCreate = components['schemas']['FamilyMemberCreate']
type FamilyMemberUpdate = components['schemas']['FamilyMemberUpdate']
type FamilyInvitation = components['schemas']['FamilyInvitationResponse']
type FamilyInvitationCreate = components['schemas']['FamilyInvitationCreate']
type FamilyInvitationUpdate = components['schemas']['FamilyInvitationUpdate']

export const useFamilyStore = defineStore('family', () => {
  // State as refs
  const familyGroups = ref<FamilyGroup[]>([])
  const currentFamilyGroup = ref<FamilyGroup | null>(null)
  const familyMembers = ref<FamilyMember[]>([])
  const familyInvitations = ref<FamilyInvitation[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getFamilyGroupById = computed(() => (id: string) => {
    return familyGroups.value.find(group => group.id === id)
  })
  
  const getFamilyMemberById = computed(() => (id: string) => {
    return familyMembers.value.find(member => member.id === id)
  })
  
  const activeFamilyMembers = computed(() => {
    return familyMembers.value.filter(member => member.is_active)
  })
  
  const pendingInvitations = computed(() => {
    return familyInvitations.value.filter(invitation => invitation.status === 'pending')
  })
  
  const acceptedInvitations = computed(() => {
    return familyInvitations.value.filter(invitation => invitation.status === 'accepted')
  })
  
  const currentFamilyMembers = computed(() => {
    if (!currentFamilyGroup.value) return []
    return familyMembers.value.filter(member => 
      member.family_group_id === currentFamilyGroup.value?.id
    )
  })

  // Actions as functions
  async function fetchFamilyGroups() {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getUserFamilyGroups()
      
      if (apiError) {
        throw new Error(`Failed to fetch family groups: ${apiError}`)
      }
      
      familyGroups.value = data || []
      
      // Set current family group to the first one if none is set
      if (familyGroups.value.length > 0 && !currentFamilyGroup.value) {
        currentFamilyGroup.value = familyGroups.value[0]
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching family groups:', err)
    } finally {
      loading.value = false
    }
  }

  async function createFamilyGroup(groupData: FamilyGroupCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createFamilyGroup(groupData)
      
      if (apiError) {
        throw new Error(`Failed to create family group: ${apiError}`)
      }
      
      if (data) {
        familyGroups.value.push(data)
        // Set as current family group
        currentFamilyGroup.value = data
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating family group:', err)
      throw err
    }
  }

  async function updateFamilyGroup(groupId: string, groupData: FamilyGroupUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateFamilyGroup(groupId, groupData)
      
      if (apiError) {
        throw new Error(`Failed to update family group: ${apiError}`)
      }
      
      if (data) {
        const index = familyGroups.value.findIndex(group => group.id === groupId)
        if (index !== -1) {
          familyGroups.value[index] = data
        }
        
        // Update current family group if it's the one being updated
        if (currentFamilyGroup.value?.id === groupId) {
          currentFamilyGroup.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating family group:', err)
      throw err
    }
  }

  async function fetchFamilyMembers(familyGroupId?: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const groupId = familyGroupId || currentFamilyGroup.value?.id
      
      if (!groupId) {
        throw new Error('No family group ID provided')
      }
      
      const { data, error: apiError } = await api.getFamilyGroupMembers(groupId)
      
      if (apiError) {
        throw new Error(`Failed to fetch family members: ${apiError}`)
      }
      
      familyMembers.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching family members:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchFamilyMembersByPregnancy(pregnancyId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      
      const { data, error: apiError } = await api.getPregnancyFamilyMembers(pregnancyId)
      
      if (apiError) {
        throw new Error(`Failed to fetch family members: ${apiError}`)
      }
      
      familyMembers.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching family members:', err)
    } finally {
      loading.value = false
    }
  }

  async function addFamilyMember(memberData: FamilyMemberCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.addFamilyMember(memberData)
      
      if (apiError) {
        throw new Error(`Failed to add family member: ${apiError}`)
      }
      
      if (data) {
        familyMembers.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error adding family member:', err)
      throw err
    }
  }

  async function updateFamilyMember(memberId: string, memberData: FamilyMemberUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateFamilyMember(memberId, memberData)
      
      if (apiError) {
        throw new Error(`Failed to update family member: ${apiError}`)
      }
      
      if (data) {
        const index = familyMembers.value.findIndex(member => member.id === memberId)
        if (index !== -1) {
          familyMembers.value[index] = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating family member:', err)
      throw err
    }
  }

  async function removeFamilyMember(memberId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.removeFamilyMember(memberId)
      
      if (apiError) {
        throw new Error(`Failed to remove family member: ${apiError}`)
      }
      
      familyMembers.value = familyMembers.value.filter(member => member.id !== memberId)
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error removing family member:', err)
      throw err
    }
  }

  async function fetchFamilyInvitations() {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getFamilyInvitations()
      
      if (apiError) {
        throw new Error(`Failed to fetch family invitations: ${apiError}`)
      }
      
      familyInvitations.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching family invitations:', err)
    } finally {
      loading.value = false
    }
  }

  async function createFamilyInvitation(invitationData: FamilyInvitationCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createFamilyInvitation(invitationData)
      
      if (apiError) {
        throw new Error(`Failed to create family invitation: ${apiError}`)
      }
      
      if (data) {
        familyInvitations.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating family invitation:', err)
      throw err
    }
  }

  async function updateFamilyInvitation(invitationId: string, invitationData: FamilyInvitationUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateFamilyInvitation(invitationId, invitationData)
      
      if (apiError) {
        throw new Error(`Failed to update family invitation: ${apiError}`)
      }
      
      if (data) {
        const index = familyInvitations.value.findIndex(invitation => invitation.id === invitationId)
        if (index !== -1) {
          familyInvitations.value[index] = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating family invitation:', err)
      throw err
    }
  }

  function setCurrentFamilyGroup(familyGroup: FamilyGroup) {
    currentFamilyGroup.value = familyGroup
    // Fetch members for the new current family group
    fetchFamilyMembers(familyGroup.id)
  }

  function reset() {
    familyGroups.value = []
    currentFamilyGroup.value = null
    familyMembers.value = []
    familyInvitations.value = []
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    familyGroups,
    currentFamilyGroup,
    familyMembers,
    familyInvitations,
    loading,
    error,
    
    // Computed
    getFamilyGroupById,
    getFamilyMemberById,
    activeFamilyMembers,
    pendingInvitations,
    acceptedInvitations,
    currentFamilyMembers,
    
    // Actions
    fetchFamilyGroups,
    createFamilyGroup,
    updateFamilyGroup,
    fetchFamilyMembers,
    fetchFamilyMembersByPregnancy,
    addFamilyMember,
    updateFamilyMember,
    removeFamilyMember,
    fetchFamilyInvitations,
    createFamilyInvitation,
    updateFamilyInvitation,
    setCurrentFamilyGroup,
    reset
  }
})