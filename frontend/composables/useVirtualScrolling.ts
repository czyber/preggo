import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'

interface VirtualScrollConfig {
  itemHeight?: number
  bufferSize?: number
  containerHeight?: number
  pregnancyAware?: boolean
  smoothScrolling?: boolean
  dynamicHeight?: boolean
  overscan?: number
}

interface VirtualItem {
  id: string
  index: number
  height: number
  top: number
  visible: boolean
  rendered: boolean
  data: any
}

interface ScrollMetrics {
  scrollTop: number
  scrollHeight: number
  clientHeight: number
  velocity: number
  direction: 'up' | 'down' | 'idle'
}

interface PregnancyScrollBehavior {
  adaptiveSpeed: boolean
  fatigueMode: boolean
  comfortScrolling: boolean
  reduceMotion: boolean
}

export const useVirtualScrolling = <T = any>(
  items: T[],
  config: VirtualScrollConfig = {}
) => {
  const {
    itemHeight = 200,
    bufferSize = 5,
    containerHeight = 600,
    pregnancyAware = true,
    smoothScrolling = true,
    dynamicHeight = false,
    overscan = 3
  } = config

  // State
  const containerRef = ref<HTMLElement>()
  const listRef = ref<HTMLElement>()
  const scrollTop = ref(0)
  const isScrolling = ref(false)
  const scrollDirection = ref<'up' | 'down' | 'idle'>('idle')
  const scrollVelocity = ref(0)

  // Virtual scroll state
  const virtualItems = ref<VirtualItem[]>([])
  const visibleRange = reactive({
    start: 0,
    end: 0
  })
  const measuredHeights = ref<Map<string, number>>(new Map())
  const renderedItems = ref<Map<string, HTMLElement>>(new Map())

  // Pregnancy-specific behavior
  const pregnancyBehavior = reactive<PregnancyScrollBehavior>({
    adaptiveSpeed: true,
    fatigueMode: false,
    comfortScrolling: true,
    reduceMotion: false
  })

  // Performance metrics
  const performanceMetrics = reactive({
    totalItems: 0,
    renderedItems: 0,
    renderTime: 0,
    scrollPerformance: 0,
    memoryUsage: 0
  })

  // Scroll timing for performance monitoring
  let scrollTimeout: NodeJS.Timeout | null = null
  let lastScrollTime = 0
  let rafId: number | null = null

  /**
   * Initialize virtual scrolling
   */
  function initialize(): void {
    if (!containerRef.value) return

    updateVirtualItems()
    calculateVisibleRange()
    setupScrollListeners()
    
    if (pregnancyAware) {
      initializePregnancyBehaviors()
    }

    performanceMetrics.totalItems = items.length
  }

  /**
   * Update virtual items based on current data
   */
  function updateVirtualItems(): void {
    const newVirtualItems: VirtualItem[] = []
    let currentTop = 0

    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      const itemId = getItemId(item, i)
      const height = measuredHeights.value.get(itemId) || itemHeight
      
      newVirtualItems.push({
        id: itemId,
        index: i,
        height,
        top: currentTop,
        visible: false,
        rendered: false,
        data: item
      })

      currentTop += height
    }

    virtualItems.value = newVirtualItems
    calculateVisibleRange()
  }

  /**
   * Calculate which items should be visible
   */
  function calculateVisibleRange(): void {
    if (!containerRef.value || virtualItems.value.length === 0) return

    const containerTop = scrollTop.value
    const containerBottom = containerTop + containerHeight
    
    let startIndex = 0
    let endIndex = virtualItems.value.length - 1

    // Find start index with binary search for better performance
    for (let i = 0; i < virtualItems.value.length; i++) {
      const item = virtualItems.value[i]
      if (item.top + item.height > containerTop) {
        startIndex = Math.max(0, i - bufferSize - overscan)
        break
      }
    }

    // Find end index
    for (let i = startIndex; i < virtualItems.value.length; i++) {
      const item = virtualItems.value[i]
      if (item.top > containerBottom) {
        endIndex = Math.min(virtualItems.value.length - 1, i + bufferSize + overscan)
        break
      }
    }

    // Update visible range
    visibleRange.start = startIndex
    visibleRange.end = endIndex

    // Update visibility flags
    virtualItems.value.forEach((item, index) => {
      item.visible = index >= visibleRange.start && index <= visibleRange.end
    })

    performanceMetrics.renderedItems = endIndex - startIndex + 1
  }

  /**
   * Handle scroll events with pregnancy-aware optimizations
   */
  function handleScroll(event: Event): void {
    const target = event.target as HTMLElement
    const newScrollTop = target.scrollTop
    
    // Update scroll metrics
    const now = performance.now()
    scrollVelocity.value = Math.abs(newScrollTop - scrollTop.value) / (now - lastScrollTime || 1)
    scrollDirection.value = newScrollTop > scrollTop.value ? 'down' : 
                           newScrollTop < scrollTop.value ? 'up' : 'idle'
    scrollTop.value = newScrollTop
    lastScrollTime = now

    // Pregnancy-aware scroll handling
    if (pregnancyAware) {
      handlePregnancyScrollBehavior()
    }

    // Debounced scroll handling for performance
    isScrolling.value = true
    if (scrollTimeout) {
      clearTimeout(scrollTimeout)
    }

    scrollTimeout = setTimeout(() => {
      isScrolling.value = false
      scrollDirection.value = 'idle'
      scrollVelocity.value = 0
    }, 150)

    // Use RAF for smooth updates
    if (rafId) {
      cancelAnimationFrame(rafId)
    }

    rafId = requestAnimationFrame(() => {
      calculateVisibleRange()
      updatePerformanceMetrics()
    })
  }

  /**
   * Handle pregnancy-specific scroll behaviors
   */
  function handlePregnancyScrollBehavior(): void {
    // Adaptive scrolling based on fatigue mode
    if (pregnancyBehavior.fatigueMode) {
      const container = containerRef.value
      if (container) {
        // Slower, gentler scrolling when fatigued
        container.style.scrollBehavior = 'smooth'
        
        // Reduce scroll sensitivity for comfort
        if (scrollVelocity.value > 100) {
          // Dampen fast scrolling
          const dampened = scrollTop.value - (scrollVelocity.value * 0.3)
          container.scrollTop = Math.max(0, dampened)
        }
      }
    }

    // Comfort scrolling - reduce jarring movements
    if (pregnancyBehavior.comfortScrolling) {
      // Add gentle momentum and easing
      if (scrollVelocity.value > 50 && !isScrolling.value) {
        const container = containerRef.value
        if (container && smoothScrolling) {
          const easeOut = (t: number) => 1 - Math.pow(1 - t, 3)
          let start = 0
          const duration = 200
          const startScroll = container.scrollTop
          const targetScroll = startScroll + (scrollVelocity.value * scrollDirection.value === 'down' ? 1 : -1) * 20

          const animate = (timestamp: number) => {
            if (!start) start = timestamp
            const progress = Math.min((timestamp - start) / duration, 1)
            const easedProgress = easeOut(progress)
            
            container.scrollTop = startScroll + (targetScroll - startScroll) * easedProgress
            
            if (progress < 1) {
              requestAnimationFrame(animate)
            }
          }
          
          requestAnimationFrame(animate)
        }
      }
    }
  }

  /**
   * Initialize pregnancy-specific behaviors
   */
  function initializePregnancyBehaviors(): void {
    // Detect user preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      pregnancyBehavior.reduceMotion = true
    }

    // Time-based fatigue mode (evening hours)
    const currentHour = new Date().getHours()
    if (currentHour >= 18 || currentHour <= 6) {
      pregnancyBehavior.fatigueMode = true
    }

    // Battery level awareness (if available)
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        if (battery.level < 0.2) {
          pregnancyBehavior.adaptiveSpeed = true
          pregnancyBehavior.reduceMotion = true
        }
      })
    }
  }

  /**
   * Setup scroll event listeners
   */
  function setupScrollListeners(): void {
    if (!containerRef.value) return

    // Use passive listeners for better performance
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
    
    // Handle resize events
    window.addEventListener('resize', debounce(handleResize, 250), { passive: true })
    
    // Handle visibility changes for performance
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  /**
   * Handle container resize
   */
  function handleResize(): void {
    if (containerRef.value) {
      calculateVisibleRange()
    }
  }

  /**
   * Handle visibility changes to optimize performance
   */
  function handleVisibilityChange(): void {
    if (document.hidden) {
      // Pause updates when tab is not visible
      if (rafId) {
        cancelAnimationFrame(rafId)
        rafId = null
      }
    } else {
      // Resume updates when tab becomes visible
      calculateVisibleRange()
    }
  }

  /**
   * Measure item height dynamically
   */
  function measureItemHeight(itemId: string, element: HTMLElement): void {
    if (!dynamicHeight) return

    const rect = element.getBoundingClientRect()
    const height = rect.height
    
    const previousHeight = measuredHeights.value.get(itemId)
    if (previousHeight !== height) {
      measuredHeights.value.set(itemId, height)
      
      // Recalculate virtual items positions
      updateVirtualItems()
    }
    
    renderedItems.value.set(itemId, element)
  }

  /**
   * Get unique item identifier
   */
  function getItemId(item: T, index: number): string {
    // Try to use item's id property if available
    if (typeof item === 'object' && item !== null && 'id' in item) {
      return String((item as any).id)
    }
    return `item-${index}`
  }

  /**
   * Scroll to specific item
   */
  function scrollToItem(index: number, behavior: ScrollBehavior = 'smooth'): void {
    if (!containerRef.value || index < 0 || index >= virtualItems.value.length) return

    const item = virtualItems.value[index]
    const targetScrollTop = item.top

    // Pregnancy-aware scrolling
    if (pregnancyAware && pregnancyBehavior.comfortScrolling) {
      // Gentle scroll with easing
      containerRef.value.scrollTo({
        top: targetScrollTop,
        behavior: pregnancyBehavior.reduceMotion ? 'auto' : 'smooth'
      })
    } else {
      containerRef.value.scrollTo({
        top: targetScrollTop,
        behavior
      })
    }
  }

  /**
   * Scroll to top with pregnancy-aware behavior
   */
  function scrollToTop(): void {
    scrollToItem(0, pregnancyBehavior.reduceMotion ? 'auto' : 'smooth')
  }

  /**
   * Update performance metrics
   */
  function updatePerformanceMetrics(): void {
    const startTime = performance.now()
    
    // Measure render time
    requestAnimationFrame(() => {
      performanceMetrics.renderTime = performance.now() - startTime
    })

    // Measure scroll performance (FPS equivalent)
    const fps = 1000 / (performance.now() - lastScrollTime || 16.67)
    performanceMetrics.scrollPerformance = Math.min(60, fps)

    // Estimate memory usage
    performanceMetrics.memoryUsage = renderedItems.value.size * 0.1 // Rough estimate in MB
  }

  /**
   * Debounce utility
   */
  function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout | null = null
    return (...args: Parameters<T>) => {
      if (timeout) {
        clearTimeout(timeout)
      }
      timeout = setTimeout(() => func(...args), wait)
    }
  }

  /**
   * Cleanup resources
   */
  function cleanup(): void {
    if (containerRef.value) {
      containerRef.value.removeEventListener('scroll', handleScroll)
    }
    
    window.removeEventListener('resize', handleResize)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    
    if (scrollTimeout) {
      clearTimeout(scrollTimeout)
    }
    
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
    
    renderedItems.value.clear()
    measuredHeights.value.clear()
  }

  // Computed properties
  const visibleItems = computed(() => {
    return virtualItems.value.filter(item => item.visible)
  })

  const totalHeight = computed(() => {
    return virtualItems.value.reduce((sum, item) => sum + item.height, 0)
  })

  const scrollProgress = computed(() => {
    if (totalHeight.value <= containerHeight) return 1
    return Math.min(1, scrollTop.value / (totalHeight.value - containerHeight))
  })

  const isNearTop = computed(() => scrollTop.value < 100)
  const isNearBottom = computed(() => {
    const remaining = totalHeight.value - (scrollTop.value + containerHeight)
    return remaining < 100
  })

  // Pregnancy-specific computed properties
  const comfortableScrolling = computed(() => {
    return pregnancyAware && (
      pregnancyBehavior.comfortScrolling || 
      pregnancyBehavior.fatigueMode ||
      pregnancyBehavior.reduceMotion
    )
  })

  // Lifecycle
  onMounted(() => {
    nextTick(() => {
      initialize()
    })
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // Refs
    containerRef,
    listRef,

    // State
    scrollTop: readonly(scrollTop),
    isScrolling: readonly(isScrolling),
    scrollDirection: readonly(scrollDirection),
    scrollVelocity: readonly(scrollVelocity),
    pregnancyBehavior,
    performanceMetrics,

    // Computed
    visibleItems,
    visibleRange,
    totalHeight,
    scrollProgress,
    isNearTop,
    isNearBottom,
    comfortableScrolling,

    // Methods
    scrollToItem,
    scrollToTop,
    measureItemHeight,
    updateVirtualItems,
    calculateVisibleRange,

    // Config
    itemHeight,
    bufferSize,
    containerHeight,
    pregnancyAware,
    smoothScrolling
  }
}