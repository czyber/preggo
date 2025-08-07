<template>
  <div
    ref="virtualHugRef"
    :class="cn(
      'virtual-hug-container relative',
      isActive && 'hug-active',
      className
    )"
  >
    <!-- Hug button/trigger -->
    <button
      v-if="!isActive && showTrigger"
      @click="sendHug"
      :disabled="disabled || isProcessing"
      :class="cn(
        'hug-trigger flex items-center gap-2 px-4 py-2.5 rounded-2xl',
        'bg-gradient-to-r from-soft-pink/80 to-gentle-mint/80',
        'text-white font-semibold text-sm shadow-md',
        'transition-all duration-300 hover:shadow-lg hover:scale-105',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
        triggerClassName
      )"
    >
      <span class="text-lg">🤗</span>
      <span>{{ triggerText }}</span>
      <div
        v-if="isProcessing"
        class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"
      />
    </button>

    <!-- Active hug animation -->
    <div
      v-if="isActive"
      class="hug-animation-container absolute inset-0 flex items-center justify-center pointer-events-none"
      :style="{ zIndex: 50 }"
    >
      <!-- Warm glow background -->
      <div class="absolute inset-0 bg-gradient-radial from-soft-pink/20 via-gentle-mint/15 to-transparent animate-pulse" />
      
      <!-- Central hug visual -->
      <div class="relative z-10 hug-visual">
        <!-- Ripple effects -->
        <div
          v-for="i in 3"
          :key="`ripple-${i}`"
          :class="cn(
            'absolute inset-0 border-2 rounded-full opacity-60',
            'border-soft-pink/40 animate-hug-ripple',
            `ripple-${i}`
          )"
          :style="{ 
            width: `${40 + i * 20}px`, 
            height: `${40 + i * 20}px`,
            marginLeft: `${-(20 + i * 10)}px`,
            marginTop: `${-(20 + i * 10)}px`,
            animationDelay: `${i * 0.2}s`
          }"
        />
        
        <!-- Main hug icon -->
        <div class="relative z-20 hug-icon-container">
          <div class="hug-icon text-4xl animate-hug-bounce">
            🤗
          </div>
        </div>
      </div>

      <!-- Floating hearts -->
      <div
        v-for="heart in floatingHearts"
        :key="`heart-${heart.id}`"
        :class="cn(
          'absolute heart-float text-soft-pink opacity-70',
          heart.size
        )"
        :style="heart.style"
      >
        {{ heart.emoji }}
      </div>

      <!-- Warm message overlay -->
      <div
        v-if="showMessage"
        class="absolute bottom-8 left-1/2 transform -translate-x-1/2 hug-message"
      >
        <div class="bg-white/90 backdrop-blur-sm rounded-2xl px-6 py-3 shadow-lg border border-white/40">
          <p class="text-sm font-medium text-gray-800 text-center">
            {{ hugMessage }}
          </p>
        </div>
      </div>
    </div>

    <!-- Received hugs display -->
    <div
      v-if="receivedHugs.length > 0 && showReceived"
      class="received-hugs mt-3"
    >
      <div class="flex items-center gap-2 mb-2">
        <span class="text-sm font-medium text-gray-700">Virtual Hugs:</span>
        <span class="text-xs text-gray-500">({{ receivedHugs.length }})</span>
      </div>
      
      <div class="flex flex-wrap gap-1">
        <div
          v-for="hug in displayHugs"
          :key="hug.id"
          class="hug-badge flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-soft-pink/20 to-gentle-mint/20 rounded-full text-xs border border-soft-pink/30"
        >
          <span class="text-sm">🤗</span>
          <span class="font-medium text-gray-700">{{ hug.senderName }}</span>
          <span v-if="hug.timestamp" class="text-gray-500">{{ formatTimeAgo(hug.timestamp) }}</span>
        </div>
        
        <button
          v-if="receivedHugs.length > maxDisplayHugs"
          @click="showAllHugs = !showAllHugs"
          class="text-xs text-soft-pink hover:text-soft-pink/80 font-medium"
        >
          {{ showAllHugs ? 'Show less' : `+${receivedHugs.length - maxDisplayHugs} more` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cn } from '~/components/ui/utils'

interface VirtualHugProps {
  postId?: string
  recipientId?: string
  senderId?: string
  senderName?: string
  triggerText?: string
  hugMessage?: string
  showTrigger?: boolean
  showMessage?: boolean
  showReceived?: boolean
  disabled?: boolean
  maxDisplayHugs?: number
  duration?: number
  className?: string
  triggerClassName?: string
}

interface ReceivedHug {
  id: string
  senderId: string
  senderName: string
  timestamp: Date
  message?: string
}

interface FloatingHeart {
  id: number
  emoji: string
  size: string
  style: Record<string, string>
}

const props = withDefaults(defineProps<VirtualHugProps>(), {
  triggerText: 'Send Hug',
  hugMessage: 'Sending you warm hugs! 🤗💕',
  showTrigger: true,
  showMessage: true,
  showReceived: true,
  disabled: false,
  maxDisplayHugs: 3,
  duration: 3000
})

const emit = defineEmits<{
  hugSent: [hugData: { postId?: string; recipientId?: string; message?: string }]
  hugReceived: [hugData: ReceivedHug]
  animationComplete: []
}>()

const virtualHugRef = ref<HTMLElement>()
const isActive = ref(false)
const isProcessing = ref(false)
const showAllHugs = ref(false)
const receivedHugs = ref<ReceivedHug[]>([])
const animationTimeout = ref<NodeJS.Timeout>()

// Computed properties
const displayHugs = computed(() => {
  if (showAllHugs.value) {
    return receivedHugs.value
  }
  return receivedHugs.value.slice(0, props.maxDisplayHugs)
})

const floatingHearts = computed((): FloatingHeart[] => {
  if (!isActive.value) return []
  
  const hearts: FloatingHeart[] = []
  const heartEmojis = ['💕', '💖', '💗', '🤍', '❤️']
  const sizes = ['text-sm', 'text-base', 'text-lg']
  
  for (let i = 0; i < 6; i++) {
    const angle = (i * 60) + (Math.random() * 30 - 15)
    const distance = 60 + Math.random() * 40
    const x = Math.cos(angle * Math.PI / 180) * distance
    const y = Math.sin(angle * Math.PI / 180) * distance
    
    hearts.push({
      id: i,
      emoji: heartEmojis[Math.floor(Math.random() * heartEmojis.length)],
      size: sizes[Math.floor(Math.random() * sizes.length)],
      style: {
        left: '50%',
        top: '50%',
        transform: `translate(-50%, -50%)`,
        '--target-x': `${x}px`,
        '--target-y': `${y}px`,
        animationDelay: `${i * 0.15}s`,
        animationDuration: '2s'
      }
    })
  }
  
  return hearts
})

// Methods
const sendHug = async () => {
  if (isProcessing.value || isActive.value) return
  
  isProcessing.value = true
  
  try {
    // Emit hug sent event
    emit('hugSent', {
      postId: props.postId,
      recipientId: props.recipientId,
      message: props.hugMessage
    })
    
    // Start animation
    isActive.value = true
    
    // Auto-complete animation
    animationTimeout.value = setTimeout(() => {
      isActive.value = false
      isProcessing.value = false
      emit('animationComplete')
    }, props.duration)
    
  } catch (error) {
    console.error('Failed to send hug:', error)
    isProcessing.value = false
  }
}

const receiveHug = (hugData: ReceivedHug) => {
  receivedHugs.value.unshift(hugData)
  emit('hugReceived', hugData)
  
  // Trigger a brief animation for received hug
  if (!isActive.value) {
    isActive.value = true
    setTimeout(() => {
      isActive.value = false
    }, 1500)
  }
}

const formatTimeAgo = (timestamp: Date): string => {
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - timestamp.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`
  return `${Math.floor(diffInSeconds / 86400)}d`
}

// Lifecycle
onMounted(() => {
  // Add haptic feedback support if available
  if ('vibrate' in navigator) {
    // Light haptic feedback on hug send
  }
})

onUnmounted(() => {
  if (animationTimeout.value) {
    clearTimeout(animationTimeout.value)
  }
})

// Expose methods for parent components
defineExpose({
  sendHug,
  receiveHug,
  isActive: computed(() => isActive.value),
  isProcessing: computed(() => isProcessing.value)
})
</script>

<style scoped>
/* Hug button styling */
.hug-trigger {
  position: relative;
  overflow: hidden;
}

.hug-trigger::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.hug-trigger:hover::before {
  transform: translateX(100%);
}

/* Hug animation container */
.hug-animation-container {
  width: 200px;
  height: 200px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

/* Ripple animations */
.ripple-1 { animation-delay: 0s; }
.ripple-2 { animation-delay: 0.2s; }
.ripple-3 { animation-delay: 0.4s; }

@keyframes hug-ripple {
  0% {
    transform: scale(0);
    opacity: 0.6;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Main hug icon animation */
.hug-icon {
  animation: hug-bounce 0.8s ease-out;
}

@keyframes hug-bounce {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Floating hearts animation */
.heart-float {
  animation: heart-float-out 2s ease-out forwards;
}

@keyframes heart-float-out {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  100% {
    transform: translate(calc(-50% + var(--target-x, 0px)), calc(-50% + var(--target-y, 0px))) scale(0.7);
    opacity: 0;
  }
}

/* Hug message animation */
.hug-message {
  animation: hug-message-appear 0.5s ease-out 0.8s both;
}

@keyframes hug-message-appear {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Active state styling */
.hug-active {
  pointer-events: none;
}

/* Received hugs styling */
.hug-badge {
  animation: hug-badge-appear 0.3s ease-out;
}

@keyframes hug-badge-appear {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Gradient background utility */
.bg-gradient-radial {
  background: radial-gradient(circle, var(--tw-gradient-stops));
}

/* Pregnancy color variables */
:root {
  --soft-pink: #F8BBD0;
  --gentle-mint: #B2DFDB;
  --muted-lavender: #E1BEE7;
  --light-coral: #FFCDD2;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .hug-animation-container {
    width: 150px;
    height: 150px;
  }
  
  .hug-trigger {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .hug-message div {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .received-hugs {
    margin-top: 0.5rem;
  }
  
  .hug-badge {
    padding: 0.25rem 0.5rem;
    font-size: 0.7rem;
  }
}

/* Accessibility */
.hug-trigger:focus {
  outline: 2px solid var(--soft-pink);
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .hug-icon,
  .heart-float,
  .hug-message,
  .hug-badge {
    animation-duration: 0.1s !important;
  }
  
  .ripple-1,
  .ripple-2, 
  .ripple-3 {
    animation: none;
  }
  
  .hug-trigger::before {
    transition: none;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .hug-trigger {
    border: 2px solid currentColor;
  }
  
  .hug-badge {
    border-width: 2px;
  }
}
</style>
