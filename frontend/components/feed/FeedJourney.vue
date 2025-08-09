<template>
  <div 
    ref="journeyRef"
    class="feed-journey w-full space-y-6"
    :class="getJourneyClass()"
  >
    <!-- Journey Header -->
    <JourneyHeader
      :user-name="userName"
      :current-week="currentWeek"
      :baby-development="babyDevelopment"
      :recent-mood="userMood"
      :weather-context="getWeatherContext()"
      :active-filter="activeFilter"
      :family-engagement-stats="familyEngagementStats"
      :show-progress-indicator="true"
      @filter-change="handleFilterChange"
    />

    <!-- Gentle Loading State -->
    <div v-if="loading && stories.length === 0" class="loading-state">
      <div class="space-y-6">
        <div 
          v-for="i in 3" 
          :key="i"
          class="story-skeleton animate-pulse"
        >
          <div class="bg-white rounded-2xl p-5 shadow-sm">
            <!-- Header skeleton -->
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-soft-pink/20 rounded-full" />
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-gray-200 rounded w-1/3" />
                <div class="h-3 bg-gray-100 rounded w-1/2" />
              </div>
            </div>
            
            <!-- Content skeleton -->
            <div class="space-y-3 mb-4">
              <div class="h-3 bg-gray-200 rounded" />
              <div class="h-3 bg-gray-200 rounded w-4/5" />
              <div class="h-20 bg-gray-100 rounded-xl" />
            </div>
            
            <!-- Footer skeleton -->
            <div class="flex items-center gap-4">
              <div class="flex -space-x-1">
                <div class="w-6 h-6 bg-gentle-mint/20 rounded-full" />
                <div class="w-6 h-6 bg-muted-lavender/20 rounded-full" />
              </div>
              <div class="h-3 bg-gray-100 rounded w-1/4" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State with Gentle Encouragement -->
    <div 
      v-else-if="!loading && stories.length === 0"
      class="empty-state py-16 text-center"
    >
      <div class="bg-white rounded-2xl p-8 max-w-sm mx-auto border border-gray-200">
        <div class="mb-6">
          <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-soft-pink/20 to-gentle-mint/20 rounded-2xl flex items-center justify-center">
            <span class="text-2xl">📝</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2 font-primary">
            {{ getEmptyStateTitle() }}
          </h3>
          <p class="text-sm text-gray-600 leading-relaxed">
            {{ getEmptyStateMessage() }}
          </p>
        </div>
        
        <button
          @click="handleCreateFirstStory"
          class="create-story-btn px-6 py-3 bg-gradient-to-r from-soft-pink to-gentle-mint text-white rounded-full text-sm font-medium hover:shadow-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
        >
          <span class="mr-2">✨</span>
          Start Your Story
        </button>
      </div>
    </div>

    <!-- Journey Stories -->
    <div v-else class="journey-stories space-y-6">
      <!-- Memory Prompts (contextual) -->
      <template v-if="shouldShowMemoryPrompts">
        <MemoryPrompt
          v-for="prompt in contextualPrompts"
          :key="`prompt-${prompt.type}-${prompt.week}`"
          :prompt-type="prompt.type"
          :pregnancy-week="prompt.week"
          :last-activity="prompt.lastActivity"
          :user-energy-level="userEnergyLevel"
          :family-count="familyMemberCount"
          :is-highlighted="prompt.isHighlighted"
          @accept="handleMemoryPromptAction"
          @dismiss="handleMemoryPromptDismiss"
          @defer="handleMemoryPromptDefer"
        />
      </template>

      <!-- Story Cards with Staggered Animation -->
      <TransitionGroup
        name="story-card"
        tag="div"
        class="stories-container"
        @enter="onStoryEnter"
        @leave="onStoryLeave"
      >
        <StoryCard
          v-for="(story, index) in displayedStories"
          :key="story.id"
          :post="story"
          :family-warmth="getFamilyWarmthData(story)"
          :user-permissions="getUserPermissions(story)"
          :card-size="getCardSize()"
          :emotional-tone="getEmotionalTone(story)"
          :data-story-index="index"
          @send-love="handleSendLove"
          @add-to-memory="handleAddToMemory"
          @view-family-activity="handleViewFamilyActivity"
          @expand-content="handleExpandContent"
          @view-media="handleViewMedia"
        />
      </TransitionGroup>

      <!-- Load More Stories -->
      <div v-if="hasMore" class="load-more-section py-8 text-center">
        <button
          v-if="!loading"
          @click="loadMoreStories"
          class="load-more-btn px-6 py-3 bg-white text-gray-700 border-2 border-gray-200 rounded-full text-sm font-medium hover:border-soft-pink/30 hover:bg-soft-pink/5 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
        >
          <span class="mr-2">📖</span>
          Continue Your Journey
        </button>
        
        <div v-else class="loading-more flex items-center justify-center gap-2 text-gray-500">
          <div class="loading-spinner w-4 h-4 border-2 border-soft-pink border-t-transparent rounded-full animate-spin" />
          <span class="text-sm">Loading more stories...</span>
        </div>
      </div>

      <!-- End of Journey Message -->
      <div 
        v-else-if="stories.length > 0"
        class="journey-end py-12 text-center"
      >
        <div class="max-w-xs mx-auto">
          <div class="mb-4 text-3xl">🌸</div>
          <h3 class="text-base font-semibold text-gray-800 mb-2 font-primary">
            You're all caught up!
          </h3>
          <p class="text-sm text-gray-600 leading-relaxed">
            Your beautiful pregnancy journey continues. Every moment is precious.
          </p>
          
          <div class="mt-4 flex items-center justify-center">
            <div class="w-12 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
            <span class="mx-3 text-xs text-gray-400">💕</span>
            <div class="w-12 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll to Top Button -->
    <Transition name="scroll-top">
      <button
        v-if="showScrollToTop"
        @click="scrollToTop"
        class="scroll-top-btn fixed bottom-6 right-4 z-30 p-3 bg-gradient-to-r from-soft-pink to-gentle-mint text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
        :aria-label="'Scroll to top of journey'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useFeedStore } from '~/stores/feed'
