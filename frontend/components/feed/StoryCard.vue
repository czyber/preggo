<template>
  <article 
    ref="storyCardRef"
    class="story-card bg-white rounded-2xl overflow-hidden transition-all duration-300 ease-out"
    :class="[
      getCardSizeClass(),
      getEmotionalToneClass(),
      { 'is-focused': isFocused, 'is-memory-bound': isMemoryBound }
    ]"
    :data-post-id="post.id"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
    @focus="handleFocus"
    @blur="handleBlur"
    tabindex="0"
    :aria-label="getAriaLabel()"
  >
    <!-- Hero Content Area (80% visual weight) -->
    <div class="story-content p-5 sm:p-6">
      <MomentContent 
        :content="post"
        :pregnancy-week="post.pregnancy_context?.current_week || 0"
        :post-type="post.type || 'update'"
        :media-items="post.media_items || []"
        :milestone-context="post.pregnancy_context"
        :expandable="hasLongContent"
        @expand="handleContentExpansion"
        @media-view="handleMediaView"
      />
    </div>

    <!-- Context Whisper (15% visual weight) -->
    <div class="context-whisper px-5 sm:px-6 pb-2">
      <PregnancyContext
        :week="post.pregnancy_context?.current_week || 0"
        :mood="post.pregnancy_context?.mood_indicator"
        :timestamp="new Date(post.created_at!)"
        :location="post.location"
        :is-milestone="post.type === 'milestone' || post.pregnancy_context?.is_milestone_week || false"
        :needs-family-response="post.engagement_stats?.needs_family_response || false"
        :viewer-relationship="getViewerRelationship()"
      />
    </div>

    <!-- Family Warmth (5% visual weight) -->
    <div class="family-warmth px-5 sm:px-6 pb-5">
      <FamilyWarmth
        :family-hearts="getFamilyHearts()"
        :recent-activity="getRecentFamilyActivity()"
        :memory-markers="getMemoryMarkers()"
        :support-level="getSupportLevel()"
        :show-details="showFamilyDetails"
        @view-activity="handleViewFamilyActivity"
      />
    </div>

    <!-- Gesture Feedback Overlays -->
    <div
      v-if="gestureState.active"
      class="gesture-overlay absolute inset-0 pointer-events-none flex items-center justify-center"
      :class="getGestureOverlayClass()"
    >
      <div class="gesture-indicator">
        <div 
          v-if="gestureState.type === 'love'"
          class="heart-particles"
        >
          <div class="heart-icon text-4xl animate-bounce">💕</div>
          <div class="text-white text-sm font-medium mt-2">Send Love</div>
        </div>
        <div 
          v-else-if="gestureState.type === 'memory'"
          class="memory-bookmark"
        >
          <div class="bookmark-icon text-4xl animate-pulse">🔖</div>
          <div class="text-white text-sm font-medium mt-2">Add to Memories</div>
        </div>
      </div>
    </div>

    <!-- Touch Target Areas for Accessibility -->
    <div class="touch-targets absolute inset-0 pointer-events-none">
      <div 
        class="love-zone absolute top-0 right-0 w-16 h-16 pointer-events-auto"
        @click="handleQuickLove"
        :aria-label="`Send love to ${getAuthorName()}'s story`"
        tabindex="0"
        @keydown.enter="handleQuickLove"
        @keydown.space="handleQuickLove"
      />
      <div 
        class="memory-zone absolute bottom-0 right-0 w-16 h-16 pointer-events-auto"
        @click="handleQuickMemory"
        :aria-label="`Add ${getAuthorName()}'s story to family memories`"
        tabindex="0"
        @keydown.enter="handleQuickMemory"
        @keydown.space="handleQuickMemory"
      />
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import type { components } from '~/types/api'
import { useAuth } from '~/composables/useAuth'
import { useGestureRecognition } from '~/composables/useGestureRecognition'
import { usePregnancyAnimations } from '~/composables/usePregnancyAnimations'
import MomentContent from './MomentContent.vue'
import PregnancyContext from './PregnancyContext.vue'
import FamilyWarmth from './FamilyWarmth.vue'

