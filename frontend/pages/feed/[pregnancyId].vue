<template>
  <div class="feed-page min-h-screen bg-gradient-to-br from-warm-neutral/20 via-white to-gentle-mint/10">
    <!-- Navigation Header -->
    <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-warm-neutral/30 shadow-sm">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Left Side - Back Button & Title -->
          <div class="flex items-center gap-4">
            <button
              @click="handleGoBack"
              class="p-2 hover:bg-gray-100 rounded-full transition-colors lg:hidden"
              aria-label="Go back"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <div>
              <h1 class="text-xl font-bold text-gray-900 font-primary">
                {{ getPageTitle() }}
              </h1>
              <p v-if="currentPregnancy" class="text-sm text-gray-600">
                Week {{ currentPregnancy.pregnancy_details?.current_week }} • Trimester {{ currentPregnancy.pregnancy_details?.trimester }}
              </p>
            </div>
          </div>

          <!-- Right Side - User Menu -->
          <div class="flex items-center gap-3">
            <!-- Notifications -->
            <button
              @click="toggleNotifications"
              class="relative p-2 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Notifications"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 -5l5 -5h-5m-6 10v-5a6 6 0 1 1 12 0v5" />
              </svg>
              <div v-if="unreadNotifications > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-soft-pink text-white text-xs rounded-full flex items-center justify-center font-medium">
                {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
              </div>
            </button>

            <!-- User Profile -->
            <div class="relative">
              <button
                @click="toggleUserMenu"
                class="flex items-center gap-2 p-1 hover:bg-gray-100 rounded-full transition-colors"
                aria-label="User menu"
              >
                <UserAvatar :user="user" size="md" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar - Family & Quick Stats -->
        <aside class="lg:col-span-1 space-y-6">
          <!-- Family Members Card -->
          <BaseCard variant="warm" class="p-4">
            <template #header>
              <h2 class="font-semibold text-gray-800 text-sm flex items-center gap-2">
                <span class="text-base">👨‍👩‍👧‍👦</span>
                Family Circle
              </h2>
            </template>
            
            <div v-if="familyMembers.length > 0" class="space-y-4">
              <div
                v-for="member in familyMembers.slice(0, 5)"
                :key="member.id"
                class="flex items-center gap-3"
              >
                <div class="w-6 h-6 bg-gentle-mint/30 rounded-full flex items-center justify-center text-xs font-semibold text-gentle-mint-dark">
                  {{ member.display_name?.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-800 truncate">
                    {{ member.display_name }}
                  </div>
                  <div class="text-xs text-gray-500 truncate">
                    {{ member.relationship || 'Family' }}
                  </div>
                </div>
                <div v-if="member.is_online" class="w-2 h-2 bg-green-400 rounded-full" title="Online" />
              </div>
              
              <button
                v-if="familyMembers.length > 5"
                @click="showAllFamily"
                class="text-sm text-soft-pink hover:text-soft-pink/80 font-medium"
              >
                View all {{ familyMembers.length }} members
              </button>
            </div>
            
            <div v-else class="text-center py-4 text-gray-500 text-sm">
              <div class="text-2xl mb-2">👥</div>
              <p>No family members yet</p>
              <button
                @click="inviteFamily"
                class="mt-2 text-soft-pink hover:text-soft-pink/80 text-sm font-medium"
              >
                Invite Family
              </button>
            </div>
          </BaseCard>

          <!-- Quick Actions -->
          <BaseCard variant="supportive" class="p-4">
            <template #header>
              <h2 class="font-semibold text-gray-800 text-sm flex items-center gap-2">
                <span class="text-base">✨</span>
                Share Your Journey
              </h2>
            </template>
            
            <div class="space-y-3">
              <BaseButton
                variant="default"
                size="sm"
                class="w-full"
                @click="createPost"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Create Post
              </BaseButton>
              
              <BaseButton
                variant="outline"
                size="sm"
                class="w-full"
                @click="addPhoto"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                </svg>
                Share Photo
              </BaseButton>
            </div>
          </BaseCard>

          <!-- Upcoming Milestones -->
          <BaseCard v-if="upcomingMilestones.length > 0" variant="milestone" class="p-4">
            <template #header>
              <h2 class="font-semibold text-gray-800 text-sm flex items-center gap-2">
                <span class="text-base">✨</span>
                Upcoming Milestones
              </h2>
            </template>
            
            <div class="space-y-2">
              <div
                v-for="milestone in upcomingMilestones.slice(0, 3)"
                :key="milestone.id"
                class="p-2 bg-white/40 rounded-lg text-sm"
              >
                <div class="font-medium text-gray-800">
                  Week {{ milestone.pregnancy_context?.current_week }}
                </div>
                <div class="text-xs text-gray-600 mt-1">
                  {{ milestone.pregnancy_context?.baby_development }}
                </div>
              </div>
            </div>
          </BaseCard>
        </aside>

        <!-- Main Feed Content -->
        <div class="lg:col-span-3">
          <!-- Loading State -->
          <div v-if="pageLoading" class="space-y-6">
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
                  </div>
                </div>
              </BaseCard>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="text-center py-12">
            <BaseCard variant="warm" class="max-w-md mx-auto">
              <div class="space-y-4">
                <div class="text-4xl">⚠️</div>
                <h3 class="text-lg font-semibold font-primary text-gray-800">
                  Oops! Something went wrong
                </h3>
                <p class="text-gray-600 text-sm">
                  {{ error }}
                </p>
                <BaseButton
                  @click="handleRetry"
                  variant="outline"
                  size="sm"
                >
                  Try Again
                </BaseButton>
              </div>
            </BaseCard>
          </div>

          <!-- Empty State for No Posts -->
          <div v-else-if="!loading && feedStore.filteredPosts.length === 0" class="text-center py-16">
            <BaseCard variant="warm" class="max-w-md mx-auto">
              <div class="space-y-6">
                <div class="text-6xl">📝</div>
                <div>
                  <h3 class="text-xl font-semibold font-primary text-gray-800 mb-2">
                    Start Your Pregnancy Story
                  </h3>
                  <p class="text-gray-600 font-secondary">
                    Share your first pregnancy update with your family. Document this special journey!
                  </p>
                </div>
                <div class="space-y-3">
                  <BaseButton
                    variant="default"
                    size="lg"
                    @click="createPost"
                    class="w-full"
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    Create Your First Post
                  </BaseButton>
                  <BaseButton
                    variant="outline"
                    size="default"
                    @click="addPhoto"
                    class="w-full"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                    </svg>
                    Share a Photo
                  </BaseButton>
                </div>
              </div>
            </BaseCard>
          </div>

          <!-- Feed Timeline -->
          <FeedTimeline
            v-else
            :pregnancy-id="pregnancyId"
            @postInteraction="handlePostInteraction"
          />
        </div>
      </div>
    </main>

    <!-- Floating Action Button -->
    <button
      @click="createPost"
      class="fixed bottom-6 right-6 z-20 w-14 h-14 bg-gradient-to-r from-soft-pink to-gentle-mint text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
      aria-label="Create new post"
    >
      <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>

    <!-- Modals and Overlays -->
    <Teleport to="body">
      <!-- Notifications Panel -->
      <div
        v-if="showNotifications"
        class="fixed inset-0 z-50 lg:inset-auto lg:top-16 lg:right-4 lg:w-80"
      >
        <div class="absolute inset-0 bg-black/20 lg:hidden" @click="closeNotifications" />
        <div class="relative bg-white rounded-lg shadow-xl border border-gray-100 h-full lg:h-auto lg:max-h-96 overflow-hidden">
          <!-- Notifications content would go here -->
          <div class="p-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-800">Notifications</h3>
          </div>
          <div class="p-4 text-center text-gray-500 text-sm">
            No new notifications
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFeedStore } from "@/stores/feed"
import { usePregnancyStore } from "@/stores/pregnancy"
import { useFamilyStore } from "@/stores/family"
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import FeedTimeline from '~/components/feed/FeedTimeline.vue'

// Composables
const route = useRoute()
const router = useRouter()
const { user, isAuthenticated } = useAuth()
const { showToast } = useToast()

// Stores
const feedStore = useFeedStore()
const pregnancyStore = usePregnancyStore()
const familyStore = useFamilyStore()

// Reactive store state
const {
  loading,
  error,
  upcomingMilestones
} = storeToRefs(feedStore)

const { currentPregnancy } = storeToRefs(pregnancyStore)
const { familyMembers } = storeToRefs(familyStore)

// Local state
const pageLoading = ref(true)
const showNotifications = ref(false)
const showUserMenu = ref(false)
const unreadNotifications = ref(0)

// Route params
const pregnancyId = computed(() => route.params.pregnancyId as string)

// Computed properties
const getPageTitle = () => {
  if (currentPregnancy.value) {
    return `${currentPregnancy.value.pregnancy_details?.current_week ? `Week ${currentPregnancy.value.pregnancy_details.current_week}` : 'Family'} Feed`
  }
  return 'Family Feed'
}

// Helper methods for FeedJourney component
const getUserName = () => {
  return user.value?.display_name || user.value?.first_name || 'You'
}

const getCurrentWeek = () => {
  return currentPregnancy.value?.pregnancy_details?.current_week || 0
}

const getBabyDevelopment = () => {
  return currentPregnancy.value?.pregnancy_details?.baby_development || ''
}

const getUserMood = () => {
  // This could come from recent posts or user settings
  return undefined // TODO: Implement mood tracking
}

const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' | 'night' => {
  const hour = new Date().getHours()
  if (hour < 12) return 'morning'
  if (hour < 17) return 'afternoon'
  if (hour < 21) return 'evening'
  return 'night'
}

const getFamilyActivity = (): 'high' | 'medium' | 'low' => {
  // Based on recent family member activity
  const recentlyActive = familyMembers.value.filter(member => member.is_online).length
  if (recentlyActive >= 3) return 'high'
  if (recentlyActive >= 1) return 'medium'
  return 'low'
}


// Methods
async function initializePage() {
  try {
    pageLoading.value = true
    
    // Fetch all data in parallel for better performance
    const promises = []
    
    if (pregnancyId.value) {
      promises.push(pregnancyStore.fetchPregnancyById(pregnancyId.value))
      promises.push(familyStore.fetchFamilyMembersByPregnancy(pregnancyId.value))
      promises.push(feedStore.fetchFeed(pregnancyId.value))
    }
    
    // Wait for all parallel requests to complete
    await Promise.allSettled(promises)
    
  } catch (err) {
    console.error('Failed to initialize feed page:', err)
    showToast({
      title: 'Error',
      description: 'Failed to load feed. Please try again.',
      type: 'error'
    })
  } finally {
    pageLoading.value = false
  }
}

function handleGoBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

function handlePostInteraction(interaction: { type: string, postId: string, data?: any }) {
  console.log('Post interaction:', interaction)
  
  // Handle different interaction types
  switch (interaction.type) {
    case 'reaction':
      if (interaction.data?.isRemoving) {
        feedStore.removeReaction(interaction.postId)
      } else {
        feedStore.addReaction(interaction.postId, interaction.data?.reactionType || 'love')
      }
      showToast({
        title: interaction.data?.isRemoving ? 'Love removed' : 'Love shared! 💕',
        description: interaction.data?.isRemoving ? 'Your love has been removed.' : 'Your family will feel the love you shared.',
        type: 'success'
      })
      break
    case 'comment':
      // Navigate to post detail or open comment modal
      break
    case 'share':
      handleShare(interaction.postId)
      break
  }
}

async function handleShare(postId: string) {
  try {
    const shareUrl = `${window.location.origin}/feed/${route.params.pregnancyId}/post/${postId}`
    const shareData = {
      title: 'Pregnancy Update',
      text: 'Check out this pregnancy milestone!',
      url: shareUrl
    }

    if (navigator.share && navigator.canShare?.(shareData)) {
      await navigator.share(shareData)
      showToast({
        title: 'Beautiful moment shared! ✨',
        description: 'Your precious memory will bring joy to your loved ones.',
        type: 'success'
      })
    } else {
      await navigator.clipboard.writeText(shareUrl)
      showToast({
        title: 'Link ready to share! 🔗',
        description: 'Spread the joy by sharing this special moment.',
        type: 'success'
      })
    }
  } catch (error) {
    console.error('Failed to share:', error)
    // Fallback to copying link
    try {
      const shareUrl = `${window.location.origin}/feed/${route.params.pregnancyId}/post/${postId}`
      await navigator.clipboard.writeText(shareUrl)
      showToast({
        title: 'Link ready to share! 🔗',
        description: 'Spread the joy by sharing this special moment.',
        type: 'success'
      })
    } catch (clipboardError) {
      showToast({
        title: 'Sharing needs a little help',
        description: 'Please copy the link from your browser to share this moment.',
        type: 'info'
      })
    }
  }
}

function handleFilterChanged(filterData: { filter: string, count: number }) {
  // Update URL with filter parameter
  if (filterData.filter !== 'all') {
    router.replace({ 
      ...route, 
      query: { ...route.query, filter: filterData.filter } 
    })
  } else {
    const query = { ...route.query }
    delete query.filter
    router.replace({ ...route, query })
  }
}

function handleCelebrationViewed(celebrationData: { celebrationId: string, postId: string }) {
  console.log('Celebration viewed:', celebrationData)
}

function handleMemoryPromptAction(data: { action: string, data?: any }) {
  console.log('Memory prompt action:', data)
  
  switch (data.action) {
    case 'take_photo':
      router.push(`/posts/create?pregnancyId=${pregnancyId.value}&type=photo&prompt=weekly`)
      break
    case 'celebrate':
      router.push(`/posts/create?pregnancyId=${pregnancyId.value}&type=milestone&week=${getCurrentWeek()}`)
      break
    case 'ask_family':
      router.push(`/posts/create?pregnancyId=${pregnancyId.value}&type=question&prompt=family`)
      break
    case 'write_reflection':
      router.push(`/posts/create?pregnancyId=${pregnancyId.value}&type=journal&prompt=reflection`)
      break
    case 'create_first_story':
      router.push(`/posts/create?pregnancyId=${pregnancyId.value}`)
      break
    default:
      console.log('Unknown memory prompt action:', data.action)
  }
}

function toggleNotifications() {
  showNotifications.value = !showNotifications.value
  showUserMenu.value = false
}

function closeNotifications() {
  showNotifications.value = false
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

function showAllFamily() {
  router.push(`/family/${pregnancyId.value}`)
}

function inviteFamily() {
  router.push(`/family/${pregnancyId.value}/invite`)
}

function createPost() {
  router.push(`/posts/create?pregnancyId=${pregnancyId.value}`)
}

function addPhoto() {
  router.push(`/posts/create?pregnancyId=${pregnancyId.value}&type=photo`)
}

function handleRetry() {
  initializePage()
}

// Lifecycle
onMounted(async () => {
  // Check authentication
  if (!isAuthenticated.value) {
    router.push('/auth/login')
    return
  }
  
  await initializePage()
})

// Watch for pregnancy ID changes
watch(() => pregnancyId.value, async (newId) => {
  if (newId && isAuthenticated.value) {
    await initializePage()
  }
})


// Meta tags
useHead({
  title: computed(() => getPageTitle()),
  meta: [
    {
      name: 'description',
      content: computed(() => 
        currentPregnancy.value 
          ? `Follow along with the pregnancy journey - Week ${currentPregnancy.value.pregnancy_details?.current_week}`
          : 'Family pregnancy feed - sharing the journey together'
      )
    }
  ]
})

// Define page middleware
definePageMeta({
  middleware: 'auth',
  layout: 'default'
})
</script>

<style scoped>
/* Page-specific animations */
.feed-page {
  animation: page-appear 0.6s ease-out;
}

@keyframes page-appear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header backdrop blur */
@supports (backdrop-filter: blur(8px)) {
  header {
    backdrop-filter: blur(8px);
  }
}

/* Floating action button pulse animation */
.fixed.bottom-6.right-6 {
  animation: fab-appear 0.5s ease-out 1s both;
}

@keyframes fab-appear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Sidebar cards stagger animation */
aside > div:nth-child(1) { animation: card-appear 0.4s ease-out 0.2s both; }
aside > div:nth-child(2) { animation: card-appear 0.4s ease-out 0.3s both; }
aside > div:nth-child(3) { animation: card-appear 0.4s ease-out 0.4s both; }

@keyframes card-appear {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive grid improvements */
@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  aside {
    order: 2;
  }
  
  .lg\:col-span-3 {
    order: 1;
  }
}

/* Mobile header adjustments */
@media (max-width: 640px) {
  header .max-w-6xl {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .feed-page main {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 1.5rem;
  }
}

/* Loading skeleton improvements */
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

/* Notification panel animation */
.fixed.inset-0 > .relative {
  animation: notification-appear 0.3s ease-out;
}

@keyframes notification-appear {
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
button:focus,
a:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Enhanced grid gap for larger screens */
@media (min-width: 1280px) {
  .grid {
    gap: 2rem;
  }
}
</style>