import { useAuth } from '~/composables/useAuth'
import { usePregnancyAnimations } from '~/composables/usePregnancyAnimations'
import type { components } from '~/types/api'
import JourneyHeader from './JourneyHeader.vue'
import StoryCard from './StoryCard.vue'
import MemoryPrompt from './MemoryPrompt.vue'

type EnrichedPost = components['schemas']['EnrichedPost']
type FilterType = 'today' | 'milestones' | 'family' | 'memories' | 'all'

interface Props {
  pregnancyId: string
  userName: string
  currentWeek: number
  babyDevelopment?: string
  userMood?: string
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night'
  familyActivity: 'high' | 'medium' | 'low'
  familyMemberCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  familyMemberCount: 0
})

const emit = defineEmits<{
  postInteraction: [{ type: string, postId: string, data?: any }]
  filterChanged: [{ filter: string, count: number }]
  memoryPromptAction: [{ action: string, data?: any }]
}>()

// Composables
const feedStore = useFeedStore()
const auth = useAuth()
const { gentleEntrance, cancelAllAnimations } = usePregnancyAnimations()

// Store refs
const {
  posts,
  loading,
  hasMore,
  activeFilter,
  familyEngagementStats
} = storeToRefs(feedStore)

// Local state
const journeyRef = ref<HTMLElement>()
const showScrollToTop = ref(false)
const displayedStories = ref<EnrichedPost[]>([])
const contextualPrompts = ref<any[]>([])

// Computed properties
const stories = computed(() => posts.value)

const userEnergyLevel = computed((): 'high' | 'medium' | 'low' => {
  const hour = new Date().getHours()
  if (props.timeOfDay === 'morning' && hour < 10) return 'high'
  if (props.timeOfDay === 'evening' && hour > 19) return 'low'
  return 'medium'
})

const shouldShowMemoryPrompts = computed(() => {
  return contextualPrompts.value.length > 0 && stories.value.length > 0
})

// Methods
function getJourneyClass(): string {
  return `journey-${props.timeOfDay} journey-activity-${props.familyActivity}`
}

function getWeatherContext(): string {
  const hour = new Date().getHours()
  const isWeekend = [0, 6].includes(new Date().getDay())
  
  if (props.timeOfDay === 'morning') {
    return isWeekend ? 'Perfect morning to rest' : 'Beautiful day ahead'
  } else if (props.timeOfDay === 'evening') {
    return 'Cozy evening to reflect'
  }
  
  return hour < 16 ? 'Lovely day for gentle movement' : 'Time to unwind'
}

function getEmptyStateTitle(): string {
  switch (activeFilter.value) {
    case 'milestones':
      return 'Your milestones await'
    case 'family':
      return 'Family memories to come'
    case 'memories':
      return 'Create your first memory'
    default:
      return 'Your journey begins here'
  }
}

