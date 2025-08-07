<template>
  <div :class="cn('family-comment relative', depth > 0 && 'ml-8 border-l-2 border-gray-100 pl-4')">
    <!-- Comment Content -->
    <div class="flex items-start gap-3">
      <!-- Avatar -->
      <UserAvatar :user="comment.author" size="md" />
      
      <!-- Comment Body -->
      <div class="flex-1 min-w-0">
        <!-- Author and Metadata -->
        <div class="flex items-center gap-2 mb-1">
          <span class="font-medium text-sm text-gray-900">
            {{ getUserDisplayName(comment.author) }}
          </span>
          
          <!-- Timestamp -->
          <span class="text-xs text-gray-500">
            {{ getRelativeTime() }}
          </span>
        </div>
        
        <!-- Comment Text -->
        <div class="text-sm text-gray-700 leading-relaxed mb-2">
          {{ comment.content }}
        </div>
        
        <!-- Pregnancy Context (if included) -->
        <div v-if="comment.pregnancy_context_included && pregnancyContext" 
             class="mb-2 p-2 bg-warm-neutral/20 rounded-lg text-xs text-gray-600">
          <span class="font-medium">Week {{ pregnancyContext.current_week }} context:</span>
          {{ getPregnancyContextMessage() }}
        </div>
        
        <!-- Comment Actions -->
        <div class="flex items-center gap-3 mt-3 text-xs">
          <!-- Like Button -->
          <button @click="$emit('like', comment.id)"
                  :class="cn(
                    'flex items-center gap-1 hover:text-gray-900 transition-colors font-medium',
                    comment.user_has_liked ? 'text-blue-600' : 'text-gray-500'
                  )">
            <span>{{ comment.user_has_liked ? 'Liked' : 'Like' }}</span>
          </button>
          
          <!-- Reply Button -->
          <button @click="$emit('reply', comment.id)"
                  class="text-gray-500 hover:text-gray-900 transition-colors font-medium">
            Reply
          </button>
          
          <!-- Reaction Count -->
          <span v-if="comment.reaction_count && comment.reaction_count > 0" class="text-gray-500">
            {{ comment.reaction_count }} {{ comment.reaction_count === 1 ? 'like' : 'likes' }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Nested Replies -->
    <div v-if="comment.replies && comment.replies.length > 0" class="replies mt-3">
      <FamilyComment
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :pregnancy-context="pregnancyContext"
        :depth="depth + 1"
        @reply="$emit('reply', $event)"
        @like="$emit('like', $event)"
        @report="$emit('report', $event)"
        @view-replies="$emit('view-replies', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import UserAvatar from '~/components/ui/UserAvatar.vue'
import { getUserDisplayName } from '@/utils/avatar'

type Comment = components['schemas']['CommentResponse']
type PregnancyContext = components['schemas']['PregnancyContext']

interface Props {
  comment: Comment
  pregnancyContext?: PregnancyContext
  depth?: number
}

const props = withDefaults(defineProps<Props>(), {
  depth: 0
})

defineEmits<{
  reply: [commentId: string]
  like: [commentId: string]
  report: [commentId: string]
  'view-replies': [commentId: string]
}>()


function getRelativeTime() {
  if (!props.comment.created_at) return 'Unknown time'
  
  const now = new Date()
  const commentTime = new Date(props.comment.created_at)
  const diffInMinutes = Math.floor((now.getTime() - commentTime.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
  if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d ago`
  
  return commentTime.toLocaleDateString()
}

function getPregnancyContextMessage() {
  if (!props.pregnancyContext) return ''
  
  const messages = []
  if (props.pregnancyContext.baby_development) {
    messages.push(`Baby: ${props.pregnancyContext.baby_development}`)
  }
  if (props.pregnancyContext.is_milestone_week) {
    messages.push('Milestone week!')
  }
  
  return messages.join(' • ')
}
</script>

<style scoped>
/* Individual comment animations */
.family-comment {
  animation: comment-appear 0.3s ease-out;
  animation-fill-mode: both;
}

@keyframes comment-appear {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Button hover effects */
.family-comment button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.family-comment button:hover {
  transform: translateY(-0.5px);
}

/* Enhanced accessibility */
.family-comment button:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .family-comment.ml-8 {
    margin-left: 1rem;
  }
}
</style>
