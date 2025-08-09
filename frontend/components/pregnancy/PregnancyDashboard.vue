<template>
  <BaseCard variant="default" class="p-lg lg:col-span-3">
    <!-- Unified Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-3xl font-primary font-semibold text-warm-graphite mb-xs">
            Your Pregnancy Journey
          </h2>
          <p class="text-soft-charcoal font-secondary font-medium">
            Week {{ currentWeek }} • {{ trimesterText }}
          </p>
        </div>
        <BaseButton
          variant="ghost"
          size="sm"
          @click="navigateToBabyDevelopment"
          class="text-sage-green hover:text-sage-green/80"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </BaseButton>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-lg">
      <!-- Left Column: Progress & Stats -->
      <div class="space-y-lg">
        <!-- Week Progress Circle -->
        <div class="flex items-center justify-center">
          <div class="relative">
            <svg class="w-40 h-40 transform -rotate-90">
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="currentColor"
                :stroke-width="10"
                fill="none"
                class="text-light-gray"
              />
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="currentColor"
                :stroke-width="10"
                fill="none"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="strokeDashoffset"
                class="transition-all duration-500"
                :class="progressCircleColor"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="text-4xl font-primary font-bold text-warm-graphite">
                {{ currentWeek || '--' }}
              </div>
              <div class="text-sm text-soft-charcoal font-secondary font-medium">weeks</div>
              <div class="text-xs text-neutral-gray font-secondary">+{{ currentDay || 0 }} days</div>
            </div>
          </div>
        </div>

        <!-- Timeline Progress -->
        <div>
          <div class="flex justify-between text-sm text-soft-charcoal font-secondary font-medium mb-sm">
            <span>Journey Progress</span>
            <span>{{ progressPercentage }}%</span>
          </div>
          <div class="w-full bg-light-gray rounded-pill h-2">
            <div 
              class="h-2 rounded-pill transition-all duration-500"
              :class="progressBarColor"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Key Stats Grid -->
        <div class="grid grid-cols-2 gap-sm">
          <div class="p-md bg-warm-gray rounded-default text-center border border-light-gray">
            <div class="text-2xl font-primary font-semibold text-warm-graphite">{{ daysUntilDue }}</div>
            <div class="text-xs text-soft-charcoal font-secondary font-medium">days to go</div>
          </div>
          <div class="p-md bg-warm-gray rounded-default text-center border border-light-gray">
            <div class="text-lg font-primary font-semibold text-warm-graphite">{{ formattedDueDate }}</div>
            <div class="text-xs text-soft-charcoal font-secondary font-medium">due date</div>
          </div>
        </div>
      </div>

      <!-- Right Column: Baby Development -->
      <div class="space-y-md">
        <!-- Baby Size Card -->
        <div 
          class="p-md rounded-default cursor-pointer transition-all hover:shadow-md bg-warm-gray border border-light-gray hover:border-sage-green/30"
          @click="navigateToBabyDevelopment"
        >
          <div class="flex items-center justify-between mb-sm">
            <h3 class="text-warm-graphite font-medium text-base flex items-center">
              <span class="mr-sm">Baby Development</span>
              <svg class="w-4 h-4 text-sage-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
              </svg>
            </h3>
            <span class="text-soft-charcoal text-sm font-medium">{{ trimesterText }}</span>
          </div>

          <!-- Baby Icon and Size -->
          <div class="text-center mb-md">
            <div class="text-5xl mb-sm">{{ babyIcon }}</div>
            <p class="text-warm-graphite font-medium text-base">Size of {{ sizeComparison }}</p>
            <p class="text-soft-charcoal text-sm">{{ babyWeight }}</p>
          </div>

          <!-- Mini Progress -->
          <div class="w-full bg-light-gray rounded-pill h-1.5 mb-md">
            <div 
              class="h-full rounded-pill transition-all duration-500"
              :class="trimesterAccentBg"
              :style="{ width: `${weekProgressInTrimester}%` }"
            ></div>
          </div>

          <!-- Development Highlights -->
          <div class="space-y-sm">
            <div 
              v-for="(milestone, index) in displayedMilestones" 
              :key="index"
              class="flex items-start text-sm text-soft-charcoal"
            >
              <div class="w-1.5 h-1.5 rounded-full mr-sm mt-1.5 flex-shrink-0" :class="trimesterAccentBg"></div>
              <span>{{ milestone }}</span>
            </div>
            <div 
              v-if="developmentMilestones.length > 2"
              class="text-center pt-xs"
            >
              <span class="text-neutral-gray text-xs font-medium">
                +{{ developmentMilestones.length - 2 }} more developments
              </span>
            </div>
          </div>
        </div>

        <!-- Next Milestone -->
        <div class="p-sm bg-warm-gray rounded-default border border-light-gray">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-soft-charcoal font-secondary font-medium mb-xs">Next milestone</p>
              <p class="text-sm font-medium text-warm-graphite">{{ nextMilestone.name }}</p>
            </div>
            <div class="text-right">
              <p class="text-lg font-semibold" :class="milestoneAccentColor">{{ nextMilestone.weeksAway }}</p>
              <p class="text-xs text-soft-charcoal font-medium">weeks</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Action -->
    <div class="mt-lg pt-md border-t border-light-gray">
      <div class="flex items-center justify-between">
        <p class="text-sm text-soft-charcoal font-secondary">
          Track your journey and baby's growth every step of the way
        </p>
        <BaseButton
          variant="outline"
          size="sm"
          @click="navigateToBabyDevelopment"
        >
          View Details
        </BaseButton>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
