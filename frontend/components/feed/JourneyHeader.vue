<template>
  <header 
    class="journey-header sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-warm-neutral/20 transition-all duration-300"
    :class="{ 'header-collapsed': isScrolled }"
  >
    <div class="header-content max-w-4xl mx-auto px-4 sm:px-6">
      <!-- Main Header Section -->
      <div class="main-header py-5 sm:py-6" :class="{ 'py-3': isScrolled }">
        <!-- Personalized Greeting -->
        <div class="greeting-section mb-4" :class="{ 'mb-2': isScrolled }">
          <h1 class="greeting-text text-xl sm:text-2xl font-semibold text-gray-900 font-primary mb-1">
            {{ getPersonalizedGreeting() }}
          </h1>
          
          <div class="pregnancy-context flex items-center gap-3 text-sm text-gray-600">
            <!-- Week & Baby Info -->
            <div class="week-info flex items-center gap-2">
              <span class="baby-emoji text-lg" :aria-hidden="true">👶</span>
              <span class="week-text font-medium">
                Week {{ currentWeek }} • {{ getBabyDevelopmentSnippet() }}
              </span>
            </div>
            
            <!-- Weather/Time Context -->
            <div 
              v-if="weatherContext && !isScrolled"
              class="weather-context hidden sm:flex items-center gap-1 text-xs px-2 py-1 bg-gentle-mint/20 text-gentle-mint-dark rounded-full"
            >
              <span class="weather-emoji">{{ getWeatherEmoji() }}</span>
              <span>{{ weatherContext }}</span>
            </div>
          </div>
        </div>

        <!-- Navigation Pills -->
        <nav 
          class="navigation-pills"
          role="navigation"
          :aria-label="'Journey navigation'"
        >
          <div 
            class="nav-container flex items-center gap-2 overflow-x-auto scrollbar-hide pb-2"
            :class="{ 'gap-1': isScrolled }"
          >
            <button
              v-for="filter in navigationFilters"
              :key="filter.value"
              @click="handleFilterSelect(filter.value)"
              class="nav-pill flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
              :class="[
                getNavPillClass(filter.value),
                { 'px-3 py-1.5 text-xs': isScrolled }
              ]"
              :aria-pressed="activeFilter === filter.value"
              :aria-label="`View ${filter.label} - ${filter.count || 0} items`"
            >
              <span class="pill-emoji mr-1.5" :class="{ 'mr-1': isScrolled }">{{ filter.emoji }}</span>
              <span class="pill-text">{{ filter.label }}</span>
              <span 
                v-if="filter.count && filter.count > 0 && !isScrolled"
                class="pill-count ml-1.5 px-1.5 py-0.5 bg-white/30 rounded text-xs"
              >
                {{ filter.count }}
              </span>
            </button>
          </div>
        </nav>
      </div>

      <!-- Quick Stats Bar (collapsed state) -->
      <div 
        v-if="isScrolled && familyEngagementStats"
        class="stats-bar flex items-center justify-between py-2 text-xs text-gray-500 border-t border-gray-100"
      >
        <div class="flex items-center gap-4">
          <span class="flex items-center gap-1">
            <span class="text-soft-pink">📝</span>
            {{ familyEngagementStats.totalPosts }} stories
          </span>
          <span class="flex items-center gap-1">
            <span class="text-gentle-mint">💕</span>
            {{ familyEngagementStats.totalReactions }} hearts
          </span>
        </div>
        
        <div v-if="recentMood" class="current-mood flex items-center gap-1">
          <span>{{ getMoodEmoji() }}</span>
          <span class="capitalize">{{ recentMood.label || recentMood }}</span>
        </div>
      </div>
    </div>

    <!-- Gentle Progress Indicator -->
    <div 
      v-if="showProgressIndicator"
      class="progress-indicator absolute bottom-0 left-0 right-0 h-1 bg-gray-100 overflow-hidden"
    >
      <div 
        class="progress-fill h-full bg-gradient-to-r from-soft-pink to-gentle-mint transition-all duration-500"
        :style="{ width: `${(currentWeek / 40) * 100}%` }"
      />
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

type FilterValue = 'today' | 'milestones' | 'family' | 'memories' | 'all'
type MoodType = 'tired' | 'excited' | 'anxious' | 'peaceful' | 'grateful' | 'uncomfortable' | 'happy' | 'emotional' | string

interface NavigationFilter {
  value: FilterValue
  label: string
  emoji: string
  count?: number
  description: string
}

