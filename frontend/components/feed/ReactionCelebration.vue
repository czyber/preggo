<template>
  <div 
    ref="celebrationRef"
    class="reaction-celebration"
    :class="{ 'is-active': isActive }"
  >
    <!-- Celebration Particles Container -->
    <div 
      ref="particlesRef"
      class="celebration-particles absolute inset-0 pointer-events-none overflow-hidden"
      role="presentation"
      aria-hidden="true"
    >
      <!-- Dynamic particles will be injected here -->
    </div>

    <!-- Main Content Slot -->
    <slot />

    <!-- Celebration Overlay Effects -->
    <div 
      v-if="showOverlay"
      class="celebration-overlay absolute inset-0 pointer-events-none"
      :class="[
        `celebration-${celebrationType}`,
        { 'overlay-active': isActive }
      ]"
    >
      <!-- Milestone Banner -->
      <div 
        v-if="celebrationType === 'milestone'"
        class="milestone-banner absolute top-2 left-2 right-2 bg-gradient-to-r from-soft-pink/90 to-gentle-mint/80 rounded-lg p-3 shadow-lg backdrop-blur-sm"
      >
        <div class="flex items-center gap-2">
          <span class="text-xl animate-bounce">🎉</span>
          <div>
            <p class="text-sm font-bold text-white drop-shadow-sm">Milestone Celebrated!</p>
            <p class="text-xs text-white/90">{{ celebrationMessage }}</p>
          </div>
        </div>
      </div>

      <!-- Special Reaction Highlight -->
      <div 
        v-if="celebrationType === 'special-reaction'"
        class="special-reaction-highlight absolute bottom-2 left-2 right-2"
      >
        <div class="bg-white/95 rounded-lg p-2 shadow-md backdrop-blur-sm border border-soft-pink/30">
          <div class="flex items-center gap-2">
            <span class="text-lg">{{ reactionEmoji }}</span>
            <p class="text-xs font-medium text-gray-800">{{ celebrationMessage }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useCelebrationAnimation, useAccessibleAnimations } from '~/composables/useAnimations'

interface Props {
  celebrationType: 'milestone' | 'special-reaction' | 'family-love' | 'first-reaction'
  reactionType?: string
  reactionEmoji?: string
  celebrationMessage?: string
  duration?: number
  intensity?: 'gentle' | 'moderate' | 'festive'
  showOverlay?: boolean
  autoTrigger?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  duration: 3000,
  intensity: 'moderate',
  showOverlay: true,
  autoTrigger: false,
  celebrationMessage: 'Your family is celebrating!'
})

const emit = defineEmits<{
  celebrationStart: []
  celebrationEnd: []
}>()

// Animation composables
const { celebrateSparkles, celebrateHearts, celebrateConfetti, celebrateMilestone } = useCelebrationAnimation()
const { reducedMotion, animateWithRespect, addAriaLiveRegion } = useAccessibleAnimations()

// Local state
const celebrationRef = ref<HTMLElement>()
const particlesRef = ref<HTMLElement>()
const isActive = ref(false)
const celebrationTimeout = ref<NodeJS.Timeout | null>(null)

// Celebration configuration
const celebrationConfig = {
  milestone: {
    particles: ['confetti', 'sparkles', 'hearts'],
    colors: ['#F8BBD0', '#E1BEE7', '#B2DFDB', '#FFCDD2'],
    intensity: { gentle: 8, moderate: 15, festive: 25 },
    message: 'Amazing milestone reached!'
  },
  'special-reaction': {
    particles: ['sparkles', 'hearts'],
    colors: ['#F8BBD0', '#E1BEE7', '#B2DFDB'],
    intensity: { gentle: 4, moderate: 8, festive: 12 },
    message: 'Special family reaction!'
  },
  'family-love': {
    particles: ['hearts', 'sparkles'],
    colors: ['#F8BBD0', '#FFCDD2', '#E1BEE7'],
    intensity: { gentle: 6, moderate: 10, festive: 16 },
    message: 'Family love celebration!'
  },
  'first-reaction': {
    particles: ['sparkles'],
    colors: ['#B2DFDB', '#F8BBD0'],
    intensity: { gentle: 3, moderate: 6, festive: 10 },
    message: 'First family reaction!'
  }
}

