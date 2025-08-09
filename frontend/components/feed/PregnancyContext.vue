<template>
  <div 
    class="pregnancy-context flex items-center gap-2 text-sm text-gray-500 transition-opacity duration-200"
    :class="{ 'context-faded': shouldFade }"
  >
    <!-- Week Badge -->
    <span 
      v-if="week > 0"
      class="week-badge inline-flex items-center px-2 py-1 bg-gradient-to-r from-soft-pink/20 to-gentle-mint/20 text-soft-pink-dark rounded-full text-xs font-medium border border-soft-pink/20"
      :class="{ 'week-milestone': isMilestone }"
      :aria-label="`Pregnancy week ${week}`"
    >
      <span class="text-xs mr-1">🤱</span>
      Week {{ week }}
    </span>

    <!-- Mood Indicator -->
    <span 
      v-if="mood && !shouldHideMood"
      class="mood-indicator inline-flex items-center gap-1 px-2 py-1 bg-muted-lavender/20 text-muted-lavender-dark rounded-full text-xs"
      :aria-label="`Feeling ${mood.label || mood}`"
    >
      <span class="mood-emoji">{{ getMoodEmoji() }}</span>
      <span class="mood-text">{{ getMoodText() }}</span>
    </span>

    <!-- Visual Separator -->
    <span 
      v-if="hasMultipleElements && !isSmallScreen" 
      class="separator text-gray-300 mx-1"
      aria-hidden="true"
    >•</span>

    <!-- Time Stamp -->
    <time 
      :datetime="timestamp.toISOString()"
      class="time-stamp text-xs"
      :title="getFullTimestamp()"
    >
      {{ getRelativeTime() }}
    </time>

    <!-- Location -->
    <template v-if="location && !shouldHideLocation">
      <span class="separator text-gray-300 mx-1" aria-hidden="true">•</span>
      <span 
        class="location inline-flex items-center gap-1 text-xs"
        :aria-label="`Shared from ${location}`"
      >
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
          <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
        </svg>
        <span>{{ getLocationDisplay() }}</span>
      </span>
    </template>

    <!-- Special Indicators -->
    <div v-if="hasSpecialIndicators" class="special-indicators flex items-center gap-1 ml-2">
      <!-- Milestone Marker -->
      <span 
        v-if="isMilestone"
        class="milestone-marker inline-flex items-center text-xs text-gentle-mint-dark"
        :aria-label="'Milestone achievement'"
      >
        <span class="milestone-sparkle text-sm animate-pulse">✨</span>
      </span>

      <!-- Family Response Flag -->
      <span 
        v-if="needsFamilyResponse && viewerRelationship !== 'self'"
        class="response-needed inline-flex items-center text-xs text-soft-pink-dark"
        :aria-label="'Family response appreciated'"
      >
        <span class="response-heart text-sm animate-bounce">💝</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

type MoodType = 'tired' | 'excited' | 'anxious' | 'peaceful' | 'grateful' | 'uncomfortable' | 'happy' | 'emotional' | string
type RelationshipType = 'partner' | 'parent' | 'sibling' | 'friend' | 'other' | 'self'

interface MoodData {
  type: MoodType
  label?: string
  intensity?: number
}

interface Props {
  week: number
  mood?: MoodType | MoodData
  timestamp: Date
  location?: string
  isMilestone: boolean
  needsFamilyResponse: boolean
  viewerRelationship: RelationshipType
}

const props = withDefaults(defineProps<Props>(), {
  week: 0,
  isMilestone: false,
  needsFamilyResponse: false,
  viewerRelationship: 'other'
})

// Reactive state for responsive behavior
const isSmallScreen = ref(false)

// Computed properties for adaptive display
const shouldFade = computed(() => {
  const now = new Date()
  const hoursSincePost = Math.floor((now.getTime() - props.timestamp.getTime()) / (1000 * 60 * 60))
  return hoursSincePost > 168 // Fade after 1 week
})

const shouldHideMood = computed(() => {
  return isSmallScreen.value && props.location && props.week > 0
})

const shouldHideLocation = computed(() => {
  return isSmallScreen.value && (props.mood || props.week > 0)
})

const hasMultipleElements = computed(() => {
  const elements = [
    props.week > 0,
    props.mood && !shouldHideMood.value,
    props.location && !shouldHideLocation.value
  ].filter(Boolean)
  
  return elements.length > 1
})

const hasSpecialIndicators = computed(() => {
  return props.isMilestone || (props.needsFamilyResponse && props.viewerRelationship !== 'self')
})

