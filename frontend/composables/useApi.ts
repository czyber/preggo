import createClient from 'openapi-fetch'
import type { paths } from '~/types/api'

/**
 * Typed API client composable for Preggo app
 * 
 * Integrates Supabase auth tokens with FastAPI backend endpoints
 * Provides comprehensive pregnancy tracking, family management, and health monitoring
 */

// Create typed API client instance with auth token injection
let apiClient: ReturnType<typeof createClient<paths>> | null = null

const getApiClient = async () => {
  if (!apiClient) {
    const config = useRuntimeConfig()
    const { getAccessToken } = useAuth()
    
    // Get the current access token for API requests
    const token = await getAccessToken()
    
    apiClient = createClient<paths>({
      baseUrl: config.public.apiBase,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      }
    })
  }
  return apiClient
}

// Wrapper functions that inject auth tokens and log API calls
const loggedGET = async (path: string, params?: any) => {
  console.log(`[API] GET ${path}`, params ? { params } : '')
  const client = await getApiClient()
  const { GET } = client
  return await GET(path as any, params)
}

const loggedPOST = async (path: string, options?: any) => {
  console.log(`[API] POST ${path}`, options ? { body: options.body, params: options.params } : '')
  const client = await getApiClient()
  const { POST } = client
  return await POST(path as any, options)
}

const loggedPUT = async (path: string, options?: any) => {
  console.log(`[API] PUT ${path}`, options ? { body: options.body, params: options.params } : '')
  const client = await getApiClient()
  const { PUT } = client
  return await PUT(path as any, options)
}

const loggedDELETE = async (path: string, options?: any) => {
  console.log(`[API] DELETE ${path}`, options ? { params: options.params } : '')
  const client = await getApiClient()
  const { DELETE } = client
  return await DELETE(path as any, options)
}

