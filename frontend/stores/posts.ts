import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type Post = components['schemas']['PostResponse']
type PostCreate = components['schemas']['PostCreate']
type PostUpdate = components['schemas']['PostUpdate']
type Comment = components['schemas']['CommentResponse']
type CommentCreate = components['schemas']['CommentCreate']
type CommentUpdate = components['schemas']['CommentUpdate']
type MediaItem = components['schemas']['MediaItemCreate']
type PostView = components['schemas']['PostViewCreate']
type PostShare = components['schemas']['PostShareCreate']

export const usePostsStore = defineStore('posts', () => {
  // State as refs
  const posts = ref<Post[]>([])
  const comments = ref<Record<string, Comment[]>>({}) // Comments keyed by post ID
  const currentPost = ref<Post | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getPostById = computed(() => (id: string) => {
    return posts.value.find(post => post.id === id)
  })
  
  const getCommentsForPost = computed(() => (postId: string) => {
    return comments.value[postId] || []
  })
  
  const publicPosts = computed(() => {
    return posts.value.filter(post => post.visibility === 'public')
  })
  
  const familyPosts = computed(() => {
    return posts.value.filter(post => post.visibility === 'family')
  })
  
  const privatePosts = computed(() => {
    return posts.value.filter(post => post.visibility === 'private')
  })
  
  const postsWithMedia = computed(() => {
    return posts.value.filter(post => post.media_items && post.media_items.length > 0)
  })
  
  const postsByType = computed(() => (type: string) => {
    return posts.value.filter(post => post.type === type)
  })

  // Actions as functions
  async function fetchPosts(pregnancyId?: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      let data, apiError
      
      if (pregnancyId) {
        ({ data, error: apiError } = await api.getPregnancyPosts(pregnancyId))
      } else {
        ({ data, error: apiError } = await api.getFamilyPosts())
      }
      
      if (apiError) {
        throw new Error(`Failed to fetch posts: ${apiError}`)
      }
      
      posts.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching posts:', err)
    } finally {
      loading.value = false
    }
  }

  async function createPost(postData: PostCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createPost(postData)
      
      if (apiError) {
        throw new Error(`Failed to create post: ${apiError}`)
      }
      
      if (data) {
        posts.value.unshift(data) // Add to beginning for chronological order
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating post:', err)
      throw err
    }
  }

  async function updatePost(postId: string, postData: PostUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updatePost(postId, postData)
      
      if (apiError) {
        throw new Error(`Failed to update post: ${apiError}`)
      }
      
      if (data) {
        const index = posts.value.findIndex(post => post.id === postId)
        if (index !== -1) {
          posts.value[index] = data
        }
        
        // Update current post if it's the one being updated
        if (currentPost.value?.id === postId) {
          currentPost.value = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating post:', err)
      throw err
    }
  }

  async function deletePost(postId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deletePost(postId)
      
      if (apiError) {
        throw new Error(`Failed to delete post: ${apiError}`)
      }
      
      posts.value = posts.value.filter(post => post.id !== postId)
      
      // Clear current post if it was deleted
      if (currentPost.value?.id === postId) {
        currentPost.value = null
      }
      
      // Clear comments for deleted post
      delete comments.value[postId]
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting post:', err)
      throw err
    }
  }

  async function fetchPostComments(postId: string) {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getPostComments(postId)
      
      if (apiError) {
        throw new Error(`Failed to fetch comments: ${apiError}`)
      }
      
      comments.value[postId] = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching comments:', err)
    } finally {
      loading.value = false
    }
  }

  async function createComment(commentData: CommentCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createComment(commentData)
      
      if (apiError) {
        throw new Error(`Failed to create comment: ${apiError}`)
      }
      
      if (data) {
        const postId = commentData.post_id
        if (!comments.value[postId]) {
          comments.value[postId] = []
        }
        comments.value[postId].push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating comment:', err)
      throw err
    }
  }

  async function updateComment(commentId: string, commentData: CommentUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateComment(commentId, commentData)
      
      if (apiError) {
        throw new Error(`Failed to update comment: ${apiError}`)
      }
      
      if (data) {
        // Find and update comment in the appropriate post's comments
        for (const postId in comments.value) {
          const index = comments.value[postId].findIndex(comment => comment.id === commentId)
          if (index !== -1) {
            comments.value[postId][index] = data
            break
          }
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating comment:', err)
      throw err
    }
  }

  async function deleteComment(commentId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deleteComment(commentId)
      
      if (apiError) {
        throw new Error(`Failed to delete comment: ${apiError}`)
      }
      
      // Remove comment from all post comment arrays
      for (const postId in comments.value) {
        comments.value[postId] = comments.value[postId].filter(comment => comment.id !== commentId)
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting comment:', err)
      throw err
    }
  }

  async function likePost(postId: string) {
    try {
      const api = useApi()
      const { error: apiError } = await api.likePost(postId)
      
      if (apiError) {
        throw new Error(`Failed to like post: ${apiError}`)
      }
      
      // Update like count in local state
      const post = getPostById.value(postId)
      if (post) {
        post.like_count = (post.like_count || 0) + 1
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error liking post:', err)
      throw err
    }
  }

  async function viewPost(postData: PostView) {
    try {
      const api = useApi()
      const { error: apiError } = await api.viewPost(postData)
      
      if (apiError) {
        throw new Error(`Failed to record post view: ${apiError}`)
      }
      
      // Update view count in local state
      const post = getPostById.value(postData.post_id)
      if (post) {
        post.view_count = (post.view_count || 0) + 1
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error recording post view:', err)
      throw err
    }
  }

  async function sharePost(shareData: PostShare) {
    try {
      const api = useApi()
      const { error: apiError } = await api.sharePost(shareData.post_id, shareData)
      
      if (apiError) {
        throw new Error(`Failed to share post: ${apiError}`)
      }
      
      // Update share count in local state
      const post = getPostById.value(shareData.post_id)
      if (post) {
        post.share_count = (post.share_count || 0) + 1
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error sharing post:', err)
      throw err
    }
  }

  function setCurrentPost(post: Post) {
    currentPost.value = post
    // Fetch comments for the current post if not already loaded
    if (!comments.value[post.id]) {
      fetchPostComments(post.id)
    }
  }

  function reset() {
    posts.value = []
    comments.value = {}
    currentPost.value = null
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    posts,
    comments,
    currentPost,
    loading,
    error,
    
    // Computed
    getPostById,
    getCommentsForPost,
    publicPosts,
    familyPosts,
    privatePosts,
    postsWithMedia,
    postsByType,
    
    // Actions
    fetchPosts,
    createPost,
    updatePost,
    deletePost,
    fetchPostComments,
    createComment,
    updateComment,
    deleteComment,
    likePost,
    viewPost,
    sharePost,
    setCurrentPost,
    reset
  }
})