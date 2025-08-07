<template>
  <div class="post-content space-y-4">
    <!-- Post Title -->
    <h3 v-if="post.content?.title" class="font-semibold text-lg text-gray-900 font-primary leading-snug">
      {{ post.content.title }}
    </h3>

    <!-- Post Text Content -->
    <div v-if="post.content?.text" class="prose prose-sm max-w-none">
      <div
        v-if="!expanded && isLongContent"
        class="relative"
      >
        <!-- Truncated content -->
        <div class="text-gray-700 leading-relaxed">
          {{ truncatedContent }}
        </div>
        
        <!-- Gradient fade overlay -->
        <div class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent pointer-events-none" />
        
        <!-- Expand button -->
        <button
          @click="toggleExpansion"
          class="mt-2 text-soft-pink hover:text-soft-pink/80 text-sm font-medium transition-colors"
        >
          Show more
        </button>
      </div>
      
      <!-- Full content -->
      <div v-else class="text-gray-700 leading-relaxed whitespace-pre-wrap">
        {{ post.content.text }}
        
        <!-- Collapse button for long content -->
        <button
          v-if="expanded && isLongContent"
          @click="toggleExpansion"
          class="block mt-2 text-soft-pink hover:text-soft-pink/80 text-sm font-medium transition-colors"
        >
          Show less
        </button>
      </div>
    </div>

    <!-- Weekly Update Specific Content -->
    <div v-if="post.type === 'weekly_update' && post.content" class="space-y-3">
      <!-- Week and Mood Info -->
      <div class="flex items-center gap-2 text-sm">
        <span v-if="post.content?.week" class="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
          Week {{ post.content.week }}
        </span>
        <span v-if="post.content?.mood" class="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
          {{ getMoodEmoji(post.content.mood) }} {{ capitalizeFirst(post.content.mood) }}
        </span>
      </div>

      <!-- Tags -->
      <div v-if="post.content?.tags && post.content.tags.length > 0" class="flex flex-wrap gap-1">
        <span
          v-for="tag in post.content.tags"
          :key="tag"
          class="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
        >
          #{{ tag }}
        </span>
      </div>
    </div>

    <!-- Media Gallery -->
    <div v-if="post.media_items && post.media_items.length > 0" class="media-gallery">
      <!-- Single image -->
      <div v-if="post.media_items.length === 1" class="single-media">
        <div
          @click="handleMediaClick(0)"
          class="relative rounded-2xl overflow-hidden cursor-pointer group"
          :class="getMediaContainerClass(post.media_items[0])"
        >
          <img
            v-if="post.media_items[0].type === 'image'"
            :src="post.media_items[0].url"
            :alt="post.media_items[0].alt_text || 'Post image'"
            class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
          
          <video
            v-else-if="post.media_items[0].type === 'video'"
            :src="post.media_items[0].url"
            class="w-full h-full object-cover"
            controls
            preload="metadata"
          />
          
          <!-- Pregnancy context for ultrasound images -->
          <div
            v-if="isUltrasoundImage(post.media_items[0])"
            class="absolute top-3 left-3 px-2 py-1 bg-black/70 text-white text-xs rounded-full"
          >
            👶 Ultrasound
          </div>
        </div>
      </div>

      <!-- Multiple images -->
      <div v-else class="grid gap-2" :class="getGridClass(post.media_items.length)">
        <div
          v-for="(media, index) in post.media_items.slice(0, 4)"
          :key="media.id"
          @click="handleMediaClick(index)"
          class="relative rounded-xl overflow-hidden cursor-pointer group aspect-square"
        >
          <img
            v-if="media.type === 'image'"
            :src="media.url"
            :alt="media.alt_text || `Post image ${index + 1}`"
            class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
          
          <video
            v-else-if="media.type === 'video'"
            :src="media.url"
            class="w-full h-full object-cover"
            preload="metadata"
          />
          
          <!-- Overlay for excess images -->
          <div
            v-if="index === 3 && post.media_items.length > 4"
            class="absolute inset-0 bg-black/60 flex items-center justify-center text-white font-semibold text-lg"
          >
            +{{ post.media_items.length - 4 }}
          </div>
          
          <!-- Media type indicator -->
          <div
            v-if="media.type === 'video'"
            class="absolute top-2 right-2 w-6 h-6 bg-black/70 rounded-full flex items-center justify-center"
          >
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Tags -->
    <div v-if="post.tags && post.tags.length > 0" class="flex flex-wrap gap-2">
      <span
        v-for="tag in post.tags"
        :key="tag"
        class="inline-flex items-center px-2 py-1 bg-gentle-mint/20 text-gray-700 text-xs font-medium rounded-full"
      >
        #{{ tag }}
      </span>
    </div>

    <!-- Pregnancy Context Card -->
    <div
      v-if="post.pregnancy_context && (post.pregnancy_context.baby_development || (post.pregnancy_context.pregnancy_symptoms && post.pregnancy_context.pregnancy_symptoms.length > 0))"
      class="pregnancy-context p-4 bg-gradient-to-r from-blue-50/50 to-gentle-mint/20 rounded-xl border border-blue-200/40"
    >
      <h4 class="font-semibold text-gray-800 text-sm mb-2 flex items-center gap-2">
        <span class="text-base">👶</span>
        <span v-if="post.pregnancy_context.current_week">
          Week {{ post.pregnancy_context.current_week }} Updates
        </span>
        <span v-else>
          Pregnancy Updates
        </span>
      </h4>
      
      <div class="space-y-3 text-sm">
        <!-- Baby Development -->
        <div v-if="post.pregnancy_context.baby_development" class="flex items-start gap-2">
          <span class="text-soft-pink font-medium">Baby:</span>
          <span class="text-gray-700">{{ post.pregnancy_context.baby_development }}</span>
        </div>
        
        <!-- Symptoms -->
        <div v-if="post.pregnancy_context.pregnancy_symptoms && post.pregnancy_context.pregnancy_symptoms.length > 0" class="flex items-start gap-2">
          <span class="text-gray-700 font-medium">Symptoms:</span>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="symptom in post.pregnancy_context.pregnancy_symptoms"
              :key="symptom"
              class="px-2 py-0.5 bg-white/50 rounded-full text-xs"
            >
              {{ symptom }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Special Post Content Types -->
    
    <!-- Week Comparison (for update posts) -->
    <div
      v-if="post.type === 'update' && post.week_comparison"
      class="week-comparison bg-muted-lavender/10 rounded-xl p-4 border border-muted-lavender/30"
    >
      <h4 class="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
        <span class="text-base">📊</span>
        This Week vs Last Week
      </h4>
      
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div class="text-gray-600 mb-1">Energy Level</div>
          <div class="flex items-center gap-2">
            <div class="flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                :class="cn(
                  'w-2 h-2 rounded-full',
                  i <= (post.week_comparison.energy_level || 0) ? 'bg-gentle-mint' : 'bg-gray-200'
                )"
              />
            </div>
            <span class="text-xs text-gray-500">{{ post.week_comparison.energy_level }}/5</span>
          </div>
        </div>
        
        <div>
          <div class="text-gray-600 mb-1">Sleep Quality</div>
          <div class="flex items-center gap-2">
            <div class="flex gap-1">
              <div
                v-for="i in 5"
                :key="i"
                :class="cn(
                  'w-2 h-2 rounded-full',
                  i <= (post.week_comparison.sleep_quality || 0) ? 'bg-soft-pink' : 'bg-gray-200'
                )"
              />
            </div>
            <span class="text-xs text-gray-500">{{ post.week_comparison.sleep_quality }}/5</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Question Context (for question posts) -->
    <div
      v-if="post.type === 'question' && post.question_context"
      class="question-context bg-light-coral/10 rounded-xl p-4 border border-light-coral/30"
    >
      <div class="flex items-start gap-3">
        <span class="text-xl">💭</span>
        <div class="flex-1">
          <h4 class="font-semibold text-gray-800 text-sm mb-2">
            Looking for advice
          </h4>
          <div class="text-sm text-gray-700">
            This is a question post - family responses are especially appreciated!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { cn } from '~/components/ui/utils'
