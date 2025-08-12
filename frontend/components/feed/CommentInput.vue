<!--
  Comment Input Component
  Instagram-like comment input with mention support and real-time typing indicators
-->
<template>
  <div class="comment-input relative">
    <!-- Input Container -->
    <div class="flex gap-3 items-start">
      <!-- Current User Avatar -->
      <UserAvatar 
        :user="auth.userProfile.value"
        size="sm"
        class="flex-shrink-0 mt-1"
      />
      
      <!-- Input Area -->
      <div class="flex-1 relative">
        <!-- Text Input -->
        <div
          ref="inputContainerRef"
          class="relative min-h-[2.5rem] max-h-32 overflow-hidden border border-light-gray rounded-2xl bg-warm-gray/50 focus-within:border-blush-rose focus-within:bg-white transition-all duration-200"
        >
          <textarea
            ref="textareaRef"
            v-model="inputValue"
            :placeholder="placeholder"
            @input="handleInput"
            @keydown="handleKeydown"
            @focus="handleFocus"
            @blur="handleBlur"
            @paste="handlePaste"
            class="w-full min-h-[2.5rem] max-h-32 px-4 py-3 bg-transparent border-0 outline-0 resize-none text-sm placeholder:text-neutral-gray"
            :class="{ 'pr-24': showActions }"
            style="field-sizing: content;"
          ></textarea>
          
          <!-- Mention Dropdown -->
          <div
            v-if="showMentions && mentionOptions.length > 0"
            ref="mentionDropdownRef"
            class="absolute bottom-full left-0 right-0 mb-2 bg-white border border-light-gray rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
          >
            <div
              v-for="(option, index) in mentionOptions"
              :key="option.id"
              @click="selectMention(option)"
              class="flex items-center gap-3 px-4 py-3 hover:bg-warm-gray cursor-pointer transition-colors"
              :class="{ 'bg-blush-rose/10': index === selectedMentionIndex }"
            >
              <UserAvatar :user="{ avatar_url: option.avatar, display_name: option.name }" size="xs" />
              <div class="flex-1 min-w-0">
                <div class="font-medium text-sm text-warm-graphite">{{ option.name }}</div>
                <div v-if="option.relationship" class="text-xs text-neutral-gray">{{ option.relationship }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div
          v-if="showActions"
          class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2"
        >
          <!-- Cancel Button -->
          <button
            v-if="parentId"
            @click="handleCancel"
            type="button"
            class="px-3 py-1.5 text-xs font-medium text-neutral-gray hover:text-warm-graphite transition-colors"
          >
            Cancel
          </button>
          
          <!-- Submit Button -->
          <button
            @click="handleSubmit"
            :disabled="!canSubmit"
            type="button"
            class="px-3 py-1.5 bg-blush-rose text-white text-xs font-medium rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blush-rose/90 hover:scale-105"
          >
            {{ parentId ? 'Reply' : 'Post' }}
          </button>
        </div>
        
        <!-- Character Counter -->
        <div
          v-if="isFocused && inputValue.length > 200"
          class="absolute -bottom-6 right-0 text-xs transition-colors duration-200"
          :class="{
            'text-neutral-gray': inputValue.length <= 280,
            'text-orange-500': inputValue.length > 280 && inputValue.length <= 300,
            'text-red-500': inputValue.length > 300
          }"
        >
          {{ inputValue.length }}/300
        </div>
      </div>
    </div>
    
    <!-- Pregnancy Context Suggestions -->
    <div
      v-if="pregnancyContext && showSuggestions && !inputValue.trim()"
      class="mt-3 ml-11"
    >
      <div class="text-xs text-neutral-gray mb-2 font-medium">Quick responses:</div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="suggestion in getPregnancySuggestions()"
          :key="suggestion"
          @click="applySuggestion(suggestion)"
          class="px-3 py-1 bg-warm-gray hover:bg-blush-rose/20 text-xs text-warm-graphite rounded-full transition-all duration-200 hover:scale-105"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
    
    <!-- Emoji Picker (Simple) -->
    <div
      v-if="showEmojiPicker"
      ref="emojiPickerRef"
      class="absolute bottom-full right-0 mb-2 bg-white border border-light-gray rounded-lg shadow-lg z-50 p-3"
    >
      <div class="grid grid-cols-6 gap-2">
        <button
          v-for="emoji in pregnancyEmojis"
          :key="emoji"
          @click="insertEmoji(emoji)"
          class="w-8 h-8 text-lg hover:bg-warm-gray rounded transition-colors flex items-center justify-center"
        >
          {{ emoji }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useWebSocket } from '~/composables/useWebSocket'
