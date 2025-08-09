<template>
  <div class="post-header flex items-start justify-between">
    <!-- Author Info -->
    <div class="flex items-start gap-3 flex-1">
      <!-- Avatar -->
      <div class="relative">
        <div
          :class="cn(
            'w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg',
            getAvatarColor()
          )"
        >
          {{ getInitials() }}
        </div>
        
        <!-- Pregnancy status indicator -->
        <div
          v-if="post.pregnancy_context?.current_week"
          :class="cn(
            'absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-2 border-white flex items-center justify-center text-xs font-bold',
            getMoodColor()
          )"
          :title="`Week ${post.pregnancy_context.current_week}`"
        >
          {{ post.pregnancy_context.current_week }}
        </div>
      </div>

      <!-- Author Details -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <h4 class="font-semibold text-warm-graphite font-inter">
            {{ getAuthorName() }}
          </h4>
          
          <!-- "You" Badge for current user -->
          <span
            v-if="isCurrentUser"
            class="px-2 py-1 bg-blush-rose/20 text-warm-graphite text-xs font-bold rounded-full border border-blush-rose/30"
          >
            You
          </span>
          
          <!-- Relationship Badge -->
          <span
            v-else-if="authorRelationship"
            class="px-2 py-1 bg-sage-green/20 text-soft-charcoal text-xs font-medium rounded-full"
          >
            {{ authorRelationship }}
          </span>
          
          <!-- Post Type Badge -->
          <span
            v-if="post.type"
            :class="cn(
              'px-2 py-1 text-xs font-medium rounded-full',
              getPostTypeBadgeColor()
            )"
          >
            {{ getPostTypeIcon() }} {{ getPostTypeLabel() }}
          </span>
        </div>

        <!-- Pregnancy Context -->
        <div v-if="post.pregnancy_context?.current_week || post.pregnancy_context?.trimester" class="flex items-center gap-2 mt-1 text-sm text-soft-charcoal">
          <span v-if="post.pregnancy_context.current_week" class="font-medium">
            Week {{ post.pregnancy_context.current_week }}
          </span>
          <span v-if="post.pregnancy_context.current_week && post.pregnancy_context.trimester" class="text-neutral-gray">•</span>
          <span v-if="post.pregnancy_context.trimester">
            Trimester {{ post.pregnancy_context.trimester }}
          </span>
          <span v-if="post.pregnancy_context.is_milestone_week" class="text-neutral-gray">•</span>
          <span v-if="post.pregnancy_context.is_milestone_week" class="text-blush-rose font-medium flex items-center gap-1">
            <Star class="w-3 h-3" />
            Milestone Week
          </span>
        </div>

        <!-- Timestamp and Mood -->
        <div class="flex items-center gap-2 mt-1 text-sm text-neutral-gray">
          <time :datetime="post.created_at" :title="getFullTimestamp()">
            {{ getRelativeTime() }}
          </time>
          
          <span v-if="post.mood" class="text-light-gray">•</span>
          <span v-if="post.mood" class="flex items-center gap-1">
            <span>{{ getMoodEmoji() }}</span>
            <span class="capitalize">{{ post.mood }}</span>
          </span>
          
          <span v-if="post.privacy_level" class="text-light-gray">•</span>
          <div v-if="post.privacy_level" class="flex items-center gap-1">
            {{ getPrivacyIcon() }}
            <span class="capitalize text-xs">{{ post.privacy_level }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Menu Button -->
    <div v-if="showMenu" class="flex-shrink-0 ml-2">
      <button
        ref="menuRef"
        @click="toggleMenu"
        class="p-2 hover:bg-warm-gray rounded-full transition-colors"
        :aria-expanded="isMenuOpen"
        aria-label="Post options"
      >
        <MoreVertical class="w-5 h-5 text-neutral-gray" />
      </button>

      <!-- Dropdown Menu -->
      <Teleport to="body">
        <div
          v-if="isMenuOpen"
          ref="menuDropdownRef"
          :style="menuStyle"
          class="fixed z-50 bg-off-white rounded-lg shadow-lg border border-light-gray py-2 min-w-48"
          @click.stop
        >
          <button
            v-for="action in menuActions"
            :key="action.key"
            @click="handleMenuAction(action.key)"
            :class="cn(
              'w-full px-4 py-2 text-left text-sm hover:bg-warm-gray transition-colors flex items-center gap-2 text-soft-charcoal',
              action.destructive && 'text-error hover:bg-error/10'
            )"
          >
            <span class="text-base">{{ action.icon }}</span>
            <span>{{ action.label }}</span>
          </button>
        </div>
      </Teleport>

      <!-- Menu Backdrop -->
      <div
        v-if="isMenuOpen"
        class="fixed inset-0 z-40"
        @click="closeMenu"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'
