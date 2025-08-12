<template>
  <article 
    ref="postCardRef"
    class="feed-post-card bg-off-white border border-light-gray rounded-lg overflow-hidden hover:border-neutral-gray/40 transition-all duration-200 shadow-sm hover:shadow-md"
    :data-post-id="post.id"
  >
    <!-- Post Header -->
    <header class="px-4 py-3 border-b border-warm-gray">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- Author Avatar -->
          <UserAvatar :user="post.author" size="md" />
          
          <!-- Author Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium text-warm-graphite text-sm truncate font-inter">
                {{ getAuthorName() }}
              </span>
              
              <!-- Milestone Badge -->
              <span 
                v-if="post.pregnancy_context?.is_milestone_week" 
                class="inline-flex items-center gap-1 px-2 py-0.5 bg-dusty-lavender/20 text-warm-graphite text-xs font-medium rounded-full border border-dusty-lavender/30"
              >
                ✨ Milestone
              </span>
            </div>
            
            <!-- Pregnancy Context -->
            <div class="flex items-center gap-1 text-xs text-neutral-gray mt-0.5">
              <span v-if="post.pregnancy_context?.current_week">
                Week {{ post.pregnancy_context.current_week }}
              </span>
              <span v-if="post.pregnancy_context?.current_week && getRelativeTime()" class="text-light-gray">•</span>
              <span v-if="getRelativeTime()">{{ getRelativeTime() }}</span>
            </div>
          </div>
        </div>

        <!-- Circle Indicator & Menu -->
        <div class="flex items-center gap-2">
          <!-- Circle Badge -->
          <div class="flex items-center gap-1.5 px-2 py-1 bg-gray-50 rounded-full border border-gray-200">
            <span class="text-sm">{{ getCircleIcon() }}</span>
            <span class="text-xs font-medium text-gray-700">{{ getCircleName() }}</span>
          </div>

          <!-- Menu Button -->
          <button
            @click="handleMenuAction('menu')"
            class="p-1.5 hover:bg-warm-gray rounded-full transition-colors"
          >
            <svg class="w-4 h-4 text-neutral-gray" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Post Content -->
    <div class="px-4 py-3">
      <PostContent 
        :post="post"
        :expanded="isExpanded"
        @toggle-expansion="toggleExpansion"
        @media-click="handleMediaClick"
      />
    </div>

    <!-- Post Engagement -->
    <footer class="border-t border-warm-gray">
      <PostEngagement
        :post="post"
        :user-reaction="post.reaction_summary?.user_reaction"
        @reaction="handleReaction"
        @removeReaction="handleRemoveReaction"
        @comment="handleComment"
        @share="handleShare"
        @view-reactions="handleViewReactions"
        @view-comments="handleViewComments"
      />
      
      <!-- Comments Section (Instagram-style) -->
      <div v-if="showComments" class="comments-section border-t border-warm-gray">
        <FamilyComments
          :comments="postComments"
          :post-id="post.id!"
          :pregnancy-context="post.pregnancy_context"
          @add-comment="handleAddComment"
          @load-more="handleLoadMoreComments"
          @reply="handleReply"
          @like="handleLikeComment"
        />
      </div>
    </footer>

  </article>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import { useGentleTransitions, useFeedAnimations, useCelebrationAnimation, useScrollAnimation } from '~/composables/useAnimations'
import { usePostsStore } from "~/stores/posts"
import PostContent from "~/components/feed/PostContent.vue";
import PostHeader from "~/components/feed/PostHeader.vue";
import PostEngagement from "~/components/feed/PostEngagement.vue";
import FamilyComments from "~/components/feed/FamilyComments.vue";
import UserAvatar from "~/components/ui/UserAvatar.vue";

type EnrichedPost = components['schemas']['EnrichedPost']
type CelebrationPost = components['schemas']['CelebrationPost']
type Comment = components['schemas']['CommentResponse']

interface Props {
  post: EnrichedPost
  celebrations?: CelebrationPost[]
  highlighted?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  celebrations: () => [],
  highlighted: false,
  compact: false
})

const emit = defineEmits<{
  reaction: [{ postId: string, reactionType: string }]
  removeReaction: [postId: string]
  comment: [postId: string]
  share: [postId: string]
  view: [postId: string]
  menuAction: [{ action: string, postId: string }]
  mediaClick: [{ postId: string, mediaIndex: number }]
  viewReactions: [postId: string]
  viewComments: [postId: string]
}>()

// Simple transitions only
const { createGentleHover, animateElementIn } = useGentleTransitions()

// Auth composable for checking current user
const auth = useAuth()

// Store for handling comments
const postsStore = usePostsStore()

// Local state
const isExpanded = ref(false)
const isHighlighted = ref(props.highlighted)
const postCardRef = ref<HTMLElement>()
const showComments = ref(false)
const postComments = ref<Comment[]>([])
const loadingComments = ref(false)

// Computed properties
const isCurrentUserPost = computed(() => {
  const currentUserId = auth.userProfile.value?.id
  const postAuthorId = props.post.author?.id
  return !!(currentUserId && postAuthorId && currentUserId === postAuthorId)
})

