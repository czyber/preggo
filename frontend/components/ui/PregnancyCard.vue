<template>
  <Card :class="cn('bg-gradient-to-br from-soft-pink/5 to-gentle-mint/5 border-soft-pink/20 hover:border-soft-pink/40 transition-colors duration-200', props.class)">
    <CardHeader>
      <div class="flex items-center gap-3">
        <div v-if="icon" class="p-2 rounded-full bg-soft-pink/20">
          <component :is="icon" class="w-5 h-5 text-soft-pink" />
        </div>
        <div>
          <CardTitle :class="cn('text-lg text-gray-800', titleClass)">{{ title }}</CardTitle>
          <CardDescription v-if="description" :class="cn('text-gray-600', descriptionClass)">{{ description }}</CardDescription>
        </div>
      </div>
    </CardHeader>
    <CardContent>
      <slot />
    </CardContent>
    <CardFooter v-if="$slots.footer">
      <slot name="footer" />
    </CardFooter>
  </Card>
</template>

<script setup lang="ts">
import { cn } from "./utils"
import Card from './Card.vue'
import CardHeader from './CardHeader.vue'
import CardTitle from './CardTitle.vue'
import CardDescription from './CardDescription.vue'
import CardContent from './CardContent.vue'
import CardFooter from './CardFooter.vue'

interface Props {
  title: string
  description?: string
  icon?: any
  class?: string
  titleClass?: string
  descriptionClass?: string
}

const props = defineProps<Props>()
</script>
