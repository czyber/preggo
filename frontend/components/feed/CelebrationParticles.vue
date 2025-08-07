<template>
  <div
    ref="particleContainer"
    :class="cn(
      'celebration-particles absolute inset-0 pointer-events-none overflow-hidden',
      isActive && 'particles-active',
      className
    )"
    :style="{ zIndex: zIndex }"
  >
    <!-- Confetti particles -->
    <div
      v-for="particle in confettiParticles"
      :key="`confetti-${particle.id}`"
      class="absolute confetti-particle"
      :style="particle.style"
    >
      <div
        :class="cn(
          'confetti-piece',
          particle.shape,
          particle.color
        )"
        :style="{ animationDelay: `${particle.delay}s` }"
      />
    </div>

    <!-- Sparkle particles -->
    <div
      v-for="particle in sparkleParticles"
      :key="`sparkle-${particle.id}`"
      class="absolute sparkle-particle"
      :style="particle.style"
    >
      <div
        :class="cn(
          'sparkle-piece',
          particle.color,
          particle.size
        )"
        :style="{ animationDelay: `${particle.delay}s` }"
      >
        ✨
      </div>
    </div>

    <!-- Heart particles -->
    <div
      v-for="particle in heartParticles"
      :key="`heart-${particle.id}`"
      class="absolute heart-particle"
      :style="particle.style"
    >
      <div
        :class="cn(
          'heart-piece',
          particle.color,
          particle.size
        )"
        :style="{ animationDelay: `${particle.delay}s` }"
      >
        {{ particle.emoji }}
      </div>
    </div>

    <!-- Star burst particles -->
    <div
      v-for="particle in starBurstParticles"
      :key="`star-${particle.id}`"
      class="absolute star-particle"
      :style="particle.style"
    >
      <div
        :class="cn(
          'star-piece',
          particle.color
        )"
        :style="{ animationDelay: `${particle.delay}s` }"
      >
        ⭐
      </div>
    </div>

    <!-- Floating bubble particles -->
    <div
      v-for="particle in bubbleParticles"
      :key="`bubble-${particle.id}`"
      class="absolute bubble-particle"
      :style="particle.style"
    >
      <div
        :class="cn(
          'bubble-piece',
          particle.size,
          particle.opacity
        )"
        :style="{ animationDelay: `${particle.delay}s` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { cn } from '~/components/ui/utils'

type ParticleType = 'confetti' | 'sparkles' | 'hearts' | 'mixed' | 'gentle' | 'celebration'
type AnimationTiming = 'instant' | 'gentle' | 'burst' | 'cascade'

interface ParticleProps {
  type?: ParticleType
  intensity?: 'light' | 'medium' | 'heavy'
  duration?: number
  timing?: AnimationTiming
  isActive?: boolean
  autoStart?: boolean
  containerBounds?: boolean
  zIndex?: number
  className?: string
}

interface Particle {
  id: number
  style: Record<string, string>
  delay: number
  color: string
  size?: string
  shape?: string
  emoji?: string
  opacity?: string
}

const props = withDefaults(defineProps<ParticleProps>(), {
  type: 'mixed',
  intensity: 'medium',
  duration: 3000,
  timing: 'gentle',
  isActive: false,
  autoStart: false,
  containerBounds: true,
  zIndex: 10
})

const emit = defineEmits<{
  animationStart: []
  animationComplete: []
  particlePhaseComplete: [phase: string]
}>()

const particleContainer = ref<HTMLElement>()
const animationActive = ref(false)
const animationTimeout = ref<NodeJS.Timeout>()

// Pregnancy-themed colors
const pregnancyColors = [
  'text-soft-pink',
  'text-gentle-mint', 
  'text-muted-lavender',
  'text-light-coral',
  'text-soft-blue',
  'text-warm-beige'
]

const confettiColors = [
  'bg-soft-pink',
  'bg-gentle-mint', 
  'bg-muted-lavender',
  'bg-light-coral'
]

// Particle generation functions
const generateConfettiParticles = () => {
  const intensity = {
    light: 8,
    medium: 15,
    heavy: 25
  }
  
  const count = intensity[props.intensity]
  const particles: Particle[] = []
  
  for (let i = 0; i < count; i++) {
    const startX = Math.random() * 100
    const endX = startX + (Math.random() - 0.5) * 30
    const rotation = Math.random() * 360
    const delay = props.timing === 'instant' ? 0 : Math.random() * 0.8
    
    particles.push({
      id: i,
      style: {
        left: `${startX}%`,
        top: '-10px',
        '--end-x': `${endX}%`,
        '--rotation': `${rotation}deg`,
        '--fall-duration': `${2 + Math.random()}s`
      },
      delay,
      color: confettiColors[Math.floor(Math.random() * confettiColors.length)],
      shape: Math.random() > 0.5 ? 'confetti-square' : 'confetti-circle'
    })
  }
  
  return particles
}

