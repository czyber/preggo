<template>
  <div 
    v-if="shouldShowIndicator"
    class="circle-indicator"
    :class="indicatorClasses"
    :title="tooltipText"
  >
    <!-- Icon and Label -->
    <div class="flex items-center space-x-2">
      <span class="indicator-icon">{{ circle.icon }}</span>
      <span class="indicator-text">{{ circle.name }}</span>
      
      <!-- Member count -->
      <div v-if="showMemberCount && circle.member_count" class="flex items-center space-x-1 text-xs text-gray-500">
        <Users class="h-3 w-3" />
        <span>{{ circle.member_count }}</span>
      </div>
    </div>

    <!-- Privacy Level Indicator -->
    <div v-if="showPrivacyLevel" class="privacy-indicator">
      <div class="flex items-center space-x-1">
        <component 
          :is="privacyIcon" 
          class="h-3 w-3"
          :class="privacyIconClass"
        />
        <span class="text-xs text-gray-500">{{ privacyLabel }}</span>
      </div>
    </div>

    <!-- Interactive Tooltip -->
    <div 
      v-if="showTooltip && isHovered"
      class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-30"
    >
      <div class="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap shadow-lg">
        <div class="font-medium mb-1">{{ circle.name }}</div>
        <div class="text-gray-300">{{ circle.description }}</div>
        <div v-if="circle.members" class="mt-2 text-gray-300">
          {{ circle.members.length }} {{ circle.members.length === 1 ? 'person' : 'people' }} will see this
        </div>
        
        <!-- Arrow -->
        <div class="absolute top-full left-1/2 transform -translate-x-1/2 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Users, Lock, Globe, Eye, EyeOff, Shield } from 'lucide-vue-next'

interface CirclePattern {
  id: string
  name: string
  icon: string
  description: string
  member_count?: number
  privacy_level: 'partner_only' | 'immediate' | 'extended' | 'friends' | 'all_family' | 'public'
  members?: Array<{
    id: string
    display_name?: string
    first_name?: string
    relationship?: string
  }>
}

interface Props {
  circle: CirclePattern
  variant?: 'subtle' | 'prominent' | 'badge'
  size?: 'sm' | 'md' | 'lg'
  showMemberCount?: boolean
  showPrivacyLevel?: boolean
  showTooltip?: boolean
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'inline'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'subtle',
  size: 'md',
  showMemberCount: false,
  showPrivacyLevel: false,
  showTooltip: true,
  position: 'top-right'
})

const emit = defineEmits<{
  click: [circle: CirclePattern]
  hover: [circle: CirclePattern]
}>()

// Local state
const isHovered = ref(false)
const indicatorRef = ref<HTMLElement>()

// Computed properties
const shouldShowIndicator = computed(() => {
  return props.circle && props.circle.id !== 'all'
})

const indicatorClasses = computed(() => {
  const baseClasses = ['circle-indicator']
  
  // Variant classes
  switch (props.variant) {
    case 'subtle':
      baseClasses.push('bg-white/90', 'backdrop-blur-sm', 'border', 'border-gray-200', 'text-gray-700')
      break
    case 'prominent':
      baseClasses.push('bg-gradient-to-r', 'from-gentle-mint/20', 'to-soft-pink/20', 'border', 'border-gentle-mint/30', 'text-gray-800')
      break
    case 'badge':
      baseClasses.push('bg-gray-100', 'text-gray-600', 'border', 'border-gray-200')
      break
  }
  
  // Size classes
  switch (props.size) {
    case 'sm':
      baseClasses.push('px-2', 'py-1', 'text-xs', 'rounded-md')
      break
    case 'md':
      baseClasses.push('px-3', 'py-1.5', 'text-sm', 'rounded-lg')
      break
    case 'lg':
      baseClasses.push('px-4', 'py-2', 'text-base', 'rounded-lg')
      break
  }
  
  // Position classes
  switch (props.position) {
    case 'top-right':
      baseClasses.push('absolute', 'top-4', 'right-4')
      break
    case 'top-left':
      baseClasses.push('absolute', 'top-4', 'left-4')
      break
    case 'bottom-right':
      baseClasses.push('absolute', 'bottom-4', 'right-4')
      break
    case 'bottom-left':
      baseClasses.push('absolute', 'bottom-4', 'left-4')
      break
    case 'inline':
      baseClasses.push('inline-flex')
      break
  }
  
  // Interactive states
  baseClasses.push('transition-all', 'duration-200', 'hover:shadow-md', 'cursor-pointer')
  
  return baseClasses
})