// Helper methods for clean header
function getAuthorName() {
  const author = props.post.author
  if (!author) return 'Unknown User'
  
  return author.display_name || author.first_name || author.email || 'Unknown User'
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

// Computed
const getCardVariant = () => {
  if (props.post.type === 'milestone' || props.post.pregnancy_context?.is_milestone_week) {
    return 'milestone'
  }
  if (props.celebrations.length > 0) {
    return 'celebration'
  }
  if (props.post.engagement_stats?.needs_family_response) {
    return 'supportive'
  }
  if (props.post.is_trending) {
    return 'warm'
  }
  return 'default'
}

// Circle display helpers
const getCircleIcon = () => {
  const visibility = props.post.privacy?.visibility || 'ALL_FAMILY'
  const icons = {
    'PRIVATE': '🔒',
    'PARTNER_ONLY': '💕',
    'IMMEDIATE': '👨‍👩‍👧‍👦',
    'ALL_FAMILY': '🌟'
  }
  return icons[visibility] || '🌟'
}

const getCircleName = () => {
  const visibility = props.post.privacy?.visibility || 'ALL_FAMILY'
  const names = {
    'PRIVATE': 'Private',
    'PARTNER_ONLY': 'Partner',
    'IMMEDIATE': 'Inner Circle',
    'ALL_FAMILY': 'Everyone'
  }
  return names[visibility] || 'Everyone'
}

// Methods
function toggleExpansion() {
  isExpanded.value = !isExpanded.value
}

function handleReaction(data: { reactionType: string }) {
  emit('reaction', { postId: props.post.id!, reactionType: data.reactionType })
  
  // Simple visual feedback for reactions
  if (postCardRef.value) {
    animateElementIn(postCardRef.value)
  }
}

function handleRemoveReaction() {
  emit('removeReaction', props.post.id!)
}

async function handleComment() {
  showComments.value = !showComments.value
  
  // Load comments if showing and not already loaded
  if (showComments.value && postComments.value.length === 0) {
    await loadComments()
  }
  
  emit('comment', props.post.id!)
}

async function loadComments() {
  if (loadingComments.value) return
  
  try {
    loadingComments.value = true
    await postsStore.fetchPostComments(props.post.id!)
    postComments.value = postsStore.getCommentsForPost(props.post.id!)
  } catch (error) {
    console.error('Failed to load comments:', error)
  } finally {
    loadingComments.value = false
  }
}

async function handleAddComment(commentData: { content: string, parentId?: string, includeContext: boolean }) {
  try {
    await postsStore.createComment({
      post_id: props.post.id!,
      content: commentData.content,
      parent_id: commentData.parentId,
      user_id: auth.userProfile.value?.id!
    })
    
    // Update local comments from store (no duplicate addition)
    postComments.value = postsStore.getCommentsForPost(props.post.id!)
  } catch (error) {
    console.error('Failed to add comment:', error)
  }
}

async function handleLoadMoreComments() {
  // Implement pagination if needed
  await loadComments()
}

function handleReply(commentId: string) {
  // The FamilyComments component handles reply UI
  console.log('Reply to comment:', commentId)
}

async function handleLikeComment(commentId: string) {
  // Implement comment liking functionality
  console.log('Like comment:', commentId)
}

function handleShare() {
  emit('share', props.post.id!)
}

function handleView() {
  emit('view', props.post.id!)
}

function handleMenuAction(action: string) {
  emit('menuAction', { action, postId: props.post.id! })
}

function handleMediaClick(mediaIndex: number) {
  emit('mediaClick', { postId: props.post.id!, mediaIndex })
}

function handleViewReactions() {
  emit('viewReactions', props.post.id!)
}

function handleViewComments() {
  emit('viewComments', props.post.id!)
}


// Setup animations and interactions when component mounts
onMounted(async () => {
  await nextTick()
  
  if (postCardRef.value && typeof postCardRef.value.querySelectorAll === 'function') {
    // Set up scroll-triggered entry animation
    observeElement(postCardRef.value, {
      animation: 'fadeInUp',
      delay: 100,
      supportive: true
    })
    
    // Add entry animation
    animatePostEntry(postCardRef.value)
    
    // Add hover effects for interactive elements
    const interactiveElements = postCardRef.value.querySelectorAll('button, [role="button"]')
    interactiveElements.forEach(element => {
      createGentleHover(element as HTMLElement, 'lift')
    })
    
    // Special animations for milestone posts
    if (props.post.type === 'milestone' || props.post.pregnancy_context?.is_milestone_week) {
      setTimeout(() => {
        if (postCardRef.value) {
          glowElement(postCardRef.value, 4000)
        }
      }, 500)
    }
    
    // Special animations for celebration posts
    if (props.celebrations.length > 0) {
      setTimeout(() => {
        if (postCardRef.value) {
          pulseElement(postCardRef.value, 'warm')
        }
      }, 300)
    }
    
    // Special animations for posts needing family response
    if (props.post.engagement_stats?.needs_family_response) {
      setTimeout(() => {
        if (postCardRef.value) {
          pulseElement(postCardRef.value, 'supportive')
        }
      }, 200)
    }
  }
  
  // Use intersection observer to record view when post is visible
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
          handleView()
          observer.disconnect()
        }
      })
    },
    { threshold: 0.5 }
  )

  if (postCardRef.value && typeof postCardRef.value.querySelectorAll === 'function') {
    observer.observe(postCardRef.value)
  }

  onUnmounted(() => {
    observer.disconnect()
  })
})
</script>

<style scoped>
/* Clean, minimal post card styling */
.feed-post-card {
  transition: border-color 0.2s ease;
}

/* Comments section animation */
.comments-section {
  animation: comments-slide-in 0.2s ease-out;
}

@keyframes comments-slide-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .feed-post-card {
    border-radius: 0;
    border-left: 0;
    border-right: 0;
  }
}
</style>
