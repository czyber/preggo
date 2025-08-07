<template>
  <div
    ref="promptContainer"
    :class="cn(
      'family-celebration-prompt relative overflow-hidden',
      'bg-gradient-to-br from-soft-pink/8 via-gentle-mint/6 to-muted-lavender/4',
      'border border-soft-pink/20 rounded-2xl p-4 shadow-sm',
      'transition-all duration-500 hover:shadow-md hover:border-soft-pink/30',
      isActive && 'prompt-active',
      className
    )"
  >
    <!-- Gentle background animation -->
    <div v-if="isActive" class="absolute inset-0 pointer-events-none">
      <!-- Floating particles -->
      <div
        v-for="i in 6"
        :key="`particle-${i}`"
        :class="cn(
          'absolute w-1 h-1 bg-soft-pink rounded-full opacity-40',
          `particle-${i}`
        )"
        :style="getParticleStyle(i)"
      />
    </div>

    <!-- Header section -->
    <div class="relative z-10 mb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="celebration-icon text-2xl animate-gentle-bounce">
            {{ celebrationIcon }}
          </div>
          <div>
            <h3 class="font-semibold text-gray-800 text-base">
              {{ promptTitle }}
            </h3>
            <p class="text-sm text-gray-600 mt-1">
              {{ promptMessage }}
            </p>
          </div>
        </div>
        
        <button
          v-if="dismissible && !isDismissed"
          @click="handleDismiss"
          class="p-1 hover:bg-gray-100 rounded-full transition-colors opacity-60 hover:opacity-80"
          aria-label="Dismiss prompt"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Family members who can participate -->
    <div v-if="familyMembers.length > 0" class="family-members mb-4">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-medium text-gray-600">Invite family members:</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="member in displayedMembers"
          :key="member.id"
          :class="cn(
            'family-member-card flex items-center gap-2 px-3 py-1.5 rounded-full text-xs',
            member.hasParticipated 
              ? 'bg-gradient-to-r from-gentle-mint/30 to-soft-pink/20 text-gray-700 border border-gentle-mint/40'
              : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100 cursor-pointer',
            'transition-all duration-200'
          )"
          @click="!member.hasParticipated && handleInviteMember(member)"
        >
          <div class="w-5 h-5 bg-gradient-to-r from-soft-pink to-gentle-mint rounded-full flex items-center justify-center text-white text-xs font-bold">
            {{ member.name.charAt(0).toUpperCase() }}
          </div>
          <span>{{ member.name }}</span>
          <span v-if="member.hasParticipated" class="text-gray-700">✓</span>
        </div>
        
        <button
          v-if="familyMembers.length > maxDisplayMembers"
          @click="showAllMembers = !showAllMembers"
          class="text-xs text-soft-pink hover:text-soft-pink/80 font-medium px-2"
        >
          {{ showAllMembers ? 'Show less' : `+${familyMembers.length - maxDisplayMembers} more` }}
        </button>
      </div>
    </div>

    <!-- Celebration participation stats -->
    <div v-if="showStats && participationStats" class="participation-stats mb-4">
      <div class="flex items-center justify-between text-xs text-gray-600 mb-2">
        <span>Family participation</span>
        <span>{{ participationStats.participated }}/{{ participationStats.total }} joined</span>
      </div>
      <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          class="absolute top-0 left-0 h-full bg-gradient-to-r from-soft-pink to-gentle-mint rounded-full transition-all duration-500"
          :style="{ width: `${participationStats.percentage}%` }"
        />
      </div>
    </div>

    <!-- Action buttons -->
    <div class="action-buttons flex flex-wrap gap-2">
      <!-- Join celebration -->
      <button
        v-if="!userHasParticipated"
        @click="handleJoinCelebration"
        :disabled="isProcessing"
        class="join-btn flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-soft-pink to-gentle-mint text-white font-semibold text-sm rounded-xl hover:shadow-md transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
      >
        <span class="text-base">🎉</span>
        <span>{{ joinButtonText }}</span>
        <div
          v-if="isProcessing"
          class="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin"
        />
      </button>

      <!-- Send blessing/message -->
      <button
        @click="handleSendBlessing"
        :disabled="isProcessing"
        class="blessing-btn flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white text-gray-700 font-medium text-sm rounded-xl border border-gray-200 hover:border-soft-pink/30 transition-all duration-200 hover:scale-105"
      >
        <span class="text-base">🙏</span>
        <span>Send Blessing</span>
      </button>

      <!-- Virtual hug -->
      <VirtualHug
        v-if="enableVirtualHugs"
        :post-id="postId"
        :recipient-id="recipientId"
        :sender-name="senderName"
        trigger-text="Send Hug"
        :show-received="false"
        class-name="hug-btn-small"
        trigger-class-name="px-3 py-2 text-sm"
        @hug-sent="handleHugSent"
      />

      <!-- Share celebration -->
      <button
        v-if="enableSharing"
        @click="handleShareCelebration"
        class="share-btn flex items-center gap-2 px-3 py-2 bg-gray-50 hover:bg-gray-100 text-gray-600 font-medium text-sm rounded-xl transition-all duration-200 hover:scale-105"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
        <span>Share</span>
      </button>
    </div>

    <!-- Recent participation activity -->
    <div v-if="recentActivity.length > 0" class="recent-activity mt-4 pt-3 border-t border-gray-200/60">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xs font-medium text-gray-600">Recent activity:</span>
      </div>
      <div class="space-y-2">
        <div
          v-for="activity in displayedActivity"
          :key="activity.id"
          class="activity-item flex items-center gap-2 text-xs text-gray-600"
        >
          <div class="w-4 h-4 bg-gradient-to-r from-soft-pink to-gentle-mint rounded-full flex items-center justify-center text-white text-xs font-bold">
            {{ activity.memberName.charAt(0).toUpperCase() }}
          </div>
          <span>{{ activity.memberName }}</span>
          <span class="text-gray-400">{{ activity.action }}</span>
          <span class="text-gray-400">{{ formatTimeAgo(activity.timestamp) }}</span>
        </div>
      </div>
    </div>

    <!-- Celebration particles overlay -->
    <CelebrationParticles
      v-if="showCelebrationAnimation"
      type="gentle"
      intensity="light"
      :is-active="showCelebrationAnimation"
      :duration="2000"
      class="celebration-overlay"
      @animation-complete="onCelebrationComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { cn } from '~/components/ui/utils'