import type { components } from '~/types/api'

type EnrichedPost = components['schemas']['EnrichedPost']

interface Props {
  post: EnrichedPost
  expanded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  expanded: false
})

const emit = defineEmits<{
  toggleExpansion: []
  mediaClick: [index: number]
}>()

// Local state
const expanded = ref(props.expanded)

// Constants
const MAX_CONTENT_LENGTH = 280

// Computed properties
const isLongContent = computed(() => {
  return (props.post.content?.text?.length || 0) > MAX_CONTENT_LENGTH
})

const truncatedContent = computed(() => {
  if (!props.post.content?.text) return ''
  return props.post.content.text.slice(0, MAX_CONTENT_LENGTH) + '...'
})

// Methods
function toggleExpansion() {
  expanded.value = !expanded.value
  emit('toggleExpansion')
}

function handleMediaClick(index: number) {
  emit('mediaClick', index)
}

function isUltrasoundImage(media: any) {
  return media.alt_text?.toLowerCase().includes('ultrasound') ||
         media.description?.toLowerCase().includes('ultrasound') ||
         media.tags?.includes('ultrasound')
}

function getMediaContainerClass(media: any) {
  // Determine aspect ratio based on media type and content
  if (media.type === 'video') {
    return 'aspect-video max-h-96'
  }
  
  if (isUltrasoundImage(media)) {
    return 'aspect-[4/3] max-h-80'
  }
  
  // Default for photos
  return 'aspect-[4/3] max-h-96'
}

