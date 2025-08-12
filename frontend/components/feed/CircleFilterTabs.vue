<template>
  <div class="circle-filter-tabs">
    <!-- Filter Tabs -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
        <button
          v-for="filter in circleFilters"
          :key="filter.id"
          @click="selectFilter(filter.id)"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
            activeFilter === filter.id
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          <span class="mr-2">{{ filter.icon }}</span>
          {{ filter.name }}
          <span 
            v-if="filter.unread_count > 0" 
            class="ml-2 bg-soft-pink text-white text-xs rounded-full px-2 py-0.5"
          >
            {{ filter.unread_count > 99 ? '99+' : filter.unread_count }}
          </span>
        </button>
      </div>

      <!-- Circle Visibility Toggle -->
      <div class="flex items-center space-x-3">
        <button
          @click="toggleCircleIndicators"
          :class="[
            'flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all duration-200',
            showCircleIndicators
              ? 'bg-gentle-mint/10 border-gentle-mint/30 text-gentle-mint'
              : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
          ]"
        >
          <Eye class="h-4 w-4" />
          <span class="text-sm">Show Circles</span>
        </button>

        <!-- Filter Options Menu -->
        <div class="relative">
          <button
            @click="toggleFilterMenu"
            class="p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Filter options"
          >
            <Filter class="h-4 w-4 text-gray-600" />
          </button>

          <!-- Dropdown Menu -->
          <div 
            v-if="showFilterMenu"
            class="absolute right-0 top-full mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-20"
          >
            <div class="p-4">
              <h3 class="font-medium text-gray-900 mb-3">Filter Options</h3>
              
              <!-- Sort Options -->
              <div class="space-y-3">
                <div>
                  <label class="text-sm text-gray-700 mb-2 block">Sort by</label>
                  <select 
                    v-model="sortBy"
                    @change="handleSortChange"
                    class="w-full px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-gentle-mint/50"
                  >
                    <option value="chronological">Most Recent</option>
                    <option value="engagement">Most Engaged</option>
                    <option value="family_priority">Family Priority</option>
                    <option value="milestone_first">Milestones First</option>
                  </select>
                </div>

                <!-- Circle Engagement Filter -->
                <div>
                  <label class="flex items-center space-x-2 text-sm">
                    <input 
                      v-model="showHighEngagement"
                      @change="handleEngagementFilter"
                      type="checkbox"
                      class="rounded border-gray-300 text-gentle-mint focus:ring-gentle-mint/50"
                    >
                    <span class="text-gray-700">High engagement only</span>
                  </label>
                </div>

                <!-- Time Range Filter -->
                <div>
                  <label class="text-sm text-gray-700 mb-2 block">Time Range</label>
                  <select 
                    v-model="timeRange"
                    @change="handleTimeRangeChange"
                    class="w-full px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-gentle-mint/50"
                  >
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Filter Summary -->
    <div v-if="activeFilterData" class="mb-4">
      <div class="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-gentle-mint/20">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <span class="text-2xl">{{ activeFilterData.icon }}</span>
            <div>
              <h4 class="font-medium text-gray-800">{{ activeFilterData.name }}</h4>
              <p class="text-sm text-gray-600">{{ activeFilterData.description }}</p>
            </div>
          </div>
          
          <div class="text-right space-y-1">
            <div class="text-sm font-medium text-gray-800">
              {{ activeFilterData.member_count }} people
            </div>
            <div class="text-xs text-gray-500">
              {{ filteredPostCount }} posts
            </div>
          </div>
        </div>

        <!-- Member Preview -->
        <div class="flex -space-x-2 mt-3" v-if="activeFilterData.members?.length > 0">
          <div 
            v-for="(member, index) in activeFilterData.members.slice(0, 5)"
            :key="member.id"
            class="relative z-10"
            :style="{ zIndex: 10 - index }"
            :title="member.display_name || member.first_name"
          >
            <div class="w-8 h-8 bg-gentle-mint/30 rounded-full flex items-center justify-center text-xs font-semibold text-gentle-mint-dark ring-2 ring-white">
              {{ (member.display_name || member.first_name || 'U').charAt(0).toUpperCase() }}
            </div>
          </div>
          <div 
            v-if="activeFilterData.members.length > 5"
            class="relative z-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center ring-2 ring-white"
          >
            <span class="text-xs text-gray-600 font-medium">
              +{{ activeFilterData.members.length - 5 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-3">
      <div class="animate-pulse bg-gray-200 h-4 rounded w-3/4"></div>
      <div class="animate-pulse bg-gray-200 h-4 rounded w-1/2"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Eye, Filter } from 'lucide-vue-next'

// Define circle patterns based on design document
interface CirclePattern {
  id: string
  name: string
  icon: string
  description: string
  member_count: number
  unread_count: number
  members?: Array<{
    id: string
    display_name?: string
    first_name?: string
    relationship?: string
  }>
}

interface Props {
  activeFilter?: string
  showCircleIndicators?: boolean
  filteredPostCount?: number
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  activeFilter: 'all',
  showCircleIndicators: false,
  filteredPostCount: 0,
  loading: false
})

