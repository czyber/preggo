<template>
  <div class="reaction-picker relative">
    <!-- Reaction Button -->
    <button
      ref="triggerRef"
      @click="togglePicker"
      :class="cn(
        'reaction-trigger flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200',
        hasUserReaction 
          ? 'bg-soft-pink/20 text-soft-pink border border-soft-pink/30 hover:bg-soft-pink/30' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200',
        isOpen && 'scale-105 shadow-sm'
      )"
      :aria-expanded="isOpen"
      :aria-label="hasUserReaction ? `Remove ${userReaction} reaction` : 'Add reaction'"
    >
      <span v-if="hasUserReaction" class="text-base">
        {{ getReactionEmoji(userReaction) }}
      </span>
      <span v-else class="text-base">❤️</span>
      
      <span>{{ hasUserReaction ? 'Reacted' : 'React' }}</span>
      
      <span v-if="totalCount > 0" class="text-xs bg-white/50 px-1.5 py-0.5 rounded-full">
        {{ totalCount }}
      </span>
    </button>

    <!-- Reaction Picker Dropdown -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="pickerRef"
        :style="pickerStyle"
        class="reaction-picker-dropdown fixed z-50 bg-white rounded-2xl shadow-xl border border-gray-100 p-4 min-w-80"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800 font-primary">Choose your reaction</h3>
          <button
            @click="closePicker"
            class="p-1 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close reactions"
          >
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Reaction Grid -->
        <div class="grid grid-cols-3 gap-3 mb-4">
          <button
            v-for="reaction in pregnancyReactions"
            :key="reaction.type"
            ref="reactionOptionRefs"
            @click="selectReaction(reaction.type)"
            @mouseenter="handleReactionHover(reaction.type, true, $event)"
            @mouseleave="handleReactionHover(reaction.type, false, $event)"
            :class="cn(
              'reaction-option p-3 rounded-xl text-center transition-all duration-200 hover:scale-105',
              userReaction === reaction.type
                ? 'bg-soft-pink/20 border-2 border-soft-pink/50 shadow-sm'
                : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
            )"
            :aria-label="`React with ${reaction.label}`"
          >
            <div class="text-2xl mb-1">{{ reaction.emoji }}</div>
            <div class="text-xs font-medium text-gray-700">{{ reaction.label }}</div>
          </button>
        </div>

        <!-- Current Reactions Summary -->
        <div v-if="reactionCounts && Object.keys(reactionCounts).length > 0" class="border-t border-gray-100 pt-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-700">Reactions ({{ totalCount }})</span>
            <button
              @click="handleViewAll"
              class="text-xs text-soft-pink hover:text-soft-pink/80 font-medium"
            >
              View all
            </button>
          </div>
          
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(count, reactionType) in reactionCounts"
              :key="reactionType"
              v-show="count > 0"
              class="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded-full text-xs"
            >
              <span>{{ getReactionEmoji(reactionType as string) }}</span>
              <span class="font-medium">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Family Context -->
        <div v-if="showFamilyContext && recentReactors.length > 0" class="border-t border-gray-100 pt-4 mt-4">
          <div class="text-xs text-gray-600 mb-2">Recent reactions from family:</div>
          <div class="flex items-center gap-2">
            <div
              v-for="reactor in recentReactors.slice(0, 3)"
              :key="reactor"
              class="w-6 h-6 bg-gentle-mint/20 rounded-full flex items-center justify-center text-xs"
            >
              {{ reactor.charAt(0).toUpperCase() }}
            </div>
            <span v-if="recentReactors.length > 3" class="text-xs text-gray-500">
              +{{ recentReactors.length - 3 }} more
            </span>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Backdrop -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-black/10 backdrop-blur-sm"
      @click="closePicker"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { cn } from '~/utils/cn'
import { useReactionAnimation, useGentleTransitions, useCelebrationAnimation } from '~/composables/useAnimations'

interface Props {
  userReaction?: string
  reactionCounts?: Record<string, number>
  totalCount?: number
  recentReactors?: string[]
  showFamilyContext?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  totalCount: 0,
  recentReactors: () => [],
  showFamilyContext: true,
  disabled: false
})

const emit = defineEmits<{
  reaction: [{ reactionType: string }]
  removeReaction: []
  viewAll: []
}>()

// Pregnancy-specific reactions with supportive context
const pregnancyReactions = [
  { type: 'love', emoji: '❤️', label: 'Love', description: 'Show love and support' },
  { type: 'excited', emoji: '😍', label: 'Excited', description: 'Share in the excitement' },
  { type: 'care', emoji: '🤗', label: 'Care', description: 'Send caring thoughts' },
  { type: 'support', emoji: '💪', label: 'Support', description: 'Offer strength and encouragement' },
  { type: 'beautiful', emoji: '✨', label: 'Beautiful', description: 'Celebrate beautiful moments' },
  { type: 'funny', emoji: '😂', label: 'Funny', description: 'Share in the laughter' },
  { type: 'praying', emoji: '🙏', label: 'Praying', description: 'Sending prayers and wishes' },
  { type: 'proud', emoji: '🏆', label: 'Proud', description: 'Express pride and admiration' },
  { type: 'grateful', emoji: '🙏✨', label: 'Grateful', description: 'Show gratitude and thankfulness' }
]

