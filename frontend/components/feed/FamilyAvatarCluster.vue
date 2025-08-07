<template>
  <div 
    ref="clusterRef"
    class="family-avatar-cluster"
    @click="handleClusterClick"
    :class="{ 'is-interactive': isInteractive }"
  >
    <!-- Avatar Stack -->
    <div class="avatar-stack flex items-center" :style="stackStyle">
      <!-- Primary Avatars (Displayed) -->
      <div
        v-for="(reactor, index) in displayedReactors"
        :key="reactor.id"
        class="avatar-wrapper"
        :class="[
          'avatar-wrapper',
          `avatar-${index}`,
          { 'has-special-relationship': isSpecialRelationship(reactor.relationship) }
        ]"
        :style="getAvatarStyle(index)"
        @mouseenter="handleAvatarHover(reactor, true, $event)"
        @mouseleave="handleAvatarHover(reactor, false, $event)"
      >
        <!-- Avatar Image or Fallback -->
        <div class="avatar-container relative">
          <img
            v-if="reactor.avatar_url"
            :src="reactor.avatar_url"
            :alt="`${reactor.name}'s avatar`"
            class="avatar-image w-full h-full object-cover rounded-full"
            @error="handleImageError"
          />
          <div
            v-else
            class="avatar-fallback w-full h-full rounded-full flex items-center justify-center font-semibold"
            :class="getAvatarFallbackClass(reactor.relationship)"
          >
            {{ getAvatarInitial(reactor.name) }}
          </div>

          <!-- Relationship Indicator -->
          <div
            v-if="showRelationshipIndicators && reactor.relationship"
            class="relationship-indicator absolute -bottom-1 -right-1"
            :class="getRelationshipIndicatorClass(reactor.relationship)"
          >
            {{ getRelationshipEmoji(reactor.relationship) }}
          </div>

          <!-- Reaction Type Indicator -->
          <div
            v-if="showReactionIndicators"
            class="reaction-indicator absolute -top-1 -right-1 bg-white rounded-full shadow-sm border border-gray-200"
          >
            <span class="text-xs p-1 flex items-center justify-center">
              {{ getReactionEmoji(reactor.reaction_type) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Overflow Counter -->
      <div
        v-if="hasOverflow"
        class="overflow-counter avatar-wrapper"
        :style="getAvatarStyle(displayedReactors.length)"
      >
        <div class="avatar-container relative">
          <div class="overflow-avatar w-full h-full rounded-full bg-gradient-to-br from-soft-pink/60 to-gentle-mint/40 flex items-center justify-center font-bold text-white shadow-md border-2 border-white">
            <span class="text-xs">+{{ overflowCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cluster Summary (Optional) -->
    <div v-if="showSummary" class="cluster-summary ml-3">
      <p class="text-sm font-medium text-gray-800">
        {{ getSummaryText() }}
      </p>
      <p v-if="hasSpecialFamily" class="text-xs text-gray-600 mt-1">
        {{ getSpecialFamilyText() }}
      </p>
    </div>

    <!-- Interactive Tooltip -->
    <ReactionTooltip
      v-if="isInteractive && hoveredReactor"
      :reaction-type="hoveredReactor.reaction_type"
      :reaction-emoji="getReactionEmoji(hoveredReactor.reaction_type)"
      :reaction-label="getReactionLabel(hoveredReactor.reaction_type)"
      :family-reactors="[hoveredReactor]"
    >
      <div class="invisible absolute"></div>
    </ReactionTooltip>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGentleTransitions } from '~/composables/useAnimations'
import ReactionTooltip from './ReactionTooltip.vue'

interface FamilyReactor {
  id: string
  name: string
  relationship?: string
  avatar_url?: string
  reaction_type: string
  reacted_at: string
}

interface Props {
  reactors: FamilyReactor[]
  maxDisplay?: number
  size?: 'sm' | 'md' | 'lg'
  isInteractive?: boolean
  showRelationshipIndicators?: boolean
  showReactionIndicators?: boolean
  showSummary?: boolean
  stackSpacing?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxDisplay: 4,
  size: 'md',
  isInteractive: true,
  showRelationshipIndicators: true,
  showReactionIndicators: false,
  showSummary: false,
  stackSpacing: -8
})

const emit = defineEmits<{
  click: []
  avatarClick: [{ reactor: FamilyReactor }]
  avatarHover: [{ reactor: FamilyReactor, isHovering: boolean }]
}>()

// Animation composables
const { createGentleHover, pulseElement } = useGentleTransitions()

// Local state
const clusterRef = ref<HTMLElement>()
const hoveredReactor = ref<FamilyReactor | null>(null)

// Avatar size configuration
const sizeConfig = {
  sm: {
    width: 28,
    height: 28,
    borderWidth: 2,
    fontSize: 'text-xs'
  },
  md: {
    width: 36,
    height: 36,
    borderWidth: 2,
    fontSize: 'text-sm'
  },
  lg: {
    width: 44,
    height: 44,
    borderWidth: 3,
    fontSize: 'text-base'
  }
}

// Relationship configuration
const relationshipConfig = {
  partner: { emoji: '💑', color: 'text-red-600', bg: 'bg-red-100' },
  mom: { emoji: '👩', color: 'text-pink-600', bg: 'bg-pink-100' },
  dad: { emoji: '👨', color: 'text-blue-600', bg: 'bg-blue-100' },
  grandma: { emoji: '👵', color: 'text-purple-600', bg: 'bg-purple-100' },
  grandpa: { emoji: '👴', color: 'text-indigo-600', bg: 'bg-indigo-100' },
  sister: { emoji: '👭', color: 'text-green-600', bg: 'bg-green-100' },
  brother: { emoji: '👬', color: 'text-cyan-600', bg: 'bg-cyan-100' },
  'best-friend': { emoji: '👯', color: 'text-yellow-600', bg: 'bg-yellow-100' },
  default: { emoji: '👤', color: 'text-gray-600', bg: 'bg-gray-100' }
}

// Pregnancy reactions
const pregnancyReactions = {
  love: { emoji: '❤️', label: 'Love' },
  excited: { emoji: '😍', label: 'Excited' },
  care: { emoji: '🤗', label: 'Care' },
  support: { emoji: '💪', label: 'Support' },
  beautiful: { emoji: '✨', label: 'Beautiful' },
  funny: { emoji: '😂', label: 'Funny' },
  praying: { emoji: '🙏', label: 'Praying' },
  proud: { emoji: '🥰', label: 'Proud' },
  grateful: { emoji: '🙏✨', label: 'Grateful' }
}

// Computed properties
const displayedReactors = computed(() => {
  return props.reactors.slice(0, props.maxDisplay)
})

const hasOverflow = computed(() => {
  return props.reactors.length > props.maxDisplay
})

const overflowCount = computed(() => {
  return props.reactors.length - props.maxDisplay
})

const hasSpecialFamily = computed(() => {
  const specialRoles = ['partner', 'mom', 'dad', 'grandma', 'grandpa']
  return props.reactors.some(reactor => 
    specialRoles.includes(reactor.relationship || '')
  )
})

const stackStyle = computed(() => {
  const size = sizeConfig[props.size]
  return {
    gap: `${props.stackSpacing}px`
  }
})

// Methods
function getAvatarStyle(index: number) {
  const size = sizeConfig[props.size]
  const zIndex = 10 - index
  
  return {
    width: `${size.width}px`,
    height: `${size.height}px`,
    zIndex: zIndex,
    marginLeft: index > 0 ? `${props.stackSpacing}px` : '0'
  }
}

function getAvatarInitial(name: string) {
  return name.charAt(0).toUpperCase()
}

function getAvatarFallbackClass(relationship?: string) {
  const config = relationshipConfig[relationship || 'default']
  const size = sizeConfig[props.size]
  
  return [
    config.bg,
    config.color,
    size.fontSize,
    'border-2 border-white shadow-sm'
  ]
}

function getRelationshipEmoji(relationship?: string) {
  return relationshipConfig[relationship || 'default'].emoji
}

function getRelationshipIndicatorClass(relationship?: string) {
  const config = relationshipConfig[relationship || 'default']
  return [
    'w-5 h-5 rounded-full flex items-center justify-center text-xs shadow-sm border border-white',
    config.bg,
    config.color
  ]
}

function getReactionEmoji(reactionType: string) {
  return pregnancyReactions[reactionType as keyof typeof pregnancyReactions]?.emoji || '❤️'
}

function getReactionLabel(reactionType: string) {
  return pregnancyReactions[reactionType as keyof typeof pregnancyReactions]?.label || 'Love'
}

function isSpecialRelationship(relationship?: string) {
  return ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(relationship || '')
}

function getSummaryText() {
  const total = props.reactors.length
  if (total === 1) return `${props.reactors[0].name} reacted`
  if (total === 2) return `${props.reactors[0].name} and 1 other`
  return `${props.reactors[0].name} and ${total - 1} others`
}

function getSpecialFamilyText() {
  const specialReactors = props.reactors.filter(reactor => 
    isSpecialRelationship(reactor.relationship)
  )
  
  if (specialReactors.length === 0) return ''
  if (specialReactors.length === 1) {
    const relationship = relationshipConfig[specialReactors[0].relationship || 'default']
    return `Including your ${specialReactors[0].relationship}`
  }
  
  return `Including close family members`
}

function handleClusterClick() {
  emit('click')
  
  // Add gentle pulse animation
  if (clusterRef.value) {
    pulseElement(clusterRef.value, 'gentle')
  }
}

function handleAvatarClick(reactor: FamilyReactor) {
  emit('avatarClick', { reactor })
}

function handleAvatarHover(reactor: FamilyReactor, isHovering: boolean, event: Event) {
  if (props.isInteractive) {
    hoveredReactor.value = isHovering ? reactor : null
    emit('avatarHover', { reactor, isHovering })
  }
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

// Lifecycle
onMounted(() => {
  // Add hover effects to interactive clusters
  if (props.isInteractive && clusterRef.value) {
    createGentleHover(clusterRef.value, 'lift')
  }
  
  // Add stagger animation to avatars
  const avatars = clusterRef.value?.querySelectorAll('.avatar-wrapper')
  avatars?.forEach((avatar, index) => {
    const element = avatar as HTMLElement
    element.style.animationDelay = `${index * 100}ms`
    element.classList.add('avatar-enter')
  })
})
</script>

<style scoped>
/* Base cluster styling */
.family-avatar-cluster {
  @apply flex items-center;
}

.family-avatar-cluster.is-interactive {
  @apply cursor-pointer transition-all duration-200;
}

.family-avatar-cluster.is-interactive:hover {
  @apply scale-105;
}

/* Avatar stack styling */
.avatar-stack {
  @apply relative;
}

/* Individual avatar wrapper */
.avatar-wrapper {
  @apply relative transition-all duration-200 hover:scale-110 hover:z-20;
}

.avatar-wrapper.has-special-relationship {
  @apply ring-2 ring-soft-pink/50 rounded-full;
}

/* Avatar container */
.avatar-container {
  @apply transition-transform duration-200;
}

/* Avatar image styling */
.avatar-image {
  @apply border-2 border-white shadow-md;
}

/* Avatar fallback styling */
.avatar-fallback {
  @apply transition-all duration-200;
}

/* Overflow counter styling */
.overflow-counter .overflow-avatar {
  @apply transition-all duration-200 hover:scale-110;
}

/* Relationship indicator styling */
.relationship-indicator {
  @apply transition-all duration-200 hover:scale-110;
}

/* Reaction indicator styling */
.reaction-indicator {
  @apply transition-all duration-200 hover:scale-110;
}

/* Cluster summary styling */
.cluster-summary {
  @apply transition-all duration-200;
}

/* Avatar entrance animation */
.avatar-enter {
  animation: avatar-enter 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
}

@keyframes avatar-enter {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Hover effects for different avatar positions */
.avatar-0:hover {
  transform: scale(1.15) translateX(2px);
}

.avatar-1:hover {
  transform: scale(1.15);
}

.avatar-2:hover {
  transform: scale(1.15) translateX(-2px);
}

.avatar-3:hover {
  transform: scale(1.15) translateX(-4px);
}

/* Special relationship highlighting */
.has-special-relationship .avatar-container {
  animation: special-family-glow 3s ease-in-out infinite;
}

@keyframes special-family-glow {
  0%, 100% {
    filter: drop-shadow(0 0 2px rgba(248, 187, 208, 0.3));
  }
  50% {
    filter: drop-shadow(0 0 6px rgba(248, 187, 208, 0.6));
  }
}

/* Interactive cluster effects */
.is-interactive:hover .avatar-wrapper {
  transform: scale(1.05);
}

.is-interactive:hover .avatar-wrapper:hover {
  transform: scale(1.2) !important;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .avatar-wrapper {
    @apply hover:scale-105;
  }
  
  .is-interactive:hover .avatar-wrapper:hover {
    transform: scale(1.1) !important;
  }
  
  .cluster-summary {
    @apply ml-2;
  }
  
  .cluster-summary p {
    @apply text-xs;
  }
}

/* Accessibility enhancements */
.family-avatar-cluster:focus {
  @apply outline-2 outline-soft-pink outline-offset-2;
}

.avatar-wrapper:focus {
  @apply outline-2 outline-soft-pink outline-offset-2 rounded-full;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .avatar-image,
  .avatar-fallback {
    @apply border-2 border-gray-900;
  }
  
  .overflow-avatar {
    @apply bg-gray-900 text-white;
  }
  
  .relationship-indicator {
    @apply border-2 border-gray-900;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .avatar-wrapper,
  .avatar-container,
  .family-avatar-cluster {
    transition: none !important;
  }
  
  .avatar-enter {
    animation: none !important;
  }
  
  .special-family-glow {
    animation: none !important;
  }
  
  .has-special-relationship {
    @apply ring-2 ring-soft-pink/50 rounded-full;
  }
}

/* Loading state for images */
.avatar-image {
  @apply transition-opacity duration-200;
}

.avatar-image[src=""] {
  @apply opacity-0;
}

/* Stacking context management */
.avatar-stack {
  isolation: isolate;
}

.avatar-wrapper {
  position: relative;
}
</style>
