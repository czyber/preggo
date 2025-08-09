<template>
  <div 
    v-if="shouldShowPrompt"
    class="memory-prompt relative overflow-hidden transition-all duration-500 ease-out"
    :class="getPromptClass()"
    role="complementary"
    :aria-label="`${getPromptTitle()} suggestion`"
  >
    <!-- Gentle Background Pattern -->
    <div class="prompt-background absolute inset-0 opacity-5" :aria-hidden="true">
      <div class="pattern-overlay" :class="getPatternClass()" />
    </div>

    <!-- Main Content -->
    <div class="prompt-content relative z-10 p-4 sm:p-5">
      <!-- Header with Icon -->
      <div class="prompt-header flex items-start gap-3 mb-3">
        <div class="prompt-icon flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-soft-pink/20 to-gentle-mint/20 flex items-center justify-center">
          <span class="text-xl" :aria-hidden="true">{{ getPromptEmoji() }}</span>
        </div>
        
        <div class="flex-1">
          <h3 class="prompt-title text-base font-semibold text-gray-800 mb-1 font-primary">
            {{ getPromptTitle() }}
          </h3>
          <p class="prompt-subtitle text-sm text-gray-600 leading-relaxed">
            {{ getPromptDescription() }}
          </p>
        </div>
        
        <!-- Dismiss Button -->
        <button
          @click="handleDismiss"
          class="dismiss-btn flex-shrink-0 p-1 hover:bg-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
          :aria-label="'Dismiss this suggestion'"
        >
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Prompt-Specific Content -->
      <div class="prompt-body mb-4">
        <!-- Weekly Photo Prompt -->
        <div v-if="promptType === 'photo'" class="photo-prompt">
          <div class="flex items-center gap-2 mb-2 text-sm text-gray-700">
            <span class="week-indicator px-2 py-1 bg-soft-pink/20 text-soft-pink-dark rounded text-xs font-medium">
              Week {{ pregnancyWeek }}
            </span>
            <span class="next-photo-text">Your weekly photo awaits</span>
          </div>
          <p class="encouragement-text text-sm text-gray-600 leading-relaxed">
            Document this amazing week of your journey. Your family loves seeing how baby is growing!
          </p>
        </div>

        <!-- Milestone Celebration -->
        <div v-else-if="promptType === 'milestone'" class="milestone-prompt">
          <div class="milestone-badge flex items-center gap-2 mb-2">
            <span class="milestone-label px-3 py-1 bg-gradient-to-r from-gentle-mint to-soft-pink text-white rounded-full text-sm font-medium">
              ✨ Milestone Week
            </span>
          </div>
          <p class="milestone-description text-sm text-gray-600 leading-relaxed mb-2">
            You've reached week {{ pregnancyWeek }} - {{ getMilestoneDescription() }}
          </p>
          <div class="celebration-hint text-xs text-gentle-mint-dark italic">
            This is a perfect moment to celebrate with your family! 🎉
          </div>
        </div>

        <!-- Family Memory Opportunity -->
        <div v-else-if="promptType === 'family'" class="family-prompt">
          <p class="family-description text-sm text-gray-600 leading-relaxed mb-2">
            Ask your family to share their favorite moment from this week
          </p>
          <div class="family-preview flex items-center gap-2">
            <div class="family-avatars flex -space-x-1">
              <div
                v-for="n in Math.min(familyCount, 3)"
                :key="n"
                class="w-6 h-6 bg-muted-lavender/30 border-2 border-white rounded-full flex items-center justify-center text-xs"
              >
                👤
              </div>
            </div>
            <span class="family-text text-xs text-gray-500">
              {{ familyCount }} family {{ familyCount === 1 ? 'member' : 'members' }} waiting to share
            </span>
          </div>
        </div>

        <!-- Reflection Prompt -->
        <div v-else-if="promptType === 'reflection'" class="reflection-prompt">
          <p class="reflection-question text-sm text-gray-600 leading-relaxed mb-2">
            {{ getReflectionQuestion() }}
          </p>
          <div class="reflection-hint text-xs text-muted-lavender-dark italic">
            These quiet moments become precious memories 💭
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="prompt-actions flex items-center gap-2 flex-wrap">
        <button
          @click="handleAccept"
          class="action-btn action-btn--primary flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-soft-pink to-gentle-mint text-white rounded-full text-sm font-medium hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-soft-pink focus:ring-offset-2"
          :aria-label="getAcceptAriaLabel()"
        >
          <span class="btn-icon">{{ getActionIcon() }}</span>
          <span class="btn-text">{{ getActionText() }}</span>
        </button>
        
        <button
          @click="handleDefer"
          class="action-btn action-btn--secondary px-3 py-2 text-gray-600 hover:text-gray-800 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2 rounded"
          :aria-label="getDeferAriaLabel()"
        >
          {{ getDeferText() }}
        </button>
      </div>
    </div>

    <!-- Gentle Glow Effect -->
    <div 
      v-if="isHighlighted"
      class="glow-effect absolute inset-0 bg-gradient-to-r from-soft-pink/10 via-gentle-mint/10 to-muted-lavender/10 rounded-lg blur-sm -z-10 animate-pulse"
      :aria-hidden="true"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

