<template>
  <div
    class="baby-development-card group relative overflow-hidden bg-white rounded-default border shadow-sm transition-all duration-200 ease-out cursor-pointer hover:shadow-md"
    @click="handleCardClick"
  >
    <!-- Subtle accent border -->
    <div class="absolute top-0 left-0 right-0 h-1 rounded-t-default" :class="trimesterAccentBg"></div>
    
    <div class="relative p-lg h-full">
      <!-- Header -->
      <div class="flex items-center justify-between mb-lg">
        <div class="flex items-center space-x-sm">
          <div class="w-1 h-8 rounded-pill" :class="trimesterAccentBg"></div>
          <h3 class="text-warm-graphite font-semibold text-xl font-primary">
            Week {{ displayWeek }}
          </h3>
        </div>
        <div class="flex items-center space-x-1 text-neutral-gray text-sm font-medium">
          <span>{{ trimesterLabel }}</span>
          <div class="w-1 h-1 bg-neutral-gray rounded-full"></div>
          <span>Day {{ currentDay || 0 }}</span>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="mb-lg">
        <div class="flex justify-between text-soft-charcoal text-xs mb-sm font-medium">
          <span>Pregnancy Progress</span>
          <span>{{ Math.round(progressPercentage) }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-pill h-2 overflow-hidden">
          <div 
            class="h-full transition-all duration-1000 ease-out rounded-pill"
            :class="trimesterAccentBg"
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
      </div>

      <!-- Baby size visualization -->
      <div class="text-center mb-lg">
        <div class="relative inline-block mb-sm">
          <div class="text-6xl mb-sm">
            {{ babyIcon }}
          </div>
        </div>
        <p class="text-warm-graphite font-medium text-base mb-xs">Size of {{ sizeComparison }}</p>
        <p class="text-soft-charcoal text-sm">{{ babyWeight }}</p>
      </div>

      <!-- Development milestones -->
      <div class="space-y-sm">
        <h4 class="text-warm-graphite text-sm font-medium mb-sm flex items-center">
          <div class="w-4 h-4 mr-sm flex items-center justify-center">
            <svg class="w-3 h-3 text-sage-green" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
          This Week's Developments
        </h4>
        <div 
          v-for="(milestone, index) in displayedMilestones" 
          :key="milestone"
          class="flex items-start text-sm text-soft-charcoal"
        >
          <div class="w-1.5 h-1.5 rounded-full mr-sm mt-2 flex-shrink-0" :class="trimesterAccentBg"></div>
          <span class="leading-5">{{ milestone }}</span>
        </div>
        
        <div 
          v-if="developmentMilestones.length > 2"
          class="text-center pt-sm"
        >
          <span class="text-neutral-gray text-xs font-medium">
            +{{ developmentMilestones.length - 2 }} more developments
          </span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentWeek?: number | null
  currentDay?: number | null
  pregnancyDay?: number | null
  developmentData?: any // API data from backend
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: null,
  currentDay: null,
  pregnancyDay: null,
  developmentData: null
})


// Router for navigation
const router = useRouter()

