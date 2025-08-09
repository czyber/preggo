<template>
  <div ref="timelineRef" class="feed-timeline w-full max-w-2xl mx-auto space-y-6">
    <!-- Feed Header with Filters -->
    <div ref="headerRef" class="sticky top-0 bg-off-white/95 backdrop-blur-sm z-20 pb-4 border-b border-light-gray/30">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold font-inter text-warm-graphite">
          Family Feed
        </h2>
        <div class="flex items-center gap-2">
          <FeedFilters
            :activeFilter="activeFilter"
            :sortBy="sortBy"
            :filters="availableFilters"
            @filter-change="handleFilterChange"
            @sort-change="handleSortChange"
          />
        </div>
      </div>
      
      <!-- Quick Stats -->
      <div v-if="familyEngagementStats" class="flex items-center gap-4 text-sm text-neutral-gray">
        <span>{{ totalCount }} posts</span>
        <span>{{ familyEngagementStats.totalReactions }} reactions</span>
        <span>{{ familyEngagementStats.totalComments }} comments</span>
        <span v-if="needsAttentionPosts.length" class="text-blush-rose font-medium">
          {{ needsAttentionPosts.length }} need attention
        </span>
      </div>
    </div>

    <!-- Celebrations Banner -->
    <div v-if="activeCelebrations.length" class="space-y-3">
      <MilestoneCelebration
        v-for="celebration in activeCelebrations"
        :key="celebration.post_id"
        :celebration="celebration"
        @dismiss="handleCelebrationDismiss"
      />
    </div>

    <!-- Feed Content -->
    <div class="feed-content space-y-6">
      <!-- Loading State -->
      <div v-if="loading && posts.length === 0" class="space-y-6">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <BaseCard class="p-6">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
              <div class="flex-1 space-y-3">
                <div class="h-4 bg-gray-200 rounded w-1/3"></div>
                <div class="space-y-2">
                  <div class="h-3 bg-gray-200 rounded"></div>
                  <div class="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
                <div class="flex space-x-4">
                  <div class="h-6 bg-gray-200 rounded w-16"></div>
                  <div class="h-6 bg-gray-200 rounded w-16"></div>
                  <div class="h-6 bg-gray-200 rounded w-16"></div>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && filteredPosts.length === 0" class="text-center py-12">
        <div class="max-w-md mx-auto bg-off-white rounded-lg p-6 shadow-sm border border-light-gray">
          <div class="space-y-4">
            <div class="text-4xl">👶</div>
            <h3 class="text-lg font-semibold font-inter text-warm-graphite">
              {{ getEmptyStateTitle() }}
            </h3>
            <p class="text-soft-charcoal text-sm">
              {{ getEmptyStateMessage() }}
            </p>
            <BaseButton
              v-if="activeFilter !== 'all'"
              @click="handleFilterChange('all')"
              variant="outline"
              size="sm"
            >
              View All Posts
            </BaseButton>
          </div>
          </div>
        </div>

      <!-- Posts -->
      <TransitionGroup
        v-else
        name="feed-item"
        tag="div"
        class="space-y-6 animate-stagger"
      >
        <FeedPostCard
          v-for="(post, index) in filteredPosts"
          :key="post.id"
          :post="post"
          :celebrations="getCelebrationsForPost(post.id)"
          :data-animation-delay="index * 100"
          @reaction="handleReaction"
          @removeReaction="handleRemoveReaction"
          @view="handleView"
          @comment="handleComment"
          @share="handleShare"
        />
      </TransitionGroup>

      <!-- Load More -->
      <div v-if="hasMore" class="flex justify-center py-8">
        <BaseButton
          @click="loadMore"
          :loading="loading"
          variant="outline"
          class="min-w-32"
        >
          {{ loading ? 'Loading...' : 'Load More Posts' }}
        </BaseButton>
      </div>

      <!-- End of Feed -->
      <div v-else-if="filteredPosts.length > 0" class="text-center py-8 text-neutral-gray text-sm">
        <div class="flex items-center justify-center gap-2">
          <div class="w-8 h-px bg-light-gray"></div>
          <span>You're all caught up!</span>
          <div class="w-8 h-px bg-light-gray"></div>
        </div>
      </div>
    </div>

    <!-- Scroll to Top -->
    <Transition name="fade">
      <button
        v-if="showScrollToTop"
        ref="scrollTopBtnRef"
        @click="scrollToTop"
        class="fixed bottom-6 right-6 z-30 p-3 bg-sage-green text-white rounded-full shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105"
        aria-label="Scroll to top"
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
import { useFeedStore } from "~/stores/feed"
import { cn } from '~/components/ui/utils'
import { useScrollAnimation, useFeedAnimations, useGentleTransitions } from '~/composables/useAnimations'

interface Props {
  pregnancyId?: string
  initialFilter?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialFilter: 'all'
})

const emit = defineEmits<{
  postInteraction: [{ type: string, postId: string, data?: any }]
  filterChanged: [{ filter: string, count: number }]
  celebrationViewed: [{ celebrationId: string, postId: string }]
}>()

// Store
const feedStore = useFeedStore()

// Animation composables
const { animateOnScroll, observeElement } = useScrollAnimation()
const { animateTimelineItem } = useFeedAnimations()
const { createGentleHover, animateElementIn } = useGentleTransitions()

// Reactive store state
const {
  posts,
  filteredPosts,
  celebrations,
  loading,
  error,
  hasMore,
  totalCount,
  activeFilter,
  sortBy,
  needsAttentionPosts,
  familyEngagementStats
} = storeToRefs(feedStore)

// Remove debug code

