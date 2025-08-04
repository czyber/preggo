import createClient from 'openapi-fetch'
import type { paths } from '~/types/api'

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
    addPostReaction: (postId: string, reactionType: string) =>
      loggedPOST('/posts/{post_id}/reactions', {
        params: { path: { post_id: postId } },
        body: { type: reactionType }
      }),
    
    removePostReaction: (postId: string) =>
      loggedDELETE('/posts/{post_id}/reactions', {
        params: { path: { post_id: postId } }
      }),
    
    recordPostView: (postId: string) =>
      loggedPOST('/posts/{post_id}/view', {
        params: { path: { post_id: postId } }
      }),

    // ==================== COMMENTS ====================
    getPostComments: (postId: string) =>
      loggedGET('/posts/{post_id}/comments', {
        params: { path: { post_id: postId } }
      }),
    
    createComment: (postId: string, data: any) =>
      loggedPOST('/posts/{post_id}/comments', {
        params: { path: { post_id: postId } },
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
  }
}

// Export types for use in components
export type {
  paths,
  components
} from '~/types/api'