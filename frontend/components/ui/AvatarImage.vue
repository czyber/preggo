<template>
  <img
    :class="cn('aspect-square h-full w-full', props.class)"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils'

interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>