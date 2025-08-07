<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-neutral via-white to-soft-pink/10">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center space-y-4">
        <div class="w-12 h-12 border-4 border-soft-pink/20 border-t-soft-pink rounded-full animate-spin mx-auto"></div>
        <p class="text-gray-600 font-secondary">Loading your family feed...</p>
      </div>
    </div>

    <!-- No Active Pregnancy -->
    <div v-else-if="!currentPregnancy" class="max-w-4xl mx-auto px-4 py-16">
      <BaseCard variant="supportive" class="text-center space-y-6">
        <div class="w-20 h-20 bg-gentle-mint/20 rounded-full flex items-center justify-center mx-auto">
          <Users class="h-10 w-10 text-gentle-mint" />
        </div>
        
        <div class="space-y-4">
          <h1 class="text-3xl font-primary font-semibold text-gray-800">
            Family Feed
          </h1>
          <p class="text-lg text-gray-600 font-secondary max-w-2xl mx-auto">
            Share your pregnancy journey with family and celebrate milestones together!
          </p>
          <p class="text-gray-500 font-secondary">
            You'll need to set up your pregnancy profile first to access your family feed.
          </p>
        </div>

        <div class="space-y-3">
          <BaseButton
            variant="default"
            size="lg"
            @click="router.push('/setup/pregnancy')"
          >
            <Baby class="h-5 w-5 mr-2" />
            Set Up Your Pregnancy
          </BaseButton>
          <BaseButton
            variant="outline"
            size="default"
            @click="router.push('/')"
          >
            Back to Dashboard
          </BaseButton>
        </div>
      </BaseCard>
    </div>

    <!-- Multiple Pregnancies - Let user choose -->
    <div v-else-if="pregnancies.length > 1" class="max-w-4xl mx-auto px-4 py-16">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-primary font-semibold text-gray-800 mb-4">
          Choose Your Family Feed
        </h1>
        <p class="text-gray-600 font-secondary">
          Select which pregnancy's family feed you'd like to view
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <BaseCard
          v-for="pregnancy in pregnancies"
          :key="pregnancy.id"
          variant="default"
          class="hover:shadow-lg transition-all duration-200 cursor-pointer group"
          @click="navigateToFeed(pregnancy.id)"
        >
          <div class="space-y-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-soft-pink/20 rounded-full flex items-center justify-center">
                <Baby class="h-6 w-6 text-soft-pink" />
              </div>
              <div>
                <h3 class="font-primary font-semibold text-gray-800">
                  {{ pregnancy.baby_name || 'Baby' }} {{ pregnancy.last_name || '' }}
                </h3>
                <p class="text-sm text-gray-600">
                  {{ pregnancy.status === 'active' ? 'Active Pregnancy' : pregnancy.status }}
                </p>
              </div>
            </div>

            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Current Week:</span>
                <span class="font-medium text-gray-800">
                  Week {{ pregnancy.pregnancy_details?.current_week || 'N/A' }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Due Date:</span>
                <span class="font-medium text-gray-800">
                  {{ formatDate(pregnancy.due_date) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Family Members:</span>
                <span class="font-medium text-gray-800">
                  {{ pregnancy.family_member_count || 0 }} members
                </span>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-100">
              <BaseButton
                variant="outline"
                size="sm"
                class="w-full group-hover:bg-soft-pink/10 group-hover:border-soft-pink/30"
              >
                <Users class="h-4 w-4 mr-2" />
                View Family Feed
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Users, Baby } from 'lucide-vue-next'
import { usePregnancyStore } from "@/stores/pregnancy"

definePageMeta({
  middleware: 'auth'
})

const router = useRouter()
const pregnancyStore = usePregnancyStore()

// Reactive data
const loading = ref(true)
const pregnancies = computed(() => pregnancyStore.pregnancies)
const currentPregnancy = computed(() => pregnancyStore.currentPregnancy)

// Helper function to format dates
const formatDate = (dateString: string) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Navigate to specific pregnancy feed
const navigateToFeed = (pregnancyId: string) => {
  router.push(`/feed/${pregnancyId}`)
}

// Load pregnancies and handle navigation
onMounted(async () => {
  try {
    await pregnancyStore.fetchPregnancies()
    
    // If user has exactly one pregnancy, redirect directly to its feed
    if (pregnancies.value.length === 1) {
      const pregnancyId = pregnancies.value[0].id
      await router.push(`/feed/${pregnancyId}`)
      return
    }
    
    loading.value = false
  } catch (error) {
    console.error('Error loading pregnancies:', error)
    loading.value = false
  }
})

// Set page meta for SEO
useSeoMeta({
  title: 'Family Feed - Preggo',
  description: 'Share your pregnancy journey with family and celebrate milestones together'
})
</script>
