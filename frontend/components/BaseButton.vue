<template>
  <button
    :class="cn(buttonVariants({ variant, size, class: $attrs.class }))"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '~/components/ui/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        // Pregnancy-themed variants with softer tones
        default: 'bg-soft-pink/70 hover:bg-soft-pink/80 text-gray-700 shadow-sm hover:shadow',
        supportive: 'bg-gentle-mint/60 hover:bg-gentle-mint/70 text-gray-700 shadow-sm hover:shadow',
        celebration: 'bg-light-coral/60 hover:bg-light-coral/70 text-gray-700 shadow-sm hover:shadow',
        calming: 'bg-muted-lavender/60 hover:bg-muted-lavender/70 text-gray-700 shadow-sm hover:shadow',
        // Standard variants adapted for pregnancy theme
        secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-200 shadow-sm hover:shadow',
        ghost: 'hover:bg-gray-100 hover:text-gray-700 text-gray-600',
        link: 'text-soft-pink/80 underline-offset-4 hover:underline',
        outline: 'border border-gray-200 bg-transparent hover:bg-gray-50 text-gray-700',
        destructive: 'bg-red-500/80 text-white hover:bg-red-500/90',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-11 rounded-lg px-6 text-base',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

/* @vue-ignore */
interface ButtonProps extends VariantProps<typeof buttonVariants> {
  disabled?: boolean
}

defineProps<ButtonProps>()
</script>

<style scoped>
/* Additional pregnancy-themed button styles */
button {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 500;
  letter-spacing: -0.01em;
}

/* Gentle haptic-like animation on press */
button:active {
  transform: scale(0.98);
  transition: transform 0.1s ease-in-out;
}

/* Soft glow effect on focus for accessibility */
button:focus-visible {
  box-shadow: 0 0 0 2px rgba(248, 187, 208, 0.2);
}
</style>