const generateSparkleParticles = () => {
  const intensity = {
    light: 6,
    medium: 12,
    heavy: 20
  }
  
  const count = intensity[props.intensity]
  const particles: Particle[] = []
  
  for (let i = 0; i < count; i++) {
    const x = 20 + Math.random() * 60  // Keep sparkles more centered
    const y = 20 + Math.random() * 60
    const delay = props.timing === 'instant' ? 0 : Math.random() * 1.2
    
    particles.push({
      id: i,
      style: {
        left: `${x}%`,
        top: `${y}%`,
        '--sparkle-duration': `${1.5 + Math.random() * 0.5}s`
      },
      delay,
      color: pregnancyColors[Math.floor(Math.random() * pregnancyColors.length)],
      size: Math.random() > 0.7 ? 'text-lg' : 'text-base'
    })
  }
  
  return particles
}

const generateHeartParticles = () => {
  const intensity = {
    light: 4,
    medium: 8,
    heavy: 12
  }
  
  const count = intensity[props.intensity]
  const particles: Particle[] = []
  const heartEmojis = ['💕', '💖', '💗', '💝', '❤️', '🤍']
  
  for (let i = 0; i < count; i++) {
    const startX = Math.random() * 100
    const endY = Math.random() * -50 - 20  // Float upward
    const delay = props.timing === 'instant' ? 0 : Math.random() * 1.5
    
    particles.push({
      id: i,
      style: {
        left: `${startX}%`,
        bottom: '0px',
        '--end-y': `${endY}px`,
        '--heart-duration': `${3 + Math.random()}s`
      },
      delay,
      color: pregnancyColors[Math.floor(Math.random() * pregnancyColors.length)],
      size: Math.random() > 0.6 ? 'text-lg' : 'text-base',
      emoji: heartEmojis[Math.floor(Math.random() * heartEmojis.length)]
    })
  }
  
  return particles
}

const generateStarBurstParticles = () => {
  const intensity = {
    light: 5,
    medium: 10,
    heavy: 15
  }
  
  const count = intensity[props.intensity]
  const particles: Particle[] = []
  
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * 360
    const distance = 50 + Math.random() * 30
    const x = 50 + Math.cos(angle * Math.PI / 180) * distance
    const y = 50 + Math.sin(angle * Math.PI / 180) * distance
    const delay = props.timing === 'burst' ? i * 0.1 : Math.random() * 0.5
    
    particles.push({
      id: i,
      style: {
        left: '50%',
        top: '50%',
        '--target-x': `${x}%`,
        '--target-y': `${y}%`,
        '--burst-duration': `${1 + Math.random() * 0.5}s`
      },
      delay,
      color: pregnancyColors[Math.floor(Math.random() * pregnancyColors.length)]
    })
  }
  
  return particles
}

const generateBubbleParticles = () => {
  const intensity = {
    light: 3,
    medium: 6,
    heavy: 10
  }
  
  const count = intensity[props.intensity]
  const particles: Particle[] = []
  
  for (let i = 0; i < count; i++) {
    const x = Math.random() * 100
    const y = Math.random() * 100
    const delay = Math.random() * 2
    
    particles.push({
      id: i,
      style: {
        left: `${x}%`,
        top: `${y}%`,
        '--bubble-duration': `${4 + Math.random() * 2}s`
      },
      delay,
      color: '',
      size: Math.random() > 0.5 ? 'bubble-lg' : 'bubble-sm',
      opacity: Math.random() > 0.5 ? 'opacity-30' : 'opacity-20'
    })
  }
  
  return particles
}

// Computed particle arrays
const confettiParticles = computed(() => {
  if (!animationActive.value || (props.type !== 'confetti' && props.type !== 'mixed' && props.type !== 'celebration')) {
    return []
  }
  return generateConfettiParticles()
})

const sparkleParticles = computed(() => {
  if (!animationActive.value || (props.type !== 'sparkles' && props.type !== 'mixed' && props.type !== 'gentle' && props.type !== 'celebration')) {
    return []
  }
  return generateSparkleParticles()
})

const heartParticles = computed(() => {
  if (!animationActive.value || (props.type !== 'hearts' && props.type !== 'mixed' && props.type !== 'gentle')) {
    return []
  }
  return generateHeartParticles()
})