// Animation composables
const { animateReactionButton, animateReactionCounter, animateReactionPicker, animateReactionOption } = useReactionAnimation()
const { createGentleHover, animateElementIn } = useGentleTransitions()
const { celebrateReaction } = useCelebrationAnimation()

// Local state
const isOpen = ref(false)
const triggerRef = ref<HTMLElement>()
const pickerRef = ref<HTMLElement>()
const pickerStyle = ref<Record<string, string>>({})

// Computed
const hasUserReaction = computed(() => !!props.userReaction)

// Methods
function getReactionEmoji(reactionType: string) {
  const reaction = pregnancyReactions.find(r => r.type === reactionType)
  return reaction?.emoji || '❤️'
}

function togglePicker() {
  if (props.disabled) return
  
  if (isOpen.value) {
    closePicker()
  } else {
    openPicker()
  }
}

async function openPicker() {
  isOpen.value = true
  await nextTick()
  positionPicker()
  
  // Animate picker entrance
  if (pickerRef.value) {
    animateReactionPicker(pickerRef.value, true)
  }
}

function closePicker() {
  isOpen.value = false
}

function selectReaction(reactionType: string) {
  if (props.userReaction === reactionType) {
    // Remove current reaction
    emit('removeReaction')
  } else {
    // Add/change reaction
    emit('reaction', { reactionType })
    
    // Celebrate the reaction selection
    if (triggerRef.value) {
      celebrateReaction(triggerRef.value, reactionType)
    }
  }
  
  closePicker()
}

function handleViewAll() {
  emit('viewAll')
  closePicker()
}

function handleReactionHover(reactionType: string, isHovering: boolean, event: Event) {
  const element = event.target as HTMLElement
  if (element) {
    animateReactionOption(element, isHovering)
  }
}

function positionPicker() {
  if (!triggerRef.value || !pickerRef.value) return

  const trigger = triggerRef.value.getBoundingClientRect()
  const picker = pickerRef.value
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }

  // Default position: center above trigger
  let top = trigger.top - picker.offsetHeight - 8
  let left = trigger.left + (trigger.width / 2) - (picker.offsetWidth / 2)

  // Adjust for viewport bounds
  if (left < 8) {
    left = 8
  } else if (left + picker.offsetWidth > viewport.width - 8) {
    left = viewport.width - picker.offsetWidth - 8
  }

  // If not enough space above, position below
  if (top < 8) {
    top = trigger.bottom + 8
  }

  // Final bounds check
  if (top + picker.offsetHeight > viewport.height - 8) {
    top = viewport.height - picker.offsetHeight - 8
  }

  pickerStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

// Event handlers
function handleClickOutside(event: Event) {
  if (
    isOpen.value &&
    triggerRef.value &&
    pickerRef.value &&
    !triggerRef.value.contains(event.target as Node) &&
    !pickerRef.value.contains(event.target as Node)
  ) {
    closePicker()
  }
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && isOpen.value) {
    closePicker()
  }
}

function handleResize() {
  if (isOpen.value) {
    positionPicker()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscape)
  window.addEventListener('resize', handleResize)
  
  // Set up gentle hover effects on trigger button
  if (triggerRef.value) {
    createGentleHover(triggerRef.value, 'lift')
    animateReactionButton(triggerRef.value, hasUserReaction.value)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscape)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Reaction picker animations */
.reaction-picker-dropdown {
  animation: picker-appear 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top center;
}

@keyframes picker-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Reaction option hover effects */
.reaction-option {
  position: relative;
  overflow: hidden;
}

.reaction-option::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(248, 187, 208, 0.1), transparent);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.reaction-option:hover::before {
  transform: translateX(100%);
}

/* Reaction trigger animations */
.reaction-trigger {
  position: relative;
  overflow: hidden;
}

.reaction-trigger:active {
  transform: scale(0.98);
}

/* Special pregnancy-themed styling */
.reaction-option[data-reaction="love"] {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.1) 0%, rgba(255, 205, 210, 0.1) 100%);
}

.reaction-option[data-reaction="excited"] {
  background: linear-gradient(135deg, rgba(225, 190, 231, 0.1) 0%, rgba(248, 187, 208, 0.1) 100%);
}

.reaction-option[data-reaction="care"] {
  background: linear-gradient(135deg, rgba(178, 223, 219, 0.1) 0%, rgba(187, 222, 251, 0.1) 100%);
}

.reaction-option[data-reaction="support"] {
  background: linear-gradient(135deg, rgba(178, 223, 219, 0.15) 0%, rgba(248, 187, 208, 0.1) 100%);
}

/* Enhanced accessibility */
.reaction-option:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

.reaction-trigger:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .reaction-picker-dropdown {
    left: 1rem !important;
    right: 1rem !important;
    max-width: calc(100vw - 2rem);
    min-width: unset;
  }
  
  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  
  .reaction-option {
    padding: 0.75rem;
  }
}

/* Smooth transitions for all interactive elements */
.reaction-option,
.reaction-trigger {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Backdrop animation */
.backdrop-enter-active,
.backdrop-leave-active {
  transition: all 0.2s ease;
}

.backdrop-enter-from,
.backdrop-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
</style>