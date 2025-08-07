<template>
  <DropdownMenu v-if="isAuthenticated" class="w-64 sm:w-56">
    <template #trigger="{ toggle, isOpen }">
      <button
        @click="toggle"
        :class="cn(
          'flex items-center space-x-2 p-2 rounded-xl hover:bg-soft-pink/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-soft-pink/50',
          isOpen && 'bg-soft-pink/15'
        )"
        :aria-expanded="isOpen"
        aria-haspopup="true"
        aria-label="User menu"
      >
        <UserAvatar
          :user="userForAvatar"
          size="sm"
          class="ring-2 ring-white shadow-sm"
        />
        <div class="hidden sm:block text-left">
          <div class="text-sm font-medium text-gray-800 truncate max-w-32">
            {{ displayName }}
          </div>
          <div class="text-xs text-gray-500 truncate max-w-32">
            {{ displayEmail }}
          </div>
        </div>
        <ChevronDown 
          :class="cn(
            'h-4 w-4 text-gray-500 transition-transform duration-200',
            isOpen && 'rotate-180'
          )"
        />
      </button>
    </template>

    <template #default="{ close }">
      <!-- User Info Header -->
      <div class="px-4 py-3 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <UserAvatar
            :user="userForAvatar"
            size="md"
            class="ring-2 ring-soft-pink/20"
          />
          <div class="min-w-0 flex-1">
            <div class="text-sm font-semibold text-gray-900 truncate">
              {{ displayName }}
            </div>
            <div class="text-xs text-gray-500 truncate">
              {{ displayEmail }}
            </div>
          </div>
        </div>
      </div>

      <!-- Menu Items -->
      <div class="py-1">
        <DropdownMenuItem
          @click="() => { handleViewProfile(); close(); }"
          class="flex items-center space-x-3"
        >
          <UserIcon class="h-4 w-4 text-gray-500" />
          <span>View Profile</span>
        </DropdownMenuItem>
        
        <DropdownMenuItem
          @click="() => { handleAccountSettings(); close(); }"
          class="flex items-center space-x-3"
        >
          <Settings class="h-4 w-4 text-gray-500" />
          <span>Account Settings</span>
        </DropdownMenuItem>
        
        <div class="border-t border-gray-200 my-1"></div>
        
        <DropdownMenuItem
          @click="() => { handleSignOut(); close(); }"
          :disabled="loading"
          class="flex items-center space-x-3 text-red-600 hover:bg-red-50 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <LogOut class="h-4 w-4" />
          <span>{{ loading ? 'Signing out...' : 'Sign Out' }}</span>
        </DropdownMenuItem>
      </div>
    </template>
  </DropdownMenu>
  
  <!-- Fallback for unauthenticated users -->
  <button
    v-else
    class="flex items-center space-x-2 p-2 rounded-xl hover:bg-soft-pink/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-soft-pink/50"
    @click="handleSignIn"
    aria-label="Sign in"
  >
    <div class="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
      <UserIcon class="h-4 w-4 text-gray-600" />
    </div>
    <span class="hidden sm:block text-sm font-medium text-gray-600">Sign In</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChevronDown, User as UserIcon, Settings, LogOut } from 'lucide-vue-next'
import { cn } from "./utils"
import DropdownMenu from "@/components/ui/DropdownMenu.vue";
import DropdownMenuItem from "@/components/ui/DropdownMenuItem.vue";
import UserAvatar from "@/components/ui/UserAvatar.vue";

const { userProfile, signOut, loading, isAuthenticated } = useAuth()
const router = useRouter()

// Convert userProfile to UserAvatar compatible format
const userForAvatar = computed(() => {
  if (!userProfile.value) return undefined
  
  return {
    id: userProfile.value.id,
    email: userProfile.value.email,
    first_name: userProfile.value.first_name,
    last_name: userProfile.value.last_name,
  }
})

const displayName = computed(() => {
  if (!userProfile.value) return 'User'
  
  // Use display_name if available, otherwise construct from first/last name
  if (userProfile.value.first_name) {
    return userProfile.value.first_name
  }
  
  const firstName = userProfile.value.first_name
  const lastName = userProfile.value.last_name
  
  if (firstName && lastName) {
    return `${firstName} ${lastName}`
  } else if (firstName) {
    return firstName
  } else if (lastName) {
    return lastName
  }
  
  // Fallback to email username
  return userProfile.value.email?.split('@')[0] || 'User'
})

const displayEmail = computed(() => {
  return userProfile.value?.email || ''
})

const handleViewProfile = () => {
  // Navigate to profile page when it exists
  // For now, just log the action
  console.log('Navigate to profile page')
  // router.push('/profile')
}

const handleAccountSettings = () => {
  // Navigate to settings page when it exists
  // For now, just log the action
  console.log('Navigate to account settings')
  // router.push('/settings')
}

const handleSignOut = async () => {
  try {
    await signOut()
    // Redirect to home page after logout
    router.push('/')
  } catch (error) {
    console.error('Sign out error:', error)
  }
}

const handleSignIn = () => {
  // Navigate to sign in page when it exists
  // For now, just log the action
  console.log('Navigate to sign in page')
  // router.push('/auth/signin')
}
</script>
