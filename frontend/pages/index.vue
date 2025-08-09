<template>
  <div class="min-h-screen bg-gradient-to-br from-off-white via-pure-white to-warm-gray relative overflow-hidden">
    <!-- Loading State -->
    <div v-if="authLoading" class="flex items-center justify-center min-h-screen">
      <div class="text-center space-y-4">
        <div class="w-12 h-12 border-4 border-blush-rose/20 border-t-blush-rose rounded-full animate-spin mx-auto"></div>
        <p class="text-soft-charcoal font-inter font-normal">Loading your pregnancy journey...</p>
      </div>
    </div>

    <!-- Not authenticated view -->
    <div v-else-if="!isLoggedIn" class="relative px-4 py-12">
      <!-- Floating background shapes for visual appeal -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="floating-shape absolute top-20 left-10 w-32 h-32 bg-warm-gray/30 rounded-full animate-pulse"></div>
        <div class="floating-shape absolute top-40 right-20 w-24 h-24 bg-warm-gray/20 rounded-full animate-pulse" style="animation-delay: 1s;"></div>
        <div class="floating-shape absolute bottom-40 left-1/4 w-16 h-16 bg-warm-gray/25 rounded-full animate-pulse" style="animation-delay: 2s;"></div>
        <div class="floating-shape absolute bottom-20 right-1/3 w-40 h-40 bg-warm-gray/15 rounded-full animate-pulse" style="animation-delay: 0.5s;"></div>
      </div>
      <div class="max-w-6xl mx-auto">
        <!-- Hero Section -->
        <div class="text-center mb-20 pt-8">
          <!-- Logo -->
          <div class="mb-8 animate-fade-in">
            <h1 class="text-4xl md:text-6xl font-inter font-bold text-warm-graphite mb-4 tracking-wide">
              preggo
            </h1>
            <div class="w-20 h-1 bg-gradient-to-r from-blush-rose to-sage-green mx-auto rounded-full"></div>
          </div>
          
          <!-- Hero Content -->
          <div class="max-w-4xl mx-auto space-y-8">
            <!-- Main Headline -->
            <h2 class="text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-inter font-bold text-warm-graphite leading-tight animate-slide-up">
              Your pregnancy journey,
              <span class="bg-gradient-to-r from-blush-rose via-dusty-lavender to-sage-green bg-clip-text text-transparent">
                beautifully shared
              </span>
            </h2>
            
            <!-- Subheadline -->
            <p class="text-lg md:text-xl lg:text-2xl text-soft-charcoal font-inter font-normal max-w-3xl mx-auto leading-relaxed animate-slide-up" style="animation-delay: 0.2s;">
              Connect your family to every precious moment of your pregnancy with private sharing, milestone tracking, and memory creation
            </p>
            
            <!-- Hero Visual Placeholder -->
            <div class="flex justify-center my-8 md:my-12 animate-fade-in" style="animation-delay: 0.4s;">
              <div class="relative hero-visual w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96">
                <!-- Pregnancy silhouette with glow -->
                <div class="absolute inset-0 flex items-center justify-center">
                  <div class="pregnancy-silhouette w-32 h-48 bg-gradient-to-b from-warm-gray/60 to-blush-rose/40 rounded-full relative">
                    <div class="absolute inset-2 bg-gradient-to-b from-warm-gray/40 to-blush-rose/30 rounded-full">
                      <div class="absolute top-8 left-1/2 transform -translate-x-1/2 w-16 h-20 bg-gradient-to-b from-blush-rose/50 to-warm-gray/50 rounded-full"></div>
                    </div>
                  </div>
                </div>
                
                <!-- Family connection circles -->
                <div class="absolute top-4 left-4 w-12 h-12 bg-sage-green/30 rounded-full flex items-center justify-center animate-pulse" style="animation-delay: 1s;">
                  <div class="w-6 h-6 bg-sage-green/50 rounded-full"></div>
                </div>
                <div class="absolute top-8 right-8 w-14 h-14 bg-blush-rose/30 rounded-full flex items-center justify-center animate-pulse" style="animation-delay: 1.5s;">
                  <div class="w-7 h-7 bg-blush-rose/50 rounded-full"></div>
                </div>
                <div class="absolute bottom-12 left-8 w-10 h-10 bg-dusty-lavender/30 rounded-full flex items-center justify-center animate-pulse" style="animation-delay: 2s;">
                  <div class="w-5 h-5 bg-dusty-lavender/50 rounded-full"></div>
                </div>
                <div class="absolute bottom-8 right-12 w-16 h-16 bg-warm-gray/40 rounded-full flex items-center justify-center animate-pulse" style="animation-delay: 0.5s;">
                  <div class="w-8 h-8 bg-warm-gray/60 rounded-full"></div>
                </div>
                
                <!-- Connection lines -->
                <svg class="absolute inset-0 w-full h-full" viewBox="0 0 400 400">
                  <defs>
                    <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#E8B4B8;stop-opacity:0.4" />
                      <stop offset="50%" style="stop-color:#C3B5D1;stop-opacity:0.3" />
                      <stop offset="100%" style="stop-color:#A8C09A;stop-opacity:0.4" />
                    </linearGradient>
                  </defs>
                  <path d="M50 50 Q200 200 350 100" stroke="url(#connectionGradient)" stroke-width="2" fill="none" opacity="0.6"/>
                  <path d="M100 350 Q200 200 50 120" stroke="url(#connectionGradient)" stroke-width="2" fill="none" opacity="0.6"/>
                  <path d="M350 350 Q200 200 350 100" stroke="url(#connectionGradient)" stroke-width="2" fill="none" opacity="0.6"/>
                </svg>
              </div>
            </div>
            
            <!-- CTA Buttons -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-3 animate-slide-up" style="animation-delay: 0.6s;">
              <BaseButton
                size="default"
                variant="default"
                class="w-full sm:w-auto"
                @click="router.push('/auth/signup')"
              >
                Start Your Journey
              </BaseButton>
              <BaseButton
                size="default"
                variant="outline"
                class="w-full sm:w-auto"
                @click="scrollToFeatures"
              >
                See How It Works
              </BaseButton>
            </div>
            
            <!-- Trust indicator -->
            <p class="text-sm text-neutral-gray font-inter font-normal animate-fade-in" style="animation-delay: 0.8s;">
              Join thousands of families sharing their pregnancy journey
            </p>
          </div>
        </div>

        <!-- Features Grid -->
        <div class="features-section grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 mb-12 scroll-mt-20">
          <div class="text-center bg-off-white rounded-rounded shadow-sm hover:shadow-md transition-all duration-300 p-lg hover:-translate-y-1">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-blush-rose/10 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-blush-rose" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-inter font-semibold text-warm-graphite">Share What Matters</h3>
              <p class="text-soft-charcoal font-inter font-normal leading-relaxed">
                Control exactly who sees each update, from ultrasounds to weekly belly photos, with complete privacy control.
              </p>
            </div>
          </div>

          <div class="text-center bg-off-white rounded-rounded shadow-sm hover:shadow-md transition-all duration-300 p-lg hover:-translate-y-1">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-dusty-lavender/10 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-dusty-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-inter font-semibold text-warm-graphite">Celebrate Every Moment</h3>
              <p class="text-soft-charcoal font-inter font-normal leading-relaxed">
                Track and share first kicks, heartbeats, and every magical milestone with your loved ones.
              </p>
            </div>
          </div>

          <div class="text-center bg-off-white rounded-rounded shadow-sm hover:shadow-md transition-all duration-300 p-lg hover:-translate-y-1">
            <div class="space-y-4">
              <div class="w-16 h-16 bg-sage-green/10 rounded-full flex items-center justify-center mx-auto">
                <svg class="h-8 w-8 text-sage-green" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-inter font-semibold text-warm-graphite">Keep Everyone Connected</h3>
              <p class="text-soft-charcoal font-inter font-normal leading-relaxed">
                Let grandparents, siblings, and friends follow along at your comfort level with safe, private sharing.
              </p>
            </div>
          </div>
        </div>

        <!-- CTA Section -->
        <div class="text-center space-y-8 bg-off-white/80 backdrop-blur-sm rounded-2xl p-8 md:p-12 shadow-sm border border-light-gray/30">
          <div class="space-y-6">
            <h3 class="text-2xl md:text-3xl font-inter font-semibold text-warm-graphite leading-tight">
              Ready to start your beautiful pregnancy journey?
            </h3>
            <p class="text-lg text-soft-charcoal font-inter font-normal max-w-2xl mx-auto leading-relaxed">
              Join thousands of families already sharing their special moments
            </p>
            <BaseButton
              size="lg"
              class="bg-blush-rose hover:bg-blush-rose/90 text-warm-graphite font-semibold px-8 py-3 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 font-inter"
              @click="router.push('/auth/signup')"
            >
              Create Your Free Account
            </BaseButton>
            <p class="text-sm text-neutral-gray font-inter font-normal">
              Already have an account?
              <NuxtLink
                to="/auth/login"
                class="font-medium text-blush-rose hover:text-blush-rose/80 transition-colors ml-1 underline-offset-4 hover:underline"
              >
                Sign in here
              </NuxtLink>
            </p>
          </div>

          <!-- Trust indicators -->
          <div class="max-w-2xl mx-auto pt-6 border-t border-light-gray/50">
            <p class="text-xs text-neutral-gray font-inter font-medium mb-6 uppercase tracking-wide">Trusted by expecting families worldwide</p>
            <div class="flex items-center justify-center space-x-10">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-neutral-gray" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span class="text-xs font-inter font-medium text-soft-charcoal">HIPAA Compliant</span>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-sage-green" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <span class="text-xs font-inter font-medium text-soft-charcoal">SSL Encrypted</span>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-dusty-lavender" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span class="text-xs font-inter font-medium text-soft-charcoal">4.9★ Rating</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Authenticated view -->
    <div v-else class="px-4 py-8 bg-warm-gray/20 min-h-screen">
      <div class="max-w-6xl mx-auto">
        <!-- Welcome Header -->
        <div class="mb-8 bg-off-white rounded-2xl p-6 shadow-sm border border-light-gray/30">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div class="mb-4 sm:mb-0">
              <h1 class="text-3xl font-inter font-semibold text-warm-graphite leading-tight">
                Welcome back, {{ currentUser?.full_name || currentUser?.email?.split('@')[0] || 'Beautiful' }}!
              </h1>
              <p class="text-soft-charcoal font-inter font-normal mt-2">Here's your pregnancy journey overview</p>
            </div>
            <!-- <BaseButton
              variant="outline"
              size="default"
              @click="auth.signOut()"
            >
              Sign Out
            </BaseButton> -->
          </div>
        </div>

        <!-- Setup reminder - only show if user doesn't have any active pregnancies -->
        <div
          v-if="!hasActivePregnancy"
          class="mb-8 bg-off-white rounded-2xl p-6 shadow-sm border border-dusty-lavender/30"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-dusty-lavender/20 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-dusty-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-inter font-semibold text-warm-graphite mb-2">Complete your profile setup</h3>
              <p class="text-soft-charcoal font-inter font-normal mb-4">Let's finish setting up your pregnancy profile to get personalized tracking and support.</p>
              <BaseButton
                class="bg-blush-rose hover:bg-blush-rose/90 text-warm-graphite font-semibold px-4 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 font-inter"
                size="sm"
                @click="router.push('/setup/pregnancy')"
              >
                Complete Setup
              </BaseButton>
            </div>
          </div>
        </div>

        <!-- Pregnancy Dashboard - show if user has active pregnancies -->
        <div v-else class="space-y-6">
          <!-- Main Dashboard Card -->
          <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
            <!-- Unified Pregnancy Dashboard -->
            <PregnancyDashboard
              :current-week="currentPregnancyDetails?.current_week"
              :current-day="currentPregnancyDetails?.current_day"
              :trimester="currentPregnancyDetails?.trimester"
              :due-date="currentPregnancyDetails?.due_date"
              :pregnancy-day="currentPregnancyDetails?.current_day ? (currentPregnancyDetails?.current_week * 7) + currentPregnancyDetails?.current_day : null"
            />
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Create Update Card -->
            <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
              <CreateUpdateCard 
                :current-pregnancy-week="currentPregnancyDetails?.current_week"
                :current-mood="currentPregnancyDetails?.current_mood"
              />
            </div>
            
            <!-- Family Feed Card -->
            <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
              <FamilyFeedCard 
                :current-pregnancy="pregnancyStore.currentPregnancy"
                @view-feed="handleViewFamilyFeed"
              />
            </div>
          </div>

          <!-- Secondary Dashboard Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
              <WeeklyInfoCard 
                :current-week="currentPregnancyDetails?.current_week"
              />
            </div>
            <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
              <QuickActionsCard 
                @log-symptoms="handleLogSymptoms"
                @add-photo="handleAddPhoto"
                @schedule-appointment="handleScheduleAppointment"
                @track-weight="handleTrackWeight"
                @view-family-feed="handleViewFamilyFeed"
              />
            </div>
            <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
              <MilestonesCard 
                :current-week="currentPregnancyDetails?.current_week"
              />
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="bg-off-white rounded-2xl shadow-sm border border-light-gray/30 overflow-hidden">
            <RecentActivityCard 
              :activities="recentActivities"
              @view-all="handleViewAllActivity"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePregnancyStore } from "@/stores/pregnancy";
