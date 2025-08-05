<template>
  <div :class="cn('w-full', props.class)">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { provide, computed } from 'vue'
import { cn } from '@/lib/utils'

interface Props {
  defaultValue?: string
  modelValue?: string
  class?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const currentValue = computed({
  get: () => props.modelValue ?? props.defaultValue ?? '',
  set: (value: string) => emit('update:modelValue', value)
})

provide('tabsValue', currentValue)
</script>