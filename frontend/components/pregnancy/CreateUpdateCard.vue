<template>
  <BaseCard variant="default" class="relative p-4 sm:p-6">
    <!-- Main content -->
    <div class="relative">
      <!-- Simplified header - mobile friendly -->
      <div class="mb-4">
        <h3 class="text-lg font-primary font-medium text-gray-800">
          Share an update
        </h3>
      </div>

      <!-- Quick create section -->
      <div v-if="!isCreating" class="space-y-4">
        <!-- Simplified input - just a clickable area that opens full creator -->
        <button
          @click="openFullCreator"
          class="w-full text-left"
        >
          <div class="p-4 border border-gray-200 rounded-xl hover:border-soft-pink/50 transition-colors duration-200 bg-white">
            <p class="text-gray-500 font-secondary">
              What's happening today?
            </p>
          </div>
        </button>

        <!-- Simplified quick actions - Linear style -->
        <div class="flex items-center gap-4 text-sm">
          <button
            @click="selectPostType('belly_photo')"
            class="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span>Photo</span>
          </button>
          
          <button
            @click="selectPostType('milestone')"
            class="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
            </svg>
            <span>Milestone</span>
          </button>
          
          <button
            @click="selectPostType('symptom_share')"
            class="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>Feeling</span>
          </button>
        </div>
      </div>

      <!-- Full creation mode - opens in modal/sheet -->
      <Teleport to="body">
        <div v-if="isCreating" class="fixed inset-0 z-50 overflow-y-auto">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50" @click="cancelCreating"></div>
          
          <!-- Modal content - optimized for mobile -->
          <div class="relative min-h-screen sm:flex sm:items-center sm:justify-center p-0 sm:p-4">
            <div class="relative bg-white w-full sm:max-w-2xl sm:rounded-2xl shadow-xl">
              <!-- Header -->
              <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 sm:px-6 sm:py-4 sm:rounded-t-2xl">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <button
                      @click="cancelCreating"
                      class="p-2 -ml-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                    <h2 class="text-lg font-primary font-medium text-gray-800">
                      Create update
                    </h2>
                  </div>
                  
                  <BaseButton
                    variant="default"
                    size="sm"
                    @click="publishUpdate"
                    :disabled="!canPublish || isPublishing || isUploadingMedia"
                  >
                    <span v-if="isUploadingMedia">Uploading...</span>
                    <span v-else-if="isPublishing">Sharing...</span>
                    <span v-else>Share</span>
                  </BaseButton>
                </div>
              </div>

              <!-- Content -->
              <div class="p-4 sm:p-6 space-y-6 pb-20 sm:pb-6">
                <!-- Post type selector - simplified -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-3">
                    What type of update?
                  </label>
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <button
                      v-for="type in mainPostTypes"
                      :key="type.value"
                      @click="selectedPostType = type.value"
                      :class="[
                        'p-3 rounded-lg border transition-all',
                        selectedPostType === type.value
                          ? 'border-soft-pink bg-soft-pink/10'
                          : 'border-gray-200 hover:border-gray-300'
                      ]"
                    >
                      <span class="block text-xl mb-1">{{ type.emoji }}</span>
                      <span class="text-xs text-gray-700">{{ type.label }}</span>
                    </button>
                  </div>
                </div>

                <!-- Main content - simplified -->
                <div>
                  <textarea
                    v-model="postContent.text"
                    :placeholder="getPlaceholder()"
                    class="w-full min-h-[120px] p-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-soft-pink/20 focus:border-soft-pink transition-all font-secondary text-gray-800"
                    autofocus
                  />
                </div>

                <!-- Quick add media -->
                <div class="flex items-center gap-4">
                  <button
                    @click="triggerMediaUpload"
                    class="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    <span>Add photo</span>
                  </button>
                  
                  <button
                    @click="showMoodPicker = !showMoodPicker"
                    class="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    <span class="text-base">{{ postContent.mood ? getMoodEmoji(postContent.mood) : '😊' }}</span>
                    <span>{{ postContent.mood ? getMoodLabel(postContent.mood) : 'Mood' }}</span>
                  </button>
                  
                  <button
                    @click="showPrivacyPicker = !showPrivacyPicker"
                    class="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors ml-auto"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                    <span>{{ getPrivacyLabel(privacy.visibility) }}</span>
                  </button>
                </div>

                <!-- Simplified mood picker inline -->
                <div v-if="showMoodPicker" class="grid grid-cols-4 gap-2 p-3 bg-gray-50 rounded-lg">
                  <button
                    v-for="mood in simpleMoods"
                    :key="mood.value"
                    @click="selectMood(mood.value)"
                    :class="[
                      'p-2 rounded text-center transition-all',
                      postContent.mood === mood.value
                        ? 'bg-soft-pink/20'
                        : 'hover:bg-gray-200'
                    ]"
                  >
                    <span class="block text-2xl">{{ mood.emoji }}</span>
                    <span class="text-xs text-gray-600">{{ mood.label }}</span>
                  </button>
                </div>

                <!-- Enhanced privacy picker with invite functionality -->
                <div v-if="showPrivacyPicker" class="space-y-3 p-4 bg-gray-50 rounded-lg">
                  <!-- Privacy Options Grid -->
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      v-for="option in simplePrivacyOptions"
                      :key="option.value"
                      @click="selectPrivacy(option.value)"
                      :class="[
                        'p-3 rounded-lg text-left transition-all border',
                        privacy.visibility === option.value
                          ? 'border-gentle-mint bg-gentle-mint/10 shadow-sm'
                          : 'border-gray-200 hover:border-gentle-mint/50 hover:bg-gentle-mint/5'
                      ]"
                    >
                      <div class="space-y-2">
                        <div class="flex items-center space-x-3">
                          <span class="text-xl">{{ option.icon }}</span>
                          <h3 class="font-medium text-gray-800 text-sm">{{ option.label }}</h3>
                        </div>
                        <p class="text-xs text-gray-600">{{ option.description }}</p>
                        <p class="text-xs text-gray-500">{{ option.count }} {{ option.count === 1 ? 'person' : 'people' }}</p>
                      </div>
                    </button>
                  </div>
                  
                  <!-- Invite Section when Everyone is selected -->
                  <div v-if="privacy.visibility === 'ALL_FAMILY'" class="mt-4 p-3 bg-gradient-to-r from-soft-pink/10 to-gentle-mint/10 rounded-lg border border-gentle-mint/20">
                    <div class="flex items-center justify-between">
                      <div class="space-y-1">
                        <h4 class="font-medium text-gray-800 text-sm">Want to share with more family?</h4>
                        <p class="text-xs text-gray-600">Invite family members to join your pregnancy journey</p>
                      </div>
                      <button
                        @click="openInviteModal"
                        class="flex items-center space-x-1 px-3 py-2 bg-gentle-mint text-white rounded-lg hover:bg-gentle-mint/90 transition-colors text-xs font-medium"
                      >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        <span>Invite</span>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Selected Privacy Preview -->
                  <div v-if="privacy.visibility !== 'PRIVATE'" class="mt-3 p-3 bg-white rounded-lg border">
                    <div class="flex items-center justify-between">
                      <div>
                        <h4 class="font-medium text-gray-800 text-sm mb-1">Who will see this:</h4>
                        <div class="flex -space-x-1">
                          <!-- Mock avatar previews - replace with actual family member avatars -->
                          <div v-for="n in Math.min(5, getSelectedPrivacyOption()?.count || 0)" :key="n" class="w-6 h-6 bg-gentle-mint/20 rounded-full border-2 border-white flex items-center justify-center text-xs text-gray-700">
                            {{ n }}
                          </div>
                          <div v-if="(getSelectedPrivacyOption()?.count || 0) > 5" class="w-6 h-6 bg-gray-300 rounded-full border-2 border-white flex items-center justify-center text-xs text-gray-600">
                            +{{ (getSelectedPrivacyOption()?.count || 0) - 5 }}
                          </div>
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="text-lg font-semibold text-gray-800">{{ getSelectedPrivacyOption()?.count || 0 }}</div>
                        <div class="text-xs text-gray-500">people</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Media preview if any -->
                <div v-if="mediaFiles.length > 0" class="flex gap-2 overflow-x-auto py-2">
                  <div
                    v-for="(file, index) in mediaFiles"
                    :key="index"
                    class="relative flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden bg-gray-100"
                  >
                    <!-- Image preview -->
                    <img
                      v-if="file.preview"
                      :src="file.preview"
                      class="w-full h-full object-cover"
                      :class="{ 'opacity-50': file.uploading }"
                    />
                    
                    <!-- Upload progress overlay -->
                    <div
                      v-if="file.uploading"
                      class="absolute inset-0 bg-black/50 flex items-center justify-center"
                    >
                      <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    </div>
                    
                    <!-- Error overlay -->
                    <div
                      v-else-if="file.error"
                      class="absolute inset-0 bg-red-500/80 flex items-center justify-center"
                    >
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                    
                    <!-- Remove button -->
                    <button
                      v-if="!file.uploading"
                      @click="removeMedia(index)"
                      class="absolute top-1 right-1 w-5 h-5 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <!-- Upload error message -->
                <div v-if="uploadError" class="p-2 bg-red-50 border border-red-200 rounded-lg">
                  <p class="text-sm text-red-600">{{ uploadError }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
      
      <!-- Invite Modal -->
      <Teleport to="body">
        <div v-if="showInviteModal" class="fixed inset-0 z-50 overflow-y-auto">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50" @click="showInviteModal = false"></div>
          
          <!-- Modal content -->
          <div class="relative min-h-screen sm:flex sm:items-center sm:justify-center p-0 sm:p-4">
            <div class="relative bg-white w-full sm:max-w-md sm:rounded-xl shadow-xl">
              <!-- Header -->
              <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 sm:rounded-t-xl">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-800">Invite Family</h3>
                  <button
                    @click="showInviteModal = false"
                    class="p-2 -mr-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Quick Invite Form -->
              <div class="p-4 space-y-4">
                <p class="text-sm text-gray-600">Share your pregnancy journey with family members</p>
                
                <!-- Relationship Selection -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Who are you inviting?</label>
                  <select 
                    v-model="selectedRelationship"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gentle-mint focus:border-gentle-mint text-sm"
                  >
                    <option value="">Select relationship...</option>
                    <option value="partner">Partner/Spouse</option>
                    <option value="mother">Mother</option>
                    <option value="father">Father</option>
                    <option value="sister">Sister</option>
                    <option value="brother">Brother</option>
                    <option value="grandmother">Grandmother</option>
                    <option value="grandfather">Grandfather</option>
                    <option value="mother_in_law">Mother-in-law</option>
                    <option value="father_in_law">Father-in-law</option>
                    <option value="aunt">Aunt</option>
                    <option value="uncle">Uncle</option>
                    <option value="friend">Close Friend</option>
                    <option value="mentor">Mentor</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                
                <!-- Custom Name -->
                <div v-if="selectedRelationship">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Custom name (optional)</label>
                  <input
                    v-model="customTitle"
                    type="text"
                    placeholder="e.g., 'Grandma Mary', 'Aunt Sarah'"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gentle-mint focus:border-gentle-mint text-sm"
                  />
                </div>
                
                <!-- Generate Link Button -->
                <button
                  v-if="selectedRelationship"
                  @click="generateInviteLink"
                  :disabled="generatingLink"
                  class="w-full py-3 bg-gradient-to-r from-soft-pink to-gentle-mint text-white rounded-lg hover:from-soft-pink/90 hover:to-gentle-mint/90 transition-all font-medium disabled:opacity-50"
                >
                  {{ generatingLink ? 'Generating...' : 'Generate Invite Link' }}
                </button>
                
                <!-- Generated Link -->
                <div v-if="generatedLink" class="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-800">Share this link:</span>
                    <button
                      @click="copyInviteLink"
                      class="px-2 py-1 text-xs bg-gentle-mint text-white rounded hover:bg-gentle-mint/90 transition-colors"
                    >
                      {{ linkCopied ? 'Copied!' : 'Copy' }}
                    </button>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      @click="shareViaWhatsApp"
                      class="flex items-center justify-center space-x-2 p-2 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg transition-colors"
                    >
                      <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                      </svg>
                      <span class="text-xs font-medium text-green-800">WhatsApp</span>
                    </button>
                    
                    <button
                      @click="shareViaSMS"
                      class="flex items-center justify-center space-x-2 p-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
                    >
                      <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                      </svg>
                      <span class="text-xs font-medium text-blue-800">Text</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { usePregnancyStore } from "@/stores/pregnancy"
import { usePostsStore } from "@/stores/posts"
import type { PostType, MoodType, VisibilityLevel } from '~/types/api'

// Props
interface Props {
  currentPregnancyWeek?: number
  currentMood?: string
}

const props = defineProps<Props>()

// Composables
const pregnancyStore = usePregnancyStore()
const postsStore = usePostsStore()
const storage = useStorage()
const api = useApi()
const toast = useToast()
const { celebrate } = useCelebration()
const auth = useAuth()

// Reactive state
const isCreating = ref(false)
const isPublishing = ref(false)
const isUploadingMedia = ref(false)
const selectedPostType = ref<PostType>('weekly_update')
const showMoodPicker = ref(false)
const showPrivacyPicker = ref(false)
const uploadError = ref<string | null>(null)

// Post content
const postContent = ref({
  text: '',
  mood: null as MoodType | null,
  week: props.currentPregnancyWeek
})

// Privacy settings
const privacy = ref({
  visibility: 'immediate' as VisibilityLevel,
  allowed_groups: [] as string[],
  allowed_members: [] as string[],
  allow_comments: true,
  allow_reactions: true,
  allow_downloads: false,
  hide_from_timeline: false
})

// Media files with upload status
interface MediaFile {
  file: File
  preview?: string
  url?: string
  uploading?: boolean
  error?: string
}
const mediaFiles = ref<MediaFile[]>([])

// Main post types - simplified
const mainPostTypes = [
  { value: 'weekly_update' as PostType, emoji: '📅', label: 'Update' },
  { value: 'belly_photo' as PostType, emoji: '📸', label: 'Photo' },
  { value: 'milestone' as PostType, emoji: '⭐', label: 'Milestone' },
  { value: 'symptom_share' as PostType, emoji: '💭', label: 'Feeling' },
  { value: 'appointment' as PostType, emoji: '🏥', label: 'Appointment' },
  { value: 'celebration' as PostType, emoji: '🎉', label: 'Celebrate' },
  { value: 'question' as PostType, emoji: '❓', label: 'Question' },
  { value: 'memory' as PostType, emoji: '💝', label: 'Memory' }
]

// Simplified moods
const simpleMoods = [
  { value: 'happy' as MoodType, emoji: '😊', label: 'Happy' },
  { value: 'excited' as MoodType, emoji: '🤗', label: 'Excited' },
  { value: 'grateful' as MoodType, emoji: '🙏', label: 'Grateful' },
  { value: 'peaceful' as MoodType, emoji: '😌', label: 'Peaceful' },
  { value: 'nervous' as MoodType, emoji: '😰', label: 'Nervous' },
  { value: 'emotional' as MoodType, emoji: '🥺', label: 'Emotional' },
  { value: 'tired' as MoodType, emoji: '😴', label: 'Tired' },
  { value: 'uncomfortable' as MoodType, emoji: '😣', label: 'Uncomfortable' }
]

// Enhanced 4-tier privacy options with member counts
const simplePrivacyOptions = computed(() => [
  { 
    value: 'PRIVATE' as VisibilityLevel, 
    icon: '🔒', 
    label: 'Just me', 
    description: 'Keep this private',
    count: 1
  },
  { 
    value: 'PARTNER_ONLY' as VisibilityLevel, 
    icon: '💕', 
    label: 'Partner only', 
    description: 'Just us two',
    count: getPartnerCount()
  },
  { 
    value: 'IMMEDIATE' as VisibilityLevel, 
    icon: '👨‍👩‍👧‍👦', 
    label: 'Inner circle', 
    description: 'Close family (parents, siblings, partner)',
    count: getInnerCircleCount()
  },
  { 
    value: 'ALL_FAMILY' as VisibilityLevel, 
    icon: '🌟', 
    label: 'Everyone', 
    description: 'All family members and friends',
    count: getEveryoneCount()
  }
])

// Member count helpers (you'll need to implement these based on your family system)
const getPartnerCount = () => {
  // TODO: Get actual partner count from family store
  return 2 // You + Partner
}

const getInnerCircleCount = () => {
  // TODO: Get actual inner circle count
  return 6 // Example count
}

const getEveryoneCount = () => {
  // TODO: Get actual total family member count
  return 18 // Example count
}

// Show invite modal state
const showInviteModal = ref(false)
const selectedRelationship = ref('')
const customTitle = ref('')
const generatingLink = ref(false)
const generatedLink = ref<string | null>(null)
const linkCopied = ref(false)

// Computed
const canPublish = computed(() => {
  return postContent.value.text?.trim() && selectedPostType.value
})

// Methods
const selectPostType = (type: string) => {
  selectedPostType.value = type
  openFullCreator()
}

const openFullCreator = () => {
  isCreating.value = true
  showMoodPicker.value = false
  showPrivacyPicker.value = false
  // Lock body scroll on mobile
  document.body.style.overflow = 'hidden'
}

const cancelCreating = () => {
  isCreating.value = false
  // Reset form data
  postContent.value = {
    text: '',
    mood: null,
    week: props.currentPregnancyWeek
  }
  mediaFiles.value = []
  showMoodPicker.value = false
  showPrivacyPicker.value = false
  // Restore body scroll
  document.body.style.overflow = ''
}

const publishUpdate = async () => {
  if (!canPublish.value || !pregnancyStore.currentPregnancy) return
  
  isPublishing.value = true
  uploadError.value = null
  
  try {
    // First, upload any media files
    const uploadedMedia = await uploadMediaFiles()
    
    // Prepare post data according to API schema
    const postData = {
      type: selectedPostType.value,
      content: {
        text: postContent.value.text.trim(),
        mood: postContent.value.mood,
        week: postContent.value.week || pregnancyStore.currentPregnancy.pregnancy_details?.current_week,
        tags: [] // TODO: Add tags support
      },
      privacy: privacy.value,
      author_id: auth.user.value?.id || '',
      pregnancy_id: pregnancyStore.currentPregnancy.id
    }
    
    // Create the post
    const { data: newPost, error } = await api.createPost(postData)
    
    if (error) {
      throw new Error(error.detail || 'Failed to create post')
    }
    
    if (newPost) {
      // Create media items for the post
      for (const media of uploadedMedia) {
        if (media.url) {
          await api.createMediaItem({
            type: media.file.type.startsWith('image/') ? 'image' : 'video',
            url: media.url,
            filename: media.file.name,
            size: media.file.size,
            caption: null,
            order: uploadedMedia.indexOf(media),
            media_metadata: {
              pregnancy_week: postContent.value.week,
              is_ultrasound: selectedPostType.value === 'ultrasound',
              is_belly_photo: selectedPostType.value === 'belly_photo'
            },
            uploaded_by: auth.user.value?.id || '',
            post_id: newPost.id
          })
        }
      }
      
      // Add to posts store
      await postsStore.fetchPosts(pregnancyStore.currentPregnancy.id)
      
      // Show celebration animation
      celebrate({
        postType: postContent.value.type
      })
      
      // Reset and close
      cancelCreating()
    }
  } catch (error: any) {
    console.error('Error publishing update:', error)
    toast.add({
      title: 'Failed to share update',
      description: error.message || 'Something went wrong. Please try again.',
      color: 'red'
    })
  } finally {
    isPublishing.value = false
  }
}

const selectMood = (mood: MoodType) => {
  postContent.value.mood = postContent.value.mood === mood ? null : mood
  showMoodPicker.value = false
}

const selectPrivacy = (visibility: VisibilityLevel) => {
  privacy.value.visibility = visibility
  showPrivacyPicker.value = false
}

const getSelectedPrivacyOption = () => {
  return simplePrivacyOptions.value.find(option => option.value === privacy.value.visibility)
}

const openInviteModal = () => {
  showInviteModal.value = true
  showPrivacyPicker.value = false
}

const generateInviteLink = async () => {
  if (!selectedRelationship.value || !pregnancyStore.currentPregnancy) return
  
  generatingLink.value = true
  
  try {
    const api = useApi()
    const response = await api.generateFamilyInviteLink({
      pregnancy_id: pregnancyStore.currentPregnancy.id,
      relationship: selectedRelationship.value,
      custom_title: customTitle.value || null,
      message: 'Join me on my pregnancy journey!'
    })
    
    generatedLink.value = response.data?.url
    
    // Show success feedback
    const toast = useToast()
    toast.add({
      title: 'Invite link generated!',
      description: 'You can now share this link with your family member',
      color: 'green'
    })
    
  } catch (error: any) {
    console.error('Failed to generate invite link:', error)
    
    // Show detailed error information
    const toast = useToast()
    let errorMessage = 'Please try again'
    
    if (error.status === 404) {
      errorMessage = 'API endpoint not found. Backend may not be running.'
    } else if (error.status === 500) {
      errorMessage = 'Server error. Check backend logs.'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    toast.add({
      title: 'Failed to generate link',
      description: errorMessage,
      color: 'red'
    })
  } finally {
    generatingLink.value = false
  }
}

const copyInviteLink = async () => {
  if (!generatedLink.value) return
  
  try {
    await navigator.clipboard.writeText(generatedLink.value)
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
    
    const toast = useToast()
    toast.add({
      title: 'Link copied!',
      description: 'You can now paste it anywhere to share',
      color: 'green'
    })
  } catch (error) {
    console.error('Failed to copy link:', error)
  }
}

const shareViaWhatsApp = () => {
  if (!generatedLink.value) return
  
  const relationshipLabel = getRelationshipLabel(selectedRelationship.value)
  const babyName = pregnancyStore.currentPregnancy?.baby_name || 'our baby'
  const message = `Hi! I'd love to share ${babyName}'s pregnancy journey with you. Join me here: ${generatedLink.value}`
  
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`
  window.open(whatsappUrl, '_blank')
}

const shareViaSMS = () => {
  if (!generatedLink.value) return
  
  const babyName = pregnancyStore.currentPregnancy?.baby_name || 'our baby'
  const message = `Hi! I'd love to share ${babyName}'s pregnancy journey with you. Join me here: ${generatedLink.value}`
  
  const smsUrl = `sms:?body=${encodeURIComponent(message)}`
  window.location.href = smsUrl
}

const getRelationshipLabel = (relationship: string) => {
  const labels: { [key: string]: string } = {
    partner: 'Partner',
    mother: 'Mother',
    father: 'Father',
    sister: 'Sister',
    brother: 'Brother',
    grandmother: 'Grandmother',
    grandfather: 'Grandfather',
    mother_in_law: 'Mother-in-law',
    father_in_law: 'Father-in-law',
    aunt: 'Aunt',
    uncle: 'Uncle',
    friend: 'Friend',
    mentor: 'Mentor',
    other: 'Family Member'
  }
  return labels[relationship] || 'Family Member'
}

const triggerMediaUpload = () => {
  // Create input dynamically
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*,video/*'
  input.multiple = true
  input.onchange = (e: Event) => {
    const target = e.target as HTMLInputElement
    if (target.files) {
      handleMediaFiles(Array.from(target.files))
    }
  }
  input.click()
}

const handleMediaFiles = (files: File[]) => {
  files.forEach(file => {
    // Validate file
    if (!storage.isAllowedFileType(file.type)) {
      toast.add({
        title: 'Invalid file type',
        description: `${file.name} is not a supported file type`,
        color: 'orange'
      })
      return
    }
    
    if (file.size > storage.getMaxFileSize(file.type)) {
      toast.add({
        title: 'File too large',
        description: `${file.name} exceeds the maximum file size`,
        color: 'orange'
      })
      return
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      mediaFiles.value.push({
        file,
        preview: e.target?.result as string
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeMedia = (index: number) => {
  const media = mediaFiles.value[index]
  if (media.preview) {
    URL.revokeObjectURL(media.preview)
  }
  mediaFiles.value.splice(index, 1)
}

const uploadMediaFiles = async (): Promise<MediaFile[]> => {
  if (mediaFiles.value.length === 0) return []
  
  isUploadingMedia.value = true
  const uploadedFiles: MediaFile[] = []
  
  try {
    for (const media of mediaFiles.value) {
      media.uploading = true
      
      // Upload to Supabase storage
      const result = await storage.uploadFile(
        media.file,
        storage.BUCKETS.PREGNANCY_MEDIA,
        `posts/${pregnancyStore.currentPregnancy?.id}/${new Date().getFullYear()}`
      )
      
      if (result.error) {
        media.error = result.error
        throw new Error(`Failed to upload ${media.file.name}: ${result.error}`)
      }
      
      media.url = result.url
      media.uploading = false
      uploadedFiles.push(media)
    }
    
    return uploadedFiles
  } catch (error: any) {
    console.error('Media upload error:', error)
    throw error
  } finally {
    isUploadingMedia.value = false
  }
}

const getPlaceholder = () => {
  const placeholders: Record<PostType, string> = {
    'weekly_update': "How's your week going? Share your pregnancy journey...",
    'belly_photo': "Add a caption to your photo...",
    'milestone': "What special moment are you celebrating?",
    'symptom_share': "How are you feeling today?",
    'appointment': "How did your appointment go?",
    'celebration': "What are you celebrating?",
    'question': "What would you like to ask your family?",
    'memory': "Share a special memory...",
    'ultrasound': "Share details about your ultrasound...",
    'announcement': "What exciting news do you want to share?",
    'preparation': "What are you preparing for your baby?"
  }
  return placeholders[selectedPostType.value] || "Share your update..."
}

// Helper functions
const getMoodEmoji = (mood: string) => {
  const moodData = simpleMoods.find(m => m.value === mood)
  return moodData?.emoji || '😊'
}

const getMoodLabel = (mood: string) => {
  const moodData = simpleMoods.find(m => m.value === mood)
  return moodData?.label || 'Mood'
}

const getPrivacyLabel = (visibility: string) => {
  const privacyData = simplePrivacyOptions.value.find(o => o.value === visibility)
  return privacyData?.label || 'Privacy'
}

// Cleanup on unmount
onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Mobile-first responsive design */
@media (max-width: 640px) {
  .fixed.inset-0 {
    padding: 0;
  }
}

/* Smooth transitions */
button {
  transition: all 0.15s ease;
}

/* Remove tap highlight on mobile */
button {
  -webkit-tap-highlight-color: transparent;
}

/* Ensure modal is above everything */
.z-50 {
  z-index: 9999;
}
</style>
