<template>
  <div
    ref="milestoneCardRef"
    :class="cn(
      'milestone-card relative overflow-hidden',
      'bg-off-white border border-light-gray rounded-lg p-6',
      'shadow-sm hover:shadow-md transition-shadow',
      isActive && 'ring-2 ring-blush-rose/20',
      className
    )"
  >
    <!-- Milestone badge -->
    <div 
      v-if="showBadge"
      class="absolute -top-2 -right-2 z-10"
    >
      <div class="flex items-center gap-2 px-3 py-1 bg-blush-rose/10 text-warm-graphite border border-blush-rose/30 rounded-full shadow-sm">
        <Star class="w-4 h-4" />
        <span class="text-xs font-medium">{{ getBadgeText() }}</span>
      </div>
    </div>

    <!-- Main slot content -->
    <div class="relative">
      <slot />
    </div>

    <!-- Memory book prompt -->
    <div
      v-if="showMemoryPrompt"
      class="absolute bottom-3 right-3"
    >
      <button
        @click="handleMemoryBookPrompt"
        class="flex items-center gap-2 px-3 py-1.5 bg-off-white border border-light-gray text-soft-charcoal text-xs rounded-md hover:bg-warm-gray transition-colors shadow-sm"
      >
        <BookOpen class="w-3 h-3" />
        <span>Save Memory</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { cn } from '~/components/ui/utils'
import { Star, BookOpen } from 'lucide-vue-next'

export interface MilestoneCardProps {
  milestoneType?: 'week' | 'trimester' | 'major' | 'appointment' | 'movement' | 'special'
  isActive?: boolean
  showBadge?: boolean
  showMemoryPrompt?: boolean
  week?: number
  milestoneTitle?: string
  celebrationDuration?: number
  className?: string
}

const props = withDefaults(defineProps<MilestoneCardProps>(), {
  milestoneType: 'week',
  isActive: false,
  showBadge: true,
  showMemoryPrompt: false,
  celebrationDuration: 5000
})

const emit = defineEmits<{
  memoryPrompt: [milestoneData: { type: string; week?: number; title?: string }]
  celebrationStart: []
  celebrationEnd: []
}>()

const milestoneCardRef = ref<HTMLElement>()

const getBadgeText = () => {
  switch (props.milestoneType) {
    case 'week':
      return props.week ? `Week ${props.week}` : 'Milestone'
    case 'trimester':
      return 'New Trimester'
    case 'major':
      return 'Big Milestone'
    case 'appointment':
      return 'Appointment'
    case 'movement':
      return 'Baby Moving'
    case 'special':
      return 'Special Moment'
    default:
      return 'Milestone'
  }
}

const handleMemoryBookPrompt = () => {
  emit('memoryPrompt', {
    type: props.milestoneType,
    week: props.week,
    title: props.milestoneTitle
  })
}

onMounted(() => {
  if (props.isActive) {
    emit('celebrationStart')
  }
})
</script>