// Mood handling
function getMoodEmoji(): string {
  const moodValue = typeof props.mood === 'object' ? props.mood.type : props.mood
  if (!moodValue) return ''
  
  const moodEmojis: Record<string, string> = {
    tired: '😴',
    excited: '🤗',
    anxious: '😰',
    peaceful: '😌',
    grateful: '🙏',
    uncomfortable: '😣',
    happy: '😊',
    emotional: '🥺',
    loving: '🥰',
    hopeful: '🌟',
    nervous: '😬',
    content: '😄'
  }
  
  return moodEmojis[moodValue] || '😊'
}

function getMoodText(): string {
  const moodValue = typeof props.mood === 'object' ? props.mood : { type: props.mood }
  if (!moodValue?.type) return ''
  
  // Use custom label if provided
  if (typeof props.mood === 'object' && props.mood.label) {
    return props.mood.label
  }
  
  // Default mood labels
  const moodLabels: Record<string, string> = {
    tired: 'tired',
    excited: 'excited',
    anxious: 'anxious', 
    peaceful: 'peaceful',
    grateful: 'grateful',
    uncomfortable: 'uncomfortable',
    happy: 'happy',
    emotional: 'emotional',
    loving: 'loving',
    hopeful: 'hopeful',
    nervous: 'nervous',
    content: 'content'
  }
  
  return moodLabels[moodValue.type] || moodValue.type
}

// Time formatting
function getRelativeTime(): string {
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - props.timestamp.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'now'
  if (diffInMinutes < 60) return `${diffInMinutes}m`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d`
  
  const diffInWeeks = Math.floor(diffInDays / 7)
  if (diffInWeeks < 4) return `${diffInWeeks}w`
  
  // For older posts, show the actual date
  return props.timestamp.toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric' 
  })
}

function getFullTimestamp(): string {
  return props.timestamp.toLocaleString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

// Location handling
function getLocationDisplay(): string {
  if (!props.location) return ''
  
  // Truncate long location names on small screens
  if (isSmallScreen.value && props.location.length > 15) {
    return props.location.substring(0, 12) + '...'
  }
  
  return props.location
}

// Responsive handling
function checkScreenSize() {
  isSmallScreen.value = window.innerWidth < 640
}

// Lifecycle
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
/* Base context whisper styling */
.pregnancy-context {
  font-size: 0.8125rem; /* 13px */
  line-height: 1.3;
  color: #6B7280;
  transition: all 0.2s ease;
}

/* Week badge special styling */
.week-badge {
  font-weight: 500;
  transition: all 0.2s ease;
}

.week-badge.week-milestone {
  background: linear-gradient(45deg, #F8BBD0, #E1BEE7);
  color: #7C2D12;
  border-color: #F8BBD0;
  animation: milestone-glow 3s ease-in-out infinite;
}

/* Mood indicator styling */
.mood-indicator {
  font-weight: 400;
  white-space: nowrap;
}

.mood-emoji {
  font-size: 0.875rem;
}

.mood-text {
  text-transform: lowercase;
}

/* Time and location styling */
.time-stamp {
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.location {
  white-space: nowrap;
}

/* Special indicators */
.special-indicators {
  margin-left: auto;
}

.milestone-marker .milestone-sparkle {
  animation: sparkle-pulse 2s ease-in-out infinite;
}

.response-needed .response-heart {
  animation: heart-bounce 1s ease-in-out infinite;
}

/* Faded state for old posts */
.context-faded {
  opacity: 0.6;
}

/* Separator dots */
.separator {
  font-size: 0.75rem;
  opacity: 0.7;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .pregnancy-context {
    font-size: 0.75rem; /* 12px on mobile */
    flex-wrap: wrap;
    gap: 0.375rem;
  }
  
  .week-badge,
  .mood-indicator {
    font-size: 0.6875rem; /* 11px */
    padding: 0.125rem 0.375rem;
  }
  
  .separator {
    display: none; /* Hide separators on mobile for cleaner look */
  }
  
  .special-indicators {
    margin-left: 0.25rem;
  }
}

/* Animations */
@keyframes milestone-glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(248, 187, 208, 0);
  }
  50% {
    box-shadow: 0 0 8px rgba(248, 187, 208, 0.4);
  }
}

@keyframes sparkle-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes heart-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .week-badge {
    border-width: 2px;
    background: white;
    color: #1F2937;
  }
  
  .mood-indicator {
    border: 1px solid currentColor;
    background: white;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .milestone-sparkle,
  .response-heart,
  .week-badge.week-milestone {
    animation: none !important;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .pregnancy-context {
    color: #9CA3AF;
  }
  
  .week-badge {
    background: rgba(248, 187, 208, 0.1);
    color: #F8BBD0;
    border-color: rgba(248, 187, 208, 0.3);
  }
  
  .mood-indicator {
    background: rgba(225, 190, 231, 0.1);
    color: #E1BEE7;
  }
}
</style>