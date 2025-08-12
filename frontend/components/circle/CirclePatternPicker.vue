<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-primary font-medium text-gray-800">
        Who should see this?
      </h3>
      <button
        v-if="selectedPattern"
        @click="showAdvanced = !showAdvanced"
        class="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200 flex items-center space-x-1"
      >
        <svg
          class="w-4 h-4"
          :class="{ 'rotate-180': showAdvanced }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
        <span>{{ showAdvanced ? 'Quick Select' : 'Advanced Options' }}</span>
      </button>
    </div>

    <!-- AI Suggestions -->
    <div v-if="suggestions.length > 0 && !showAdvanced" class="space-y-3">
      <div class="flex items-center space-x-2">
        <div class="flex items-center justify-center w-5 h-5 rounded-full bg-gradient-to-r from-gentle-mint to-soft-pink">
          <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <span class="text-sm font-medium text-gray-600">Suggested for you</span>
      </div>
      
      <div class="flex flex-wrap gap-2">
        <PatternSuggestion
          v-for="suggestion in suggestions"
          :key="suggestion.pattern.id"
          :suggestion="suggestion"
          :selected="selectedPattern?.id === suggestion.pattern.id"
          @select="selectPattern(suggestion.pattern)"
        />
      </div>
    </div>

    <!-- Circle Pattern Grid -->
    <div v-if="!showAdvanced" class="space-y-4">
      <div class="text-sm text-gray-600">
        Or choose from your circles:
      </div>
      
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <PatternCard
          v-for="pattern in availablePatterns"
          :key="pattern.id"
          :pattern="pattern"
          :selected="selectedPattern?.id === pattern.id"
          :member-count="getMemberCount(pattern)"
          @select="selectPattern(pattern)"
        />
      </div>
    </div>

    <!-- Selected Pattern Preview -->
    <div v-if="selectedPattern && !showAdvanced" class="bg-gradient-to-br from-gentle-mint/5 to-soft-pink/5 rounded-xl p-4 border border-gentle-mint/20">
      <PatternPreview
        :pattern="selectedPattern"
        :members="getPatternMembers(selectedPattern)"
        :member-count="getMemberCount(selectedPattern)"
      />
    </div>

    <!-- Advanced Options (Fallback to existing PrivacySelector) -->
    <div v-if="showAdvanced" class="border-t border-gray-200 pt-6">
      <div class="mb-4">
        <h4 class="font-medium text-gray-800 mb-2">Advanced Privacy Settings</h4>
        <p class="text-sm text-gray-600">
          Choose specific privacy levels and customize who can interact with your post.
        </p>
      </div>
      <PrivacySelector v-model="advancedPrivacy" />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 border-2 border-gentle-mint/30 border-t-gentle-mint rounded-full animate-spin"></div>
        <span class="text-sm text-gray-600">Loading your circles...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
      <div class="flex items-start space-x-2">
        <svg class="w-5 h-5 text-red-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <p class="text-sm font-medium text-red-800">Unable to load circles</p>
          <p class="text-xs text-red-600 mt-1">{{ error }}</p>
          <button
            @click="retryLoadCircles"
            class="text-xs text-red-600 hover:text-red-700 underline mt-2"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import type { CirclePattern, CircleSuggestion, FamilyMember, PostType } from '~/types/api'
import PatternCard from './PatternCard.vue'
import PatternPreview from './PatternPreview.vue'
import PatternSuggestion from './PatternSuggestion.vue'
import PrivacySelector from '~/components/pregnancy/PrivacySelector.vue'

// Props
interface Props {
  modelValue: CirclePattern | null
  postContent?: {
    text: string
    type: PostType
  }
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [pattern: CirclePattern | null]
  'change': [pattern: CirclePattern | null]
}>()

// Composables
const api = useApi()
const auth = useAuth()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const showAdvanced = ref(false)
const selectedPattern = ref<CirclePattern | null>(props.modelValue)
const availablePatterns = ref<CirclePattern[]>([])
const suggestions = ref<CircleSuggestion[]>([])
const familyMembers = ref<FamilyMember[]>([])

// Advanced privacy fallback
const advancedPrivacy = ref({
  visibility: 'immediate' as string,
  allowed_groups: [] as string[],
  allowed_members: [] as string[],
  allow_comments: true,
  allow_reactions: true,
  allow_downloads: false,
  hide_from_timeline: false
})

// Default circle patterns based on design document
const defaultPatterns: CirclePattern[] = [
  {
    id: 'just-us',
    name: 'Just Us',
    icon: '💕',
    description: 'You and your partner',
    groups: [],
    visibility: 'partner_only',
    suggested_for: ['symptom_share', 'preparation'],
    usage_frequency: 0
  },
  {
    id: 'close-family',
    name: 'Close Family',
    icon: '👨‍👩‍👧‍👦',
    description: 'Parents, siblings, and partner',
    groups: ['immediate_family'],
    visibility: 'immediate',
    suggested_for: ['ultrasound', 'milestone'],
    usage_frequency: 0
  },
  {
    id: 'everyone',
    name: 'Everyone',
    icon: '🌟',
    description: 'All your family and friends',
    groups: ['immediate_family', 'extended_family', 'friends'],
    visibility: 'all_family',
    suggested_for: ['announcement', 'celebration'],
    usage_frequency: 0
  },
  {
    id: 'grandparents',
    name: 'Grandparents Circle',
    icon: '👴👵',
    description: 'Extended family including grandparents',
    groups: ['immediate_family', 'extended_family'],
    visibility: 'extended',
    suggested_for: ['weekly_update', 'belly_photo'],
    usage_frequency: 0
  },
  {
    id: 'friends-support',
    name: 'Friend Support',
    icon: '🤗',
    description: 'Close friends and support network',
    groups: ['friends', 'support_circle'],
    visibility: 'friends',
    suggested_for: ['question', 'memory'],
    usage_frequency: 0
  }
]

