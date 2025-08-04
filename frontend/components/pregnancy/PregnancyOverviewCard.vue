<template>
  <BaseCard variant="supportive" class="p-6 lg:col-span-2">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-xl font-primary font-semibold text-gray-800 mb-2">
          Your Pregnancy Journey
        </h2>
        <p class="text-gray-600 font-secondary">
          Week {{ currentWeek }} • {{ trimesterText }}
        </p>
      </div>
      <div class="text-right">
        <div class="text-3xl font-primary font-bold text-gentle-mint">
          {{ currentWeek || '--' }}<span class="text-lg">w</span>
        </div>
        <div class="text-sm text-gray-500 font-secondary">{{ currentDay || 0 }} days</div>
      </div>
    </div>
    
    <!-- Progress Bar -->
    <div class="mb-4">
      <div class="flex justify-between text-sm text-gray-600 font-secondary mb-2">
        <span>Progress</span>
        <span>{{ progressPercentage }}% complete</span>
      </div>
      <div class="w-full bg-warm-neutral rounded-full h-3">
        <div 
          class="bg-gradient-to-r from-gentle-mint to-soft-pink h-3 rounded-full transition-all duration-500"
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>

    <!-- Key Stats -->
    <div class="grid grid-cols-3 gap-4 text-center">
      <div class="p-3 bg-warm-neutral/30 rounded-lg">
        <div class="text-lg font-primary font-semibold text-gray-800">{{ daysUntilDue }}</div>
        <div class="text-sm text-gray-600 font-secondary">days to go</div>
      </div>
      <div class="p-3 bg-warm-neutral/30 rounded-lg">
        <div class="text-lg font-primary font-semibold text-gray-800">{{ formattedDueDate }}</div>
        <div class="text-sm text-gray-600 font-secondary">due date</div>
      </div>
      <div class="p-3 bg-warm-neutral/30 rounded-lg">
        <div class="text-lg font-primary font-semibold text-gray-800">{{ trimester || '--' }}</div>
        <div class="text-sm text-gray-600 font-secondary">trimester</div>
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
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: null,
  currentDay: null,
  trimester: null,
  dueDate: null
})

const trimesterText = computed(() => {
  if (!props.trimester) return 'Not set'
  
  const trimesterNames = {
    1: '1st Trimester',
    2: '2nd Trimester', 
    3: '3rd Trimester'
  }
  return trimesterNames[props.trimester] || 'Unknown'
})

const progressPercentage = computed(() => {
  if (!props.currentWeek) return 0
  return Math.min(Math.round((props.currentWeek / 40) * 100), 100)
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
</script>