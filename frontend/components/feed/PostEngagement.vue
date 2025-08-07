<template>
  <div ref="engagementRef" class="post-engagement px-4 py-3">
    <!-- Engagement Stats (if any) -->
    <div v-if="hasEngagement" class="mb-3 space-y-1">
      <!-- Reactions Summary -->
      <div v-if="totalReactions > 0" class="text-sm text-gray-600">
        {{ formatReactionText() }}
      </div>

      <!-- Comments Summary -->
      <div v-if="totalComments > 0" class="text-sm text-gray-600">
        {{ totalComments }} {{ totalComments === 1 ? 'comment' : 'comments' }}
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-6">
        <!-- Like Button -->
        <button
          @click="handleReaction"
          class="flex items-center gap-1.5 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg class="w-5 h-5" :class="userReaction ? 'text-rose-500 fill-current' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <span class="text-sm font-medium">{{ userReaction ? 'Liked' : 'Like' }}</span>
        </button>

        <!-- Comment Button -->
        <button
          @click="handleComment"
          class="flex items-center gap-1.5 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a9.954 9.954 0 01-4.951-1.323L3 21l2.323-5.051C4.477 14.934 3 13.054 3 11c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
          </svg>
          <span class="text-sm font-medium">Comment</span>
        </button>

        <!-- Share Button -->
        <button
          @click="handleShare"
          class="flex items-center gap-1.5 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          <span class="text-sm font-medium">Share</span>
        </button>
      </div>

      <!-- Bookmark Button -->
      <button
        @click="handleBookmark"
        :class="cn(
          'p-1 text-gray-600 hover:text-gray-900 transition-colors',
          isBookmarked && 'text-gray-900'
        )"
        :title="isBookmarked ? 'Remove from memory book' : 'Save to memory book'"
      >
        <svg class="w-5 h-5" :fill="isBookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import { useReactionAnimation, useGentleTransitions, useFeedAnimations } from '~/composables/useAnimations'

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

// Local state
const engagementRef = ref<HTMLElement>()
const reactionCounterRef = ref<HTMLElement>()
const commentCounterRef = ref<HTMLElement>()
const previousReactionCount = ref(0)
const previousCommentCount = ref(0)

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
    return `${total} reactions`
  }
  
  return `${total} reactions`
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

// Event handlers
function handleReaction() {
  // Toggle the main reaction (love for pregnancy posts)
  if (userReaction.value) {
    emit('removeReaction')
  } else {
    emit('reaction', { reactionType: 'love' })
  }
  
  // Animate the engagement section
  if (engagementRef.value) {
    animateEngagementUpdate(engagementRef.value)
  }
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
  
  // Set up hover effects for buttons
  if (engagementRef.value) {
    const buttons = engagementRef.value.querySelectorAll('button')
    buttons.forEach(button => {
      createGentleHover(button as HTMLElement, 'lift')
    })
  }
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
