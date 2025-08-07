<template>
  <div ref="dropdownRef" class="relative inline-block text-left">
    <slot name="trigger" :toggle="toggle" :isOpen="isOpen" />
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div
          v-if="isOpen"
          ref="dropdownMenuRef"
          :class="cn(
            'fixed z-[99999] w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none',
            props.class
          )"
          :style="dropdownStyle"
          @click.stop
        >
          <div class="py-1">
            <slot :close="close" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { cn } from "./utils"

interface Props {
  class?: string
}

const props = defineProps<Props>()
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement>()
const dropdownMenuRef = ref<HTMLElement>()

const dropdownStyle = computed(() => {
  if (!isOpen.value || !dropdownRef.value) return {}
  
  const rect = dropdownRef.value.getBoundingClientRect()
  return {
    top: `${rect.bottom + 8}px`,
    right: `${window.innerWidth - rect.right}px`,
  }
})

const toggle = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    await nextTick()
    // Ensure positioning is updated
  }
}

const close = () => {
  isOpen.value = false
}

const handleClickOutside = (event: Event) => {
  const target = event.target as Node
  if (
    isOpen.value && 
    dropdownRef.value && 
    dropdownMenuRef.value &&
    !dropdownRef.value.contains(target) && 
    !dropdownMenuRef.value.contains(target)
  ) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
