<template>
  <div 
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click="$emit('close')"
  >
    <!-- Backdrop -->
    <div 
      class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity duration-300"
      :class="{ 'opacity-100': isOpen, 'opacity-0': !isOpen }"
    ></div>
    
    <!-- Modal -->
    <div class="flex min-h-screen items-center justify-center p-4">
      <div 
        class="relative bg-white rounded-rounded shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden transition-all duration-300 border border-gray-200"
        :class="{ 'scale-100 opacity-100': isOpen, 'scale-95 opacity-0': !isOpen }"
        @click.stop
      >
        <!-- Header with subtle accent -->
        <div class="relative overflow-hidden bg-gray-50">
          <!-- Subtle accent bar -->
          <div class="absolute top-0 left-0 right-0 h-1" :class="trimesterAccentBg"></div>
          
          <div class="relative p-lg text-warm-graphite">
            <div class="flex items-center justify-between mb-lg">
              <div class="flex items-center space-x-sm">
                <div class="w-1 h-10 rounded-pill" :class="trimesterAccentBg"></div>
                <div>
                  <h2 class="text-3xl font-bold font-primary text-warm-graphite">Week {{ displayWeek }} Development</h2>
                  <p class="text-soft-charcoal font-medium">{{ trimesterLabel }} • Day {{ currentDay }}</p>
                </div>
              </div>
              <button 
                @click="$emit('close')"
                class="bg-gray-100 hover:bg-gray-200 rounded-default p-sm transition-colors duration-200 text-soft-charcoal"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Progress indicator -->
            <div class="mb-lg">
              <div class="flex justify-between text-soft-charcoal text-sm mb-sm font-medium">
                <span>Pregnancy Progress</span>
                <span>{{ Math.round(progressPercentage) }}% Complete</span>
              </div>
              <div class="w-full bg-gray-100 rounded-pill h-3 overflow-hidden">
                <div 
                  class="h-full transition-all duration-1000 ease-out rounded-pill"
                  :class="trimesterAccentBg"
                  :style="{ width: progressPercentage + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Content -->
        <div class="p-lg overflow-y-auto max-h-[60vh]">
          <!-- Baby size section -->
          <div class="mb-8">
            <div class="grid md:grid-cols-2 gap-6">
              <!-- Visual representation -->
              <div class="text-center">
                <div class="relative inline-block mb-4">
                  <div class="text-8xl mb-4 animate-pulse">{{ babyIcon }}</div>
                  <!-- Animated size circle -->
                  <div 
                    class="absolute -bottom-2 left-1/2 transform -translate-x-1/2 border-3 rounded-full transition-all duration-1000"
                    :class="[trimesterGradient.replace('bg-gradient-to-br', 'border-gradient-to-br')]"
                    :style="{
                      width: sizeVisualization.width,
                      height: sizeVisualization.height,
                      borderColor: trimesterColor
                    }"
                  ></div>
                </div>
                <h3 class="text-xl font-semibold mb-sm font-primary text-warm-graphite">Size Comparison</h3>
                <p class="text-2xl font-bold mb-xs text-warm-graphite">{{ sizeComparison }}</p>
                <p class="text-soft-charcoal">Average weight: {{ babyWeight }}</p>
              </div>
              
              <!-- Size details -->
              <div class="space-y-4">
                <h3 class="text-xl font-semibold mb-lg font-primary text-warm-graphite">Physical Development</h3>
                <div class="grid grid-cols-2 gap-md">
                  <div class="bg-white rounded-default p-md border border-gray-200 shadow-sm">
                    <div class="text-sm text-soft-charcoal mb-xs font-medium">Length</div>
                    <div class="font-semibold text-warm-graphite">{{ estimatedLength }}cm</div>
                  </div>
                  <div class="bg-white rounded-default p-md border border-gray-200 shadow-sm">
                    <div class="text-sm text-soft-charcoal mb-xs font-medium">Weight</div>
                    <div class="font-semibold text-warm-graphite">{{ babyWeight }}</div>
                  </div>
                  <div class="bg-white rounded-default p-md border border-gray-200 shadow-sm">
                    <div class="text-sm text-soft-charcoal mb-xs font-medium">Trimester</div>
                    <div class="font-semibold text-warm-graphite">{{ trimesterLabel }}</div>
                  </div>
                  <div class="bg-white rounded-default p-md border border-gray-200 shadow-sm">
                    <div class="text-sm text-soft-charcoal mb-xs font-medium">Weeks to go</div>
                    <div class="font-semibold text-warm-graphite">{{ 40 - displayWeek }} weeks</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Development milestones -->
          <div class="mb-8">
            <h3 class="text-xl font-semibold mb-lg font-primary text-warm-graphite">This Week's Milestones</h3>
            <div class="grid md:grid-cols-2 gap-md">
              <div 
                v-for="(milestone, index) in developmentMilestones" 
                :key="milestone"
                class="flex items-start p-md bg-white rounded-default transition-all duration-300 hover:shadow-sm border border-gray-200 shadow-sm"
                :style="{ animationDelay: (index * 100) + 'ms' }"
              >
                <div class="flex-shrink-0 mr-sm mt-1">
                  <div 
                    class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium"
                    :class="trimesterAccentBg"
                  >
                    {{ index + 1 }}
                  </div>
                </div>
                <div>
                  <p class="text-soft-charcoal leading-relaxed">{{ milestone }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Additional information -->
          <div class="mb-8">
            <h3 class="text-xl font-semibold mb-lg font-primary text-warm-graphite">What's Happening</h3>
            <div class="bg-white rounded-default p-lg border border-gray-200 shadow-sm">
              <div class="prose prose-sm max-w-none">
                <p class="text-soft-charcoal leading-relaxed mb-lg">
                  {{ weekDescription }}
                </p>
                <div class="grid md:grid-cols-2 gap-xl mt-lg">
                  <div>
                    <h4 class="font-semibold text-warm-graphite mb-sm font-medium">For Baby</h4>
                    <ul class="space-y-1 text-sm text-soft-charcoal">
                      <li v-for="item in babyHighlights" :key="item" class="flex items-start">
                        <span class="text-green-500 mr-sm font-medium">•</span>
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div>
                    <h4 class="font-semibold text-warm-graphite mb-sm font-medium">For Mom</h4>
                    <ul class="space-y-1 text-sm text-soft-charcoal">
                      <li v-for="item in momHighlights" :key="item" class="flex items-start">
                        <span class="text-rose-500 mr-sm font-medium">•</span>
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Timeline navigation -->
          <div class="border-t pt-6">
            <h3 class="text-lg font-semibold mb-lg font-primary text-warm-graphite">Explore Other Weeks</h3>
            <div class="flex items-center justify-center space-x-4">
              <button 
                @click="navigateWeek(displayWeek - 1)"
                :disabled="displayWeek <= 1"
                class="flex items-center px-4 py-2 rounded-lg transition-colors duration-200"
                :class="[
                  displayWeek <= 1 
                    ? 'bg-gray-100 text-neutral-gray cursor-not-allowed' 
                    : 'bg-white hover:bg-gray-50 text-soft-charcoal border border-gray-200'
                ]"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Previous Week
              </button>
              
              <div class="text-center px-4">
                <div class="text-sm text-neutral-gray font-medium">Current</div>
                <div class="font-semibold text-warm-graphite">Week {{ displayWeek }}</div>
              </div>
              
              <button 
                @click="navigateWeek(displayWeek + 1)"
                :disabled="displayWeek >= 40"
                class="flex items-center px-4 py-2 rounded-lg transition-colors duration-200"
                :class="[
                  displayWeek >= 40 
                    ? 'bg-gray-100 text-neutral-gray cursor-not-allowed' 
                    : 'bg-white hover:bg-gray-50 text-soft-charcoal border border-gray-200'
                ]"
              >
                Next Week
                <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  isOpen: boolean
  currentWeek?: number | null
  currentDay?: number | null
  pregnancyDay?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  currentWeek: null,
  currentDay: null,
  pregnancyDay: null
})

