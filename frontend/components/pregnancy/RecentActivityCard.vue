<template>
  <BaseCard variant="supportive" class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-primary font-semibold text-gray-800">
        Recent Activity
      </h3>
      <BaseButton 
        variant="outline" 
        size="sm"
        @click="$emit('viewAll')"
      >
        View All
      </BaseButton>
    </div>
    <div class="space-y-4">
      <div 
        v-for="activity in activities" 
        :key="activity.id"
        class="flex items-center space-x-4 p-3 bg-warm-neutral/10 rounded-lg"
      >
        <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" :class="activity.iconBg">
          <component :is="activity.icon" class="w-5 h-5" :class="activity.iconColor" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-800 truncate">{{ activity.title }}</p>
          <p class="text-xs text-gray-600 font-secondary">{{ activity.timestamp }}</p>
        </div>
      </div>
      <div v-if="activities.length === 0" class="text-center py-4">
        <p class="text-sm text-gray-500 font-secondary">
          Start your pregnancy journey by logging your first symptom or uploading a photo!
        </p>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { h } from 'vue'

interface Activity {
  id: string
  title: string
  timestamp: string
  type: 'photo' | 'symptom' | 'appointment' | 'weight' | 'milestone'
  icon: any
  iconBg: string
  iconColor: string
}

interface Props {
  activities?: Activity[]
}

const props = withDefaults(defineProps<Props>(), {
  activities: () => []
})

defineEmits<{
  viewAll: []
}>()

// Default activities if none provided (for demo purposes)
const defaultActivities: Activity[] = [
  {
    id: '1',
    title: 'Week 39 belly photo added',
    timestamp: 'Today at 2:30 PM',
    type: 'photo',
    icon: h('svg', {
      fill: 'none',
      stroke: 'currentColor',
      viewBox: '0 0 24 24'
    }, h('path', {
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'stroke-width': '2',
      d: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z'
    })),
    iconBg: 'bg-gentle-mint/20',
    iconColor: 'text-gentle-mint'
  }
]

const displayActivities = computed(() => {
  return props.activities.length > 0 ? props.activities.slice(0, 3) : defaultActivities
})
</script>