type EnrichedPost = components['schemas']['EnrichedPost']
type FamilyMember = components['schemas']['FamilyMember']
type FamilyActivity = components['schemas']['FamilyActivity']
type RelationshipType = 'partner' | 'parent' | 'sibling' | 'friend' | 'other'

interface Props {
  post: EnrichedPost
  familyWarmth: FamilyWarmthIndicator
  userPermissions: UserPermissions
  cardSize: 'comfortable' | 'cozy' | 'minimal'
  emotionalTone: 'supportive' | 'celebratory' | 'gentle'
}

interface FamilyWarmthIndicator {
  hearts: FamilyMember[]
  activities: FamilyActivity[]
  memoryCount: number
  supportLevel: 'gentle' | 'warm' | 'wrapped'
}

interface UserPermissions {
  canLove: boolean
  canAddToMemory: boolean
  canViewDetails: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cardSize: 'comfortable',
  emotionalTone: 'gentle',
  familyWarmth: () => ({
    hearts: [],
    activities: [],
    memoryCount: 0,
    supportLevel: 'gentle' as const
  }),
  userPermissions: () => ({
    canLove: true,
    canAddToMemory: true,
    canViewDetails: true
  })
})

const emit = defineEmits<{
  sendLove: [{ postId: string, method: 'gesture' | 'tap' }]
  addToMemory: [{ postId: string, method: 'gesture' | 'tap' }]
  viewFamilyActivity: [{ postId: string }]
  expandContent: [{ postId: string }]
  viewMedia: [{ postId: string, mediaIndex: number }]
}>()

// Composables
const auth = useAuth()
const { recognizeSwipe, recognizeDoubleTap, recognizeLongPress } = useGestureRecognition()
const { gentleHeartAnimation, softBookmarkAnimation, warmGlowEffect } = usePregnancyAnimations()

// Refs
const storyCardRef = ref<HTMLElement>()

// Local state
const isFocused = ref(false)
const isMemoryBound = ref(false)
const showFamilyDetails = ref(false)
const hasLongContent = ref(false)
const gestureState = ref({
  active: false,
  type: null as 'love' | 'memory' | null,
  progress: 0
})

// Touch/gesture handling
let touchStartX = 0
let touchStartY = 0
let touchStartTime = 0
let lastTap = 0

// Computed properties
const getAuthorName = () => {
  const author = props.post.author
  if (!author) return 'Someone'
  return author.display_name || author.first_name || 'Family member'
}

const getViewerRelationship = (): RelationshipType => {
  const currentUserId = auth.userProfile.value?.id
  const authorId = props.post.author?.id
  
  if (currentUserId === authorId) return 'other' // Own post
  // This would need to be determined from family relationship data
  return 'other'
}

const getFamilyHearts = () => props.familyWarmth.hearts || []
const getRecentFamilyActivity = () => props.familyWarmth.activities || []
const getMemoryMarkers = () => props.familyWarmth.memoryCount || 0
const getSupportLevel = () => props.familyWarmth.supportLevel || 'gentle'

const getCardSizeClass = () => {
  switch (props.cardSize) {
    case 'cozy': return 'story-card--cozy'
    case 'minimal': return 'story-card--minimal'
    default: return 'story-card--comfortable'
  }
}

const getEmotionalToneClass = () => {
  switch (props.emotionalTone) {
    case 'celebratory': return 'story-card--celebratory'
    case 'supportive': return 'story-card--supportive'
    default: return 'story-card--gentle'
  }
}

const getGestureOverlayClass = () => {
  const baseClass = 'bg-gradient-to-r opacity-90'
  if (gestureState.value.type === 'love') {
    return `${baseClass} from-pink-400 to-red-400`
  } else if (gestureState.value.type === 'memory') {
    return `${baseClass} from-blue-400 to-purple-400`
  }
  return baseClass
}

