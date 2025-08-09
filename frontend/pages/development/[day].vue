<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Navigation Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-4">
            <button 
              @click="$router.back()"
              class="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 class="text-xl font-semibold text-gray-900">Baby Development</h1>
          </div>
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <span>{{ formatWeekDay(currentWeek, currentDay) }}</span>
            <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
            <span>{{ trimesterInfo.name }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>

      <div v-else class="space-y-8">
        <!-- Hero Section -->
        <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-pink-100 to-pink-200">
          <!-- Removed floating particles for cleaner design -->

          <div class="relative px-8 py-12">
            <div class="text-center text-gray-900">
              <div class="text-8xl mb-6">{{ sizeComparison.icon }}</div>
              <h2 class="text-3xl font-bold mb-2">{{ formatWeekDay(currentWeek, currentDay) }}</h2>
              <p class="text-xl text-gray-700 mb-4">{{ sizeComparison.description }}</p>
              <div class="flex items-center justify-center space-x-6">
                <div class="text-center">
                  <div class="text-2xl font-bold">{{ Math.round(developmentStats.progressPercentage) }}%</div>
                  <div class="text-sm text-gray-600">Complete</div>
                </div>
                <div class="w-px h-8 bg-gray-300"></div>
                <div class="text-center">
                  <div class="text-2xl font-bold">{{ getWeeksUntilDue() }}</div>
                  <div class="text-sm text-gray-600">Weeks to go</div>
                </div>
                <div class="w-px h-8 bg-gray-300"></div>
                <div class="text-center">
                  <div class="text-2xl font-bold">{{ currentWeekData?.weight || 'Growing' }}</div>
                  <div class="text-sm text-gray-600">Baby's weight</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="absolute bottom-0 left-0 right-0 h-2 bg-gray-200">
            <div 
              class="h-full bg-pink-500 transition-all duration-1000 ease-out"
              :style="{ width: developmentStats.progressPercentage + '%' }"
            ></div>
          </div>
        </div>

        <!-- Main Development Card -->
        <div class="grid lg:grid-cols-3 gap-8">
          <!-- Enhanced Baby Development Card -->
          <div class="lg:col-span-2">
            <BabyDevelopmentCard 
              :current-week="currentWeek"
              :current-day="currentDay"
              :pregnancy-day="pregnancyDay"
              @open-detail="showDetailModal = true"
              class="h-full"
            />
          </div>

          <!-- Quick Stats -->
          <div class="space-y-6">
            <!-- Trimester Info -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 class="font-semibold mb-4 text-pink-600">
                {{ trimesterInfo.name }}
              </h3>
              <p class="text-gray-600 text-sm mb-4">{{ trimesterInfo.description }}</p>
              <div class="space-y-3">
                <div 
                  v-for="milestone in trimesterInfo.keyMilestones.slice(0, 3)" 
                  :key="milestone"
                  class="flex items-start text-sm"
                >
                  <div class="w-2 h-2 rounded-full mr-3 mt-2 flex-shrink-0 bg-pink-500"></div>
                  <span class="text-gray-700">{{ milestone }}</span>
                </div>
              </div>
            </div>

            <!-- Recommendations -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 class="font-semibold mb-4 text-gray-900">This Week's Tips</h3>
              <div class="space-y-3">
                <div 
                  v-for="(recommendation, index) in recommendations.slice(0, 3)" 
                  :key="index"
                  class="flex items-start text-sm"
                >
                  <svg class="w-4 h-4 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">{{ recommendation }}</span>
                </div>
              </div>
            </div>

            <!-- Important Milestones -->
            <div v-if="isViabilityReached() || isFullTerm()" class="bg-green-50 rounded-xl border border-green-200 p-6">
              <div class="flex items-center mb-3">
                <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <h3 class="font-semibold text-green-800">
                  {{ isFullTerm() ? 'Full Term!' : 'Viability Milestone!' }}
                </h3>
              </div>
              <p class="text-sm text-green-700">
                {{ isFullTerm() 
                  ? 'Your baby is now considered full-term and ready for delivery!' 
                  : 'Your baby has reached the viability milestone - they could survive outside the womb with medical support.'
                }}
              </p>
            </div>
          </div>
        </div>

        <!-- Timeline Navigation -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="font-semibold mb-6 text-gray-900">Navigate Development Timeline</h3>
          
          <!-- Week selector -->
          <div class="mb-6">
            <div class="flex items-center justify-center space-x-4 mb-4">
              <button 
                @click="navigateToWeek(currentWeek - 1)"
                :disabled="currentWeek <= 1"
                class="flex items-center px-4 py-2 rounded-lg transition-colors duration-200"
                :class="[
                  currentWeek <= 1 
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                ]"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Previous Week
              </button>
              
              <div class="text-center px-4">
                <div class="text-sm text-gray-500">Current</div>
                <div class="font-semibold text-pink-600">Week {{ currentWeek }}</div>
              </div>
              
              <button 
                @click="navigateToWeek(currentWeek + 1)"
                :disabled="currentWeek >= 40"
                class="flex items-center px-4 py-2 rounded-lg transition-colors duration-200"
                :class="[
                  currentWeek >= 40 
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                ]"
              >
                Next Week
                <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            <!-- Visual timeline -->
            <div class="relative">
              <div class="absolute top-2 left-0 right-0 h-1 bg-gray-200 rounded"></div>
              <div 
                class="absolute top-2 left-0 h-1 rounded transition-all duration-500 bg-pink-400"
                :style="{ width: (currentWeek / 40) * 100 + '%' }"
              ></div>
              <div class="flex justify-between items-center">
                <div 
                  v-for="week in [1, 10, 20, 30, 40]" 
                  :key="week"
                  class="flex flex-col items-center"
                >
                  <div 
                    class="w-4 h-4 rounded-full border-2 transition-all duration-300"
                    :class="[
                      currentWeek >= week 
                        ? 'bg-pink-400 border-white shadow-md' 
                        : 'bg-white border-gray-300'
                    ]"
                  ></div>
                  <span class="text-xs text-gray-500 mt-2">{{ week }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Development Insights -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="font-semibold mb-6 text-gray-900">Development Insights</h3>
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="(insight, index) in developmentInsights.slice(0, 6)" 
              :key="index"
              class="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-all duration-200"
              :class="{
                'bg-red-50 border-red-200': insight.priority === 'high',
                'bg-yellow-50 border-yellow-200': insight.priority === 'medium',
                'bg-blue-50 border-blue-200': insight.priority === 'low'
              }"
            >
              <div class="flex items-start">
                <div 
                  class="w-2 h-2 rounded-full mr-3 mt-2 flex-shrink-0"
                  :class="{
                    'bg-red-400': insight.priority === 'high',
                    'bg-yellow-400': insight.priority === 'medium',
                    'bg-blue-400': insight.priority === 'low'
                  }"
                ></div>
                <div>
                  <h4 class="font-medium text-sm mb-1 text-gray-900">{{ insight.title }}</h4>
                  <p class="text-xs text-gray-600">{{ insight.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Development Detail Modal -->
    <BabyDevelopmentDetail
      :is-open="showDetailModal"
      :current-week="currentWeek"
      :current-day="currentDay"
      :pregnancy-day="pregnancyDay"
      @close="showDetailModal = false"
      @week-changed="handleWeekChange"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()

// Get the day parameter from the route
const routeDay = computed(() => {
  const day = route.params.day
  if (typeof day === 'string') {
    return parseInt(day, 10)
  }
  return 1
})

// Use the baby development composable
const {
  currentPregnancyWeek,
  currentPregnancyDay,
  pregnancyDay,
  currentWeekData,
  trimesterInfo,
  developmentStats,
  sizeComparison,
  isLoading,
  formatWeekDay,
  getDaysUntilDue,
  getWeeksUntilDue,
  isViabilityReached,
  isFullTerm,
  getDevelopmentInsights,
  getRecommendations,
  syncWithPregnancyData
} = useBabyDevelopment()

// Local state
const showDetailModal = ref(false)
// Removed heroParticles - no longer needed for cleaner design

// Computed properties
const currentWeek = computed(() => {
  // Convert pregnancy day to week
  const week = Math.floor(routeDay.value / 7)
  return Math.max(1, Math.min(week, 40))
})

const currentDay = computed(() => {
  return routeDay.value % 7
})

const developmentInsights = computed(() => {
  return getDevelopmentInsights(currentWeek.value)
})

const recommendations = computed(() => {
  return getRecommendations(currentWeek.value)
})

// Methods
const navigateToWeek = (week: number) => {
  if (week >= 1 && week <= 40) {
    const day = (week - 1) * 7 + 1 // Convert week to pregnancy day
    router.push(`/development/${day}`)
  }
}

const handleWeekChange = (week: number) => {
  navigateToWeek(week)
  showDetailModal.value = false
}

// Removed generateHeroParticles function for cleaner design

// Lifecycle
onMounted(() => {
  syncWithPregnancyData()
})

// Watch for route changes - removed particle generation

// SEO
const weekData = currentWeekData.value
useSeoMeta({
  title: `Week ${currentWeek.value} Baby Development | Pregnancy Journey`,
  description: weekData 
    ? `Discover what's happening in week ${currentWeek.value} of your pregnancy. ${weekData.description.substring(0, 150)}...`
    : `Track your baby's development in week ${currentWeek.value} of pregnancy with detailed milestones and insights.`
})
</script>

<style scoped>
@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-20px) scale(1.2);
    opacity: 0.9;
  }
}

.animate-float {
  animation: float linear infinite;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .grid.lg\\:grid-cols-3 {
    grid-template-columns: 1fr;
  }
  
  .grid.md\\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .text-8xl {
    font-size: 4rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .animate-float,
  .animate-pulse,
  .transition-all {
    animation: none;
    transition: none;
  }
}

/* Enhanced hover effects */
.hover\\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>