// Computed
const canShowSuggestions = computed(() => {
  return props.postContent && (props.postContent.text.length > 10 || props.postContent.type)
})

// Methods
const selectPattern = (pattern: CirclePattern) => {
  selectedPattern.value = pattern
  showAdvanced.value = false
  emit('update:modelValue', pattern)
  emit('change', pattern)
}

const getMemberCount = (pattern: CirclePattern): number => {
  // Mock member counts for demo - in real app, calculate from actual family members
  const mockCounts: Record<string, number> = {
    'just-us': 2,
    'close-family': 6,
    'everyone': 18,
    'grandparents': 12,
    'friends-support': 8
  }
  return mockCounts[pattern.id] || 0
}

const getPatternMembers = (pattern: CirclePattern): FamilyMember[] => {
  // Mock members for demo - in real app, filter actual family members by pattern groups
  const mockMembers: Record<string, Partial<FamilyMember>[]> = {
    'just-us': [
      { id: '1', user: { first_name: 'You', profile_image: null } },
      { id: '2', user: { first_name: 'Partner', profile_image: null } }
    ],
    'close-family': [
      { id: '1', user: { first_name: 'Mom', profile_image: null } },
      { id: '2', user: { first_name: 'Dad', profile_image: null } },
      { id: '3', user: { first_name: 'Sister', profile_image: null } },
      { id: '4', user: { first_name: 'Partner', profile_image: null } }
    ],
    'everyone': [
      { id: '1', user: { first_name: 'Mom', profile_image: null } },
      { id: '2', user: { first_name: 'Dad', profile_image: null } },
      { id: '3', user: { first_name: 'Grandma', profile_image: null } },
      { id: '4', user: { first_name: 'Jessica', profile_image: null } },
      { id: '5', user: { first_name: 'Amanda', profile_image: null } }
    ]
  }
  return (mockMembers[pattern.id] || []) as FamilyMember[]
}

const generateSuggestions = async () => {
  if (!canShowSuggestions.value || !props.postContent) return

  try {
    const newSuggestions: CircleSuggestion[] = []

    // Content-based suggestions
    const text = props.postContent.text.toLowerCase()
    const postType = props.postContent.type

    // Announcement detection
    if (text.includes('first') || text.includes('exciting') || text.includes('announcement') || postType === 'announcement') {
      const pattern = availablePatterns.value.find(p => p.id === 'everyone')
      if (pattern) {
        newSuggestions.push({
          pattern,
          confidence: 90,
          reason: "Exciting announcements are usually shared with everyone",
          learned_from: 'content_analysis'
        })
      }
    }

    // Intimate/personal content detection
    if (text.includes('feeling') || text.includes('worried') || postType === 'symptom_share') {
      const pattern = availablePatterns.value.find(p => p.id === 'just-us')
      if (pattern) {
        newSuggestions.push({
          pattern,
          confidence: 75,
          reason: "Personal feelings are often shared privately first",
          learned_from: 'content_analysis'
        })
      }
    }

    // Milestone/celebration detection
    if (text.includes('milestone') || text.includes('celebration') || postType === 'milestone') {
      const pattern = availablePatterns.value.find(p => p.id === 'close-family')
      if (pattern) {
        newSuggestions.push({
          pattern,
          confidence: 85,
          reason: "Milestones are perfect for sharing with close family",
          learned_from: 'content_analysis'
        })
      }
    }

    // Photo-specific suggestions
    if (postType === 'belly_photo' || text.includes('photo') || text.includes('picture')) {
      const pattern = availablePatterns.value.find(p => p.id === 'grandparents')
      if (pattern) {
        newSuggestions.push({
          pattern,
          confidence: 80,
          reason: "Grandparents love seeing baby bump photos",
          learned_from: 'content_analysis'
        })
      }
    }

    suggestions.value = newSuggestions
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 2) // Limit to top 2 suggestions
      
  } catch (err) {
    console.warn('Failed to generate suggestions:', err)
  }
}

const loadCircles = async () => {
  loading.value = true
  error.value = null
  
  try {
    // For now, use default patterns
    // In real implementation, fetch user's custom patterns from API
    availablePatterns.value = [...defaultPatterns]
    
    // Load family members for pattern preview
    // familyMembers.value = await api.getFamilyMembers()
    
    // Generate suggestions if we have content
    if (canShowSuggestions.value) {
      await generateSuggestions()
    }
    
  } catch (err: any) {
    error.value = err.message || 'Failed to load circles'
    console.error('Error loading circles:', err)
  } finally {
    loading.value = false
  }
}

const retryLoadCircles = () => {
  loadCircles()
}

// Watch for content changes to update suggestions
watch(() => props.postContent, (newContent) => {
  if (newContent && canShowSuggestions.value) {
    generateSuggestions()
  }
}, { deep: true })

// Watch for modelValue changes
watch(() => props.modelValue, (newValue) => {
  selectedPattern.value = newValue
})

// Initialize
onMounted(() => {
  loadCircles()
})
</script>

<style scoped>
/* Smooth transitions for all interactive elements */
button, .grid > * {
  transition: all 0.2s ease-in-out;
}

/* Hover effects for better touch experience */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
button:focus-visible {
  outline: 2px solid theme('colors.gentle-mint');
  outline-offset: 2px;
}

/* Advanced toggle animation */
svg {
  transition: transform 0.2s ease-in-out;
}

/* Loading animation enhancement */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>