interface FamilyEngagementStats {
  totalPosts: number
  totalReactions: number
  totalComments: number
  avgEngagement: number
}

interface Props {
  userName: string
  currentWeek: number
  babyDevelopment?: string
  recentMood?: MoodType | { type: MoodType, label?: string }
  weatherContext?: string
  activeFilter: FilterValue
  familyEngagementStats?: FamilyEngagementStats
  showProgressIndicator?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: 0,
  activeFilter: 'today',
  showProgressIndicator: true
})

const emit = defineEmits<{
  filterChange: [filter: FilterValue]
}>()

// Local state
const isScrolled = ref(false)
const scrollThreshold = 60

// Navigation filters with pregnancy-focused language
const navigationFilters = ref<NavigationFilter[]>([
  {
    value: 'today',
    label: 'Today',
    emoji: '🌅',
    description: "Today's moments and family responses"
  },
  {
    value: 'milestones',
    label: 'Milestones',
    emoji: '✨',
    description: 'Special achievements and celebrations'
  },
  {
    value: 'family',
    label: 'Family',
    emoji: '💝',
    description: 'Stories with lots of family love'
  },
  {
    value: 'memories',
    label: 'Memories',
    emoji: '📖',
    description: 'Saved moments for reflection'
  },
  {
    value: 'all',
    label: 'Journey',
    emoji: '🌸',
    description: 'Your complete pregnancy story'
  }
])

// Computed properties
const timeOfDay = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'morning'
  if (hour < 17) return 'afternoon'
  if (hour < 21) return 'evening'
  return 'night'
})

// Methods
function getPersonalizedGreeting(): string {
  const timeGreetings = {
    morning: 'Good morning',
    afternoon: 'Good afternoon', 
    evening: 'Good evening',
    night: 'Hope you\'re resting well'
  }
  
  const greeting = timeGreetings[timeOfDay.value]
  return `${greeting}, ${props.userName} 💕`
}

function getBabyDevelopmentSnippet(): string {
  if (props.babyDevelopment) {
    // Take first 40 characters and add ellipsis
    const snippet = props.babyDevelopment.substring(0, 40)
    return snippet.length < props.babyDevelopment.length ? `${snippet}...` : snippet
  }
  
  // Fallback development info by week
  const fallbackInfo = {
    1: 'Your journey begins',
    4: 'Baby is the size of a poppy seed',
    8: 'Baby is the size of a raspberry', 
    12: 'End of first trimester',
    16: 'Baby is the size of an avocado',
    20: 'Halfway there! Baby is the size of a banana',
    24: 'Baby can hear your voice',
    28: 'Third trimester begins',
    32: 'Baby is the size of a pineapple',
    36: 'Baby is considered full-term soon',
    40: 'Welcome to the world, baby!'
  }
  
  // Find closest week
  const weeks = Object.keys(fallbackInfo).map(Number).sort((a, b) => a - b)
  const closestWeek = weeks.reduce((prev, curr) => 
    Math.abs(curr - props.currentWeek) < Math.abs(prev - props.currentWeek) ? curr : prev
  )
  
  return fallbackInfo[closestWeek as keyof typeof fallbackInfo] || 'Baby is growing strong'
}

function getWeatherEmoji(): string {
  if (!props.weatherContext) return '☀️'
  
  const context = props.weatherContext.toLowerCase()
  if (context.includes('rain')) return '🌧️'
  if (context.includes('cold') || context.includes('snow')) return '❄️'
  if (context.includes('warm') || context.includes('sunny')) return '☀️'
  if (context.includes('cloud')) return '⛅'
  if (context.includes('cozy')) return '🏠'
  
  return '🌤️'
}

function getMoodEmoji(): string {
  const moodValue = typeof props.recentMood === 'object' ? props.recentMood.type : props.recentMood
  if (!moodValue) return '😊'
  
  const moodEmojis: Record<string, string> = {
    tired: '😴',
    excited: '🤗',
    anxious: '😰',
    peaceful: '😌',
    grateful: '🙏',
    uncomfortable: '😣',
    happy: '😊',
    emotional: '🥺'
  }
  
  return moodEmojis[moodValue] || '😊'
}

function getNavPillClass(filterValue: FilterValue): string {
  const baseClass = 'hover:shadow-md focus:shadow-md transform hover:scale-105 active:scale-95'
  
  if (props.activeFilter === filterValue) {
    return `${baseClass} bg-gradient-to-r from-soft-pink to-gentle-mint text-white shadow-md`
  }
  
  return `${baseClass} bg-white text-gray-700 border border-gray-200 hover:border-soft-pink/30 hover:bg-soft-pink/5`
}

