# Vue.js/Nuxt Feed System Component Specifications

## Executive Summary

This document provides comprehensive specifications for the Vue.js/Nuxt feed system overhaul, transforming the existing sophisticated components into a modern, Instagram-like pregnancy sharing experience. The design builds upon the current architecture while introducing advanced interaction patterns, optimistic updates, and comprehensive performance optimizations.

## 1. Component Architecture Overview

### Core Feed Components

```typescript
// Main feed components hierarchy
FeedTimeline.vue              // Primary container
├── FeedHeader.vue           // Sticky header with filters
├── FeedJourney.vue          // Personal pregnancy journey
├── FeedPostCard.vue         // Enhanced post cards
│   ├── PostHeader.vue       // Author info & metadata
│   ├── PostContent.vue      // Content with media
│   ├── PostEngagement.vue   // Reactions & interactions
│   └── FamilyComments.vue   // Threaded comments
├── MilestoneCard.vue        // Highlighted milestones
├── CelebrationBanner.vue    // Active celebrations
└── FeedFilters.vue          // Advanced filtering
```

### Supporting Components

```typescript
// Interaction components
FeedReactionPicker.vue       // Advanced reaction interface
ReactionSummary.vue          // Reaction aggregation
VirtualHug.vue              // Pregnancy-specific gestures
MemoryPrompt.vue            // Memory book integration
FamilyAvatarCluster.vue     // Family member indicators

// Performance components
VirtualScrollContainer.vue   // Virtual scrolling
LazyImageLoader.vue         // Optimized image loading
InfiniteLoadTrigger.vue     // Smooth infinite scroll
```

## 2. State Management - Pinia Store Design

### Feed Store Architecture

```typescript
// stores/feed.ts - Enhanced with real-time capabilities
interface FeedState {
  // Core data
  posts: EnrichedPost[]
  personalPosts: EnrichedPost[]
  celebrations: CelebrationPost[]
  
  // Real-time state
  realtimeUpdates: Map<string, any>
  optimisticUpdates: Map<string, OptimisticUpdate>
  connectionState: 'connected' | 'connecting' | 'disconnected'
  
  // Performance state
  viewportInfo: ViewportInfo
  preloadedImages: Set<string>
  scrollPosition: number
  
  // Interaction state
  activeReactions: Map<string, ReactionState>
  expandedComments: Set<string>
  pendingActions: Array<PendingAction>
}

interface OptimisticUpdate {
  id: string
  type: 'reaction' | 'comment' | 'view'
  postId: string
  data: any
  timestamp: number
  confirmed: boolean
  failed?: boolean
}

// Enhanced actions with optimistic updates
async function addReaction(postId: string, reactionType: PregnancyReactionType) {
  // 1. Immediate optimistic update
  const optimisticId = generateId()
  addOptimisticUpdate({
    id: optimisticId,
    type: 'reaction',
    postId,
    data: { reactionType },
    timestamp: Date.now(),
    confirmed: false
  })
  
  // 2. Update UI immediately
  updatePostReactionOptimistically(postId, reactionType)
  
  // 3. Send to backend
  try {
    const response = await api.addPostReaction(postId, { reaction_type: reactionType })
    confirmOptimisticUpdate(optimisticId, response.data)
  } catch (error) {
    failOptimisticUpdate(optimisticId)
    revertPostReaction(postId, reactionType)
    showErrorToast('Failed to add reaction')
  }
}
```

### Real-time Updates Integration

```typescript
// composables/useRealtimeFeed.ts
export const useRealtimeFeed = (pregnancyId: string) => {
  const feedStore = useFeedStore()
  const socket = useWebSocket()
  
  const subscribeToUpdates = () => {
    socket.subscribe(`pregnancy:${pregnancyId}:feed`, (update) => {
      switch (update.type) {
        case 'new_reaction':
          feedStore.handleRealtimeReaction(update.data)
          break
        case 'new_comment':
          feedStore.handleRealtimeComment(update.data)
          break
        case 'celebration':
          feedStore.handleRealtimeCelebration(update.data)
          break
      }
    })
  }
  
  return { subscribeToUpdates }
}
```

## 3. Enhanced Component Specifications

### 3.1 FeedTimeline.vue - Primary Container

