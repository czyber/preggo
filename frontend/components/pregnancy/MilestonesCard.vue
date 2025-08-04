<template>
  <BaseCard variant="celebration" class="p-6">
    <h3 class="text-lg font-primary font-semibold text-gray-800 mb-4">
      Upcoming Milestones
    </h3>
    <div class="space-y-3">
      <div 
        v-for="milestone in upcomingMilestones" 
        :key="milestone.name"
        class="flex items-center justify-between p-3 bg-warm-neutral/20 rounded-lg"
      >
        <div>
          <p class="text-sm font-medium text-gray-800">{{ milestone.name }}</p>
          <p class="text-xs text-gray-600 font-secondary">Week {{ milestone.week }}</p>
        </div>
        <div class="text-xs font-secondary" :class="milestone.urgencyClass">
          {{ milestone.timeUntil }}
        </div>
      </div>
      <div v-if="upcomingMilestones.length === 0" class="text-center py-4">
        <p class="text-sm text-gray-500 font-secondary">All major milestones completed! 🎉</p>
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

// Static milestone data
const milestoneData = [
  { name: 'First Prenatal Visit', week: 8 },
  { name: 'Tell Family & Friends', week: 12 },
  { name: 'Genetic Testing', week: 15 },
  { name: 'Anatomy Scan', week: 20 },
  { name: 'Glucose Screening', week: 24 },
  { name: 'Baby Shower Planning', week: 28 },
  { name: 'Childbirth Classes', week: 32 },
  { name: 'Hospital Bag', week: 36 },
  { name: 'Weekly Checkups Begin', week: 37 },
  { name: 'Final Preparations', week: 39 },
  { name: 'Baby\'s Arrival', week: 40 }
]

const upcomingMilestones = computed(() => {
  if (!props.currentWeek) return milestoneData.slice(0, 3)
  
  return milestoneData
    .filter(milestone => milestone.week > props.currentWeek!)
    .slice(0, 3)
    .map(milestone => {
      const weeksUntil = milestone.week - props.currentWeek!
      let timeUntil = ''
      let urgencyClass = ''
      
      if (weeksUntil <= 1) {
        timeUntil = 'This week'
        urgencyClass = 'text-light-coral'
      } else if (weeksUntil <= 2) {
        timeUntil = 'Soon'
        urgencyClass = 'text-light-coral'
      } else if (weeksUntil <= 4) {
        timeUntil = `${weeksUntil} weeks`
        urgencyClass = 'text-muted-lavender'
      } else {
        timeUntil = `${weeksUntil} weeks`
        urgencyClass = 'text-gray-500'
      }
      
      return {
        ...milestone,
        timeUntil,
        urgencyClass
      }
    })
})
</script>