function getEmptyStateMessage(): string {
  switch (activeFilter.value) {
    case 'milestones':
      return 'Special moments and achievements will be celebrated here as your pregnancy progresses.'
    case 'family':
      return 'When your family shares love and memories, they\'ll appear here.'
    case 'memories':
      return 'Moments you save and cherish will create a beautiful collection here.'
    default:
      return 'Start documenting your pregnancy journey. Every moment is worth sharing with your loved ones.'
  }
}

function getCardSize(): 'comfortable' | 'cozy' | 'minimal' {
  if (userEnergyLevel.value === 'low') return 'cozy'
  return 'comfortable'
}

function getEmotionalTone(story: EnrichedPost): 'supportive' | 'celebratory' | 'gentle' {
  if (story.type === 'milestone') return 'celebratory'
  if (story.engagement_stats?.needs_family_response) return 'supportive'
  return 'gentle'
}

function getFamilyWarmthData(story: EnrichedPost) {
  return {
    hearts: [], // TODO: Extract from story engagement
    activities: [], // TODO: Extract recent family activity
    memoryCount: 0, // TODO: Extract memory count
    supportLevel: 'gentle' as const // TODO: Calculate support level
  }
}

function getUserPermissions(story: EnrichedPost) {
  const isOwner = story.author?.id === auth.userProfile.value?.id
  
  return {
    canLove: true,
    canAddToMemory: true,
    canViewDetails: true
  }
}

function generateContextualPrompts(): void {
  const prompts = []
  
  // Weekly photo prompt (appears weekly)
  const daysSinceLastPhoto = 7 // TODO: Calculate from last photo post
  if (daysSinceLastPhoto >= 6 && props.timeOfDay === 'morning') {
    prompts.push({
      type: 'photo',
      week: props.currentWeek,
      lastActivity: new Date(),
      isHighlighted: true
    })
  }
  
  // Milestone prompt (at milestone weeks)
  const milestoneWeeks = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40]
  if (milestoneWeeks.includes(props.currentWeek)) {
    prompts.push({
      type: 'milestone',
      week: props.currentWeek,
      lastActivity: new Date(),
      isHighlighted: false
    })
  }
  
  // Family engagement prompt (when activity is low)
  if (props.familyActivity === 'low' && props.timeOfDay === 'evening') {
    prompts.push({
      type: 'family',
      week: props.currentWeek,
      lastActivity: new Date(),
      isHighlighted: false
    })
  }
  
  // Limit to 2 prompts maximum
  contextualPrompts.value = prompts.slice(0, 2)
}

// Event handlers
function handleFilterChange(filter: FilterType): void {
  feedStore.updateFilter(filter as any)
  emit('filterChanged', { filter, count: stories.value.length })
}

function handleSendLove(data: { postId: string, method: 'gesture' | 'tap' }): void {
  emit('postInteraction', { 
    type: 'love', 
    postId: data.postId, 
    data: { method: data.method } 
  })
}

function handleAddToMemory(data: { postId: string, method: 'gesture' | 'tap' }): void {
  emit('postInteraction', { 
    type: 'memory', 
    postId: data.postId, 
    data: { method: data.method } 
  })
}

function handleViewFamilyActivity(data: { postId: string }): void {
  emit('postInteraction', { type: 'view_activity', postId: data.postId })
}

function handleExpandContent(data: { postId: string }): void {
  emit('postInteraction', { type: 'expand', postId: data.postId })
}

function handleViewMedia(data: { postId: string, mediaIndex: number }): void {
  emit('postInteraction', { 
    type: 'view_media', 
    postId: data.postId, 
    data: { mediaIndex: data.mediaIndex } 
  })
}

function handleMemoryPromptAction(action: string): void {
  emit('memoryPromptAction', { action })
}

function handleMemoryPromptDismiss(): void {
  // Remove dismissed prompts
  generateContextualPrompts()
}

function handleMemoryPromptDefer(): void {
  // Defer prompts for later
  generateContextualPrompts()
}

function handleCreateFirstStory(): void {
  emit('memoryPromptAction', { action: 'create_first_story' })
}

async function loadMoreStories(): Promise<void> {
  await feedStore.loadMore()
}

