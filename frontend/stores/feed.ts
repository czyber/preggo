import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { useWebSocket } from '~/composables/useWebSocket'
import { useOptimisticUpdates } from '~/composables/useOptimisticUpdates'
import { useAuth } from '~/composables/useAuth'
import type { components } from '@/types/api'

// Type aliases for cleaner code - matching backend schemas
type EnrichedPost = components['schemas']['EnrichedPost']
type FeedResponse = components['schemas']['FeedResponse']
type PersonalTimelineResponse = components['schemas']['PersonalTimelineResponse']
type FeedRequest = components['schemas']['FeedRequest']
type ReactionRequest = components['schemas']['ReactionRequest']
type ReactionResponse = components['schemas']['ReactionResponse']
type FeedFiltersResponse = components['schemas']['FeedFiltersResponse']
type CelebrationPost = components['schemas']['CelebrationPost']
type FeedAnalytics = components['schemas']['FeedAnalytics']

// Feed filter and sort types
type FeedFilterType = 'all' | 'my_posts' | 'milestones' | 'photos' | 'updates' | 'celebrations' | 'questions' | 'recent' | 'trending'
type FeedSortType = 'chronological' | 'engagement' | 'family_priority' | 'milestone_first'
type PregnancyReactionType = 'love' | 'excited' | 'care' | 'support' | 'beautiful' | 'funny' | 'praying' | 'proud' | 'grateful'

interface FeedState {
  posts: EnrichedPost[]
  personalPosts: EnrichedPost[]
  celebrations: CelebrationPost[]
  filters: FeedFiltersResponse | null
  analytics: FeedAnalytics | null
  currentPregnancyId: string | null
  loading: boolean
  error: string | null
  hasMore: boolean
  nextCursor: string | null
  totalCount: number
  activeFilter: FeedFilterType
  sortBy: FeedSortType
  lastFetchTime: Date | null
  cache: Map<string, { data: any; timestamp: number; ttl: number }>
  // Real-time state
  realtimeEnabled: boolean
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error'
  pendingOperations: Map<string, any>
  // Performance state
  virtualScrollEnabled: boolean
  prefetchDistance: number
}

