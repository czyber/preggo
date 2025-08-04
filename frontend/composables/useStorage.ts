import { v4 as uuidv4 } from 'uuid'

export const useStorage = () => {
  const supabase = useSupabase()
  const auth = useAuth()

  // Storage bucket names
  const BUCKETS = {
    PREGNANCY_MEDIA: 'pregnancy-photos',
    PROFILE_IMAGES: 'profile-images',
    ULTRASOUNDS: 'ultrasounds',
    DOCUMENTS: 'documents',
    MEMORY_BOOKS: 'memory-books'
  }

  // Maximum file sizes (in bytes)
  const MAX_FILE_SIZE = {
    IMAGE: 10 * 1024 * 1024, // 10MB
    VIDEO: 50 * 1024 * 1024, // 50MB
    DOCUMENT: 20 * 1024 * 1024 // 20MB
  }

  // Allowed file types
  const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg']
  const ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'image/jpeg', 'image/png']

  /**
   * Upload a file to Supabase storage
   */
  async function uploadFile(
    file: File,
    bucket: string = BUCKETS.PREGNANCY_MEDIA,
    path?: string
  ): Promise<{ url: string; path: string; error?: string }> {
    try {
      // Validate user is authenticated
      if (!auth.user.value) {
        throw new Error('User must be authenticated to upload files')
      }

      // Validate file size
      if (file.size > getMaxFileSize(file.type)) {
        throw new Error(`File size exceeds maximum allowed size`)
      }

      // Validate file type
      if (!isAllowedFileType(file.type)) {
        throw new Error(`File type ${file.type} is not allowed`)
      }

      // Generate unique file path
      const fileExt = file.name.split('.').pop()
      const fileName = `${uuidv4()}.${fileExt}`
      const filePath = path 
        ? `${path}/${fileName}`
        : `${auth.user.value.id}/${new Date().getFullYear()}/${fileName}`

      // Upload file
      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        })

      if (error) {
        throw error
      }

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from(bucket)
        .getPublicUrl(data.path)

      return {
        url: publicUrl,
        path: data.path
      }
    } catch (error: any) {
      console.error('File upload error:', error)
      return {
        url: '',
        path: '',
        error: error.message || 'Failed to upload file'
      }
    }
  }

  /**
   * Upload multiple files
   */
  async function uploadMultipleFiles(
    files: File[],
    bucket: string = BUCKETS.PREGNANCY_MEDIA,
    path?: string
  ): Promise<Array<{ file: File; url: string; path: string; error?: string }>> {
    const uploadPromises = files.map(file => 
      uploadFile(file, bucket, path).then(result => ({
        file,
        ...result
      }))
    )

    return Promise.all(uploadPromises)
  }

  /**
   * Delete a file from storage
   */
  async function deleteFile(
    filePath: string,
    bucket: string = BUCKETS.PREGNANCY_MEDIA
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await supabase.storage
        .from(bucket)
        .remove([filePath])

      if (error) {
        throw error
      }

      return { success: true }
    } catch (error: any) {
      console.error('File deletion error:', error)
      return {
        success: false,
        error: error.message || 'Failed to delete file'
      }
    }
  }

  /**
   * Generate a signed URL for private file access
   */
  async function getSignedUrl(
    filePath: string,
    bucket: string,
    expiresIn: number = 3600 // 1 hour default
  ): Promise<{ url: string; error?: string }> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .createSignedUrl(filePath, expiresIn)

      if (error) {
        throw error
      }

      return { url: data.signedUrl }
    } catch (error: any) {
      console.error('Signed URL generation error:', error)
      return {
        url: '',
        error: error.message || 'Failed to generate signed URL'
      }
    }
  }

  /**
   * Get the maximum file size based on file type
   */
  function getMaxFileSize(mimeType: string): number {
    if (ALLOWED_IMAGE_TYPES.includes(mimeType)) {
      return MAX_FILE_SIZE.IMAGE
    }
    if (ALLOWED_VIDEO_TYPES.includes(mimeType)) {
      return MAX_FILE_SIZE.VIDEO
    }
    if (ALLOWED_DOCUMENT_TYPES.includes(mimeType)) {
      return MAX_FILE_SIZE.DOCUMENT
    }
    return MAX_FILE_SIZE.IMAGE // Default
  }

  /**
   * Check if file type is allowed
   */
  function isAllowedFileType(mimeType: string): boolean {
    return [
      ...ALLOWED_IMAGE_TYPES,
      ...ALLOWED_VIDEO_TYPES,
      ...ALLOWED_DOCUMENT_TYPES
    ].includes(mimeType)
  }

  /**
   * Generate a thumbnail from video file
   */
  async function generateVideoThumbnail(
    videoFile: File
  ): Promise<{ thumbnail: Blob | null; error?: string }> {
    try {
      const video = document.createElement('video')
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')

      return new Promise((resolve) => {
        video.onloadedmetadata = () => {
          video.currentTime = video.duration * 0.1 // Get frame at 10% of video
        }

        video.onseeked = () => {
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          context?.drawImage(video, 0, 0, canvas.width, canvas.height)
          
          canvas.toBlob((blob) => {
            resolve({ thumbnail: blob })
          }, 'image/jpeg', 0.8)
        }

        video.onerror = () => {
          resolve({ 
            thumbnail: null, 
            error: 'Failed to generate video thumbnail' 
          })
        }

        video.src = URL.createObjectURL(videoFile)
      })
    } catch (error: any) {
      return {
        thumbnail: null,
        error: error.message || 'Failed to generate thumbnail'
      }
    }
  }

  /**
   * Get file metadata
   */
  function getFileMetadata(file: File) {
    return {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: new Date(file.lastModified),
      extension: file.name.split('.').pop()?.toLowerCase() || '',
      isImage: ALLOWED_IMAGE_TYPES.includes(file.type),
      isVideo: ALLOWED_VIDEO_TYPES.includes(file.type),
      isDocument: ALLOWED_DOCUMENT_TYPES.includes(file.type)
    }
  }

  /**
   * Format file size for display
   */
  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return {
    // Constants
    BUCKETS,
    MAX_FILE_SIZE,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    ALLOWED_DOCUMENT_TYPES,
    
    // Methods
    uploadFile,
    uploadMultipleFiles,
    deleteFile,
    getSignedUrl,
    generateVideoThumbnail,
    
    // Utilities
    getFileMetadata,
    formatFileSize,
    getMaxFileSize,
    isAllowedFileType
  }
}
