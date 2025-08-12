<template>
  <div ref="engagementRef" class="post-engagement px-4 py-3">
    <!-- Enhanced Engagement Stats -->
    <div v-if="hasEngagement" class="mb-3 space-y-2">
      <!-- Reactions Summary with Animation -->
      <div v-if="totalReactions > 0" class="flex items-center gap-2">
        <div class="flex items-center gap-1">
          <!-- Top Reactions Display -->
          <div 
            v-for="(count, reactionType) in topReactions" 
            :key="reactionType"
            class="flex items-center bg-warm-gray rounded-full px-2 py-1 transition-all duration-300"
            :class="reactionAnimations[reactionType] ? 'scale-110 bg-blush-rose/20' : ''"
          >
            <span class="text-sm">{{ getReactionEmoji(reactionType) }}</span>
            <span 
              ref="reactionCounterRef"
              class="text-xs font-medium text-warm-graphite ml-1 transition-all duration-300"
              :class="reactionAnimations[reactionType] ? 'text-blush-rose' : ''"
            >
              {{ count }}
            </span>
          </div>
        </div>
        
        <!-- Total Reactions with Real-time Animation -->
        <button
          @click="$emit('viewReactions')"
          class="text-sm text-neutral-gray hover:text-warm-graphite transition-colors"
        >
          <span 
            ref="totalReactionsRef"
            class="transition-all duration-300"
            :class="totalReactionsPulse ? 'text-blush-rose scale-105 font-semibold' : ''"
          >
            {{ formatReactionText() }}
          </span>
        </button>
      </div>

      <!-- Comments Summary with Family Insights -->
      <div v-if="totalComments > 0" class="flex items-center justify-between">
        <button
          @click="$emit('viewComments')"
          class="text-sm text-neutral-gray hover:text-warm-graphite transition-colors"
        >
          <span 
            ref="totalCommentsRef"
            class="transition-all duration-300"
            :class="totalCommentsPulse ? 'text-sage-green scale-105 font-semibold' : ''"
          >
            {{ formatCommentText() }}
          </span>
        </button>
        
        <!-- Family Engagement Indicator -->
        <div v-if="familyEngagementInsights?.family_participation_rate" class="flex items-center gap-1 text-xs text-neutral-gray">
          <Users class="w-3 h-3" />
          <span>{{ Math.round(familyEngagementInsights.family_participation_rate * 100) }}% family</span>
        </div>
      </div>
      
      <!-- Recent Activity Preview -->
      <div v-if="recentActivity.length > 0" class="text-xs text-neutral-gray">
        <span>{{ formatRecentActivity() }}</span>
      </div>
    </div>

    <!-- Enhanced Action Buttons -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Enhanced Reaction Button with Intensity -->
        <div class="relative">
          <button
            ref="reactionButtonRef"
            @click="handleReaction"
            class="flex items-center gap-2 px-3 py-2 rounded-full transition-all duration-200 hover:bg-warm-gray"
            :class="{
              'text-blush-rose bg-blush-rose/10': userReaction,
              'text-neutral-gray hover:text-warm-graphite': !userReaction,
              'animate-bounce': reactionButtonAnimation
            }"
          >
            <Heart :class="cn('w-5 h-5 transition-all duration-200', {
              'text-blush-rose fill-current': userReaction,
              'scale-110': reactionButtonAnimation
            })" />
            <span class="text-sm font-medium">
              {{ userReaction ? getReactionLabel(userReaction) : 'Love' }}
            </span>
            
            <!-- Reaction Count Badge -->
            <span 
              v-if="totalReactions > 0"
              class="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 text-xs font-medium rounded-full transition-all duration-300"
              :class="{
                'bg-blush-rose text-white': userReaction,
                'bg-warm-gray text-neutral-gray': !userReaction
              }"
            >
              {{ totalReactions }}
            </span>
          </button>
          
          <!-- Reaction Intensity Indicator -->
          <div 
            v-if="reactionIntensity > 1"
            class="absolute -top-1 -right-1 w-3 h-3 bg-sage-green rounded-full flex items-center justify-center"
          >
            <TrendingUp class="w-2 h-2 text-white" />
          </div>
        </div>

        <!-- Enhanced Comment Button -->
        <button
          ref="commentButtonRef"
          @click="handleComment"
          class="flex items-center gap-2 px-3 py-2 rounded-full text-neutral-gray hover:text-warm-graphite hover:bg-warm-gray transition-all duration-200"
          :class="{ 'animate-pulse': commentButtonAnimation }"
        >
          <MessageCircle class="w-5 h-5" />
          <span class="text-sm font-medium">Comment</span>
          
          <!-- Comment Count Badge -->
          <span 
            v-if="totalComments > 0"
            class="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 text-xs font-medium bg-warm-gray text-neutral-gray rounded-full"
          >
            {{ totalComments }}
          </span>
        </button>

        <!-- Enhanced Share Button -->
        <button
          ref="shareButtonRef"
          @click="handleShare"
          class="flex items-center gap-2 px-3 py-2 rounded-full text-neutral-gray hover:text-warm-graphite hover:bg-warm-gray transition-all duration-200"
        >
          <Share class="w-5 h-5" />
          <span class="text-sm font-medium">Share</span>
        </button>
      </div>

      <!-- Enhanced Bookmark Button -->
      <button
        ref="bookmarkButtonRef"
        @click="handleBookmark"
        class="p-2 rounded-full transition-all duration-200"
        :class="{
          'text-sage-green bg-sage-green/10': isBookmarked,
          'text-neutral-gray hover:text-warm-graphite hover:bg-warm-gray': !isBookmarked
        }"
        :title="isBookmarked ? 'Remove from memory book' : 'Save to memory book'"
      >
        <Bookmark :class="cn('w-5 h-5 transition-all duration-200', {
          'fill-current': isBookmarked,
          'scale-110': bookmarkAnimation
        })" />
      </button>
    </div>
    
    <!-- Quick Reaction Intensity Display -->
    <div v-if="showIntensityIndicator" class="mt-2 flex items-center gap-2 text-xs text-neutral-gray">
      <div class="flex items-center gap-1">
        <div 
          v-for="i in 5" 
          :key="i"
          class="w-2 h-2 rounded-full transition-all duration-300"
          :class="i <= reactionIntensity ? 'bg-blush-rose' : 'bg-light-gray'"
        ></div>
      </div>
      <span>{{ getIntensityLabel() }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import { useReactionAnimation, useGentleTransitions, useFeedAnimations } from '~/composables/useAnimations'
import { useWebSocket } from '~/composables/useWebSocket'
import { useOptimisticUpdates } from '~/composables/useOptimisticUpdates'
import { Heart, MessageCircle, Share, Bookmark, Users, TrendingUp } from 'lucide-vue-next'

type EnrichedPost = components['schemas']['EnrichedPost']

interface Props {
  post: EnrichedPost
  userReaction?: string
  hasUserCommented?: boolean
  isBookmarked?: boolean
  showFamilyInsights?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  hasUserCommented: false,
  isBookmarked: false,
  showFamilyInsights: true
})

