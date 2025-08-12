import { ref, computed } from 'vue'

// Types based on the design document
export interface CirclePattern {
  id: string
  name: string
  icon: string
  description: string
  groups: string[]
  visibility: string
  suggestedFor: string[]
  usage_frequency?: number
  member_count?: number
}

export interface InviteContext {
  token: string
  inviter: {
    first_name: string
    last_name: string
    profile_image?: string
    relationship?: string
  }
  pregnancy: {
    id: string
    baby_name?: string
    current_week?: number
    due_date?: string
  }
  suggested_circles: CirclePattern[]
  onboarding_content: {
    welcome_message: string
    relationship_context: string
    privacy_explanation: string
  }
  auto_add_to_patterns: string[]
}

export interface ContextualInviteCreate {
  email: string
  relationship: string
  message?: string
  suggested_circles: string[]
  auto_add_to_patterns: string[]
}

// Circle pattern presets based on design document
export const CIRCLE_PATTERNS: CirclePattern[] = [
  {
    id: "just-us",
    name: "Just Us",
    icon: "💕",
    description: "You and your partner",
    groups: [],
    visibility: 'PARTNER_ONLY',
    suggestedFor: ['symptom_share', 'preparation'],
    usage_frequency: 0,
    member_count: 2
  },
  {
    id: "close-family",
    name: "Close Family",
    icon: "👨‍👩‍👧‍👦",
    description: "Parents, siblings, and partner",
    groups: ['IMMEDIATE_FAMILY'],
    visibility: 'IMMEDIATE',
    suggestedFor: ['ultrasound', 'milestone'],
    usage_frequency: 0,
    member_count: 6
  },
  {
    id: "everyone",
    name: "Everyone",
    icon: "🌟",
    description: "All your family and friends",
    groups: ['IMMEDIATE_FAMILY', 'EXTENDED_FAMILY', 'FRIENDS'],
    visibility: 'ALL_FAMILY',
    suggestedFor: ['announcement', 'celebration'],
    usage_frequency: 0,
    member_count: 18
  },
  {
    id: "grandparents",
    name: "Grandparents Circle",
    icon: "👴👵",
    description: "Extended family including grandparents",
    groups: ['IMMEDIATE_FAMILY', 'EXTENDED_FAMILY'],
    visibility: 'EXTENDED',
    suggestedFor: ['weekly_update', 'belly_photo'],
    usage_frequency: 0,
    member_count: 12
  },
  {
    id: "friends-support",
    name: "Friend Support",
    icon: "🤗",
    description: "Close friends and support network",
    groups: ['FRIENDS', 'SUPPORT_CIRCLE'],
    visibility: 'FRIENDS',
    suggestedFor: ['question', 'memory'],
    usage_frequency: 0,
    member_count: 8
  }
]

/**
 * Composable for handling invite functionality and circle management
 */
