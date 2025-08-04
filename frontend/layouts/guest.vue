<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-neutral via-white to-soft-pink/20">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-soft-pink/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gentle-mint/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-muted-lavender/5 rounded-full blur-3xl"></div>
    </div>
    
    <!-- Content -->
    <div class="relative flex min-h-screen">
      <!-- Left side - Brand/Welcome message (hidden on mobile) -->
      <div class="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12 text-center">
        <div class="max-w-md space-y-8">
          <!-- Logo/Brand -->
          <div class="space-y-4">
            <h1 class="text-4xl font-logo text-gray-800">
              preggo
            </h1>
            <div class="w-16 h-1 bg-soft-pink mx-auto rounded-full"></div>
          </div>
          
          <!-- Welcome message -->
          <div class="space-y-4">
            <h2 class="text-2xl font-primary text-gray-800 font-medium">
              Your pregnancy journey, beautifully tracked
            </h2>
            <p class="text-gray-600 font-secondary leading-relaxed">
              Join thousands of expecting parents who trust Preggo to track their pregnancy milestones, 
              symptoms, and memories in one beautiful, supportive space.
            </p>
          </div>
          
          <!-- Pregnancy-themed features -->
          <div class="space-y-4 text-left">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gentle-mint/20 rounded-full flex items-center justify-center">
                <span class="text-gentle-mint text-sm">✓</span>
              </div>
              <span class="text-gray-700 font-secondary">Track weekly development</span>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-light-coral/20 rounded-full flex items-center justify-center">
                <span class="text-light-coral text-sm">✓</span>
              </div>
              <span class="text-gray-700 font-secondary">Log symptoms & moods</span>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-soft-pink/20 rounded-full flex items-center justify-center">
                <span class="text-soft-pink text-sm">✓</span>
              </div>
              <span class="text-gray-700 font-secondary">Celebrate milestones</span>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-muted-lavender/20 rounded-full flex items-center justify-center">
                <span class="text-muted-lavender text-sm">✓</span>
              </div>
              <span class="text-gray-700 font-secondary">Expert guidance & tips</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Right side - Auth form -->
      <div class="w-full lg:w-1/2 flex flex-col justify-center items-center p-6 sm:p-12">
        <!-- Mobile logo (visible only on mobile) -->
        <div class="lg:hidden mb-8 text-center">
          <h1 class="text-3xl font-logo text-gray-800 mb-2">preggo</h1>
          <div class="w-12 h-1 bg-soft-pink mx-auto rounded-full"></div>
        </div>
        
        <!-- Auth form container -->
        <div class="w-full max-w-md">
          <slot />
        </div>
        
        <!-- Footer -->
        <div class="mt-8 text-center">
          <p class="text-xs text-gray-500 font-secondary">
            By using Preggo, you agree to our 
            <NuxtLink to="/terms" class="text-soft-pink hover:underline">Terms</NuxtLink> and 
            <NuxtLink to="/privacy" class="text-soft-pink hover:underline">Privacy Policy</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Guest layout for authentication pages
// Provides a welcoming, pregnancy-themed background with branding
</script>

<style scoped>
/* Ensure smooth transitions and proper spacing */
.min-h-screen {
  min-height: 100vh;
  min-height: 100dvh; /* For mobile browsers */
}

/* Gentle animations */
@media (prefers-reduced-motion: no-preference) {
  .space-y-4 > * {
    animation: fadeInUp 0.6s ease-out;
    animation-fill-mode: both;
  }
  
  .space-y-4 > *:nth-child(1) { animation-delay: 0.1s; }
  .space-y-4 > *:nth-child(2) { animation-delay: 0.2s; }
  .space-y-4 > *:nth-child(3) { animation-delay: 0.3s; }
  .space-y-4 > *:nth-child(4) { animation-delay: 0.4s; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .min-h-screen {
    background: linear-gradient(135deg, #FFF3E0 0%, #ffffff 50%, rgba(248, 187, 208, 0.1) 100%);
  }
}
</style>