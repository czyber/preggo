<template>
  <div
    ref="celebrationElementRef"
    :class="cn(
      'milestone-celebration relative overflow-hidden',
      'bg-gradient-to-br from-soft-pink/20 via-gentle-mint/15 to-muted-lavender/10',
      'border-2 border-soft-pink/30 rounded-2xl p-6',
      'shadow-lg hover:shadow-xl transition-all duration-500',
      celebration.is_new && 'celebration-glow animate-pulse'
    )"
  >
    <!-- Celebration Background Effects -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Sparkle Animation -->
      <div
        v-for="i in 12"
        :key="`sparkle-${i}`"
        :class="cn(
          'absolute w-2 h-2 bg-soft-pink rounded-full opacity-70',
          `sparkle-${i}`
        )"
        :style="getSparkleStyle(i)"
      />
      
      <!-- Floating Hearts -->
      <div
        v-for="i in 6"
        :key="`heart-${i}`"
        :class="cn(
          'absolute text-soft-pink opacity-60 text-xl pointer-events-none',
          `heart-${i}`
        )"
        :style="getHeartStyle(i)"
      >
        ❤️
      </div>
    </div>

    <!-- Celebration Header -->
    <div class="relative z-10">
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <div class="celebration-icon text-4xl">
            {{ getCelebrationIcon() }}
          </div>
          <div>
            <h3 class="font-bold text-xl text-gray-900 font-primary mb-1">
              {{ getCelebrationTitle() }}
            </h3>
            <p class="text-sm text-gray-700">
              {{ getCelebrationDescription() }}
            </p>
          </div>
        </div>
        
        <button
          v-if="celebration.is_new && !isDismissed"
          @click="handleDismiss"
          class="p-1 hover:bg-white/50 rounded-full transition-colors opacity-60 hover:opacity-80"
          aria-label="Dismiss celebration"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Milestone Details -->
      <div v-if="celebration.milestone_details" class="milestone-details mb-4 p-4 bg-white/40 rounded-xl border border-white/60">
        <div class="flex items-start gap-3">
          <span class="text-2xl">👶</span>
          <div class="flex-1">
            <h4 class="font-semibold text-gray-800 mb-2">
              Week {{ celebration.milestone_details.week }} Milestone
            </h4>
            
            <div class="space-y-2 text-sm text-gray-700">
              <div v-if="celebration.milestone_details.baby_size" class="flex items-center gap-2">
                <span class="font-medium text-gray-700">Baby Size:</span>
                <span>{{ celebration.milestone_details.baby_size }}</span>
              </div>
              
              <div v-if="celebration.milestone_details.development" class="flex items-start gap-2">
                <span class="font-medium text-gray-700">Development:</span>
                <span>{{ celebration.milestone_details.development }}</span>
              </div>
              
              <div v-if="celebration.milestone_details.key_changes && celebration.milestone_details.key_changes.length > 0" class="flex items-start gap-2">
                <span class="font-medium text-gray-700">Key Changes:</span>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="change in celebration.milestone_details.key_changes"
                    :key="change"
                    class="px-2 py-1 bg-gentle-mint/20 text-gray-700 text-xs rounded-full"
                  >
                    {{ change }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Family Participation -->
      <div v-if="celebration.family_participation" class="family-participation mb-4">
        <h4 class="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <span class="text-base">👨‍👩‍👧‍👦</span>
          Family Celebrating With You
        </h4>
        
        <!-- Reaction Summary -->
        <div v-if="celebration.family_participation.reactions && Object.keys(celebration.family_participation.reactions).length > 0" class="mb-3">
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(count, reactionType) in celebration.family_participation.reactions"
              :key="reactionType"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-white/60 rounded-full text-sm"
            >
              <span class="text-base">{{ getReactionEmoji(reactionType as string) }}</span>
              <span class="font-medium text-gray-700">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Messages -->
        <div v-if="celebration.family_participation.messages && celebration.family_participation.messages.length > 0" class="space-y-2">
          <div
            v-for="message in celebration.family_participation.messages.slice(0, 3)"
            :key="message.id"
            class="flex items-start gap-2 p-2 bg-white/50 rounded-lg"
          >
            <div class="w-6 h-6 bg-gentle-mint/30 rounded-full flex items-center justify-center text-xs font-semibold text-gray-700">
              {{ message.author_name?.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-xs text-gray-700">{{ message.author_name }}</div>
              <div class="text-xs text-gray-600 mt-0.5">{{ message.content }}</div>
            </div>
          </div>
          
          <button
            v-if="celebration.family_participation.messages.length > 3"
            @click="handleViewAllMessages"
            class="text-xs text-soft-pink hover:text-soft-pink/80 font-medium"
          >
            View all {{ celebration.family_participation.messages.length }} messages
          </button>
        </div>
      </div>

      <!-- Celebration Actions -->
      <div class="celebration-actions flex items-center justify-between">
        <div class="flex items-center gap-2">
          <!-- Join Celebration Button -->
          <button
            v-if="!hasUserCelebrated"
            @click="handleJoinCelebration"
            class="celebration-btn px-4 py-2 bg-gradient-to-r from-soft-pink to-gentle-mint text-white font-semibold rounded-xl hover:shadow-md transition-all duration-200 hover:scale-105"
          >
            <span class="flex items-center gap-2">
              🎉 <span>Celebrate!</span>
            </span>
          </button>
          
          <span v-else class="flex items-center gap-2 px-4 py-2 bg-white/60 rounded-xl text-sm font-medium text-gray-700">
            ✨ <span>You're celebrating!</span>
          </span>

          <!-- Send Message Button -->
          <button
            @click="handleSendMessage"
            class="flex items-center gap-2 px-3 py-2 bg-white/60 hover:bg-white/80 rounded-xl text-sm font-medium text-gray-700 transition-colors"
          >
            💝 <span>Send Love</span>
          </button>
        </div>

        <!-- Share Celebration -->
        <button
          @click="handleShareCelebration"
          class="flex items-center gap-2 px-3 py-2 bg-white/40 hover:bg-white/60 rounded-xl text-sm font-medium text-gray-600 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          <span>Share</span>
        </button>
      </div>

      <!-- Celebration Timer (for time-limited celebrations) -->
      <div v-if="celebration.celebration_duration && celebration.celebration_duration > 0" class="celebration-timer mt-4 text-center">
        <div class="text-xs text-gray-600 mb-1">Celebration active for</div>
        <div class="font-mono text-sm font-semibold text-soft-pink">
          {{ formatTimeRemaining() }}
        </div>
      </div>
    </div>

    <!-- Celebration Animation Overlay -->
    <div
      v-if="showCelebrationAnimation"
      class="absolute inset-0 pointer-events-none z-20 flex items-center justify-center"
    >
      <CelebrationAnimation
        :type="animationType"
        @complete="onAnimationComplete"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import { useCelebrationAnimation, useGentleTransitions, useScrollAnimation } from '~/composables/useAnimations'

type CelebrationPost = components['schemas']['CelebrationPost']

interface Props {
  celebration: CelebrationPost
  autoAnimate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoAnimate: true
})

const emit = defineEmits<{
  joinCelebration: [celebrationId: string]
  sendMessage: [celebrationId: string]
  shareCelebration: [celebrationId: string]
  viewAllMessages: [celebrationId: string]
  dismiss: [celebrationId: string]
  animationComplete: []
}>()

// Animation composables
const { celebrateSparkles, celebrateHearts, celebrateConfetti, celebrateMilestone } = useCelebrationAnimation()
const { createGentleHover, animateElementIn, glowElement, pulseElement } = useGentleTransitions()
const { observeElement } = useScrollAnimation()

// Local state
const isDismissed = ref(false)
const showCelebrationAnimation = ref(false)
const animationType = ref<'confetti' | 'hearts' | 'sparkles'>('confetti')
const timeRemaining = ref(0)
const timerInterval = ref<NodeJS.Timeout>()
const celebrationElementRef = ref<HTMLElement>()

// Pregnancy-specific reactions mapping
const pregnancyReactions = {
  love: '❤️',
  excited: '😍',
  care: '🤗',
  support: '💪',
  beautiful: '✨',
  funny: '😂',
  praying: '🙏',
  proud: '🏆',
  grateful: '🙏✨'
}

// Computed properties
const hasUserCelebrated = computed(() => {
  return props.celebration.user_participation?.has_celebrated || false
})

// Methods
function getCelebrationIcon() {
  const celebrationType = props.celebration.celebration_type
  
  const celebrationIcons = {
    milestone: '🎉',
    week_achievement: '✨',
    trimester_change: '🌟',
    baby_movement: '👶',
    appointment_success: '💝',
    symptom_relief: '😌',
    energy_boost: '⚡',
    special_moment: '💫'
  }
  
  return celebrationIcons[celebrationType] || '🎉'
}

function getCelebrationTitle() {
  const celebrationType = props.celebration.celebration_type
  
  const celebrationTitles = {
    milestone: 'Milestone Achieved!',
    week_achievement: 'New Week Milestone!',
    trimester_change: 'New Trimester!',
    baby_movement: 'Baby\'s Moving!',
    appointment_success: 'Great Appointment!',
    symptom_relief: 'Feeling Better!',
    energy_boost: 'Energy Boost!',
    special_moment: 'Special Moment!'
  }
  
  return celebrationTitles[celebrationType] || 'Time to Celebrate!'
}

function getCelebrationDescription() {
  const week = props.celebration.milestone_details?.week
  const celebrationType = props.celebration.celebration_type
  
  const baseDescriptions = {
    milestone: week ? `Congratulations on reaching week ${week}!` : 'Another beautiful milestone in your pregnancy journey!',
    week_achievement: week ? `Welcome to week ${week} of your pregnancy!` : 'Another week of your amazing journey!',
    trimester_change: 'You\'ve entered a new phase of your pregnancy!',
    baby_movement: 'Your little one is making their presence known!',
    appointment_success: 'Everything looks great with you and baby!',
    symptom_relief: 'So glad you\'re feeling more comfortable!',
    energy_boost: 'Wonderful to see you feeling energized!',
    special_moment: 'These precious moments make the journey so special!'
  }
  
  return baseDescriptions[celebrationType] || 'Your family is celebrating this moment with you!'
}

function getReactionEmoji(reactionType: string) {
  return pregnancyReactions[reactionType as keyof typeof pregnancyReactions] || '❤️'
}

function getSparkleStyle(index: number) {
  const positions = [
    { top: '10%', left: '15%' },
    { top: '15%', right: '20%' },
    { top: '25%', left: '8%' },
    { top: '30%', right: '12%' },
    { top: '45%', left: '12%' },
    { top: '50%', right: '18%' },
    { top: '65%', left: '10%' },
    { top: '70%', right: '15%' },
    { top: '80%', left: '20%' },
    { top: '85%', right: '25%' },
    { top: '20%', left: '50%' },
    { top: '75%', right: '45%' }
  ]
  
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.2}s`
  
  return {
    ...position,
    animationDelay
  }
}

function getHeartStyle(index: number) {
  const positions = [
    { top: '20%', left: '25%' },
    { top: '35%', right: '30%' },
    { top: '55%', left: '20%' },
    { top: '65%', right: '25%' },
    { top: '40%', left: '60%' },
    { top: '80%', right: '50%' }
  ]
  
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.5}s`
  
  return {
    ...position,
    animationDelay
  }
}

function formatTimeRemaining() {
  const hours = Math.floor(timeRemaining.value / 3600)
  const minutes = Math.floor((timeRemaining.value % 3600) / 60)
  const seconds = timeRemaining.value % 60
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`
  }
  return `${seconds}s`
}

function updateTimer() {
  if (props.celebration.celebration_duration && props.celebration.celebration_duration > 0) {
    const now = Date.now()
    const celebrationStart = new Date(props.celebration.created_at || '').getTime()
    const elapsed = Math.floor((now - celebrationStart) / 1000)
    const remaining = Math.max(0, props.celebration.celebration_duration - elapsed)
    
    timeRemaining.value = remaining
    
    if (remaining <= 0) {
      clearInterval(timerInterval.value)
    }
  }
}

// Event handlers
function handleJoinCelebration() {
  emit('joinCelebration', props.celebration.post_id)
  
  // Show celebration animation
  showCelebrationAnimation.value = true
  animationType.value = 'confetti'
  
  // Trigger celebration effects
  if (celebrationElementRef.value) {
    celebrateMilestone(celebrationElementRef.value)
    glowElement(celebrationElementRef.value, 5000)
  }
}

function handleSendMessage() {
  emit('sendMessage', props.celebration.post_id)
  
  // Add gentle hearts animation
  if (celebrationElementRef.value) {
    celebrateHearts(celebrationElementRef.value, 3)
  }
}

function handleShareCelebration() {
  emit('shareCelebration', props.celebration.post_id)
  
  // Add sparkle animation for sharing
  if (celebrationElementRef.value) {
    celebrateSparkles(celebrationElementRef.value, 6)
  }
}

function handleViewAllMessages() {
  emit('viewAllMessages', props.celebration.post_id)
}

function handleDismiss() {
  isDismissed.value = true
  emit('dismiss', props.celebration.post_id)
}

function onAnimationComplete() {
  showCelebrationAnimation.value = false
  emit('animationComplete')
}

// Lifecycle
onMounted(() => {
  // Set up scroll animation
  if (celebrationElementRef.value) {
    observeElement(celebrationElementRef.value, {
      animation: 'fadeInScale',
      delay: 200,
      supportive: true
    })
    
    // Add hover effects to buttons
    const buttons = celebrationElementRef.value.querySelectorAll('button')
    buttons.forEach(button => {
      createGentleHover(button as HTMLElement, 'celebration')
    })
  }
  
  // Auto-animate if new celebration
  if (props.autoAnimate && props.celebration.is_new) {
    setTimeout(() => {
      showCelebrationAnimation.value = true
      animationType.value = 'sparkles'
      
      // Add automatic celebration animation
      if (celebrationElementRef.value) {
        celebrateSparkles(celebrationElementRef.value, 10)
        setTimeout(() => {
          pulseElement(celebrationElementRef.value!, 'warm')
        }, 800)
      }
    }, 500)
  }
  
  // Set up timer if celebration has duration
  if (props.celebration.celebration_duration && props.celebration.celebration_duration > 0) {
    updateTimer()
    timerInterval.value = setInterval(updateTimer, 1000)
  }
})

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
/* Celebration glow effect */
.celebration-glow {
  position: relative;
}

.celebration-glow::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  padding: 2px;
  background: linear-gradient(45deg, #F8BBD0, #B2DFDB, #E1BEE7, #FFCDD2);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: xor;
  -webkit-mask-composite: xor;
  opacity: 0.6;
  animation: celebration-border-glow 3s ease-in-out infinite;
}

@keyframes celebration-border-glow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Sparkle animations */
.sparkle-1 { animation: sparkle-float 3s ease-in-out infinite; }
.sparkle-2 { animation: sparkle-float 3.2s ease-in-out infinite; }
.sparkle-3 { animation: sparkle-float 2.8s ease-in-out infinite; }
.sparkle-4 { animation: sparkle-float 3.5s ease-in-out infinite; }
.sparkle-5 { animation: sparkle-float 2.5s ease-in-out infinite; }
.sparkle-6 { animation: sparkle-float 3.8s ease-in-out infinite; }
.sparkle-7 { animation: sparkle-float 2.9s ease-in-out infinite; }
.sparkle-8 { animation: sparkle-float 3.3s ease-in-out infinite; }
.sparkle-9 { animation: sparkle-float 2.7s ease-in-out infinite; }
.sparkle-10 { animation: sparkle-float 3.1s ease-in-out infinite; }
.sparkle-11 { animation: sparkle-float 3.6s ease-in-out infinite; }
.sparkle-12 { animation: sparkle-float 2.6s ease-in-out infinite; }

@keyframes sparkle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.7;
  }
  25% {
    transform: translateY(-5px) scale(1.1);
    opacity: 1;
  }
  75% {
    transform: translateY(-3px) scale(0.9);
    opacity: 0.8;
  }
}

/* Heart float animations */
.heart-1 { animation: heart-float 4s ease-in-out infinite; }
.heart-2 { animation: heart-float 4.5s ease-in-out infinite; }
.heart-3 { animation: heart-float 3.5s ease-in-out infinite; }
.heart-4 { animation: heart-float 4.2s ease-in-out infinite; }
.heart-5 { animation: heart-float 3.8s ease-in-out infinite; }
.heart-6 { animation: heart-float 4.8s ease-in-out infinite; }

@keyframes heart-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-8px) rotate(5deg) scale(1.1);
    opacity: 0.9;
  }
}

/* Celebration icon animation */
.celebration-icon {
  animation: celebration-bounce 1s ease-in-out infinite;
}

@keyframes celebration-bounce {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  25% {
    transform: scale(1.1) rotate(-5deg);
  }
  75% {
    transform: scale(1.05) rotate(3deg);
  }
}

/* Celebration button special effects */
.celebration-btn {
  position: relative;
  overflow: hidden;
}

.celebration-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.celebration-btn:hover::before {
  transform: translateX(100%);
}

/* Component appear animation */
.milestone-celebration {
  animation: celebration-appear 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes celebration-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Family participation animations */
.family-participation > div {
  animation: family-appear 0.4s ease-out;
  animation-fill-mode: both;
}

.family-participation > div:nth-child(1) { animation-delay: 0.1s; }
.family-participation > div:nth-child(2) { animation-delay: 0.2s; }
.family-participation > div:nth-child(3) { animation-delay: 0.3s; }

@keyframes family-appear {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Timer animation */
.celebration-timer {
  animation: timer-pulse 2s ease-in-out infinite;
}

@keyframes timer-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}

/* Enhanced accessibility */
.milestone-celebration button:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .milestone-celebration {
    padding: 1rem;
    margin: 0 -1rem;
    border-radius: 1rem;
  }
  
  .celebration-actions {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .celebration-actions > div:first-child {
    justify-content: center;
  }
  
  .celebration-btn,
  .celebration-actions button {
    width: 100%;
    justify-content: center;
  }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .sparkle-1, .sparkle-2, .sparkle-3, .sparkle-4, .sparkle-5, .sparkle-6,
  .sparkle-7, .sparkle-8, .sparkle-9, .sparkle-10, .sparkle-11, .sparkle-12,
  .heart-1, .heart-2, .heart-3, .heart-4, .heart-5, .heart-6,
  .celebration-icon,
  .celebration-glow,
  .timer-pulse {
    animation: none;
  }
}
</style>
