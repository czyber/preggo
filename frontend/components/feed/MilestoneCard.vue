<template>
  <div
    ref="milestoneCardRef"
    :class="cn(
      'milestone-card relative overflow-hidden',
      'bg-gradient-to-br from-soft-pink/10 via-gentle-mint/8 to-muted-lavender/6',
      'border-2 rounded-3xl p-1 shadow-lg transition-all duration-700',
      isActive && 'celebration-active',
      milestoneType && `milestone-${milestoneType}`,
      className
    )"
  >
    <!-- Golden celebration border animation -->
    <div 
      v-if="isActive"
      class="absolute inset-0 pointer-events-none celebration-border"
      :class="cn(
        'border-2 rounded-3xl',
        'bg-gradient-to-r from-soft-pink via-gentle-mint to-muted-lavender',
        'animate-border-glow'
      )"
    />
    
    <!-- Main card content wrapper -->
    <div
      :class="cn(
        'relative bg-white/60 backdrop-blur-sm rounded-3xl p-6',
        'border border-white/40 shadow-inner',
        'transition-all duration-500 hover:bg-white/70'
      )"
    >
      <!-- Milestone badge -->
      <div 
        v-if="showBadge"
        class="absolute -top-2 -right-2 z-10"
      >
        <div class="milestone-badge flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-soft-pink to-gentle-mint text-white font-bold rounded-2xl shadow-lg">
          <span class="text-lg animate-bounce">{{ getMilestoneIcon() }}</span>
          <span class="text-sm font-primary">{{ getBadgeText() }}</span>
        </div>
      </div>

      <!-- Floating celebration particles (background) -->
      <div v-if="isActive" class="absolute inset-0 pointer-events-none">
        <!-- Gentle sparkles -->
        <div
          v-for="i in 8"
          :key="`sparkle-${i}`"
          :class="cn(
            'absolute w-1.5 h-1.5 rounded-full opacity-60',
            `sparkle-float-${i}`,
            getSparkleColor(i)
          )"
          :style="getSparklePosition(i)"
        />
        
        <!-- Floating hearts -->
        <div
          v-for="i in 4"
          :key="`heart-${i}`"
          :class="cn(
            'absolute text-soft-pink opacity-50 text-sm pointer-events-none',
            `heart-float-${i}`
          )"
          :style="getHeartPosition(i)"
        >
          💕
        </div>
      </div>

      <!-- Main slot content -->
      <div class="relative z-10">
        <slot />
      </div>

      <!-- Memory book prompt overlay -->
      <div
        v-if="showMemoryPrompt"
        class="absolute bottom-4 right-4 z-20"
      >
        <button
          @click="handleMemoryBookPrompt"
          class="memory-prompt-btn flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-muted-lavender/90 to-soft-pink/90 text-white text-xs font-semibold rounded-xl hover:shadow-md transition-all duration-300 hover:scale-105"
        >
          <span class="text-sm">📖</span>
          <span>Save Memory</span>
        </button>
      </div>
    </div>

    <!-- Celebration glow effect -->
    <div
      v-if="isActive"
      class="absolute inset-0 pointer-events-none celebration-glow"
      :class="cn(
        'rounded-3xl opacity-30',
        'bg-gradient-to-br from-soft-pink/20 via-gentle-mint/15 to-muted-lavender/10'
      )"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { cn } from '~/components/ui/utils'

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

// Computed properties
const getBadgeText = () => {
  switch (props.milestoneType) {
    case 'week':
      return props.week ? `Week ${props.week}` : 'Milestone'
    case 'trimester':
      return 'New Trimester!'
    case 'major':
      return 'Big Milestone!'
    case 'appointment':
      return 'Appointment'
    case 'movement':
      return 'Baby Moving!'
    case 'special':
      return 'Special Moment'
    default:
      return 'Milestone'
  }
}

const getMilestoneIcon = () => {
  const icons = {
    week: '⭐',
    trimester: '🌟',
    major: '🎉',
    appointment: '🩺',
    movement: '👶',
    special: '💫'
  }
  return icons[props.milestoneType] || '⭐'
}

const getSparkleColor = (index: number) => {
  const colors = [
    'bg-soft-pink',
    'bg-gentle-mint', 
    'bg-muted-lavender',
    'bg-light-coral'
  ]
  return colors[index % colors.length]
}

const getSparklePosition = (index: number) => {
  const positions = [
    { top: '15%', left: '20%' },
    { top: '25%', right: '25%' },
    { top: '40%', left: '15%' },
    { top: '50%', right: '30%' },
    { top: '65%', left: '25%' },
    { top: '75%', right: '20%' },
    { top: '30%', left: '60%' },
    { top: '80%', right: '50%' }
  ]
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.3}s`
  
  return {
    ...position,
    animationDelay
  }
}

const getHeartPosition = (index: number) => {
  const positions = [
    { top: '20%', left: '30%' },
    { top: '45%', right: '35%' },
    { top: '70%', left: '40%' },
    { top: '55%', right: '45%' }
  ]
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.8}s`
  
  return {
    ...position,
    animationDelay
  }
}