function scrollToTop(): void {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleScroll(): void {
  showScrollToTop.value = window.scrollY > 500
}

// Animation handlers
function onStoryEnter(el: Element, done: () => void): void {
  const index = parseInt((el as HTMLElement).dataset.storyIndex || '0')
  const delay = index * 100
  
  gentleEntrance(el as HTMLElement, delay).then(done)
}

function onStoryLeave(el: Element, done: () => void): void {
  const animation = (el as HTMLElement).animate([
    { opacity: 1, transform: 'translateX(0)' },
    { opacity: 0, transform: 'translateX(-20px)' }
  ], {
    duration: 200,
    easing: 'ease-in'
  })
  
  animation.onfinish = () => done()
}

// Lifecycle
onMounted(async () => {
  await nextTick()
  
  // Initialize displayed stories
  displayedStories.value = stories.value
  
  // Generate initial prompts
  generateContextualPrompts()
  
  // Set up scroll listener
  window.addEventListener('scroll', handleScroll, { passive: true })
  
  // Load initial feed if needed
  if (stories.value.length === 0) {
    await feedStore.fetchFeed(props.pregnancyId)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  cancelAllAnimations()
})

// Watch for story updates
watch(stories, (newStories) => {
  displayedStories.value = newStories
}, { deep: true })

// Watch for context changes
watch([() => props.currentWeek, () => props.timeOfDay, () => props.familyActivity], () => {
  generateContextualPrompts()
})
</script>

<style scoped>
/* Feed journey base styles */
.feed-journey {
  padding: 1.5rem 1rem;
  min-height: 100vh;
}

/* Time-based styling */
.journey-morning {
  background: linear-gradient(to bottom, #FFF8E1 0%, #FFFFFF 20%);
}

.journey-afternoon {
  background: linear-gradient(to bottom, #F3E5F5 0%, #FFFFFF 15%);
}

.journey-evening {
  background: linear-gradient(to bottom, #FFF3E0 0%, #FFFFFF 25%);
}

.journey-night {
  background: linear-gradient(to bottom, #E8EAF6 0%, #F5F5F5 30%);
}

/* Loading state */
.loading-state {
  opacity: 0.8;
}

.story-skeleton {
  animation: gentle-pulse 2s ease-in-out infinite;
}

/* Empty state */
.empty-state {
  margin: 3rem 0;
}

.create-story-btn {
  box-shadow: 0 4px 12px rgba(248, 187, 208, 0.3);
}

.create-story-btn:hover {
  box-shadow: 0 6px 20px rgba(248, 187, 208, 0.4);
}

/* Story cards transitions */
.story-card-enter-active,
.story-card-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.story-card-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.story-card-leave-to {
  opacity: 0;
  transform: translateX(-20px) scale(0.95);
}

.story-card-move {
  transition: transform 0.4s ease;
}

/* Load more section */
.load-more-btn {
  min-width: 200px;
  transition: all 0.2s ease;
}

.load-more-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

/* Journey end */
.journey-end {
  opacity: 0.8;
}

/* Scroll to top button */
.scroll-top-btn {
  backdrop-filter: blur(8px);
}

.scroll-top-enter-active,
.scroll-top-leave-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.scroll-top-enter-from,
.scroll-top-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(10px);
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .feed-journey {
    padding: 1rem 0.5rem;
    max-width: 100%;
  }
  
  .journey-stories {
    space-y: 4rem;
  }
  
  .scroll-top-btn {
    bottom: 1rem;
    right: 1rem;
    padding: 0.75rem;
  }
}

/* Tablet optimizations */
@media (min-width: 641px) and (max-width: 1024px) {
  .feed-journey {
    max-width: 28rem;
  }
}

/* Desktop optimizations */
@media (min-width: 1025px) {
  .feed-journey {
    max-width: 32rem;
  }
  
  .journey-stories {
    space-y: 2rem;
  }
}

/* Animations */
@keyframes gentle-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .journey-morning,
  .journey-afternoon,
  .journey-evening,
  .journey-night {
    background: #fff;
  }
  
  .create-story-btn,
  .load-more-btn,
  .scroll-top-btn {
    background: #000;
    color: #fff;
    border: 2px solid #000;
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .story-skeleton,
  .loading-spinner,
  .story-card-enter-active,
  .story-card-leave-active,
  .scroll-top-enter-active,
  .scroll-top-leave-active {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
  
  .create-story-btn:hover,
  .load-more-btn:hover {
    transform: none;
  }
}

/* Print styles */
@media print {
  .scroll-top-btn,
  .load-more-btn {
    display: none !important;
  }
  
  .feed-journey {
    background: white !important;
    padding: 0 !important;
  }
}
</style>