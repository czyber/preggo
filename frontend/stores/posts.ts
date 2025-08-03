import { defineStore } from 'pinia'
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

export const usePostsStore = defineStore('posts', {
  state: () => ({
    posts: [] as Post[],
    comments: {} as Record<string, Comment[]>, // Comments keyed by post ID
    currentPost: null as Post | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getPostById: (state) => (id: string) => {
      return state.posts.find(post => post.id === id)
    },
    
    getCommentsForPost: (state) => (postId: string) => {
      return state.comments[postId] || []
    },
    
    publicPosts: (state) => {
      return state.posts.filter(post => post.visibility === 'public')
    },
    
    familyPosts: (state) => {
      return state.posts.filter(post => post.visibility === 'family')
    },
    
    privatePosts: (state) => {
      return state.posts.filter(post => post.visibility === 'private')
    },
    
    postsWithMedia: (state) => {
      return state.posts.filter(post => post.media_items && post.media_items.length > 0)
    },
    
    postsByType: (state) => (type: string) => {
      return state.posts.filter(post => post.type === type)
    },
  },

  actions: {
    async fetchPosts(pregnancyId?: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        let data, error
        
        if (pregnancyId) {
          ({ data, error } = await api.getPregnancyPosts(pregnancyId))
        } else {
          ({ data, error } = await api.getFamilyPosts())
        }
        
        if (error) {
          throw new Error(`Failed to fetch posts: ${error}`)
        }
        
        this.posts = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching posts:', err)
      } finally {
        this.loading = false
      }
    },

    async createPost(postData: PostCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createPost(postData)
        
        if (error) {
          throw new Error(`Failed to create post: ${error}`)
        }
        
        if (data) {
          this.posts.unshift(data) // Add to beginning for chronological order
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating post:', err)
        throw err
      }
    },

    async updatePost(postId: string, postData: PostUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updatePost(postId, postData)
        
        if (error) {
          throw new Error(`Failed to update post: ${error}`)
        }
        
        if (data) {
          const index = this.posts.findIndex(post => post.id === postId)
          if (index !== -1) {
            this.posts[index] = data
          }
          
          // Update current post if it's the one being updated
          if (this.currentPost?.id === postId) {
            this.currentPost = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating post:', err)
        throw err
      }
    },

    async deletePost(postId: string) {
      try {
        const api = useApi()
        const { error } = await api.deletePost(postId)
        
        if (error) {
          throw new Error(`Failed to delete post: ${error}`)
        }
        
        this.posts = this.posts.filter(post => post.id !== postId)
        
        // Clear current post if it was deleted
        if (this.currentPost?.id === postId) {
          this.currentPost = null
        }
        
        // Clear comments for deleted post
        delete this.comments[postId]
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting post:', err)
        throw err
      }
    },

    async fetchPostComments(postId: string) {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getPostComments(postId)
        
        if (error) {
          throw new Error(`Failed to fetch comments: ${error}`)
        }
        
        this.comments[postId] = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching comments:', err)
      } finally {
        this.loading = false
      }
    },

    async createComment(commentData: CommentCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createComment(commentData)
        
        if (error) {
          throw new Error(`Failed to create comment: ${error}`)
        }
        
        if (data) {
          const postId = commentData.post_id
          if (!this.comments[postId]) {
            this.comments[postId] = []
          }
          this.comments[postId].push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating comment:', err)
        throw err
      }
    },

    async updateComment(commentId: string, commentData: CommentUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateComment(commentId, commentData)
        
        if (error) {
          throw new Error(`Failed to update comment: ${error}`)
        }
        
        if (data) {
          // Find and update comment in the appropriate post's comments
          for (const postId in this.comments) {
            const index = this.comments[postId].findIndex(comment => comment.id === commentId)
            if (index !== -1) {
              this.comments[postId][index] = data
              break
            }
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating comment:', err)
        throw err
      }
    },

    async deleteComment(commentId: string) {
      try {
        const api = useApi()
        const { error } = await api.deleteComment(commentId)
        
        if (error) {
          throw new Error(`Failed to delete comment: ${error}`)
        }
        
        // Remove comment from all post comment arrays
        for (const postId in this.comments) {
          this.comments[postId] = this.comments[postId].filter(comment => comment.id !== commentId)
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting comment:', err)
        throw err
      }
    },

    async likePost(postId: string) {
      try {
        const api = useApi()
        const { error } = await api.likePost(postId)
        
        if (error) {
          throw new Error(`Failed to like post: ${error}`)
        }
        
        // Update like count in local state
        const post = this.getPostById(postId)
        if (post) {
          post.like_count = (post.like_count || 0) + 1
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error liking post:', err)
        throw err
      }
    },

    async viewPost(postData: PostView) {
      try {
        const api = useApi()
        const { error } = await api.viewPost(postData)
        
        if (error) {
          throw new Error(`Failed to record post view: ${error}`)
        }
        
        // Update view count in local state
        const post = this.getPostById(postData.post_id)
        if (post) {
          post.view_count = (post.view_count || 0) + 1
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error recording post view:', err)
        throw err
      }
    },

    async sharePost(shareData: PostShare) {
      try {
        const api = useApi()
        const { error } = await api.sharePost(shareData.post_id, shareData)
        
        if (error) {
          throw new Error(`Failed to share post: ${error}`)
        }
        
        // Update share count in local state
        const post = this.getPostById(shareData.post_id)
        if (post) {
          post.share_count = (post.share_count || 0) + 1
        }
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error sharing post:', err)
        throw err
      }
    },

    setCurrentPost(post: Post) {
      this.currentPost = post
      // Fetch comments for the current post if not already loaded
      if (!this.comments[post.id]) {
        this.fetchPostComments(post.id)
      }
    },

    reset() {
      this.posts = []
      this.comments = {}
      this.currentPost = null
      this.loading = false
      this.error = null
    }
  }
})