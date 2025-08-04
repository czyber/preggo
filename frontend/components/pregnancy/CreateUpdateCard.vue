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

                <!-- Simplified privacy picker inline -->
                <div v-if="showPrivacyPicker" class="space-y-2 p-3 bg-gray-50 rounded-lg">
                  <button
                    v-for="option in simplePrivacyOptions"
                    :key="option.value"
                    @click="selectPrivacy(option.value)"
                    :class="[
                      'w-full p-2 rounded text-left flex items-center gap-3 transition-all',
                      privacy.visibility === option.value
                        ? 'bg-soft-pink/20'
                        : 'hover:bg-gray-200'
                    ]"
                  >
                    <span>{{ option.icon }}</span>
                    <div>
                      <p class="text-sm font-medium text-gray-800">{{ option.label }}</p>
                      <p class="text-xs text-gray-600">{{ option.description }}</p>
                    </div>
                  </button>
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
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { usePregnancyStore } from '~/stores/pregnancy'
import { usePostsStore } from '~/stores/posts'
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

// Simplified privacy options
const simplePrivacyOptions = [
  { value: 'private' as VisibilityLevel, icon: '🔒', label: 'Just me', description: 'Save privately' },
  { value: 'partner_only' as VisibilityLevel, icon: '💕', label: 'Partner', description: 'Share with partner' },
  { value: 'immediate' as VisibilityLevel, icon: '👨‍👩‍👧', label: 'Close family', description: 'Parents & siblings' },
  { value: 'all_family' as VisibilityLevel, icon: '👪', label: 'All family', description: 'Everyone in family' }
]

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
  const privacyData = simplePrivacyOptions.find(o => o.value === visibility)
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