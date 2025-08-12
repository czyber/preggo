<template>
  <div class="min-h-screen bg-gradient-to-br from-warm-neutral via-white to-soft-pink/10">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center space-y-4">
        <div class="w-12 h-12 border-4 border-soft-pink/20 border-t-soft-pink rounded-full animate-spin mx-auto"></div>
        <p class="text-gray-600 font-secondary">Loading your invitation...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center min-h-screen p-4">
      <BaseCard variant="supportive" class="max-w-md w-full text-center">
        <div class="space-y-4">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <AlertCircle class="h-8 w-8 text-red-500" />
          </div>
          <div>
            <h1 class="text-xl font-primary font-semibold text-gray-800 mb-2">
              Invalid Invitation
            </h1>
            <p class="text-gray-600 font-secondary">
              {{ error }}
            </p>
          </div>
          <BaseButton
            @click="router.push('/auth/signup')"
            variant="outline"
            class="w-full"
          >
            Sign Up Anyway
          </BaseButton>
        </div>
      </BaseCard>
    </div>

    <!-- Success State - Invite Details -->
    <div v-else-if="invite" class="flex items-center justify-center min-h-screen p-4">
      <BaseCard variant="supportive" class="max-w-lg w-full">
        <div class="text-center space-y-6">
          <!-- Celebration Header -->
          <div class="space-y-4">
            <div class="relative">
              <Avatar 
                :src="invite.inviter.profile_image" 
                size="xl" 
                class="mx-auto ring-4 ring-gentle-mint/20" 
              />
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-soft-pink rounded-full flex items-center justify-center">
                <Heart class="h-4 w-4 text-white fill-current" />
              </div>
            </div>
            
            <div>
              <h1 class="text-3xl font-primary font-bold text-gray-800 mb-2">
                You're Invited! 🎉
              </h1>
              <p class="text-lg text-gray-600 font-secondary">
                <strong>{{ invite.inviter.first_name }} {{ invite.inviter.last_name }}</strong> wants to share their pregnancy journey with you
              </p>
            </div>
          </div>

          <!-- Pregnancy Context Card -->
          <div class="bg-gradient-to-r from-soft-pink/10 to-gentle-mint/10 rounded-xl p-6 border border-gentle-mint/20">
            <div class="flex items-center justify-center space-x-3 mb-4">
              <Baby class="h-6 w-6 text-soft-pink" />
              <h2 class="text-xl font-semibold text-gray-800">
                {{ invite.baby_name || 'Baby' }} {{ invite.inviter.last_name }}'s Journey
              </h2>
            </div>
            
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div class="text-center p-3 bg-white/60 rounded-lg">
                <div class="text-2xl font-bold text-soft-pink mb-1">{{ invite.current_week || '?' }}</div>
                <div class="text-gray-600">Weeks Along</div>
              </div>
              <div class="text-center p-3 bg-white/60 rounded-lg">
                <div class="text-lg font-semibold text-gentle-mint mb-1">
                  {{ invite.due_date ? formatDueDate(invite.due_date) : 'TBD' }}
                </div>
                <div class="text-gray-600">Due Date</div>
              </div>
            </div>

            <!-- Personal Message -->
            <div v-if="invite.message" class="mt-4 p-4 bg-white/80 rounded-lg border border-gentle-mint/10">
              <p class="text-gray-700 italic">
                "{{ invite.message }}"
              </p>
            </div>
          </div>

          <!-- What You'll See Section -->
          <div class="text-left space-y-4">
            <h3 class="font-semibold text-gray-800 text-center">
              As {{ invite.custom_title || getRelationshipLabel(invite.relationship) }}, you'll be part of:
            </h3>
            
            <div class="space-y-3">
              <div
                v-for="circle in getAccessibleCircles(invite.relationship)"
                :key="circle.level"
                class="flex items-center space-x-4 p-4 bg-white rounded-lg border border-gray-100"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-soft-pink/20 to-gentle-mint/20 rounded-full flex items-center justify-center">
                  <span class="text-xl">{{ circle.icon }}</span>
                </div>
                <div>
                  <h4 class="font-medium text-gray-800">{{ circle.name }}</h4>
                  <p class="text-sm text-gray-600">{{ circle.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Sample Content Preview -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h4 class="font-medium text-gray-800 mb-3 text-center">You'll see updates like:</h4>
            <div class="space-y-3">
              <div class="flex items-center space-x-3 text-sm">
                <span class="text-lg">📸</span>
                <span class="text-gray-700">Weekly belly photos and ultrasound pictures</span>
              </div>
              <div class="flex items-center space-x-3 text-sm">
                <span class="text-lg">🎯</span>
                <span class="text-gray-700">Milestone celebrations and special moments</span>
              </div>
              <div class="flex items-center space-x-3 text-sm">
                <span class="text-lg">💭</span>
                <span class="text-gray-700">Thoughts, feelings, and pregnancy journey updates</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-4">
            <!-- For Non-Logged In Users -->
            <div v-if="!auth.isLoggedIn.value">
              <BaseButton
                @click="handleSignupFromInvite"
                :disabled="accepting"
                variant="default"
                size="lg"
                class="w-full bg-gradient-to-r from-soft-pink to-gentle-mint hover:from-soft-pink/90 hover:to-gentle-mint/90"
              >
                <UserPlus class="h-5 w-5 mr-2" />
                {{ accepting ? 'Creating Account...' : `Join ${invite.baby_name || 'Baby'}'s Journey` }}
              </BaseButton>
              
              <p class="text-xs text-gray-500 text-center">
                Free to join • You can adjust your settings anytime
              </p>
              
              <div class="pt-4 border-t border-gray-200">
                <p class="text-sm text-gray-600 text-center mb-3">
                  Already have an account?
                </p>
                <BaseButton
                  @click="handleLoginToAccept"
                  variant="outline"
                  size="default"
                  class="w-full"
                >
                  Sign In to Accept
                </BaseButton>
              </div>
            </div>

            <!-- For Logged In Users -->
            <div v-else>
              <BaseButton
                @click="acceptInvite"
                :disabled="accepting"
                variant="default"
                size="lg"
                class="w-full bg-gradient-to-r from-soft-pink to-gentle-mint hover:from-soft-pink/90 hover:to-gentle-mint/90"
              >
                <Check class="h-5 w-5 mr-2" />
                {{ accepting ? 'Accepting...' : 'Accept Invitation' }}
              </BaseButton>
            </div>
          </div>

          <!-- Trust Signals -->
          <div class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-center space-x-6 text-xs text-gray-500">
              <div class="flex items-center space-x-1">
                <Shield class="h-3 w-3" />
                <span>Secure</span>
              </div>
              <div class="flex items-center space-x-1">
                <Lock class="h-3 w-3" />
                <span>Private</span>
              </div>
              <div class="flex items-center space-x-1">
                <Users class="h-3 w-3" />
                <span>Family Only</span>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  AlertCircle, Heart, Baby, UserPlus, Check, Shield, Lock, Users
} from 'lucide-vue-next'

definePageMeta({
  layout: 'guest'
})

// Composables
const route = useRoute()
const router = useRouter()
const auth = useAuth()

// Reactive state
const loading = ref(true)
const accepting = ref(false)
const error = ref('')
const invite = ref<any>(null)

// Get the invite token from the route
const token = route.params.token as string

// Load invite details
const loadInviteDetails = async () => {
  try {
    loading.value = true
    
    const response = await $fetch(`/api/family/invitations/details/${token}`)
    invite.value = response
    
    // Set page title dynamically
    const inviterName = response.inviter.first_name
    const babyName = response.baby_name || 'Baby'
    useSeoMeta({
      title: `Join ${inviterName}'s pregnancy journey - ${babyName}`,
      description: `${inviterName} has invited you to follow their pregnancy journey. Join the family circle to stay connected.`
    })
    
  } catch (err: any) {
    console.error('Failed to load invite:', err)
    
    if (err.statusCode === 404) {
      error.value = "This invitation link is invalid or has expired."
    } else if (err.statusCode === 410) {
      error.value = "This invitation has already been used or cancelled."
    } else {
      error.value = "Unable to load invitation details. Please try again."
    }
  } finally {
    loading.value = false
  }
}

// Handle signup from invite
const handleSignupFromInvite = async () => {
  // Store invite token for after signup
  const inviteToken = token
  
  // Redirect to signup with invite context
  await router.push({
    path: '/auth/signup',
    query: { invite: inviteToken }
  })
}

// Handle login to accept invite
const handleLoginToAccept = async () => {
  // Store invite token for after login
  const inviteToken = token
  
  // Redirect to login with invite context
  await router.push({
    path: '/auth/login',
    query: { 
      invite: inviteToken,
      redirect: `/invite/${inviteToken}`
    }
  })
}

// Accept invite for logged-in users
const acceptInvite = async () => {
  if (!auth.isLoggedIn.value || !invite.value) return
  
  accepting.value = true
  
  try {
    // Accept the invitation
    await $fetch(`/api/family/invitations/${token}/accept`, {
      method: 'POST'
    })
    
    const toast = useToast()
    toast.add({
      title: 'Welcome to the family!',
      description: `You're now part of ${invite.value.baby_name || 'Baby'}'s journey`,
      color: 'green'
    })
    
    // Redirect to the pregnancy feed or welcome page
    await router.push(`/feed/${invite.value.pregnancy_id}?welcome=true`)
    
  } catch (err: any) {
    console.error('Failed to accept invite:', err)
    
    const toast = useToast()
    toast.add({
      title: 'Failed to accept invitation',
      description: err.message || 'Please try again',
      color: 'red'
    })
  } finally {
    accepting.value = false
  }
}

// Helper functions
const getRelationshipLabel = (relationship: string) => {
  const labels: { [key: string]: string } = {
    PARTNER: 'their partner',
    MOTHER: 'their mother',
    FATHER: 'their father',
    SISTER: 'their sister',
    BROTHER: 'their brother',
    GRANDMOTHER: 'their grandmother',
    GRANDFATHER: 'their grandfather',
    MOTHER_IN_LAW: 'their mother-in-law',
    FATHER_IN_LAW: 'their father-in-law',
    AUNT: 'their aunt',
    UNCLE: 'their uncle',
    FRIEND: 'their close friend',
    OTHER: 'family'
  }
  return labels[relationship] || 'family'
}

const getAccessibleCircles = (relationship: string) => {
  const circles = []
  
  // Everyone gets to see "Everyone" level posts
  circles.push({
    level: 'ALL_FAMILY',
    icon: '🌟',
    name: 'Everyone Posts',
    description: 'General pregnancy updates, celebrations, and milestones'
  })
  
  // Inner circle members
  const innerCircleRelations = ['MOTHER', 'FATHER', 'SISTER', 'BROTHER']
  if (innerCircleRelations.includes(relationship)) {
    circles.unshift({
      level: 'IMMEDIATE',
      icon: '👨‍👩‍👧‍👦',
      name: 'Inner Circle',
      description: 'Close family updates and special moments'
    })
  }
  
  // Partners get the most access
  if (relationship === 'PARTNER') {
    circles.unshift({
      level: 'PARTNER_ONLY',
      icon: '💕',
      name: 'Partner Updates',
      description: 'Private moments just between partners'
    })
  }
  
  return circles
}

const formatDueDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })
}

// Load invite details on mount
onMounted(async () => {
  await loadInviteDetails()
  
  // If user is already logged in and this is a direct acceptance, try to accept automatically
  if (auth.isLoggedIn.value && invite.value && route.query.auto === 'true') {
    await acceptInvite()
  }
})

// Set default SEO
useSeoMeta({
  title: 'You\'re Invited - Pregnancy Journey',
  description: 'Join a special pregnancy journey and stay connected with family moments'
})
</script>

<style scoped>
/* Custom gradient animation */
@keyframes gradient-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.bg-gradient-to-r {
  background-size: 200% 200%;
  animation: gradient-flow 3s ease infinite;
}

/* Floating heart animation */
@keyframes float-heart {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.absolute .h-4.w-4 {
  animation: float-heart 2s ease-in-out infinite;
}

/* Fade in animation for content */
.space-y-6 > * {
  animation: fade-in-up 0.6s ease-out forwards;
}

.space-y-6 > *:nth-child(2) {
  animation-delay: 0.1s;
}

.space-y-6 > *:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>