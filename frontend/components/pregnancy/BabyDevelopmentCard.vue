<template>
  <BaseCard variant="celebration" class="p-6">
    <div class="text-center">
      <h3 class="text-lg font-primary font-semibold text-gray-800 mb-4">
        Baby Development
      </h3>
      <div class="mb-4">
        <div class="text-4xl mb-2">{{ babyIcon }}</div>
        <p class="text-sm text-gray-600 font-secondary mb-2">{{ sizeComparison }}</p>
        <p class="text-xs text-gray-500 font-secondary">Week {{ currentWeek }}</p>
      </div>
      <div class="space-y-2 text-left">
        <div 
          v-for="development in developmentMilestones" 
          :key="development"
          class="flex items-center text-sm text-gray-600"
        >
          <div class="w-2 h-2 bg-light-coral rounded-full mr-2"></div>
          <span class="font-secondary">{{ development }}</span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
interface Props {
  currentWeek?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: null
})

// Static data for baby development (could be dynamic based on week in the future)
const babyDevelopmentData = {
  1: { icon: '🌱', size: 'Size of a poppy seed', milestones: ['Neural tube forms', 'Heart begins to develop'] },
  4: { icon: '🌾', size: 'Size of a sesame seed', milestones: ['Limb buds appear', 'Heart starts beating'] },
  8: { icon: '🫐', size: 'Size of a blueberry', milestones: ['Brain waves detectable', 'Fingers and toes form'] },
  12: { icon: '🍋', size: 'Size of a lime', milestones: ['All organs present', 'Can make fists'] },
  16: { icon: '🥑', size: 'Size of an avocado', milestones: ['Can hear sounds', 'Develops unique fingerprints'] },
  20: { icon: '🍌', size: 'Size of a banana', milestones: ['Can suck thumb', 'Hair and nails grow'] },
  24: { icon: '🌽', size: 'Size of corn', milestones: ['Lungs developing', 'Taste buds form'] },
  28: { icon: '🥒', size: 'Size of a cucumber', milestones: ['Eyes can open', 'Brain tissue increases'] },
  32: { icon: '🥥', size: 'Size of a coconut', milestones: ['Bones hardening', 'Practices breathing'] },
  36: { icon: '🍈', size: 'Size of a cantaloupe', milestones: ['Immune system develops', 'Gains weight rapidly'] },
  39: { icon: '🍊', size: 'Size of an orange', milestones: ['Baby can hear sounds', 'Developing sleep patterns', 'Lung maturation continues'] },
  40: { icon: '🍉', size: 'Size of a watermelon', milestones: ['Fully developed', 'Ready for birth'] }
}

const getCurrentWeekData = (week: number) => {
  // Find the closest week data
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

const babyIcon = computed(() => {
  if (!props.currentWeek) return '👶'
  const data = getCurrentWeekData(props.currentWeek)
  return data?.icon || '👶'
})

const sizeComparison = computed(() => {
  if (!props.currentWeek) return 'Growing beautifully'
  const data = getCurrentWeekData(props.currentWeek)
  return data?.size || 'Growing beautifully'
})

const developmentMilestones = computed(() => {
  if (!props.currentWeek) return ['Growing and developing']
  const data = getCurrentWeekData(props.currentWeek)
  return data?.milestones || ['Growing and developing']
})
</script>