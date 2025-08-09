<template>
  <div 
    class="moment-content"
    :class="[getContentTypeClass(), { 'is-expanded': isExpanded }]"
  >
    <!-- Content Header (for special post types) -->
    <div v-if="shouldShowContentHeader" class="content-header mb-4">
      <div class="flex items-center gap-3">
        <UserAvatar :user="content.author" size="md" />
        <div class="flex-1">
          <h3 class="font-medium text-gray-900 text-base">
            {{ getAuthorName() }}
          </h3>
          <p v-if="getContentTypeDescription()" class="text-sm text-gray-600 mt-0.5">
            {{ getContentTypeDescription() }}
          </p>
        </div>
        <div v-if="postType === 'milestone'" class="milestone-badge">
          <span class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-gentle-mint to-soft-pink text-white rounded-full text-sm font-medium">
            <span class="mr-1">✨</span>
            Milestone
          </span>
        </div>
      </div>
    </div>

    <!-- Hero Media (photos, ultrasounds, etc.) -->
    <div v-if="mediaItems?.length" class="hero-media mb-4">
      <div 
        class="media-container rounded-xl overflow-hidden bg-warm-neutral/10"
        :class="getMediaContainerClass()"
      >
        <!-- Single Image -->
        <div 
          v-if="mediaItems.length === 1"
          class="single-media relative cursor-pointer group"
          @click="handleMediaClick(0)"
          @keydown.enter="handleMediaClick(0)"
          @keydown.space.prevent="handleMediaClick(0)"
          tabindex="0"
          :aria-label="`View ${getMediaAriaLabel(mediaItems[0])}`"
        >
          <img
            :src="mediaItems[0].url"
            :alt="getMediaAltText(mediaItems[0])"
            class="w-full h-auto max-h-80 object-cover transition-transform duration-200 group-hover:scale-[1.02]"
            loading="lazy"
          />
          <div v-if="isPregnancyPhoto(mediaItems[0])" class="pregnancy-overlay">
            <div class="absolute bottom-3 left-3 bg-black/60 text-white px-3 py-1 rounded-full text-sm backdrop-blur-sm">
              Week {{ pregnancyWeek }}
            </div>
          </div>
          <div v-if="isUltrasound(mediaItems[0])" class="ultrasound-overlay">
            <div class="absolute top-3 right-3 bg-gradient-to-r from-gentle-mint to-soft-pink text-white px-3 py-1 rounded-full text-sm backdrop-blur-sm">
              Baby's Photo ❤️
            </div>
          </div>
        </div>

        <!-- Multiple Images Grid -->
        <div 
          v-else-if="mediaItems.length > 1"
          class="media-grid grid gap-1 rounded-xl overflow-hidden"
          :class="getMediaGridClass()"
        >
          <div
            v-for="(media, index) in mediaItems.slice(0, 4)"
            :key="media.id || index"
            class="media-item relative cursor-pointer group"
            @click="handleMediaClick(index)"
            @keydown.enter="handleMediaClick(index)"
            @keydown.space.prevent="handleMediaClick(index)"
            tabindex="0"
            :aria-label="`View ${getMediaAriaLabel(media)}, image ${index + 1} of ${mediaItems.length}`"
          >
            <img
              :src="media.url"
              :alt="getMediaAltText(media)"
              class="w-full h-full object-cover aspect-square transition-transform duration-200 group-hover:scale-105"
              loading="lazy"
            />
            <div 
              v-if="index === 3 && mediaItems.length > 4"
              class="more-overlay absolute inset-0 bg-black/60 flex items-center justify-center text-white font-medium text-lg backdrop-blur-sm"
            >
              +{{ mediaItems.length - 4 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Text Content -->
    <div 
      v-if="content.content"
      class="text-content mb-4"
    >
      <div 
        class="content-text text-gray-800 leading-relaxed"
        :class="getTextSizeClass()"
      >
        <!-- Milestone Content Special Treatment -->
        <div v-if="postType === 'milestone'" class="milestone-content">
          <h2 class="text-xl font-semibold text-gray-900 mb-2 font-primary">
            {{ getMilestoneTitle() }}
          </h2>
          <div 
            class="milestone-description text-base leading-relaxed"
            v-html="formatMilestoneContent(content.content)"
          />
        </div>

        <!-- Regular Content -->
        <div v-else class="regular-content">
          <div
            class="content-body"
            :class="{ 'line-clamp-3': !isExpanded && shouldTruncate }"
            v-html="formatContentText(content.content)"
          />
          
          <!-- Read More Button -->
          <button
            v-if="expandable && shouldTruncate && !isExpanded"
            @click="handleExpansion"
            class="read-more-btn mt-2 text-soft-pink hover:text-soft-pink/80 text-sm font-medium transition-colors inline-flex items-center gap-1"
          >
            Read more
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Pregnancy Keywords Highlighting -->
      <div v-if="hasPregnancyKeywords" class="pregnancy-keywords mt-3 flex flex-wrap gap-1">
        <span
          v-for="keyword in extractPregnancyKeywords(content.content)"
          :key="keyword"
          class="keyword-tag inline-flex items-center px-2 py-1 bg-gentle-mint/20 text-gentle-mint-dark rounded text-xs"
        >
          {{ keyword }}
        </span>
      </div>
    </div>

    <!-- Baby Development Info (for milestone posts) -->
    <div 
      v-if="milestoneContext?.baby_development && postType === 'milestone'"
      class="baby-development bg-gradient-to-r from-warm-neutral/20 to-gentle-mint/20 rounded-lg p-4 mb-4"
    >
      <div class="flex items-start gap-3">
        <div class="baby-icon text-2xl">👶</div>
        <div class="flex-1">
          <h3 class="font-medium text-gray-800 mb-1">Your Baby This Week</h3>
          <p class="text-sm text-gray-700 leading-relaxed">
            {{ milestoneContext.baby_development }}
          </p>
        </div>
      </div>
    </div>

    <!-- Weekly Update Special Display -->
    <div 
      v-if="postType === 'update' && pregnancyWeek > 0"
      class="weekly-update-info mt-3"
    >
      <div class="progress-visualization">
        <div class="flex items-center justify-between text-xs text-gray-600 mb-2">
          <span>Week {{ pregnancyWeek }}</span>
          <span>{{ Math.round((pregnancyWeek / 40) * 100) }}% complete</span>
        </div>
        <div class="progress-bar bg-gray-200 h-1.5 rounded-full overflow-hidden">
          <div 
            class="progress-fill bg-gradient-to-r from-soft-pink to-gentle-mint h-full rounded-full transition-all duration-500"
            :style="{ width: `${(pregnancyWeek / 40) * 100}%` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { components } from '~/types/api'
import UserAvatar from '~/components/ui/UserAvatar.vue'

type PostType = 'milestone' | 'update' | 'photo' | 'journal' | 'question' | 'announcement'
type MediaItem = components['schemas']['MediaItem']
type MilestoneContext = components['schemas']['PregnancyContext']
type PostContent = components['schemas']['EnrichedPost']

interface Props {
  content: PostContent
  pregnancyWeek: number
  postType: PostType
  mediaItems?: MediaItem[]
  milestoneContext?: MilestoneContext
  expandable: boolean
}

const props = withDefaults(defineProps<Props>(), {
  postType: 'update',
  mediaItems: () => [],
  expandable: true
})

const emit = defineEmits<{
  expand: []
  mediaView: [index: number]
}>()

// Local state
const isExpanded = ref(false)
const shouldTruncate = ref(false)

// Computed properties
const shouldShowContentHeader = computed(() => {
  return props.postType === 'milestone' || props.postType === 'announcement'
})

const hasPregnancyKeywords = computed(() => {
  if (!props.content.content) return false
  const keywords = extractPregnancyKeywords(props.content.content)
  return keywords.length > 0
})

// Methods
function getAuthorName(): string {
  const author = props.content.author
  if (!author) return 'Someone'
  return author.display_name || author.first_name || 'Family member'
}

function getContentTypeDescription(): string {
  switch (props.postType) {
    case 'milestone':
      return `Reached a special milestone at week ${props.pregnancyWeek}`
    case 'announcement':
      return 'has an announcement to share'
    default:
      return ''
  }
}

function getContentTypeClass(): string {
  return `moment-content--${props.postType}`
}

function getMediaContainerClass(): string {
  if (!props.mediaItems?.length) return ''
  
  const classes = ['relative']
  if (props.mediaItems.length === 1) {
    classes.push('single-image')
  } else {
    classes.push('multi-image')
  }
  
  return classes.join(' ')
}

function getMediaGridClass(): string {
  const count = Math.min(props.mediaItems?.length || 0, 4)
  
  if (count === 2) return 'grid-cols-2'
  if (count === 3) return 'grid-cols-3'
  if (count >= 4) return 'grid-cols-2'
  
  return 'grid-cols-1'
}

function getTextSizeClass(): string {
  switch (props.postType) {
    case 'milestone':
      return 'text-base' // Larger for milestones
    case 'journal':
      return 'text-base leading-loose' // More reading-friendly
    default:
      return 'text-sm' // Standard size
  }
}

function getMediaAriaLabel(media: MediaItem): string {
  if (isUltrasound(media)) {
    return `ultrasound photo from week ${props.pregnancyWeek}`
  }
  if (isPregnancyPhoto(media)) {
    return `pregnancy photo from week ${props.pregnancyWeek}`
  }
  return media.alt_text || 'shared photo'
}

function getMediaAltText(media: MediaItem): string {
  if (media.alt_text) return media.alt_text
  
  if (isUltrasound(media)) {
    return `Ultrasound image showing baby at ${props.pregnancyWeek} weeks`
  }
  if (isPregnancyPhoto(media)) {
    return `Pregnancy photo at ${props.pregnancyWeek} weeks`
  }
  return 'Shared photo'
}

function isPregnancyPhoto(media: MediaItem): boolean {
  return media.type === 'pregnancy_photo' || 
         media.tags?.includes('belly') || 
         media.tags?.includes('bump')
}

function isUltrasound(media: MediaItem): boolean {
  return media.type === 'ultrasound' || 
         media.tags?.includes('ultrasound') ||
         media.tags?.includes('scan')
}

function getMilestoneTitle(): string {
  if (props.milestoneContext?.milestone_title) {
    return props.milestoneContext.milestone_title
  }
  
  return `Week ${props.pregnancyWeek} Milestone`
}

function formatMilestoneContent(content: string): string {
  // Enhanced formatting for milestone posts
  return content
    .replace(/\n/g, '</p><p class="mb-2">')
    .replace(/^/, '<p class="mb-2">')
    .replace(/$/, '</p>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-soft-pink-dark">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic text-gray-700">$1</em>')
}

function formatContentText(content: string): string {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
    .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" class="text-soft-pink hover:underline" target="_blank" rel="noopener">$1</a>')
}

function extractPregnancyKeywords(content: string): string[] {
  const pregnancyKeywords = [
    'kicks', 'movement', 'baby', 'bump', 'growing', 'nausea', 'tired', 'appointment',
    'doctor', 'ultrasound', 'scan', 'heartbeat', 'trimester', 'contractions',
    'labor', 'delivery', 'birth', 'nursery', 'names', 'gender', 'cravings'
  ]
  
  const found = pregnancyKeywords.filter(keyword => 
    content.toLowerCase().includes(keyword.toLowerCase())
  )
  
  return found.slice(0, 3) // Limit to 3 keywords max
}

function handleExpansion(): void {
  isExpanded.value = true
  emit('expand')
}

function handleMediaClick(index: number): void {
  emit('mediaView', index)
}

// Lifecycle
onMounted(() => {
  // Check if content needs truncation
  const contentLength = props.content.content?.length || 0
  shouldTruncate.value = contentLength > 200 // Truncate after ~200 characters
})
</script>

<style scoped>
/* Base moment content styling */
.moment-content {
  width: 100%;
}

/* Content type variations */
.moment-content--milestone {
  position: relative;
}

.moment-content--milestone::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #F8BBD0, #E1BEE7, #B2DFDB);
  border-radius: 1rem;
  opacity: 0.1;
  z-index: -1;
}

.moment-content--photo .hero-media {
  margin-bottom: 0.75rem;
}

.moment-content--journal .text-content {
  font-family: 'Georgia', serif;
  line-height: 1.7;
}

/* Header styling */
.content-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

/* Media styling */
.hero-media {
  position: relative;
}

.media-container.single-image {
  max-height: 20rem;
}

.media-grid {
  min-height: 12rem;
}

.media-item {
  min-height: 6rem;
  overflow: hidden;
}

.pregnancy-overlay,
.ultrasound-overlay {
  position: absolute;
  pointer-events: none;
}

.more-overlay {
  backdrop-filter: blur(4px);
}

/* Text content styling */
.text-content {
  line-height: 1.6;
}

.content-text {
  font-size: 1.0625rem; /* 17px - optimized for readability */
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.read-more-btn:hover svg {
  transform: translateY(1px);
}

/* Milestone-specific styling */
.milestone-content h2 {
  color: #7C2D12;
  text-shadow: 0 1px 2px rgba(248, 187, 208, 0.1);
}

.milestone-badge {
  animation: milestone-glow 3s ease-in-out infinite;
}

/* Baby development info */
.baby-development {
  border-left: 4px solid #B2DFDB;
}

.baby-icon {
  animation: gentle-bounce 2s ease-in-out infinite;
}

/* Pregnancy keywords */
.keyword-tag {
  transition: all 0.2s ease;
}

.keyword-tag:hover {
  background: rgba(178, 223, 219, 0.3);
  transform: scale(1.05);
}

/* Progress visualization */
.progress-bar {
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.progress-fill {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Media hover effects */
.single-media:hover img,
.media-item:hover img {
  filter: brightness(1.05);
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .content-text {
    font-size: 1rem; /* 16px on mobile */
  }
  
  .media-container.single-image {
    max-height: 16rem;
  }
  
  .media-grid {
    gap: 0.25rem;
  }
  
  .baby-development {
    padding: 0.75rem;
  }
}

/* Animations */
@keyframes milestone-glow {
  0%, 100% {
    box-shadow: 0 0 0 rgba(248, 187, 208, 0);
  }
  50% {
    box-shadow: 0 0 12px rgba(248, 187, 208, 0.4);
  }
}

@keyframes gentle-bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  .milestone-badge,
  .baby-icon,
  .keyword-tag {
    animation: none !important;
  }
  
  .media-item:hover img,
  .single-media:hover img {
    transform: none !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .keyword-tag {
    border: 1px solid currentColor;
  }
  
  .progress-bar {
    border: 1px solid #000;
  }
  
  .baby-development {
    border: 2px solid #B2DFDB;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .content-text {
    color: #F9FAFB;
  }
  
  .baby-development {
    background: rgba(178, 223, 219, 0.1);
    border-left-color: rgba(178, 223, 219, 0.5);
  }
  
  .progress-bar {
    background: #374151;
  }
}
</style>