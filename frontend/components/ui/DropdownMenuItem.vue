<template>
  <button
    :class="cn(
      'group flex w-full items-center rounded-md px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900',
      props.class
    )"
    @click="handleClick"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { cn } from "./utils"

interface Props {
  class?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  click: [event: Event]
}>()

const handleClick = (event: Event) => {
  emit('click', event)
}
</script>