import VirtualHug from './VirtualHug.vue'
import CelebrationParticles from './CelebrationParticles.vue'

interface FamilyMember {
  id: string
  name: string
  relationship: string
  hasParticipated: boolean
  avatar?: string
}

interface ParticipationActivity {
  id: string
  memberId: string
  memberName: string
  action: string
  timestamp: Date
}

interface Props {
  postId?: string
  recipientId?: string
  senderName?: string
  milestoneType?: string
  celebrationIcon?: string
  promptTitle?: string
  promptMessage?: string
  familyMembers?: FamilyMember[]
  recentActivity?: ParticipationActivity[]
  userHasParticipated?: boolean
  joinButtonText?: string
  enableVirtualHugs?: boolean
  enableSharing?: boolean
  showStats?: boolean
  dismissible?: boolean
  isActive?: boolean
  maxDisplayMembers?: number
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  celebrationIcon: '🎉',
  promptTitle: 'Join the Celebration!',
  promptMessage: 'Your family would love to celebrate this special moment with you.',
  familyMembers: () => [],
  recentActivity: () => [],
  userHasParticipated: false,
  joinButtonText: 'Join Celebration',
  enableVirtualHugs: true,
  enableSharing: true,
  showStats: true,
  dismissible: true,
  isActive: false,
  maxDisplayMembers: 4
})

const emit = defineEmits<{
  joinCelebration: [data: { postId?: string; milestoneType?: string }]
  sendBlessing: [data: { postId?: string; recipientId?: string }]
  inviteMember: [member: FamilyMember]
  shareCelebration: [data: { postId?: string }]
  hugSent: [data: any]
  dismiss: []
}>()

const promptContainer = ref<HTMLElement>()
const isProcessing = ref(false)
const isDismissed = ref(false)
const showAllMembers = ref(false)
const showCelebrationAnimation = ref(false)

// Computed properties
const displayedMembers = computed(() => {
  if (showAllMembers.value) {
    return props.familyMembers
  }
  return props.familyMembers.slice(0, props.maxDisplayMembers)
})

const displayedActivity = computed(() => {
  return props.recentActivity.slice(0, 3)
})

const participationStats = computed(() => {
  if (props.familyMembers.length === 0) return null
  
  const participated = props.familyMembers.filter(m => m.hasParticipated).length
  const total = props.familyMembers.length
  const percentage = Math.round((participated / total) * 100)
  
  return { participated, total, percentage }
})

