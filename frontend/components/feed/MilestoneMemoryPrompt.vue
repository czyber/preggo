<template>
  <div
    ref="memoryPromptRef"
    :class="cn(
      'milestone-memory-prompt relative overflow-hidden',
      'bg-gradient-to-br from-muted-lavender/8 via-soft-pink/6 to-gentle-mint/4',
      'border border-muted-lavender/20 rounded-2xl p-4 shadow-sm',
      'transition-all duration-500 hover:shadow-md hover:border-muted-lavender/30',
      isActive && 'memory-active',
      className
    )"
  >
    <!-- Gentle memory book animation background -->
    <div v-if="showAnimation" class="absolute inset-0 pointer-events-none">
      <!-- Floating book pages -->
      <div
        v-for="i in 4"
        :key="`page-${i}`"
        :class="cn(
          'absolute w-3 h-4 bg-white rounded-sm opacity-30 shadow-sm',
          `page-float-${i}`
        )"
        :style="getPageStyle(i)"
      />
      
      <!-- Sparkle memories -->
      <div
        v-for="i in 3"
        :key="`memory-sparkle-${i}`"
        :class="cn(
          'absolute w-1.5 h-1.5 bg-muted-lavender rounded-full opacity-50',
          `memory-sparkle-${i}`
        )"
        :style="getSparkleStyle(i)"
      />
    </div>

    <!-- Header with memory book icon -->
    <div class="relative z-10 mb-4">
      <div class="flex items-start justify-between">
        <div class="flex items-start gap-3">
          <div class="memory-icon-container flex-shrink-0">
            <div class="memory-icon relative text-2xl">
              📖
              <div v-if="isActive" class="absolute -top-1 -right-1 text-xs animate-pulse">✨</div>
            </div>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-gray-800 text-base mb-1">
              {{ promptTitle }}
            </h3>
            <p class="text-sm text-gray-600 leading-relaxed">
              {{ promptMessage }}
            </p>
            <div v-if="milestoneInfo" class="mt-2 text-xs text-muted-lavender-dark font-medium">
              {{ milestoneInfo.type }} • Week {{ milestoneInfo.week }} • {{ formatDate(milestoneInfo.date) }}
            </div>
          </div>
        </div>
        
        <button
          v-if="dismissible && !isDismissed"
          @click="handleDismiss"
          class="flex-shrink-0 p-1 hover:bg-gray-100 rounded-full transition-colors opacity-60 hover:opacity-80"
          aria-label="Dismiss memory prompt"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Memory preview card -->
    <div v-if="showPreview && memoryPreview" class="memory-preview mb-4">
      <div class="bg-white/60 backdrop-blur-sm rounded-xl p-3 border border-white/60 shadow-sm">
        <div class="flex items-start gap-3">
          <!-- Preview thumbnail -->
          <div class="preview-thumbnail flex-shrink-0">
            <div v-if="memoryPreview.image" class="w-16 h-16 rounded-lg overflow-hidden bg-gray-100">
              <img 
                :src="memoryPreview.image" 
                :alt="memoryPreview.title"
                class="w-full h-full object-cover"
              />
            </div>
            <div v-else class="w-16 h-16 rounded-lg bg-gradient-to-br from-muted-lavender/20 to-soft-pink/20 flex items-center justify-center">
              <span class="text-2xl">{{ memoryPreview.icon || '📸' }}</span>
            </div>
          </div>
          
          <!-- Preview content -->
          <div class="flex-1 min-w-0">
            <h4 class="font-medium text-gray-800 text-sm mb-1 truncate">
              {{ memoryPreview.title }}
            </h4>
            <p class="text-xs text-gray-600 line-clamp-2 mb-2">
              {{ memoryPreview.description }}
            </p>
            <div class="flex items-center gap-2 text-xs text-gray-500">
              <span>{{ memoryPreview.category }}</span>
              <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
              <span>{{ formatTimeAgo(memoryPreview.date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Memory categories/tags -->
    <div v-if="suggestedTags.length > 0" class="memory-tags mb-4">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-medium text-gray-600">Memory tags:</span>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="tag in suggestedTags"
          :key="tag.name"
          @click="handleTagSelect(tag)"
          :class="cn(
            'memory-tag px-2.5 py-1 rounded-full text-xs font-medium transition-all duration-200',
            tag.selected 
              ? 'bg-gradient-to-r from-muted-lavender to-soft-pink text-white shadow-sm'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:scale-105'
          )"
        >
          <span class="mr-1">{{ tag.icon }}</span>
          {{ tag.name }}
        </button>
      </div>
    </div>

    <!-- Memory actions -->
    <div class="memory-actions flex flex-wrap gap-2">
      <!-- Save to memory book -->
      <button
        @click="handleSaveMemory"
        :disabled="isProcessing"
        class="save-memory-btn flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-muted-lavender to-soft-pink text-white font-semibold text-sm rounded-xl hover:shadow-md transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
      >
        <span class="text-base">📚</span>
        <span>{{ saveButtonText }}</span>
        <div
          v-if="isProcessing"
          class="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin"
        />
      </button>

      <!-- Add personal note -->
      <button
        @click="handleAddNote"
        class="add-note-btn flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white text-gray-700 font-medium text-sm rounded-xl border border-gray-200 hover:border-muted-lavender/30 transition-all duration-200 hover:scale-105"
      >
        <span class="text-base">✏️</span>
        <span>Add Note</span>
      </button>

      <!-- Share memory -->
      <button
        v-if="enableSharing"
        @click="handleShareMemory"
        class="share-memory-btn flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 text-gray-600 font-medium text-sm rounded-xl transition-all duration-200 hover:scale-105"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
        <span>Share</span>
      </button>
    </div>

    <!-- Memory book stats -->
    <div v-if="showStats && memoryStats" class="memory-stats mt-4 pt-3 border-t border-gray-200/60">
      <div class="flex items-center justify-between text-xs text-gray-600">
        <div class="flex items-center gap-2">
          <span>📖 {{ memoryStats.totalMemories }} memories saved</span>
          <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
          <span>Week {{ memoryStats.currentWeek }}</span>
        </div>
        <button
          @click="handleViewMemoryBook"
          class="text-muted-lavender-dark hover:text-muted-lavender font-medium"
        >
          View Memory Book →
        </button>
      </div>
    </div>

    <!-- Success animation overlay -->
    <div
      v-if="showSuccessAnimation"
      class="absolute inset-0 flex items-center justify-center pointer-events-none z-20"
    >
      <div class="success-animation bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/60 text-center">
        <div class="text-3xl mb-2 animate-bounce">📚✨</div>
        <p class="text-sm font-semibold text-gray-800 mb-1">Memory Saved!</p>
        <p class="text-xs text-gray-600">Added to your pregnancy memory book</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cn } from '~/components/ui/utils'

interface MemoryTag {
  name: string
  icon: string
  selected: boolean
}

interface MemoryPreview {
  title: string
  description: string
  category: string
  date: Date
  image?: string
  icon?: string
}

interface MilestoneInfo {
  type: string
  week: number
  date: Date
}

interface MemoryStats {
  totalMemories: number
  currentWeek: number
  weeklyMemories: number
}

interface Props {
  postId?: string
  milestoneInfo?: MilestoneInfo
  memoryPreview?: MemoryPreview
  memoryStats?: MemoryStats
  promptTitle?: string
  promptMessage?: string
  saveButtonText?: string
  suggestedTags?: MemoryTag[]
  enableSharing?: boolean
  showPreview?: boolean
  showStats?: boolean
  showAnimation?: boolean
  dismissible?: boolean
  isActive?: boolean
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  promptTitle: 'Save This Special Moment',
  promptMessage: 'This milestone would make a beautiful addition to your pregnancy memory book. Capture this moment to treasure forever.',
  saveButtonText: 'Save to Memory Book',
  suggestedTags: () => [
    { name: 'Milestone', icon: '⭐', selected: true },
    { name: 'Growth', icon: '📈', selected: false },
    { name: 'Special', icon: '💫', selected: false },
    { name: 'Family', icon: '👨‍👩‍👧‍👦', selected: false }
  ],
  enableSharing: true,
  showPreview: true,
  showStats: true,
  showAnimation: true,
  dismissible: true,
  isActive: false
})

