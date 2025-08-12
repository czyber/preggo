<!--
  Threaded Comment System with Real-time Features
  Instagram-like comment threading with pregnancy-focused UI
-->
<template>
  <div class="comment-thread" :data-thread-depth="threadDepth">
    <!-- Thread Comments -->
    <div class="space-y-3">
      <div
        v-for="comment in topLevelComments"
        :key="comment.id"
        class="comment-item"
        :data-comment-id="comment.id"
      >
        <!-- Main Comment -->
        <CommentItem
          :comment="comment"
          :postId="postId"
          :threadDepth="0"
          :pregnancyContext="pregnancyContext"
          :canReply="threadDepth < maxDepth"
          @reply="handleReply"
          @like="handleLikeComment"
          @delete="handleDeleteComment"
          @mention="handleMention"
        />
        
        <!-- Threaded Replies -->
        <div
          v-if="comment.replies && comment.replies.length > 0"
          class="mt-3 ml-8 border-l-2 border-light-gray pl-4 space-y-3"
        >
          <CommentThread
            v-for="reply in comment.replies.slice(0, getVisibleRepliesCount(comment.id))"
            :key="reply.id"
            :comments="[reply]"
            :postId="postId"
            :threadDepth="threadDepth + 1"
            :maxDepth="maxDepth"
            :pregnancyContext="pregnancyContext"
            @reply="handleReply"
            @like="handleLikeComment"
            @delete="handleDeleteComment"
            @mention="handleMention"
            @loadMore="handleLoadMoreReplies"
          />
          
          <!-- Show More Replies Button -->
          <button
            v-if="comment.replies.length > getVisibleRepliesCount(comment.id) && !loadingReplies[comment.id]"
            @click="handleLoadMoreReplies(comment.id)"
            class="flex items-center gap-2 text-sm text-neutral-gray hover:text-warm-graphite transition-colors py-2"
          >
            <div class="w-6 h-px bg-light-gray"></div>
            <span>Show {{ comment.replies.length - getVisibleRepliesCount(comment.id) }} more replies</span>
          </button>
          
          <!-- Loading More Replies -->
          <div
            v-if="loadingReplies[comment.id]"
            class="flex items-center gap-2 text-sm text-neutral-gray py-2"
          >
            <div class="w-6 h-px bg-light-gray"></div>
            <div class="w-4 h-4 border-2 border-neutral-gray/30 border-t-neutral-gray rounded-full animate-spin"></div>
            <span>Loading replies...</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Load More Comments -->
    <div v-if="hasMoreComments && threadDepth === 0" class="mt-4">
      <button
        @click="handleLoadMoreComments"
        :disabled="loadingMore"
        class="flex items-center gap-2 text-sm text-neutral-gray hover:text-warm-graphite transition-colors py-2 px-3 rounded-full hover:bg-warm-gray disabled:opacity-50"
      >
        <div v-if="loadingMore" class="w-4 h-4 border-2 border-neutral-gray/30 border-t-neutral-gray rounded-full animate-spin"></div>
        <MessageCircle v-else class="w-4 h-4" />
        <span>{{ loadingMore ? 'Loading...' : `Load ${remainingCommentsCount} more comments` }}</span>
      </button>
    </div>
    
    <!-- Comment Input -->
    <div v-if="threadDepth === 0 || showReplyInput" class="mt-4">
      <CommentInput
        :postId="postId"
        :parentId="replyingToCommentId"
        :pregnancyContext="pregnancyContext"
        :placeholder="getInputPlaceholder()"
        :mentionOptions="mentionOptions"
        @submit="handleAddComment"
        @cancel="handleCancelReply"
        @mention="handleMentionSearch"
      />
    </div>
    
    <!-- Real-time Typing Indicators -->
    <div v-if="typingUsers.length > 0" class="mt-2 flex items-center gap-2 text-xs text-neutral-gray">
      <div class="flex space-x-1">
        <div 
          v-for="i in 3" 
          :key="i"
          class="w-1 h-1 bg-sage-green rounded-full animate-pulse"
          :style="{ animationDelay: `${i * 0.2}s` }"
        ></div>
      </div>
      <span>{{ formatTypingUsers() }} typing...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import type { components } from '~/types/api'
import { useWebSocket } from '~/composables/useWebSocket'
import { useOptimisticUpdates } from '~/composables/useOptimisticUpdates'
import { MessageCircle } from 'lucide-vue-next'
import CommentItem from './CommentItem.vue'
import CommentInput from './CommentInput.vue'

type Comment = components['schemas']['CommentResponse']
type PregnancyContext = components['schemas']['PregnancyContextResponse']

