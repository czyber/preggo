<template>
  <div 
    class="family-warmth py-3"
    :class="[
      getSupportLevelClass(),
      { 'warmth-detailed': showDetails }
    ]"
  >
    <!-- Family Avatars Cluster -->
    <div 
      v-if="familyHearts.length > 0"
      class="family-cluster flex items-center justify-between mb-2"
    >
      <div 
        class="avatar-cluster relative flex items-center"
        :class="getClusterSizeClass()"
      >
        <!-- Family Member Avatars -->
        <div class="avatar-group flex -space-x-2">
          <div
            v-for="(member, index) in visibleMembers"
            :key="member.id || index"
            class="family-avatar relative group cursor-pointer"
            :style="{ zIndex: 10 - index }"
            @click="handleAvatarClick(member)"
            @keydown.enter="handleAvatarClick(member)"
            @keydown.space.prevent="handleAvatarClick(member)"
            tabindex="0"
            :aria-label="`${member.display_name || member.first_name} sent love`"
          >
            <div 
              class="avatar-container w-8 h-8 rounded-full border-2 border-white bg-gradient-to-br from-soft-pink/30 to-gentle-mint/30 flex items-center justify-center text-xs font-semibold text-gray-700 transition-all duration-200 group-hover:scale-110"
              :class="getAvatarWarmthClass(member)"
            >
              {{ getAvatarInitial(member) }}
            </div>
            
            <!-- Love indicator -->
            <div 
              v-if="hasRecentLove(member)"
              class="love-pulse absolute -top-1 -right-1 w-3 h-3 bg-soft-pink rounded-full animate-pulse"
              aria-hidden="true"
            >
              <span class="sr-only">Recently sent love</span>
            </div>
          </div>
          
          <!-- More members indicator -->
          <div
            v-if="familyHearts.length > maxVisibleAvatars"
            class="more-avatars w-8 h-8 rounded-full border-2 border-white bg-muted-lavender/40 flex items-center justify-center text-xs font-medium text-gray-600 cursor-pointer hover:bg-muted-lavender/60 transition-colors"
            @click="handleMoreMembersClick"
            @keydown.enter="handleMoreMembersClick"
            @keydown.space.prevent="handleMoreMembersClick"
            tabindex="0"
            :aria-label="`and ${familyHearts.length - maxVisibleAvatars} more family members`"
          >
            +{{ familyHearts.length - maxVisibleAvatars }}
          </div>
        </div>

        <!-- Warm background glow effect -->
        <div 
          v-if="supportLevel === 'wrapped'"
          class="warmth-glow absolute inset-0 bg-gradient-to-r from-soft-pink/20 via-gentle-mint/20 to-muted-lavender/20 rounded-full blur-sm -z-10 animate-pulse"
          aria-hidden="true"
        />
      </div>

      <!-- Love message -->
      <div 
        v-if="!showDetails"
        class="warmth-message text-xs text-gray-600 flex items-center gap-1"
      >
        <span class="heart-icon text-soft-pink">💕</span>
        <span>{{ getWarmthMessage() }}</span>
      </div>
    </div>

    <!-- Recent Family Activity (when details shown) -->
    <div 
      v-if="showDetails && recentActivity.length > 0"
      class="recent-activity mt-3 space-y-2"
    >
      <h4 class="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
        <span class="activity-icon">🌟</span>
        Recent family love
      </h4>
      
      <div class="activity-list space-y-1.5">
        <div
          v-for="activity in recentActivity.slice(0, 3)"
          :key="activity.id || `${activity.member_name}-${activity.timestamp}`"
          class="activity-item flex items-center gap-2 text-xs text-gray-600"
        >
          <div class="member-initial w-5 h-5 rounded-full bg-gentle-mint/30 flex items-center justify-center text-xs font-medium">
            {{ activity.member_name?.charAt(0).toUpperCase() }}
          </div>
          
          <div class="activity-description flex-1">
            <span class="member-name font-medium">{{ activity.member_name }}</span>
            <span class="activity-text"> {{ formatActivity(activity) }}</span>
          </div>
          
          <time 
            class="activity-time text-gray-400"
            :datetime="activity.timestamp"
            :title="getActivityFullTime(activity)"
          >
            {{ getActivityTime(activity) }}
          </time>
        </div>
      </div>
    </div>

    <!-- Memory markers -->
    <div 
      v-if="memoryMarkers > 0"
      class="memory-indicators flex items-center gap-2 mt-3 pt-2 border-t border-gray-100"
    >
      <div class="memory-count flex items-center gap-1 text-xs text-gray-600">
        <span class="memory-icon text-muted-lavender">📖</span>
        <span>
          Added to {{ memoryMarkers }} family {{ memoryMarkers === 1 ? 'memory' : 'memories' }}
        </span>
      </div>
    </div>

    <!-- Gentle call-to-action (only for family members viewing) -->
    <div 
      v-if="shouldShowCallToAction && !hasCurrentUserInteracted"
      class="gentle-cta mt-3 pt-2 border-t border-gray-50"
    >
      <div class="flex items-center justify-between">
        <span class="cta-text text-xs text-gray-500">
          Send some love to support this moment
        </span>
        <div class="cta-actions flex items-center gap-2">
          <button
            @click="handleQuickLove"
            class="quick-love-btn p-1.5 rounded-full hover:bg-soft-pink/10 transition-colors group"
            :aria-label="'Send love to this story'"
          >
            <span class="text-sm group-hover:scale-110 transition-transform">💕</span>
          </button>
          <button
            v-if="canAddToMemory"
            @click="handleQuickMemory"
            class="quick-memory-btn p-1.5 rounded-full hover:bg-muted-lavender/10 transition-colors group"
            :aria-label="'Add to family memories'"
          >
            <span class="text-sm group-hover:scale-110 transition-transform">📖</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Warmth level visualization -->
    <div 
      v-if="supportLevel === 'wrapped'"
      class="warmth-visualization mt-3 text-center"
    >
      <div class="warmth-sparkles text-xs text-gentle-mint animate-pulse">
        ✨ Wrapped in family love ✨
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuth } from '~/composables/useAuth'
import type { components } from '~/types/api'