```vue
<template>
  <div 
    ref="timelineRef" 
    class="feed-timeline relative"
    @scroll="handleScroll"
  >
    <!-- Sticky Header -->
    <FeedHeader
      :pregnancy-id="pregnancyId"
      :active-filter="activeFilter"
      :sort-by="sortBy"
      @filter-change="handleFilterChange"
      @sort-change="handleSortChange"
    />
    
    <!-- Personal Journey Section -->
    <FeedJourney
      v-if="showPersonalJourney"
      :pregnancy-context="pregnancyContext"
      :upcoming-milestones="upcomingMilestones"
      class="mb-6"
    />
    
    <!-- Active Celebrations -->
    <CelebrationBanner
      v-if="activeCelebrations.length"
      :celebrations="activeCelebrations"
      @dismiss="handleCelebrationDismiss"
      class="mb-6"
    />
    
    <!-- Virtual Scroll Container -->
    <VirtualScrollContainer
      :items="filteredPosts"
      :item-height="estimatePostHeight"
      :buffer-size="5"
      @visible-range="handleVisibleRangeChange"
    >
      <template #default="{ item: post, index }">
        <FeedPostCard
          :key="post.id"
          :post="post"
          :index="index"
          :celebrations="getCelebrationsForPost(post.id)"
          :highlighted="post.type === 'milestone'"
          @reaction="handleReaction"
          @comment="handleComment"
          @share="handleShare"
          @view="handleView"
          @double-tap="handleDoubleTapReaction"
          @swipe-left="handleSwipeLeft"
          @swipe-right="handleSwipeRight"
        />
      </template>
    </VirtualScrollContainer>
    
    <!-- Infinite Load Trigger -->
    <InfiniteLoadTrigger
      :loading="loading"
      :has-more="hasMore"
      @load-more="loadMore"
    />
    
    <!-- Floating Action Elements -->
    <ScrollToTopButton v-if="showScrollToTop" @click="scrollToTop" />
    <MemoryPrompt v-if="showMemoryPrompt" :post="currentMemoryPost" />
  </div>
</template>

<script setup lang="ts">
interface Props {
  pregnancyId: string
  initialFilter?: FeedFilterType
  showPersonalJourney?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialFilter: 'all',
  showPersonalJourney: true
})

// Enhanced composables
const { 
  posts, 
  filteredPosts, 
  activeCelebrations,
  loading, 
  hasMore 
} = storeToRefs(useFeedStore())

const { subscribeToUpdates } = useRealtimeFeed(props.pregnancyId)
const { initializeGestures } = useGestureRecognition()
const { monitorPerformance } = useFeedPerformance()
const { preloadImages } = useImageOptimization()

// Performance monitoring
const estimatePostHeight = (post: EnrichedPost) => {
  const baseHeight = 200
  const mediaHeight = post.media_items?.length ? 300 : 0
  const commentHeight = post.comment_preview?.total_count ? 50 : 0
  return baseHeight + mediaHeight + commentHeight
}

// Gesture handlers
const handleDoubleTapReaction = async (postId: string) => {
  await addReaction(postId, 'love')
  // Trigger celebration animation
  const postElement = document.querySelector(`[data-post-id="${postId}"]`)
  if (postElement) {
    triggerReactionAnimation(postElement, 'love')
  }
}

const handleSwipeLeft = (postId: string) => {
  // Add to memory book
  showMemoryPrompt.value = true
  currentMemoryPost.value = getPostById(postId)
}

const handleSwipeRight = (postId: string) => {
  // Quick love reaction
  handleDoubleTapReaction(postId)
}

// Lifecycle
onMounted(() => {
  subscribeToUpdates()
  monitorPerformance()
  preloadImages(filteredPosts.value.slice(0, 5))
})
</script>
```

### 3.2 FeedPostCard.vue - Enhanced Post Cards

