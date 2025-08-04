<template>
  <div
    :class="cn(getAvatarClasses(size), 'select-none')"
    :style="{ backgroundColor: avatarColor }"
    :title="displayName"
  >
    {{ initials }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '~/utils/cn'
import { getUserAvatarColor, getUserInitials, getUserDisplayName, getAvatarClasses } from '~/utils/avatar'

interface User {
  id?: string
  email?: string
  first_name?: string
  last_name?: string
  display_name?: string
}

interface Props {
  user?: User
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const avatarColor = computed(() => getUserAvatarColor(props.user?.id))
const initials = computed(() => getUserInitials(props.user))
const displayName = computed(() => getUserDisplayName(props.user))
</script>

<style scoped>
/* Ensure consistent text rendering */
div {
  user-select: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>