<template>
  <div class="feed-filters relative">
    <!-- Filter Trigger Button -->
    <button
      ref="triggerRef"
      @click="toggleFilters"
      :class="cn(
        'filter-trigger flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 border',
        isOpen
          ? 'bg-gentle-mint/20 text-gray-800 border-gentle-mint/30 shadow-sm'
          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50',
        hasActiveFilters && 'bg-soft-pink/10 border-soft-pink/30 text-soft-pink'
      )"
      :aria-expanded="isOpen"
      aria-label="Filter and sort options"
    >
      <Filter class="w-4 h-4" />
      
      <span>Filters</span>
      
      <!-- Active filter indicator -->
      <div
        v-if="hasActiveFilters"
        class="w-2 h-2 bg-soft-pink rounded-full animate-pulse"
      />
      
      <!-- Chevron -->
      <ChevronDown :class="cn('w-4 h-4 transition-transform duration-200', isOpen && 'rotate-180')" />
    </button>

    <!-- Filter Dropdown -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        :style="dropdownStyle"
        class="filter-dropdown fixed z-50 bg-white rounded-2xl shadow-xl border border-gray-100 p-4 min-w-72"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800 font-primary">Filter & Sort</h3>
          <button
            @click="closeFilters"
            class="p-1 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close filters"
          >
            <X class="w-4 h-4 text-gray-500" />
          </button>
        </div>

        <!-- Filter Types -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">Content Type</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="filter in availableFilters"
                :key="filter.value"
                @click="selectFilter(filter.value)"
                :class="cn(
                  'filter-option p-3 rounded-lg text-left transition-all duration-200 border',
                  activeFilter === filter.value
                    ? 'bg-soft-pink/20 border-soft-pink/30 text-gray-800'
                    : 'bg-gray-50 border-gray-100 hover:bg-gray-100 text-gray-700'
                )"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-sm">{{ filter.label }}</div>
                    <div v-if="filter.description" class="text-xs text-gray-500 mt-0.5">
                      {{ filter.description }}
                    </div>
                  </div>
                  <div
                    v-if="filter.count > 0"
                    class="text-xs bg-white/50 px-1.5 py-0.5 rounded-full font-medium"
                  >
                    {{ filter.count }}
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Sort Options -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">Sort By</label>
            <div class="space-y-2">
              <button
                v-for="sort in availableSorts"
                :key="sort.value"
                @click="selectSort(sort.value)"
                :class="cn(
                  'sort-option w-full p-3 rounded-lg text-left transition-all duration-200 border flex items-center gap-3',
                  sortBy === sort.value
                    ? 'bg-gentle-mint/20 border-gentle-mint/30 text-gray-800'
                    : 'bg-gray-50 border-gray-100 hover:bg-gray-100 text-gray-700'
                )"
              >
                <div class="text-base">{{ sort.icon }}</div>
                <div class="flex-1">
                  <div class="font-medium text-sm">{{ sort.label }}</div>
                  <div class="text-xs text-gray-500">{{ sort.description }}</div>
                </div>
                <div
                  v-if="sortBy === sort.value"
                  class="w-4 h-4 text-gentle-mint"
                >
                  <Check class="w-4 h-4" />
                </div>
              </button>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="border-t border-gray-100 pt-4">
            <div class="flex items-center justify-between">
              <button
                @click="clearAllFilters"
                :disabled="!hasActiveFilters"
                :class="cn(
                  'text-sm font-medium transition-colors',
                  hasActiveFilters
                    ? 'text-soft-pink hover:text-soft-pink/80'
                    : 'text-gray-400 cursor-not-allowed'
                )"
              >
                Clear All
              </button>
              
              <div class="flex items-center gap-2">
                <button
                  @click="applyFilters"
                  class="px-4 py-2 bg-gentle-mint text-white rounded-lg text-sm font-medium hover:bg-gentle-mint/90 transition-colors"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>

          <!-- Filter Summary -->
          <div v-if="filterSummary" class="bg-warm-neutral/30 p-3 rounded-lg">
            <div class="text-xs text-gray-600 mb-1">Active filters:</div>
            <div class="text-sm font-medium text-gray-800">{{ filterSummary }}</div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Backdrop -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-black/10 backdrop-blur-sm"
      @click="closeFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { cn } from '~/components/ui/utils'