const emit = defineEmits<{
  close: []
  weekChanged: [week: number]
}>()

// Particles for animation
const particles = ref<Array<{
  id: number
  x: number
  y: number
  delay: number
  duration: number
}>>([])

// Enhanced baby development data (same as card component but with additional details)
const babyDevelopmentData = {
  1: { 
    icon: '🌱', 
    size: 'Poppy seed', 
    weight: '< 1g', 
    length: 0.1,
    milestones: ['Neural tube forms', 'Heart begins to develop', 'Basic body structure emerges'],
    description: 'Your baby is just beginning to form! The neural tube, which will become the brain and spinal cord, is developing.',
    babyHighlights: ['Cell division is rapid', 'Basic body plan is established', 'Implantation occurs'],
    momHighlights: ['You might not know you\'re pregnant yet', 'Take prenatal vitamins with folic acid', 'Maintain healthy lifestyle']
  },
  4: { 
    icon: '🌾', 
    size: 'Sesame seed', 
    weight: '< 1g', 
    length: 0.2,
    milestones: ['Limb buds appear', 'Heart starts beating', 'Neural tube closes'],
    description: 'Your baby\'s heart has started beating! Tiny limb buds that will become arms and legs are beginning to form.',
    babyHighlights: ['Heart begins to beat', 'Arms and legs start forming', 'Brain divides into sections'],
    momHighlights: ['Morning sickness may begin', 'Breast tenderness', 'First missed period']
  },
  // ... (continuing with more detailed data for other weeks)
  20: {
    icon: '🍌',
    size: 'Banana',
    weight: '240g',
    length: 16,
    milestones: ['Can suck thumb', 'Hair and nails grow', 'Taste buds develop'],
    description: 'Congratulations - you\'re halfway there! Your baby can now hear sounds and is developing a regular sleep-wake cycle.',
    babyHighlights: ['Can hear your voice', 'Developing fingerprints', 'Growing hair and nails'],
    momHighlights: ['Anatomy scan scheduled', 'Baby movements become stronger', 'Energy levels may improve']
  },
  40: {
    icon: '🍉',
    size: 'Watermelon',
    weight: '3.2kg',
    length: 50,
    milestones: ['Fully developed', 'Ready for birth', 'Perfect timing for delivery'],
    description: 'Your baby is fully developed and ready to meet you! They have everything needed to thrive outside the womb.',
    babyHighlights: ['All organs are mature', 'Strong bones and muscles', 'Ready for life outside'],
    momHighlights: ['Labor may begin any day', 'Frequent doctor visits', 'Hospital bag ready']
  }
}