const privacyIcon = computed(() => {
  switch (props.circle.privacy_level) {
    case 'partner_only':
      return Lock
    case 'immediate':
      return Shield
    case 'extended':
      return Users
    case 'friends':
      return Eye
    case 'all_family':
      return Globe
    case 'public':
      return Globe
    default:
      return Users
  }
})

const privacyIconClass = computed(() => {
  switch (props.circle.privacy_level) {
    case 'partner_only':
      return 'text-red-500'
    case 'immediate':
      return 'text-orange-500'
    case 'extended':
      return 'text-blue-500'
    case 'friends':
      return 'text-green-500'
    case 'all_family':
      return 'text-purple-500'
    case 'public':
      return 'text-gray-500'
    default:
      return 'text-gray-500'
  }
})

const privacyLabel = computed(() => {
  switch (props.circle.privacy_level) {
    case 'partner_only':
      return 'Private'
    case 'immediate':
      return 'Close Family'
    case 'extended':
      return 'Extended Family'
    case 'friends':
      return 'Friends'
    case 'all_family':
      return 'All Family'
    case 'public':
      return 'Public'
    default:
      return 'Family'
  }
})

const tooltipText = computed(() => {
  if (!props.showTooltip) return ''
  
  const memberText = props.circle.member_count 
    ? `${props.circle.member_count} ${props.circle.member_count === 1 ? 'person' : 'people'}`
    : 'Family'
  
  return `${props.circle.name} • ${memberText} can see this`
})

// Methods
function handleClick() {
  emit('click', props.circle)
}

function handleMouseEnter() {
  isHovered.value = true
  emit('hover', props.circle)
}

function handleMouseLeave() {
  isHovered.value = false
}

// Animation on mount
onMounted(() => {
  if (indicatorRef.value) {
    // Add entrance animation
    indicatorRef.value.style.opacity = '0'
    indicatorRef.value.style.transform = 'scale(0.8) translateY(-10px)'
    
    requestAnimationFrame(() => {
      if (indicatorRef.value) {
        indicatorRef.value.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)'
        indicatorRef.value.style.opacity = '1'
        indicatorRef.value.style.transform = 'scale(1) translateY(0)'
      }
    })
  }
})
</script>

<style scoped>
.circle-indicator {
  font-family: inherit;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  max-width: fit-content;
  user-select: none;
  z-index: 10;
}

.indicator-icon {
  font-size: 1em;
  line-height: 1;
}

.indicator-text {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.privacy-indicator {
  margin-left: 0.5rem;
  opacity: 0.7;
}

/* Hover effects */
.circle-indicator:hover {
  transform: translateY(-1px);
}

.circle-indicator:hover .privacy-indicator {
  opacity: 1;
}

/* Responsive design */
@media (max-width: 640px) {
  .circle-indicator {
    font-size: 0.75rem;
  }
  
  .indicator-text {
    max-width: 100px;
  }
  
  /* Hide privacy level on mobile for space */
  .privacy-indicator {
    display: none;
  }
}

/* Animation keyframes */
@keyframes circle-appear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Focus styles for accessibility */
.circle-indicator:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.1);
}

/* Tooltip positioning adjustments */
@media (max-width: 768px) {
  .absolute.bottom-full {
    position: fixed;
    bottom: auto;
    top: 50%;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    max-width: calc(100vw - 2rem);
  }
  
  .absolute.bottom-full .absolute.top-full {
    display: none; /* Hide arrow on mobile */
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .circle-indicator,
  .circle-indicator * {
    animation: none !important;
    transition: none !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .circle-indicator {
    border-width: 2px;
    border-color: currentColor;
  }
}
</style>