type FamilyMember = components['schemas']['FamilyMember']
type SupportLevel = 'gentle' | 'warm' | 'wrapped'

interface FamilyActivity {
  id?: string
  member_name: string
  member_id: string
  action_type: 'love' | 'memory' | 'comment' | 'hug'
  timestamp: string
  details?: string
}

interface Props {
  familyHearts: FamilyMember[]
  recentActivity: FamilyActivity[]
  memoryMarkers: number
  supportLevel: SupportLevel
  showDetails: boolean
  canAddToMemory?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  familyHearts: () => [],
  recentActivity: () => [],
  memoryMarkers: 0,
  supportLevel: 'gentle',
  showDetails: false,
  canAddToMemory: true
})

const emit = defineEmits<{
  viewActivity: []
  sendLove: [{ method: 'quick' }]
  addToMemory: [{ method: 'quick' }]
  memberClick: [{ member: FamilyMember }]
  showAllMembers: []
}>()

// Composables
const auth = useAuth()

// Constants
const maxVisibleAvatars = 4

// Computed properties
const visibleMembers = computed(() => {
  return props.familyHearts.slice(0, maxVisibleAvatars)
})

const hasCurrentUserInteracted = computed(() => {
  const currentUserId = auth.userProfile.value?.id
  if (!currentUserId) return false
  
  return props.familyHearts.some(member => member.id === currentUserId) ||
         props.recentActivity.some(activity => activity.member_id === currentUserId)
})

const shouldShowCallToAction = computed(() => {
  return props.familyHearts.length < 3 && // Don't show if already lots of engagement
         !props.showDetails && // Only show in compact view
         !hasCurrentUserInteracted.value
})

// Methods
function getSupportLevelClass(): string {
  return `family-warmth--${props.supportLevel}`
}

function getClusterSizeClass(): string {
  const count = props.familyHearts.length
  if (count >= 5) return 'cluster-large'
  if (count >= 3) return 'cluster-medium'
  return 'cluster-small'
}

function getAvatarWarmthClass(member: FamilyMember): string {
  if (hasRecentLove(member)) {
    return 'avatar-recent-love'
  }
  return 'avatar-gentle'
}

function getAvatarInitial(member: FamilyMember): string {
  return (member.display_name || member.first_name || 'F').charAt(0).toUpperCase()
}

function hasRecentLove(member: FamilyMember): boolean {
  const recentThreshold = new Date()
  recentThreshold.setHours(recentThreshold.getHours() - 2) // Within last 2 hours
  
  return props.recentActivity.some(activity => 
    activity.member_id === member.id &&
    activity.action_type === 'love' &&
    new Date(activity.timestamp) > recentThreshold
  )
}

function getWarmthMessage(): string {
  const count = props.familyHearts.length
  
  if (count === 0) return ''
  if (count === 1) return 'Family is sending love'
  if (count <= 3) return 'Family is gathering around this moment'
  return 'Wrapped in family love'
}

function formatActivity(activity: FamilyActivity): string {
  switch (activity.action_type) {
    case 'love':
      return 'sent love'
    case 'memory':
      return 'added to memories'
    case 'comment':
      return 'left a sweet message'
    case 'hug':
      return 'sent a virtual hug'
    default:
      return 'showed support'
  }
}

