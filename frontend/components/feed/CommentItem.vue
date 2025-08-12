<!--
  Individual Comment Item Component
  Instagram-like comment with pregnancy-focused features
-->
<template>
  <div 
    ref="commentRef"
    class="comment-item flex gap-3 p-3 rounded-lg hover:bg-warm-gray/50 transition-all duration-200"
    :class="{
      'bg-blush-rose/5 border border-blush-rose/20': isHighlighted,
      'opacity-60': isDeleted
    }"
  >
    <!-- Author Avatar -->
    <div class="flex-shrink-0">
      <UserAvatar 
        :user="comment.author" 
        :size="threadDepth === 0 ? 'md' : 'sm'" 
        class="ring-2 ring-transparent transition-all duration-200"
        :class="{ 'ring-sage-green': isAuthorPregnant }"
      />
    </div>
    
    <!-- Comment Content -->
    <div class="flex-1 min-w-0">
      <!-- Author and Time -->
      <div class="flex items-center gap-2 mb-1">
        <span class="font-medium text-sm text-warm-graphite">
          {{ getAuthorName() }}
        </span>
        
        <!-- Author Tags -->
        <div class="flex items-center gap-1">
          <span
            v-if="isAuthorPregnant"
            class="inline-flex items-center px-1.5 py-0.5 bg-blush-rose/20 text-blush-rose text-xs font-medium rounded-full"
          >
            👶 Expecting
          </span>
          
          <span
            v-if="isAuthorFamily"
            class="inline-flex items-center px-1.5 py-0.5 bg-sage-green/20 text-sage-green text-xs font-medium rounded-full"
          >
            👨‍👩‍👧‍👦 Family
          </span>
        </div>
        
        <!-- Timestamp -->
        <span class="text-xs text-neutral-gray">
          {{ getRelativeTime() }}
        </span>
        
        <!-- Edited Indicator -->
        <span
          v-if="comment.edited_at"
          class="text-xs text-neutral-gray italic"
          :title="`Edited ${getEditedTime()}`"
        >
          edited
        </span>
      </div>
      
      <!-- Comment Text with Mentions -->
      <div class="text-sm text-soft-charcoal mb-2 leading-relaxed">
        <span
          v-if="!isDeleted"
          v-html="formatCommentContent()"
          class="comment-content"
        ></span>
        <span
          v-else
          class="italic text-neutral-gray"
        >
          This comment has been deleted
        </span>
      </div>
      
      <!-- Comment Actions -->
      <div v-if="!isDeleted" class="flex items-center gap-4">
        <!-- Like Button -->
        <button
          @click="handleLike"
          class="flex items-center gap-1 text-xs transition-all duration-200 hover:scale-105"
          :class="{
            'text-blush-rose font-medium': comment.user_has_liked,
            'text-neutral-gray hover:text-warm-graphite': !comment.user_has_liked
          }"
        >
          <Heart 
            :class="cn('w-3 h-3', comment.user_has_liked ? 'fill-current' : '')" 
          />
          <span>{{ comment.user_has_liked ? 'Liked' : 'Like' }}</span>
          <span v-if="comment.like_count && comment.like_count > 0" class="ml-1">
            ({{ comment.like_count }})
          </span>
        </button>
        
        <!-- Reply Button -->
        <button
          v-if="canReply"
          @click="handleReply"
          class="text-xs text-neutral-gray hover:text-warm-graphite transition-colors"
        >
          Reply
        </button>
        
        <!-- Delete Button (for author) -->
        <button
          v-if="canDelete"
          @click="handleDelete"
          class="text-xs text-neutral-gray hover:text-red-500 transition-colors"
        >
          Delete
        </button>
        
        <!-- Report Button -->
        <button
          v-if="!isCurrentUserComment"
          @click="handleReport"
          class="text-xs text-neutral-gray hover:text-orange-500 transition-colors"
        >
          Report
        </button>
      </div>
      
      <!-- Reply Count -->
      <div
        v-if="comment.reply_count && comment.reply_count > 0 && threadDepth === 0"
        class="mt-2 text-xs text-neutral-gray"
      >
        {{ comment.reply_count }} {{ comment.reply_count === 1 ? 'reply' : 'replies' }}
      </div>
    </div>
    
    <!-- Pregnancy Context Indicator -->
    <div
      v-if="pregnancyContext?.is_milestone_week && threadDepth === 0"
      class="flex-shrink-0 w-1 bg-gradient-to-b from-blush-rose to-sage-green rounded-full opacity-60"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { cn } from '~/components/ui/utils'
import { useAuth } from '~/composables/useAuth'
import { useGentleTransitions } from '~/composables/useAnimations'
import { Heart } from 'lucide-vue-next'
import UserAvatar from '~/components/ui/UserAvatar.vue'
import type { components } from '~/types/api'