// Enhanced baby development data with more details
const babyDevelopmentData = {
  1: { icon: '🌱', size: 'Poppy seed', weight: '< 1g', milestones: ['Neural tube forms', 'Heart begins to develop', 'Basic body structure emerges'] },
  4: { icon: '🌾', size: 'Sesame seed', weight: '< 1g', milestones: ['Limb buds appear', 'Heart starts beating', 'Neural tube closes'] },
  6: { icon: '🫛', size: 'Sweet pea', weight: '2g', milestones: ['Brain hemispheres form', 'Jaw and facial features develop', 'Heart chambers form'] },
  8: { icon: '🫐', size: 'Blueberry', weight: '4g', milestones: ['Brain waves detectable', 'Fingers and toes form', 'Major organs developing'] },
  10: { icon: '🍇', size: 'Grape', weight: '8g', milestones: ['Webbed fingers separate', 'Eyelids form', 'External ears develop'] },
  12: { icon: '🍋', size: 'Lime', weight: '18g', milestones: ['All organs present', 'Can make fists', 'Reflexes developing'] },
  14: { icon: '🥝', size: 'Kiwi', weight: '40g', milestones: ['Hair follicles form', 'Can suck thumb', 'Kidneys produce urine'] },
  16: { icon: '🥑', size: 'Avocado', weight: '85g', milestones: ['Can hear sounds', 'Develops unique fingerprints', 'Skeleton hardening'] },
  18: { icon: '🍠', size: 'Sweet potato', weight: '150g', milestones: ['Vocal cords form', 'Can yawn and hiccup', 'Vernix forms'] },
  20: { icon: '🍌', size: 'Banana', weight: '240g', milestones: ['Can suck thumb', 'Hair and nails grow', 'Taste buds develop'] },
  22: { icon: '🥒', size: 'Cucumber', weight: '350g', milestones: ['Eyebrows and eyelashes', 'Brain growth spurt', 'Can respond to sounds'] },
  24: { icon: '🌽', size: 'Corn cob', weight: '540g', milestones: ['Lungs developing', 'Taste buds form', 'Hearing improves'] },
  26: { icon: '🥬', size: 'Lettuce head', weight: '760g', milestones: ['Eyes open and close', 'Responds to light', 'Regular sleep patterns'] },
  28: { icon: '🥥', size: 'Coconut', weight: '1kg', milestones: ['Eyes can open', 'Brain tissue increases', 'Can distinguish sounds'] },
  30: { icon: '🍈', size: 'Cantaloupe', weight: '1.3kg', milestones: ['Bone marrow produces blood', 'Lanugo hair sheds', 'Temperature regulation'] },
  32: { icon: '🥭', size: 'Mango', weight: '1.6kg', milestones: ['Bones hardening', 'Practices breathing', 'Immune system developing'] },
  34: { icon: '🍍', size: 'Pineapple', weight: '2kg', milestones: ['Central nervous system matures', 'Fingernails reach fingertips', 'Fat layers increase'] },
  36: { icon: '🎃', size: 'Small pumpkin', weight: '2.4kg', milestones: ['Immune system develops', 'Gains weight rapidly', 'Skull bones soft'] },
  38: { icon: '🍊', size: 'Orange', weight: '2.8kg', milestones: ['Lungs nearly mature', 'Developing sleep patterns', 'Meconium forms'] },
  40: { icon: '🍉', size: 'Watermelon', weight: '3.2kg', milestones: ['Fully developed', 'Ready for birth', 'Perfect timing for delivery'] }
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
  
  return babyDevelopmentData[closestWeek as keyof typeof babyDevelopmentData]
}

const babyData = computed(() => {
  // Use API data if available, otherwise fall back to static data
  if (props.developmentData) {
    return {
      icon: getWeekIcon(displayWeek.value),
      size: props.developmentData.baby_size_comparison,
      weight: `${props.developmentData.baby_weight_grams}g`,
      milestones: props.developmentData.development_highlights || []
    }
  }
  return getCurrentWeekData(displayWeek.value)
})

function getWeekIcon(week: number): string {
  if (week <= 4) return '🌱'
  if (week <= 8) return '🫐'
  if (week <= 12) return '🍋'
  if (week <= 16) return '🥑'
  if (week <= 20) return '🍌'
  if (week <= 24) return '🌽'
  if (week <= 28) return '🥥'
  if (week <= 32) return '🥭'
  if (week <= 36) return '🎃'
  return '🍉'
}

const babyIcon = computed(() => babyData.value?.icon || '👶')
const sizeComparison = computed(() => babyData.value?.size || 'Growing beautifully')
const babyWeight = computed(() => babyData.value?.weight || 'Growing')
const developmentMilestones = computed(() => babyData.value?.milestones || ['Growing and developing'])

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

const displayedMilestones = computed(() => {
  return developmentMilestones.value.slice(0, 2)
})

const sizeVisualization = computed(() => {
  const week = displayWeek.value
  // Calculate size based on week (approximate)
  const baseSize = Math.min(20 + (week * 1.5), 60)
  return {
    width: `${baseSize}px`,
    height: `${baseSize}px`
  }
})

// Navigation handler
const handleCardClick = () => {
  router.push('/baby-development')
}
</script>

<style scoped>
.baby-development-card {
  min-height: 320px;
  border-color: #e5e7eb;
}

.baby-development-card:hover {
  transform: translateY(-1px);
}

/* Mobile touch interactions */
@media (max-width: 768px) {
  .baby-development-card {
    min-height: 280px;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .baby-development-card {
    transition: none;
  }
  
  .baby-development-card:hover {
    transform: none;
  }
}
</style>