type PromptType = 'photo' | 'milestone' | 'family' | 'reflection'

interface Props {
  promptType: PromptType
  pregnancyWeek: number
  lastActivity: Date
  userEnergyLevel?: 'high' | 'medium' | 'low'
  familyCount?: number
  isHighlighted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  userEnergyLevel: 'medium',
  familyCount: 0,
  isHighlighted: false
})

const emit = defineEmits<{
  accept: [action: string]
  dismiss: []
  defer: []
}>()

// Local state
const shouldShowPrompt = ref(true)
const timeOfDay = ref<'morning' | 'afternoon' | 'evening' | 'night'>('morning')

// Computed properties
const isOptimalTime = computed(() => {
  switch (props.promptType) {
    case 'photo':
      return timeOfDay.value === 'morning' || timeOfDay.value === 'afternoon'
    case 'milestone':
      return timeOfDay.value === 'morning'
    case 'family':
      return timeOfDay.value === 'evening'
    case 'reflection':
      return timeOfDay.value === 'evening' || timeOfDay.value === 'night'
    default:
      return true
  }
})

// Methods
function getPromptClass(): string {
  const baseClass = 'bg-white border-2 border-dashed rounded-lg shadow-sm hover:shadow-md'
  
  switch (props.promptType) {
    case 'photo':
      return `${baseClass} border-soft-pink/30 hover:border-soft-pink/50`
    case 'milestone':
      return `${baseClass} border-gentle-mint/40 hover:border-gentle-mint/60 bg-gradient-to-br from-gentle-mint/5 to-soft-pink/5`
    case 'family':
      return `${baseClass} border-muted-lavender/30 hover:border-muted-lavender/50`
    case 'reflection':
      return `${baseClass} border-gray-300/50 hover:border-gray-400/60`
    default:
      return baseClass
  }
}

function getPatternClass(): string {
  switch (props.promptType) {
    case 'photo':
      return 'bg-photo-pattern'
    case 'milestone':
      return 'bg-celebration-pattern'
    case 'family':
      return 'bg-heart-pattern'
    case 'reflection':
      return 'bg-star-pattern'
    default:
      return ''
  }
}

function getPromptEmoji(): string {
  switch (props.promptType) {
    case 'photo':
      return '📸'
    case 'milestone':
      return '🎉'
    case 'family':
      return '💝'
    case 'reflection':
      return '💭'
    default:
      return '✨'
  }
}

function getPromptTitle(): string {
  switch (props.promptType) {
    case 'photo':
      return 'Your weekly photo awaits'
    case 'milestone':
      return 'Time to celebrate!'
    case 'family':
      return 'Create a family memory'
    case 'reflection':
      return 'A moment for reflection'
    default:
      return 'Special moment'
  }
}

