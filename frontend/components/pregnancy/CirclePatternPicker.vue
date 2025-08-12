<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <label class="font-medium text-gray-800">Who should see this?</label>
      <button 
        v-if="selectedPattern"
        @click="showAdvanced = !showAdvanced"
        class="text-sm text-gray-500 hover:text-gray-700"
      >
        {{ showAdvanced ? 'Use Quick Select' : 'Advanced Options' }}
      </button>
    </div>

    <!-- AI Suggestions -->
    <div v-if="suggestions.length > 0" class="space-y-2">
      <div class="flex items-center space-x-2 text-sm">
        <svg class="h-4 w-4 text-gentle-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3l14 14m0 0v-5m0 5h-5M6 3h5.5M6 21V9"/>
        </svg>
        <span class="text-gray-600">Suggested for you:</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="suggestion in suggestions"
          :key="suggestion.pattern.id"
          @click="selectPattern(suggestion.pattern)"
          class="group relative bg-gradient-to-r from-gentle-mint/10 to-soft-pink/10 
                 hover:from-gentle-mint/20 hover:to-soft-pink/20 
                 rounded-full px-4 py-2 border border-gentle-mint/20 
                 transition-all duration-200"
        >
          <div class="flex items-center space-x-2">
            <span class="text-lg">{{ suggestion.pattern.icon }}</span>
            <span class="font-medium text-gray-700">{{ suggestion.pattern.name }}</span>
            <div class="flex items-center space-x-1">
              <svg class="h-3 w-3 text-gentle-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              <span class="text-xs text-gentle-mint font-medium">{{ suggestion.confidence }}%</span>
            </div>
          </div>
          
          <!-- Tooltip -->
          <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 
                      bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap
                      opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10">
            {{ suggestion.reason }}
            <div class="absolute top-full left-1/2 transform -translate-x-1/2 
                        border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </button>
      </div>
    </div>

    <!-- Circle Pattern Grid -->
    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <button
        v-for="pattern in availablePatterns"
        :key="pattern.id"
        @click="selectPattern(pattern)"
        :class="[
          'group relative p-4 rounded-xl border-2 transition-all duration-200',
          selectedPattern?.id === pattern.id
            ? 'border-gentle-mint bg-gentle-mint/10 shadow-lg'
            : 'border-gray-200 hover:border-gentle-mint/50 hover:bg-gentle-mint/5'
        ]"
      >
        <div class="text-center space-y-2">
          <div class="text-3xl">{{ pattern.icon }}</div>
          <div class="font-medium text-gray-800">{{ pattern.name }}</div>
          <div class="text-xs text-gray-500">{{ pattern.description }}</div>
          <div class="flex items-center justify-center space-x-1 text-xs text-gray-400">
            <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            <span>{{ getMemberCount(pattern) }}</span>
          </div>
        </div>

        <!-- Selected Indicator -->
        <div 
          v-if="selectedPattern?.id === pattern.id"
          class="absolute top-2 right-2 w-6 h-6 bg-gentle-mint rounded-full 
                 flex items-center justify-center"
        >
          <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
        </div>

        <!-- Usage Frequency Indicator -->
        <div 
          v-if="pattern.usage_frequency && pattern.usage_frequency > 0"
          class="absolute top-2 left-2 bg-soft-pink/80 text-white text-xs 
                 rounded-full w-5 h-5 flex items-center justify-center"
        >
          {{ pattern.usage_frequency }}
        </div>
      </button>
    </div>

    <!-- Selected Pattern Preview -->
    <div v-if="selectedPattern" class="bg-gray-50 rounded-lg p-4">
      <div class="flex items-start justify-between">
        <div class="space-y-2">
          <div class="flex items-center space-x-3">
            <span class="text-2xl">{{ selectedPattern.icon }}</span>
            <div>
              <h4 class="font-medium text-gray-800">{{ selectedPattern.name }}</h4>
              <p class="text-sm text-gray-600">{{ selectedPattern.description }}</p>
            </div>
          </div>
          
          <!-- Member Preview -->
          <div class="flex -space-x-2 mt-3">
            <div 
              v-for="(member, index) in mockMembers.slice(0, 5)"
              :key="member.id"
              class="relative z-10"
              :style="{ zIndex: 10 - index }"
            >
              <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center ring-2 ring-white text-xs font-medium text-gray-600">
                {{ member.initials }}
              </div>
            </div>
            <div 
              v-if="getMemberCount(selectedPattern) > 5"
              class="relative z-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center ring-2 ring-white"
            >
              <span class="text-xs text-gray-600 font-medium">
                +{{ getMemberCount(selectedPattern) - 5 }}
              </span>
            </div>
          </div>
        </div>

        <div class="text-right space-y-1">
          <div class="text-sm font-medium text-gray-800">
            {{ getMemberCount(selectedPattern) }} people
          </div>
          <div class="text-xs text-gray-500">
            will see this post
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Options -->
    <div v-if="showAdvanced" class="border-t border-gray-200 pt-4">
      <PrivacySelector v-model="advancedPrivacy" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import PrivacySelector from './PrivacySelector.vue'