type Comment = components['schemas']['CommentResponse']
type PregnancyContext = components['schemas']['PregnancyContextResponse']

interface Props {
  comment: Comment
  postId: string
  threadDepth?: number
  pregnancyContext?: PregnancyContext
  canReply?: boolean
  isHighlighted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  threadDepth: 0,
  canReply: true,
  isHighlighted: false
})

const emit = defineEmits<{
  reply: [commentId: string]
  like: [commentId: string]
  delete: [commentId: string]
  mention: [{ commentId: string, mentionedUserId: string, mentionedUserName: string }]
  report: [commentId: string]
}>()

// Composables
const auth = useAuth()
const { createGentleHover } = useGentleTransitions()

// Refs
const commentRef = ref<HTMLElement>()

// Computed
const isCurrentUserComment = computed(() => {
  return auth.userProfile.value?.id === props.comment.author?.id
})

const canDelete = computed(() => {
  return isCurrentUserComment.value // Only author can delete
})

const isDeleted = computed(() => {
  return props.comment.is_deleted || false
})

const isAuthorPregnant = computed(() => {
  // Check if comment author is the pregnant person
  return props.comment.author?.profile?.is_expecting || false
})

const isAuthorFamily = computed(() => {
  // Check if comment author is family member
  return props.comment.author?.profile?.relationship_type === 'family'
})

// Methods
function getAuthorName(): string {
  const author = props.comment.author
  if (!author) return 'Unknown User'
  
  return author.display_name || author.first_name || 'User'
}

function getRelativeTime(): string {
  if (!props.comment.created_at) return ''
  
  const now = new Date()
  const commentTime = new Date(props.comment.created_at)
  const diffInMinutes = Math.floor((now.getTime() - commentTime.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'now'
  if (diffInMinutes < 60) return `${diffInMinutes}m`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`
  if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d`
  
  return commentTime.toLocaleDateString()
}

function getEditedTime(): string {
  if (!props.comment.edited_at) return ''
  return new Date(props.comment.edited_at).toLocaleString()
}

function formatCommentContent(): string {
  let content = props.comment.content || ''
  
  // Escape HTML first
  content = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Format mentions (@username)
  content = content.replace(
    /@(\w+)/g,
    '<span class="mention text-blush-rose font-medium cursor-pointer hover:underline" data-mention="$1">@$1</span>'
  )
  
  // Format pregnancy-related emojis with extra styling
  const pregnancyEmojis = ['👶', '🤱', '🤰', '👪', '❤️', '💕', '✨', '🌟', '🎉']
  pregnancyEmojis.forEach(emoji => {
    content = content.replace(
      new RegExp(emoji, 'g'),
      `<span class="text-lg">${emoji}</span>`
    )
  })
  
  // Format URLs
  content = content.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-sage-green hover:underline">$1</a>'
  )
  
  // Format line breaks
  content = content.replace(/\n/g, '<br>')
  
  return content
}

function handleLike() {
  emit('like', props.comment.id)
}

function handleReply() {
  emit('reply', props.comment.id)
}

function handleDelete() {
  if (confirm('Are you sure you want to delete this comment?')) {
    emit('delete', props.comment.id)
  }
}

function handleReport() {
  emit('report', props.comment.id)
}

function handleMentionClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target.classList.contains('mention')) {
    const mentionedUser = target.getAttribute('data-mention')
    if (mentionedUser) {
      emit('mention', {
        commentId: props.comment.id,
        mentionedUserId: '', // Would need to resolve username to userId
        mentionedUserName: mentionedUser
      })
    }
  }
}

// Lifecycle
onMounted(() => {
  if (commentRef.value) {
    // Add gentle hover effect
    createGentleHover(commentRef.value, 'lift')
    
    // Set up mention click handlers
    commentRef.value.addEventListener('click', handleMentionClick)
  }
})
</script>

<style scoped>
/* Comment content styling */
.comment-content :deep(.mention) {
  @apply text-blush-rose font-medium cursor-pointer hover:underline;
}

.comment-content :deep(a) {
  @apply text-sage-green hover:underline;
}

/* Thread depth styling */
.comment-item {
  border-left: 2px solid transparent;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .comment-item {
    padding: 0.75rem;
  }
  
  .comment-item .gap-4 {
    gap: 0.75rem;
  }
  
  .comment-item .text-sm {
    font-size: 0.875rem;
    line-height: 1.4;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .comment-item {
    transition: none;
  }
  
  .transition-all {
    transition: none;
  }
}

/* Focus styles */
.comment-item button:focus-visible {
  outline: 2px solid theme(colors.blush-rose);
  outline-offset: 2px;
  border-radius: 4px;
}
</style>