import UserAvatar from '~/components/ui/UserAvatar.vue'
import type { components } from '~/types/api'

type PregnancyContext = components['schemas']['PregnancyContextResponse']

interface MentionOption {
  id: string
  name: string
  avatar?: string
  relationship?: string
}

interface Props {
  postId: string
  parentId?: string
  pregnancyContext?: PregnancyContext
  placeholder?: string
  mentionOptions?: MentionOption[]
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Add a comment...',
  mentionOptions: () => [],
  maxLength: 300
})

const emit = defineEmits<{
  submit: [{ content: string, parentId?: string, mentions?: string[] }]
  cancel: []
  mention: [query: string]
  typing: [isTyping: boolean]
}>()

// Composables
const auth = useAuth()
// const websocket = useWebSocket({
//   pregnancyOptimizations: true
// })

// State
const inputValue = ref('')
const isFocused = ref(false)
const showMentions = ref(false)
const showSuggestions = ref(false)
const showEmojiPicker = ref(false)
const selectedMentionIndex = ref(0)
const mentionQuery = ref('')
const mentions = ref<string[]>([])
const isTyping = ref(false)
const typingTimeout = ref<number>()

// Refs
const textareaRef = ref<HTMLTextAreaElement>()
const inputContainerRef = ref<HTMLElement>()
const mentionDropdownRef = ref<HTMLElement>()
const emojiPickerRef = ref<HTMLElement>()

// Pregnancy-specific emojis
const pregnancyEmojis = [
  '❤️', '😍', '🥰', '😊', '🤗', '💕',
  '👶', '🤰', '🤱', '👪', '✨', '🌟',
  '🎉', '🎊', '👏', '💪', '🙏', '💝'
]

// Computed
const canSubmit = computed(() => {
  return inputValue.value.trim().length > 0 && inputValue.value.length <= props.maxLength
})

const showActions = computed(() => {
  return isFocused.value || inputValue.value.trim().length > 0
})

// Methods
function handleInput() {
  // Auto-resize textarea
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
  
  // Handle mentions
  const mentionMatch = inputValue.value.match(/@(\w*)$/)
  if (mentionMatch) {
    mentionQuery.value = mentionMatch[1]
    showMentions.value = true
    emit('mention', mentionQuery.value)
  } else {
    showMentions.value = false
  }
  
  // Handle typing indicator
  handleTypingState(true)
}

function handleKeydown(event: KeyboardEvent) {
  // Submit on Ctrl+Enter or Cmd+Enter
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    if (canSubmit.value) {
      handleSubmit()
    }
    return
  }
  
  // Handle mention dropdown navigation
  if (showMentions.value && props.mentionOptions.length > 0) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      selectedMentionIndex.value = Math.min(
        selectedMentionIndex.value + 1,
        props.mentionOptions.length - 1
      )
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      selectedMentionIndex.value = Math.max(selectedMentionIndex.value - 1, 0)
    } else if (event.key === 'Enter' || event.key === 'Tab') {
      event.preventDefault()
      selectMention(props.mentionOptions[selectedMentionIndex.value])
    } else if (event.key === 'Escape') {
      showMentions.value = false
    }
  }
  
  // Regular Enter to submit (on mobile)
  if (event.key === 'Enter' && !event.shiftKey && window.innerWidth <= 640) {
    event.preventDefault()
    if (canSubmit.value) {
      handleSubmit()
    }
  }
}

function handleFocus() {
  isFocused.value = true
  showSuggestions.value = !inputValue.value.trim()
}

function handleBlur() {
  // Delay to allow for button clicks
  setTimeout(() => {
    isFocused.value = false
    showSuggestions.value = false
    showMentions.value = false
    showEmojiPicker.value = false
    handleTypingState(false)
  }, 150)
}

function handlePaste(event: ClipboardEvent) {
  // Handle pasted content (could add image support later)
  const pastedText = event.clipboardData?.getData('text') || ''
  
  // Check if pasting would exceed max length
  const newLength = inputValue.value.length + pastedText.length
  if (newLength > props.maxLength) {
    event.preventDefault()
    const allowedLength = props.maxLength - inputValue.value.length
    if (allowedLength > 0) {
      const truncated = pastedText.substring(0, allowedLength)
      inputValue.value += truncated
    }
  }
}

