<template>
  <div 
    v-if="hasReactions" 
    ref="summaryRef"
    class="reaction-summary family-warm-context"
    :class="{ 'is-milestone': isMilestone }"
  >
    <!-- Main Reaction Display -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-3">
        <!-- Top Reactions -->
        <div class="flex items-center gap-1">
          <div
            v-for="(count, reactionType) in topReactions"
            :key="reactionType"
            class="reaction-bubble"
            :class="[
              `reaction-${reactionType}`,
              { 'has-celebration': isCelebrationMoment(reactionType as string) }
            ]"
            @click="handleReactionClick(reactionType as string)"
          >
            <span class="reaction-emoji">{{ getReactionEmoji(reactionType as string) }}</span>
            <span class="reaction-count">{{ count }}</span>
          </div>
        </div>

        <!-- Family Love Message -->
        <p class="family-message text-sm text-gray-700 font-medium">
          {{ getFamilyLoveMessage() }}
        </p>
      </div>

      <!-- View All Button -->
      <button
        v-if="totalCount > 3"
        @click="handleViewAll"
        class="text-xs text-soft-pink hover:text-soft-pink/80 font-medium transition-colors py-1 px-2 rounded-full hover:bg-soft-pink/10"
        :aria-label="`View all ${totalCount} reactions`"
      >
        View all {{ totalCount }}
      </button>
    </div>

    <!-- Family Context Row -->
    <div v-if="showFamilyContext && recentReactors.length > 0" class="family-context-row">
      <div class="flex items-center gap-3">
        <!-- Family Avatar Cluster -->
        <FamilyAvatarCluster
          :reactors="recentReactors"
          :max-display="4"
          @click="handleViewReactors"
        />

        <!-- Warm Family Message -->
        <div class="family-reaction-text">
          <p class="text-sm text-gray-600">
            <span class="family-warmth-emoji">💕</span>
            {{ getFamilyReactionText() }}
          </p>
          <p v-if="hasSpecialRelationships" class="text-xs text-gray-500 mt-1">
            {{ getSpecialRelationshipText() }}
          </p>
        </div>
      </div>
    </div>

    <!-- Milestone Celebration Banner -->
    <div v-if="isMilestone" class="milestone-celebration-banner mt-3">
      <div class="flex items-center gap-2 p-3 bg-gradient-to-r from-soft-pink/20 to-gentle-mint/15 rounded-xl border border-soft-pink/30">
        <span class="text-xl">🎉</span>
        <div>
          <p class="text-sm font-semibold text-gray-800">Milestone Moment!</p>
          <p class="text-xs text-gray-600">Your family is celebrating this special share</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGentleTransitions, useCelebrationAnimation } from '~/composables/useAnimations'
import FamilyAvatarCluster from './FamilyAvatarCluster.vue'

interface FamilyReactor {
  id: string
  name: string
  relationship?: string // 'grandma', 'mom', 'partner', 'best-friend', etc.
  avatar_url?: string
  reaction_type: string
  reacted_at: string
}

interface Props {
  reactionCounts?: Record<string, number>
  totalCount?: number
  recentReactors?: FamilyReactor[]
  isMilestone?: boolean
  showFamilyContext?: boolean
  maxReactionsDisplay?: number
}

const props = withDefaults(defineProps<Props>(), {
  totalCount: 0,
  recentReactors: () => [],
  showFamilyContext: true,
  maxReactionsDisplay: 3,
  isMilestone: false
})

const emit = defineEmits<{
  viewAll: []
  viewReactors: []
  reactionClick: [{ reactionType: string }]
}>()

// Animation composables
const { pulseElement, glowElement } = useGentleTransitions()
const { celebrateReaction } = useCelebrationAnimation()

// Local state
const summaryRef = ref<HTMLElement>()

// Pregnancy-specific reaction configuration
const pregnancyReactions = {
  love: { emoji: '❤️', label: 'Love', warmMessage: 'sends love' },
  excited: { emoji: '😍', label: 'Excited', warmMessage: 'is so excited' },
  care: { emoji: '🤗', label: 'Care', warmMessage: 'sends hugs' },
  support: { emoji: '💪', label: 'Support', warmMessage: 'supports you' },
  beautiful: { emoji: '✨', label: 'Beautiful', warmMessage: 'finds this beautiful' },
  funny: { emoji: '😂', label: 'Funny', warmMessage: 'smiled at this' },
  praying: { emoji: '🙏', label: 'Praying', warmMessage: 'sends prayers' },
  proud: { emoji: '🥰', label: 'Proud', warmMessage: 'is proud of you' },
  grateful: { emoji: '🙏✨', label: 'Grateful', warmMessage: 'is grateful' }
}

// Relationship display names
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

// Computed properties
const hasReactions = computed(() => props.totalCount > 0)

const topReactions = computed(() => {
  if (!props.reactionCounts) return {}
  
  const sorted = Object.entries(props.reactionCounts)
    .filter(([_, count]) => count > 0)
    .sort(([_, a], [__, b]) => b - a)
    .slice(0, props.maxReactionsDisplay)
  
  return Object.fromEntries(sorted)
})

const hasSpecialRelationships = computed(() => {
  return props.recentReactors.some(reactor => 
    ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(reactor.relationship || '')
  )
})

// Methods
function getReactionEmoji(reactionType: string) {
  return pregnancyReactions[reactionType as keyof typeof pregnancyReactions]?.emoji || '❤️'
}

function isCelebrationMoment(reactionType: string) {
  return ['beautiful', 'proud', 'excited'].includes(reactionType) && props.isMilestone
}