interface Props {
  comments: Comment[]
  postId: string
  threadDepth?: number
  maxDepth?: number
  pregnancyContext?: PregnancyContext
  hasMoreComments?: boolean
  remainingCommentsCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  threadDepth: 0,
  maxDepth: 5,
  hasMoreComments: false,
  remainingCommentsCount: 0
})

const emit = defineEmits<{
  reply: [commentId: string]
  like: [commentId: string]
  delete: [commentId: string]
  mention: [{ commentId: string, mentionedUserId: string, mentionedUserName: string }]
  loadMore: [postId: string]
  addComment: [{ content: string, parentId?: string, mentions?: string[] }]
}>()

// Real-time composables - disabled for now
// const websocket = useWebSocket({
//   pregnancyOptimizations: true
// })

// const optimisticUpdates = useOptimisticUpdates({
//   pregnancyAdaptations: true
// })

// State
const showReplyInput = ref(false)
const replyingToCommentId = ref<string | undefined>()
const loadingMore = ref(false)
const loadingReplies = reactive<Record<string, boolean>>({})
const visibleRepliesCount = reactive<Record<string, number>>({})
const typingUsers = ref<Array<{ userId: string, userName: string, timestamp: number }>>([])
const mentionOptions = ref<Array<{ id: string, name: string, avatar?: string }>>([])

// Computed
const topLevelComments = computed(() => {
  // For top-level thread, show comments without parent_id
  // For nested threads, show all provided comments
  if (props.threadDepth === 0) {
    return props.comments.filter(comment => !comment.parent_id)
  }
  return props.comments
})

// Methods
function getVisibleRepliesCount(commentId: string): number {
  return visibleRepliesCount[commentId] || 3 // Show 3 replies by default
}

function handleReply(commentId: string) {
  replyingToCommentId.value = commentId
  showReplyInput.value = true
  emit('reply', commentId)
}

function handleCancelReply() {
  replyingToCommentId.value = undefined
  showReplyInput.value = false
}

function handleLikeComment(commentId: string) {
  // Simplified comment liking without optimistic updates
  const comment = findCommentById(commentId)
  if (comment) {
    const isLiked = comment.user_has_liked
    // const operationId = optimisticUpdates.applyOptimistic(
    //   commentId,
    //   'update',
    //   { liked: !isLiked },
    //   { liked: isLiked },
    // Optimistic updates disabled for now
    
    emit('like', commentId)
  }
}

function handleDeleteComment(commentId: string) {
  emit('delete', commentId)
}

function handleMention(data: { commentId: string, mentionedUserId: string, mentionedUserName: string }) {
  emit('mention', data)
}

function handleLoadMoreComments() {
  loadingMore.value = true
  emit('loadMore', props.postId)
  
  // Reset loading state after a reasonable timeout
  setTimeout(() => {
    loadingMore.value = false
  }, 5000)
}

function handleLoadMoreReplies(commentId: string) {
  loadingReplies[commentId] = true
  
  // Increase visible replies count
  const currentCount = visibleRepliesCount[commentId] || 3
  visibleRepliesCount[commentId] = currentCount + 5
  
  // Simulate loading (in real app, this would fetch from API)
  setTimeout(() => {
    loadingReplies[commentId] = false
  }, 1000)
}

function handleAddComment(data: { content: string, parentId?: string, mentions?: string[] }) {
  const commentData = {
    ...data,
    parentId: data.parentId || replyingToCommentId.value
  }
  
  emit('addComment', commentData)
  
  // Reset reply state
  handleCancelReply()
}

function handleMentionSearch(query: string) {
  // In real app, this would search for users
  // For now, return placeholder options
  mentionOptions.value = [
    { id: '1', name: 'Sarah Mom', avatar: '' },
    { id: '2', name: 'John Dad', avatar: '' },
    { id: '3', name: 'Grandma Mary', avatar: '' }
  ].filter(user => user.name.toLowerCase().includes(query.toLowerCase()))
}

function getInputPlaceholder(): string {
  if (replyingToCommentId.value) {
    const comment = findCommentById(replyingToCommentId.value)
    if (comment?.author?.display_name) {
      return `Reply to ${comment.author.display_name}...`
    }
    return 'Reply to comment...'
  }
  
  if (props.pregnancyContext?.is_milestone_week) {
    return 'Share your excitement about this milestone...'
  }
  
  return 'Add a loving comment...'
}

function findCommentById(commentId: string): Comment | undefined {
  for (const comment of props.comments) {
    if (comment.id === commentId) {
      return comment
    }
    
    // Search in replies recursively
    if (comment.replies) {
      const found = findCommentInReplies(comment.replies, commentId)
      if (found) return found
    }
  }
  return undefined
}