// Local state
const showScrollToTop = ref(false)
const timelineRef = ref<HTMLElement>()
const headerRef = ref<HTMLElement>()
const scrollTopBtnRef = ref<HTMLElement>()
const availableFilters = ref([
  { value: 'all', label: 'All Posts', count: 0 },
  { value: 'milestones', label: 'Milestones', count: 0 },
  { value: 'photos', label: 'Photos', count: 0 },
  { value: 'updates', label: 'Updates', count: 0 },
  { value: 'celebrations', label: 'Celebrations', count: 0 },
  { value: 'recent', label: 'Recent', count: 0 },
])

// Computed
const activeCelebrations = computed(() => {
  return celebrations.value.filter(cel => cel.is_new).slice(0, 2)
})

// Methods
function getCelebrationsForPost(postId: string) {
  return celebrations.value.filter(cel => cel.post_id === postId)
}

function getEmptyStateTitle() {
  switch (activeFilter.value) {
    case 'milestones': return 'No Milestones Yet'
    case 'photos': return 'No Photos Shared'
    case 'updates': return 'No Updates Posted'
    case 'celebrations': return 'No Celebrations'
    case 'recent': return 'No Recent Posts'
    default: return 'Welcome to Your Family Feed'
  }
}

function getEmptyStateMessage() {
  switch (activeFilter.value) {
    case 'milestones': return 'Milestone posts will appear here as your pregnancy progresses.'
    case 'photos': return 'Share photos of your pregnancy journey with your family.'
    case 'updates': return 'Share updates about how you\'re feeling and what\'s happening.'
    case 'celebrations': return 'Special moments and achievements will be celebrated here.'
    case 'recent': return 'No posts in the last few days. Share an update!'
    default: return 'Start sharing your pregnancy journey with your loved ones.'
  }
}

async function handleFilterChange(filter: string) {
  await feedStore.updateFilter(filter as any)
  emit('filterChanged', { filter, count: filteredPosts.value.length })
}

function handleSortChange(sort: string) {
  feedStore.updateSort(sort as any)
}

async function handleReaction(data: { postId: string, reactionType: string }) {
  try {
    await feedStore.addReaction(data.postId, data.reactionType as any)
    emit('postInteraction', { type: 'reaction', postId: data.postId, data })
  } catch (error) {
    console.error('Failed to add reaction:', error)
  }
}

async function handleRemoveReaction(postId: string) {
  try {
    await feedStore.removeReaction(postId)
    emit('postInteraction', { type: 'reaction', postId, data: { isRemoving: true } })
  } catch (error) {
    console.error('Failed to remove reaction:', error)
  }
}

async function handleView(postId: string) {
  await feedStore.recordView(postId)
  emit('postInteraction', { type: 'view', postId })
}

function handleComment(postId: string) {
  emit('postInteraction', { type: 'comment', postId })
}

function handleShare(postId: string) {
  emit('postInteraction', { type: 'share', postId })
}

function handleCelebrationDismiss(celebrationId: string) {
  const index = celebrations.value.findIndex(cel => cel.post_id === celebrationId)
  if (index !== -1) {
    celebrations.value[index].is_new = false
  }
}

async function loadMore() {
  await feedStore.loadMore()
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Scroll handler
function handleScroll() {
  showScrollToTop.value = window.scrollY > 500
}

// Lifecycle
onMounted(async () => {
  // Set up animations first
  await nextTick()
  
  if (timelineRef.value) {
    // Set up scroll animation for timeline items
    const postCards = timelineRef.value.querySelectorAll('.feed-post-card')
    postCards.forEach((card, index) => {
      animateTimelineItem(card as HTMLElement, index)
    })
    
    // Animate timeline entry
    animateElementIn(timelineRef.value, 'fadeInUp', 'supportive')
  }
  
  if (headerRef.value) {
    // Animate header
    animateElementIn(headerRef.value, 'fadeInScale', 'gentle')
    
    // Add hover effects to interactive elements in header
    const buttons = headerRef.value.querySelectorAll('button')
    buttons.forEach(button => {
      createGentleHover(button as HTMLElement, 'lift')
    })
  }
  
  if (scrollTopBtnRef.value) {
    createGentleHover(scrollTopBtnRef.value, 'celebration')
  }
  
  // Initial filter setup
  if (props.initialFilter !== 'all') {
    await handleFilterChange(props.initialFilter)
  } else {
    await feedStore.fetchFeed(props.pregnancyId)
  }

  // Fetch additional data
  await Promise.all([
    feedStore.fetchFeedFilters(),
    feedStore.fetchCelebrations(props.pregnancyId)
  ])

  // Set up scroll listener
  window.addEventListener('scroll', handleScroll)

})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// Watch for pregnancy ID changes
watch(() => props.pregnancyId, async (newId) => {
  if (newId) {
    feedStore.reset()
    await feedStore.fetchFeed(newId)
    await feedStore.fetchCelebrations(newId)
  }
})
</script>

<style scoped>
/* Feed item transitions */
.feed-item-enter-active,
.feed-item-leave-active {
  transition: all 0.3s ease;
}

.feed-item-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.feed-item-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.feed-item-move {
  transition: transform 0.3s ease;
}

/* Smooth scrolling enhancement */
.feed-timeline {
  scroll-behavior: smooth;
}

/* Backdrop blur support */
@supports (backdrop-filter: blur(8px)) {
  .sticky {
    backdrop-filter: blur(8px);
  }
}

/* Feed content spacing optimization for mobile */
@media (max-width: 640px) {
  .feed-content {
    padding: 0 1rem;
  }
  
  .feed-timeline {
    max-width: 100%;
  }
}

/* Animation for scroll to top button */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Enhanced loading skeleton */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>
