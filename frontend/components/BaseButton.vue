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
import { cn } from '~/utils/cn'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        // Pregnancy-themed variants
        default: 'bg-soft-pink hover:bg-soft-pink/80 text-gray-800 shadow-sm hover:shadow-md',
        supportive: 'bg-gentle-mint hover:bg-gentle-mint/80 text-gray-800 shadow-sm hover:shadow-md',
        celebration: 'bg-light-coral hover:bg-light-coral/80 text-gray-800 shadow-sm hover:shadow-md',
        calming: 'bg-muted-lavender hover:bg-muted-lavender/80 text-gray-800 shadow-sm hover:shadow-md',
        // Standard variants adapted for pregnancy theme
        secondary: 'bg-warm-neutral hover:bg-warm-neutral/80 text-gray-800 border border-warm-neutral/50 shadow-sm hover:shadow-md',
        ghost: 'hover:bg-soft-pink/10 hover:text-gray-800 text-gray-600',
        link: 'text-soft-pink underline-offset-4 hover:underline',
        outline: 'border border-soft-pink bg-background hover:bg-soft-pink/10 hover:text-gray-800 text-soft-pink',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
      },
      size: {
        default: 'h-12 px-6 py-3',
        sm: 'h-10 rounded-lg px-4 text-xs',
        lg: 'h-14 rounded-xl px-8 text-base',
        icon: 'h-12 w-12',
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
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* Gentle haptic-like animation on press */
button:active {
  transform: translateY(1px);
  transition: transform 0.1s ease-in-out;
}

/* Soft glow effect on focus for accessibility */
button:focus-visible {
  box-shadow: 0 0 0 3px rgba(248, 187, 208, 0.3);
}
</style>