```vue
<template>
  <article 
    ref="postCardRef"
    class="feed-post-card group relative bg-off-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-200"
    :class="cardVariantClasses"
    :data-post-id="post.id"
  >
    <!-- Milestone Badge -->
    <MilestoneBadge 
      v-if="isMilestone"
      :milestone-type="post.pregnancy_context?.milestone_type"
      :week="post.pregnancy_context?.current_week"
      class="absolute top-2 right-2 z-10"
    />
    
    <!-- Post Header -->
    <PostHeader 
      :post="post"
      :show-menu="!compact"
      @menu-action="handleMenuAction"
    />
    
    <!-- Post Content with Media -->
    <PostContent 
      :post="post"
      :expanded="isExpanded"
      :show-read-more="!compact"
      @toggle-expansion="toggleExpansion"
      @media-click="handleMediaClick"
    />
    
    <!-- Post Engagement Bar -->
    <PostEngagement
      :post="post"
      :reactions="reactionSummary"
      :comments="commentSummary"
      :user-reaction="userReaction"
      @reaction="handleReaction"
      @remove-reaction="handleRemoveReaction"
      @comment="toggleComments"
      @share="handleShare"
      @bookmark="handleBookmark"
    />
    
    <!-- Expandable Comments -->
    <Transition name="comments-expand">
      <FamilyComments
        v-if="showComments"
        :post-id="post.id"
        :comments="comments"
        :loading="loadingComments"
        @add-comment="handleAddComment"
        @reply="handleReply"
        @load-more="handleLoadMoreComments"
      />
    </Transition>
    
    <!-- Celebration Overlay -->
    <CelebrationOverlay
      v-if="showCelebration"
      :celebration-type="celebrationType"
      @complete="hideCelebration"
    />
    
    <!-- Loading State Overlay -->
    <Transition name="fade">
      <div 
        v-if="hasOptimisticUpdates"
        class="absolute inset-0 bg-off-white/50 flex items-center justify-center"
      >
        <LoadingSpinner size="sm" />
      </div>
    </Transition>
  </article>
</template>

<script setup lang="ts">
interface Props {
  post: EnrichedPost
  celebrations?: CelebrationPost[]
  highlighted?: boolean
  compact?: boolean
  index?: number
}

const props = withDefaults(defineProps<Props>(), {
  celebrations: () => [],
  highlighted: false,
  compact: false
})

// Local state
const isExpanded = ref(false)
const showComments = ref(false)
const loadingComments = ref(false)
const comments = ref<Comment[]>([])
const showCelebration = ref(false)
const celebrationType = ref<string>('')

// Computed properties
const isMilestone = computed(() => 
  props.post.type === 'milestone' || 
  props.post.pregnancy_context?.is_milestone_week
)

const cardVariantClasses = computed(() => ({
  'border-l-4 border-l-blush-rose bg-gradient-to-r from-blush-rose/5 to-transparent': isMilestone.value,
  'ring-2 ring-sage-green/20': props.celebrations.length > 0,
  'shadow-lg': props.highlighted
}))

const userReaction = computed(() => 
  props.post.reaction_summary?.user_reaction
)

const reactionSummary = computed(() => ({
  total: props.post.reaction_summary?.total_count || 0,
  breakdown: props.post.reaction_summary?.reaction_counts || {},
  recent: props.post.reaction_summary?.recent_reactors || []
}))

// Optimistic update tracking
const feedStore = useFeedStore()
const hasOptimisticUpdates = computed(() => 
  feedStore.hasOptimisticUpdatesForPost(props.post.id)
)

// Gesture integration
const { initializeGestures } = useGestureRecognition()

// Methods
const handleReaction = async (reactionType: string) => {
  try {
    await feedStore.addReaction(props.post.id, reactionType as PregnancyReactionType)
    
    // Trigger celebration animation
    triggerCelebration('reaction')
    
    // Haptic feedback on mobile
    if ('vibrate' in navigator) {
      navigator.vibrate(50)
    }
  } catch (error) {
    // Error handling is done in store
  }
}

const toggleComments = async () => {
  showComments.value = !showComments.value
  
  if (showComments.value && comments.value.length === 0) {
    await loadComments()
  }
}

const loadComments = async () => {
  loadingComments.value = true
  try {
    const response = await useApi().getPostComments(props.post.id)
    comments.value = response.data?.comments || []
  } finally {
    loadingComments.value = false
  }
}

const handleAddComment = async (commentData: { content: string, parentId?: string }) => {
  const optimisticComment = {
    id: `temp-${Date.now()}`,
    content: commentData.content,
    author: useAuth().userProfile.value,
    created_at: new Date().toISOString(),
    parent_id: commentData.parentId,
    temp: true
  }
  
  // Add optimistic comment
  if (commentData.parentId) {
    const parentIndex = comments.value.findIndex(c => c.id === commentData.parentId)
    if (parentIndex !== -1) {
      if (!comments.value[parentIndex].replies) {
        comments.value[parentIndex].replies = []
      }
      comments.value[parentIndex].replies!.push(optimisticComment)
    }
  } else {
    comments.value.unshift(optimisticComment)
  }
  
  try {
    const response = await useApi().createComment({
      post_id: props.post.id,
      content: commentData.content,
      parent_id: commentData.parentId
    })
    
    // Replace optimistic comment with real one
    const realComment = response.data
    if (commentData.parentId) {
      const parentIndex = comments.value.findIndex(c => c.id === commentData.parentId)
      if (parentIndex !== -1 && comments.value[parentIndex].replies) {
        const optimisticIndex = comments.value[parentIndex].replies!.findIndex(c => c.id === optimisticComment.id)
        if (optimisticIndex !== -1) {
          comments.value[parentIndex].replies![optimisticIndex] = realComment
        }
      }
    } else {
      const optimisticIndex = comments.value.findIndex(c => c.id === optimisticComment.id)
      if (optimisticIndex !== -1) {
        comments.value[optimisticIndex] = realComment
      }
    }
    
  } catch (error) {
    // Remove optimistic comment on error
    if (commentData.parentId) {
      const parentIndex = comments.value.findIndex(c => c.id === commentData.parentId)
      if (parentIndex !== -1 && comments.value[parentIndex].replies) {
        comments.value[parentIndex].replies = comments.value[parentIndex].replies!.filter(c => c.id !== optimisticComment.id)
      }
    } else {
      comments.value = comments.value.filter(c => c.id !== optimisticComment.id)
    }
    
    useToast().error('Failed to add comment')
  }
}

const triggerCelebration = (type: string) => {
  celebrationType.value = type
  showCelebration.value = true
  
  // Auto-hide after animation
  setTimeout(() => {
    showCelebration.value = false
  }, 2000)
}

// Lifecycle
onMounted(() => {
  if (postCardRef.value) {
    initializeGestures(postCardRef.value, {
      onDoubleTap: () => handleReaction('love'),
      onSwipeLeft: () => emit('swipe-left', props.post.id),
      onSwipeRight: () => emit('swipe-right', props.post.id),
      onLongPress: () => handleLongPress()
    })
  }
})
</script>

<style scoped>
.comments-expand-enter-active,
.comments-expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.comments-expand-enter-from {
  opacity: 0;
  transform: translateY(-20px);
  max-height: 0;
}

.comments-expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

.comments-expand-enter-to,
.comments-expand-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 500px;
}
</style>
```