const emit = defineEmits<{
  reaction: [{ reactionType: string }]
  removeReaction: []
  comment: []
  share: []
  viewReactions: []
  viewComments: []
  bookmark: []
}>()

// Animation composables
const { animateReactionCounter } = useReactionAnimation()
const { createGentleHover, pulseElement } = useGentleTransitions()
const { animateEngagementUpdate } = useFeedAnimations()

// Real-time composables - disabled for now
// const websocket = useWebSocket({
//   pregnancyOptimizations: true
// })

// const optimisticUpdates = useOptimisticUpdates({
//   pregnancyAdaptations: true,
//   enableHapticFeedback: true
// })

// Local state
const engagementRef = ref<HTMLElement>()
const reactionButtonRef = ref<HTMLElement>()
const commentButtonRef = ref<HTMLElement>()
const shareButtonRef = ref<HTMLElement>()
const bookmarkButtonRef = ref<HTMLElement>()
const reactionCounterRef = ref<HTMLElement>()
const commentCounterRef = ref<HTMLElement>()
const totalReactionsRef = ref<HTMLElement>()
const totalCommentsRef = ref<HTMLElement>()
const previousReactionCount = ref(0)
const previousCommentCount = ref(0)

// Animation states
const reactionButtonAnimation = ref(false)
const commentButtonAnimation = ref(false)
const bookmarkAnimation = ref(false)
const totalReactionsPulse = ref(false)
const totalCommentsPulse = ref(false)

// Real-time states
const reactionAnimations = reactive<Record<string, boolean>>({})
const recentActivity = ref<Array<{ type: string, user: string, timestamp: number }>>([])
const reactionIntensity = ref(1)
const showIntensityIndicator = ref(false)

// Pregnancy-specific reactions mapping
const pregnancyReactions = {
  love: '❤️',
  excited: '😍',
  care: '🤗',
  support: '💪',
  beautiful: '✨',
  funny: '😂',
  praying: '🙏',
  proud: '🏆',
  grateful: '🙏✨'
}

// Computed properties
const totalReactions = computed(() => {
  return props.post.reaction_summary?.total_count || 0
})

const totalComments = computed(() => {
  return props.post.comment_preview?.total_count || 0
})

const hasEngagement = computed(() => {
  return totalReactions.value > 0 || totalComments.value > 0
})