function getPromptDescription(): string {
  switch (props.promptType) {
    case 'photo':
      return `Capture week ${props.pregnancyWeek} of your beautiful journey`
    case 'milestone':
      return `Week ${props.pregnancyWeek} is a special milestone in your pregnancy`
    case 'family':
      return 'Invite your loved ones to share in this precious time'
    case 'reflection':
      return 'Take a quiet moment to connect with your experience'
    default:
      return 'Something special is happening'
  }
}

function getMilestoneDescription(): string {
  const milestones: Record<number, string> = {
    4: "baby's heart starts beating",
    8: "baby has tiny arms and legs",
    12: "end of first trimester",
    16: "baby can hear your voice",
    20: "halfway to meeting baby",
    24: "baby's eyes can open",
    28: "third trimester begins", 
    32: "baby's bones are hardening",
    36: "baby is considered full-term soon",
    40: "your due date has arrived"
  }
  
  // Find closest milestone
  const weeks = Object.keys(milestones).map(Number)
  const closestWeek = weeks.reduce((prev, curr) => 
    Math.abs(curr - props.pregnancyWeek) < Math.abs(prev - props.pregnancyWeek) ? curr : prev
  )
  
  return milestones[closestWeek] || "baby is growing strong"
}

function getReflectionQuestion(): string {
  const questions = [
    "How are you feeling about becoming a parent?",
    "What are you most excited about this week?",
    "What would you like to tell your baby right now?",
    "How has your body been feeling lately?",
    "What are you grateful for in this moment?",
    "What hopes do you have for your growing family?"
  ]
  
  // Use week to deterministically select a question
  return questions[props.pregnancyWeek % questions.length]
}

function getActionIcon(): string {
  switch (props.promptType) {
    case 'photo':
      return '📷'
    case 'milestone':
      return '🎈'
    case 'family':
      return '💌'
    case 'reflection':
      return '✍️'
    default:
      return '✨'
  }
}

function getActionText(): string {
  switch (props.promptType) {
    case 'photo':
      return 'Take Photo'
    case 'milestone':
      return 'Share Joy'
    case 'family':
      return 'Ask Family'
    case 'reflection':
      return 'Write Thoughts'
    default:
      return 'Continue'
  }
}

function getDeferText(): string {
  switch (props.userEnergyLevel) {
    case 'low':
      return 'Rest for now'
    case 'high':
      return 'Maybe later'
    default:
      return 'Save for later'
  }
}

function getAcceptAriaLabel(): string {
  return `${getActionText()} for ${getPromptTitle().toLowerCase()}`
}

function getDeferAriaLabel(): string {
  return `Defer ${getPromptTitle().toLowerCase()} for later`
}

// Event handlers
function handleAccept(): void {
  const actions = {
    photo: 'take_photo',
    milestone: 'celebrate',
    family: 'ask_family',
    reflection: 'write_reflection'
  }
  
  emit('accept', actions[props.promptType])
}

function handleDismiss(): void {
  shouldShowPrompt.value = false
  setTimeout(() => emit('dismiss'), 300) // Allow animation to complete
}

function handleDefer(): void {
  shouldShowPrompt.value = false
  setTimeout(() => emit('defer'), 300)
}

// Lifecycle
onMounted(() => {
  // Determine time of day
  const hour = new Date().getHours()
  if (hour < 12) timeOfDay.value = 'morning'
  else if (hour < 17) timeOfDay.value = 'afternoon'
  else if (hour < 21) timeOfDay.value = 'evening'
  else timeOfDay.value = 'night'
})
</script>

<style scoped>
/* Memory prompt base styling */
.memory-prompt {
  margin: 1.5rem 0;
  max-width: 100%;
  position: relative;
  animation: gentle-appear 0.6s ease-out;
}

/* Background patterns (subtle) */
.prompt-background {
  background-size: 20px 20px;
}

