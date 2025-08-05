<template>
  <div
    :class="cn(
      'flex h-full w-full items-center justify-center rounded-full bg-muted',
      props.class
    )"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>