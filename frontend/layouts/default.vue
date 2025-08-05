<template>
  <div class="min-h-screen bg-warm-neutral/20">
    <!-- Navigation Header -->
    <nav class="bg-white/80 backdrop-blur-sm shadow-sm border-b border-warm-neutral/30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-18">
          <div class="flex items-center">
            <NuxtLink to="/" class="flex items-center space-x-3 group">
              <div class="w-10 h-10 bg-gradient-to-br from-soft-pink to-gentle-mint rounded-2xl flex items-center justify-center shadow-sm group-hover:shadow-md transition-all duration-200">
                <Baby class="h-6 w-6 text-white" />
              </div>
              <h1 class="logo text-2xl text-gray-800 group-hover:text-soft-pink transition-colors duration-200">
                preggo
              </h1>
            </NuxtLink>
          </div>
          
          <!-- Navigation Links -->
          <div class="flex items-center space-x-2">
            <NuxtLink
              to="/"
              class="nav-link"
              :class="{ 'nav-link-active': isCurrentRoute('/') }"
            >
              <Home class="h-4 w-4" />
              <span>Home</span>
            </NuxtLink>
            <NuxtLink
              to="/journey"
              class="nav-link"
              :class="{ 'nav-link-active': isCurrentRoute('/journey') }"
            >
              <Heart class="h-4 w-4" />
              <span>Journey</span>
            </NuxtLink>
            <NuxtLink
              to="/milestones"
              class="nav-link"
              :class="{ 'nav-link-active': isCurrentRoute('/milestones') }"
            >
              <Sparkles class="h-4 w-4" />
              <span>Milestones</span>
            </NuxtLink>
            <NuxtLink
              to="/health"
              class="nav-link"
              :class="{ 'nav-link-active': isCurrentRoute('/health') }"
            >
              <Activity class="h-4 w-4" />
              <span>Health</span>
            </NuxtLink>
            <NuxtLink
              to="/family-feed"
              class="nav-link"
              :class="{ 'nav-link-active': isCurrentRoute('/family-feed') || isCurrentRoute('/feed') }"
            >
              <Users class="h-4 w-4" />
              <span>Family</span>
            </NuxtLink>
            
            <!-- User Menu -->
            <div class="ml-4 pl-4 border-l border-warm-neutral/40">
              <UserProfileDropdown />
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="fade-in">
        <slot />
      </div>
    </main>

    <!-- Supportive Footer -->
    <footer class="bg-white/60 backdrop-blur-sm border-t border-warm-neutral/30 mt-16">
      <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <p class="text-sm text-gray-600 font-secondary">
            Supporting you through every step of your pregnancy journey
          </p>
          <div class="flex justify-center items-center space-x-4 mt-4">
            <div class="flex items-center space-x-2 text-gentle-mint">
              <Heart class="h-4 w-4" />
              <span class="text-xs font-medium">Made with care</span>
            </div>
            <div class="flex items-center space-x-2 text-soft-pink">
              <Baby class="h-4 w-4" />
              <span class="text-xs font-medium">For expecting families</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { Baby, Home, Heart, Sparkles, Activity, Users } from 'lucide-vue-next'
import UserProfileDropdown from '~/components/ui/UserProfileDropdown.vue'

// Navigation helper
const route = useRoute()
const isCurrentRoute = (path: string) => {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}

</script>

<style scoped>
/* Navigation link styles */
.nav-link {
  @apply flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-soft-pink/10 transition-all duration-200 font-primary;
}

.nav-link-active {
  @apply text-gray-800 bg-soft-pink/15 shadow-sm;
}

/* Enhanced hover effects */
.nav-link:hover {
  transform: translateY(-1px);
}

/* Smooth transitions for all interactive elements */
a, button {
  transition: all 0.2s ease-in-out;
}

/* Footer styling */
footer {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 243, 224, 0.6) 100%);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .nav-link span {
    @apply sr-only;
  }
  
  .nav-link {
    @apply px-3;
  }
  
  .logo {
    @apply text-xl;
  }
}
</style>