function handleTypingState(typing: boolean) {
  if (typing !== isTyping.value) {
    isTyping.value = typing
    emit('typing', typing)
    
    // Send typing indicator via WebSocket - disabled for now
    // websocket.send('typing', {
    //   postId: props.postId,
    //   userId: auth.userProfile.value?.id,
    //   userName: auth.userProfile.value?.display_name,
    //   isTyping: typing
    // })
  }
  
  // Clear typing state after delay
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
  
  if (typing) {
    typingTimeout.value = window.setTimeout(() => {
      handleTypingState(false)
    }, 3000)
  }
}

function selectMention(option: MentionOption) {
  const mentionMatch = inputValue.value.match(/@(\w*)$/)
  if (mentionMatch) {
    const beforeMention = inputValue.value.substring(0, mentionMatch.index)
    const afterMention = inputValue.value.substring(mentionMatch.index! + mentionMatch[0].length)
    inputValue.value = `${beforeMention}@${option.name} ${afterMention}`
    
    // Add to mentions list
    if (!mentions.value.includes(option.id)) {
      mentions.value.push(option.id)
    }
  }
  
  showMentions.value = false
  selectedMentionIndex.value = 0
  
  // Focus back on textarea
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

function applySuggestion(suggestion: string) {
  inputValue.value = suggestion
  showSuggestions.value = false
  textareaRef.value?.focus()
}

function insertEmoji(emoji: string) {
  const cursorPosition = textareaRef.value?.selectionStart || inputValue.value.length
  const before = inputValue.value.substring(0, cursorPosition)
  const after = inputValue.value.substring(cursorPosition)
  inputValue.value = `${before}${emoji}${after}`
  
  showEmojiPicker.value = false
  
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.focus()
      textareaRef.value.setSelectionRange(cursorPosition + emoji.length, cursorPosition + emoji.length)
    }
  })
}

function handleSubmit() {
  if (!canSubmit.value) return
  
  const content = inputValue.value.trim()
  
  emit('submit', {
    content,
    parentId: props.parentId,
    mentions: mentions.value.length > 0 ? mentions.value : undefined
  })
  
  // Reset form
  inputValue.value = ''
  mentions.value = []
  handleTypingState(false)
  
  // Reset textarea height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

function handleCancel() {
  inputValue.value = ''
  mentions.value = []
  handleTypingState(false)
  emit('cancel')
}

function getPregnancySuggestions(): string[] {
  if (!props.pregnancyContext) {
    return [
      'So beautiful! ❤️',
      'Congratulations! 🎉',
      'Love this! 😍',
      'Amazing! ✨'
    ]
  }
  
  if (props.pregnancyContext.is_milestone_week) {
    return [
      'Congratulations on this milestone! 🎉',
      'So exciting! Can\'t wait to meet baby! 👶',
      'You\'re glowing! ✨',
      'Such a beautiful journey ❤️'
    ]
  }
  
  return [
    'Thinking of you! 💕',
    'You\'re doing great! 💪',
    'Sending love! ❤️',
    'Beautiful update! 😊'
  ]
}

// Click outside handlers
function handleClickOutside(event: MouseEvent) {
  const target = event.target as Element
  
  if (showEmojiPicker.value && emojiPickerRef.value && !emojiPickerRef.value.contains(target)) {
    showEmojiPicker.value = false
  }
  
  if (showMentions.value && mentionDropdownRef.value && !mentionDropdownRef.value.contains(target)) {
    showMentions.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
  handleTypingState(false)
})

// Watch mention options
watch(() => props.mentionOptions, () => {
  selectedMentionIndex.value = 0
})
</script>

<style scoped>
/* Auto-growing textarea */
textarea {
  field-sizing: content;
  min-height: 2.5rem;
}

/* Custom scrollbar for mentions dropdown */
.max-h-48::-webkit-scrollbar {
  width: 6px;
}

.max-h-48::-webkit-scrollbar-track {
  background: theme(colors.warm-gray);
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb {
  background: theme(colors.neutral-gray);
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb:hover {
  background: theme(colors.warm-graphite);
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .comment-input textarea {
    font-size: 16px; /* Prevent zoom on iOS */
  }
  
  .grid-cols-6 {
    grid-template-columns: repeat(8, 1fr);
  }
}

/* Focus styles */
.comment-input button:focus-visible {
  outline: 2px solid theme(colors.blush-rose);
  outline-offset: 2px;
}

/* Animation for suggestions */
.comment-input button {
  transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.comment-input button:hover {
  transform: translateY(-1px);
}
</style>