export const useInvites = () => {
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Fetch invite context by token
  const fetchInviteContext = async (token: string): Promise<InviteContext | null> => {
    loading.value = true
    error.value = null

    try {
      const api = useApi()
      // This endpoint would need to be implemented in the backend
      const { data, error: apiError } = await api.getInviteContext(token)
      
      if (apiError) {
        throw new Error(`Failed to fetch invite context: ${apiError}`)
      }
      
      return data || null
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch invite context'
      console.error('Error fetching invite context:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  // Accept invite and join circles
  const acceptInviteAndJoinCircles = async (token: string, userId: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const api = useApi()
      // This endpoint would need to be implemented in the backend
      const { data, error: apiError } = await api.acceptInvite(token, { user_id: userId })
      
      if (apiError) {
        throw new Error(`Failed to accept invite: ${apiError}`)
      }
      
      return !!data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to accept invite'
      console.error('Error accepting invite:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  // Create contextual invite
  const createContextualInvite = async (
    pregnancyId: string, 
    inviteData: ContextualInviteCreate
  ): Promise<string | null> => {
    loading.value = true
    error.value = null

    try {
      const api = useApi()
      // This endpoint would need to be implemented in the backend
      const { data, error: apiError } = await api.createContextualInvite(pregnancyId, inviteData)
      
      if (apiError) {
        throw new Error(`Failed to create invite: ${apiError}`)
      }
      
      return data?.token || null
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create invite'
      console.error('Error creating contextual invite:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  // Get suggested circles for a relationship
  const suggestCirclesForRelationship = (relationship: string): CirclePattern[] => {
    const relationshipMap: Record<string, string[]> = {
      'partner': ['just-us', 'close-family'],
      'parent': ['close-family', 'grandparents'],
      'sibling': ['close-family', 'everyone'],
      'grandparent': ['grandparents', 'everyone'],
      'friend': ['friends-support', 'everyone'],
      'extended_family': ['grandparents', 'everyone'],
      'default': ['close-family', 'everyone']
    }

    const patternIds = relationshipMap[relationship] || relationshipMap['default']
    return CIRCLE_PATTERNS.filter(pattern => patternIds.includes(pattern.id))
  }

  // Suggest circles for post content (AI-like suggestions)
  const suggestCirclesForPost = (
    postContent: string, 
    postType: string
  ): { pattern: CirclePattern; confidence: number; reason: string }[] => {
    const suggestions: { pattern: CirclePattern; confidence: number; reason: string }[] = []
    
    // Content-based suggestions
    const lowerContent = postContent.toLowerCase()
    
    if (lowerContent.includes('first') || lowerContent.includes('exciting') || lowerContent.includes('announcement')) {
      const everyonePattern = CIRCLE_PATTERNS.find(p => p.id === 'everyone')
      if (everyonePattern) {
        suggestions.push({
          pattern: everyonePattern,
          confidence: 90,
          reason: "Exciting announcements are usually shared with everyone"
        })
      }
    }

    if (lowerContent.includes('private') || lowerContent.includes('personal') || lowerContent.includes('concern')) {
      const justUsPattern = CIRCLE_PATTERNS.find(p => p.id === 'just-us')
      if (justUsPattern) {
        suggestions.push({
          pattern: justUsPattern,
          confidence: 85,
          reason: "Personal concerns are often shared privately"
        })
      }
    }

    if (lowerContent.includes('ultrasound') || lowerContent.includes('appointment') || lowerContent.includes('doctor')) {
      const closeFamilyPattern = CIRCLE_PATTERNS.find(p => p.id === 'close-family')
      if (closeFamilyPattern) {
        suggestions.push({
          pattern: closeFamilyPattern,
          confidence: 80,
          reason: "Medical updates are typically shared with close family"
        })
      }
    }

    // Post type based suggestions
    const typeMap: Record<string, string[]> = {
      'ultrasound': ['close-family', 'grandparents'],
      'milestone': ['everyone', 'close-family'],
      'symptom': ['just-us', 'friends-support'],
      'announcement': ['everyone'],
      'question': ['friends-support', 'close-family']
    }

    const suggestedPatternIds = typeMap[postType] || []
    suggestedPatternIds.forEach(patternId => {
      const pattern = CIRCLE_PATTERNS.find(p => p.id === patternId)
      if (pattern && !suggestions.find(s => s.pattern.id === pattern.id)) {
        suggestions.push({
          pattern,
          confidence: 75,
          reason: `${postType} posts are usually shared this way`
        })
      }
    })

    return suggestions.sort((a, b) => b.confidence - a.confidence)
  }

  // Get pattern by ID
  const getPatternById = (id: string): CirclePattern | undefined => {
    return CIRCLE_PATTERNS.find(pattern => pattern.id === id)
  }

  // Get member count for pattern (mock implementation)
  const getPatternMemberCount = (pattern: CirclePattern): number => {
    return pattern.member_count || 0
  }

  // Generate onboarding content
  const generateOnboardingContent = (
    inviteContext: InviteContext
  ): { title: string; description: string; steps: string[] } => {
    const inviterName = inviteContext.inviter.first_name
    const babyName = inviteContext.pregnancy.baby_name || 'their baby'
    const relationship = inviteContext.inviter.relationship || 'family member'

    return {
      title: `Welcome to ${babyName}'s Journey!`,
      description: `${inviterName} has invited you to share in the excitement of their pregnancy journey as their ${relationship}.`,
      steps: [
        `You're now part of ${babyName}'s support circle`,
        "You'll receive updates about milestones and special moments",
        'You can react, comment, and share in the joy',
        'Your privacy is protected - only invited family sees updates'
      ]
    }
  }

  return {
    // State
    loading: readonly(loading),
    error: readonly(error),

    // Data
    CIRCLE_PATTERNS: readonly(CIRCLE_PATTERNS),

    // Methods
    fetchInviteContext,
    acceptInviteAndJoinCircles,
    createContextualInvite,
    suggestCirclesForRelationship,
    suggestCirclesForPost,
    getPatternById,
    getPatternMemberCount,
    generateOnboardingContent
  }
}