const starBurstParticles = computed(() => {
  if (!animationActive.value || props.type !== 'celebration') {
    return []
  }
  return generateStarBurstParticles()
})

const bubbleParticles = computed(() => {
  if (!animationActive.value || (props.type !== 'gentle' && props.type !== 'mixed')) {
    return []
  }
  return generateBubbleParticles()
})

// Methods
const startAnimation = () => {
  if (animationActive.value) return
  
  animationActive.value = true
  emit('animationStart')
  
  // Clear any existing timeout
  if (animationTimeout.value) {
    clearTimeout(animationTimeout.value)
  }
  
  // Set timeout to end animation
  animationTimeout.value = setTimeout(() => {
    animationActive.value = false
    emit('animationComplete')
  }, props.duration)
}

const stopAnimation = () => {
  animationActive.value = false
  if (animationTimeout.value) {
    clearTimeout(animationTimeout.value)
  }
  emit('animationComplete')
}

// Watchers
watch(() => props.isActive, (newValue) => {
  if (newValue) {
    startAnimation()
  } else {
    stopAnimation()
  }
})

// Lifecycle
onMounted(() => {
  if (props.autoStart || props.isActive) {
    startAnimation()
  }
})

onUnmounted(() => {
  if (animationTimeout.value) {
    clearTimeout(animationTimeout.value)
  }
})

// Expose methods for parent components
defineExpose({
  startAnimation,
  stopAnimation,
  isAnimating: computed(() => animationActive.value)
})
</script>

<style scoped>
/* Confetti animations */
.confetti-particle {
  width: 8px;
  height: 8px;
}

.confetti-piece {
  width: 100%;
  height: 100%;
  animation: confetti-fall var(--fall-duration, 2s) ease-in forwards;
}

.confetti-square {
  width: 6px;
  height: 6px;
}

.confetti-circle {
  width: 4px;
  height: 4px;
  border-radius: 50%;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) translateX(var(--end-x, 0%)) rotate(var(--rotation, 360deg));
    opacity: 0;
  }
}

/* Sparkle animations */
.sparkle-piece {
  animation: sparkle-twinkle var(--sparkle-duration, 1.5s) ease-in-out infinite;
}

@keyframes sparkle-twinkle {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }
}

/* Heart animations */
.heart-piece {
  animation: heart-float-up var(--heart-duration, 3s) ease-out forwards;
}

@keyframes heart-float-up {
  0% {
    transform: translateY(0) scale(0.8);
    opacity: 0.8;
  }
  20% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(var(--end-y, -100px)) scale(0.6);
    opacity: 0;
  }
}

/* Star burst animations */
.star-piece {
  animation: star-burst var(--burst-duration, 1s) ease-out forwards;
}

@keyframes star-burst {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translate(calc(var(--target-x, 50%) - 50%), calc(var(--target-y, 50%) - 50%)) scale(1);
    opacity: 0;
  }
}

/* Bubble animations */
.bubble-piece {
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), rgba(248, 187, 208, 0.2));
  animation: bubble-float var(--bubble-duration, 4s) ease-in-out infinite;
}

.bubble-sm {
  width: 12px;
  height: 12px;
}

.bubble-lg {
  width: 20px;
  height: 20px;
}

@keyframes bubble-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-20px) scale(1.1);
    opacity: 0.6;
  }
}

/* Container states */
.particles-active {
  pointer-events: none;
}

/* Pregnancy-themed particle colors */
.text-soft-pink { color: #F8BBD0; }
.text-gentle-mint { color: #B2DFDB; }
.text-muted-lavender { color: #E1BEE7; }
.text-light-coral { color: #FFCDD2; }
.text-soft-blue { color: #BBDEFB; }
.text-warm-beige { color: #FFF3E0; }

.bg-soft-pink { background-color: #F8BBD0; }
.bg-gentle-mint { background-color: #B2DFDB; }
.bg-muted-lavender { background-color: #E1BEE7; }
.bg-light-coral { background-color: #FFCDD2; }

/* Accessibility - reduced motion */
@media (prefers-reduced-motion: reduce) {
  .confetti-piece,
  .sparkle-piece,
  .heart-piece,
  .star-piece,
  .bubble-piece {
    animation-duration: 0.1s !important;
    animation-iteration-count: 1 !important;
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .confetti-particle {
    width: 6px;
    height: 6px;
  }
  
  .confetti-square {
    width: 4px;
    height: 4px;
  }
  
  .confetti-circle {
    width: 3px;
    height: 3px;
  }
  
  .bubble-sm {
    width: 8px;
    height: 8px;
  }
  
  .bubble-lg {
    width: 14px;
    height: 14px;
  }
}
</style>