function getFamilyLoveMessage() {
  const count = props.totalCount
  
  if (count === 0) return ''
  if (count === 1) return 'Your family loves this moment'
  if (count <= 3) return 'Your family is celebrating with you'
  if (count <= 10) return 'So much family love for this share'
  return 'Your whole family is celebrating this with you!'
}

function getFamilyReactionText() {
  const reactors = props.recentReactors.slice(0, 3)
  
  if (reactors.length === 0) return ''
  
  if (reactors.length === 1) {
    const reactor = reactors[0]
    const relationship = relationshipLabels[reactor.relationship || ''] || reactor.name
    const warmMessage = pregnancyReactions[reactor.reaction_type as keyof typeof pregnancyReactions]?.warmMessage || 'reacted'
    return `${relationship} ${warmMessage}`
  }
  
  if (reactors.length === 2) {
    const names = reactors.map(r => relationshipLabels[r.relationship || ''] || r.name)
    return `${names[0]} and ${names[1]} are celebrating with you`
  }
  
  const names = reactors.map(r => relationshipLabels[r.relationship || ''] || r.name)
  return `${names[0]}, ${names[1]} and others are celebrating`
}

function getSpecialRelationshipText() {
  const specialReactors = props.recentReactors.filter(reactor => 
    ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(reactor.relationship || '')
  )
  
  if (specialReactors.length === 0) return ''
  
  const relationships = specialReactors.map(r => 
    relationshipLabels[r.relationship || ''] || r.name
  ).slice(0, 2)
  
  if (relationships.length === 1) {
    return `${relationships[0]} shared a special reaction`
  }
  
  return `${relationships.join(' and ')} shared special reactions`
}

function handleReactionClick(reactionType: string) {
  emit('reactionClick', { reactionType })
  
  // Add celebration animation for special reactions
  if (summaryRef.value && isCelebrationMoment(reactionType)) {
    celebrateReaction(summaryRef.value, reactionType)
  }
}

function handleViewAll() {
  emit('viewAll')
}

function handleViewReactors() {
  emit('viewReactors')
}

// Lifecycle
onMounted(() => {
  // Add gentle glow for milestone moments
  if (props.isMilestone && summaryRef.value) {
    glowElement(summaryRef.value, 5000)
  }
  
  // Add gentle pulse for first few reactions
  if (props.totalCount <= 3 && summaryRef.value) {
    pulseElement(summaryRef.value, 'warm')
  }
})
</script>

<style scoped>
/* Main container styling */
.reaction-summary {
  @apply transition-all duration-300 ease-out;
}

.reaction-summary.is-milestone {
  @apply bg-gradient-to-r from-soft-pink/5 to-gentle-mint/5 rounded-xl p-4 border border-soft-pink/20;
}

/* Reaction bubble styling */
.reaction-bubble {
  @apply flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-full border border-gray-200/60 shadow-sm cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-105;
}

.reaction-bubble:hover {
  @apply border-soft-pink/40 bg-soft-pink/5;
}

.reaction-bubble.has-celebration {
  @apply animate-gentle-pulse;
}

/* Reaction type specific styling */
.reaction-love {
  @apply hover:border-red-300 hover:bg-red-50/50;
}

.reaction-excited {
  @apply hover:border-purple-300 hover:bg-purple-50/50;
}

.reaction-care {
  @apply hover:border-blue-300 hover:bg-blue-50/50;
}

.reaction-support {
  @apply hover:border-green-300 hover:bg-green-50/50;
}

.reaction-beautiful {
  @apply hover:border-yellow-300 hover:bg-yellow-50/50;
}

.reaction-funny {
  @apply hover:border-orange-300 hover:bg-orange-50/50;
}

.reaction-praying {
  @apply hover:border-indigo-300 hover:bg-indigo-50/50;
}

.reaction-proud {
  @apply hover:border-pink-300 hover:bg-pink-50/50;
}

.reaction-grateful {
  @apply hover:border-purple-300 hover:bg-purple-50/50;
}

/* Emoji and count styling */
.reaction-emoji {
  @apply text-lg transition-transform duration-200;
}

.reaction-bubble:hover .reaction-emoji {
  @apply scale-110;
}

.reaction-count {
  @apply text-sm font-semibold text-gray-700 min-w-[1rem] text-center;
}

/* Family context styling */
.family-context-row {
  @apply border-t border-gray-100/80 pt-3 mt-3;
}

.family-reaction-text {
  @apply flex-1;
}

.family-warmth-emoji {
  @apply mr-1;
}

/* Family message styling */
.family-message {
  @apply text-gray-700 font-medium;
}

/* Milestone celebration banner */
.milestone-celebration-banner {
  @apply animate-gentle-pulse;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .reaction-bubble {
    @apply px-2 py-1 gap-1;
  }
  
  .reaction-emoji {
    @apply text-base;
  }
  
  .reaction-count {
    @apply text-xs;
  }
  
  .family-message {
    @apply text-xs;
  }
}

/* Accessibility enhancements */
.reaction-bubble:focus {
  @apply outline-2 outline-soft-pink outline-offset-2;
}

.reaction-summary button:focus {
  @apply outline-2 outline-soft-pink outline-offset-2;
}

/* Animation classes for dynamic reactions */
@keyframes celebration-sparkle {
  0%, 100% { 
    transform: scale(1) rotate(0deg); 
    opacity: 1; 
  }
  50% { 
    transform: scale(1.1) rotate(180deg); 
    opacity: 0.8; 
  }
}

.has-celebration:hover {
  animation: celebration-sparkle 0.6s ease-in-out;
}

/* Special milestone styling */
.is-milestone .reaction-bubble {
  @apply shadow-md;
}

.is-milestone .family-message {
  @apply text-soft-pink font-semibold;
}
</style>
