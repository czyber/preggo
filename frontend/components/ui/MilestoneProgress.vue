<template>
  <div :class="cn('space-y-3', props.class)">
    <div class="flex justify-between items-center">
      <div>
        <h3 class="font-medium text-gray-800">{{ title }}</h3>
        <p v-if="subtitle" class="text-sm text-gray-600">{{ subtitle }}</p>
      </div>
      <div class="text-right">
        <span class="text-sm font-medium text-gray-700">{{ current }}/{{ total }}</span>
        <p v-if="unit" class="text-xs text-gray-500">{{ unit }}</p>
      </div>
    </div>
    
    <div class="relative">
      <Progress 
        :model-value="percentage" 
        :class="cn('h-3 bg-gradient-to-r from-soft-pink/20 to-gentle-mint/20', progressClass)" 
      />
      <div 
        class="absolute top-0 left-0 h-full bg-gradient-to-r from-soft-pink to-gentle-mint rounded-full transition-all duration-500 ease-out"
        :style="{ width: `${percentage}%` }"
      />
    </div>
    
    <div v-if="showMilestones" class="flex justify-between text-xs text-gray-500">
      <span v-for="milestone in milestones" :key="milestone" class="relative">
        {{ milestone }}
        <div 
          class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full bg-gray-300"
          :class="{ 'bg-soft-pink': current >= milestone }"
        />
      </span>
    </div>
    
    <div v-if="message" class="text-sm text-center p-3 bg-gradient-to-r from-light-coral/10 to-soft-blue/10 rounded-lg border border-light-coral/20">
      <p class="text-gray-700">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import Progress from './Progress.vue'

interface Props {
  title: string
  subtitle?: string
  current: number
  total: number
  unit?: string
  milestones?: number[]
  message?: string
  showMilestones?: boolean
  class?: string
  progressClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  showMilestones: false,
  milestones: () => []
})

const percentage = computed(() => Math.min(100, Math.max(0, (props.current / props.total) * 100)))
</script>