const getAriaLabel = () => {
  const author = getAuthorName()
  const week = props.post.pregnancy_context?.current_week
  const weekText = week ? ` from week ${week}` : ''
  const milestone = props.post.type === 'milestone' ? ' milestone story' : ' story'
  return `${author}'s${milestone}${weekText}. Double tap to send love, swipe left to add to memories.`
}

// Touch and gesture handlers
function handleTouchStart(event: TouchEvent) {
  const touch = event.touches[0]
  touchStartX = touch.clientX
  touchStartY = touch.clientY
  touchStartTime = Date.now()
}

function handleTouchMove(event: TouchEvent) {
  if (!event.touches[0]) return
  
  const touch = event.touches[0]
  const deltaX = touch.clientX - touchStartX
  const deltaY = touch.clientY - touchStartY
  
  // Only handle horizontal gestures to avoid conflicts with scrolling
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 30) {
    event.preventDefault()
    
    if (deltaX > 60) {
      // Swipe right - send love
      gestureState.value = { active: true, type: 'love', progress: Math.min(deltaX / 120, 1) }
    } else if (deltaX < -60) {
      // Swipe left - add to memory
      gestureState.value = { active: true, type: 'memory', progress: Math.min(-deltaX / 120, 1) }
    }
  }
}

function handleTouchEnd(event: TouchEvent) {
  const touchEndTime = Date.now()
  const touchDuration = touchEndTime - touchStartTime
  
  // Handle double tap
  if (touchDuration < 300) {
    const timeSinceLastTap = touchEndTime - lastTap
    if (timeSinceLastTap < 500) {
      handleDoubleTap()
    }
    lastTap = touchEndTime
  }
  
  // Complete gesture if active
  if (gestureState.value.active && gestureState.value.progress > 0.7) {
    if (gestureState.value.type === 'love') {
      handleGestureLove()
    } else if (gestureState.value.type === 'memory') {
      handleGestureMemory()
    }
  }
  
  // Reset gesture state
  gestureState.value = { active: false, type: null, progress: 0 }
}

function handleDoubleTap() {
  if (props.userPermissions.canLove) {
    handleQuickLove()
  }
}

function handleFocus() {
  isFocused.value = true
}

function handleBlur() {
  isFocused.value = false
}

// Action handlers
function handleQuickLove() {
  if (!props.userPermissions.canLove) return
  
  emit('sendLove', { postId: props.post.id!, method: 'tap' })
  
  // Trigger heart animation
  if (storyCardRef.value) {
    gentleHeartAnimation(storyCardRef.value)
  }
}

function handleGestureLove() {
  if (!props.userPermissions.canLove) return
  
  emit('sendLove', { postId: props.post.id!, method: 'gesture' })
  
  // Trigger heart animation
  if (storyCardRef.value) {
    gentleHeartAnimation(storyCardRef.value)
  }
}

function handleQuickMemory() {
  if (!props.userPermissions.canAddToMemory) return
  
  emit('addToMemory', { postId: props.post.id!, method: 'tap' })
  isMemoryBound.value = true
  
  // Trigger bookmark animation
  if (storyCardRef.value) {
    softBookmarkAnimation(storyCardRef.value)
  }
}

function handleGestureMemory() {
  if (!props.userPermissions.canAddToMemory) return
  
  emit('addToMemory', { postId: props.post.id!, method: 'gesture' })
  isMemoryBound.value = true
  
  // Trigger bookmark animation
  if (storyCardRef.value) {
    softBookmarkAnimation(storyCardRef.value)
  }
}

function handleViewFamilyActivity() {
  if (!props.userPermissions.canViewDetails) return
  
  showFamilyDetails.value = !showFamilyDetails.value
  emit('viewFamilyActivity', { postId: props.post.id! })
}

function handleContentExpansion() {
  emit('expandContent', { postId: props.post.id! })
}

function handleMediaView(mediaIndex: number) {
  emit('viewMedia', { postId: props.post.id!, mediaIndex })
}

