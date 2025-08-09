import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useImageOptimization } from './useImageOptimization'
import { useVirtualScrolling } from './useVirtualScrolling'
import { usePerformanceMonitoring } from './usePerformanceMonitoring'

interface PerformanceConfig {
  enableLazyLoading?: boolean
  enableImageOptimization?: boolean
  enableVirtualScrolling?: boolean
  enablePreloading?: boolean
  batchSize?: number
  intersectionThreshold?: number
  rootMargin?: string
  pregnancyOptimizations?: boolean
}

interface LazyElement {
  element: HTMLElement
  observer: IntersectionObserver
  loaded: boolean
  priority: 'high' | 'medium' | 'low'
}

interface ImageOptimization {
  enableWebP?: boolean
  enableProgressiveLoading?: boolean
  placeholderQuality?: number
  targetSizes?: string[]
}

export const useFeedPerformance = (feedItems: any[] = [], config: PerformanceConfig = {}) => {
  const {
    enableLazyLoading = true,
    enableImageOptimization = true,
    enableVirtualScrolling = true,
    enablePreloading = true,
    batchSize = 5,
    intersectionThreshold = 0.1,
    rootMargin = '50px 0px 200px 0px',
    pregnancyOptimizations = true
  } = config

  // Initialize performance optimizations
  const imageOptimization = useImageOptimization({
    enableWebP: true,
    enableAVIF: true,
    enableProgressiveLoading: true,
    pregnancyTheme: pregnancyOptimizations
  })

  const virtualScrolling = useVirtualScrolling(feedItems, {
    itemHeight: 300,
    bufferSize: 3,
    containerHeight: 800,
    pregnancyAware: pregnancyOptimizations,
    smoothScrolling: true,
    dynamicHeight: true
  })

  const performanceMonitoring = usePerformanceMonitoring({
    enableRealUserMonitoring: true,
    enableCoreWebVitals: true,
    enablePregnancyMetrics: pregnancyOptimizations,
    sampleRate: 0.1
  })

  // Performance state
  const lazyElements = ref<Map<string, LazyElement>>(new Map())
  const visibleElements = ref<Set<string>>(new Set())
  const loadingElements = ref<Set<string>>(new Set())
  const preloadedContent = ref<Map<string, any>>(new Map())
  const performanceMetrics = ref({
    renderTime: 0,
    loadTime: 0,
    memoryUsage: 0,
    visibleStories: 0
  })

  // Intersection Observer for lazy loading
  let intersectionObserver: IntersectionObserver | null = null

  /**
   * Initialize lazy loading with pregnancy-focused optimizations
   */
  function initializeLazyLoading(): void {
    if (!enableLazyLoading || typeof window === 'undefined') return

    intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const elementId = entry.target.getAttribute('data-story-id')
          if (!elementId) return

          if (entry.isIntersecting) {
            handleElementVisible(elementId, entry.target as HTMLElement)
          } else {
            handleElementHidden(elementId)
          }
        })
      },
      {
        threshold: intersectionThreshold,
        rootMargin
      }
    )
  }

  /**
   * Register element for lazy loading
   */
  function registerLazyElement(
    elementId: string,
    element: HTMLElement,
    priority: 'high' | 'medium' | 'low' = 'medium'
  ): void {
    if (!intersectionObserver || !enableLazyLoading) return

    const lazyElement: LazyElement = {
      element,
      observer: intersectionObserver,
      loaded: false,
      priority
    }

    lazyElements.value.set(elementId, lazyElement)
    intersectionObserver.observe(element)

    // Set initial placeholder
    setPlaceholderContent(element, priority)
  }

  /**
   * Handle when element becomes visible
   */
  function handleElementVisible(elementId: string, element: HTMLElement): void {
    if (visibleElements.value.has(elementId)) return

    visibleElements.value.add(elementId)
    performanceMetrics.value.visibleStories = visibleElements.value.size

    const lazyElement = lazyElements.value.get(elementId)
    if (lazyElement && !lazyElement.loaded) {
      loadStoryContent(elementId, element, lazyElement.priority)
    }

    // Preload nearby content
    if (enablePreloading) {
      preloadNearbyContent(elementId)
    }
  }

  /**
   * Handle when element becomes hidden
   */
  function handleElementHidden(elementId: string): void {
    visibleElements.value.delete(elementId)
    performanceMetrics.value.visibleStories = visibleElements.value.size

    // Optional: Unload non-critical content to save memory
    const lazyElement = lazyElements.value.get(elementId)
    if (lazyElement && lazyElement.priority === 'low') {
      // For low priority elements, consider unloading after they've been hidden for a while
      setTimeout(() => {
        if (!visibleElements.value.has(elementId)) {
          unloadLowPriorityContent(elementId)
        }
      }, 30000) // 30 seconds
    }
  }

  /**
   * Load story content with optimizations
   */
  async function loadStoryContent(
    elementId: string,
    element: HTMLElement,
    priority: 'high' | 'medium' | 'low'
  ): Promise<void> {
    if (loadingElements.value.has(elementId)) return

    loadingElements.value.add(elementId)
    const startTime = performance.now()

    try {
      // Check if content is preloaded
      const preloadedData = preloadedContent.value.get(elementId)
      if (preloadedData) {
        await applyPreloadedContent(element, preloadedData)
      } else {
        await loadContentProgressive(element, priority)
      }

      const lazyElement = lazyElements.value.get(elementId)
      if (lazyElement) {
        lazyElement.loaded = true
      }

      // Remove placeholder
      removePlaceholder(element)

    } catch (error) {
      console.warn('Failed to load story content:', error)
      // Keep placeholder or show gentle error state
      setErrorPlaceholder(element)
    } finally {
      loadingElements.value.delete(elementId)
      
      const loadTime = performance.now() - startTime
      performanceMetrics.value.loadTime = loadTime
    }
  }

  /**
   * Load content progressively based on priority
   */
  async function loadContentProgressive(
    element: HTMLElement,
    priority: 'high' | 'medium' | 'low'
  ): Promise<void> {
    // Load text content first (fast)
    const textElements = element.querySelectorAll('[data-lazy-text]')
    textElements.forEach((el) => {
      el.classList.remove('lazy-placeholder')
      el.classList.add('loaded')
    })

    // Then load images based on priority
    const images = element.querySelectorAll('img[data-lazy-src]')
    
    if (priority === 'high') {
      // Load all images immediately
      await Promise.all(Array.from(images).map(loadImage))
    } else {
      // Load images progressively
      for (const img of Array.from(images)) {
        await loadImage(img as HTMLImageElement)
        await new Promise(resolve => setTimeout(resolve, 50)) // Small delay between images
      }
    }
  }

  /**
   * Optimized image loading with pregnancy-themed placeholders
   */
  function loadImage(img: HTMLImageElement): Promise<void> {
    return new Promise((resolve, reject) => {
      const lazySrc = img.getAttribute('data-lazy-src')
      if (!lazySrc) {
        resolve()
        return
      }

      // Create optimized image URLs
      const optimizedSrc = enableImageOptimization 
        ? getOptimizedImageUrl(lazySrc, img) 
        : lazySrc

      const tempImg = new Image()
      
      tempImg.onload = () => {
        // Smooth transition from placeholder
        img.style.opacity = '0'
        img.src = optimizedSrc
        img.removeAttribute('data-lazy-src')
        
        // Fade in
        requestAnimationFrame(() => {
          img.style.transition = 'opacity 0.3s ease-out'
          img.style.opacity = '1'
          resolve()
        })
      }

      tempImg.onerror = () => {
        // Keep placeholder on error
        reject(new Error('Failed to load image'))
      }

      tempImg.src = optimizedSrc
    })
  }

  /**
   * Generate optimized image URLs
   */
  function getOptimizedImageUrl(originalUrl: string, imgElement: HTMLImageElement): string {
    if (!enableImageOptimization) return originalUrl

    const { width, height } = imgElement.getBoundingClientRect()
    const devicePixelRatio = window.devicePixelRatio || 1
    
    // Calculate optimal dimensions
    const targetWidth = Math.ceil(width * devicePixelRatio)
    const targetHeight = Math.ceil(height * devicePixelRatio)

    // Add optimization parameters (this would depend on your image service)
    const url = new URL(originalUrl)
    url.searchParams.set('w', targetWidth.toString())
    url.searchParams.set('h', targetHeight.toString())
    url.searchParams.set('q', '85') // Quality
    url.searchParams.set('fm', 'webp') // Format

    return url.toString()
  }

  /**
   * Set pregnancy-themed placeholders
   */
  function setPlaceholderContent(element: HTMLElement, priority: 'high' | 'medium' | 'low'): void {
    // Add skeleton loading with pregnancy theme
    const placeholders = element.querySelectorAll('[data-lazy-text], img[data-lazy-src]')
    
    placeholders.forEach((el) => {
      el.classList.add('lazy-placeholder')
      
      if (el.tagName === 'IMG') {
        // Pregnancy-themed placeholder for images
        const canvas = document.createElement('canvas')
        canvas.width = 300
        canvas.height = 200
        const ctx = canvas.getContext('2d')
        
        if (ctx) {
          // Gentle gradient background
          const gradient = ctx.createLinearGradient(0, 0, 300, 200)
          gradient.addColorStop(0, '#FFF3E0')
          gradient.addColorStop(1, '#F8BBD0')
          ctx.fillStyle = gradient
          ctx.fillRect(0, 0, 300, 200)
          
          // Add gentle icon
          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
          ctx.font = '48px serif'
          ctx.textAlign = 'center'
          ctx.fillText('👶', 150, 120)
        }
        
        (el as HTMLImageElement).src = canvas.toDataURL()
      }
    })
  }

  /**
   * Remove placeholder content
   */
  function removePlaceholder(element: HTMLElement): void {
    const placeholders = element.querySelectorAll('.lazy-placeholder')
    placeholders.forEach((el) => {
      el.classList.remove('lazy-placeholder')
      el.classList.add('loaded')
    })
  }

  /**
   * Set gentle error placeholder
   */
  function setErrorPlaceholder(element: HTMLElement): void {
    const errorElements = element.querySelectorAll('img[data-lazy-src]')
    errorElements.forEach((img) => {
      const errorDiv = document.createElement('div')
      errorDiv.className = 'gentle-error-placeholder'
      errorDiv.innerHTML = `
        <div class="error-content">
          <span class="error-icon">🌸</span>
          <span class="error-text">Content loading gently...</span>
        </div>
      `
      img.parentNode?.replaceChild(errorDiv, img)
    })
  }

  /**
   * Preload nearby content
   */
  function preloadNearbyContent(currentElementId: string): void {
    if (!enablePreloading) return

    // Get elements near the current one
    const currentIndex = Array.from(lazyElements.value.keys()).indexOf(currentElementId)
    const preloadRange = 2 // Preload 2 items before and after

    for (let i = currentIndex - preloadRange; i <= currentIndex + preloadRange; i++) {
      const elementId = Array.from(lazyElements.value.keys())[i]
      if (elementId && elementId !== currentElementId && !preloadedContent.value.has(elementId)) {
        queuePreload(elementId)
      }
    }
  }

  /**
   * Queue content for preloading
   */
  function queuePreload(elementId: string): void {
    // Use requestIdleCallback if available for non-critical preloading
    const preloadFn = () => {
      const element = lazyElements.value.get(elementId)?.element
      if (element && !loadingElements.value.has(elementId)) {
        preloadStoryContent(elementId, element)
      }
    }

    if ('requestIdleCallback' in window) {
      (window as any).requestIdleCallback(preloadFn)
    } else {
      setTimeout(preloadFn, 100)
    }
  }

  /**
   * Preload story content
   */
  async function preloadStoryContent(elementId: string, element: HTMLElement): Promise<void> {
    try {
      const images = element.querySelectorAll('img[data-lazy-src]')
      const imagePromises = Array.from(images).map((img) => {
        const src = img.getAttribute('data-lazy-src')
        if (src) {
          return preloadImage(src)
        }
      }).filter(Boolean)

      const preloadedImages = await Promise.all(imagePromises)
      preloadedContent.value.set(elementId, { images: preloadedImages })
    } catch (error) {
      console.debug('Preload failed for', elementId, error)
    }
  }

  /**
   * Preload individual image
   */
  function preloadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = src
    })
  }

  /**
   * Apply preloaded content
   */
  async function applyPreloadedContent(element: HTMLElement, preloadedData: any): Promise<void> {
    // Apply preloaded images
    if (preloadedData.images) {
      const images = element.querySelectorAll('img[data-lazy-src]')
      images.forEach((img, index) => {
        const preloadedImg = preloadedData.images[index]
        if (preloadedImg) {
          (img as HTMLImageElement).src = preloadedImg.src
          img.removeAttribute('data-lazy-src')
        }
      })
    }
  }

  /**
   * Unload low priority content to save memory
   */
  function unloadLowPriorityContent(elementId: string): void {
    const lazyElement = lazyElements.value.get(elementId)
    if (!lazyElement) return

    // Replace images with placeholders
    const images = lazyElement.element.querySelectorAll('img:not([data-lazy-src])')
    images.forEach((img) => {
      const placeholder = img.getAttribute('data-placeholder-src')
      if (placeholder) {
        img.setAttribute('data-lazy-src', (img as HTMLImageElement).src)
        ;(img as HTMLImageElement).src = placeholder
      }
    })

    lazyElement.loaded = false
  }

  /**
   * Monitor performance metrics
   */
  function startPerformanceMonitoring(): void {
    if (typeof window === 'undefined') return

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach((entry) => {
        if (entry.entryType === 'measure' && entry.name.includes('story-render')) {
          performanceMetrics.value.renderTime = entry.duration
        }
      })
    })

    observer.observe({ entryTypes: ['measure'] })

    // Monitor memory usage
    if ('memory' in performance) {
      setInterval(() => {
        const memInfo = (performance as any).memory
        performanceMetrics.value.memoryUsage = memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit
      }, 5000)
    }
  }

  /**
   * Batch DOM updates for better performance
   */
  function batchDOMUpdates(updates: Array<() => void>): Promise<void> {
    return new Promise((resolve) => {
      requestAnimationFrame(() => {
        updates.forEach((update) => {
          try {
            update()
          } catch (error) {
            console.warn('Batch update failed:', error)
          }
        })
        resolve()
      })
    })
  }

  /**
   * Cleanup resources
   */
  function cleanup(): void {
    if (intersectionObserver) {
      intersectionObserver.disconnect()
      intersectionObserver = null
    }

    lazyElements.value.clear()
    visibleElements.value.clear()
    loadingElements.value.clear()
    preloadedContent.value.clear()
  }

  // Lifecycle
  onMounted(() => {
    nextTick(() => {
      initializeLazyLoading()
      startPerformanceMonitoring()
    })
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // State
    performanceMetrics,
    visibleElements,
    loadingElements,

    // Methods
    registerLazyElement,
    loadImage,
    batchDOMUpdates,
    cleanup,

    // Config
    enableLazyLoading,
    enableImageOptimization,
    enableVirtualScrolling,
    enablePreloading
  }
}