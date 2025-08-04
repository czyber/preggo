<template>
  <div class="relative">
    <!-- Selected mood display -->
    <button
      @click="toggleDropdown"
      :class="[
        'w-full p-3 border rounded-xl bg-white text-left transition-all duration-200',
        isOpen 
          ? 'border-light-coral ring-2 ring-light-coral/20' 
          : 'border-light-coral/30 hover:border-light-coral/50',
        'focus:outline-none focus:ring-2 focus:ring-light-coral/20 focus:border-light-coral'
      ]"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <span class="text-2xl">{{ selectedMood ? getMoodEmoji(selectedMood) : '😊' }}</span>
          <div>
            <p class="font-primary font-medium text-gray-800">
              {{ selectedMood ? getMoodLabel(selectedMood) : 'How are you feeling?' }}
            </p>
            <p v-if="selectedMood" class="text-sm text-gray-600">
              {{ getMoodDescription(selectedMood) }}
            </p>
          </div>
        </div>
        <svg 
          :class="['w-5 h-5 text-gray-400 transition-transform duration-200', isOpen && 'rotate-180']"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </button>

    <!-- Dropdown menu -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 w-full mt-2 bg-white border border-light-coral/30 rounded-xl shadow-lg overflow-hidden"
      >
        <!-- Mood grid -->
        <div class="p-4">
          <p class="text-sm font-primary font-medium text-gray-700 mb-3">
            Select how you're feeling today
          </p>
          
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="mood in moods"
              :key="mood.value"
              @click="selectMood(mood.value)"
              :class="[
                'p-3 rounded-lg text-left transition-all duration-200 border',
                selectedMood === mood.value
                  ? 'bg-light-coral/10 border-light-coral text-gray-800'
                  : 'hover:bg-light-coral/5 border-transparent hover:border-light-coral/30 text-gray-700'
              ]"
            >
              <div class="flex items-center space-x-3">
                <span class="text-xl">{{ mood.emoji }}</span>
                <div class="min-w-0 flex-1">
                  <p class="font-primary font-medium text-sm">{{ mood.label }}</p>
                  <p class="text-xs text-gray-600 truncate">{{ mood.description }}</p>
                </div>
              </div>
            </button>
          </div>

          <!-- Clear selection -->
          <div class="mt-3 pt-3 border-t border-gray-200">
            <button
              @click="clearMood"
              class="w-full p-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors duration-200"
            >
              Clear selection
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Backdrop -->
    <div
      v-if="isOpen"
      @click="closeDropdown"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup lang="ts">
// Props
interface Props {
  modelValue?: string | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

// State
const isOpen = ref(false)
const selectedMood = ref<string | null>(props.modelValue || null)

// Mood options based on the backend enum values
const moods = [
  {
    value: 'EXCITED',
    emoji: '🤗',
    label: 'Excited',
    description: 'Feeling thrilled and energetic'
  },
  {
    value: 'HAPPY',
    emoji: '😊',
    label: 'Happy',
    description: 'Content and joyful'
  },
  {
    value: 'GRATEFUL',
    emoji: '🙏',
    label: 'Grateful',
    description: 'Thankful and appreciative'
  },
  {
    value: 'PEACEFUL',
    emoji: '😌',
    label: 'Peaceful',
    description: 'Calm and serene'
  },
  {
    value: 'NERVOUS',
    emoji: '😰',
    label: 'Nervous',
    description: 'A bit anxious or worried'
  },
  {
    value: 'EMOTIONAL',
    emoji: '🥺',
    label: 'Emotional',
    description: 'Feeling sensitive or tearful'
  },
  {
    value: 'TIRED',
    emoji: '😴',
    label: 'Tired',
    description: 'Exhausted and need rest'
  },
  {
    value: 'UNCOMFORTABLE',
    emoji: '😣',
    label: 'Uncomfortable',
    description: 'Physical discomfort or pain'
  }
]

// Methods
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const selectMood = (mood: string) => {
  selectedMood.value = mood
  emit('update:modelValue', mood)
  closeDropdown()
}

const clearMood = () => {
  selectedMood.value = null
  emit('update:modelValue', null)
  closeDropdown()
}

const getMoodEmoji = (mood: string) => {
  const moodData = moods.find(m => m.value === mood)
  return moodData?.emoji || '😊'
}

const getMoodLabel = (mood: string) => {
  const moodData = moods.find(m => m.value === mood)
  return moodData?.label || mood
}

const getMoodDescription = (mood: string) => {
  const moodData = moods.find(m => m.value === mood)
  return moodData?.description || ''
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  selectedMood.value = newValue
})

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen.value) {
      closeDropdown()
    }
  })
})
</script>

<style scoped>
/* Custom styling for smooth animations */
.transition {
  transition-property: opacity, transform;
}

/* Ensure dropdown appears above other elements */
.z-50 {
  z-index: 50;
}

.z-40 {
  z-index: 40;
}

/* Subtle shadow for the dropdown */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
              0 4px 6px -2px rgba(0, 0, 0, 0.05),
              0 0 0 1px rgba(244, 114, 182, 0.05);
}

/* Hover effects */
button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

/* Focus styles for accessibility */
button:focus-visible {
  outline: 2px solid rgba(244, 114, 182, 0.5);
  outline-offset: 2px;
}
</style>