## 4. Real-time Updates & Optimistic UI

### 4.1 Optimistic Updates Pattern

```typescript
// composables/useOptimisticUpdates.ts
export const useOptimisticUpdates = () => {
  const pendingUpdates = ref<Map<string, OptimisticUpdate>>(new Map())
  
  const addOptimisticUpdate = (update: OptimisticUpdate) => {
    pendingUpdates.value.set(update.id, update)
    
    // Auto-cleanup after timeout
    setTimeout(() => {
      if (pendingUpdates.value.has(update.id) && !update.confirmed) {
        failOptimisticUpdate(update.id)
      }
    }, 10000) // 10 second timeout
  }
  
  const confirmOptimisticUpdate = (updateId: string, serverData?: any) => {
    const update = pendingUpdates.value.get(updateId)
    if (update) {
      update.confirmed = true
      update.serverData = serverData
      
      // Clean up after short delay to allow UI to update
      setTimeout(() => {
        pendingUpdates.value.delete(updateId)
      }, 500)
    }
  }
  
  const failOptimisticUpdate = (updateId: string) => {
    const update = pendingUpdates.value.get(updateId)
    if (update) {
      update.failed = true
      
      // Trigger revert animation
      triggerRevertAnimation(update)
      
      setTimeout(() => {
        pendingUpdates.value.delete(updateId)
      }, 1000)
    }
  }
  
  return {
    pendingUpdates,
    addOptimisticUpdate,
    confirmOptimisticUpdate,
    failOptimisticUpdate
  }
}
```