export const useApi = () => {
  return {
    // ==================== AUTHENTICATION ====================
    register: (data: paths['/api/v1/auth/auth/register']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/auth/auth/register', { body: data }),
    
    login: (data: paths['/api/v1/auth/auth/login']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/auth/auth/login', { body: data }),
    
    logout: () => loggedPOST('/api/v1/auth/auth/logout', {}),
    
    getCurrentUser: () => loggedGET('/api/v1/auth/auth/me'),
    
    updateProfile: (data: paths['/api/v1/auth/auth/me']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/auth/auth/me', { body: data }),
    
    forgotPassword: (data: paths['/api/v1/auth/auth/forgot-password']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/auth/auth/forgot-password', { body: data }),
    
    updatePassword: (data: paths['/api/v1/auth/auth/update-password']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/auth/auth/update-password', { body: data }),
    
    deleteAccount: () => loggedDELETE('/api/v1/auth/auth/account'),
    
    verifyEmailStatus: () => loggedGET('/api/v1/auth/auth/verify-email'),
    
    resendVerificationEmail: () => loggedPOST('/api/v1/auth/auth/resend-verification', {}),

    // ==================== PREGNANCIES ====================
    getPregnancies: (params?: paths['/api/v1/pregnancies/pregnancies/']['get']['parameters']) =>
      loggedGET('/api/v1/pregnancies/pregnancies/', params),
    
    createPregnancy: (data: paths['/api/v1/pregnancies/pregnancies/']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/pregnancies/pregnancies/', { body: data }),
    
    getPregnancy: (pregnancyId: string) =>
      loggedGET('/api/v1/pregnancies/pregnancies/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    updatePregnancy: (pregnancyId: string, data: paths['/api/v1/pregnancies/pregnancies/{pregnancy_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/pregnancies/pregnancies/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } },
        body: data
      }),
    
    deletePregnancy: (pregnancyId: string) =>
      loggedDELETE('/api/v1/pregnancies/pregnancies/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    getWeekCalculation: (pregnancyId: string) =>
      loggedGET('/api/v1/pregnancies/pregnancies/{pregnancy_id}/week-calculation', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    getWeeklyJourney: (pregnancyId: string) =>
      loggedGET('/api/v1/pregnancies/pregnancies/{pregnancy_id}/weekly-journey', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    addPartner: (pregnancyId: string, partnerId: string, data: paths['/api/v1/pregnancies/pregnancies/{pregnancy_id}/partners/{partner_id}']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/pregnancies/pregnancies/{pregnancy_id}/partners/{partner_id}', {
        params: { path: { pregnancy_id: pregnancyId, partner_id: partnerId } },
        body: data
      }),
    
    removePartner: (pregnancyId: string, partnerId: string) =>
      loggedDELETE('/api/v1/pregnancies/pregnancies/{pregnancy_id}/partners/{partner_id}', { 
        params: { path: { pregnancy_id: pregnancyId, partner_id: partnerId } } 
      }),
    
    updatePregnancyStatus: (pregnancyId: string, data: paths['/api/v1/pregnancies/pregnancies/{pregnancy_id}/status']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/pregnancies/pregnancies/{pregnancy_id}/status', {
        params: { path: { pregnancy_id: pregnancyId } },
        body: data
      }),

    // ==================== FAMILY MANAGEMENT ====================
    getFamilyGroups: (params?: paths['/api/v1/family/family/groups']['get']['parameters']) =>
      loggedGET('/api/v1/family/family/groups', params),
    
    createFamilyGroup: (data: paths['/api/v1/family/family/groups']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/family/family/groups', { body: data }),
    
    getFamilyGroupsByPregnancy: (pregnancyId: string) =>
      loggedGET('/api/v1/family/family/groups/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    getFamilyGroup: (groupId: string) =>
      loggedGET('/api/v1/family/family/groups/single/{group_id}', { 
        params: { path: { group_id: groupId } } 
      }),
    
    updateFamilyGroup: (groupId: string, data: paths['/api/v1/family/family/groups/{group_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/family/family/groups/{group_id}', {
        params: { path: { group_id: groupId } },
        body: data
      }),
    
    deleteFamilyGroup: (groupId: string) =>
      loggedDELETE('/api/v1/family/family/groups/{group_id}', { 
        params: { path: { group_id: groupId } } 
      }),
    
    getFamilyMembers: (params?: paths['/api/v1/family/family/members']['get']['parameters']) =>
      loggedGET('/api/v1/family/family/members', params),
    
    addFamilyMember: (data: paths['/api/v1/family/family/members']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/family/family/members', { body: data }),
    
    getFamilyMembersByGroup: (groupId: string) =>
      loggedGET('/api/v1/family/family/members/{group_id}', { 
        params: { path: { group_id: groupId } } 
      }),
    
    updateFamilyMember: (memberId: string, data: paths['/api/v1/family/family/members/{member_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/family/family/members/{member_id}', {
        params: { path: { member_id: memberId } },
        body: data
      }),
    
    removeFamilyMember: (memberId: string) =>
      loggedDELETE('/api/v1/family/family/members/{member_id}', { 
        params: { path: { member_id: memberId } } 
      }),
    
    // Family Invitations
    getFamilyInvitations: (params?: paths['/api/v1/family/family/invitations']['get']['parameters']) =>
      loggedGET('/api/v1/family/family/invitations', params),
    
    createFamilyInvitation: (data: paths['/api/v1/family/family/invitations']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/family/family/invitations', { body: data }),
    
    getFamilyInvitationsByGroup: (groupId: string) =>
      loggedGET('/api/v1/family/family/invitations/{group_id}', { 
        params: { path: { group_id: groupId } } 
      }),
    
    acceptFamilyInvitation: (invitationId: string) =>
      loggedPOST('/api/v1/family/family/invitations/{invitation_id}/accept', { 
        params: { path: { invitation_id: invitationId } } 
      }),
    
    cancelFamilyInvitation: (invitationId: string) =>
      loggedDELETE('/api/v1/family/family/invitations/{invitation_id}', { 
        params: { path: { invitation_id: invitationId } } 
      }),
    
    // Emergency Contacts
    getEmergencyContacts: (params?: paths['/api/v1/family/family/emergency-contacts']['get']['parameters']) =>
      loggedGET('/api/v1/family/family/emergency-contacts', params),
    
    createEmergencyContact: (data: paths['/api/v1/family/family/emergency-contacts']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/family/family/emergency-contacts', { body: data }),
    
    getEmergencyContactsByPregnancy: (pregnancyId: string) =>
      loggedGET('/api/v1/family/family/emergency-contacts/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    updateEmergencyContact: (contactId: string, data: paths['/api/v1/family/family/emergency-contacts/{contact_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/family/family/emergency-contacts/{contact_id}', {
        params: { path: { contact_id: contactId } },
        body: data
      }),
    
    deleteEmergencyContact: (contactId: string) =>
      loggedDELETE('/api/v1/family/family/emergency-contacts/{contact_id}', { 
        params: { path: { contact_id: contactId } } 
      }),

    // ==================== POSTS & CONTENT ====================
    getPosts: (params?: paths['/api/v1/posts/posts/']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/', params),
    
    createPost: (data: paths['/api/v1/posts/posts/']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/posts/posts/', { body: data }),
    
    getPostsByPregnancy: (pregnancyId: string, params?: paths['/api/v1/posts/posts/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    getPostsByUser: (userId: string, params?: paths['/api/v1/posts/posts/user/{user_id}']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/user/{user_id}', { 
        params: { path: { user_id: userId }, ...params } 
      }),
    
    getPost: (postId: string) =>
      loggedGET('/api/v1/posts/posts/{post_id}', { 
        params: { path: { post_id: postId } } 
      }),
    
    updatePost: (postId: string, data: paths['/api/v1/posts/posts/{post_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/posts/posts/{post_id}', {
        params: { path: { post_id: postId } },
        body: data
      }),
    
    deletePost: (postId: string) =>
      loggedDELETE('/api/v1/posts/posts/{post_id}', { 
        params: { path: { post_id: postId } } 
      }),
    
    // Comments
    getPostComments: (postId: string, params?: paths['/api/v1/posts/posts/{post_id}/comments']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/{post_id}/comments', { 
        params: { path: { post_id: postId }, ...params } 
      }),
    
    createComment: (postId: string, data: paths['/api/v1/posts/posts/{post_id}/comments']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/posts/posts/{post_id}/comments', {
        params: { path: { post_id: postId } },
        body: data
      }),
    
    updateComment: (commentId: string, data: paths['/api/v1/posts/posts/comments/{comment_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/posts/posts/comments/{comment_id}', {
        params: { path: { comment_id: commentId } },
        body: data
      }),
    
    deleteComment: (commentId: string) =>
      loggedDELETE('/api/v1/posts/posts/comments/{comment_id}', { 
        params: { path: { comment_id: commentId } } 
      }),
    
    // Reactions
    getPostReactions: (postId: string, params?: paths['/api/v1/posts/posts/{post_id}/reactions']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/{post_id}/reactions', { 
        params: { path: { post_id: postId }, ...params } 
      }),
    
    addPostReaction: (postId: string, data: paths['/api/v1/posts/posts/{post_id}/reactions']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/posts/posts/{post_id}/reactions', {
        params: { path: { post_id: postId } },
        body: data
      }),
    
    removePostReaction: (postId: string, params: paths['/api/v1/posts/posts/{post_id}/reactions']['delete']['parameters']) =>
      loggedDELETE('/api/v1/posts/posts/{post_id}/reactions', { 
        params: { path: { post_id: postId }, ...params } 
      }),
    
    getCommentReactions: (commentId: string, params?: paths['/api/v1/posts/posts/comments/{comment_id}/reactions']['get']['parameters']) =>
      loggedGET('/api/v1/posts/posts/comments/{comment_id}/reactions', { 
        params: { path: { comment_id: commentId }, ...params } 
      }),
    
    addCommentReaction: (commentId: string, data: paths['/api/v1/posts/posts/comments/{comment_id}/reactions']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/posts/posts/comments/{comment_id}/reactions', {
        params: { path: { comment_id: commentId } },
        body: data
      }),
    
    removeCommentReaction: (commentId: string, params: paths['/api/v1/posts/posts/comments/{comment_id}/reactions']['delete']['parameters']) =>
      loggedDELETE('/api/v1/posts/posts/comments/{comment_id}/reactions', { 
        params: { path: { comment_id: commentId }, ...params } 
      }),
    
    // Media
    uploadPostMedia: (data: paths['/api/v1/posts/posts/media']['post']['requestBody']['content']['multipart/form-data']) =>
      loggedPOST('/api/v1/posts/posts/media', { body: data }),
    
    getPostMedia: (postId: string) =>
      loggedGET('/api/v1/posts/posts/{post_id}/media', { 
        params: { path: { post_id: postId } } 
      }),
    
    // Post Actions
    recordPostView: (postId: string) =>
      loggedPOST('/api/v1/posts/posts/{post_id}/view', { 
        params: { path: { post_id: postId } } 
      }),
    
    sharePost: (postId: string, data: paths['/api/v1/posts/posts/{post_id}/share']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/posts/posts/{post_id}/share', {
        params: { path: { post_id: postId } },
        body: data
      }),

    // ==================== MILESTONES ====================
    getMilestones: (params?: paths['/api/v1/milestones/milestones/']['get']['parameters']) =>
      loggedGET('/api/v1/milestones/milestones/', params),
    
    createMilestone: (data: paths['/api/v1/milestones/milestones/']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/milestones/milestones/', { body: data }),
    
    getMilestonesByPregnancy: (pregnancyId: string, params?: paths['/api/v1/milestones/milestones/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/milestones/milestones/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    getMilestonesByWeek: (pregnancyId: string, week: number, params?: paths['/api/v1/milestones/milestones/pregnancy/{pregnancy_id}/week/{week}']['get']['parameters']) =>
      loggedGET('/api/v1/milestones/milestones/pregnancy/{pregnancy_id}/week/{week}', { 
        params: { path: { pregnancy_id: pregnancyId, week }, ...params } 
      }),
    
    getUpcomingMilestones: (pregnancyId: string, params?: paths['/api/v1/milestones/milestones/pregnancy/{pregnancy_id}/upcoming']['get']['parameters']) =>
      loggedGET('/api/v1/milestones/milestones/pregnancy/{pregnancy_id}/upcoming', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    getMilestone: (milestoneId: string) =>
      loggedGET('/api/v1/milestones/milestones/{milestone_id}', { 
        params: { path: { milestone_id: milestoneId } } 
      }),
    
    updateMilestone: (milestoneId: string, data: paths['/api/v1/milestones/milestones/{milestone_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/milestones/milestones/{milestone_id}', {
        params: { path: { milestone_id: milestoneId } },
        body: data
      }),
    
    deleteMilestone: (milestoneId: string) =>
      loggedDELETE('/api/v1/milestones/milestones/{milestone_id}', { 
        params: { path: { milestone_id: milestoneId } } 
      }),
    
    completeMilestone: (milestoneId: string, data: paths['/api/v1/milestones/milestones/{milestone_id}/complete']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/milestones/milestones/{milestone_id}/complete', {
        params: { path: { milestone_id: milestoneId } },
        body: data
      }),
    
    createDefaultMilestones: (pregnancyId: string) =>
      loggedPOST('/api/v1/milestones/milestones/pregnancy/{pregnancy_id}/defaults', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),

    // ==================== HEALTH TRACKING ====================
    getHealthMetrics: (params?: paths['/api/v1/health/health/']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/', params),
    
    createHealthMetric: (data: paths['/api/v1/health/health/']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/', { body: data }),
    
    getHealthMetricsByPregnancy: (pregnancyId: string, params?: paths['/api/v1/health/health/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    // Health Alerts
    getHealthAlerts: (params?: paths['/api/v1/health/health/alerts']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/alerts', params),
    
    createHealthAlert: (data: paths['/api/v1/health/health/alerts']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/alerts', { body: data }),
    
    getHealthAlertsByPregnancy: (pregnancyId: string, params?: paths['/api/v1/health/health/alerts/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/alerts/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    acknowledgeHealthAlert: (alertId: string) =>
      loggedPOST('/api/v1/health/health/alerts/{alert_id}/acknowledge', { 
        params: { path: { alert_id: alertId } } 
      }),
    
    resolveHealthAlert: (alertId: string, data: paths['/api/v1/health/health/alerts/{alert_id}/resolve']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/alerts/{alert_id}/resolve', {
        params: { path: { alert_id: alertId } },
        body: data
      }),
    
    // Symptoms
    getSymptoms: (params?: paths['/api/v1/health/health/symptoms']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/symptoms', params),
    
    logSymptom: (data: paths['/api/v1/health/health/symptoms']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/symptoms', { body: data }),
    
    getSymptomsByPregnancy: (pregnancyId: string, params?: paths['/api/v1/health/health/symptoms/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/symptoms/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    getSymptomTrends: (pregnancyId: string, symptomName: string, params?: paths['/api/v1/health/health/symptoms/pregnancy/{pregnancy_id}/trends/{symptom_name}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/symptoms/pregnancy/{pregnancy_id}/trends/{symptom_name}', { 
        params: { path: { pregnancy_id: pregnancyId, symptom_name: symptomName }, ...params } 
      }),
    
    // Weight Tracking
    getWeightReadings: (params?: paths['/api/v1/health/health/weight']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/weight', params),
    
    logWeight: (data: paths['/api/v1/health/health/weight']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/weight', { body: data }),
    
    getWeightByPregnancy: (pregnancyId: string, params?: paths['/api/v1/health/health/weight/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/weight/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),
    
    // Mood Tracking
    getMoodReadings: (params?: paths['/api/v1/health/health/mood']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/mood', params),
    
    logMood: (data: paths['/api/v1/health/health/mood']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/health/health/mood', { body: data }),
    
    getMoodByPregnancy: (pregnancyId: string, params?: paths['/api/v1/health/health/mood/pregnancy/{pregnancy_id}']['get']['parameters']) =>
      loggedGET('/api/v1/health/health/mood/pregnancy/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId }, ...params } 
      }),

    // ==================== LOGGING ====================
    createFrontendLog: (data: paths['/api/v1/logs/frontend']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/logs/frontend', { body: data }),
    
    getLogs: (params?: paths['/api/v1/logs/']['get']['parameters']) =>
      loggedGET('/api/v1/logs/', params),
    
    clearLogs: () => loggedDELETE('/api/v1/logs/'),

    // ==================== LEGACY ITEMS (for compatibility) ====================
    getItems: (params?: paths['/api/v1/items/']['get']['parameters']) => 
      loggedGET('/api/v1/items/', params),
    
    createItem: (data: paths['/api/v1/items/']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/api/v1/items/', { body: data }),
    
    getItem: (itemId: number) =>
      loggedGET('/api/v1/items/{item_id}', { params: { path: { item_id: itemId } } }),
    
    updateItem: (itemId: number, data: paths['/api/v1/items/{item_id}']['put']['requestBody']['content']['application/json']) =>
      loggedPUT('/api/v1/items/{item_id}', { 
        params: { path: { item_id: itemId } },
        body: data 
      }),
    
    deleteItem: (itemId: number) =>
      loggedDELETE('/api/v1/items/{item_id}', { params: { path: { item_id: itemId } } }),
  }
}

// Export types for use in components
export type {
  paths,
  components
} from '~/types/api'