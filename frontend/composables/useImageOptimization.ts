import { ref, computed, onMounted } from 'vue'

interface ImageOptimizationConfig {
  enableWebP?: boolean
  enableAVIF?: boolean
  enableProgressiveLoading?: boolean
  placeholderQuality?: number
  targetSizes?: number[]
  lazyLoadingThreshold?: number
  pregnancyTheme?: boolean
}

interface OptimizedImageData {
  originalSrc: string
  webpSrc?: string
  avifSrc?: string
  placeholderSrc?: string
  srcSet: string
  sizes: string
  loaded: boolean
  error: boolean
}

interface PregnancyPlaceholders {
  general: string
  ultrasound: string
  belly: string
  milestone: string
  family: string
}

export const useImageOptimization = (config: ImageOptimizationConfig = {}) => {
  const {
    enableWebP = true,
    enableAVIF = true,
    enableProgressiveLoading = true,
    placeholderQuality = 20,
    targetSizes = [320, 640, 960, 1280, 1920],
    lazyLoadingThreshold = 0.1,
    pregnancyTheme = true
  } = config

  // Browser support detection
  const webpSupported = ref(false)
  const avifSupported = ref(false)
  const supportsIntersectionObserver = ref(false)

  // Pregnancy-themed placeholders
  const pregnancyPlaceholders = ref<PregnancyPlaceholders>({
    general: '',
    ultrasound: '',
    belly: '',
    milestone: '',
    family: ''
  })

  // Performance metrics
  const optimizationMetrics = ref({
    totalImages: 0,
    optimizedImages: 0,
    bytessaved: 0,
    loadTimeReduction: 0
  })

  /**
   * Detect browser capabilities for modern image formats
   */
  async function detectBrowserSupport(): Promise<void> {
    if (typeof window === 'undefined') return

    // Test WebP support
    try {
      const webpTest = await createTestImage(
        'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA'
      )
      webpSupported.value = webpTest.width === 1
    } catch {
      webpSupported.value = false
    }

    // Test AVIF support  
    try {
      const avifTest = await createTestImage(
        'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A='
      )
      avifSupported.value = avifTest.width === 2
    } catch {
      avifSupported.value = false
    }

    // Check Intersection Observer support
    supportsIntersectionObserver.value = 'IntersectionObserver' in window
  }

  /**
   * Create test image for format support detection
   */
  function createTestImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = src
    })
  }

  /**
   * Generate pregnancy-themed placeholder images
   */
  async function generatePregnancyPlaceholders(): Promise<void> {
    if (!pregnancyTheme) return

    const canvas = document.createElement('canvas')
    canvas.width = 400
    canvas.height = 300
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    // Generate different placeholder types
    const placeholders: Array<{ key: keyof PregnancyPlaceholders; color: string; icon: string }> = [
      { key: 'general', color: '#FFF3E0', icon: '👶' },
      { key: 'ultrasound', color: '#E8F5E8', icon: '📱' },
      { key: 'belly', color: '#FCE4EC', icon: '🤱' },
      { key: 'milestone', color: '#F3E5F5', icon: '🎉' },
      { key: 'family', color: '#FFF8E1', icon: '👨‍👩‍👧‍👦' }
    ]

    for (const placeholder of placeholders) {
      // Create gentle gradient
      const gradient = ctx.createLinearGradient(0, 0, 400, 300)
      gradient.addColorStop(0, placeholder.color)
      gradient.addColorStop(1, adjustColorBrightness(placeholder.color, -10))
      
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, 400, 300)

      // Add subtle pattern
      ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
      for (let i = 0; i < 20; i++) {
        for (let j = 0; j < 15; j++) {
          if ((i + j) % 2) {
            ctx.fillRect(i * 20, j * 20, 10, 10)
          }
        }
      }

      // Add centered icon
      ctx.font = '48px system-ui'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
      ctx.fillText(placeholder.icon, 200, 150)

      // Convert to data URL
      pregnancyPlaceholders.value[placeholder.key] = canvas.toDataURL('image/jpeg', placeholderQuality / 100)
    }
  }

  /**
   * Adjust color brightness for gradients
   */
  function adjustColorBrightness(hex: string, percent: number): string {
    // Remove # if present
    hex = hex.replace('#', '')
    
    // Parse RGB
    const num = parseInt(hex, 16)
    const r = (num >> 16) + percent
    const g = (num >> 8 & 0x00FF) + percent
    const b = (num & 0x0000FF) + percent
    
    return `#${(1 << 24 | (r < 255 ? r < 1 ? 0 : r : 255) << 16 | 
                 (g < 255 ? g < 1 ? 0 : g : 255) << 8 | 
                 (b < 255 ? b < 1 ? 0 : b : 255)).toString(16).slice(1)}`
  }

  /**
   * Generate optimized image URLs with multiple formats and sizes
   */
  function generateOptimizedImageData(
    originalSrc: string, 
    maxWidth: number = 1200,
    aspectRatio: number = 16/9,
    imageType: keyof PregnancyPlaceholders = 'general'
  ): OptimizedImageData {
    const baseUrl = new URL(originalSrc, window.location.origin)
    
    // Generate different size variants
    const srcSetEntries: string[] = []
    const webpSrcSetEntries: string[] = []
    const avifSrcSetEntries: string[] = []

    for (const size of targetSizes) {
      if (size <= maxWidth) {
        // Original format
        const originalUrl = new URL(baseUrl)
        originalUrl.searchParams.set('w', size.toString())
        originalUrl.searchParams.set('h', Math.round(size / aspectRatio).toString())
        originalUrl.searchParams.set('q', '85')
        srcSetEntries.push(`${originalUrl.toString()} ${size}w`)

        // WebP format
        if (enableWebP && webpSupported.value) {
          const webpUrl = new URL(baseUrl)
          webpUrl.searchParams.set('w', size.toString())
          webpUrl.searchParams.set('h', Math.round(size / aspectRatio).toString())
          webpUrl.searchParams.set('q', '85')
          webpUrl.searchParams.set('fm', 'webp')
          webpSrcSetEntries.push(`${webpUrl.toString()} ${size}w`)
        }

        // AVIF format  
        if (enableAVIF && avifSupported.value) {
          const avifUrl = new URL(baseUrl)
          avifUrl.searchParams.set('w', size.toString())
          avifUrl.searchParams.set('h', Math.round(size / aspectRatio).toString())
          avifUrl.searchParams.set('q', '75') // AVIF can use lower quality
          avifUrl.searchParams.set('fm', 'avif')
          avifSrcSetEntries.push(`${avifUrl.toString()} ${size}w`)
        }
      }
    }

    return {
      originalSrc,
      webpSrc: webpSrcSetEntries.length > 0 ? webpSrcSetEntries.join(', ') : undefined,
      avifSrc: avifSrcSetEntries.length > 0 ? avifSrcSetEntries.join(', ') : undefined,
      placeholderSrc: pregnancyPlaceholders.value[imageType],
      srcSet: srcSetEntries.join(', '),
      sizes: '(max-width: 640px) 100vw, (max-width: 1200px) 50vw, 33vw',
      loaded: false,
      error: false
    }
  }

  /**
   * Progressive image loading with format selection
   */
  async function loadProgressiveImage(
    imgElement: HTMLImageElement,
    imageData: OptimizedImageData
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const startTime = performance.now()

      // Set initial placeholder
      if (imageData.placeholderSrc) {
        imgElement.src = imageData.placeholderSrc
        imgElement.style.filter = 'blur(5px)'
        imgElement.style.transition = 'filter 0.3s ease-out'
      }

      // Create picture element for format selection if not exists
      let pictureElement = imgElement.parentElement
      if (pictureElement?.tagName !== 'PICTURE') {
        pictureElement = document.createElement('picture')
        imgElement.parentNode?.insertBefore(pictureElement, imgElement)
        pictureElement.appendChild(imgElement)
      }

      // Add source elements for modern formats
      if (imageData.avifSrc && avifSupported.value) {
        const avifSource = document.createElement('source')
        avifSource.type = 'image/avif'
        avifSource.srcset = imageData.avifSrc
        avifSource.sizes = imageData.sizes
        pictureElement.insertBefore(avifSource, imgElement)
      }

      if (imageData.webpSrc && webpSupported.value) {
        const webpSource = document.createElement('source')
        webpSource.type = 'image/webp'
        webpSource.srcset = imageData.webpSrc
        webpSource.sizes = imageData.sizes
        pictureElement.insertBefore(webpSource, imgElement)
      }

      // Set up main image
      imgElement.srcset = imageData.srcSet
      imgElement.sizes = imageData.sizes
      imgElement.loading = 'lazy'

      imgElement.onload = () => {
        const loadTime = performance.now() - startTime
        
        // Remove blur effect
        imgElement.style.filter = 'none'
        
        // Update metrics
        optimizationMetrics.value.optimizedImages++
        optimizationMetrics.value.loadTimeReduction += Math.max(0, 1000 - loadTime)
        
        imageData.loaded = true
        resolve()
      }

      imgElement.onerror = () => {
        imageData.error = true
        reject(new Error('Failed to load optimized image'))
      }

      // Start loading by setting the src
      if (!imgElement.src || imgElement.src === imageData.placeholderSrc) {
        imgElement.src = imageData.originalSrc
      }
    })
  }

  /**
   * Lazy load images with intersection observer
   */
  function setupLazyLoading(
    container: HTMLElement,
    imageSelector: string = 'img[data-lazy-src]'
  ): void {
    if (!supportsIntersectionObserver.value) {
      // Fallback for browsers without Intersection Observer
      const images = container.querySelectorAll(imageSelector)
      images.forEach(async (img) => {
        const imgElement = img as HTMLImageElement
        const lazySrc = imgElement.dataset.lazySrc
        const imageType = (imgElement.dataset.imageType as keyof PregnancyPlaceholders) || 'general'
        
        if (lazySrc) {
          const imageData = generateOptimizedImageData(lazySrc, 1200, 16/9, imageType)
          await loadProgressiveImage(imgElement, imageData)
        }
      })
      return
    }

    const observer = new IntersectionObserver(
      async (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const imgElement = entry.target as HTMLImageElement
            const lazySrc = imgElement.dataset.lazySrc
            const imageType = (imgElement.dataset.imageType as keyof PregnancyPlaceholders) || 'general'

            if (lazySrc) {
              try {
                const imageData = generateOptimizedImageData(lazySrc, 1200, 16/9, imageType)
                await loadProgressiveImage(imgElement, imageData)
                observer.unobserve(imgElement)
              } catch (error) {
                console.warn('Failed to load lazy image:', error)
              }
            }
          }
        }
      },
      {
        threshold: lazyLoadingThreshold,
        rootMargin: '50px 0px 200px 0px' // Start loading before image is visible
      }
    )

    // Observe all lazy images
    const images = container.querySelectorAll(imageSelector)
    images.forEach(img => observer.observe(img))
  }

  /**
   * Preload critical images
   */
  async function preloadCriticalImages(imageSrcs: string[]): Promise<void> {
    const preloadPromises = imageSrcs.map(async (src) => {
      const imageData = generateOptimizedImageData(src)
      
      // Preload the most optimized format available
      const preloadSrc = imageData.avifSrc?.split(' ')[0] || 
                        imageData.webpSrc?.split(' ')[0] || 
                        imageData.originalSrc

      const link = document.createElement('link')
      link.rel = 'preload'
      link.as = 'image'
      link.href = preloadSrc
      
      if (imageData.avifSrc && avifSupported.value) {
        link.type = 'image/avif'
      } else if (imageData.webpSrc && webpSupported.value) {
        link.type = 'image/webp'
      }

      document.head.appendChild(link)
    })

    await Promise.all(preloadPromises)
  }

  /**
   * Calculate bytes saved through optimization
   */
  function calculateBytesSaved(originalSize: number, optimizedSize: number): number {
    const saved = originalSize - optimizedSize
    optimizationMetrics.value.bytesaved += saved
    return saved
  }

  /**
   * Get pregnancy-appropriate placeholder for image type
   */
  function getPregnancyPlaceholder(imageType: keyof PregnancyPlaceholders = 'general'): string {
    return pregnancyPlaceholders.value[imageType] || pregnancyPlaceholders.value.general
  }

  // Computed properties
  const browserSupport = computed(() => ({
    webp: webpSupported.value,
    avif: avifSupported.value,
    intersectionObserver: supportsIntersectionObserver.value
  }))

  const optimizationStats = computed(() => ({
    ...optimizationMetrics.value,
    optimizationRate: optimizationMetrics.value.totalImages > 0 
      ? (optimizationMetrics.value.optimizedImages / optimizationMetrics.value.totalImages) * 100 
      : 0
  }))

  // Initialize on mount
  onMounted(async () => {
    await detectBrowserSupport()
    await generatePregnancyPlaceholders()
  })

  return {
    // State
    browserSupport,
    optimizationStats,
    pregnancyPlaceholders,

    // Methods
    generateOptimizedImageData,
    loadProgressiveImage,
    setupLazyLoading,
    preloadCriticalImages,
    getPregnancyPlaceholder,
    calculateBytesSaved,

    // Config
    enableWebP,
    enableAVIF,
    enableProgressiveLoading
  }
}