### 4.2 Real-time Reaction System

```typescript
// components/FeedReactionPicker.vue
<template>
  <div class="reaction-picker">
    <!-- Quick Reactions -->
    <div class="quick-reactions flex items-center gap-2 mb-3">
      <button
        v-for="reaction in quickReactions"
        :key="reaction.type"
        @click="selectReaction(reaction.type)"
        :class="[
          'reaction-btn transition-all duration-200',
          userReaction === reaction.type && 'selected'
        ]"
      >
        <span class="text-lg">{{ reaction.emoji }}</span>
        <span class="text-xs ml-1">{{ reaction.count || 0 }}</span>
      </button>
    </div>
    
    <!-- Extended Reactions (on long press) -->
    <Transition name="slide-up">
      <div 
        v-if="showExtended"
        class="extended-reactions grid grid-cols-3 gap-2 p-3 bg-warm-gray rounded-lg"
      >
        <button
          v-for="reaction in extendedReactions"
          :key="reaction.type"
          @click="selectReaction(reaction.type)"
          class="extended-reaction-btn flex flex-col items-center p-2 rounded-md hover:bg-off-white transition-colors"
        >
          <span class="text-2xl mb-1">{{ reaction.emoji }}</span>
          <span class="text-xs text-neutral-gray">{{ reaction.label }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const quickReactions = [
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'excited', emoji: '😍', label: 'Excited' },
  { type: 'care', emoji: '🤗', label: 'Care' },
  { type: 'support', emoji: '💪', label: 'Support' }
]

const extendedReactions = [
  { type: 'beautiful', emoji: '✨', label: 'Beautiful' },
  { type: 'funny', emoji: '😂', label: 'Funny' },
  { type: 'praying', emoji: '🙏', label: 'Praying' },
  { type: 'proud', emoji: '🏆', label: 'Proud' },
  { type: 'grateful', emoji: '🙏✨', label: 'Grateful' }
]

const selectReaction = async (reactionType: string) => {
  // Immediate visual feedback
  triggerReactionAnimation(reactionType)
  
  // Optimistic update
  emit('reaction', { reactionType })
  
  // Haptic feedback
  if ('vibrate' in navigator) {
    navigator.vibrate([50, 50, 100])
  }
}
</script>
```

## 5. Performance Optimizations

### 5.1 Virtual Scrolling Implementation

```typescript
// composables/useVirtualScrolling.ts
export const useVirtualScrolling = <T>(
  items: Ref<T[]>,
  options: {
    itemHeight: (item: T, index: number) => number
    containerHeight: number
    buffer?: number
  }
) => {
  const scrollTop = ref(0)
  const containerRef = ref<HTMLElement>()
  
  const visibleRange = computed(() => {
    const buffer = options.buffer ?? 5
    const startIndex = Math.max(0, 
      Math.floor(scrollTop.value / averageItemHeight.value) - buffer
    )
    const endIndex = Math.min(
      items.value.length - 1,
      Math.ceil((scrollTop.value + options.containerHeight) / averageItemHeight.value) + buffer
    )
    
    return { startIndex, endIndex }
  })
  
  const visibleItems = computed(() => {
    const { startIndex, endIndex } = visibleRange.value
    return items.value.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
      key: `${startIndex + index}`
    }))
  })
  
  const totalHeight = computed(() => {
    return items.value.reduce((sum, item, index) => 
      sum + options.itemHeight(item, index), 0
    )
  })
  
  const offsetY = computed(() => {
    let offset = 0
    for (let i = 0; i < visibleRange.value.startIndex; i++) {
      offset += options.itemHeight(items.value[i], i)
    }
    return offset
  })
  
  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    scrollTop: readonly(scrollTop)
  }
}
```

### 5.2 Image Optimization

