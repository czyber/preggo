<template>
  <div
    v-if="isActive"
    :class="cn(
      'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      props.class
    )"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { inject, computed, type Ref } from 'vue'
import { cn } from "./utils"

interface Props {
  value: string
  class?: string
}

const props = defineProps<Props>()

const tabsValue = inject<Ref<string>>('tabsValue')
const isActive = computed(() => tabsValue?.value === props.value)
</script>