function getGridClass(mediaCount: number) {
  if (mediaCount === 2) return 'grid-cols-2'
  if (mediaCount === 3) return 'grid-cols-2 [&>:first-child]:col-span-2'
  if (mediaCount >= 4) return 'grid-cols-2'
  return 'grid-cols-1'
}

function getMoodEmoji(mood: string): string {
  const moodEmojis: Record<string, string> = {
    happy: '😊',
    excited: '🤗',
    nervous: '😰',
    tired: '😴',
    emotional: '🥺',
    grateful: '🙏',
    anxious: '😟',
    content: '😌',
    overwhelmed: '😵',
    hopeful: '🤞'
  }
  return moodEmojis[mood] || '😊'
}

function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
</script>

<style scoped>
/* Content animations */
.post-content {
  animation: content-appear 0.4s ease-out 0.1s both;
}

@keyframes content-appear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Enhanced prose styling for pregnancy content */
.prose {
  color: rgb(55, 65, 81);
  line-height: 1.6;
}

.prose p {
  margin-bottom: 1rem;
}

.prose p:last-child {
  margin-bottom: 0;
}

/* Media gallery hover effects */
.media-gallery img,
.media-gallery video {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.single-media {
  max-height: 32rem;
  overflow: hidden;
}

/* Grid layout for multiple images */
.grid > div:first-child:nth-last-child(3) {
  grid-column: span 2;
}

/* Tag animations */
.post-content span[class*="bg-gentle-mint"] {
  animation: tag-appear 0.3s ease-out;
  animation-fill-mode: both;
}

.post-content span[class*="bg-gentle-mint"]:nth-child(1) { animation-delay: 0.1s; }
.post-content span[class*="bg-gentle-mint"]:nth-child(2) { animation-delay: 0.15s; }
.post-content span[class*="bg-gentle-mint"]:nth-child(3) { animation-delay: 0.2s; }

@keyframes tag-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Pregnancy context card styling */
.pregnancy-context {
  animation: context-appear 0.5s ease-out 0.2s both;
}

@keyframes context-appear {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Media loading states - removed to prevent gray overlay */

/* Enhanced accessibility */
.post-content button:focus {
  outline: 2px solid #F8BBD0;
  outline-offset: 2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .single-media {
    max-height: 24rem;
  }
  
  .grid {
    gap: 0.5rem;
  }
  
  .pregnancy-context,
  .week-comparison,
  .question-context {
    padding: 1rem;
  }
  
  .prose {
    font-size: 0.875rem;
  }
}

/* Dark mode support for media overlays */
@media (prefers-color-scheme: dark) {
  .media-gallery .absolute {
    background-color: rgba(0, 0, 0, 0.8);
  }
}

/* Smooth transitions for interactive elements */
.post-content button,
.media-gallery > div {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Special styling for ultrasound images - removed filters */
</style>