import { Filter, ChevronDown, X, Check } from 'lucide-vue-next'

interface FilterOption {
  value: string
  label: string
  description?: string
  count: number
  icon?: string
}

interface SortOption {
  value: string
  label: string
  description: string
  icon: string
}

interface Props {
  activeFilter: string
  sortBy: string
  filters?: FilterOption[]
}

const props = withDefaults(defineProps<Props>(), {
  filters: () => []
})

const emit = defineEmits<{
  filterChange: [filter: string]
  sortChange: [sort: string]
  filtersApplied: [{ filter: string, sort: string }]
}>()

// Available filter options with pregnancy context
const availableFilters = computed<FilterOption[]>(() => [
  {
    value: 'all',
    label: 'All Posts',
    description: 'Everything from family',
    count: props.filters.find(f => f.value === 'all')?.count || 0
  },
  {
    value: 'my_posts',
    label: 'My Posts',
    description: 'Posts you created',
    count: props.filters.find(f => f.value === 'my_posts')?.count || 0
  },
  {
    value: 'milestones',
    label: 'Milestones',
    description: 'Special pregnancy moments',
    count: props.filters.find(f => f.value === 'milestones')?.count || 0
  },
  {
    value: 'photos',
    label: 'Photos',
    description: 'Visual memories',
    count: props.filters.find(f => f.value === 'photos')?.count || 0
  },
  {
    value: 'updates',
    label: 'Updates',
    description: 'Daily life and feelings',
    count: props.filters.find(f => f.value === 'updates')?.count || 0
  },
  {
    value: 'celebrations',
    label: 'Celebrations',
    description: 'Joyful achievements',
    count: props.filters.find(f => f.value === 'celebrations')?.count || 0
  },
  {
    value: 'questions',
    label: 'Questions',
    description: 'Looking for input',
    count: props.filters.find(f => f.value === 'questions')?.count || 0
  },
  {
    value: 'recent',
    label: 'Recent',
    description: 'Last 3 days',
    count: props.filters.find(f => f.value === 'recent')?.count || 0
  },
  {
    value: 'trending',
    label: 'Trending',
    description: 'Popular with family',
    count: props.filters.find(f => f.value === 'trending')?.count || 0
  }
])

// Available sort options with pregnancy-friendly descriptions
const availableSorts: SortOption[] = [
  {
    value: 'chronological',
    label: 'Most Recent',
    description: 'Newest posts first',
    icon: '🕒'
  },
  {
    value: 'engagement',
    label: 'Most Engaging',
    description: 'Posts with most reactions',
    icon: '💫'
  },
  {
    value: 'family_priority',
    label: 'Family Favorites',
    description: 'Loved by family members',
    icon: '👨‍👩‍👧‍👦'
  },
  {
    value: 'milestone_first',
    label: 'Milestones First',
    description: 'Special moments at top',
    icon: '✨'
  }
]

// Local state
const isOpen = ref(false)
const triggerRef = ref<HTMLElement>()
const dropdownRef = ref<HTMLElement>()
const dropdownStyle = ref<Record<string, string>>({})
const selectedFilter = ref(props.activeFilter)
const selectedSort = ref(props.sortBy)

// Computed
const hasActiveFilters = computed(() => {
  return props.activeFilter !== 'all' || props.sortBy !== 'chronological'
})

const filterSummary = computed(() => {
  const filterLabel = availableFilters.value.find(f => f.value === props.activeFilter)?.label
  const sortLabel = availableSorts.find(s => s.value === props.sortBy)?.label
  
  const parts = []
  if (props.activeFilter !== 'all') parts.push(filterLabel)
  if (props.sortBy !== 'chronological') parts.push(`sorted by ${sortLabel}`)
  
  return parts.join(', ')
})

// Methods
async function toggleFilters() {
  if (isOpen.value) {
    closeFilters()
  } else {
    openFilters()
  }
}