// Lifecycle
onMounted(async () => {
  await nextTick()
  
  if (storyCardRef.value) {
    // Add gentle entrance animation
    warmGlowEffect(storyCardRef.value, {
      duration: 2000,
      intensity: 0.3,
      color: 'soft-pink'
    })
    
    // Check if content needs truncation
    const contentHeight = storyCardRef.value.querySelector('.story-content')?.scrollHeight || 0
    hasLongContent.value = contentHeight > 200
  }
})
</script>

<style scoped>
/* Story card base styles */
.story-card {
  /* Warm minimalistic shadow */
  box-shadow: 
    0 2px 8px rgba(248, 187, 208, 0.08),
    0 1px 3px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
  position: relative;
  overflow: visible;
}

.story-card:hover {
  box-shadow: 
    0 4px 12px rgba(248, 187, 208, 0.12),
    0 2px 6px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.story-card.is-focused {
  box-shadow: 
    0 0 0 2px #F8BBD0,
    0 4px 16px rgba(248, 187, 208, 0.2);
}

.story-card.is-memory-bound {
  position: relative;
}

.story-card.is-memory-bound::before {
  content: '🔖';
  position: absolute;
  top: -8px;
  right: 12px;
  font-size: 1.5rem;
  z-index: 10;
  animation: bookmark-pulse 2s ease-out;
}

/* Card size variations */
.story-card--comfortable {
  max-width: 100%;
}

.story-card--cozy .story-content {
  padding: 1rem 1.25rem;
}

.story-card--cozy .context-whisper,
.story-card--cozy .family-warmth {
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}

.story-card--minimal .story-content {
  padding: 0.75rem 1rem;
}

.story-card--minimal .context-whisper,
.story-card--minimal .family-warmth {
  padding-left: 1rem;
  padding-right: 1rem;
}

/* Emotional tone variations */
.story-card--celebratory {
  background: linear-gradient(135deg, #FFF3E0 0%, #FFFFFF 50%, #FFF8E1 100%);
  border: 1px solid rgba(248, 187, 208, 0.2);
}

.story-card--supportive {
  background: linear-gradient(135deg, #F3E5F5 0%, #FFFFFF 50%, #E8F5E8 100%);
  border: 1px solid rgba(178, 223, 219, 0.2);
}

.story-card--gentle {
  background: #FFFFFF;
}

/* Gesture overlay */
.gesture-overlay {
  border-radius: 1rem;
  z-index: 20;
  transition: opacity 0.2s ease;
}

.gesture-indicator {
  text-align: center;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Touch zones for accessibility */
.touch-targets .love-zone,
.touch-targets .memory-zone {
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.touch-targets .love-zone:hover {
  background: rgba(248, 187, 208, 0.1);
}

.touch-targets .memory-zone:hover {
  background: rgba(178, 223, 219, 0.1);
}

/* Content sections visual hierarchy */
.story-content {
  /* 80% visual weight */
  position: relative;
  z-index: 3;
}

.context-whisper {
  /* 15% visual weight */
  opacity: 0.8;
  position: relative;
  z-index: 2;
}

.family-warmth {
  /* 5% visual weight */
  opacity: 0.9;
  position: relative;
  z-index: 1;
}

/* Animations */
@keyframes bookmark-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1) rotate(-5deg);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1) rotate(-3deg);
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .story-card {
    margin-bottom: 16px;
    border-radius: 1rem;
  }
  
  .story-content {
    padding: 1rem;
  }
  
  .context-whisper,
  .family-warmth {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  /* Increase touch target sizes on mobile */
  .touch-targets .love-zone,
  .touch-targets .memory-zone {
    width: 20px;
    height: 20px;
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .story-card,
  .gesture-indicator * {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .story-card {
    border: 2px solid #000;
    box-shadow: none;
  }
  
  .story-card:hover {
    border-color: #F8BBD0;
    box-shadow: 0 0 0 3px rgba(248, 187, 208, 0.5);
  }
}

/* Dark mode support (if ever needed) */
@media (prefers-color-scheme: dark) {
  .story-card {
    background: #1f2937;
    color: #f9fafb;
  }
  
  .story-card--celebratory {
    background: linear-gradient(135deg, #374151 0%, #1f2937 50%, #374151 100%);
  }
}
</style>