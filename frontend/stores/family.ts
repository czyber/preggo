import { defineStore } from 'pinia'
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

export const useFamilyStore = defineStore('family', {
  state: () => ({
    familyGroups: [] as FamilyGroup[],
    currentFamilyGroup: null as FamilyGroup | null,
    familyMembers: [] as FamilyMember[],
    familyInvitations: [] as FamilyInvitation[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getFamilyGroupById: (state) => (id: string) => {
      return state.familyGroups.find(group => group.id === id)
    },
    
    getFamilyMemberById: (state) => (id: string) => {
      return state.familyMembers.find(member => member.id === id)
    },
    
    activeFamilyMembers: (state) => {
      return state.familyMembers.filter(member => member.is_active)
    },
    
    pendingInvitations: (state) => {
      return state.familyInvitations.filter(invitation => invitation.status === 'pending')
    },
    
    acceptedInvitations: (state) => {
      return state.familyInvitations.filter(invitation => invitation.status === 'accepted')
    },
    
    currentFamilyMembers: (state) => {
      if (!state.currentFamilyGroup) return []
      return state.familyMembers.filter(member => 
        member.family_group_id === state.currentFamilyGroup?.id
      )
    },
  },

  actions: {
    async fetchFamilyGroups() {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getUserFamilyGroups()
        
        if (error) {
          throw new Error(`Failed to fetch family groups: ${error}`)
        }
        
        this.familyGroups = data || []
        
        // Set current family group to the first one if none is set
        if (this.familyGroups.length > 0 && !this.currentFamilyGroup) {
          this.currentFamilyGroup = this.familyGroups[0]
        }
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching family groups:', err)
      } finally {
        this.loading = false
      }
    },

    async createFamilyGroup(groupData: FamilyGroupCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createFamilyGroup(groupData)
        
        if (error) {
          throw new Error(`Failed to create family group: ${error}`)
        }
        
        if (data) {
          this.familyGroups.push(data)
          // Set as current family group
          this.currentFamilyGroup = data
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating family group:', err)
        throw err
      }
    },

    async updateFamilyGroup(groupId: string, groupData: FamilyGroupUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateFamilyGroup(groupId, groupData)
        
        if (error) {
          throw new Error(`Failed to update family group: ${error}`)
        }
        
        if (data) {
          const index = this.familyGroups.findIndex(group => group.id === groupId)
          if (index !== -1) {
            this.familyGroups[index] = data
          }
          
          // Update current family group if it's the one being updated
          if (this.currentFamilyGroup?.id === groupId) {
            this.currentFamilyGroup = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating family group:', err)
        throw err
      }
    },

    async fetchFamilyMembers(familyGroupId?: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const groupId = familyGroupId || this.currentFamilyGroup?.id
        
        if (!groupId) {
          throw new Error('No family group ID provided')
        }
        
        const { data, error } = await api.getFamilyGroupMembers(groupId)
        
        if (error) {
          throw new Error(`Failed to fetch family members: ${error}`)
        }
        
        this.familyMembers = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching family members:', err)
      } finally {
        this.loading = false
      }
    },

    async addFamilyMember(memberData: FamilyMemberCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.addFamilyMember(memberData)
        
        if (error) {
          throw new Error(`Failed to add family member: ${error}`)
        }
        
        if (data) {
          this.familyMembers.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error adding family member:', err)
        throw err
      }
    },

    async updateFamilyMember(memberId: string, memberData: FamilyMemberUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateFamilyMember(memberId, memberData)
        
        if (error) {
          throw new Error(`Failed to update family member: ${error}`)
        }
        
        if (data) {
          const index = this.familyMembers.findIndex(member => member.id === memberId)
          if (index !== -1) {
            this.familyMembers[index] = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating family member:', err)
        throw err
      }
    },

    async removeFamilyMember(memberId: string) {
      try {
        const api = useApi()
        const { error } = await api.removeFamilyMember(memberId)
        
        if (error) {
          throw new Error(`Failed to remove family member: ${error}`)
        }
        
        this.familyMembers = this.familyMembers.filter(member => member.id !== memberId)
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error removing family member:', err)
        throw err
      }
    },

    async fetchFamilyInvitations() {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getFamilyInvitations()
        
        if (error) {
          throw new Error(`Failed to fetch family invitations: ${error}`)
        }
        
        this.familyInvitations = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching family invitations:', err)
      } finally {
        this.loading = false
      }
    },

    async createFamilyInvitation(invitationData: FamilyInvitationCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createFamilyInvitation(invitationData)
        
        if (error) {
          throw new Error(`Failed to create family invitation: ${error}`)
        }
        
        if (data) {
          this.familyInvitations.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating family invitation:', err)
        throw err
      }
    },

    async updateFamilyInvitation(invitationId: string, invitationData: FamilyInvitationUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateFamilyInvitation(invitationId, invitationData)
        
        if (error) {
          throw new Error(`Failed to update family invitation: ${error}`)
        }
        
        if (data) {
          const index = this.familyInvitations.findIndex(invitation => invitation.id === invitationId)
          if (index !== -1) {
            this.familyInvitations[index] = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating family invitation:', err)
        throw err
      }
    },

    setCurrentFamilyGroup(familyGroup: FamilyGroup) {
      this.currentFamilyGroup = familyGroup
      // Fetch members for the new current family group
      this.fetchFamilyMembers(familyGroup.id)
    },

    reset() {
      this.familyGroups = []
      this.currentFamilyGroup = null
      this.familyMembers = []
      this.familyInvitations = []
      this.loading = false
      this.error = null
    }
  }
})