<template>
  <BaseCard 
    variant="celebration"
    class="relative overflow-hidden group hover:shadow-lg transition-all duration-300"
  >
    <!-- Background decoration -->
    <div class="absolute inset-0 bg-gradient-to-br from-soft-pink/5 via-gentle-mint/5 to-muted-lavender/5"></div>
    <div class="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity duration-300">
      <Users class="h-16 w-16 text-soft-pink" />
    </div>
    
    <div class="relative space-y-6">
      <!-- Header -->
      <div class="flex items-center space-x-4">
        <div class="w-14 h-14 bg-gradient-to-br from-soft-pink/20 to-gentle-mint/20 rounded-2xl flex items-center justify-center shadow-sm">
          <Users class="h-7 w-7 text-soft-pink" />
        </div>
        <div>
          <h3 class="text-xl font-primary font-semibold text-gray-800">
            Family Feed
          </h3>
          <p class="text-gray-600 font-secondary text-sm">
            Share moments with your loved ones
          </p>
        </div>
      </div>

      <!-- Family Stats -->
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center p-3 bg-white/50 rounded-xl">
            <div class="text-2xl font-bold text-soft-pink font-primary">
              {{ familyMemberCount }}
            </div>
            <div class="text-xs text-gray-600 font-secondary">
              Family Members
            </div>
          </div>
          <div class="text-center p-3 bg-white/50 rounded-xl">
            <div class="text-2xl font-bold text-gentle-mint font-primary">
              {{ recentActivityCount }}
            </div>
            <div class="text-xs text-gray-600 font-secondary">
              Recent Updates
            </div>
          </div>
        </div>

        <!-- Recent Family Activity Preview -->
        <div v-if="hasRecentActivity" class="space-y-2">
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <Sparkles class="h-4 w-4 text-muted-lavender" />
            <span class="font-secondary">Recent family activity:</span>
          </div>
          <div class="space-y-1">
            <div class="text-sm text-gray-700 font-secondary">
              💝 Grandma Mary reacted to your week 24 update
            </div>
            <div class="text-sm text-gray-700 font-secondary">
              🎉 Sister Emma commented on your milestone
            </div>
            <div class="text-sm text-gray-500 font-secondary">
              + {{ Math.max(0, recentActivityCount - 2) }} more updates
            </div>
          </div>
        </div>

        <!-- Milestone Celebration Banner -->
        <div v-if="hasUpcomingMilestone" class="p-3 bg-gradient-to-r from-muted-lavender/10 to-light-coral/10 rounded-xl border border-muted-lavender/20">
          <div class="flex items-center space-x-2">
            <Sparkles class="h-4 w-4 text-muted-lavender animate-pulse" />
            <span class="text-sm font-medium text-gray-700 font-secondary">
              Week {{ currentPregnancy?.pregnancy_details?.current_week }} milestone ready to share!
            </span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!hasRecentActivity && !hasUpcomingMilestone" class="text-center py-2">
          <p class="text-sm text-gray-500 font-secondary">
            Start sharing your pregnancy journey with family
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-3">
        <BaseButton 
          variant="default"
          size="default"
          class="w-full group"
          @click="$emit('view-feed')"
        >
          <Users class="h-4 w-4 mr-2 group-hover:scale-110 transition-transform duration-200" />
          View Family Feed
        </BaseButton>
        
        <div class="grid grid-cols-2 gap-2">
          <BaseButton 
            variant="outline"
            size="sm"
            class="text-xs"
            @click="handleShareUpdate"
          >
            <Plus class="h-3 w-3 mr-1" />
            Share Update
          </BaseButton>
          <BaseButton 
            variant="ghost"
            size="sm"
            class="text-xs"
            @click="handleInviteFamily"
          >
            <UserPlus class="h-3 w-3 mr-1" />
            Invite Family
          </BaseButton>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { Users, Sparkles, Plus, UserPlus } from 'lucide-vue-next'
import type { Pregnancy } from '~/types/api'

interface Props {
  currentPregnancy?: Pregnancy | null
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  'view-feed': []
}>()

// Computed properties
const familyMemberCount = computed(() => {
  // This would come from the pregnancy's family data
  return props.currentPregnancy?.family_member_count || 3
})

const recentActivityCount = computed(() => {
  // This would come from recent feed activity
  return Math.floor(Math.random() * 8) + 2 // Mock data
})

const hasRecentActivity = computed(() => {
  return recentActivityCount.value > 0
})

const hasUpcomingMilestone = computed(() => {
  const currentWeek = props.currentPregnancy?.pregnancy_details?.current_week
  if (!currentWeek) return false
  
  // Check if current week is a milestone week (every 4 weeks, plus special weeks)
  const milestoneWeeks = [12, 16, 20, 24, 28, 32, 36, 40]
  return milestoneWeeks.includes(currentWeek)
})

// Event handlers
const handleShareUpdate = () => {
  // Navigate to create post/update
  console.log('Share update clicked')
  // Could emit an event or navigate directly
}

const handleInviteFamily = () => {
  // Navigate to family management
  console.log('Invite family clicked')
  // Could emit an event or navigate directly
}
</script>

<style scoped>
/* Add subtle animations */
.group:hover .animate-pulse {
  animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Gradient text effect */
.text-gradient {
  background: linear-gradient(135deg, #F8BBD0, #B2DFDB);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
