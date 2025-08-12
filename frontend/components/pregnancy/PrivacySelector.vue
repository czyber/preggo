<template>
  <div class="space-y-4">
    <label class="block text-sm font-primary font-medium text-gray-700">
      Who can see this update?
    </label>

    <!-- Simplified 4-tier selector -->
    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="option in privacyOptions"
        :key="option.value"
        :class="[
          'p-4 rounded-lg border-2 text-left transition-all duration-200',
          privacy.visibility === option.value
            ? 'border-gentle-mint bg-gentle-mint/10 shadow-sm'
            : 'border-gray-200 hover:border-gentle-mint/50 hover:bg-gentle-mint/5'
        ]"
        @click="selectVisibility(option.value)"
      >
        <div class="space-y-2">
          <div class="flex items-center space-x-3">
            <span class="text-2xl">{{ option.icon }}</span>
            <h3 class="font-medium text-gray-800">{{ option.label }}</h3>
          </div>
          <p class="text-sm text-gray-600">{{ option.description }}</p>
          <p class="text-xs text-gray-500">{{ option.count }} {{ option.count === 1 ? 'person' : 'people' }}</p>
        </div>
      </button>
    </div>

    <!-- Preview who will see this -->
    <div v-if="privacy.visibility !== 'PRIVATE'" class="bg-gray-50 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="font-medium text-gray-800 mb-2">Who will see this:</h4>
          <div class="flex -space-x-2">
            <div 
              v-for="(member, index) in getSelectedOption()?.members?.slice(0, 5) || []"
              :key="index"
              class="relative w-6 h-6 bg-gentle-mint/20 rounded-full flex items-center justify-center text-xs text-gray-700 ring-2 ring-white"
            >
              {{ member.charAt(0) }}
            </div>
            <div 
              v-if="(getSelectedOption()?.members?.length || 0) > 5"
              class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center ring-2 ring-white text-xs text-gray-600"
            >
              +{{ (getSelectedOption()?.members?.length || 0) - 5 }}
            </div>
          </div>
        </div>
        <div class="text-right">
          <div class="text-lg font-semibold text-gray-800">{{ getSelectedOption()?.count || 0 }}</div>
          <div class="text-sm text-gray-500">people</div>
        </div>
      </div>
    </div>

    <!-- Invite more people section -->
    <div v-if="privacy.visibility === 'ALL_FAMILY'" class="bg-gradient-to-r from-soft-pink/10 to-gentle-mint/10 rounded-lg p-4 border border-gentle-mint/20">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <h4 class="font-medium text-gray-800">Want to share with more family?</h4>
          <p class="text-sm text-gray-600">Invite family members to join your pregnancy journey</p>
        </div>
        <BaseButton
          variant="outline"
          size="sm"
          @click="$emit('openInviteModal')"
        >
          <UserPlus class="h-4 w-4 mr-2" />
          Invite Family
        </BaseButton>
      </div>
    </div>

    <!-- Old complex selector (keeping for reference but simplified) -->
    <div class="hidden">
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
</template>

<script setup lang="ts">
import { UserPlus } from 'lucide-vue-next'

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
  'openInviteModal': []
}>()

// Reactive privacy state
const privacy = ref({ ...props.modelValue })

// Simplified 4-tier privacy options
const privacyOptions = [
  {
    value: 'PRIVATE',
    icon: '🔒',
    label: 'Just me',
    description: 'Keep this private',
    count: 1,
    members: []
  },
  {
    value: 'PARTNER_ONLY',
    icon: '💕',
    label: 'Partner only',
    description: 'Just us two',
    count: 2,
    members: ['You', 'Partner']
  },
  {
    value: 'IMMEDIATE',
    icon: '👨‍👩‍👧‍👦',
    label: 'Inner circle',
    description: 'Close family (parents, siblings, partner)',
    count: 6,
    members: ['Mom', 'Dad', 'Sister Sarah', 'Brother Mike', 'Partner']
  },
  {
    value: 'ALL_FAMILY',
    icon: '🌟',
    label: 'Everyone',
    description: 'All family members and friends',
    count: 18,
    members: ['Mom', 'Dad', 'Grandma Pat', 'Sister Sarah', 'Aunt Lisa', 'Uncle Tom']
  }
]

// Methods
const selectVisibility = (visibility: string) => {
  privacy.value.visibility = visibility
  privacy.value.allowed_groups = []
  privacy.value.allowed_members = []
  updatePrivacy()
}

const getSelectedOption = () => {
  return privacyOptions.find(option => option.value === privacy.value.visibility)
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
