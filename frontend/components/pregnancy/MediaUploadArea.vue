<template>
  <div class="space-y-4">
    <label class="block text-sm font-primary font-medium text-gray-700">
      Add Photos or Videos
      <span v-if="postType === 'ULTRASOUND'" class="text-gentle-mint">(Ultrasound images)</span>
      <span v-else-if="postType === 'BELLY_PHOTO'" class="text-soft-pink">(Progress photos)</span>
    </label>

    <!-- Upload area -->
    <div
      ref="dropZone"
      :class="[
        'relative border-2 border-dashed rounded-xl p-6 transition-all duration-200',
        isDragOver 
          ? 'border-light-coral bg-light-coral/10 scale-105' 
          : 'border-light-coral/30 bg-light-coral/5',
        'hover:border-light-coral hover:bg-light-coral/10'
      ]"
      @click="triggerFileInput"
      @dragenter.prevent="handleDragEnter"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <!-- Upload icon and text -->
      <div class="text-center">
        <div class="mx-auto w-12 h-12 mb-4">
          <svg 
            v-if="!uploadFiles.length"
            class="w-full h-full text-light-coral/60" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="1.5" 
              d="M12 4v16m8-8H4"
            />
          </svg>
          <div v-else class="w-full h-full bg-light-coral/20 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-light-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </div>
        
        <p class="text-sm font-primary font-medium text-gray-700 mb-1">
          {{ uploadFiles.length ? `${uploadFiles.length} file(s) selected` : 'Click to upload or drag and drop' }}
        </p>
        <p class="text-xs text-gray-500">
          PNG, JPG, GIF, MP4 up to 10MB each
        </p>
      </div>

      <!-- Hidden file input -->
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*,video/*"
        class="hidden"
        @change="handleFileInput"
      >

      <!-- Upload progress overlay -->
      <div 
        v-if="isUploading" 
        class="absolute inset-0 bg-white/90 rounded-xl flex items-center justify-center"
      >
        <div class="text-center">
          <div class="w-8 h-8 border-3 border-light-coral/20 border-t-light-coral rounded-full animate-spin mx-auto mb-2"></div>
          <p class="text-sm font-medium text-gray-700">Uploading... {{ uploadProgress }}%</p>
        </div>
      </div>
    </div>

    <!-- File preview grid -->
    <div v-if="uploadFiles.length" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div
        v-for="(file, index) in uploadFiles"
        :key="index"
        class="relative group bg-white border border-light-coral/30 rounded-lg overflow-hidden"
      >
        <!-- Image preview -->
        <div class="aspect-square bg-gray-100">
          <img
            v-if="file.type.startsWith('image/')"
            :src="file.preview"
            :alt="file.name"
            class="w-full h-full object-cover"
          >
          <div
            v-else-if="file.type.startsWith('video/')"
            class="w-full h-full flex items-center justify-center bg-gray-200"
          >
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <div v-else class="w-full h-full flex items-center justify-center bg-gray-200">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
        </div>

        <!-- File info overlay -->
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
          <p class="text-xs text-white font-medium truncate">{{ file.name }}</p>
          <p class="text-xs text-gray-300">{{ formatFileSize(file.size) }}</p>
        </div>

        <!-- Remove button -->
        <button
          @click.stop="removeFile(index)"
          class="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center hover:bg-red-600"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>

        <!-- Special indicators -->
        <div v-if="postType === 'ULTRASOUND'" class="absolute top-2 left-2">
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gentle-mint/90 text-white">
            👶 Ultrasound
          </span>
        </div>
        <div v-else-if="postType === 'BELLY_PHOTO'" class="absolute top-2 left-2">
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-soft-pink/90 text-white">
            📸 Progress
          </span>
        </div>
      </div>
    </div>

    <!-- Upload tips -->
    <div v-if="postType === 'ULTRASOUND' || postType === 'BELLY_PHOTO'" class="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
      <div class="flex items-start space-x-2">
        <svg class="w-4 h-4 text-gentle-mint mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div>
          <p class="font-medium text-gray-600 mb-1">Tips for great photos:</p>
          <ul class="space-y-1">
            <li v-if="postType === 'ULTRASOUND'">• Ensure text and measurements are clearly visible</li>
            <li v-if="postType === 'BELLY_PHOTO'">• Take photos in good lighting for best results</li>
            <li v-if="postType === 'BELLY_PHOTO'">• Consider taking from the same angle each week</li>
            <li>• Photos will be automatically tagged with your current pregnancy week</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface FileWithPreview extends File {
  preview?: string
}

// Props
interface Props {
  postType?: string
  modelValue?: File[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [files: File[]]
  'upload-progress': [progress: number]
}>()

// Refs
const dropZone = ref<HTMLDivElement>()
const fileInput = ref<HTMLInputElement>()

// State
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadFiles = ref<FileWithPreview[]>([])

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    handleFiles(Array.from(input.files))
  }
}

const handleDragEnter = () => {
  isDragOver.value = true
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  if (!dropZone.value?.contains(event.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  handleFiles(files)
}

const handleFiles = (files: File[]) => {
  const validFiles = files.filter(file => {
    // Check file type
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      console.warn(`File ${file.name} is not a valid image or video`)
      return false
    }
    
    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return false
    }
    
    return true
  })

  // Create preview URLs for images
  const filesWithPreviews = validFiles.map(file => {
    const fileWithPreview = file as FileWithPreview
    if (file.type.startsWith('image/')) {
      fileWithPreview.preview = URL.createObjectURL(file)
    }
    return fileWithPreview
  })

  uploadFiles.value = [...uploadFiles.value, ...filesWithPreviews]
  emit('update:modelValue', uploadFiles.value)

  // Simulate upload progress
  simulateUpload()
}

const removeFile = (index: number) => {
  const file = uploadFiles.value[index]
  if (file.preview) {
    URL.revokeObjectURL(file.preview)
  }
  uploadFiles.value.splice(index, 1)
  emit('update:modelValue', uploadFiles.value)
}

const simulateUpload = () => {
  if (uploadFiles.value.length === 0) return
  
  isUploading.value = true
  uploadProgress.value = 0
  
  const interval = setInterval(() => {
    uploadProgress.value += Math.random() * 20
    
    if (uploadProgress.value >= 100) {
      uploadProgress.value = 100
      isUploading.value = false
      clearInterval(interval)
    }
    
    emit('upload-progress', uploadProgress.value)
  }, 200)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Cleanup on unmount
onUnmounted(() => {
  uploadFiles.value.forEach(file => {
    if (file.preview) {
      URL.revokeObjectURL(file.preview)
    }
  })
})

// Watch for external changes
watch(() => props.modelValue, (newFiles) => {
  if (newFiles && newFiles !== uploadFiles.value) {
    uploadFiles.value = newFiles as FileWithPreview[]
  }
}, { immediate: true })
</script>

<style scoped>
/* Custom border animation */
.border-dashed {
  border-style: dashed;
  border-width: 2px;
  animation: dash 20s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -1000;
  }
}

/* Hover effects */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>