```typescript
// composables/useImageOptimization.ts
export const useImageOptimization = () => {
  const imageCache = new Map<string, HTMLImageElement>()
  const preloadQueue = ref<string[]>([])
  const isPreloading = ref(false)
  
  const preloadImage = (src: string): Promise<HTMLImageElement> => {
    return new Promise((resolve, reject) => {
      if (imageCache.has(src)) {
        resolve(imageCache.get(src)!)
        return
      }
      
      const img = new Image()
      img.onload = () => {
        imageCache.set(src, img)
        resolve(img)
      }
      img.onerror = reject
      
      // Use responsive image loading
      img.src = optimizeImageUrl(src, {
        width: window.innerWidth > 768 ? 600 : 400,
        quality: 85,
        format: 'webp'
      })
    })
  }
  
  const preloadImages = async (imageSrcs: string[], priority: 'high' | 'low' = 'low') => {
    if (priority === 'high') {
      // Preload immediately
      await Promise.allSettled(imageSrcs.map(preloadImage))
    } else {
      // Add to queue for background preloading
      preloadQueue.value.push(...imageSrcs)
      processPreloadQueue()
    }
  }
  
  const processPreloadQueue = async () => {
    if (isPreloading.value || preloadQueue.value.length === 0) return
    
    isPreloading.value = true
    
    while (preloadQueue.value.length > 0) {
      const src = preloadQueue.value.shift()!
      try {
        await preloadImage(src)
        // Small delay to avoid blocking the main thread
        await new Promise(resolve => setTimeout(resolve, 10))
      } catch (error) {
        console.warn('Failed to preload image:', src, error)
      }
    }
    
    isPreloading.value = false
  }
  
  return { preloadImage, preloadImages, imageCache }
}
```

## 6. Interaction Patterns

### 6.1 Instagram-like Gestures

```typescript
// Enhanced gesture integration for posts
const usePostGestures = (post: EnrichedPost) => {
  const { initializeGestures } = useGestureRecognition({
    pregnancyAdaptations: true,
    doubleTapWindow: 400, // More forgiving for pregnant users
    swipeThreshold: 40
  })
  
  const gestures = {
    // Double tap for love reaction
    onDoubleTap: (gesture: TapGesture) => {
      addReaction(post.id, 'love')
      showHeartAnimation(gesture.point)
    },
    
    // Swipe right for quick love
    onSwipeRight: (gesture: SwipeGesture) => {
      if (gesture.velocity > 0.3) {
        addReaction(post.id, 'love')
        showSwipeReactionAnimation('right')
      }
    },
    
    // Swipe left for memory book
    onSwipeLeft: (gesture: SwipeGesture) => {
      if (gesture.velocity > 0.3) {
        showMemoryBookPrompt(post)
        showSwipeReactionAnimation('left')
      }
    },
    
    // Long press for reaction picker
    onLongPress: (gesture: LongPressGesture) => {
      showReactionPicker(gesture.point)
      // Haptic feedback
      if ('vibrate' in navigator) {
        navigator.vibrate([100, 50, 100])
      }
    },
    
    // Long press start for visual feedback
    onLongPressStart: () => {
      showLongPressIndicator()
    }
  }
  
  return gestures
}
```

### 6.2 Accessibility Integration

```typescript
// composables/useReactionAccessibility.ts
export const useReactionAccessibility = () => {
  const announceReaction = (reactionType: string, postAuthor: string) => {
    const message = `Added ${reactionType} reaction to ${postAuthor}'s post`
    
    // Screen reader announcement
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message
    
    document.body.appendChild(announcement)
    
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }
  
  const getReactionLabel = (reactionType: string) => {
    const labels = {
      love: 'Send love and support',
      excited: 'Show excitement',
      care: 'Show care and concern',
      support: 'Offer support',
      beautiful: 'Say it\'s beautiful',
      funny: 'React with laughter',
      praying: 'Send prayers',
      proud: 'Show pride',
      grateful: 'Express gratitude'
    }
    
    return labels[reactionType as keyof typeof labels] || 'React to post'
  }
  
  return {
    announceReaction,
    getReactionLabel
  }
}
```

## 7. Responsive Design Implementation

### 7.1 Mobile-First Component Adaptations

```vue
<!-- FeedPostCard.vue mobile adaptations -->
<style scoped>
.feed-post-card {
  /* Desktop base styles */
  @apply rounded-lg border border-light-gray;
}

