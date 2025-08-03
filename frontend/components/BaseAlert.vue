<template>
  <div :class="cn(alertVariants({ variant }), $attrs.class)" role="alert">
    <div class="flex items-start gap-3">
      <div v-if="showIcon" :class="cn(iconVariants({ variant }))">
        <component :is="iconComponent" class="h-5 w-5" />
      </div>
      
      <div class="flex-1 space-y-2">
        <div v-if="hasHeaderSlot || title" :class="cn(titleVariants({ variant }))">
          <slot name="header">
            <h5 v-if="title" class="font-medium leading-none tracking-tight font-primary">
              {{ title }}
            </h5>
          </slot>
        </div>
        
        <div :class="cn(contentVariants({ variant }))">
          <slot>
            <p v-if="description" class="text-sm font-secondary">
              {{ description }}
            </p>
          </slot>
        </div>
      </div>
      
      <button
        v-if="dismissible"
        @click="$emit('dismiss')"
        :class="cn(dismissButtonVariants({ variant }))"
        aria-label="Dismiss alert"
      >
        <X class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '~/utils/cn'
import { useSlots, computed } from 'vue'
import { Heart, Baby, Sparkles, Info, AlertTriangle, CheckCircle, X } from 'lucide-vue-next'

const slots = useSlots()
const hasHeaderSlot = computed(() => !!slots.header)

const alertVariants = cva(
  'relative w-full rounded-xl border p-4 text-left transition-all duration-200',
  {
    variants: {
      variant: {
        // Pregnancy-themed supportive variants
        supportive: 'bg-gentle-mint/15 text-gray-800 border-gentle-mint/30 [&>svg]:text-gentle-mint',
        celebration: 'bg-light-coral/15 text-gray-800 border-light-coral/30 [&>svg]:text-light-coral',
        milestone: 'bg-soft-pink/15 text-gray-800 border-soft-pink/30 [&>svg]:text-soft-pink',
        calming: 'bg-muted-lavender/15 text-gray-800 border-muted-lavender/30 [&>svg]:text-muted-lavender',
        encouragement: 'bg-warm-beige/40 text-gray-800 border-warm-beige/60 [&>svg]:text-orange-500',
        // Standard alert variants with pregnancy theme
        default: 'bg-background text-foreground border-warm-beige/40',
        info: 'bg-soft-blue/15 text-gray-800 border-soft-blue/30 [&>svg]:text-blue-600',
        warning: 'bg-orange-50 text-orange-900 border-orange-200 [&>svg]:text-orange-600',
        destructive: 'bg-red-50 text-red-900 border-red-200 [&>svg]:text-red-600',
        success: 'bg-green-50 text-green-900 border-green-200 [&>svg]:text-green-600',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const iconVariants = cva(
  'mt-0.5 flex-shrink-0',
  {
    variants: {
      variant: {
        supportive: 'text-gentle-mint',
        celebration: 'text-light-coral',
        milestone: 'text-soft-pink',
        calming: 'text-muted-lavender',
        encouragement: 'text-orange-500',
        default: 'text-foreground',
        info: 'text-blue-600',
        warning: 'text-orange-600',
        destructive: 'text-red-600',
        success: 'text-green-600',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const titleVariants = cva(
  '',
  {
    variants: {
      variant: {
        supportive: 'text-gray-800',
        celebration: 'text-gray-800',
        milestone: 'text-gray-800',
        calming: 'text-gray-800',
        encouragement: 'text-gray-800',
        default: 'text-foreground',
        info: 'text-gray-800',
        warning: 'text-orange-900',
        destructive: 'text-red-900',
        success: 'text-green-900',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const contentVariants = cva(
  '',
  {
    variants: {
      variant: {
        supportive: 'text-gray-700',
        celebration: 'text-gray-700',
        milestone: 'text-gray-700',
        calming: 'text-gray-700',
        encouragement: 'text-gray-700',
        default: 'text-muted-foreground',
        info: 'text-gray-700',
        warning: 'text-orange-800',
        destructive: 'text-red-800',
        success: 'text-green-800',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const dismissButtonVariants = cva(
  'mt-0.5 opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none rounded-md p-1',
  {
    variants: {
      variant: {
        supportive: 'text-gray-600 hover:text-gray-800',
        celebration: 'text-gray-600 hover:text-gray-800',
        milestone: 'text-gray-600 hover:text-gray-800',
        calming: 'text-gray-600 hover:text-gray-800',
        encouragement: 'text-gray-600 hover:text-gray-800',
        default: 'text-muted-foreground hover:text-foreground',
        info: 'text-gray-600 hover:text-gray-800',
        warning: 'text-orange-700 hover:text-orange-900',
        destructive: 'text-red-700 hover:text-red-900',
        success: 'text-green-700 hover:text-green-900',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

/* @vue-ignore */
interface AlertProps extends VariantProps<typeof alertVariants> {
  title?: string
  description?: string
  showIcon?: boolean
  dismissible?: boolean
}

const props = withDefaults(defineProps<AlertProps>(), {
  showIcon: true,
  dismissible: false,
})

defineEmits<{
  dismiss: []
}>()

const iconComponent = computed(() => {
  switch (props.variant) {
    case 'supportive':
      return Heart
    case 'celebration':
      return Sparkles
    case 'milestone':
      return Baby
    case 'calming':
      return Heart
    case 'encouragement':
      return Heart
    case 'info':
      return Info
    case 'warning':
      return AlertTriangle
    case 'destructive':
      return AlertTriangle
    case 'success':
      return CheckCircle
    default:
      return Info
  }
})
</script>

<style scoped>
/* Enhanced alert styling for pregnancy theme */
div[role="alert"] {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Gentle entrance animation */
div[role="alert"] {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Supportive messaging emphasis */
.supportive-emphasis {
  font-style: italic;
  font-weight: 500;
}

/* Milestone celebration effects */
.milestone-glow {
  position: relative;
}

.milestone-glow::before {
  content: '';
  position: absolute;
  inset: -1px;
  background: linear-gradient(45deg, rgba(248, 187, 208, 0.3), rgba(225, 190, 231, 0.3));
  border-radius: inherit;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.milestone-glow:hover::before {
  opacity: 1;
}
</style>