export const useFeedStore = defineStore('feed', () => {
  // Auth composable - initialize at store level to avoid reactivity issues
  const auth = useAuth()
  
  // Real-time and optimistic updates composables - disabled for now
  // const websocket = useWebSocket({
  //   pregnancyOptimizations: true,
  //   enableHaptics: true
  // })
  
  // const optimisticUpdates = useOptimisticUpdates({
  //   pregnancyAdaptations: true,
  //   enableHapticFeedback: true
  // })
  
  // State as refs
  const posts = ref<EnrichedPost[]>([])
  const personalPosts = ref<EnrichedPost[]>([])
  const celebrations = ref<CelebrationPost[]>([])
  const filters = ref<FeedFiltersResponse | null>(null)
  const analytics = ref<FeedAnalytics | null>(null)
  const currentPregnancyId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const hasMore = ref(true)
  const nextCursor = ref<string | null>(null)
  const totalCount = ref(0)
  const activeFilter = ref<FeedFilterType>('all')
  const sortBy = ref<FeedSortType>('chronological')
  const lastFetchTime = ref<Date | null>(null)
  const cache = ref<Map<string, { data: any; timestamp: number; ttl: number }>>(new Map())
  
  // Real-time state - disabled for now
  const realtimeEnabled = ref(false)
  const connectionStatus = ref('disconnected')
  const pendingOperations = reactive<Map<string, any>>(new Map())
  
  // Performance state
  const virtualScrollEnabled = ref(true)
  const prefetchDistance = ref(3) // Number of posts to prefetch ahead

  // Computed properties
  const getPostById = computed(() => (id: string) => {
    return posts.value.find(post => post.id === id) || 
           personalPosts.value.find(post => post.id === id)
  })

  const allPosts = computed(() => {
    // Combine personal posts and family posts, then sort by date
    const combined = [...personalPosts.value, ...posts.value]
    
    return combined.sort((a, b) => {
      const dateA = new Date(a.created_at!).getTime()
      const dateB = new Date(b.created_at!).getTime()
      
      if (sortBy.value === 'chronological') {
        return dateB - dateA // Newest first
      } else if (sortBy.value === 'engagement') {
        const engagementA = (a.reaction_summary?.total_count || 0) + (a.comment_preview?.total_count || 0)
        const engagementB = (b.reaction_summary?.total_count || 0) + (b.comment_preview?.total_count || 0)
        return engagementB - engagementA
      } else if (sortBy.value === 'milestone_first') {
        const isAMilestone = a.type === 'milestone' || a.pregnancy_context?.is_milestone_week
        const isBMilestone = b.type === 'milestone' || b.pregnancy_context?.is_milestone_week
        if (isAMilestone && !isBMilestone) return -1
        if (!isAMilestone && isBMilestone) return 1
        return dateB - dateA
      }
      return dateB - dateA
    })
  })

  const filteredPosts = computed(() => {
    let filtered = allPosts.value

    // Apply active filter
    switch (activeFilter.value) {
      case 'my_posts':
        // Use auth from store level
        const currentUserId = auth.userProfile.value?.id
        filtered = filtered.filter(post => 
          post.author?.id === currentUserId
        )
        break
      case 'milestones':
        filtered = filtered.filter(post => 
          post.type === 'milestone' || 
          post.pregnancy_context?.is_milestone_week
        )
        break
      case 'photos':
        filtered = filtered.filter(post => 
          post.media_items && post.media_items.length > 0
        )
        break
      case 'updates':
        filtered = filtered.filter(post => 
          post.type === 'update' || post.type === 'journal'
        )
        break
      case 'celebrations':
        filtered = filtered.filter(post => 
          post.engagement_stats?.celebration_worthy || 
          celebrations.value.some(cel => cel.post_id === post.id)
        )
        break
      case 'questions':
        filtered = filtered.filter(post => 
          post.content?.includes('?') || 
          post.engagement_stats?.needs_family_response
        )
        break
      case 'recent':
        const threeDaysAgo = new Date()
        threeDaysAgo.setDate(threeDaysAgo.getDate() - 3)
        filtered = filtered.filter(post => 
          new Date(post.created_at!) > threeDaysAgo
        )
        break
      case 'trending':
        filtered = filtered.filter(post => post.is_trending)
        break
      default:
        // 'all' - no additional filtering
        break
    }

    // Apply sorting
    return filtered.sort((a, b) => {
      switch (sortBy.value) {
        case 'engagement':
          const aScore = a.engagement_stats?.engagement_score || 0
          const bScore = b.engagement_stats?.engagement_score || 0
          return bScore - aScore
        case 'family_priority':
          const aFamily = a.engagement_stats?.family_member_reactions || 0
          const bFamily = b.engagement_stats?.family_member_reactions || 0
          return bFamily - aFamily
        case 'milestone_first':
          const aMilestone = a.pregnancy_context?.is_milestone_week ? 1 : 0
          const bMilestone = b.pregnancy_context?.is_milestone_week ? 1 : 0
          if (aMilestone !== bMilestone) {
            return bMilestone - aMilestone
          }
          // Fall through to chronological for same milestone status
        case 'chronological':
        default:
          return new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime()
      }
    })
  })

  const milestonePosts = computed(() => {
    return posts.value.filter(post => 
      post.type === 'milestone' || 
      post.pregnancy_context?.is_milestone_week
    )
  })

  const needsAttentionPosts = computed(() => {
    return posts.value.filter(post => post.requires_attention)
  })

  const trendingPosts = computed(() => {
    return posts.value.filter(post => post.is_trending)
  })

  const upcomingMilestones = computed(() => {
    // This would come from the personal timeline response
    return personalPosts.value
      .filter(post => post.pregnancy_context?.is_milestone_week)
      .slice(0, 3)
  })

  const familyEngagementStats = computed(() => {
    const totalPosts = posts.value.length
    const totalReactions = posts.value.reduce((sum, post) => 
      sum + (post.reaction_summary?.total_count || 0), 0
    )
    const totalComments = posts.value.reduce((sum, post) => 
      sum + (post.comment_preview?.total_count || 0), 0
    )
    const avgEngagement = totalPosts > 0 ? (totalReactions + totalComments) / totalPosts : 0

    return {
      totalPosts,
      totalReactions,
      totalComments,
      avgEngagement: Math.round(avgEngagement * 100) / 100
    }
  })

  // Helper functions
  function getCacheKey(pregnancyId: string, requestData: FeedRequest): string {
    return `feed:${pregnancyId}:${JSON.stringify(requestData)}`
  }

  function getCachedData(key: string): any | null {
    const cached = cache.value.get(key)
    if (!cached) return null
    
    const now = Date.now()
    if (now > cached.timestamp + cached.ttl) {
      cache.value.delete(key)
      return null
    }
    
    return cached.data
  }

  function setCachedData(key: string, data: any, ttlMs: number = 120000): void {
    cache.value.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs
    })
  }

  // Real-time event handlers - disabled for now
  function setupRealtimeHandlers() {
    // Disabled WebSocket functionality
    return
  }
  
  function updatePostReaction(post: EnrichedPost, reactionType: string, userId: string, userDisplayName: string) {
    if (!post.reaction_summary) {
      post.reaction_summary = {
        total_count: 0,
        reaction_counts: {},
        recent_reactors: []
      }
    }
    
    // Update reaction count
    if (!post.reaction_summary.reaction_counts[reactionType]) {
      post.reaction_summary.reaction_counts[reactionType] = 0
    }
    post.reaction_summary.reaction_counts[reactionType]++
    post.reaction_summary.total_count++
    
    // Update recent reactors
    if (!post.reaction_summary.recent_reactors) {
      post.reaction_summary.recent_reactors = []
    }
    post.reaction_summary.recent_reactors.unshift(userDisplayName)
    post.reaction_summary.recent_reactors = post.reaction_summary.recent_reactors.slice(0, 3)
  }
  
  function updatePostComments(post: EnrichedPost, comment: any, userId: string, userDisplayName: string) {
    if (!post.comment_preview) {
      post.comment_preview = {
        total_count: 0,
        recent_comments: [],
        recent_commenters: []
      }
    }
    
    post.comment_preview.total_count++
    
    if (!post.comment_preview.recent_commenters) {
      post.comment_preview.recent_commenters = []
    }
    post.comment_preview.recent_commenters.unshift(userDisplayName)
    post.comment_preview.recent_commenters = post.comment_preview.recent_commenters.slice(0, 3)
  }
  
  function shouldIncludePostInFeed(post: EnrichedPost): boolean {
    // Apply current filter logic
    switch (activeFilter.value) {
      case 'milestones':
        return post.type === 'milestone' || post.pregnancy_context?.is_milestone_week
      case 'photos':
        return post.media_items && post.media_items.length > 0
      case 'updates':
        return post.type === 'update' || post.type === 'journal'
      default:
        return true
    }
  }
  
  function syncMissedUpdates() {
    // Fetch updates since last sync
    // In a real app, this would call a sync endpoint
    console.log('Syncing missed updates...')
  }

  // Actions with cursor-based pagination
  async function fetchFeed(pregnancyId?: string, options: Partial<FeedRequest> = {}) {
    loading.value = true
    error.value = null

    try {
      const api = useApi()
      const requestData: FeedRequest = {
        limit: 20,
        cursor: nextCursor.value,
        filter_type: activeFilter.value,
        sort_by: sortBy.value,
        include_reactions: true,
        include_comments: true,
        include_media: true,
        ...options
      }

      // Check cache for first-page requests
      if (pregnancyId && !nextCursor.value) {
        const cacheKey = getCacheKey(pregnancyId, requestData)
        const cachedData = getCachedData(cacheKey)
        if (cachedData) {
          posts.value = cachedData.posts || []
          personalPosts.value = cachedData.personalPosts || []
          hasMore.value = cachedData.hasMore || false
          nextCursor.value = cachedData.nextCursor || null
          totalCount.value = cachedData.totalCount || 0
          loading.value = false
          return
        }
      }

      if (pregnancyId) {
        currentPregnancyId.value = pregnancyId
        
        // Fetch both personal timeline and family feed in parallel
        const [personalResponse, familyResponse] = await Promise.all([
          api.getPersonalTimeline(pregnancyId),
          api.getFamilyFeed(pregnancyId, requestData)
        ])
        
        // Handle personal timeline
        if (!personalResponse.error) {
          const timelineResponse = personalResponse.data as PersonalTimelineResponse
          personalPosts.value = timelineResponse.posts || []
        } else {
          console.warn('Personal timeline failed to load:', personalResponse.error)
          personalPosts.value = []
        }
        
        // Handle family feed
        if (!familyResponse.error) {
          const feedResponse = familyResponse.data as FeedResponse
          
          if (!nextCursor.value) {
            posts.value = feedResponse.posts || []
          } else {
            posts.value.push(...(feedResponse.posts || []))
          }

          hasMore.value = feedResponse.has_more
          nextCursor.value = feedResponse.next_cursor || null
          totalCount.value = feedResponse.total_count
        } else {
          console.warn('Family feed failed to load:', familyResponse.error)
          posts.value = []
          hasMore.value = false
          nextCursor.value = null
          totalCount.value = personalPosts.value.length
        }

        // Cache the results for first-page requests
        if (!nextCursor.value) {
          const cacheKey = getCacheKey(pregnancyId, requestData)
          setCachedData(cacheKey, {
            posts: posts.value,
            personalPosts: personalPosts.value,
            hasMore: hasMore.value,
            nextCursor: nextCursor.value,
            totalCount: totalCount.value
          })
        }

      } else {
        // Fallback for no pregnancy ID - just fetch available posts
        const { data, error: apiError } = await api.getFamilyFeed(requestData)

        if (apiError) {
          throw new Error(`Failed to fetch feed: ${apiError}`)
        }

        const feedResponse = data as FeedResponse
        
        if (!nextCursor.value) {
          posts.value = feedResponse.posts || []
        } else {
          posts.value.push(...(feedResponse.posts || []))
        }

        hasMore.value = feedResponse.has_more
        nextCursor.value = feedResponse.next_cursor || null
        totalCount.value = feedResponse.total_count
      }

      lastFetchTime.value = new Date()

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching feed:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchPersonalTimeline(pregnancyId: string) {
    loading.value = true
    error.value = null

    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPersonalTimeline(pregnancyId)

      if (apiError) {
        throw new Error(`Failed to fetch personal timeline: ${apiError}`)
      }

      const timelineResponse = data as PersonalTimelineResponse
      personalPosts.value = timelineResponse.posts || []

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching personal timeline:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchFeedFilters() {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getFeedFilters()

      if (apiError) {
        throw new Error(`Failed to fetch feed filters: ${apiError}`)
      }

      filters.value = data as FeedFiltersResponse

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching feed filters:', err)
    }
  }

  async function fetchCelebrations(pregnancyId: string) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPregnancyCelebrations(pregnancyId)

      if (apiError) {
        throw new Error(`Failed to fetch celebrations: ${apiError}`)
      }

      celebrations.value = data?.celebrations || []

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching celebrations:', err)
    }
  }

  async function fetchAnalytics() {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getFeedAnalytics()

      if (apiError) {
        throw new Error(`Failed to fetch analytics: ${apiError}`)
      }

      analytics.value = data as FeedAnalytics

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching analytics:', err)
    }
  }

  async function addReaction(postId: string, reactionType: PregnancyReactionType) {
    const post = getPostById.value(postId)
    if (!post) {
      throw new Error('Post not found')
    }
    
    // Simplified reaction handling without optimistic updates for now
    
    // Apply optimistic UI update
    if (!post.reaction_summary) {
      post.reaction_summary = {
        total_count: 0,
        reaction_counts: {},
        recent_reactors: []
      }
    }
    
    const currentReaction = post.reaction_summary.user_reaction
    
    // Remove previous reaction count if exists
    if (currentReaction && post.reaction_summary.reaction_counts[currentReaction]) {
      post.reaction_summary.reaction_counts[currentReaction]--
      post.reaction_summary.total_count--
    }

    // Add new reaction count
    if (!post.reaction_summary.reaction_counts[reactionType]) {
      post.reaction_summary.reaction_counts[reactionType] = 0
    }
    post.reaction_summary.reaction_counts[reactionType]++
    post.reaction_summary.total_count++
    post.reaction_summary.user_reaction = reactionType
    
    try {
      const api = useApi()
      const reactionData: ReactionRequest = {
        post_id: postId,
        reaction_type: reactionType
      }

      const { data, error: apiError } = await api.addPostReaction(postId, reactionData)

      if (apiError) {
        throw new Error(`Failed to add reaction: ${apiError}`)
      }

      return data as ReactionResponse

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error adding reaction:', err)
      throw err
    }
  }

  async function removeReaction(postId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.removePostReaction(postId)

      if (apiError) {
        throw new Error(`Failed to remove reaction: ${apiError}`)
      }

      // Update local state optimistically
      const post = getPostById.value(postId)
      if (post && post.reaction_summary && post.reaction_summary.user_reaction) {
        const currentReaction = post.reaction_summary.user_reaction
        
        if (post.reaction_summary.reaction_counts[currentReaction]) {
          post.reaction_summary.reaction_counts[currentReaction]--
          post.reaction_summary.total_count--
        }
        
        post.reaction_summary.user_reaction = undefined
      }

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error removing reaction:', err)
      throw err
    }
  }

  async function recordView(postId: string) {
    try {
      const api = useApi()
      await api.recordPostView(postId)

      // Update local view count optimistically
      const post = getPostById.value(postId)
      if (post) {
        post.view_count = (post.view_count || 0) + 1
      }

    } catch (err) {
      // Views are non-critical, just log error
      console.error('Error recording view:', err)
    }
  }

  function updateFilter(filterType: FeedFilterType) {
    activeFilter.value = filterType
    // Reset pagination and refetch
    nextCursor.value = null
    posts.value = []
    lastFetchTime.value = null
    fetchFeed(currentPregnancyId.value || undefined)
  }

  function updateSort(sortType: FeedSortType) {
    sortBy.value = sortType
    // Re-sort existing posts without refetching
    // The computed filteredPosts will automatically update
  }

  async function loadMore() {
    if (hasMore.value && !loading.value) {
      await fetchFeed(currentPregnancyId.value || undefined)
    }
  }


  function reset() {
    posts.value = []
    personalPosts.value = []
    celebrations.value = []
    filters.value = null
    analytics.value = null
    currentPregnancyId.value = null
    loading.value = false
    error.value = null
    hasMore.value = true
    nextCursor.value = null
    totalCount.value = 0
    activeFilter.value = 'all'
    sortBy.value = 'chronological'
    lastFetchTime.value = null
    cache.value.clear()
    
    // Reset real-time state
    pendingOperations.clear()
    // optimisticUpdates.cleanup()
  }
  
  // Performance optimization methods
  function enableVirtualScrolling(enabled: boolean = true) {
    virtualScrollEnabled.value = enabled
  }
  
  function setPrefetchDistance(distance: number) {
    prefetchDistance.value = Math.max(1, Math.min(10, distance))
  }
  
  function enableRealtime(enabled: boolean = true) {
    realtimeEnabled.value = enabled
    if (enabled) {
      setupRealtimeHandlers()
    }
  }
  
  // Initialize the store
  function initialize() {
    if (realtimeEnabled.value) {
      setupRealtimeHandlers()
    }
  }
  
  // Call initialize when store is created
  initialize()

  // Return all state, computed properties, and functions
  return {
    // State
    posts,
    personalPosts,
    celebrations,
    filters,
    analytics,
    currentPregnancyId,
    loading,
    error,
    hasMore,
    nextCursor,
    totalCount,
    activeFilter,
    sortBy,
    lastFetchTime,
    
    // Real-time state
    realtimeEnabled,
    connectionStatus,
    pendingOperations,
    
    // Performance state
    virtualScrollEnabled,
    prefetchDistance,

    // Computed
    getPostById,
    filteredPosts,
    milestonePosts,
    needsAttentionPosts,
    trendingPosts,
    upcomingMilestones,
    familyEngagementStats,

    // Actions
    fetchFeed,
    fetchPersonalTimeline,
    fetchFeedFilters,
    fetchCelebrations,
    fetchAnalytics,
    addReaction,
    removeReaction,
    recordView,
    updateFilter,
    updateSort,
    loadMore,
    reset,
    
    // Real-time methods
    setupRealtimeHandlers,
    enableRealtime,
    
    // Performance methods
    enableVirtualScrolling,
    setPrefetchDistance
  }
})