// Methods
function startCelebration() {
  if (isActive.value) return

  isActive.value = true
  emit('celebrationStart')

  // Add accessibility announcement
  const config = celebrationConfig[props.celebrationType]
  addAriaLiveRegion(props.celebrationMessage || config.message, 'polite')

  // Create celebration particles based on type and intensity
  createCelebrationParticles()

  // Auto-end celebration after duration
  celebrationTimeout.value = setTimeout(() => {
    endCelebration()
  }, props.duration)
}

function endCelebration() {
  isActive.value = false
  emit('celebrationEnd')

  if (celebrationTimeout.value) {
    clearTimeout(celebrationTimeout.value)
    celebrationTimeout.value = null
  }

  // Clean up particles
  cleanupParticles()
}

function createCelebrationParticles() {
  if (!particlesRef.value) return

  const config = celebrationConfig[props.celebrationType]
  const particleCount = config.intensity[props.intensity]
  const particles = config.particles

  // Respect user's motion preferences
  animateWithRespect(
    particlesRef.value,
    () => {
      // Full animation for users who prefer motion
      particles.forEach((particleType, index) => {
        setTimeout(() => {
          createParticleType(particleType, Math.ceil(particleCount / particles.length))
        }, index * 200)
      })
    },
    () => {
      // Reduced animation - just add a gentle glow
      if (celebrationRef.value) {
        celebrationRef.value.classList.add('celebration-glow-only')
        setTimeout(() => {
          celebrationRef.value?.classList.remove('celebration-glow-only')
        }, 1000)
      }
    }
  )
}

function createParticleType(type: string, count: number) {
  if (!particlesRef.value) return

  switch (type) {
    case 'sparkles':
      celebrateSparkles(particlesRef.value, count)
      break
    case 'hearts':
      celebrateHearts(particlesRef.value, count)
      break
    case 'confetti':
      celebrateConfetti(particlesRef.value, count)
      break
  }
}

function cleanupParticles() {
  if (!particlesRef.value) return

  // Remove all dynamically created particles
  const particles = particlesRef.value.querySelectorAll('.celebration-particle')
  particles.forEach(particle => {
    particle.remove()
  })
}

// Pregnancy-specific particle creation
function createPregnancySparkle(x: number, y: number, color: string) {
  if (!particlesRef.value) return

  const sparkle = document.createElement('div')
  sparkle.className = 'celebration-particle sparkle-particle absolute pointer-events-none'
  sparkle.style.cssText = `
    left: ${x}px;
    top: ${y}px;
    width: 8px;
    height: 8px;
    background: ${color};
    border-radius: 50%;
    animation: sparkle-celebration 1.5s ease-out forwards;
    z-index: 1000;
  `
  
  // Add sparkle symbol
  sparkle.innerHTML = '✨'
  sparkle.style.display = 'flex'
  sparkle.style.alignItems = 'center'
  sparkle.style.justifyContent = 'center'
  sparkle.style.fontSize = '8px'
  
  particlesRef.value.appendChild(sparkle)
  
  // Clean up after animation
  setTimeout(() => {
    if (sparkle.parentNode) {
      sparkle.parentNode.removeChild(sparkle)
    }
  }, 1500)
}

function createPregnancyHeart(x: number, y: number, color: string) {
  if (!particlesRef.value) return

  const heart = document.createElement('div')
  heart.className = 'celebration-particle heart-particle absolute pointer-events-none'
  heart.style.cssText = `
    left: ${x}px;
    top: ${y}px;
    font-size: 12px;
    animation: heart-float 2s ease-out forwards;
    z-index: 1000;
    --drift: ${(Math.random() - 0.5) * 40}px;
  `
  
  heart.innerHTML = '💕'
  
  particlesRef.value.appendChild(heart)
  
  // Clean up after animation
  setTimeout(() => {
    if (heart.parentNode) {
      heart.parentNode.removeChild(heart)
    }
  }, 2000)
}

function createPregnancyConfetti(x: number, y: number, color: string) {
  if (!particlesRef.value) return

  const confetti = document.createElement('div')
  confetti.className = 'celebration-particle confetti-particle absolute pointer-events-none'
  confetti.style.cssText = `
    left: ${x}px;
    top: ${y}px;
    width: 6px;
    height: 12px;
    background: ${color};
    border-radius: 2px;
    animation: confetti-burst 2.5s ease-out forwards;
    z-index: 1000;
  `
  
  particlesRef.value.appendChild(confetti)
  
  // Clean up after animation
  setTimeout(() => {
    if (confetti.parentNode) {
      confetti.parentNode.removeChild(confetti)
    }
  }, 2500)
}

// Trigger celebration manually
function triggerCelebration() {
  startCelebration()
}