async function openFilters() {
  isOpen.value = true
  await nextTick()
  positionDropdown()
}

function closeFilters() {
  isOpen.value = false
}

function selectFilter(filterValue: string) {
  selectedFilter.value = filterValue
}

function selectSort(sortValue: string) {
  selectedSort.value = sortValue
}

function applyFilters() {
  emit('filterChange', selectedFilter.value)
  emit('sortChange', selectedSort.value)
  emit('filtersApplied', { 
    filter: selectedFilter.value, 
    sort: selectedSort.value 
  })
  closeFilters()
}

function clearAllFilters() {
  selectedFilter.value = 'all'
  selectedSort.value = 'chronological'
  emit('filterChange', 'all')
  emit('sortChange', 'chronological')
  emit('filtersApplied', { filter: 'all', sort: 'chronological' })
}

function positionDropdown() {
  if (!triggerRef.value || !dropdownRef.value) return

  const trigger = triggerRef.value.getBoundingClientRect()
  const dropdown = dropdownRef.value
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }

  // Default position: below trigger, aligned to right
  let top = trigger.bottom + 8
  let left = trigger.right - dropdown.offsetWidth

  // Adjust for viewport bounds
  if (left < 8) {
    left = 8
  } else if (left + dropdown.offsetWidth > viewport.width - 8) {
    left = viewport.width - dropdown.offsetWidth - 8
  }

  // If not enough space below, position above
  if (top + dropdown.offsetHeight > viewport.height - 8) {
    top = trigger.top - dropdown.offsetHeight - 8
  }

  // Final bounds check
  if (top < 8) {
    top = 8
  }

  dropdownStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

// Event handlers
function handleClickOutside(event: Event) {
  if (
    isOpen.value &&
    triggerRef.value &&
    dropdownRef.value &&
    !triggerRef.value.contains(event.target as Node) &&
    !dropdownRef.value.contains(event.target as Node)
  ) {
    closeFilters()
  }
}

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && isOpen.value) {
    closeFilters()
  }
}

function handleResize() {
  if (isOpen.value) {
    positionDropdown()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscape)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscape)
  window.removeEventListener('resize', handleResize)
})

// Watch for prop changes
watch(() => props.activeFilter, (newFilter) => {
  selectedFilter.value = newFilter
})

watch(() => props.sortBy, (newSort) => {
  selectedSort.value = newSort
})
</script>

<style scoped>
/* Filter dropdown animations */
.filter-dropdown {
  animation: dropdown-appear 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top right;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Filter option hover effects */
.filter-option,
.sort-option {
  position: relative;
  overflow: hidden;
}

.filter-option::before,
.sort-option::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(248, 187, 208, 0.05), transparent);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.filter-option:hover::before,
.sort-option:hover::before {
  transform: translateX(100%);
}

/* Active filter styling */
.filter-option[data-active="true"] {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.1) 0%, rgba(255, 205, 210, 0.1) 100%);
  border-color: rgba(248, 187, 208, 0.3);
}

.sort-option[data-active="true"] {
  background: linear-gradient(135deg, rgba(178, 223, 219, 0.1) 0%, rgba(187, 222, 251, 0.1) 100%);
  border-color: rgba(178, 223, 219, 0.3);
}

/* Enhanced accessibility */
.filter-option:focus,
.sort-option:focus,
.filter-trigger:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .filter-dropdown {
    left: 1rem !important;
    right: 1rem !important;
    max-width: calc(100vw - 2rem);
    min-width: unset;
  }
  
  .grid {
    grid-template-columns: 1fr;
  }
  
  .filter-option,
  .sort-option {
    padding: 1rem;
  }
}

/* Filter trigger animation */
.filter-trigger {
  position: relative;
  overflow: hidden;
}

.filter-trigger:active {
  transform: scale(0.98);
}

/* Smooth transitions */
.filter-option,
.sort-option,
.filter-trigger {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Special styling for active filters indicator */
@keyframes filter-pulse {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(1.1);
  }
}

.animate-pulse {
  animation: filter-pulse 1.5s ease-in-out infinite;
}
</style>