function handleFilterSelect(filter: FilterValue): void {
  if (filter !== props.activeFilter) {
    emit('filterChange', filter)
  }
}

function handleScroll(): void {
  if (typeof window !== 'undefined') {
    isScrolled.value = window.scrollY > scrollThreshold
  }
}

// Lifecycle
onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('scroll', handleScroll)
  }
})
</script>

<style scoped>
/* Journey header base styles */
.journey-header {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.journey-header.header-collapsed {
  backdrop-filter: blur(12px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Backdrop blur support */
@supports (backdrop-filter: blur(12px)) {
  .journey-header {
    backdrop-filter: blur(8px);
  }
}

/* Greeting section */
.greeting-section {
  transition: all 0.3s ease;
}

.greeting-text {
  background: linear-gradient(135deg, #374151 0%, #4B5563 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none;
}

.baby-emoji {
  animation: gentle-bounce 3s ease-in-out infinite;
  display: inline-block;
}

.week-text {
  color: #6B7280;
  font-variation-settings: "wght" 500;
}

/* Weather context */
.weather-context {
  animation: fade-in 0.5s ease-out;
  backdrop-filter: blur(4px);
}

.weather-emoji {
  animation: gentle-float 4s ease-in-out infinite;
  display: inline-block;
}

/* Navigation pills */
.navigation-pills {
  position: relative;
}

.nav-container {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.nav-container::-webkit-scrollbar {
  display: none;
}

.nav-pill {
  position: relative;
  min-height: 44px; /* Pregnancy-aware touch target */
  white-space: nowrap;
  user-select: none;
  backdrop-filter: blur(4px);
}

.nav-pill:hover .pill-emoji {
  transform: scale(1.1);
}

.nav-pill:active {
  transform: scale(0.98);
}

/* Active pill special effects */
.nav-pill:has(.pill-count) {
  position: relative;
  overflow: hidden;
}

/* Pill components */
.pill-emoji {
  transition: transform 0.2s ease;
  display: inline-block;
}

.pill-text {
  font-weight: 500;
  letter-spacing: 0.01em;
}

.pill-count {
  font-size: 0.6875rem;
  font-weight: 600;
  line-height: 1;
}

/* Stats bar */
.stats-bar {
  animation: slide-down 0.3s ease-out;
  background: rgba(255, 255, 255, 0.8);
}

/* Progress indicator */
.progress-indicator {
  transition: opacity 0.3s ease;
}

.progress-fill {
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 8px rgba(248, 187, 208, 0.3);
}

/* Responsive design */
@media (max-width: 640px) {
  .header-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .greeting-text {
    font-size: 1.25rem;
  }
  
  .pregnancy-context {
    font-size: 0.8125rem;
  }
  
  .nav-pill {
    min-height: 40px;
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }
  
  .nav-container {
    gap: 0.5rem;
  }
}

/* Animations */
@keyframes gentle-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

@keyframes gentle-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Focus styles for accessibility */
.nav-pill:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(248, 187, 208, 0.4);
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .journey-header {
    border-bottom: 2px solid #000;
  }
  
  .nav-pill {
    border-width: 2px;
  }
  
  .nav-pill[aria-pressed="true"] {
    background: #000;
    color: #fff;
  }
  
  .progress-fill {
    background: #000;
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .journey-header,
  .greeting-section,
  .nav-pill,
  .baby-emoji,
  .weather-emoji,
  .pill-emoji,
  .progress-fill {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .journey-header {
    background: rgba(17, 24, 39, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .greeting-text {
    background: linear-gradient(135deg, #F9FAFB 0%, #D1D5DB 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .week-text {
    color: #9CA3AF;
  }
  
  .nav-pill {
    background: rgba(31, 41, 55, 0.8);
    border-color: rgba(75, 85, 99, 0.5);
    color: #F9FAFB;
  }
  
  .stats-bar {
    background: rgba(17, 24, 39, 0.8);
    border-color: rgba(75, 85, 99, 0.3);
    color: #9CA3AF;
  }
}

/* Print styles */
@media print {
  .journey-header {
    position: static !important;
    box-shadow: none !important;
    border-bottom: 1px solid #ccc !important;
  }
  
  .nav-pill {
    display: none !important;
  }
}
</style>