const emit = defineEmits<{
  filterChange: [filterId: string]
  toggleIndicators: [show: boolean]
  sortChange: [sortBy: string]
  engagementFilter: [highOnly: boolean]
  timeRangeChange: [range: string]
}>()

// Local state
const activeFilter = ref(props.activeFilter)
const showCircleIndicators = ref(props.showCircleIndicators)
const showFilterMenu = ref(false)
const sortBy = ref('chronological')
const showHighEngagement = ref(false)
const timeRange = ref('all')

// Circle filters based on design document patterns
const circleFilters = ref<CirclePattern[]>([
  {
    id: 'all',
    name: 'All Updates',
    icon: '🌟',
    description: 'All posts from your pregnancy journey',
    member_count: 0,
    unread_count: 0
  },
  {
    id: 'just-us',
    name: 'Just Us',
    icon: '💕',
    description: 'You and your partner',
    member_count: 2,
    unread_count: 3
  },
  {
    id: 'close-family',
    name: 'Close Family',
    icon: '👨‍👩‍👧‍👦',
    description: 'Parents, siblings, and partner',
    member_count: 6,
    unread_count: 12
  },
  {
    id: 'grandparents',
    name: 'Grandparents',
    icon: '👴👵',
    description: 'Extended family including grandparents',
    member_count: 8,
    unread_count: 5
  },
  {
    id: 'friends-support',
    name: 'Friend Support',
    icon: '🤗',
    description: 'Close friends and support network',
    member_count: 15,
    unread_count: 8
  },
  {
    id: 'everyone',
    name: 'Everyone',
    icon: '🌍',
    description: 'All your family and friends',
    member_count: 23,
    unread_count: 25
  }
])

// Computed
const activeFilterData = computed(() => {
  return circleFilters.value.find(filter => filter.id === activeFilter.value)
})

// Methods
function selectFilter(filterId: string) {
  if (filterId === activeFilter.value) return
  
  activeFilter.value = filterId
  emit('filterChange', filterId)
}

function toggleCircleIndicators() {
  showCircleIndicators.value = !showCircleIndicators.value
  emit('toggleIndicators', showCircleIndicators.value)
}

function toggleFilterMenu() {
  showFilterMenu.value = !showFilterMenu.value
}

function handleSortChange() {
  emit('sortChange', sortBy.value)
}

function handleEngagementFilter() {
  emit('engagementFilter', showHighEngagement.value)
}

function handleTimeRangeChange() {
  emit('timeRangeChange', timeRange.value)
}

// Close filter menu when clicking outside
function handleClickOutside(event: Event) {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showFilterMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watchers
watch(() => props.activeFilter, (newValue) => {
  activeFilter.value = newValue
})

watch(() => props.showCircleIndicators, (newValue) => {
  showCircleIndicators.value = newValue
})
</script>

<style scoped>
/* Smooth transitions for filter tabs */
.circle-filter-tabs button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced hover effects */
.circle-filter-tabs button:hover {
  transform: translateY(-1px);
}

/* Active filter glow effect */
.circle-filter-tabs button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.1);
}

/* Dropdown animation */
.relative > div {
  animation: dropdown-appear 0.2s ease-out;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Member avatar hover effects */
.relative.z-10:hover {
  transform: scale(1.1);
  z-index: 20;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .circle-filter-tabs {
    padding: 0 1rem;
  }
  
  .flex.items-center.space-x-1 {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .flex.items-center.space-x-1 button {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }
  
  .absolute.right-0 {
    right: -1rem;
    width: calc(100vw - 2rem);
    max-width: 280px;
  }
}

@media (max-width: 480px) {
  .flex.items-center.justify-between {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .flex.items-center.space-x-3 {
    justify-content: center;
  }
}
</style>