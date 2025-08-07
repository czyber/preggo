<template>
  <div class="reaction-tooltip-wrapper relative inline-block">
    <!-- Trigger Element -->
    <div
      ref="triggerRef"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      @focus="showTooltip"
      @blur="hideTooltip"
      class="cursor-pointer"
    >
      <slot />
    </div>

    <!-- Tooltip Portal -->
    <Teleport to="body">
      <div
        v-if="isVisible"
        ref="tooltipRef"
        :style="tooltipStyle"
        class="reaction-tooltip-content fixed z-50 max-w-sm"
        role="tooltip"
        :aria-describedby="tooltipId"
      >
        <!-- Tooltip Card -->
        <div class="tooltip-card bg-white rounded-xl shadow-xl border border-gray-100/80 p-4 backdrop-blur-sm">
          <!-- Header with Reaction Info -->
          <div class="flex items-center gap-3 mb-3">
            <div class="reaction-icon text-2xl">
              {{ reactionEmoji }}
            </div>
            <div>
              <h3 class="font-bold text-gray-900 text-sm">{{ reactionLabel }}</h3>
              <p class="text-xs text-gray-600">{{ getReactionDescription() }}</p>
            </div>
          </div>

          <!-- Family Members Who Reacted -->
          <div v-if="familyReactors.length > 0" class="family-reactors">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-sm font-medium text-gray-700">Family celebrating:</span>
              <span class="text-xs bg-soft-pink/20 px-2 py-1 rounded-full text-pink-700">
                {{ familyReactors.length }} {{ familyReactors.length === 1 ? 'person' : 'people' }}
              </span>
            </div>

            <!-- Family Member List -->
            <div class="space-y-2 max-h-32 overflow-y-auto">
              <div
                v-for="reactor in displayedReactors"
                :key="reactor.id"
                class="flex items-center gap-3 p-2 bg-gray-50/60 rounded-lg"
              >
                <!-- Avatar -->
                <div class="avatar-container">
                  <img
                    v-if="reactor.avatar_url"
                    :src="reactor.avatar_url"
                    :alt="`${reactor.name}'s avatar`"
                    class="w-8 h-8 rounded-full object-cover border-2 border-white shadow-sm"
                  />
                  <div
                    v-else
                    class="w-8 h-8 rounded-full bg-gradient-to-br from-gentle-mint/40 to-soft-pink/30 flex items-center justify-center text-sm font-semibold text-gray-700 border-2 border-white shadow-sm"
                  >
                    {{ reactor.name.charAt(0).toUpperCase() }}
                  </div>
                </div>

                <!-- Reactor Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900 text-sm truncate">
                      {{ reactor.name }}
                    </span>
                    <span
                      v-if="reactor.relationship"
                      class="relationship-badge text-xs px-2 py-0.5 rounded-full"
                      :class="getRelationshipBadgeClass(reactor.relationship)"
                    >
                      {{ getRelationshipLabel(reactor.relationship) }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 mt-1">
                    <span class="text-xs text-gray-500">
                      {{ getWarmMessage(reactor.relationship) }}
                    </span>
                    <span class="text-xs text-gray-400">
                      {{ getRelativeTime(reactor.reacted_at) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Show More Button -->
            <button
              v-if="familyReactors.length > maxDisplay"
              @click="toggleShowAll"
              class="w-full mt-3 text-xs text-soft-pink hover:text-soft-pink/80 font-medium py-2 px-3 rounded-lg hover:bg-soft-pink/10 transition-colors"
            >
              {{ showAll ? 'Show less' : `Show ${familyReactors.length - maxDisplay} more` }}
            </button>
          </div>

          <!-- Special Family Context -->
          <div v-if="hasSpecialFamilyContext" class="special-context mt-3 pt-3 border-t border-gray-100">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-lg">{{ getSpecialContextEmoji() }}</span>
              <span class="text-xs font-medium text-gray-700">Special family moment</span>
            </div>
            <p class="text-xs text-gray-600 leading-relaxed">
              {{ getSpecialContextMessage() }}
            </p>
          </div>

          <!-- Tooltip Arrow -->
          <div class="tooltip-arrow" :class="arrowPosition"></div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useGentleTransitions } from '~/composables/useAnimations'

interface FamilyReactor {
  id: string
  name: string
  relationship?: string
  avatar_url?: string
  reacted_at: string
}

interface Props {
  reactionType: string
  reactionEmoji: string
  reactionLabel: string
  familyReactors: FamilyReactor[]
  maxDisplay?: number
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxDisplay: 4,
  delay: 300
})

// Animation composables
const { animateElementIn } = useGentleTransitions()

// Local state
const isVisible = ref(false)
const showAll = ref(false)
const triggerRef = ref<HTMLElement>()
const tooltipRef = ref<HTMLElement>()
const tooltipStyle = ref<Record<string, string>>({})
const arrowPosition = ref<string>('bottom')
const tooltipId = ref(`tooltip-${Math.random().toString(36).substr(2, 9)}`)

let showTimeout: NodeJS.Timeout | null = null
let hideTimeout: NodeJS.Timeout | null = null

// Relationship display configuration
const relationshipLabels: Record<string, string> = {
  'partner': 'Partner',
  'mom': 'Mom',
  'dad': 'Dad',
  'grandma': 'Grandma',
  'grandpa': 'Grandpa',
  'sister': 'Sister',
  'brother': 'Brother',
  'best-friend': 'Best Friend',
  'friend': 'Friend',
  'aunt': 'Aunt',
  'uncle': 'Uncle',
  'cousin': 'Cousin',
  'mother-in-law': 'Mother-in-law',
  'father-in-law': 'Father-in-law'
}

// Warm reaction messages by relationship
const warmMessages: Record<string, string> = {
  'partner': 'Your partner is celebrating with you',
  'mom': 'Mom is so proud and happy',
  'dad': 'Dad is beaming with joy',
  'grandma': 'Grandma sends all her love',
  'grandpa': 'Grandpa is so excited',
  'sister': 'Your sister is cheering you on',
  'brother': 'Your brother supports you',
  'best-friend': 'Your bestie is here for you',
  'friend': 'Sending friendship and support',
  'default': 'Celebrating this moment with you'
}

// Computed properties
const displayedReactors = computed(() => {
  return showAll.value 
    ? props.familyReactors 
    : props.familyReactors.slice(0, props.maxDisplay)
})

const hasSpecialFamilyContext = computed(() => {
  const specialRoles = ['partner', 'mom', 'dad', 'grandma', 'grandpa']
  return props.familyReactors.some(reactor => 
    specialRoles.includes(reactor.relationship || '')
  )
})

// Methods
function getReactionDescription() {
  const descriptions: Record<string, string> = {
    love: 'Sending warm love and support',
    excited: 'Sharing in your excitement',
    care: 'Wrapping you in caring thoughts',
    support: 'Standing strong beside you',
    beautiful: 'Finding beauty in this moment',
    funny: 'Sharing smiles and joy',
    praying: 'Offering prayers and blessings',
    proud: 'Bursting with pride for you',
    grateful: 'Grateful to share this journey'
  }
  return descriptions[props.reactionType] || 'Reacting to your special moment'
}

function getRelationshipLabel(relationship?: string) {
  return relationshipLabels[relationship || ''] || 'Family'
}

function getRelationshipBadgeClass(relationship?: string) {
  const classes: Record<string, string> = {
    'partner': 'bg-red-100 text-red-700',
    'mom': 'bg-pink-100 text-pink-700',
    'dad': 'bg-blue-100 text-blue-700',
    'grandma': 'bg-purple-100 text-purple-700',
    'grandpa': 'bg-indigo-100 text-indigo-700',
    'sister': 'bg-green-100 text-green-700',
    'brother': 'bg-cyan-100 text-cyan-700',
    'best-friend': 'bg-yellow-100 text-yellow-700',
    'default': 'bg-gray-100 text-gray-700'
  }
  return classes[relationship || 'default']
}

function getWarmMessage(relationship?: string) {
  return warmMessages[relationship || 'default']
}

function getSpecialContextEmoji() {
  const specialReactors = props.familyReactors.filter(r => 
    ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(r.relationship || '')
  )
  
  if (specialReactors.some(r => r.relationship === 'partner')) return '💑'
  if (specialReactors.some(r => ['mom', 'dad'].includes(r.relationship || ''))) return '👨‍👩‍👧‍👦'
  if (specialReactors.some(r => ['grandma', 'grandpa'].includes(r.relationship || ''))) return '👵👴'
  return '💕'
}

function getSpecialContextMessage() {
  const specialReactors = props.familyReactors.filter(r => 
    ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(r.relationship || '')
  )
  
  if (specialReactors.length === 0) return ''
  
  const relationships = specialReactors.map(r => getRelationshipLabel(r.relationship))
  
  if (relationships.length === 1) {
    return `Your ${relationships[0]} shared a heartfelt reaction to celebrate this precious moment with you.`
  }
  
  return `Your closest family members are joining together to celebrate this special milestone in your journey.`
}

function getRelativeTime(timestamp: string) {
  const now = new Date()
  const reactedAt = new Date(timestamp)
  const diffInMinutes = Math.floor((now.getTime() - reactedAt.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
  return `${Math.floor(diffInMinutes / 1440)}d ago`
}

function toggleShowAll() {
  showAll.value = !showAll.value
}

function showTooltip() {
  if (hideTimeout) {
    clearTimeout(hideTimeout)
    hideTimeout = null
  }
  
  showTimeout = setTimeout(async () => {
    isVisible.value = true
    await nextTick()
    positionTooltip()
    
    if (tooltipRef.value) {
      animateElementIn(tooltipRef.value, 'fadeInScale', 'supportive')
    }
  }, props.delay)
}

function hideTooltip() {
  if (showTimeout) {
    clearTimeout(showTimeout)
    showTimeout = null
  }
  
  hideTimeout = setTimeout(() => {
    isVisible.value = false
    showAll.value = false
  }, 150)
}

function handleMouseEnter() {
  showTooltip()
}

function handleMouseLeave() {
  hideTooltip()
}

function positionTooltip() {
  if (!triggerRef.value || !tooltipRef.value) return

  const trigger = triggerRef.value.getBoundingClientRect()
  const tooltip = tooltipRef.value
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }

  // Default position: center above trigger
  let top = trigger.top - tooltip.offsetHeight - 12
  let left = trigger.left + (trigger.width / 2) - (tooltip.offsetWidth / 2)
  let arrow = 'bottom'

  // Adjust horizontal position if tooltip would overflow
  if (left < 8) {
    left = 8
  } else if (left + tooltip.offsetWidth > viewport.width - 8) {
    left = viewport.width - tooltip.offsetWidth - 8
  }

  // If not enough space above, position below
  if (top < 8) {
    top = trigger.bottom + 12
    arrow = 'top'
  }

  // Final bounds check
  if (top + tooltip.offsetHeight > viewport.height - 8) {
    top = viewport.height - tooltip.offsetHeight - 8
  }

  tooltipStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }
  
  arrowPosition.value = arrow
}

// Event listeners
function handleClickOutside(event: Event) {
  if (
    isVisible.value &&
    tooltipRef.value &&
    !tooltipRef.value.contains(event.target as Node) &&
    triggerRef.value &&
    !triggerRef.value.contains(event.target as Node)
  ) {
    hideTooltip()
  }
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && isVisible.value) {
    hideTooltip()
  }
}

