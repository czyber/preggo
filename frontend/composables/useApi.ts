import createClient from 'openapi-fetch'
import type { paths } from '@/types/api'

/**
 * Typed API client composable for Preggo app
 * 
 * Integrates unified auth system with FastAPI backend endpoints
 * Provides comprehensive pregnancy tracking, family management, and health monitoring
 */

export const useApi = () => {
  const config = useRuntimeConfig()

  // Create API client for each request with current auth state
  const createApiClient = async () => {
    let token = null
    
    // Only try to get auth token on client-side
    if (process.client) {
      try {
        // Use unified auth composable for token retrieval
        const auth = useAuth()
        token = auth.session.value?.access_token
      } catch (error) {
        // Auth not available, continue without token
      }
    }
    
    return createClient<paths>({
      baseUrl: config.public.apiBase,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      }
    })
  }

  // Wrapper functions that inject auth tokens and log API calls
  const loggedGET = async (path: string, params?: any) => {
    console.log(`[API] GET ${path}`, params ? { params } : '')
    const client = await createApiClient()
    const { GET } = client
    return await GET(path as any, params)
  }

  const loggedPOST = async (path: string, options?: any) => {
    console.log(`[API] POST ${path}`, options ? { body: options.body, params: options.params } : '')
    const client = await createApiClient()
    const { POST } = client
    return await POST(path as any, options)
  }

  const loggedPUT = async (path: string, options?: any) => {
    console.log(`[API] PUT ${path}`, options ? { body: options.body, params: options.params } : '')
    const client = await createApiClient()
    const { PUT } = client
    return await PUT(path as any, options)
  }

  const loggedDELETE = async (path: string, options?: any) => {
    console.log(`[API] DELETE ${path}`, options ? { params: options.params } : '')
    const client = await createApiClient()
    const { DELETE } = client
    return await DELETE(path as any, options)
  }

  return {
    // ==================== AUTHENTICATION ====================
    register: (data: paths['/api/v1/auth/auth/register']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/auth/register', { body: data }),
    
    login: (data: paths['/api/v1/auth/auth/login']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/auth/login', { body: data }),
    
    logout: () => loggedPOST('/auth/logout', {}),
    
    getCurrentUser: () => loggedGET('/auth/me'),
    
    updateCurrentUser: (data: any) => loggedPUT('/auth/me', { body: data }),
    
    forgotPassword: (data: paths['/api/v1/auth/auth/forgot-password']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/auth/forgot-password', { body: data }),
    
    updatePassword: (data: paths['/api/v1/auth/auth/update-password']['post']['requestBody']['content']['application/json']) =>
      loggedPOST('/auth/update-password', { body: data }),
    
    deleteAccount: () => loggedDELETE('/auth/account'),
    
    verifyEmailStatus: () => loggedGET('/auth/verify-email'),
    
    resendVerificationEmail: () => loggedPOST('/auth/resend-verification', {}),

    // ==================== PREGNANCIES ====================
    getUserPregnancies: () => loggedGET('/pregnancies/'),
    
    createPregnancy: (data: any) => loggedPOST('/pregnancies/', { body: data }),
    
    getPregnancy: (pregnancyId: string) =>
      loggedGET('/pregnancies/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),
    
    updatePregnancy: (pregnancyId: string, data: any) =>
      loggedPUT('/pregnancies/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } },
        body: data
      }),
    
    deletePregnancy: (pregnancyId: string) =>
      loggedDELETE('/pregnancies/{pregnancy_id}', { 
        params: { path: { pregnancy_id: pregnancyId } } 
      }),

    // ==================== ITEMS (Legacy) ====================
    getItems: (params?: any) => loggedGET('/items/', params),
    
    createItem: (data: any) => loggedPOST('/items/', { body: data }),
    
    getItem: (itemId: number) =>
      loggedGET('/items/{item_id}', { params: { path: { item_id: itemId } } }),
    
    updateItem: (itemId: number, data: any) =>
      loggedPUT('/items/{item_id}', { 
        params: { path: { item_id: itemId } },
        body: data 
      }),
    
    deleteItem: (itemId: number) =>
      loggedDELETE('/items/{item_id}', { params: { path: { item_id: itemId } } }),

    // ==================== POSTS ====================
    getPosts: () => loggedGET('/posts/'),
    
    getPregnancyPosts: (pregnancyId: string) =>
      loggedGET('/posts/pregnancy/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } }
      }),
    
    getPost: (postId: string) =>
      loggedGET('/posts/{post_id}', {
        params: { path: { post_id: postId } }
      }),
    
    createPost: (data: any) => loggedPOST('/posts/', { body: data }),
    
    updatePost: (postId: string, data: any) =>
      loggedPUT('/posts/{post_id}', {
        params: { path: { post_id: postId } },
        body: data
      }),
    
    deletePost: (postId: string) =>
      loggedDELETE('/posts/{post_id}', {
        params: { path: { post_id: postId } }
      }),

    // ==================== MEDIA ====================
    createMediaItem: (data: any) => loggedPOST('/posts/media', { body: data }),
    
    getPostMedia: (postId: string) =>
      loggedGET('/posts/{post_id}/media', {
        params: { path: { post_id: postId } }
      }),

    // ==================== POST INTERACTIONS ====================
    addPostReaction: (postId: string, reactionData: any) =>
      loggedPOST('/feed/reactions', {
        body: reactionData
      }),
    
    removePostReaction: (postId: string) =>
      loggedDELETE('/feed/reactions', {
        body: { post_id: postId }
      }),
    
    recordPostView: (postId: string, data?: { time_spent?: number, source?: string }) =>
      loggedPOST('/posts/{post_id}/view', {
        params: { path: { post_id: postId } },
        body: {
          post_id: postId,
          user_id: '', // Will be set by backend from auth
          time_spent: data?.time_spent || null,
          source: data?.source || 'timeline'
        }
      }),

    // ==================== COMMENTS ====================
    getPostComments: (postId: string) =>
      loggedGET('/posts/{post_id}/comments', {
        params: { path: { post_id: postId } }
      }),
    
    createComment: (data: any) =>
      loggedPOST('/posts/{post_id}/comments', {
        params: { path: { post_id: data.post_id } },
        body: data
      }),
    
    updateComment: (commentId: string, data: any) =>
      loggedPUT('/posts/comments/{comment_id}', {
        params: { path: { comment_id: commentId } },
        body: data
      }),
    
    deleteComment: (commentId: string) =>
      loggedDELETE('/posts/comments/{comment_id}', {
        params: { path: { comment_id: commentId } }
      }),

    // ==================== FEED ====================
    getFamilyFeed: (pregnancyId: string, params?: any) =>
      loggedGET('/feed/family/{pregnancy_id}', {
        params: {
          path: { pregnancy_id: pregnancyId },
          query: params
        }
      }),

    getPersonalTimeline: (pregnancyId: string) =>
      loggedGET('/feed/personal/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } }
      }),

    getFeedFilters: () => loggedGET('/feed/filters'),

    getTrendingPosts: (pregnancyId: string) =>
      loggedGET('/feed/trending/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } }
      }),

    getPregnancyCelebrations: (pregnancyId: string, limit?: number) =>
      loggedGET('/feed/celebrations/{pregnancy_id}', {
        params: { 
          path: { pregnancy_id: pregnancyId },
          query: limit ? { limit } : {}
        }
      }),

    // ==================== FAMILY ====================
    getFamilyGroupMembers: (groupId: string) =>
      loggedGET('/family/members/{group_id}', {
        params: { path: { group_id: groupId } }
      }),

    getPregnancyFamilyMembers: (pregnancyId: string) =>
      loggedGET('/family/{pregnancy_id}/members', {
        params: { path: { pregnancy_id: pregnancyId } }
      }),

    addFamilyMember: (groupId: string, data: any) =>
      loggedPOST('/family/{group_id}/members', {
        params: { path: { group_id: groupId } },
        body: data
      }),

    updateFamilyMember: (groupId: string, memberId: string, data: any) =>
      loggedPUT('/family/{group_id}/members/{member_id}', {
        params: { path: { group_id: groupId, member_id: memberId } },
        body: data
      }),

    removeFamilyMember: (groupId: string, memberId: string) =>
      loggedDELETE('/family/{group_id}/members/{member_id}', {
        params: { path: { group_id: groupId, member_id: memberId } }
      }),

    inviteFamilyMember: (groupId: string, data: any) =>
      loggedPOST('/family/{group_id}/invite', {
        params: { path: { group_id: groupId } },
        body: data
      }),

    getFamilyGroup: (groupId: string) =>
      loggedGET('/family/{group_id}', {
        params: { path: { group_id: groupId } }
      }),

    createFamilyGroup: (data: any) => loggedPOST('/family/', { body: data }),

    updateFamilyGroup: (groupId: string, data: any) =>
      loggedPUT('/family/{group_id}', {
        params: { path: { group_id: groupId } },
        body: data
      }),

    getUserFamilyGroups: () => loggedGET('/family/'),

    getFamilyInvitations: () => loggedGET('/family/invitations'),

    createFamilyInvitation: (data: any) => loggedPOST('/family/invitations', { body: data }),

    updateFamilyInvitation: (invitationId: string, data: any) =>
      loggedPUT('/family/invitations/{invitation_id}', {
        params: { path: { invitation_id: invitationId } },
        body: data
      }),

    generateFamilyInviteLink: (data: any) => loggedPOST('/family/invitations/generate-link', { body: data }),

    // ==================== CONTEXTUAL INVITES ====================
    getInviteContext: (token: string) =>
      loggedGET('/invites/{token}/context', {
        params: { path: { token } }
      }),

    acceptInvite: (token: string, data: { user_id: string }) =>
      loggedPOST('/invites/{token}/accept', {
        params: { path: { token } },
        body: data
      }),

    createContextualInvite: (pregnancyId: string, data: any) =>
      loggedPOST('/invites/contextual/{pregnancy_id}', {
        params: { path: { pregnancy_id: pregnancyId } },
        body: data
      }),

    // ==================== CIRCLE PATTERNS ====================
    getCirclePatterns: (pregnancyId?: string) =>
      loggedGET('/circles/patterns', {
        params: pregnancyId ? { query: { pregnancy_id: pregnancyId } } : {}
      }),

    createCirclePattern: (data: any) =>
      loggedPOST('/circles/patterns', { body: data }),

    updateCirclePattern: (patternId: string, data: any) =>
      loggedPUT('/circles/patterns/{pattern_id}', {
        params: { path: { pattern_id: patternId } },
        body: data
      }),

    getCircleSuggestions: (postContent: string, postType: string) =>
      loggedPOST('/circles/suggestions', {
        body: { content: postContent, type: postType }
      }),
  }
}

// Export types for use in components
export type {
  paths,
  components
} from '@/types/api'
