<template>
  <div :class="cn(badgeVariants({ variant }), props.class)" v-bind="$attrs">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
        pregnancy: 'border-transparent bg-soft-pink text-gray-800 hover:bg-soft-pink/80',
        milestone: 'border-transparent bg-gentle-mint text-gray-800 hover:bg-gentle-mint/80',
        health: 'border-transparent bg-muted-lavender text-gray-800 hover:bg-muted-lavender/80',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

interface Props {
  variant?: VariantProps<typeof badgeVariants>['variant']
  class?: string
}

const props = defineProps<Props>()
</script>