function handleResize() {
  if (isVisible.value) {
    positionTooltip()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscape)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscape)
  window.removeEventListener('resize', handleResize)
  
  if (showTimeout) clearTimeout(showTimeout)
  if (hideTimeout) clearTimeout(hideTimeout)
})
</script>

<style scoped>
/* Tooltip card styling */
.tooltip-card {
  animation: tooltip-appear 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top center;
  min-width: 280px;
  max-width: 420px;
}

@keyframes tooltip-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Tooltip arrow */
.tooltip-arrow {
  position: absolute;
  width: 12px;
  height: 12px;
  background: white;
  border: 1px solid rgba(229, 231, 235, 0.8);
  transform: rotate(45deg);
}

.tooltip-arrow.bottom {
  bottom: -6px;
  left: 50%;
  margin-left: -6px;
  border-top: none;
  border-left: none;
}

.tooltip-arrow.top {
  top: -6px;
  left: 50%;
  margin-left: -6px;
  border-bottom: none;
  border-right: none;
}

/* Avatar container with hover effect */
.avatar-container {
  @apply transition-transform duration-200 hover:scale-110;
}

/* Relationship badge styling */
.relationship-badge {
  @apply font-medium;
}

/* Special context styling */
.special-context {
  @apply bg-gradient-to-r from-soft-pink/10 to-gentle-mint/10 -mx-4 -mb-4 px-4 pb-4 rounded-b-xl;
}

/* Scrollbar styling for reactor list */
.family-reactors .space-y-2::-webkit-scrollbar {
  width: 4px;
}

.family-reactors .space-y-2::-webkit-scrollbar-track {
  background: rgba(243, 244, 246, 0.5);
  border-radius: 2px;
}

.family-reactors .space-y-2::-webkit-scrollbar-thumb {
  background: rgba(248, 187, 208, 0.5);
  border-radius: 2px;
}

.family-reactors .space-y-2::-webkit-scrollbar-thumb:hover {
  background: rgba(248, 187, 208, 0.7);
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .tooltip-card {
    min-width: 260px;
    max-width: calc(100vw - 2rem);
  }
  
  .reaction-tooltip-content {
    left: 1rem !important;
    right: 1rem !important;
    max-width: calc(100vw - 2rem);
  }
}

/* Accessibility enhancements */
.reaction-tooltip-wrapper:focus-within .tooltip-card {
  @apply ring-2 ring-soft-pink ring-offset-2;
}

/* Animation for show/hide transitions */
.tooltip-card {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

/* Loading state for avatars */
.avatar-container img {
  @apply transition-opacity duration-200;
}

.avatar-container img[src=""] {
  @apply opacity-0;
}
</style>
