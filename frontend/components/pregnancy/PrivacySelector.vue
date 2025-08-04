<template>
  <div class="space-y-4">
    <label class="block text-sm font-primary font-medium text-gray-700">
      Who can see this update?
    </label>

    <!-- Privacy level selector -->
    <div class="space-y-2">
      <div
        v-for="option in privacyOptions"
        :key="option.value"
        :class="[
          'relative border rounded-lg p-4 cursor-pointer transition-all duration-200',
          privacy.visibility === option.value
            ? 'border-gentle-mint bg-gentle-mint/10 shadow-sm'
            : 'border-gray-200 hover:border-gentle-mint/50 hover:bg-gentle-mint/5'
        ]"
        @click="selectVisibility(option.value)"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3">
            <!-- Radio button -->
            <div class="flex-shrink-0 mt-1">
              <div
                :class="[
                  'w-4 h-4 rounded-full border-2 transition-all duration-200',
                  privacy.visibility === option.value
                    ? 'border-gentle-mint bg-gentle-mint'
                    : 'border-gray-300'
                ]"
              >
                <div
                  v-if="privacy.visibility === option.value"
                  class="w-full h-full rounded-full bg-white scale-50"
                ></div>
              </div>
            </div>

            <!-- Option details -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2">
                <span class="text-lg">{{ option.icon }}</span>
                <h4 class="font-primary font-medium text-gray-800">{{ option.label }}</h4>
              </div>
              <p class="text-sm text-gray-600 mt-1">{{ option.description }}</p>
              
              <!-- Show who's included -->
              <div v-if="option.members && option.members.length > 0" class="mt-2">
                <p class="text-xs text-gray-500 mb-1">Includes:</p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="member in option.members.slice(0, 3)"
                    :key="member"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gentle-mint/20 text-gray-700"
                  >
                    {{ member }}
                  </span>
                  <span
                    v-if="option.members.length > 3"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600"
                  >
                    +{{ option.members.length - 3 }} more
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Preview count -->
          <div class="flex-shrink-0">
            <span class="text-xs text-gray-500">{{ option.count }} {{ option.count === 1 ? 'person' : 'people' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced privacy settings -->
    <div v-if="privacy.visibility !== 'PRIVATE'" class="mt-6 p-4 bg-gray-50 rounded-lg">
      <h5 class="font-primary font-medium text-gray-800 mb-3">Additional Settings</h5>
      
      <div class="space-y-3">
        <!-- Allow comments -->
        <label class="flex items-center justify-between cursor-pointer">
          <div class="flex items-center space-x-3">
            <span class="text-sm">💬</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Allow comments</p>
              <p class="text-xs text-gray-500">Family can comment on your update</p>
            </div>
          </div>
          <div class="relative">
            <input
              v-model="privacy.allow_comments"
              type="checkbox"
              class="sr-only"
              @change="updatePrivacy"
            >
            <div
              :class="[
                'w-11 h-6 rounded-full transition-colors duration-200',
                privacy.allow_comments ? 'bg-gentle-mint' : 'bg-gray-300'
              ]"
            >
              <div
                :class="[
                  'w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200',
                  privacy.allow_comments ? 'translate-x-5' : 'translate-x-0'
                ]"
              ></div>
            </div>
          </div>
        </label>

        <!-- Allow reactions -->
        <label class="flex items-center justify-between cursor-pointer">
          <div class="flex items-center space-x-3">
            <span class="text-sm">❤️</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Allow reactions</p>
              <p class="text-xs text-gray-500">Family can react with emojis</p>
            </div>
          </div>
          <div class="relative">
            <input
              v-model="privacy.allow_reactions"
              type="checkbox"
              class="sr-only"
              @change="updatePrivacy"
            >
            <div
              :class="[
                'w-11 h-6 rounded-full transition-colors duration-200',
                privacy.allow_reactions ? 'bg-gentle-mint' : 'bg-gray-300'
              ]"
            >
              <div
                :class="[
                  'w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200',
                  privacy.allow_reactions ? 'translate-x-5' : 'translate-x-0'
                ]"
              ></div>
            </div>
          </div>
        </label>

        <!-- Allow downloads -->
        <label class="flex items-center justify-between cursor-pointer">
          <div class="flex items-center space-x-3">
            <span class="text-sm">📥</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Allow photo downloads</p>
              <p class="text-xs text-gray-500">Family can save your photos</p>
            </div>
          </div>
          <div class="relative">
            <input
              v-model="privacy.allow_downloads"
              type="checkbox"
              class="sr-only"
              @change="updatePrivacy"
            >
            <div
              :class="[
                'w-11 h-6 rounded-full transition-colors duration-200',
                privacy.allow_downloads ? 'bg-gentle-mint' : 'bg-gray-300'
              ]"
            >
              <div
                :class="[
                  'w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200',
                  privacy.allow_downloads ? 'translate-x-5' : 'translate-x-0'
                ]"
              ></div>
            </div>
          </div>
        </label>
      </div>
    </div>

    <!-- Custom privacy hint -->
    <div v-if="privacy.visibility === 'CUSTOM'" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="flex items-start space-x-2">
        <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <p class="text-sm font-medium text-blue-800">Custom Privacy</p>
          <p class="text-xs text-blue-600 mt-1">
            You can select specific family members to share with in the full create view.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props