import { MoreVertical, Star } from 'lucide-vue-next'

type EnrichedPost = components['schemas']['EnrichedPost']

interface Props {
  post: EnrichedPost
  authorRelationship?: string
  showPrivacy?: boolean
  showMenu?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showPrivacy: false,
  showMenu: false
})

const emit = defineEmits<{
  menuAction: [action: string]
}>()

console.log(props.post)
// Local state
const isMenuOpen = ref(false)
const menuRef = ref<HTMLElement>()
const menuDropdownRef = ref<HTMLElement>()
const menuStyle = ref<Record<string, string>>({})

// Menu actions based on post context
const menuActions = computed(() => {
  const actions = [
    { key: 'bookmark', icon: '🔖', label: 'Save to Memory Book' },
    { key: 'share', icon: '↗️', label: 'Share Post' },
    { key: 'copy-link', icon: '🔗', label: 'Copy Link' }
  ]

  // Add moderation actions if user has permissions
  if (post.value.can_edit) {
    actions.push(
      { key: 'edit', icon: '✏️', label: 'Edit Post' },
      { key: 'delete', icon: '🗑️', label: 'Delete Post', destructive: true }
    )
  }

  // Add reporting option
  actions.push({ key: 'report', icon: '⚠️', label: 'Report Post', destructive: true })

  return actions
})

// Auth composable for checking current user
const auth = useAuth()

// Computed properties
const isCurrentUser = computed(() => {
  const currentUserId = auth.userProfile.value?.id
  const postAuthorId = props.post.author?.id
  return currentUserId && postAuthorId && currentUserId === postAuthorId
})

function getAuthorName() {
  if (!props.post.author) {
    return 'Unknown User'
  }
  
  const firstName = props.post.author.first_name?.trim() || ''
  const lastName = props.post.author.last_name?.trim() || ''
  
  if (firstName && lastName) {
    return `${firstName} ${lastName}`
  }
  
  if (firstName) {
    return firstName
  }
  
  if (lastName) {
    return lastName
  }
  
  return props.post.author.email || 'Unknown User'
}

function getInitials() {
  const name = getAuthorName()
  
  if (name === 'Unknown User') {
    return '?'
  }
  
  // Check if it's an email address
  if (name.includes('@')) {
    // For emails, try to get meaningful initials
    const emailPart = name.split('@')[0]
    // Check if email has dots or underscores
    const parts = emailPart.split(/[._-]/).filter(part => part.length > 0)
    if (parts.length >= 2) {
      return parts.slice(0, 2).map(part => part.charAt(0)).join('').toUpperCase()
    }
    // Otherwise use first two letters of email
    return emailPart.slice(0, 2).toUpperCase()
  }
  
  const words = name.split(' ').filter(word => word.length > 0)
  
  if (words.length === 0) {
    return '?'
  }
  
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  
  return words
    .slice(0, 2)
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
}

function getAvatarColor() {
  const colors = [
    'bg-blush-rose',
    'bg-sage-green', 
    'bg-dusty-lavender',
    'bg-light-coral',
    'bg-soft-blue'
  ]
  
  const authorId = props.post.author?.id || ''
  if (!authorId) {
    return 'bg-gray-400' // Default color for unknown users
  }
  
  const colorIndex = authorId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  return colors[colorIndex]
}

function getMoodColor() {
  const mood = props.post.mood
  if (!mood) return 'bg-gray-400'
  
  const moodColors = {
    happy: 'bg-blush-rose',
    excited: 'bg-blush-rose',
    peaceful: 'bg-sage-green',
    tired: 'bg-dusty-lavender',
    anxious: 'bg-info',
    grateful: 'bg-warm-gray'
  }
  
  return moodColors[mood] || 'bg-gray-400'
}