@media (max-width: 640px) {
  .feed-post-card {
    /* Mobile: edge-to-edge with minimal borders */
    @apply rounded-none border-0 border-b border-b-light-gray;
    margin-left: calc(-1 * theme('spacing.4'));
    margin-right: calc(-1 * theme('spacing.4'));
  }
  
  .post-content {
    /* Larger touch targets on mobile */
    padding: theme('spacing.4');
  }
  
  .reaction-buttons {
    /* Pregnancy-friendly larger buttons */
    gap: theme('spacing.4');
  }
  
  .reaction-btn {
    min-height: 44px; /* WCAG touch target size */
    min-width: 44px;
    padding: theme('spacing.3');
  }
}

@media (min-width: 768px) {
  .feed-post-card:hover {
    /* Desktop hover effects */
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(44, 41, 55, 0.1);
  }
}

/* Pregnancy-specific larger text option */
.large-text {
  .post-content {
    font-size: 1.125rem;
    line-height: 1.6;
  }
  
  .comment-text {
    font-size: 1rem;
  }
}
</style>
```

### 7.2 Adaptive Layout System

```typescript
// composables/useAdaptiveLayout.ts
export const useAdaptiveLayout = () => {
  const screenSize = useScreenSize()
  const userPreferences = useUserPreferences()
  
  const layout = computed(() => {
    const isMobile = screenSize.width < 768
    const isTablet = screenSize.width >= 768 && screenSize.width < 1024
    const isDesktop = screenSize.width >= 1024
    
    return {
      isMobile,
      isTablet,
      isDesktop,
      columns: isMobile ? 1 : isTablet ? 1 : 1, // Single column for feed
      spacing: isMobile ? 'sm' : 'md',
      cardSize: isMobile ? 'full' : 'contained',
      showSidebar: isDesktop,
      compactMode: userPreferences.value.compactMode || isMobile
    }
  })
  
  const adaptiveClasses = computed(() => ({
    container: layout.value.isMobile 
      ? 'px-0' 
      : 'px-4 max-w-2xl mx-auto',
    card: layout.value.cardSize === 'full' 
      ? 'w-full' 
      : 'max-w-lg mx-auto',
    spacing: layout.value.spacing === 'sm' 
      ? 'space-y-4' 
      : 'space-y-6'
  }))
  
  return { layout, adaptiveClasses }
}
```

## 8. Error States & Loading Patterns

### 8.1 Progressive Loading States

```vue
<!-- LoadingStates.vue -->
<template>
  <div class="loading-container">
    <!-- Skeleton Loading -->
    <div v-if="state === 'initial'" class="skeleton-feed">
      <div v-for="i in 3" :key="i" class="skeleton-post">
        <div class="skeleton-header">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-text skeleton-name"></div>
        </div>
        <div class="skeleton-content">
          <div class="skeleton-text skeleton-line"></div>
          <div class="skeleton-text skeleton-line short"></div>
        </div>
        <div class="skeleton-image"></div>
        <div class="skeleton-engagement">
          <div class="skeleton-button"></div>
          <div class="skeleton-button"></div>
          <div class="skeleton-button"></div>
        </div>
      </div>
    </div>
    
    <!-- Loading More -->
    <div v-else-if="state === 'loadingMore'" class="loading-more">
      <div class="flex items-center justify-center py-6">
        <LoadingSpinner class="mr-2" />
        <span class="text-neutral-gray">Loading more posts...</span>
      </div>
    </div>
    
    <!-- Network Error -->
    <div v-else-if="state === 'networkError'" class="error-state">
      <div class="text-center py-8">
        <div class="text-4xl mb-4">📡</div>
        <h3 class="font-semibold text-warm-graphite mb-2">Connection Issue</h3>
        <p class="text-neutral-gray text-sm mb-4">
          Having trouble connecting. Your posts are safe.
        </p>
        <BaseButton @click="retry" variant="outline" size="sm">
          Try Again
        </BaseButton>
      </div>
    </div>
    
    <!-- Server Error -->
    <div v-else-if="state === 'serverError'" class="error-state">
      <div class="text-center py-8">
        <div class="text-4xl mb-4">🔧</div>
        <h3 class="font-semibold text-warm-graphite mb-2">Something went wrong</h3>
        <p class="text-neutral-gray text-sm mb-4">
          We're working to fix this. Please try again in a moment.
        </p>
        <BaseButton @click="retry" variant="outline" size="sm">
          Refresh
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-post {
  @apply bg-off-white p-4 mb-4 rounded-lg;
}