interface Props {
  currentWeek?: number | null
  currentDay?: number | null
  trimester?: number | null
  dueDate?: string | null
  pregnancyDay?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: null,
  currentDay: null,
  trimester: null,
  dueDate: null,
  pregnancyDay: null
})

const router = useRouter()

// Baby development data
const babyDevelopmentData = {
  1: { icon: '🌱', size: 'a poppy seed', weight: '< 1g', milestones: ['Neural tube forms', 'Heart begins to develop', 'Basic body structure emerges'] },
  4: { icon: '🌾', size: 'a sesame seed', weight: '< 1g', milestones: ['Limb buds appear', 'Heart starts beating', 'Neural tube closes'] },
  6: { icon: '🫛', size: 'a sweet pea', weight: '2g', milestones: ['Brain hemispheres form', 'Jaw and facial features develop', 'Heart chambers form'] },
  8: { icon: '🫐', size: 'a blueberry', weight: '4g', milestones: ['Brain waves detectable', 'Fingers and toes form', 'Major organs developing'] },
  10: { icon: '🍇', size: 'a grape', weight: '8g', milestones: ['Webbed fingers separate', 'Eyelids form', 'External ears develop'] },
  12: { icon: '🍋', size: 'a lime', weight: '18g', milestones: ['All organs present', 'Can make fists', 'Reflexes developing'] },
  14: { icon: '🥝', size: 'a kiwi', weight: '40g', milestones: ['Hair follicles form', 'Can suck thumb', 'Kidneys produce urine'] },
  16: { icon: '🥑', size: 'an avocado', weight: '85g', milestones: ['Can hear sounds', 'Develops unique fingerprints', 'Skeleton hardening'] },
  18: { icon: '🍠', size: 'a sweet potato', weight: '150g', milestones: ['Vocal cords form', 'Can yawn and hiccup', 'Vernix forms'] },
  20: { icon: '🍌', size: 'a banana', weight: '240g', milestones: ['Can suck thumb', 'Hair and nails grow', 'Taste buds develop'] },
  22: { icon: '🥒', size: 'a cucumber', weight: '350g', milestones: ['Eyebrows and eyelashes', 'Brain growth spurt', 'Can respond to sounds'] },
  24: { icon: '🌽', size: 'a corn cob', weight: '540g', milestones: ['Lungs developing', 'Taste buds form', 'Hearing improves'] },
  26: { icon: '🥬', size: 'a lettuce head', weight: '760g', milestones: ['Eyes open and close', 'Responds to light', 'Regular sleep patterns'] },
  28: { icon: '🥥', size: 'a coconut', weight: '1kg', milestones: ['Eyes can open', 'Brain tissue increases', 'Can distinguish sounds'] },
  30: { icon: '🍈', size: 'a cantaloupe', weight: '1.3kg', milestones: ['Bone marrow produces blood', 'Lanugo hair sheds', 'Temperature regulation'] },
  32: { icon: '🥭', size: 'a mango', weight: '1.6kg', milestones: ['Bones hardening', 'Practices breathing', 'Immune system developing'] },
  34: { icon: '🍍', size: 'a pineapple', weight: '2kg', milestones: ['Central nervous system matures', 'Fingernails reach fingertips', 'Fat layers increase'] },
  36: { icon: '🎃', size: 'a small pumpkin', weight: '2.4kg', milestones: ['Immune system develops', 'Gains weight rapidly', 'Skull bones soft'] },
  38: { icon: '🍊', size: 'an orange', weight: '2.8kg', milestones: ['Lungs nearly mature', 'Developing sleep patterns', 'Meconium forms'] },
  40: { icon: '🍉', size: 'a watermelon', weight: '3.2kg', milestones: ['Fully developed', 'Ready for birth', 'Perfect timing for delivery'] }
}

