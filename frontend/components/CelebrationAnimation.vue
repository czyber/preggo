<template>
  <Teleport to="body">
    <div 
      v-if="show" 
      class="fixed inset-0 z-50 flex items-center justify-center celebration-overlay"
      role="status"
      aria-live="polite"
      aria-label="Celebration animation"
      @wheel.prevent
      @touchmove.prevent
      @scroll.prevent
      @keydown.prevent="preventScrollKeys"
    >
      <!-- Background overlay with subtle glow -->
      <div class="absolute inset-0 bg-warm-neutral/10 backdrop-blur-sm animate-fade-in" />
      
      <div class="relative">
        <!-- Ripple Effects -->
        <div 
          v-for="(ripple, index) in 3" 
          :key="`ripple-${index}`"
          class="absolute inset-0 w-32 h-32 -left-16 -top-16 rounded-full border-2 ripple"
          :class="getRippleClass(index)"
        />
        
        <!-- Central Heart Container -->
        <div 
          class="relative z-10 w-16 h-16 flex items-center justify-center heart-container"
        >
          <!-- Glow Effect -->
          <div class="absolute inset-0 w-20 h-20 -left-2 -top-2 rounded-full bg-soft-pink/30 blur-lg glow-effect" />
          
          <!-- Heart Icon -->
          <div class="relative z-10 heart-icon">
            <svg 
              class="w-8 h-8 text-soft-pink drop-shadow-sm" 
              fill="currentColor" 
              viewBox="0 0 24 24"
            >
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </div>
        </div>
        
        <!-- Floating Sparkles -->
        <div 
          v-for="sparkle in sparkles" 
          :key="`sparkle-${sparkle.id}`"
          class="absolute w-2 h-2 sparkle"
          :style="sparkle.style"
        >
          <div 
            class="w-full h-full rounded-full sparkle-element"
            :class="getSparkleClass(sparkle.id)"
            :style="{ animationDelay: `${sparkle.delay}s` }"
          />
        </div>
        
        <!-- Message -->
        <div class="absolute top-20 left-1/2 transform -translate-x-1/2 text-center message-container">
          <div class="bg-white/30 backdrop-blur-sm rounded-2xl px-8 sm:px-10 py-5 shadow-sm border border-white/10 mx-4 min-w-80 sm:min-w-96">
            <h3 class="text-xl font-primary font-semibold text-gray-900 mb-2 animate-slide-up drop-shadow-sm">
              {{ message.title }}
            </h3>
            <p class="text-base font-secondary text-gray-800 animate-slide-up leading-relaxed drop-shadow-sm" style="animation-delay: 0.2s;">
              {{ message.subtitle }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const { show, message, sparkles } = useCelebration()

const getRippleClass = (index: number) => {
  const classes = [
    'ripple-1 border-soft-pink/40',
    'ripple-2 border-muted-lavender/35', 
    'ripple-3 border-gentle-mint/30'
  ]
  return classes[index]
}

const getSparkleClass = (index: number) => {
  const colors = [
    'bg-soft-pink',
    'bg-muted-lavender', 
    'bg-gentle-mint',
    'bg-light-coral'
  ]
  return `${colors[index % colors.length]} sparkle-float`
}

// Prevent scroll keys like arrow keys, space, etc.
const preventScrollKeys = (event: KeyboardEvent) => {
  const scrollKeys = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' ']
  if (scrollKeys.includes(event.key)) {
    event.preventDefault()
  }
}
</script>

<style scoped>
/* Global scroll prevention when celebration is active */
:global(body.celebration-active) {
  overflow: hidden !important;
  position: fixed !important;
  width: 100% !important;
  height: 100% !important;
}

:global(html:has(body.celebration-active)) {
  overflow: hidden !important;
}

/* Celebration overlay prevents all interactions with background */
.celebration-overlay {
  touch-action: none;
  overscroll-behavior: contain;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .celebration-overlay * {
    animation-duration: 0.1s !important;
    animation-iteration-count: 1 !important;
  }
}

/* Ripple animations */
.ripple-1 {
  animation: ripple 2s ease-out forwards;
  animation-delay: 0s;
}

.ripple-2 {
  animation: ripple 2s ease-out forwards;
  animation-delay: 0.3s;
}

.ripple-3 {
  animation: ripple 2s ease-out forwards;
  animation-delay: 0.6s;
}

@keyframes ripple {
  0% {
    transform: scale(0);
    opacity: 0.8;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
}

/* Heart animations */
.heart-container {
  animation: heartEmerge 0.8s ease-out forwards;
}

@keyframes heartEmerge {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  70% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.heart-icon {
  animation: heartPulse 0.6s ease-in-out;
  animation-delay: 0.8s;
}

@keyframes heartPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* Glow animation */
.glow-effect {
  animation: glowFade 2.5s ease-in-out;
}

@keyframes glowFade {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
  70% {
    opacity: 0.8;
  }
  100% {
    opacity: 0;
    transform: scale(1.2);
  }
}

/* Sparkle animations */
.sparkle-float {
  animation: sparkleFloat 1.5s ease-out forwards;
}

@keyframes sparkleFloat {
  0% {
    transform: translateY(0) scale(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    transform: translateY(-80px) scale(0.5);
    opacity: 0;
  }
}

/* Message animations */
.message-container {
  animation: messageSlide 0.6s ease-out forwards;
  animation-delay: 1s;
  opacity: 0;
}

.message-container h3,
.message-container p {
  opacity: 0;
}

@keyframes messageSlide {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Override slide-up for message text */
.message-container .animate-slide-up {
  animation: messageTextSlide 0.4s ease-out forwards;
}

@keyframes messageTextSlide {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Fade in animation for background */
@keyframes fadeIn {
  0% { 
    opacity: 0; 
  }
  100% { 
    opacity: 1; 
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
</style>