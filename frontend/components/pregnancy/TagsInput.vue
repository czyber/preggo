<template>
  <div class="space-y-2">
    <!-- Tags display -->
    <div v-if="tags.length > 0" class="flex flex-wrap gap-2">
      <span
        v-for="(tag, index) in tags"
        :key="index"
        class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-soft-pink/10 border border-soft-pink/30 text-gray-700 group hover:bg-soft-pink/15 transition-colors duration-200"
      >
        <span class="mr-2">#</span>
        {{ tag }}
        <button
          @click="removeTag(index)"
          class="ml-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
          :aria-label="`Remove ${tag} tag`"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </span>
    </div>

    <!-- Input field -->
    <div class="relative">
      <input
        ref="tagInput"
        v-model="inputValue"
        type="text"
        placeholder="Add tags to organize your update (press Enter to add)"
        class="w-full p-3 border border-soft-pink/30 rounded-xl bg-white placeholder:text-gray-500 placeholder:italic focus:outline-none focus:ring-2 focus:ring-soft-pink/50 focus:border-soft-pink transition-all duration-200 font-secondary text-gray-800"
        @keydown="handleKeydown"
        @keyup.enter="addTag"
        @blur="addTagOnBlur"
      >
      
      <!-- Character limit indicator -->
      <div class="absolute right-3 top-1/2 transform -translate-y-1/2">
        <span class="text-xs text-gray-400">{{ inputValue.length }}/20</span>
      </div>
    </div>

    <!-- Popular tags suggestions -->
    <div v-if="showSuggestions && popularTags.length > 0" class="mt-3">
      <p class="text-xs font-primary font-medium text-gray-600 mb-2">Popular tags:</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="suggestion in filteredSuggestions"
          :key="suggestion"
          @click="addSuggestionTag(suggestion)"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 hover:bg-soft-pink/10 hover:border-soft-pink/30 border border-transparent text-gray-600 hover:text-gray-700 transition-all duration-200"
        >
          <span class="mr-1">#</span>
          {{ suggestion }}
        </button>
      </div>
    </div>

    <!-- Tags help text -->
    <div class="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
      <div class="flex items-start space-x-2">
        <svg class="w-4 h-4 text-soft-pink mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <p class="font-medium text-gray-600 mb-1">Tips for tags:</p>
          <ul class="space-y-1">
            <li>• Use tags to organize and find your updates later</li>
            <li>• Popular tags: #firstkick, #ultrasound, #cravings, #nursery</li>
            <li>• Keep tags short and descriptive</li>
            <li>• Press Enter or comma to add multiple tags</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props
interface Props {
  modelValue: string[]
  maxTags?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxTags: 10
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [tags: string[]]
}>()

// Refs
const tagInput = ref<HTMLInputElement>()

// State
const inputValue = ref('')
const tags = ref<string[]>([...props.modelValue])
const showSuggestions = ref(true)

// Popular/suggested tags based on pregnancy tracking
const popularTags = [
  'firstkick', 'ultrasound', 'cravings', 'nursery', 'babyshower',
  'appointment', 'milestone', 'symptoms', 'excited', 'nervous',
  'grateful', 'tired', 'emotional', 'preparation', 'announcement',
  'celebration', 'hospital', 'checkup', 'measurements', 'heartbeat',
  'movement', 'gender', 'name', 'clothes', 'shopping', 'vitamins',
  'exercise', 'sleep', 'mood', 'family', 'partner', 'photos'
]

// Computed
const filteredSuggestions = computed(() => {
  if (!inputValue.value) {
    return popularTags
      .filter(tag => !tags.value.includes(tag))
      .slice(0, 8)
  }
  
  return popularTags
    .filter(tag => 
      tag.toLowerCase().includes(inputValue.value.toLowerCase()) &&
      !tags.value.includes(tag)
    )
    .slice(0, 6)
})

// Methods
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' || event.key === ',' || event.key === ' ') {
    event.preventDefault()
    addTag()
  } else if (event.key === 'Backspace' && !inputValue.value && tags.value.length > 0) {
    // Remove last tag when backspacing on empty input
    removeTag(tags.value.length - 1)
  }
}

const addTag = () => {
  const value = inputValue.value.trim().toLowerCase().replace(/[^a-z0-9]/g, '')
  
  if (value && !tags.value.includes(value) && tags.value.length < props.maxTags && value.length <= 20) {
    tags.value.push(value)
    inputValue.value = ''
    updateModelValue()
    showSuggestions.value = true
  }
}

const addTagOnBlur = () => {
  // Add tag on blur only if there's meaningful content
  if (inputValue.value.trim().length > 2) {
    addTag()
  }
}

const addSuggestionTag = (suggestion: string) => {
  if (!tags.value.includes(suggestion) && tags.value.length < props.maxTags) {
    tags.value.push(suggestion)
    updateModelValue()
    showSuggestions.value = false
    
    // Focus back to input
    nextTick(() => {
      tagInput.value?.focus()
    })
  }
}

const removeTag = (index: number) => {
  tags.value.splice(index, 1)
  updateModelValue()
  showSuggestions.value = true
}

const updateModelValue = () => {
  emit('update:modelValue', [...tags.value])
}

// Watch for external changes
watch(() => props.modelValue, (newTags) => {
  tags.value = [...newTags]
}, { immediate: true })

// Focus management
onMounted(() => {
  // Show suggestions when input is focused
  tagInput.value?.addEventListener('focus', () => {
    showSuggestions.value = true
  })
})

// Hide suggestions when clicking outside
onMounted(() => {
  document.addEventListener('click', (event) => {
    if (!tagInput.value?.contains(event.target as Node)) {
      showSuggestions.value = false
    }
  })
})
</script>

<style scoped>
/* Tag animation on add/remove */
.inline-flex {
  animation: tagAppear 0.3s ease-out;
}

@keyframes tagAppear {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Input focus styling */
input:focus {
  transform: scale(1.01);
  box-shadow: 0 4px 20px rgba(248, 187, 208, 0.15);
}

/* Suggestion buttons animation */
button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

/* Tag hover effects */
.group:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(248, 187, 208, 0.2);
}

/* Character limit styling */
input:focus + div span {
  color: #6b7280;
}

/* Limit warning when approaching max */
.text-xs.text-gray-400 {
  transition: color 0.2s ease;
}

/* Style for when near character limit */
input[data-length="18"] + div span,
input[data-length="19"] + div span,
input[data-length="20"] + div span {
  color: #ef4444;
  font-weight: 600;
}
</style>