import PregnancyDashboard from "@/components/pregnancy/PregnancyDashboard.vue";
import WeeklyInfoCard from "@/components/pregnancy/WeeklyInfoCard.vue";
import QuickActionsCard from "@/components/pregnancy/QuickActionsCard.vue";
import MilestonesCard from "@/components/pregnancy/MilestonesCard.vue";
import RecentActivityCard from "@/components/pregnancy/RecentActivityCard.vue";
import CreateUpdateCard from "@/components/pregnancy/CreateUpdateCard.vue";
import FamilyFeedCard from "@/components/pregnancy/FamilyFeedCard.vue";

const router = useRouter()

// Use unified auth composable
const auth = useAuth()
const pregnancyStore = usePregnancyStore()

// Reactive data
const currentUser = computed(() => auth.userProfile.value)
const isLoggedIn = computed(() => auth.isLoggedIn.value)
const authLoading = computed(() => auth.loading.value)

// Pregnancy data
const hasActivePregnancy = computed(() => {
  return pregnancyStore.activePregnancies.length > 0
})

const currentPregnancyDetails = computed(() => {
  return pregnancyStore.currentPregnancy?.pregnancy_details || null
})

// Mock recent activities (could be from a store in the future)
const recentActivities = ref([])

// Smooth scroll to features section
const scrollToFeatures = () => {
  const featuresSection = document.querySelector('.features-section')
  if (featuresSection) {
    featuresSection.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
}

// Event handlers for quick actions
const handleLogSymptoms = () => {
  console.log('Navigate to log symptoms')
  // TODO: Navigate to symptoms logging page
}

const handleAddPhoto = () => {
  console.log('Navigate to add photo')
  // TODO: Navigate to photo upload page
}

const handleScheduleAppointment = () => {
  console.log('Navigate to schedule appointment')
  // TODO: Navigate to appointment scheduling page
}

const handleTrackWeight = () => {
  console.log('Navigate to track weight')
  // TODO: Navigate to weight tracking page
}

const handleViewAllActivity = () => {
  console.log('Navigate to all activity')
  // TODO: Navigate to activity feed page
}

const handleViewFamilyFeed = () => {
  if (pregnancyStore.currentPregnancy?.id) {
    router.push(`/feed/${pregnancyStore.currentPregnancy.id}`)
  } else {
    router.push('/family-feed')
  }
}

// Load pregnancies when user is logged in
watch(isLoggedIn, async (loggedIn) => {
  if (loggedIn && !pregnancyStore.pregnancies.length) {
    await pregnancyStore.fetchPregnancies()
  }
}, { immediate: true })
</script>

<style scoped>
/* Enhanced animations for the landing page */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out forwards;
}