.bg-photo-pattern {
  background-image: radial-gradient(circle, #F8BBD0 1px, transparent 1px);
}

.bg-celebration-pattern {
  background-image: 
    radial-gradient(circle at 25% 25%, #B2DFDB 2px, transparent 2px),
    radial-gradient(circle at 75% 75%, #E1BEE7 1px, transparent 1px);
}

.bg-heart-pattern {
  background-image: 
    radial-gradient(circle at 50% 50%, #E1BEE7 1px, transparent 1px);
  background-size: 15px 15px;
}

.bg-star-pattern {
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(156, 163, 175, 0.3) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(156, 163, 175, 0.2) 1px, transparent 1px);
}

/* Prompt content */
.prompt-content {
  position: relative;
}

.prompt-icon {
  animation: gentle-float 3s ease-in-out infinite;
}

.prompt-title {
  color: #374151;
  line-height: 1.3;
}

.prompt-subtitle {
  line-height: 1.5;
}

/* Dismiss button */
.dismiss-btn {
  opacity: 0.6;
  transition: all 0.2s ease;
}

.dismiss-btn:hover {
  opacity: 1;
  background: rgba(243, 244, 246, 0.8);
}

/* Prompt-specific styling */
.week-indicator {
  backdrop-filter: blur(4px);
}

.milestone-badge {
  margin-bottom: 0.5rem;
}

.milestone-label {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.family-avatars {
  padding: 0.25rem 0;
}

.celebration-hint,
.reflection-hint {
  font-style: italic;
  font-size: 0.75rem;
}

/* Action buttons */
.prompt-actions {
  gap: 0.75rem;
}

.action-btn {
  min-height: 44px; /* Pregnancy-aware touch targets */
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.action-btn--primary {
  box-shadow: 0 2px 4px rgba(248, 187, 208, 0.15);
}

.action-btn--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(248, 187, 208, 0.25);
}

.action-btn--primary:active {
  transform: translateY(0);
}

.action-btn--secondary {
  position: relative;
}

.action-btn--secondary:hover {
  background: rgba(243, 244, 246, 0.6);
}

/* Glow effect */
.glow-effect {
  animation: gentle-glow 3s ease-in-out infinite;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .memory-prompt {
    margin: 1rem 0;
  }
  
  .prompt-content {
    padding: 1rem;
  }
  
  .prompt-header {
    gap: 0.75rem;
  }
  
  .prompt-icon {
    width: 2rem;
    height: 2rem;
  }
  
  .prompt-title {
    font-size: 0.9375rem;
  }
  
  .prompt-subtitle {
    font-size: 0.8125rem;
  }
  
  .prompt-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
}

/* Animations */
@keyframes gentle-appear {
  from {
    opacity: 0;
    transform: translateY(15px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes gentle-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

@keyframes gentle-glow {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .memory-prompt {
    border-width: 3px;
    border-style: solid;
    border-color: #000;
  }
  
  .action-btn--primary {
    background: #000;
    color: #fff;
  }
  
  .action-btn--secondary {
    border: 2px solid #000;
  }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
  .memory-prompt,
  .prompt-icon,
  .glow-effect,
  .action-btn {
    animation: none !important;
  }
  
  .action-btn--primary:hover {
    transform: none;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .memory-prompt {
    background: rgba(31, 41, 55, 0.95);
    border-color: rgba(75, 85, 99, 0.5);
  }
  
  .prompt-title {
    color: #F9FAFB;
  }
  
  .prompt-subtitle {
    color: #D1D5DB;
  }
  
  .dismiss-btn {
    color: #9CA3AF;
  }
  
  .dismiss-btn:hover {
    background: rgba(55, 65, 81, 0.8);
    color: #F3F4F6;
  }
  
  .action-btn--secondary {
    color: #D1D5DB;
  }
  
  .action-btn--secondary:hover {
    background: rgba(55, 65, 81, 0.6);
    color: #F9FAFB;
  }
}

/* Print styles */
@media print {
  .memory-prompt {
    border: 1px solid #ccc !important;
    box-shadow: none !important;
    break-inside: avoid;
  }
  
  .action-btn {
    display: none !important;
  }
  
  .dismiss-btn {
    display: none !important;
  }
}
</style>