function findCommentInReplies(replies: Comment[], commentId: string): Comment | undefined {
  for (const reply of replies) {
    if (reply.id === commentId) {
      return reply
    }
    
    if (reply.replies) {
      const found = findCommentInReplies(reply.replies, commentId)
      if (found) return found
    }
  }
  return undefined
}

function formatTypingUsers(): string {
  const users = typingUsers.value
  if (users.length === 1) {
    return users[0].userName
  } else if (users.length === 2) {
    return `${users[0].userName} and ${users[1].userName}`
  } else if (users.length > 2) {
    return `${users[0].userName} and ${users.length - 1} others`
  }
  return ''
}

// Real-time handlers
function handleRealtimeTyping(message: any) {
  const { userId, userName, postId, isTyping } = message.payload
  
  if (postId !== props.postId) return
  
  const existingIndex = typingUsers.value.findIndex(user => user.userId === userId)
  
  if (isTyping) {
    if (existingIndex === -1) {
      typingUsers.value.push({
        userId,
        userName,
        timestamp: Date.now()
      })
    } else {
      typingUsers.value[existingIndex].timestamp = Date.now()
    }
  } else {
    if (existingIndex !== -1) {
      typingUsers.value.splice(existingIndex, 1)
    }
  }
}

function handleRealtimeComment(message: any) {
  const { postId, comment } = message.payload
  
  if (postId === props.postId) {
    // Add comment to the thread optimistically
    // In a real app, this would be handled by the parent component
    console.log('New comment received:', comment)
  }
}

// Cleanup typing indicators that are too old
function cleanupTypingIndicators() {
  const now = Date.now()
  typingUsers.value = typingUsers.value.filter(user => 
    now - user.timestamp < 10000 // Remove after 10 seconds
  )
}

// Lifecycle
onMounted(() => {
  // Set up WebSocket handlers - disabled for now
  // const unsubscribeTyping = websocket.onMessage('typing', handleRealtimeTyping)
  // const unsubscribeComment = websocket.onMessage('comment', handleRealtimeComment)
  
  // Set up cleanup interval
  const cleanupInterval = setInterval(cleanupTypingIndicators, 5000)
  
  onUnmounted(() => {
    // unsubscribeTyping()
    // unsubscribeComment()
    clearInterval(cleanupInterval)
  })
})

// Initialize visible replies count for existing comments
watch(() => props.comments, (newComments) => {
  newComments.forEach(comment => {
    if (comment.replies && comment.replies.length > 0) {
      if (!visibleRepliesCount[comment.id]) {
        visibleRepliesCount[comment.id] = Math.min(3, comment.replies.length)
      }
    }
  })
}, { immediate: true, deep: true })
</script>

<style scoped>
/* Thread depth indicators */
.comment-thread[data-thread-depth="0"] {
  --thread-color: theme(colors.light-gray);
}

.comment-thread[data-thread-depth="1"] {
  --thread-color: theme(colors.blush-rose / 0.3);
}

.comment-thread[data-thread-depth="2"] {
  --thread-color: theme(colors.sage-green / 0.3);
}

.comment-thread[data-thread-depth="3"] {
  --thread-color: theme(colors.dusty-lavender / 0.3);
}

.comment-thread[data-thread-depth="4"] {
  --thread-color: theme(colors.warm-gray);
}

/* Thread connection lines */
.comment-thread .border-l-2 {
  border-color: var(--thread-color, theme(colors.light-gray));
}

/* Smooth animations for expanding/collapsing */
.comment-item {
  animation: comment-fade-in 0.3s ease-out;
}

@keyframes comment-fade-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Typing indicator animation */
@keyframes typing-pulse {
  0%, 60%, 100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}

/* Mobile threading adjustments */
@media (max-width: 640px) {
  .comment-thread .ml-8 {
    margin-left: 1rem;
  }
  
  .comment-thread .pl-4 {
    padding-left: 0.75rem;
  }
  
  /* Reduce thread depth on mobile */
  .comment-thread[data-thread-depth="3"] .comment-thread,
  .comment-thread[data-thread-depth="4"] .comment-thread {
    margin-left: 0;
    padding-left: 0;
    border-left: none;
  }
}

/* Accessibility enhancements */
@media (prefers-reduced-motion: reduce) {
  .comment-item {
    animation: none;
  }
  
  .animate-spin {
    animation: none;
  }
  
  .animate-pulse {
    animation: none;
  }
}
</style>