// Computed properties
const displayWeek = computed(() => props.currentWeek || 1)
const currentDay = computed(() => props.currentDay || 0)
const pregnancyDay = computed(() => props.pregnancyDay || (displayWeek.value * 7) + currentDay.value)

const getCurrentWeekData = (week: number) => {
  const availableWeeks = Object.keys(babyDevelopmentData).map(Number).sort((a, b) => a - b)
  let closestWeek = availableWeeks[0]
  
  for (const availableWeek of availableWeeks) {
    if (week >= availableWeek) {
      closestWeek = availableWeek
    } else {
      break
    }
  }
  
  return babyDevelopmentData[closestWeek as keyof typeof babyDevelopmentData] || babyDevelopmentData[20]
}

const babyData = computed(() => getCurrentWeekData(displayWeek.value))
const babyIcon = computed(() => babyData.value?.icon || '👶')
const sizeComparison = computed(() => babyData.value?.size || 'Growing beautifully')
const babyWeight = computed(() => babyData.value?.weight || 'Growing')
const estimatedLength = computed(() => babyData.value?.length || 'Unknown')
const developmentMilestones = computed(() => babyData.value?.milestones || ['Growing and developing'])
const weekDescription = computed(() => babyData.value?.description || 'Your baby is growing and developing beautifully.')
const babyHighlights = computed(() => babyData.value?.babyHighlights || ['Growing steadily'])
const momHighlights = computed(() => babyData.value?.momHighlights || ['Take care of yourself'])

// Trimester calculations
const trimester = computed(() => {
  const week = displayWeek.value
  if (week <= 12) return 1
  if (week <= 26) return 2
  return 3
})

const trimesterLabel = computed(() => {
  const t = trimester.value
  return `${t === 1 ? '1st' : t === 2 ? '2nd' : '3rd'} Trimester`
})

const trimesterAccentBg = computed(() => {
  const t = trimester.value
  if (t === 1) return 'bg-rose-400'
  if (t === 2) return 'bg-purple-400'
  return 'bg-green-400'
})

const progressPercentage = computed(() => {
  const totalDays = 280 // 40 weeks
  const currentDays = pregnancyDay.value
  return Math.min((currentDays / totalDays) * 100, 100)
})

const sizeVisualization = computed(() => {
  const week = displayWeek.value
  const baseSize = Math.min(30 + (week * 2), 80)
  return {
    width: `${baseSize}px`,
    height: `${baseSize}px`
  }
})

// Methods
const navigateWeek = (week: number) => {
  if (week >= 1 && week <= 40) {
    emit('weekChanged', week)
  }
}

const generateParticles = () => {
  particles.value = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 6,
    duration: 4 + Math.random() * 3
  }))
}

// Lifecycle
onMounted(() => {
  generateParticles()
})

// Handle escape key
const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
@keyframes float {
  0%, 100% {
    transform: translateY(0px) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-15px) scale(1.2);
    opacity: 0.9;
  }
}

.animate-float {
  animation: float linear infinite;
}

/* Scrollbar styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f9fafb;
  border-radius: 8px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 8px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .max-w-4xl {
    max-width: 95vw;
  }
  
  .grid.md\\:grid-cols-2 {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .transition-all {
    transition: none;
  }
}
</style>