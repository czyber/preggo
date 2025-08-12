<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="text-center space-y-2">
      <h2 class="text-2xl font-primary font-semibold text-gray-800">
        Invite Family & Friends
      </h2>
      <p class="text-gray-600 font-secondary">
        Share your pregnancy journey with those you love
      </p>
    </div>

    <!-- Quick Invite Section -->
    <div class="bg-gradient-to-r from-soft-pink/10 to-gentle-mint/10 rounded-lg p-6 border border-gentle-mint/20">
      <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
        <Zap class="h-5 w-5 mr-2 text-gentle-mint" />
        Quick Invite
      </h3>
      
      <div class="space-y-4">
        <!-- Relationship Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Who are you inviting?
          </label>
          <select 
            v-model="selectedRelationship"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gentle-mint focus:border-gentle-mint"
          >
            <option value="">Select relationship...</option>
            <option value="partner">Partner/Spouse</option>
            <option value="mother">Mother</option>
            <option value="father">Father</option>
            <option value="sister">Sister</option>
            <option value="brother">Brother</option>
            <option value="grandmother">Grandmother</option>
            <option value="grandfather">Grandfather</option>
            <option value="mother_in_law">Mother-in-law</option>
            <option value="father_in_law">Father-in-law</option>
            <option value="aunt">Aunt</option>
            <option value="uncle">Uncle</option>
            <option value="friend">Close Friend</option>
            <option value="other">Other</option>
          </select>
        </div>

        <!-- Custom Title (Optional) -->
        <div v-if="selectedRelationship">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Custom name (optional)
          </label>
          <BaseInput
            v-model="customTitle"
            placeholder="e.g., 'Grandma Mary', 'Aunt Sarah'"
            class="w-full"
          />
        </div>

        <!-- Personal Message (Optional) -->
        <div v-if="selectedRelationship">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Personal message (optional)
          </label>
          <textarea
            v-model="personalMessage"
            rows="3"
            placeholder="Add a personal touch to your invitation..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-gentle-mint focus:border-gentle-mint resize-none"
          ></textarea>
        </div>

        <!-- Generate Link Button -->
        <BaseButton
          v-if="selectedRelationship"
          @click="generateInviteLink"
          :disabled="generating"
          variant="default"
          size="lg"
          class="w-full"
        >
          <Link class="h-5 w-5 mr-2" />
          {{ generating ? 'Generating...' : 'Generate Invite Link' }}
        </BaseButton>
      </div>
    </div>

    <!-- Generated Link Section -->
    <div v-if="generatedLink" class="bg-white border border-gentle-mint/30 rounded-lg p-6">
      <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
        <CheckCircle class="h-5 w-5 mr-2 text-green-500" />
        Invite Link Generated!
      </h3>
      
      <!-- Link Preview -->
      <div class="space-y-4">
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex-1 mr-3">
              <p class="text-sm font-medium text-gray-800 mb-1">Invite Link</p>
              <p class="text-xs text-gray-600 break-all">{{ generatedLink.url }}</p>
            </div>
            <BaseButton
              @click="copyLink"
              variant="outline"
              size="sm"
            >
              <Copy class="h-4 w-4 mr-1" />
              {{ copied ? 'Copied!' : 'Copy' }}
            </BaseButton>
          </div>
        </div>

        <!-- Sharing Options -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            @click="shareViaWhatsApp"
            class="flex items-center justify-center space-x-2 p-3 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg transition-colors"
          >
            <MessageCircle class="h-4 w-4 text-green-600" />
            <span class="text-sm font-medium text-green-800">WhatsApp</span>
          </button>
          
          <button
            @click="shareViaEmail"
            class="flex items-center justify-center space-x-2 p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
          >
            <Mail class="h-4 w-4 text-blue-600" />
            <span class="text-sm font-medium text-blue-800">Email</span>
          </button>
          
          <button
            @click="shareViaSMS"
            class="flex items-center justify-center space-x-2 p-3 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg transition-colors"
          >
            <MessageSquare class="h-4 w-4 text-purple-600" />
            <span class="text-sm font-medium text-purple-800">Text</span>
          </button>
          
          <button
            @click="copyLink"
            class="flex items-center justify-center space-x-2 p-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors"
          >
            <Share class="h-4 w-4 text-gray-600" />
            <span class="text-sm font-medium text-gray-800">Share</span>
          </button>
        </div>

        <!-- What they'll see preview -->
        <div class="bg-gradient-to-r from-soft-pink/5 to-gentle-mint/5 rounded-lg p-4 border border-gentle-mint/10">
          <h4 class="font-medium text-gray-800 mb-2">What {{ customTitle || getRelationshipLabel(selectedRelationship) }} will see:</h4>
          <div class="space-y-2 text-sm text-gray-600">
            <div class="flex items-center space-x-2">
              <span class="text-lg">{{ getCircleIcon('IMMEDIATE') }}</span>
              <span>{{ getCircleAccess(selectedRelationship) }}</span>
            </div>
            <p class="text-xs text-gray-500">
              {{ getAccessDescription(selectedRelationship) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Invites -->
    <div class="space-y-4">
      <h3 class="font-semibold text-gray-800 flex items-center">
        <Users class="h-5 w-5 mr-2" />
        Pending Invitations ({{ pendingInvites.length }})
      </h3>
      
      <div v-if="pendingInvites.length === 0" class="text-center py-8 text-gray-500">
        <UserX class="h-8 w-8 mx-auto mb-2 text-gray-400" />
        <p>No pending invitations</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="invite in pendingInvites"
          :key="invite.id"
          class="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
        >
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
              <span class="text-lg">{{ getRelationshipIcon(invite.relationship) }}</span>
            </div>
            <div>
              <h4 class="font-medium text-gray-800">
                {{ invite.custom_title || getRelationshipLabel(invite.relationship) }}
              </h4>
              <p class="text-sm text-gray-600">{{ invite.email }}</p>
              <p class="text-xs text-gray-500">
                Sent {{ formatDate(invite.created_at) }} • Expires {{ formatDate(invite.expires_at) }}
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-2">
            <BaseButton
              @click="resendInvite(invite)"
              variant="outline"
              size="sm"
            >
              <RefreshCcw class="h-4 w-4 mr-1" />
              Resend
            </BaseButton>
            
            <BaseButton
              @click="cancelInvite(invite)"
              variant="outline"
              size="sm"
              class="text-red-600 hover:bg-red-50"
            >
              <X class="h-4 w-4" />
            </BaseButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Zap, Link, CheckCircle, Copy, MessageCircle, Mail, MessageSquare, Share,
  Users, UserX, RefreshCcw, X
} from 'lucide-vue-next'

// Props
interface Props {
  pregnancyId: string
}

const props = defineProps<Props>()

// Reactive state
const selectedRelationship = ref('')
const customTitle = ref('')
const personalMessage = ref('')
const generating = ref(false)
const copied = ref(false)
const generatedLink = ref<{
  url: string
  token: string
  expires_at: string
} | null>(null)

const pendingInvites = ref([
  // Mock data - replace with real API call
  {
    id: '1',
    email: 'mom@example.com',
    relationship: 'MOTHER',
    custom_title: 'Mom',
    created_at: new Date(),
    expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  }
])

// Methods
const generateInviteLink = async () => {
  generating.value = true
  
  try {
    // Call API to generate invite using proper API client
    const api = useApi()
    const response = await api.generateFamilyInviteLink({
      pregnancy_id: props.pregnancyId,
      relationship: selectedRelationship.value,
      custom_title: customTitle.value,
      message: personalMessage.value
    })
    
    generatedLink.value = response.data
    
    // Show success toast
    const toast = useToast()
    toast.add({
      title: 'Invite link generated!',
      description: 'You can now share this link with your family member',
      color: 'green'
    })
    
  } catch (error) {
    console.error('Failed to generate invite link:', error)
    const toast = useToast()
    toast.add({
      title: 'Failed to generate link',
      description: 'Please try again',
      color: 'red'
    })
  } finally {
    generating.value = false
  }
}

const copyLink = async () => {
  if (!generatedLink.value) return
  
  try {
    await navigator.clipboard.writeText(generatedLink.value.url)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
    
    const toast = useToast()
    toast.add({
      title: 'Link copied!',
      description: 'You can now paste it anywhere to share',
      color: 'green'
    })
  } catch (error) {
    console.error('Failed to copy link:', error)
  }
}

const shareViaWhatsApp = () => {
  if (!generatedLink.value) return
  
  const message = `Hi! I'd love to share my pregnancy journey with you. Join me here: ${generatedLink.value.url}`
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`
  window.open(whatsappUrl, '_blank')
}

const shareViaEmail = () => {
  if (!generatedLink.value) return
  
  const subject = 'Join my pregnancy journey!'
  const body = `Hi!

I'd love to share my pregnancy journey with you. Click the link below to join:

${generatedLink.value.url}

${personalMessage.value ? `\n${personalMessage.value}\n` : ''}

Looking forward to sharing this special time with you!`
  
  const emailUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  window.location.href = emailUrl
}

const shareViaSMS = () => {
  if (!generatedLink.value) return
  
  const message = `Hi! I'd love to share my pregnancy journey with you. Join me here: ${generatedLink.value.url}`
  const smsUrl = `sms:?body=${encodeURIComponent(message)}`
  window.location.href = smsUrl
}

const resendInvite = async (invite: any) => {
  try {
    await $fetch(`/api/family/invitations/${invite.id}/resend`, {
      method: 'POST'
    })
    
    const toast = useToast()
    toast.add({
      title: 'Invitation resent!',
      description: `New invite sent to ${invite.email}`,
      color: 'green'
    })
  } catch (error) {
    console.error('Failed to resend invite:', error)
  }
}

const cancelInvite = async (invite: any) => {
  try {
    await $fetch(`/api/family/invitations/${invite.id}`, {
      method: 'DELETE'
    })
    
    // Remove from local list
    pendingInvites.value = pendingInvites.value.filter(i => i.id !== invite.id)
    
    const toast = useToast()
    toast.add({
      title: 'Invitation cancelled',
      description: `Invitation to ${invite.email} has been cancelled`,
      color: 'orange'
    })
  } catch (error) {
    console.error('Failed to cancel invite:', error)
  }
}

// Helper functions
const getRelationshipLabel = (relationship: string) => {
  const labels: { [key: string]: string } = {
    PARTNER: 'Partner',
    MOTHER: 'Mother',
    FATHER: 'Father', 
    SISTER: 'Sister',
    BROTHER: 'Brother',
    GRANDMOTHER: 'Grandmother',
    GRANDFATHER: 'Grandfather',
    MOTHER_IN_LAW: 'Mother-in-law',
    FATHER_IN_LAW: 'Father-in-law',
    AUNT: 'Aunt',
    UNCLE: 'Uncle',
    FRIEND: 'Friend',
    OTHER: 'Family Member'
  }
  return labels[relationship] || 'Family Member'
}

const getRelationshipIcon = (relationship: string) => {
  const icons: { [key: string]: string } = {
    PARTNER: '💕',
    MOTHER: '👩',
    FATHER: '👨',
    SISTER: '👭',
    BROTHER: '👬',
    GRANDMOTHER: '👵',
    GRANDFATHER: '👴',
    MOTHER_IN_LAW: '👩',
    FATHER_IN_LAW: '👨',
    AUNT: '👩',
    UNCLE: '👨',
    FRIEND: '👥',
    OTHER: '👤'
  }
  return icons[relationship] || '👤'
}

const getCircleIcon = (level: string) => {
  const icons: { [key: string]: string } = {
    PARTNER_ONLY: '💕',
    IMMEDIATE: '👨‍👩‍👧‍👦',
    ALL_FAMILY: '🌟'
  }
  return icons[level] || '👨‍👩‍👧‍👦'
}

const getCircleAccess = (relationship: string) => {
  const partnerRelations = ['PARTNER']
  const immediateRelations = ['MOTHER', 'FATHER', 'SISTER', 'BROTHER']
  
  if (partnerRelations.includes(relationship)) {
    return 'Partner + Inner Circle + Everyone posts'
  } else if (immediateRelations.includes(relationship)) {
    return 'Inner Circle + Everyone posts'
  } else {
    return 'Everyone posts only'
  }
}

const getAccessDescription = (relationship: string) => {
  const partnerRelations = ['PARTNER']
  const immediateRelations = ['MOTHER', 'FATHER', 'SISTER', 'BROTHER']
  
  if (partnerRelations.includes(relationship)) {
    return 'Will see all updates including private partner moments'
  } else if (immediateRelations.includes(relationship)) {
    return 'Will see family updates and celebration moments'
  } else {
    return 'Will see general pregnancy updates and celebrations'
  }
}

const formatDate = (date: Date | string) => {
  return new Date(date).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

// Load pending invites on mount
onMounted(async () => {
  try {
    const invites = await $fetch(`/api/family/invitations/${props.pregnancyId}`)
    pendingInvites.value = invites.filter((i: any) => i.status === 'PENDING')
  } catch (error) {
    console.error('Failed to load pending invites:', error)
  }
})
</script>

<style scoped>
/* Custom animations for the invite flow */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>