const emit = defineEmits<{
  saveMemory: [data: { postId?: string; tags: string[]; note?: string }]
  addNote: [data: { postId?: string }]
  shareMemory: [data: { postId?: string }]
  tagSelect: [tag: MemoryTag]
  viewMemoryBook: []
  dismiss: []
  memorySaved: []
}>()

const memoryPromptRef = ref<HTMLElement>()
const isProcessing = ref(false)
const isDismissed = ref(false)
const showSuccessAnimation = ref(false)
const successTimeout = ref<NodeJS.Timeout>()

// Computed properties
const selectedTags = computed(() => {
  return props.suggestedTags.filter(tag => tag.selected)
})

// Methods
const getPageStyle = (index: number) => {
  const positions = [
    { top: '15%', left: '20%', transform: 'rotate(-5deg)' },
    { top: '25%', right: '25%', transform: 'rotate(3deg)' },
    { top: '70%', left: '15%', transform: 'rotate(-2deg)' },
    { top: '60%', right: '20%', transform: 'rotate(4deg)' }
  ]
  
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.8}s`
  
  return {
    ...position,
    animationDelay
  }
}

const getSparkleStyle = (index: number) => {
  const positions = [
    { top: '30%', left: '60%' },
    { top: '80%', right: '40%' },
    { top: '50%', left: '30%' }
  ]
  
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 1.2}s`
  
  return {
    ...position,
    animationDelay
  }
}