// Computed properties
const circumference = 2 * Math.PI * 70
const strokeDashoffset = computed(() => {
  const progress = progressPercentage.value / 100
  return circumference * (1 - progress)
})

const trimesterText = computed(() => {
  if (!props.trimester) return 'Getting Started'
  const trimesterNames = {
    1: '1st Trimester',
    2: '2nd Trimester', 
    3: '3rd Trimester'
  }
  return trimesterNames[props.trimester as keyof typeof trimesterNames] || 'Unknown'
})

const progressPercentage = computed(() => {
  if (!props.currentWeek) return 0
  return Math.min(Math.round((props.currentWeek / 40) * 100), 100)
})

const weekProgressInTrimester = computed(() => {
  if (!props.currentWeek) return 0
  const week = props.currentWeek
  if (props.trimester === 1) {
    return (week / 12) * 100
  } else if (props.trimester === 2) {
    return ((week - 12) / 14) * 100
  } else {
    return ((week - 26) / 14) * 100
  }
})

const daysUntilDue = computed(() => {
  if (!props.dueDate) return '--'
  
  const dueDate = new Date(props.dueDate)
  const today = new Date()
  const diffTime = dueDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays > 0 ? diffDays : 0
})

const formattedDueDate = computed(() => {
  if (!props.dueDate) return 'Not set'
  return new Date(props.dueDate).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
})

const trimesterAccentBg = computed(() => {
  const t = props.trimester || 1
  if (t === 1) return 'bg-blush-rose'
  if (t === 2) return 'bg-dusty-lavender'
  return 'bg-sage-green'
})

const progressCircleColor = computed(() => {
  const t = props.trimester || 1
  if (t === 1) return 'text-blush-rose'
  if (t === 2) return 'text-dusty-lavender'
  return 'text-sage-green'
})

const progressBarColor = computed(() => {
  const t = props.trimester || 1
  if (t === 1) return 'bg-blush-rose'
  if (t === 2) return 'bg-dusty-lavender'
  return 'bg-sage-green'
})

const milestoneAccentColor = computed(() => {
  const t = props.trimester || 1
  if (t === 1) return 'text-blush-rose'
  if (t === 2) return 'text-dusty-lavender'
  return 'text-sage-green'
})

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
  return getCurrentWeekData(props.currentWeek || 1)
})

const babyIcon = computed(() => babyData.value?.icon || '👶')
const sizeComparison = computed(() => babyData.value?.size || 'growing beautifully')
const babyWeight = computed(() => babyData.value?.weight || 'Growing')
const developmentMilestones = computed(() => babyData.value?.milestones || ['Growing and developing'])
const displayedMilestones = computed(() => developmentMilestones.value.slice(0, 2))

const nextMilestone = computed(() => {
  const week = props.currentWeek || 0
  if (week < 12) {
    return { name: 'End of 1st trimester', weeksAway: 12 - week }
  } else if (week < 20) {
    return { name: 'Anatomy scan', weeksAway: 20 - week }
  } else if (week < 24) {
    return { name: 'Viability milestone', weeksAway: 24 - week }
  } else if (week < 28) {
    return { name: 'Third trimester begins', weeksAway: 28 - week }
  } else if (week < 37) {
    return { name: 'Full term', weeksAway: 37 - week }
  } else {
    return { name: 'Due date approaching', weeksAway: 40 - week }
  }
})

// Navigation
const navigateToBabyDevelopment = () => {
  router.push('/baby-development')
}
</script>

<style scoped>
/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .grid {
    gap: var(--space-md);
  }
}

/* Subtle hover effects */
@media (hover: hover) {
  .cursor-pointer:hover {
    transform: translateY(-1px);
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .transition-all {
    transition: none;
  }
  
  .cursor-pointer:hover {
    transform: none;
  }
}
</style>