/* Floating shapes animation */
@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-10px) rotate(1deg);
  }
  66% {
    transform: translateY(5px) rotate(-1deg);
  }
}

/* Enhanced pulse animation for hero visual */
@keyframes pregnancy-glow {
  0%, 100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
}

.pregnancy-silhouette {
  animation: pregnancy-glow 3s ease-in-out infinite;
}

/* Feature cards subtle accent highlights on hover */
.features-section > div:hover .w-16 {
  background-color: #F5F4F2; /* warm-gray slightly darker */
}

.features-section > div:nth-child(1):hover svg {
  color: #A8C09A; /* sage-green accent */
}

.features-section > div:nth-child(2):hover svg {
  color: #E8B4B8; /* blush-rose accent */
}

.features-section > div:nth-child(3):hover svg {
  color: #C3B5D1; /* dusty-lavender accent */
}

/* Gradient text effect */
.gradient-text {
  background: linear-gradient(135deg, #F8BBD0, #E1BEE7, #B2DFDB);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .hero-visual {
    width: 16rem; /* 256px */
    height: 16rem;
  }
  
  .floating-shape {
    display: none;
  }
  
  /* Prevent horizontal overflow on mobile */
  .pregnancy-silhouette {
    max-width: 100%;
  }
}

/* Smooth scroll behavior */
html {
  scroll-behavior: smooth;
}

/* Enhanced card animations */
.card-enter-active,
.card-leave-active {
  transition: all 0.3s ease;
}

.card-enter-from,
.card-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>