const handleSaveMemory = async () => {
  if (isProcessing.value) return
  
  isProcessing.value = true
  
  try {
    const selectedTagNames = selectedTags.value.map(tag => tag.name)
    
    emit('saveMemory', {
      postId: props.postId,
      tags: selectedTagNames
    })
    
    // Show success animation
    showSuccessAnimation.value = true
    
    // Add haptic feedback if available
    if ('vibrate' in navigator) {
      navigator.vibrate([50, 30, 50])
    }
    
    // Auto-hide success animation
    successTimeout.value = setTimeout(() => {
      showSuccessAnimation.value = false
      emit('memorySaved')
    }, 2500)
    
  } catch (error) {
    console.error('Failed to save memory:', error)
  } finally {
    setTimeout(() => {
      isProcessing.value = false
    }, 1000)
  }
}

const handleAddNote = () => {
  emit('addNote', {
    postId: props.postId
  })
}

const handleShareMemory = () => {
  emit('shareMemory', {
    postId: props.postId
  })
}

const handleTagSelect = (tag: MemoryTag) => {
  tag.selected = !tag.selected
  emit('tagSelect', tag)
}

const handleViewMemoryBook = () => {
  emit('viewMemoryBook')
}

const handleDismiss = () => {
  isDismissed.value = true
  emit('dismiss')
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTimeAgo = (date: Date): string => {
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

// Lifecycle
onMounted(() => {
  // Auto-show animation if active
  if (props.isActive && props.showAnimation) {
    // Slight delay for smoother entrance
    setTimeout(() => {
      // Animation is handled by CSS
    }, 200)
  }
})

onUnmounted(() => {
  if (successTimeout.value) {
    clearTimeout(successTimeout.value)
  }
})
</script>

<style scoped>
/* Main memory prompt styling */
.milestone-memory-prompt {
  backdrop-filter: blur(8px);
}

.memory-active {
  animation: memory-gentle-glow 4s ease-in-out infinite;
}

@keyframes memory-gentle-glow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(225, 190, 231, 0.2);
  }
  50% {
    box-shadow: 0 0 25px rgba(225, 190, 231, 0.4), 0 0 35px rgba(248, 187, 208, 0.2);
  }
}

/* Memory icon animation */
.memory-icon {
  animation: memory-icon-gentle-bounce 3s ease-in-out infinite;
}

@keyframes memory-icon-gentle-bounce {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  25% {
    transform: scale(1.05) rotate(-2deg);
  }
  75% {
    transform: scale(1.02) rotate(1deg);
  }
}

/* Floating pages animation */
.page-float-1 { animation: page-float 6s ease-in-out infinite; }
.page-float-2 { animation: page-float 6.5s ease-in-out infinite; }
.page-float-3 { animation: page-float 5.5s ease-in-out infinite; }
.page-float-4 { animation: page-float 6.2s ease-in-out infinite; }

@keyframes page-float {
  0%, 100% {
    opacity: 0.3;
    transform: translateY(0) rotate(var(--rotation, 0deg));
  }
  50% {
    opacity: 0.6;
    transform: translateY(-10px) rotate(var(--rotation, 0deg));
  }
}

/* Memory sparkles */
.memory-sparkle-1 { animation: memory-sparkle-twinkle 3s ease-in-out infinite; }
.memory-sparkle-2 { animation: memory-sparkle-twinkle 3.5s ease-in-out infinite; }
.memory-sparkle-3 { animation: memory-sparkle-twinkle 2.8s ease-in-out infinite; }

@keyframes memory-sparkle-twinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.4);
  }
}

/* Memory preview styling */
.memory-preview {
  animation: preview-slide-in 0.5s ease-out;
}

@keyframes preview-slide-in {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Memory tags */
.memory-tag {
  animation: tag-appear 0.3s ease-out;
}

.memory-tag:nth-child(odd) {
  animation-delay: 0.1s;
}

.memory-tag:nth-child(even) {
  animation-delay: 0.2s;
}

@keyframes tag-appear {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Action buttons */
.save-memory-btn,
.add-note-btn,
.share-memory-btn {
  position: relative;
  overflow: hidden;
}

.save-memory-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.save-memory-btn:hover::before {
  transform: translateX(100%);
}

/* Success animation */
.success-animation {
  animation: success-appear 0.4s ease-out;
}

@keyframes success-appear {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .milestone-memory-prompt {
    margin: 0 -0.5rem;
    padding: 0.75rem;
  }
  
  .memory-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .save-memory-btn,
  .add-note-btn,
  .share-memory-btn {
    width: 100%;
    justify-content: center;
  }
  
  .memory-preview {
    padding: 0.5rem;
  }
  
  .preview-thumbnail {
    width: 3rem;
    height: 3rem;
  }
  
  .memory-tag {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
}

/* Accessibility */
.save-memory-btn:focus,
.add-note-btn:focus,
.share-memory-btn:focus,
.memory-tag:focus {
  outline: 2px solid #E1BEE7;
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .memory-active,
  .memory-icon,
  .page-float-1, .page-float-2, .page-float-3, .page-float-4,
  .memory-sparkle-1, .memory-sparkle-2, .memory-sparkle-3,
  .preview-slide-in,
  .tag-appear,
  .success-animation {
    animation: none;
  }
  
  .save-memory-btn::before {
    transition: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .save-memory-btn,
  .add-note-btn,
  .memory-tag {
    border: 2px solid currentColor;
  }
}
</style>