const reactionCounts = computed(() => {
  return props.post.reaction_summary?.reaction_counts || {}
})

const userReaction = computed(() => {
  return props.post.reaction_summary?.user_reaction || props.userReaction
})

const topReactions = computed(() => {
  const reactions = reactionCounts.value
  const sorted = Object.entries(reactions)
    .filter(([_, count]) => count > 0)
    .sort(([_, a], [__, b]) => b - a)
    .slice(0, 3)
  
  return Object.fromEntries(sorted)
})

const recentReactors = computed(() => {
  return props.post.reaction_summary?.recent_reactors || []
})

const familyEngagementInsights = computed(() => {
  return props.post.engagement_stats?.family_insights
})

// Methods
function getReactionEmoji(reactionType: string) {
  return pregnancyReactions[reactionType as keyof typeof pregnancyReactions] || '❤️'
}

function formatReactionText() {
  const total = totalReactions.value
  const types = Object.keys(topReactions.value).length
  
  if (total === 1) {
    return '1 reaction'
  }
  
  if (types === 1) {
    const reactionType = Object.keys(topReactions.value)[0]
    return `${total} ${getReactionLabel(reactionType).toLowerCase()}`
  }
  
  return `${total} reactions`
}

function formatCommentText() {
  const total = totalComments.value
  if (total === 1) return '1 comment'
  return `${total} comments`
}

function formatRecentActivity() {
  if (recentActivity.value.length === 0) return ''
  
  const latest = recentActivity.value[0]
  const timeDiff = Date.now() - latest.timestamp
  
  if (timeDiff < 60000) { // Less than 1 minute
    return `${latest.user} just reacted`
  } else if (timeDiff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(timeDiff / 60000)
    return `${latest.user} reacted ${minutes}m ago`
  }
  
  return ''
}

function getReactionLabel(reactionType: string): string {
  const labels: Record<string, string> = {
    love: 'Love',
    excited: 'Excited',
    care: 'Caring',
    support: 'Support',
    beautiful: 'Beautiful',
    funny: 'Funny',
    praying: 'Praying',
    proud: 'Proud',
    grateful: 'Grateful'
  }
  return labels[reactionType] || 'Love'
}

function getIntensityLabel(): string {
  const intensity = reactionIntensity.value
  if (intensity <= 1) return 'Gentle reaction'
  if (intensity <= 2) return 'Sweet response'
  if (intensity <= 3) return 'Loving engagement'
  if (intensity <= 4) return 'Family excitement'
  return 'Overwhelming love!'
}

function triggerReactionAnimation(reactionType: string) {
  // Animate specific reaction type
  reactionAnimations[reactionType] = true
  setTimeout(() => {
    reactionAnimations[reactionType] = false
  }, 800)
  
  // Animate total reactions counter
  totalReactionsPulse.value = true
  setTimeout(() => {
    totalReactionsPulse.value = false
  }, 500)
}

function calculateReactionIntensity() {
  const reactionCounts = props.post.reaction_summary?.reaction_counts || {}
  const totalReactions = Object.values(reactionCounts).reduce((sum, count) => sum + count, 0)
  const reactionTypes = Object.keys(reactionCounts).filter(type => reactionCounts[type] > 0).length
  
  // Calculate intensity based on total reactions and variety
  let intensity = Math.min(5, Math.floor(totalReactions / 3) + Math.floor(reactionTypes / 2))
  
  // Boost for pregnancy milestones
  if (props.post.type === 'milestone' || props.post.pregnancy_context?.is_milestone_week) {
    intensity = Math.min(5, intensity + 1)
  }
  
  reactionIntensity.value = Math.max(1, intensity)
  
  // Show intensity indicator for high engagement
  showIntensityIndicator.value = intensity > 2
  
  // Auto-hide after 3 seconds
  if (showIntensityIndicator.value) {
    setTimeout(() => {
      showIntensityIndicator.value = false
    }, 3000)
  }
}

// Real-time update handlers
function handleRealtimeReaction(message: any) {
  const { reactionType, userId, userDisplayName } = message.payload
  
  // Add to recent activity
  recentActivity.value.unshift({
    type: 'reaction',
    user: userDisplayName,
    timestamp: Date.now()
  })
  
  // Limit recent activity to 3 items
  recentActivity.value = recentActivity.value.slice(0, 3)
  
  // Trigger animation for this reaction type
  triggerReactionAnimation(reactionType)
  
  // Recalculate intensity
  calculateReactionIntensity()
}

function handleRealtimeComment(message: any) {
  const { userId, userDisplayName } = message.payload
  
  // Add to recent activity
  recentActivity.value.unshift({
    type: 'comment',
    user: userDisplayName,
    timestamp: Date.now()
  })
  
  // Limit recent activity to 3 items
  recentActivity.value = recentActivity.value.slice(0, 3)
  
  // Animate total comments counter
  totalCommentsPulse.value = true
  setTimeout(() => {
    totalCommentsPulse.value = false
  }, 500)
}

