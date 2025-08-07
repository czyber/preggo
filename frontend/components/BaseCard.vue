<template>
  <div :class="cn(cardVariants({ variant, size }), $attrs.class)">
    <div
      v-if="hasHeaderSlot || title || description"
      :class="cn(headerVariants({ variant }))"
    >
      <slot name="header">
        <div v-if="title || description" class="space-y-1.5">
          <h3 v-if="title" :class="cn(titleVariants({ variant }))">
            {{ title }}
          </h3>
          <p v-if="description" :class="cn(descriptionVariants({ variant }))">
            {{ description }}
          </p>
        </div>
      </slot>
    </div>
    
    <div :class="cn(contentVariants({ variant, size }))">
      <slot />
    </div>
    
    <div
      v-if="hasFooterSlot"
      :class="cn(footerVariants({ variant }))"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '~/components/ui/utils'
import { useSlots } from 'vue'

const slots = useSlots()
const hasHeaderSlot = computed(() => !!slots.header)
const hasFooterSlot = computed(() => !!slots.footer)

const cardVariants = cva(
  'rounded-2xl border text-card-foreground shadow-sm transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'bg-card border-warm-neutral hover:shadow-md',
        supportive: 'bg-gentle-mint/10 border-gentle-mint/30 hover:bg-gentle-mint/15 hover:shadow-md',
        celebration: 'bg-light-coral/10 border-light-coral/30 hover:bg-light-coral/15 hover:shadow-md',
        calming: 'bg-muted-lavender/10 border-muted-lavender/30 hover:bg-muted-lavender/15 hover:shadow-md',
        warm: 'bg-warm-neutral/30 border-warm-neutral/50 hover:bg-warm-neutral/40 hover:shadow-md',
        milestone: 'bg-gradient-to-br from-soft-pink/10 to-gentle-mint/10 border-soft-pink/20 hover:shadow-lg',
        progress: 'bg-gradient-to-r from-gentle-mint/5 to-soft-blue/5 border-gentle-mint/20 hover:shadow-md',
      },
      size: {
        sm: 'p-4',
        default: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const headerVariants = cva(
  'flex flex-col space-y-1.5',
  {
    variants: {
      variant: {
        default: '',
        supportive: 'border-b border-gentle-mint/20 pb-4 mb-4',
        celebration: 'border-b border-light-coral/20 pb-4 mb-4',
        calming: 'border-b border-muted-lavender/20 pb-4 mb-4',
        warm: 'border-b border-warm-neutral/40 pb-4 mb-4',
        milestone: 'border-b border-soft-pink/20 pb-4 mb-4',
        progress: 'border-b border-gentle-mint/20 pb-4 mb-4',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const titleVariants = cva(
  'text-lg font-semibold leading-none tracking-tight font-primary',
  {
    variants: {
      variant: {
        default: 'text-card-foreground',
        supportive: 'text-gray-800',
        celebration: 'text-gray-800',
        calming: 'text-gray-800',
        warm: 'text-gray-800',
        milestone: 'text-gray-800',
        progress: 'text-gray-800',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const descriptionVariants = cva(
  'text-sm font-secondary',
  {
    variants: {
      variant: {
        default: 'text-muted-foreground',
        supportive: 'text-gray-600',
        celebration: 'text-gray-600',
        calming: 'text-gray-600',
        warm: 'text-gray-600',
        milestone: 'text-gray-600',
        progress: 'text-gray-600',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

const contentVariants = cva(
  'font-secondary',
  {
    variants: {
      variant: {
        default: '',
        supportive: '',
        celebration: '',
        calming: '',
        warm: '',
        milestone: '',
        progress: '',
      },
      size: {
        sm: 'text-sm',
        default: 'text-base',
        lg: 'text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const footerVariants = cva(
  'pt-4 mt-4',
  {
    variants: {
      variant: {
        default: 'border-t border-warm-neutral/40',
        supportive: 'border-t border-gentle-mint/20',
        celebration: 'border-t border-light-coral/20',
        calming: 'border-t border-muted-lavender/20',
        warm: 'border-t border-warm-neutral/40',
        milestone: 'border-t border-soft-pink/20',
        progress: 'border-t border-gentle-mint/20',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

/* @vue-ignore */
interface CardProps extends VariantProps<typeof cardVariants> {
  title?: string
  description?: string
}

defineProps<CardProps>()
</script>

<style scoped>
/* Enhanced card styling for pregnancy theme */
.card-hover-lift:hover {
  transform: translateY(-2px);
}

/* Gentle shadow transitions */
div[class*="shadow-"] {
  transition: box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out;
}

/* Milestone card special effects */
.milestone-shine {
  position: relative;
  overflow: hidden;
}

.milestone-shine::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  transition: transform 0.6s;
}

.milestone-shine:hover::before {
  transform: translateX(100%) translateY(100%) rotate(45deg);
}
</style>