import { useInvites, type CirclePattern } from '@/composables/useInvites'

interface Props {
  modelValue?: CirclePattern | null
  postContent?: string
  postType?: string
  suggestions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  suggestions: true
})

const emit = defineEmits<{
  'update:modelValue': [pattern: CirclePattern | null]
}>()

const { 
  CIRCLE_PATTERNS,
  suggestCirclesForPost,
  getPatternMemberCount 
} = useInvites()

// State
const selectedPattern = ref<CirclePattern | null>(props.modelValue || null)
const showAdvanced = ref(false)
const advancedPrivacy = ref({
  visibility: 'IMMEDIATE',
  allowed_groups: [] as string[],
  allowed_members: [] as string[],
  allow_comments: true,
  allow_reactions: true,
  allow_downloads: false,
  hide_from_timeline: false
})

// Mock member data for preview
const mockMembers = [
  { id: '1', initials: 'MP', name: 'Mom Partner' },
  { id: '2', initials: 'DP', name: 'Dad Partner' },
  { id: '3', initials: 'SS', name: 'Sister Sarah' },
  { id: '4', initials: 'BM', name: 'Brother Mike' },
  { id: '5', initials: 'GP', name: 'Grandma Pat' },
  { id: '6', initials: 'GJ', name: 'Grandpa Joe' }
]

// Computed
const availablePatterns = computed(() => CIRCLE_PATTERNS)

const suggestions = computed(() => {
  if (!props.suggestions || !props.postContent || !props.postType) {
    return []
  }
  return suggestCirclesForPost(props.postContent, props.postType)
})

// Methods
const selectPattern = (pattern: CirclePattern) => {
  selectedPattern.value = pattern
  emit('update:modelValue', pattern)
}

const getMemberCount = (pattern: CirclePattern): number => {
  return getPatternMemberCount(pattern)
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  selectedPattern.value = newValue
})

// Auto-select first suggestion if available
onMounted(() => {
  if (!selectedPattern.value && suggestions.value.length > 0) {
    selectPattern(suggestions.value[0].pattern)
  }
})
</script>

<style scoped>
/* Enhance hover effects */
button:hover {
  transform: translateY(-1px);
}

/* Smooth transitions */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Custom shadow for selected pattern */
.shadow-lg {
  box-shadow: 0 10px 25px 0 rgba(74, 222, 128, 0.1), 
              0 4px 6px 0 rgba(74, 222, 128, 0.06);
}

/* Tooltip positioning */
.group:hover .opacity-0 {
  opacity: 1;
}

/* Z-index management for avatars */
.relative.z-10 {
  z-index: 10;
}
</style>