.skeleton-avatar {
  @apply w-12 h-12 bg-light-gray rounded-full;
  animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-text {
  @apply bg-light-gray rounded;
  animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-name {
  @apply h-4 w-24;
}

.skeleton-line {
  @apply h-3 w-full mb-2;
}

.skeleton-line.short {
  @apply w-2/3;
}

.skeleton-image {
  @apply h-48 bg-light-gray rounded-lg my-3;
  animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-button {
  @apply h-8 w-16 bg-light-gray rounded mr-4;
  animation: skeleton-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
```

### 8.2 Graceful Degradation

```typescript
// composables/useGracefulDegradation.ts
export const useGracefulDegradation = () => {
  const features = ref({
    webSocket: true,
    serviceWorker: true,
    intersectionObserver: true,
    resizeObserver: true,
    vibration: 'vibrate' in navigator,
    touch: 'ontouchstart' in window
  })
  
  const checkFeatureSupport = () => {
    // Check WebSocket support
    try {
      features.value.webSocket = 'WebSocket' in window
    } catch {
      features.value.webSocket = false
    }
    
    // Check Service Worker support
    features.value.serviceWorker = 'serviceWorker' in navigator
    
    // Check Intersection Observer
    features.value.intersectionObserver = 'IntersectionObserver' in window
    
    // Check Resize Observer
    features.value.resizeObserver = 'ResizeObserver' in window
  }
  
  const getAdaptedBehavior = () => ({
    // Use polling instead of WebSocket if not supported
    realtimeUpdates: features.value.webSocket ? 'websocket' : 'polling',
    
    // Use timeout-based animation if no intersection observer
    scrollAnimation: features.value.intersectionObserver ? 'observer' : 'timeout',
    
    // Use click events instead of touch gestures if no touch support
    interactions: features.value.touch ? 'gestures' : 'clicks',
    
    // Disable advanced animations on low-end devices
    animations: window.navigator.hardwareConcurrency > 4 ? 'full' : 'reduced'
  })
  
  onMounted(() => {
    checkFeatureSupport()
  })
  
  return { features, getAdaptedBehavior }
}
```

## 9. Implementation Guidelines

### 9.1 Development Workflow

1. **Component Development Order:**
   ```
   1. Core data models and types
   2. Enhanced Pinia store with optimistic updates
   3. Base components (buttons, inputs, cards)
   4. Feed infrastructure (timeline, virtual scroll)
   5. Post components (header, content, engagement)
   6. Interaction systems (gestures, reactions)
   7. Real-time integration
   8. Performance optimizations
   9. Accessibility enhancements
   10. Testing and refinement
   ```

2. **Testing Strategy:**
   - Unit tests for composables and utilities
   - Component tests for user interactions
   - E2E tests for critical user journeys
   - Performance testing with virtual scrolling
   - Accessibility testing with screen readers

3. **Progressive Enhancement:**
   - Start with basic functionality
   - Add gesture recognition as enhancement
   - Implement real-time updates as progressive feature
   - Add advanced animations for capable devices

### 9.2 Performance Targets

- **Initial Load:** < 2s on 3G connection
- **Time to Interactive:** < 3s
- **Virtual Scroll Performance:** 60fps scrolling
- **Image Loading:** Progressive with WebP support
- **Memory Usage:** < 50MB for 100 posts
- **Battery Impact:** Minimal with efficient animations

### 9.3 Browser Support

- **Primary:** Chrome 90+, Safari 14+, Firefox 88+
- **Secondary:** Edge 90+
- **Mobile:** iOS Safari 14+, Chrome Mobile 90+
- **Graceful Degradation:** IE11 (basic functionality)

## Conclusion

This specification provides a comprehensive foundation for building a modern, Instagram-like pregnancy sharing feed system. The architecture emphasizes performance, accessibility, and user experience while maintaining the sophisticated design language of the existing application.

Key innovations include:
- Optimistic UI updates for immediate feedback
- Pregnancy-adapted gesture recognition
- Virtual scrolling for performance
- Real-time updates with graceful fallbacks
- Comprehensive accessibility support
- Mobile-first responsive design

The implementation should be done incrementally, starting with core functionality and progressively enhancing with advanced features. Each component should be thoroughly tested and optimized for the target user base of expectant parents and their families.