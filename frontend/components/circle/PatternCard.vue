<template>
  <button
    @click="handleSelect"
    :disabled="disabled"
    :class="[
      'group relative p-4 rounded-xl border-2 transition-all duration-200 text-left w-full',
      'focus:outline-none focus:ring-2 focus:ring-gentle-mint/50 focus:ring-offset-2',
      selected
        ? 'border-gentle-mint bg-gradient-to-br from-gentle-mint/10 to-soft-pink/5 shadow-lg scale-[1.02]'
        : 'border-gray-200 hover:border-gentle-mint/50 hover:bg-gradient-to-br hover:from-gentle-mint/5 hover:to-soft-pink/3 hover:shadow-md hover:scale-[1.01]',
      disabled && 'opacity-50 cursor-not-allowed'
    ]"
    :aria-pressed="selected"
    :aria-label="`Select ${pattern.name} circle - ${pattern.description}`"
    role="radio"
  >
    <!-- Pattern Content -->
    <div class="flex flex-col items-center space-y-3 relative">
      <!-- Icon with subtle animation -->
      <div
        :class="[
          'text-3xl transition-transform duration-200',
          selected ? 'scale-110' : 'group-hover:scale-105'
        ]"
      >
        {{ pattern.icon }}
      </div>
      
      <!-- Name -->
      <div class="font-primary font-medium text-gray-800 text-center">
        {{ pattern.name }}
      </div>
      
      <!-- Description -->
      <div class="text-xs text-gray-600 text-center leading-relaxed">
        {{ pattern.description }}
      </div>
      
      <!-- Member count badge -->
      <div class="flex items-center justify-center space-x-1 text-xs text-gray-500">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
          />
        </svg>
        <span>{{ memberCount }}</span>
      </div>
    </div>

    <!-- Selected indicator -->
    <div 
      v-if="selected"
      class="absolute top-3 right-3 w-6 h-6 bg-gradient-to-br from-gentle-mint to-soft-pink rounded-full 
             flex items-center justify-center shadow-sm"
      aria-hidden="true"
    >
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
      </svg>
    </div>

    <!-- Usage frequency indicator -->
    <div 
      v-if="pattern.usage_frequency > 0"
      class="absolute top-3 left-3 bg-soft-pink/90 text-white text-xs 
             rounded-full w-6 h-6 flex items-center justify-center font-medium shadow-sm"
      :title="`Used ${pattern.usage_frequency} times recently`"
      aria-hidden="true"
    >
      {{ pattern.usage_frequency }}
    </div>

    <!-- Hover overlay for better visual feedback -->
    <div
      class="absolute inset-0 rounded-xl bg-gradient-to-br from-gentle-mint/0 to-soft-pink/0
             group-hover:from-gentle-mint/5 group-hover:to-soft-pink/5 
             transition-all duration-200 pointer-events-none"
      aria-hidden="true"
    ></div>

    <!-- Subtle glow effect when selected -->
    <div
      v-if="selected"
      class="absolute inset-0 rounded-xl bg-gradient-to-br from-gentle-mint/10 to-soft-pink/10
             animate-gentle-pulse pointer-events-none"
      aria-hidden="true"
    ></div>
  </button>
</template>

<script setup lang="ts">
import type { CirclePattern } from '~/types/api'

// Props
interface Props {
  pattern: CirclePattern
  selected?: boolean
  memberCount?: number
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  memberCount: 0,
  disabled: false
})

// Emits
const emit = defineEmits<{
  select: [pattern: CirclePattern]
}>()

// Methods
const handleSelect = () => {
  if (!props.disabled) {
    emit('select', props.pattern)
  }
}
</script>

<style scoped>
/* Enhanced button interactions */
button:not(:disabled):active {
  transform: scale(0.98);
}

/* Smooth transitions for all states */
button, button > div {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Subtle shadow enhancements */
.shadow-lg {
  box-shadow: 
    0 10px 15px -3px rgba(74, 222, 128, 0.1),
    0 4px 6px -2px rgba(74, 222, 128, 0.05),
    0 0 0 1px rgba(74, 222, 128, 0.1);
}

.shadow-md {
  box-shadow: 
    0 4px 6px -1px rgba(74, 222, 128, 0.08),
    0 2px 4px -1px rgba(74, 222, 128, 0.04);
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  button {
    border-width: 3px;
  }
  
  .selected {
    background: highlight;
    color: highlighttext;
  }
}

/* Focus visible improvements */
button:focus-visible {
  outline: 2px solid theme('colors.gentle-mint');
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.2);
}

/* Usage frequency badge hover effect */
div[title]:hover {
  transform: scale(1.1);
}
</style>