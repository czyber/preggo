<template>
  <div class="circle-filters flex justify-center mb-6">
    <div class="flex space-x-1 bg-gray-100 rounded-lg p-1">
      <button
        v-for="filter in circleFilters"
        :key="filter.value"
        @click="selectFilter(filter.value)"
        :class="[
          'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center space-x-2',
          modelValue === filter.value
            ? 'bg-white shadow-sm text-gray-900'
            : 'text-gray-600 hover:text-gray-900'
        ]"
      >
        <span>{{ filter.icon }}</span>
        <span>{{ filter.name }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 'all'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Circle filter options
const circleFilters = [
  {
    value: 'all',
    name: 'All Updates',
    icon: '📰'
  },
  {
    value: 'PARTNER_ONLY',
    name: 'Just Us',
    icon: '💕'
  },
  {
    value: 'IMMEDIATE',
    name: 'Inner Circle',
    icon: '👨‍👩‍👧‍👦'
  },
  {
    value: 'ALL_FAMILY',
    name: 'Everyone',
    icon: '🌟'
  }
]

const selectFilter = (value: string) => {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.circle-filters button:hover {
  transform: translateY(-1px);
}

.circle-filters button:active {
  transform: translateY(0px);
}
</style>