interface Props {
  modelValue: {
    visibility: string
    allowed_groups: string[]
    allowed_members: string[]
    allow_comments: boolean
    allow_reactions: boolean
    allow_downloads: boolean
    hide_from_timeline: boolean
  }
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [privacy: Props['modelValue']]
}>()

// Reactive privacy state
const privacy = ref({ ...props.modelValue })

// Privacy options with mock family data
const privacyOptions = [
  {
    value: 'PRIVATE',
    icon: '🔒',
    label: 'Just me',
    description: 'Only you can see this update',
    count: 1,
    members: []
  },
  {
    value: 'PARTNER_ONLY',
    icon: '💕',
    label: 'Partner only',
    description: 'Share with your partner/spouse',
    count: 2,
    members: ['You', 'Partner']
  },
  {
    value: 'IMMEDIATE',
    icon: '👨‍👩‍👧‍👦',
    label: 'Immediate family',
    description: 'Parents, siblings, and partners',
    count: 6,
    members: ['Mom', 'Dad', 'Sister Sarah', 'Brother Mike', 'Partner']
  },
  {
    value: 'EXTENDED',
    icon: '👪',
    label: 'Extended family',
    description: 'Includes grandparents, aunts, uncles',
    count: 12,
    members: ['Grandma Pat', 'Grandpa Joe', 'Aunt Lisa', 'Uncle Tom', 'Mom', 'Dad']
  },
  {
    value: 'FRIENDS',
    icon: '👥',
    label: 'Close friends',
    description: 'Your selected friend circle',
    count: 8,
    members: ['Jessica', 'Amanda', 'Katie', 'Emma', 'Melissa']
  },
  {
    value: 'ALL_FAMILY',
    icon: '🌟',
    label: 'All family',
    description: 'Everyone in your family network',
    count: 18,
    members: ['Mom', 'Dad', 'Grandma Pat', 'Sister Sarah', 'Aunt Lisa', 'Uncle Tom']
  },
  {
    value: 'CUSTOM',
    icon: '⚙️',
    label: 'Custom selection',
    description: 'Choose specific people to share with',
    count: 0,
    members: []
  }
]

// Methods
const selectVisibility = (visibility: string) => {
  privacy.value.visibility = visibility
  
  // Reset custom settings when changing visibility
  if (visibility !== 'CUSTOM') {
    privacy.value.allowed_groups = []
    privacy.value.allowed_members = []
  }
  
  updatePrivacy()
}

const updatePrivacy = () => {
  emit('update:modelValue', { ...privacy.value })
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  privacy.value = { ...newValue }
}, { deep: true })
</script>

<style scoped>
/* Toggle switch styling */
input[type="checkbox"]:focus + div {
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.1);
}

/* Smooth hover transitions */
.cursor-pointer:hover {
  transform: translateY(-1px);
}

/* Radio button animation */
.w-4.h-4.rounded-full div {
  transition: all 0.2s ease-in-out;
}

/* Custom shadow for selected option */
.shadow-sm {
  box-shadow: 0 1px 3px 0 rgba(74, 222, 128, 0.1), 
              0 1px 2px 0 rgba(74, 222, 128, 0.06);
}
</style>