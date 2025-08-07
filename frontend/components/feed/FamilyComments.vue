<template>
  <div class="family-comments space-y-6">
    <!-- Comments Header -->
    <div v-if="comments.length > 0" class="px-6 py-4 border-b border-gray-100">
      <div class="text-sm font-medium text-gray-900">
        {{ comments.length }} {{ comments.length === 1 ? 'comment' : 'comments' }}
      </div>
    </div>

    <!-- Comments List -->
    <div class="comments-list px-6 space-y-4">
      <FamilyComment
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :pregnancy-context="pregnancyContext"
        :depth="0"
        @reply="handleReply"
        @like="handleLike"
        @report="handleReport"
        @view-replies="handleViewReplies"
      />
    </div>

    <!-- Add Comment Form -->
    <div class="add-comment p-6 bg-gray-50">
      <div class="flex items-start gap-3">
        <!-- User Avatar -->
        <UserAvatar :user="currentUser" size="md" />
        
        <!-- Comment Input -->
        <div class="flex-1">
          <textarea
            v-model="newCommentText"
            :placeholder="getCommentPlaceholder()"
            class="w-full resize-none bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
            rows="1"
            @keydown="handleKeyDown"
            @input="handleInput"
          />
          
          <!-- Submit Button -->
          <div class="flex justify-end mt-2">
            <button
              @click="handleSubmitComment"
              :disabled="!canSubmit"
              :class="cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                canSubmit
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              )"
            >
              {{ replyingTo ? 'Reply' : 'Post' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Reply Context -->
      <div v-if="replyingTo" class="mt-3 ml-11 p-2 bg-blue-50 rounded-lg border-l-2 border-blue-400">
        <div class="text-xs text-gray-600 mb-1">
          Replying to {{ getDisplayName(replyingTo.author) }}
        </div>
        <div class="text-xs text-gray-700 line-clamp-2">
          {{ replyingTo.content }}
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import FamilyComment from './FamilyComment.vue'
import UserAvatar from '~/components/ui/UserAvatar.vue'

type Comment = components['schemas']['CommentResponse']
type PregnancyContext = components['schemas']['PregnancyContext']

interface Props {
  comments: Comment[]
  pregnancyContext?: PregnancyContext
  postId: string
  hasMoreComments?: boolean
  remainingCount?: number
  loadingMore?: boolean
  showFamilySupportPrompt?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  hasMoreComments: false,
  remainingCount: 0,
  loadingMore: false,
  showFamilySupportPrompt: false
})

const emit = defineEmits<{
  addComment: [{ content: string, parentId?: string, includeContext: boolean }]
  loadMore: []
  reply: [commentId: string]
  like: [commentId: string]
  report: [commentId: string]
  viewReplies: [commentId: string]
}>()

// Local state
const newCommentText = ref('')
const includePregnancyContext = ref(false)
const replyingTo = ref<Comment | null>(null)
const sortBy = ref<'newest' | 'oldest' | 'family'>('newest')
const isCollapsed = ref(true)

// Get current user for avatar
const auth = useAuth()
const currentUser = computed(() => auth.userProfile.value)

// Computed properties
const canSubmit = computed(() => {
  return newCommentText.value.trim().length > 0
})

const sortedComments = computed(() => {
  const sorted = [...props.comments]
  
  switch (sortBy.value) {
    case 'oldest':
      return sorted.sort((a, b) => new Date(a.created_at!).getTime() - new Date(b.created_at!).getTime())
    case 'family':
      return sorted.sort((a, b) => {
        const aIsFamily = a.author?.is_family_member || false
        const bIsFamily = b.author?.is_family_member || false
        if (aIsFamily !== bIsFamily) {
          return bIsFamily ? 1 : -1
        }
        return new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime()
      })
    default: // newest
      return sorted.sort((a, b) => new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime())
  }
})

// Methods

function getDisplayName(author: any) {
  if (!author) {
    return 'Unknown User'
  }
  
  return author.display_name || author.first_name || author.email || 'Anonymous'
}

function getCommentPlaceholder() {
  if (replyingTo.value) {
    return `Reply to ${getDisplayName(replyingTo.value.author)}...`
  }
  
  if (props.pregnancyContext?.is_milestone_week) {
    return 'Congratulate and share your excitement...'
  }
  
  return 'Share your thoughts and support...'
}

function getFamilySupportMessage() {
  if (props.pregnancyContext?.is_milestone_week) {
    return 'This is a special milestone moment - let them know you\'re celebrating with them!'
  }
  
  return 'Show your love and support during this pregnancy journey.'
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
    event.preventDefault()
    handleSubmitComment()
  }
  
  if (event.key === 'Escape' && replyingTo.value) {
    cancelReply()
  }
}

function handleInput() {
  // Auto-resize textarea
  const textarea = event?.target as HTMLTextAreaElement
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
  }
}

function handleSubmitComment() {
  if (!canSubmit.value) return
  
  const commentData = {
    content: newCommentText.value.trim(),
    parentId: replyingTo.value?.id,
    includeContext: includePregnancyContext.value
  }
  
  emit('addComment', commentData)
  
  // Reset form
  newCommentText.value = ''
  includePregnancyContext.value = false
  replyingTo.value = null
}

function addSupportComment(supportText: string) {
  const commentData = {
    content: supportText,
    parentId: undefined,
    includeContext: true
  }
  
  emit('addComment', commentData)
}

function handleReply(commentId: string) {
  const comment = props.comments.find(c => c.id === commentId)
  if (comment) {
    replyingTo.value = comment
    includePregnancyContext.value = true
  }
  emit('reply', commentId)
}

function cancelReply() {
  replyingTo.value = null
  newCommentText.value = ''
}

function handleLike(commentId: string) {
  emit('like', commentId)
}

function handleReport(commentId: string) {
  emit('report', commentId)
}

function handleViewReplies(commentId: string) {
  emit('viewReplies', commentId)
}

function handleLoadMore() {
  emit('loadMore')
}

function handleSortChange() {
  // Sort change is reactive through computed property
}

function toggleCollapsed() {
  isCollapsed.value = !isCollapsed.value
}

// Watch for new comments to auto-expand if collapsed
watch(() => props.comments.length, (newLength, oldLength) => {
  if (newLength > oldLength && isCollapsed.value && newLength <= 5) {
    isCollapsed.value = false
  }
})
</script>


<style scoped>
/* Clean comments styling */
.family-comments {
  border-top: 1px solid #f3f4f6;
}

/* Textarea auto-resize */
.add-comment textarea {
  transition: height 0.2s ease;
  max-height: 120px;
  overflow-y: auto;
}

/* Button transitions */
.add-comment button {
  transition: background-color 0.2s ease;
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .comments-list {
    padding: 1rem;
  }
  
  .add-comment {
    padding: 1rem;
  }
}
</style>