function formatCommenters() {
  const commenters = props.post.comment_preview?.recent_commenters || []
  
  if (commenters.length === 0) return ''
  if (commenters.length === 1) return commenters[0]
  if (commenters.length === 2) return `${commenters[0]} and ${commenters[1]}`
  
  return `${commenters[0]}, ${commenters[1]} and ${commenters.length - 2} others`
}

function formatViewCount() {
  const count = props.post.view_count || 0
  if (count < 1000) return count.toString()
  if (count < 10000) return `${Math.floor(count / 100) / 10}k`
  return `${Math.floor(count / 1000)}k`
}

function getRelativeTime() {
  if (!props.post.created_at) return ''
  
  const now = new Date()
  const postTime = new Date(props.post.created_at)
  const diffInHours = Math.floor((now.getTime() - postTime.getTime()) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return 'now'
  if (diffInHours < 24) return `${diffInHours}h`
  if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d`
  
  return postTime.toLocaleDateString()
}

// Event handlers with optimistic updates
function handleReaction() {
  const reactionType = userReaction.value ? undefined : 'love'
  
  // Simplified reaction handling without optimistic updates
  if (reactionType) {
    // Optimistic updates disabled for now
    
    emit('reaction', { reactionType })
    
    // Trigger animations
    triggerReactionAnimation(reactionType)
    
    // Calculate intensity based on engagement velocity
    calculateReactionIntensity()
  } else {
    emit('removeReaction')
  }
  
  // Animate the reaction button
  reactionButtonAnimation.value = true
  setTimeout(() => {
    reactionButtonAnimation.value = false
  }, 600)
}

function handleRemoveReaction() {
  emit('removeReaction')
  
  // Animate the engagement section
  if (engagementRef.value) {
    animateEngagementUpdate(engagementRef.value)
  }
}

function handleComment() {
  emit('comment')
  
  // Animate comment button
  commentButtonAnimation.value = true
  setTimeout(() => {
    commentButtonAnimation.value = false
  }, 400)
  
  // Add gentle pulse to comment area
  if (engagementRef.value) {
    pulseElement(engagementRef.value, 'supportive')
  }
}

function handleShare() {
  emit('share')
  
  // Add gentle pulse to engagement area
  if (engagementRef.value) {
    pulseElement(engagementRef.value, 'gentle')
  }
}

function handleViewReactions() {
  emit('viewReactions')
}

function handleViewComments() {
  emit('viewComments')
}

function handleBookmark() {
  emit('bookmark')
  
  // Animate bookmark button
  bookmarkAnimation.value = true
  setTimeout(() => {
    bookmarkAnimation.value = false
  }, 300)
  
  // Add gentle pulse for bookmark feedback
  if (engagementRef.value) {
    pulseElement(engagementRef.value, 'warm')
  }
}

// Lifecycle
onMounted(() => {
  // Set initial counter values
  previousReactionCount.value = totalReactions.value
  previousCommentCount.value = totalComments.value
  
  // Calculate initial reaction intensity
  calculateReactionIntensity()
  
  // Set up hover effects for buttons
  if (engagementRef.value) {
    const buttons = engagementRef.value.querySelectorAll('button')
    buttons.forEach(button => {
      createGentleHover(button as HTMLElement, 'lift')
    })
  }
  
  // Set up real-time message handlers - disabled for now
  // const unsubscribeReaction = websocket.onMessage('reaction', handleRealtimeReaction)
  // const unsubscribeComment = websocket.onMessage('comment', handleRealtimeComment)
  
  // Cleanup on unmount
  onUnmounted(() => {
    // unsubscribeReaction()
    // unsubscribeComment()
  })
})

// Watch for counter changes and animate
watch(totalReactions, (newCount, oldCount) => {
  if (oldCount > 0 && newCount > oldCount && reactionCounterRef.value) {
    animateReactionCounter(reactionCounterRef.value, true)
  }
  previousReactionCount.value = newCount
})

watch(totalComments, (newCount, oldCount) => {
  if (oldCount > 0 && newCount > oldCount && commentCounterRef.value) {
    animateReactionCounter(commentCounterRef.value, true)
  }
  previousCommentCount.value = newCount
})
</script>

<style scoped>
/* Clean engagement styling */
.post-engagement button {
  transition: color 0.2s ease;
}

.post-engagement button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .post-engagement {
    padding: 0.75rem 1rem;
  }
  
  .post-engagement .flex.items-center.gap-6 {
    gap: 1.5rem;
  }
}
</style>