// Expose methods to parent
defineExpose({
  triggerCelebration,
  endCelebration,
  isActive: readonly(isActive)
})

// Lifecycle
onMounted(() => {
  if (props.autoTrigger) {
    nextTick(() => {
      startCelebration()
    })
  }
})

onUnmounted(() => {
  if (celebrationTimeout.value) {
    clearTimeout(celebrationTimeout.value)
  }
  cleanupParticles()
})

// Watch for celebration type changes
watch(() => props.celebrationType, () => {
  if (isActive.value) {
    endCelebration()
    nextTick(() => {
      startCelebration()
    })
  }
})
</script>

<style scoped>
/* Base celebration container */
.reaction-celebration {
  @apply relative;
  transition: all 0.3s ease;
}

.reaction-celebration.is-active {
  @apply transform scale-[1.02];
}

/* Celebration particles container */
.celebration-particles {
  @apply z-10;
}

/* Celebration overlay effects */
.celebration-overlay {
  @apply transition-opacity duration-300;
  opacity: 0;
}

.celebration-overlay.overlay-active {
  opacity: 1;
}

/* Milestone specific styling */
.celebration-milestone {
  @apply relative;
}

.milestone-banner {
  animation: milestone-banner-appear 0.4s ease-out forwards;
}

@keyframes milestone-banner-appear {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Special reaction highlighting */
.celebration-special-reaction {
  @apply relative;
}

.special-reaction-highlight {
  animation: special-reaction-slide 0.3s ease-out forwards;
}

@keyframes special-reaction-slide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Family love celebration */
.celebration-family-love {
  @apply relative;
}

.celebration-family-love.overlay-active {
  background: radial-gradient(circle at center, rgba(248, 187, 208, 0.1) 0%, transparent 70%);
}

/* First reaction celebration */
.celebration-first-reaction {
  @apply relative;
}

.celebration-first-reaction.overlay-active::before {
  content: '';
  @apply absolute inset-0 bg-gradient-to-r from-gentle-mint/10 to-soft-pink/10 rounded-lg;
  animation: gentle-pulse 2s ease-in-out infinite;
}

/* Particle animations */
@keyframes sparkle-celebration {
  0% {
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  20% {
    opacity: 1;
    transform: scale(1) rotate(45deg);
  }
  80% {
    opacity: 1;
    transform: scale(1.2) rotate(315deg);
  }
  100% {
    opacity: 0;
    transform: scale(0) rotate(360deg);
  }
}

@keyframes heart-float {
  0% {
    opacity: 0;
    transform: translateY(0) translateX(0) scale(0.8);
  }
  10% {
    opacity: 1;
    transform: translateY(-10px) translateX(5px) scale(1);
  }
  90% {
    opacity: 1;
    transform: translateY(-60px) translateX(var(--drift)) scale(1.1);
  }
  100% {
    opacity: 0;
    transform: translateY(-80px) translateX(var(--drift)) scale(0.8);
  }
}

@keyframes confetti-burst {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translateY(100px) scale(0.5) rotate(720deg);
  }
}

/* Celebration glow for reduced motion users */
.celebration-glow-only {
  animation: celebration-glow 1s ease-in-out;
}

@keyframes celebration-glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(248, 187, 208, 0);
  }
  50% {
    box-shadow: 0 0 20px rgba(248, 187, 208, 0.4);
  }
}

/* Accessibility - respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .reaction-celebration.is-active {
    transform: none;
  }
  
  .milestone-banner,
  .special-reaction-highlight {
    animation: none;
  }
  
  .celebration-particle {
    display: none !important;
  }
  
  .celebration-overlay.overlay-active {
    opacity: 0.3;
  }
  
  .celebration-glow-only {
    animation: celebration-glow 1s ease-in-out;
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .milestone-banner {
    @apply p-2 text-xs;
  }
  
  .special-reaction-highlight {
    @apply p-1.5;
  }
  
  .celebration-particle {
    @apply scale-75;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .milestone-banner {
    @apply bg-gray-900 text-white border border-gray-600;
  }
  
  .special-reaction-highlight {
    @apply bg-white text-gray-900 border border-gray-900;
  }
}

/* Focus management */
.reaction-celebration:focus-within {
  @apply outline-2 outline-offset-2 outline-soft-pink;
}

/* Particle cleanup */
.celebration-particle {
  will-change: transform, opacity;
}

/* Performance optimizations */
.celebration-particles,
.celebration-overlay {
  transform: translateZ(0);
}
</style>
