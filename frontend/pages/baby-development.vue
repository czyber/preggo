<template>
  <div class="min-h-screen bg-white">
    <!-- Hero Section with Current Pregnancy Info -->
    <div class="relative overflow-hidden bg-gradient-to-r from-pink-50 to-pink-100">
      <div class="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 sm:text-4xl md:text-5xl">
            Your Baby's Development
          </h1>
          <p class="mt-3 max-w-md mx-auto text-base text-gray-700 sm:text-lg md:mt-5 md:text-xl md:max-w-2xl">
            {{ formatWeekDay(currentWeek, currentDay) }} of pregnancy
          </p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
      </div>
      
      <div v-else-if="!currentPregnancy" class="text-center py-12">
        <div class="text-gray-600 mb-4">No active pregnancy found</div>
        <NuxtLink 
          to="/"
          class="px-4 py-2 bg-pink-500 text-white rounded-md hover:bg-pink-600"
        >
          Create Pregnancy
        </NuxtLink>
      </div>

      <div v-else class="space-y-8">
        <!-- Progress Indicator -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900">Pregnancy Progress</h2>
            <span class="text-2xl font-bold" :class="trimesterInfo.colorScheme.text">
              {{ Math.round(progressPercentage) }}%
            </span>
          </div>
          
          <div class="w-full bg-gray-100 rounded-full h-3 mb-4">
            <div 
              class="h-3 rounded-full transition-all duration-500 bg-pink-400"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
          
          <div class="flex justify-between text-sm text-gray-600">
            <span>{{ trimesterInfo.name }}</span>
            <span>{{ weeksUntilDue }} weeks until due date</span>
          </div>
        </div>

        <!-- Current Week Info -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <div class="flex items-start gap-6">
            <div class="text-6xl" v-if="sizeComparison.icon">{{ sizeComparison.icon }}</div>
            
            <div class="flex-1">
              <h2 class="text-xl font-semibold text-gray-900 mb-2">
                Week {{ currentWeek }}
              </h2>
              <p class="text-gray-600 mb-4" v-if="currentWeekData">
                {{ currentWeekData.description }}
              </p>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div class="bg-pink-50 rounded-lg p-3">
                  <div class="font-medium text-gray-900">Baby Size</div>
                  <div class="text-gray-600">{{ sizeComparison.item }}</div>
                </div>
                <div class="bg-pink-50 rounded-lg p-3" v-if="currentWeekData">
                  <div class="font-medium text-gray-900">Weight</div>
                  <div class="text-gray-600">{{ currentWeekData.weight }}</div>
                </div>
                <div class="bg-pink-50 rounded-lg p-3" v-if="currentWeekData">
                  <div class="font-medium text-gray-900">Length</div>
                  <div class="text-gray-600">{{ currentWeekData.length }}cm</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Development Milestones -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6" v-if="currentWeekData">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">This Week's Milestones</h3>
          <ul class="space-y-2">
            <li 
              v-for="milestone in currentWeekData.milestones" 
              :key="milestone"
              class="flex items-start gap-3"
            >
              <div class="w-2 h-2 bg-pink-500 rounded-full mt-2"></div>
              <span class="text-gray-700">{{ milestone }}</span>
            </li>
          </ul>
        </div>

        <!-- Baby and Mom Highlights -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6" v-if="currentWeekData">
          <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              👶 For Baby
            </h3>
            <ul class="space-y-2">
              <li 
                v-for="highlight in currentWeekData.babyHighlights" 
                :key="highlight"
                class="flex items-start gap-3"
              >
                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <span class="text-gray-700">{{ highlight }}</span>
              </li>
            </ul>
          </div>

          <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              🤱 For Mom
            </h3>
            <ul class="space-y-2">
              <li 
                v-for="highlight in currentWeekData.momHighlights" 
                :key="highlight"
                class="flex items-start gap-3"
              >
                <div class="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                <span class="text-gray-700">{{ highlight }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { usePregnancyStore } from '~/stores/pregnancy'
import { useBabyDevelopment } from '~/composables/useBabyDevelopment'

// Meta
definePageMeta({
  title: 'Baby Development',
  description: 'Track your baby\'s development week by week'
})

// Store and composable setup
const pregnancyStore = usePregnancyStore()
const {
  currentPregnancyWeek,
  currentPregnancyDay,
  currentWeekData,
  trimesterInfo,
  sizeComparison,
  formatWeekDay,
  getWeeksUntilDue,
  calculatePregnancyProgress,
  syncWithPregnancyData,
  isLoading
} = useBabyDevelopment()

// Computed properties
const currentPregnancy = computed(() => pregnancyStore.currentPregnancy)
const currentWeek = computed(() => currentPregnancyWeek.value)
const currentDay = computed(() => currentPregnancyDay.value)
const loading = computed(() => isLoading.value || pregnancyStore.loading)

// Removed complex trimester gradient - using single clean gradient in template

const progressPercentage = computed(() => {
  if (!currentPregnancy.value) return 0
  return calculatePregnancyProgress().percentage
})

const weeksUntilDue = computed(() => {
  if (!currentPregnancy.value) return 0
  return getWeeksUntilDue()
})

// Initialize data
onMounted(async () => {
  // Fetch pregnancies if not already loaded
  if (!pregnancyStore.currentPregnancy) {
    await pregnancyStore.fetchPregnancies()
  }
  
  // Sync baby development data with pregnancy data
  syncWithPregnancyData()
})
</script>

<style scoped>
/* Clean, minimal styling for development page */
</style>