// Methods
const getParticleStyle = (index: number) => {
  const positions = [
    { top: '20%', left: '10%' },
    { top: '30%', right: '15%' },
    { top: '60%', left: '20%' },
    { top: '70%', right: '25%' },
    { top: '40%', left: '70%' },
    { top: '85%', right: '60%' }
  ]
  
  const position = positions[(index - 1) % positions.length]
  const animationDelay = `${(index - 1) * 0.4}s`
  
  return {
    ...position,
    animationDelay
  }
}

const handleJoinCelebration = async () => {
  if (isProcessing.value) return
  
  isProcessing.value = true
  
  try {
    emit('joinCelebration', {
      postId: props.postId,
      milestoneType: props.milestoneType
    })
    
    // Show celebration animation
    showCelebrationAnimation.value = true
    
    // Add haptic feedback if available
    if ('vibrate' in navigator) {
      navigator.vibrate([100, 50, 100])
    }
    
  } catch (error) {
    console.error('Failed to join celebration:', error)
  } finally {
    setTimeout(() => {
      isProcessing.value = false
    }, 1000)
  }
}

const handleSendBlessing = () => {
  emit('sendBlessing', {
    postId: props.postId,
    recipientId: props.recipientId
  })
}

const handleInviteMember = (member: FamilyMember) => {
  emit('inviteMember', member)
}

const handleShareCelebration = () => {
  emit('shareCelebration', {
    postId: props.postId
  })
}

const handleHugSent = (data: any) => {
  emit('hugSent', data)
}

const handleDismiss = () => {
  isDismissed.value = true
  emit('dismiss')
}

const onCelebrationComplete = () => {
  showCelebrationAnimation.value = false
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
  // Auto-activate if specified
  if (props.isActive) {
    setTimeout(() => {
      showCelebrationAnimation.value = true
    }, 500)
  }
})
</script>

<style scoped>
/* Main prompt styling */
.family-celebration-prompt {
  backdrop-filter: blur(8px);
}

.prompt-active {
  animation: prompt-gentle-glow 3s ease-in-out infinite;
}

@keyframes prompt-gentle-glow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(248, 187, 208, 0.2);
  }
  50% {
    box-shadow: 0 0 25px rgba(248, 187, 208, 0.4), 0 0 35px rgba(178, 223, 219, 0.2);
  }
}

/* Floating particles */
.particle-1 { animation: gentle-float 4s ease-in-out infinite; }
.particle-2 { animation: gentle-float 4.5s ease-in-out infinite; }
.particle-3 { animation: gentle-float 3.5s ease-in-out infinite; }
.particle-4 { animation: gentle-float 4.2s ease-in-out infinite; }
.particle-5 { animation: gentle-float 3.8s ease-in-out infinite; }
.particle-6 { animation: gentle-float 4.8s ease-in-out infinite; }

@keyframes gentle-float {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.4;
  }
  50% {
    transform: translateY(-8px) scale(1.2);
    opacity: 0.7;
  }
}

/* Celebration icon animation */
.celebration-icon {
  animation: gentle-bounce 2s ease-in-out infinite;
}

@keyframes gentle-bounce {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  25% {
    transform: scale(1.05) rotate(-2deg);
  }
  75% {
    transform: scale(1.02) rotate(1deg);
  }
}

/* Family member cards */
.family-member-card {
  animation: member-appear 0.3s ease-out;
}

@keyframes member-appear {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Action buttons */
.join-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.join-btn:hover::before {
  transform: translateX(100%);
}

.join-btn,
.blessing-btn,
.share-btn {
  position: relative;
  overflow: hidden;
}

/* Activity items */
.activity-item {
  animation: activity-slide-in 0.4s ease-out;
}

@keyframes activity-slide-in {
  0% {
    opacity: 0;
    transform: translateX(-10px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Celebration overlay */
.celebration-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 20;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .family-celebration-prompt {
    margin: 0 -0.5rem;
    padding: 0.75rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .join-btn,
  .blessing-btn,
  .share-btn {
    width: 100%;
    justify-content: center;
  }
  
  .family-member-card {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
}

/* Accessibility */
.join-btn:focus,
.blessing-btn:focus,
.share-btn:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .prompt-active,
  .celebration-icon,
  .particle-1, .particle-2, .particle-3, .particle-4, .particle-5, .particle-6,
  .member-appear,
  .activity-slide-in {
    animation: none;
  }
  
  .join-btn::before {
    transition: none;
  }
}
</style>
