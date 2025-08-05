<template>
  <div class="relative inline-block">
    <div
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
      @focus="showTooltip = true"
      @blur="showTooltip = false"
    >
      <slot />
    </div>
    <Transition
      enter-active-class="transition-opacity duration-300"
      leave-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showTooltip"
        :class="cn(
          'absolute z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95',
          'bottom-full left-1/2 -translate-x-1/2 -translate-y-2',
          props.class
        )"
      >
        <slot name="content">
          {{ content }}
        </slot>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { cn } from '@/lib/utils'

interface Props {
  content?: string
  class?: string
}

const props = defineProps<Props>()
const showTooltip = ref(false)
</script>