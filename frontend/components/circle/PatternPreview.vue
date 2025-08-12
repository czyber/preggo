<template>
  <div class="space-y-4">
    <!-- Pattern Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="text-2xl">{{ pattern.icon }}</div>
        <div>
          <h4 class="font-primary font-medium text-gray-800">{{ pattern.name }}</h4>
          <p class="text-sm text-gray-600">{{ pattern.description }}</p>
        </div>
      </div>
      
      <div class="text-right">
        <div class="text-lg font-medium text-gray-800">
          {{ memberCount }}
        </div>
        <div class="text-xs text-gray-500">
          {{ memberCount === 1 ? 'person' : 'people' }}
        </div>
      </div>
    </div>

    <!-- Member Avatars with Stacking -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Who will see this:</span>
        <button
          v-if="members.length > visibleCount"
          @click="showAll = !showAll"
          class="text-xs text-gentle-mint hover:text-gentle-mint/80 transition-colors"
        >
          {{ showAll ? 'Show less' : `Show all ${memberCount}` }}
        </button>
      </div>
      
      <!-- Avatar Stack -->
      <div class="flex items-center space-x-2">
        <!-- Stacked avatars for first few members -->
        <div class="flex -space-x-2">
          <div
            v-for="(member, index) in visibleMembers"
            :key="member.id"
            class="relative"
            :style="{ zIndex: visibleMembers.length - index }"
          >
            <!-- User avatar or fallback -->
            <div
              v-if="member.user?.profile_image"
              class="w-8 h-8 rounded-full border-2 border-white bg-cover bg-center shadow-sm"
              :style="{ backgroundImage: `url(${member.user.profile_image})` }"
              :title="getUserDisplayName(member.user)"
            ></div>
            
            <!-- Fallback avatar with initials -->
            <div
              v-else
              class="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-xs font-medium text-white shadow-sm"
              :style="{ backgroundColor: getUserAvatarColor(member.user?.id) }"
              :title="getUserDisplayName(member.user)"
            >
              {{ getUserInitials(member.user) }}
            </div>
          </div>
          
          <!-- "More" indicator -->
          <div
            v-if="!showAll && members.length > visibleCount"
            class="w-8 h-8 bg-gray-300 rounded-full border-2 border-white flex items-center justify-center text-xs font-medium text-gray-600 shadow-sm"
            :title="`+${members.length - visibleCount} more people`"
          >
            +{{ members.length - visibleCount }}
          </div>
        </div>
        
        <!-- Animated heart when sharing with loved ones -->
        <div
          v-if="pattern.id === 'just-us' || pattern.id === 'close-family'"
          class="ml-3 text-soft-pink animate-gentle-pulse"
        >
          💝
        </div>
        
        <!-- Celebratory sparkles for big announcements -->
        <div
          v-else-if="pattern.id === 'everyone'"
          class="ml-3 text-gentle-mint animate-gentle-pulse"
        >
          ✨
        </div>
      </div>
      
      <!-- Expanded member list -->
      <div v-if="showAll && members.length > visibleCount" class="mt-4">
        <div class="grid grid-cols-2 gap-2">
          <div
            v-for="member in members.slice(visibleCount)"
            :key="`expanded-${member.id}`"
            class="flex items-center space-x-2 text-sm"
          >
            <!-- Small avatar -->
            <div
              v-if="member.user?.profile_image"
              class="w-5 h-5 rounded-full bg-cover bg-center"
              :style="{ backgroundImage: `url(${member.user.profile_image})` }"
            ></div>
            <div
              v-else
              class="w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium text-white"
              :style="{ backgroundColor: getUserAvatarColor(member.user?.id) }"
            >
              {{ getUserInitials(member.user) }}
            </div>
            
            <!-- Name and relationship -->
            <div class="flex-1 min-w-0">
              <span class="text-gray-700 truncate">
                {{ getUserDisplayName(member.user) }}
              </span>
              <span
                v-if="member.relationship"
                class="text-gray-500 text-xs ml-1"
              >
                ({{ formatRelationship(member.relationship) }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Warm messaging based on circle type -->
    <div class="mt-4 p-3 rounded-lg bg-gradient-to-r from-warm-neutral to-gentle-mint/5 border border-gentle-mint/10">
      <div class="flex items-start space-x-2">
        <div class="flex-shrink-0 text-gentle-mint mt-0.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <p class="text-sm text-gray-600">
          {{ getWarmMessage(pattern) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CirclePattern, FamilyMember } from '~/types/api'
import { getUserAvatarColor, getUserInitials, getUserDisplayName } from '@/utils/avatar'

// Props
interface Props {
  pattern: CirclePattern
  members: FamilyMember[]
  memberCount: number
}

const props = defineProps<Props>()

// State
const showAll = ref(false)
const visibleCount = 5

// Computed
const visibleMembers = computed(() => {
  return showAll.value ? props.members : props.members.slice(0, visibleCount)
})

// Methods
const formatRelationship = (relationship: string): string => {
  // Convert relationship to display format
  const relationshipMap: Record<string, string> = {
    'spouse': 'Spouse',
    'partner': 'Partner',
    'mother': 'Mom',
    'father': 'Dad',
    'sister': 'Sister',
    'brother': 'Brother',
    'grandmother': 'Grandma',
    'grandfather': 'Grandpa',
    'friend': 'Friend',
    'other_family': 'Family'
  }
  return relationshipMap[relationship] || relationship
}

const getWarmMessage = (pattern: CirclePattern): string => {
  // Provide contextual, warm messages for each circle type
  const messages: Record<string, string> = {
    'just-us': "A special moment just for you two. Perfect for sharing intimate thoughts and feelings during this precious time.",
    'close-family': "Your inner circle of love and support. They'll cherish being part of your journey and celebrate every milestone with you.",
    'everyone': "Your whole family network! This is perfect for big announcements and celebrations that everyone should know about.",
    'grandparents': "Grandparents-to-be love staying connected to your pregnancy journey. They'll treasure every update and photo you share.",
    'friends-support': "Your chosen family and support network. These are the friends who will cheer you on through every step of parenthood."
  }
  return messages[pattern.id] || "This circle will be notified about your update and can interact with your post."
}
</script>

<style scoped>
/* Smooth animations for avatar interactions */
.flex.-space-x-2 > div {
  transition: transform 0.2s ease;
}

.flex.-space-x-2 > div:hover {
  transform: translateY(-2px) scale(1.1);
  z-index: 50 !important;
}

/* Gentle pulse animation for special emojis */
@keyframes gentlePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

.animate-gentle-pulse {
  animation: gentlePulse 2s ease-in-out infinite;
}

/* Hover effects for expandable content */
button:hover {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
button:focus-visible {
  outline: 2px solid theme('colors.gentle-mint');
  outline-offset: 2px;
}

/* Avatar border styling */
.border-white {
  border-color: rgba(255, 255, 255, 0.9);
}

/* Shadow enhancements for depth */
.shadow-sm {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
}

/* High contrast support */
@media (prefers-contrast: high) {
  .border-white {
    border-color: white;
    border-width: 3px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .animate-gentle-pulse {
    animation: none;
  }
  
  .flex.-space-x-2 > div:hover {
    transform: none;
  }
  
  button:hover {
    transform: none;
  }
}
</style>