function getPostTypeLabel() {
  const typeLabels = {
    milestone: 'Milestone',
    update: 'Update',
    photo: 'Photo',
    journal: 'Journal',
    question: 'Question',
    celebration: 'Celebration'
  }
  
  return typeLabels[props.post.type || 'update'] || 'Update'
}

function getPostTypeIcon() {
  const typeIcons = {
    milestone: '🎉',
    update: '📝',
    photo: '📸',
    journal: '📖',
    question: '❓',
    celebration: '🎊'
  }
  
  return typeIcons[props.post.type || 'update'] || '📝'
}

function getPostTypeBadgeColor() {
  const type = props.post.type
  
  const typeColors = {
    milestone: 'bg-blush-rose/20 text-warm-graphite',
    update: 'bg-sage-green/20 text-soft-charcoal',
    photo: 'bg-dusty-lavender/20 text-soft-charcoal',
    journal: 'bg-info/20 text-soft-charcoal',
    question: 'bg-warning/20 text-soft-charcoal',
    celebration: 'bg-blush-rose/20 text-warm-graphite'
  }
  
  return typeColors[type || 'update'] || 'bg-warm-gray text-neutral-gray'
}

function getMoodEmoji() {
  const mood = props.post.mood
  if (!mood) return ''
  
  const moodEmojis = {
    happy: '😊',
    excited: '😍',
    peaceful: '😌',
    tired: '😴',
    anxious: '😰',
    grateful: '🙏'
  }
  
  return moodEmojis[mood] || '😊'
}

function getPrivacyIcon() {
  const privacy = props.post.privacy_level
  
  const privacyIcons = {
    public: '🌍',
    family: '👨‍👩‍👧‍👦',
    close_family: '👪',
    private: '🔒'
  }
  
  return privacyIcons[privacy || 'family'] || '👨‍👩‍👧‍👦'
}

function getRelativeTime() {
  if (!props.post.created_at) return 'Unknown time'
  
  const now = new Date()
  const postTime = new Date(props.post.created_at)
  const diffInSeconds = Math.floor((now.getTime() - postTime.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return postTime.toLocaleDateString()
}

function getFullTimestamp() {
  if (!props.post.created_at) return ''
  return new Date(props.post.created_at).toLocaleString()
}

// Menu methods
async function toggleMenu() {
  if (isMenuOpen.value) {
    closeMenu()
  } else {
    await openMenu()
  }
}

async function openMenu() {
  isMenuOpen.value = true
  await nextTick()
  positionMenu()
}

function closeMenu() {
  isMenuOpen.value = false
}

function handleMenuAction(action: string) {
  emit('menuAction', action)
  closeMenu()
}

function positionMenu() {
  if (!menuRef.value || !menuDropdownRef.value) return
  
  const trigger = menuRef.value.getBoundingClientRect()
  const menu = menuDropdownRef.value
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  }
  
  // Default position: below trigger, aligned to right
  let top = trigger.bottom + 4
  let left = trigger.right - menu.offsetWidth
  
  // Adjust for viewport bounds
  if (left < 8) {
    left = 8
  }
  
  if (top + menu.offsetHeight > viewport.height - 8) {
    top = trigger.top - menu.offsetHeight - 4
  }
  
  if (top < 8) {
    top = 8
  }
  
  menuStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

// Click outside handler
function handleClickOutside(event: Event) {
  if (
    isMenuOpen.value &&
    menuRef.value &&
    menuDropdownRef.value &&
    !menuRef.value.contains(event.target as Node) &&
    !menuDropdownRef.value.contains(event.target as Node)
  ) {
    closeMenu()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Header animations */
.post-header {
  animation: header-appear 0.3s ease-out;
}

@keyframes header-appear {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Avatar hover effect */
.post-header .relative:hover {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

/* Badge animations */
.post-header span {
  animation: badge-appear 0.4s ease-out;
}

@keyframes badge-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Menu dropdown animation */
.menu-dropdown {
  animation: menu-appear 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top right;
}

@keyframes menu-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-5px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Enhanced accessibility */
button:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .post-header {
    padding: 0.5rem 0;
  }
  
  .post-header .w-12 {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 0.875rem;
  }
  
  .post-header .text-sm {
    font-size: 0.75rem;
  }
  
  .menu-dropdown {
    left: 1rem !important;
    right: 1rem !important;
    max-width: calc(100vw - 2rem);
    min-width: unset;
  }
}

/* Smooth transitions */
* {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