function getActivityTime(activity: FamilyActivity): string {
  const now = new Date()
  const activityTime = new Date(activity.timestamp)
  const diffInMinutes = Math.floor((now.getTime() - activityTime.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'now'
  if (diffInMinutes < 60) return `${diffInMinutes}m`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`
  return `${Math.floor(diffInMinutes / 1440)}d`
}

function getActivityFullTime(activity: FamilyActivity): string {
  return new Date(activity.timestamp).toLocaleString()
}

// Event handlers
function handleAvatarClick(member: FamilyMember): void {
  emit('memberClick', { member })
}

function handleMoreMembersClick(): void {
  emit('showAllMembers')
}

function handleQuickLove(): void {
  emit('sendLove', { method: 'quick' })
}

function handleQuickMemory(): void {
  emit('addToMemory', { method: 'quick' })
}
</script>

<style scoped>
/* Base family warmth styling */
.family-warmth {
  transition: all 0.3s ease;
}

/* Support level variations */
.family-warmth--gentle {
  /* Minimal styling for gentle support */
}

.family-warmth--warm {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.05) 0%, rgba(178, 223, 219, 0.05) 100%);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.family-warmth--wrapped {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.1) 0%, rgba(178, 223, 219, 0.1) 50%, rgba(225, 190, 231, 0.1) 100%);
  border-radius: 0.75rem;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.family-warmth--wrapped::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(248, 187, 208, 0.1) 50%, transparent 70%);
  animation: warmth-shimmer 3s ease-in-out infinite;
  pointer-events: none;
}

/* Family cluster styling */
.family-cluster {
  min-height: 2rem;
}

.avatar-cluster {
  transition: transform 0.2s ease;
}

.cluster-small:hover {
  transform: scale(1.02);
}

.cluster-medium:hover {
  transform: scale(1.01);
}

/* Avatar styling */
.family-avatar {
  transition: all 0.2s ease;
}

.family-avatar:hover {
  z-index: 20 !important;
}

.avatar-container {
  position: relative;
}

.avatar-recent-love {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.6), rgba(225, 190, 231, 0.4));
  border-color: #F8BBD0;
  animation: recent-love-glow 2s ease-in-out infinite;
}

.avatar-gentle {
  background: linear-gradient(135deg, rgba(248, 187, 208, 0.2), rgba(178, 223, 219, 0.2));
}

.more-avatars {
  background: linear-gradient(135deg, rgba(225, 190, 231, 0.3), rgba(178, 223, 219, 0.3));
}

/* Love pulse indicator */
.love-pulse {
  animation: love-pulse 1.5s ease-in-out infinite;
}

/* Warmth glow effect */
.warmth-glow {
  animation: warmth-glow 4s ease-in-out infinite;
}

/* Warmth message styling */
.warmth-message {
  opacity: 0.8;
  font-weight: 400;
}

.heart-icon {
  animation: gentle-bounce 2s ease-in-out infinite;
}

/* Recent activity styling */
.recent-activity {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.activity-item {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.25rem;
  padding: 0.5rem;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background: rgba(255, 255, 255, 0.9);
}

.member-initial {
  font-size: 0.625rem;
}

/* Memory indicators */
.memory-indicators {
  opacity: 0.9;
}

.memory-icon {
  animation: gentle-float 3s ease-in-out infinite;
}

/* Gentle call-to-action */
.gentle-cta {
  background: rgba(248, 187, 208, 0.02);
  border-radius: 0.375rem;
  padding: 0.5rem 0;
}

.quick-love-btn,
.quick-memory-btn {
  min-width: 2rem;
  min-height: 2rem;
}

/* Warmth sparkles */
.warmth-sparkles {
  font-weight: 500;
  letter-spacing: 0.025em;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .avatar-container {
    width: 1.75rem;
    height: 1.75rem;
  }
  
  .more-avatars {
    width: 1.75rem;
    height: 1.75rem;
    font-size: 0.625rem;
  }
  
  .member-initial {
    width: 1.125rem;
    height: 1.125rem;
    font-size: 0.5rem;
  }
  
  .family-warmth--warm,
  .family-warmth--wrapped {
    padding: 0.5rem;
  }
}

/* Animations */
@keyframes recent-love-glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(248, 187, 208, 0);
  }
  50% {
    box-shadow: 0 0 8px rgba(248, 187, 208, 0.4);
  }
}

@keyframes love-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes warmth-glow {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.05);
  }
}

@keyframes warmth-shimmer {
  0%, 100% {
    transform: translateX(-100%);
    opacity: 0;
  }
  50% {
    transform: translateX(100%);
    opacity: 1;
  }
}

@keyframes gentle-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-1px);
  }
}

@keyframes gentle-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

/* Accessibility improvements */
.family-avatar:focus,
.more-avatars:focus,
.quick-love-btn:focus,
.quick-memory-btn:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .avatar-container {
    border-width: 3px;
    border-color: #000;
  }
  
  .family-warmth--warm,
  .family-warmth--wrapped {
    border: 2px solid #F8BBD0;
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .family-avatar,
  .avatar-container,
  .heart-icon,
  .memory-icon,
  .warmth-glow,
  .love-pulse,
  .warmth-sparkles,
  .quick-love-btn span,
  .quick-memory-btn span {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .family-warmth--warm {
    background: rgba(248, 187, 208, 0.1);
  }
  
  .family-warmth--wrapped {
    background: rgba(248, 187, 208, 0.15);
  }
  
  .recent-activity {
    background: rgba(0, 0, 0, 0.2);
  }
  
  .activity-item {
    background: rgba(0, 0, 0, 0.3);
  }
  
  .warmth-message {
    color: #D1D5DB;
  }
}
</style>