// Event handlers
const handleMemoryBookPrompt = () => {
  emit('memoryPrompt', {
    type: props.milestoneType,
    week: props.week,
    title: props.milestoneTitle
  })
}

// Lifecycle and watchers
watch(() => props.isActive, (newValue) => {
  if (newValue) {
    emit('celebrationStart')
    // Auto-deactivate after duration
    setTimeout(() => {
      emit('celebrationEnd')
    }, props.celebrationDuration)
  }
})

onMounted(() => {
  if (props.isActive) {
    emit('celebrationStart')
  }
})
</script>

<style scoped>
/* Milestone card base styling */
.milestone-card {
  position: relative;
  transform-origin: center;
}

/* Celebration border animation */
.celebration-border {
  background: linear-gradient(45deg, #F8BBD0, #B2DFDB, #E1BEE7, #FFCDD2);
  background-size: 300% 300%;
  animation: celebration-border-flow 3s ease-in-out infinite;
}

@keyframes celebration-border-flow {
  0%, 100% { background-position: 0% 50%; }
  25% { background-position: 100% 50%; }
  50% { background-position: 100% 100%; }
  75% { background-position: 0% 100%; }
}

/* Milestone badge animations */
.milestone-badge {
  animation: milestone-badge-appear 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 15px rgba(248, 187, 208, 0.3);
}

@keyframes milestone-badge-appear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Celebration active state */
.celebration-active {
  animation: celebration-card-glow 2s ease-in-out infinite;
}

@keyframes celebration-card-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(248, 187, 208, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(248, 187, 208, 0.5), 0 0 40px rgba(178, 223, 219, 0.3);
  }
}

/* Sparkle float animations */
.sparkle-float-1 { animation: gentle-sparkle-float 3s ease-in-out infinite; }
.sparkle-float-2 { animation: gentle-sparkle-float 3.2s ease-in-out infinite; }
.sparkle-float-3 { animation: gentle-sparkle-float 2.8s ease-in-out infinite; }
.sparkle-float-4 { animation: gentle-sparkle-float 3.5s ease-in-out infinite; }
.sparkle-float-5 { animation: gentle-sparkle-float 2.5s ease-in-out infinite; }
.sparkle-float-6 { animation: gentle-sparkle-float 3.8s ease-in-out infinite; }
.sparkle-float-7 { animation: gentle-sparkle-float 2.9s ease-in-out infinite; }
.sparkle-float-8 { animation: gentle-sparkle-float 3.3s ease-in-out infinite; }

@keyframes gentle-sparkle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.6;
  }
  25% {
    transform: translateY(-8px) scale(1.2);
    opacity: 1;
  }
  75% {
    transform: translateY(-4px) scale(0.9);
    opacity: 0.8;
  }
}

/* Heart float animations */
.heart-float-1 { animation: gentle-heart-float 4s ease-in-out infinite; }
.heart-float-2 { animation: gentle-heart-float 4.5s ease-in-out infinite; }
.heart-float-3 { animation: gentle-heart-float 3.5s ease-in-out infinite; }
.heart-float-4 { animation: gentle-heart-float 4.2s ease-in-out infinite; }

@keyframes gentle-heart-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-12px) rotate(10deg) scale(1.1);
    opacity: 0.8;
  }
}

/* Memory prompt button */
.memory-prompt-btn {
  animation: memory-prompt-pulse 2s ease-in-out infinite;
}

@keyframes memory-prompt-pulse {
  0%, 100% {
    opacity: 0.9;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

/* Celebration glow effect */
.celebration-glow {
  animation: celebration-glow-pulse 3s ease-in-out infinite;
}

@keyframes celebration-glow-pulse {
  0%, 100% {
    opacity: 0.2;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.02);
  }
}

/* Milestone type specific styling */
.milestone-week {
  border-color: theme('colors.soft-pink');
}

.milestone-trimester {
  border-color: theme('colors.gentle-mint');
}

.milestone-major {
  border-color: theme('colors.muted-lavender');
}

.milestone-appointment {
  border-color: theme('colors.light-coral');
}

.milestone-movement {
  border-color: theme('colors.soft-blue');
}

.milestone-special {
  border-image: linear-gradient(45deg, #F8BBD0, #B2DFDB, #E1BEE7) 1;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .milestone-card {
    margin: 0 -0.5rem;
    border-radius: 1.5rem;
  }
  
  .milestone-badge {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }
  
  .memory-prompt-btn {
    font-size: 0.7rem;
    padding: 0.4rem 0.6rem;
  }
}

/* Accessibility - reduced motion */
@media (prefers-reduced-motion: reduce) {
  .sparkle-float-1, .sparkle-float-2, .sparkle-float-3, .sparkle-float-4,
  .sparkle-float-5, .sparkle-float-6, .sparkle-float-7, .sparkle-float-8,
  .heart-float-1, .heart-float-2, .heart-float-3, .heart-float-4,
  .celebration-border,
  .celebration-active,
  .celebration-glow,
  .memory-prompt-btn {
    animation: none;
  }
  
  .milestone-badge {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

/* Focus states for accessibility */
.memory-prompt-btn:focus {
  outline: 2px solid theme('colors.soft-pink');
  outline-offset: 2px;
}
</style>
