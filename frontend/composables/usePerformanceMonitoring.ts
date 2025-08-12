import { ref, computed, onMounted, onUnmounted } from 'vue'

interface PerformanceConfig {
  enableRealUserMonitoring?: boolean
  enableCoreWebVitals?: boolean
  enablePregnancyMetrics?: boolean
  sampleRate?: number
  reportingInterval?: number
  budgets?: PerformanceBudgets
}

interface PerformanceBudgets {
  firstContentfulPaint: number // ms
  timeToInteractive: number // ms  
  largestContentfulPaint: number // ms
  firstInputDelay: number // ms
  cumulativeLayoutShift: number // score
  bundleSize: number // KB
  memoryUsage: number // MB
}

interface CoreWebVitals {
  lcp: number | null // Largest Contentful Paint
  fid: number | null // First Input Delay
  cls: number | null // Cumulative Layout Shift
  fcp: number | null // First Contentful Paint
  ttfb: number | null // Time to First Byte
  tti: number | null // Time to Interactive
}

interface PregnancyMetrics {
  feedLoadTime: number
  imageOptimizationRate: number
  interactionLatency: number
  batteryImpact: number
  memoryEfficiency: number
  userComfortScore: number
}

interface PerformanceEntry {
  timestamp: number
  metric: string
  value: number
  url: string
  userAgent: string
  connectionType?: string
  deviceMemory?: number
  hardwareConcurrency?: number
}

export const usePerformanceMonitoring = (config: PerformanceConfig = {}) => {
  const {
    enableRealUserMonitoring = true,
    enableCoreWebVitals = true,
    enablePregnancyMetrics = true,
    sampleRate = 0.1, // 10% of users
    reportingInterval = 30000, // 30 seconds
    budgets = {
      firstContentfulPaint: 1500,
      timeToInteractive: 3500,
      largestContentfulPaint: 2500,
      firstInputDelay: 100,
      cumulativeLayoutShift: 0.1,
      bundleSize: 500,
      memoryUsage: 50
    }
  } = config

  // State
  const coreWebVitals = ref<CoreWebVitals>({
    lcp: null,
    fid: null,
    cls: null,
    fcp: null,
    ttfb: null,
    tti: null
  })

  const pregnancyMetrics = ref<PregnancyMetrics>({
    feedLoadTime: 0,
    imageOptimizationRate: 0,
    interactionLatency: 0,
    batteryImpact: 0,
    memoryEfficiency: 0,
    userComfortScore: 100
  })

  const performanceEntries = ref<PerformanceEntry[]>([])
  const isMonitoring = ref(false)
  const reportingQueue = ref<PerformanceEntry[]>([])

  // Observers
  let performanceObserver: PerformanceObserver | null = null
  let intersectionObserver: IntersectionObserver | null = null
  let reportingIntervalId: NodeJS.Timeout | null = null

  /**
   * Initialize performance monitoring
   */
  function initializeMonitoring(): void {
    if (!shouldMonitor()) return

    isMonitoring.value = true
    
    if (enableCoreWebVitals) {
      initializeCoreWebVitals()
    }
    
    if (enablePregnancyMetrics) {
      initializePregnancyMetrics()
    }
    
    if (enableRealUserMonitoring) {
      setupRealUserMonitoring()
    }

    setupPerformanceBudgetAlerts()
    startReporting()

    console.log('Performance monitoring initialized for pregnancy app')
  }

  /**
   * Check if we should monitor this user (sampling)
   */
  function shouldMonitor(): boolean {
    return Math.random() < sampleRate
  }

  /**
   * Initialize Core Web Vitals monitoring
   */
  function initializeCoreWebVitals(): void {
    if (!('PerformanceObserver' in window)) return

    // First Contentful Paint
    observePerformanceEntry('paint', (entry) => {
      if (entry.name === 'first-contentful-paint') {
        coreWebVitals.value.fcp = entry.startTime
        recordMetric('fcp', entry.startTime)
        checkBudget('firstContentfulPaint', entry.startTime)
      }
    })

    // Largest Contentful Paint
    observePerformanceEntry('largest-contentful-paint', (entry) => {
      coreWebVitals.value.lcp = entry.startTime
      recordMetric('lcp', entry.startTime)
      checkBudget('largestContentfulPaint', entry.startTime)
    })

    // First Input Delay
    observePerformanceEntry('first-input', (entry) => {
      const fid = entry.processingStart - entry.startTime
      coreWebVitals.value.fid = fid
      recordMetric('fid', fid)
      checkBudget('firstInputDelay', fid)
    })

    // Cumulative Layout Shift
    observePerformanceEntry('layout-shift', (entry) => {
      if (!(entry as any).hadRecentInput) {
        coreWebVitals.value.cls = (coreWebVitals.value.cls || 0) + (entry as any).value
        recordMetric('cls', coreWebVitals.value.cls)
        checkBudget('cumulativeLayoutShift', coreWebVitals.value.cls)
      }
    })

    // Navigation timing for TTFB and TTI
    setTimeout(() => {
      const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      if (navEntry) {
        // Time to First Byte
        const ttfb = navEntry.responseStart - navEntry.fetchStart
        coreWebVitals.value.ttfb = ttfb
        recordMetric('ttfb', ttfb)

        // Time to Interactive (approximation)
        const tti = navEntry.domInteractive - navEntry.fetchStart
        coreWebVitals.value.tti = tti
        recordMetric('tti', tti)
        checkBudget('timeToInteractive', tti)
      }
    }, 0)
  }

  /**
   * Initialize pregnancy-specific metrics
   */
  function initializePregnancyMetrics(): void {
    // Monitor feed loading performance
    monitorFeedPerformance()

    // Monitor image optimization
    monitorImageOptimization()

    // Monitor user interactions
    monitorInteractionLatency()

    // Monitor battery impact
    monitorBatteryImpact()

    // Monitor memory efficiency
    monitorMemoryUsage()

    // Monitor user comfort score
    monitorUserComfort()
  }

  /**
   * Monitor feed loading performance
   */
  function monitorFeedPerformance(): void {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
              const element = node as HTMLElement
              if (element.classList.contains('feed-post-card')) {
                const startTime = performance.now()
                
                // Wait for images to load
                const images = element.querySelectorAll('img')
                Promise.all(Array.from(images).map(img => {
                  if (img.complete) return Promise.resolve()
                  return new Promise(resolve => {
                    img.onload = img.onerror = resolve
                  })
                })).then(() => {
                  const loadTime = performance.now() - startTime
                  pregnancyMetrics.value.feedLoadTime = Math.max(pregnancyMetrics.value.feedLoadTime, loadTime)
                  recordMetric('feed-load-time', loadTime)
                })
              }
            }
          })
        }
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true
    })
  }

  /**
   * Monitor image optimization effectiveness
   */
  function monitorImageOptimization(): void {
    let totalImages = 0
    let optimizedImages = 0

    const imageObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            const element = node as HTMLElement
            const images = element.querySelectorAll('img')
            
            images.forEach((img) => {
              totalImages++
              
              // Check if image is optimized (WebP, AVIF, or has srcset)
              if (img.srcset || 
                  img.src.includes('fm=webp') || 
                  img.src.includes('fm=avif') ||
                  img.closest('picture')) {
                optimizedImages++
              }
              
              pregnancyMetrics.value.imageOptimizationRate = totalImages > 0 
                ? (optimizedImages / totalImages) * 100 
                : 0
            })
          }
        })
      })
    })

    imageObserver.observe(document.body, {
      childList: true,
      subtree: true
    })
  }

  /**
   * Monitor user interaction latency
   */
  function monitorInteractionLatency(): void {
    const interactionEvents = ['click', 'touchstart', 'keydown']
    
    interactionEvents.forEach(eventType => {
      document.addEventListener(eventType, (event) => {
        const startTime = performance.now()
        
        requestAnimationFrame(() => {
          const latency = performance.now() - startTime
          pregnancyMetrics.value.interactionLatency = Math.max(
            pregnancyMetrics.value.interactionLatency,
            latency
          )
          recordMetric('interaction-latency', latency)
          
          // Update user comfort score based on latency
          if (latency > 100) {
            pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 1)
          }
        })
      }, { passive: true })
    })
  }

  /**
   * Monitor battery impact
   */
  function monitorBatteryImpact(): void {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        const initialLevel = battery.level
        
        setTimeout(() => {
          const currentLevel = battery.level
          const batteryDrop = initialLevel - currentLevel
          const timeElapsed = 60000 // 1 minute
          
          // Calculate battery impact per hour
          pregnancyMetrics.value.batteryImpact = (batteryDrop / timeElapsed) * 3600000
          recordMetric('battery-impact', pregnancyMetrics.value.batteryImpact)
        }, 60000)
      })
    }
  }

  /**
   * Monitor memory usage
   */
  function monitorMemoryUsage(): void {
    if ('memory' in performance) {
      setInterval(() => {
        const memInfo = (performance as any).memory
        const memoryUsage = memInfo.usedJSHeapSize / (1024 * 1024) // Convert to MB
        
        pregnancyMetrics.value.memoryEfficiency = memoryUsage
        recordMetric('memory-usage', memoryUsage)
        
        checkBudget('memoryUsage', memoryUsage)
        
        // Update user comfort score based on memory usage
        if (memoryUsage > 100) {
          pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 2)
        }
      }, 10000) // Check every 10 seconds
    }
  }

  /**
   * Monitor user comfort indicators
   */
  function monitorUserComfort(): void {
    // Monitor scroll smoothness
    let lastScrollTime = 0
    let scrollSamples: number[] = []
    
    window.addEventListener('scroll', () => {
      const now = performance.now()
      if (lastScrollTime > 0) {
        const scrollDelta = now - lastScrollTime
        scrollSamples.push(scrollDelta)
        
        if (scrollSamples.length > 10) {
          const avgScrollTime = scrollSamples.reduce((a, b) => a + b) / scrollSamples.length
          
          if (avgScrollTime > 16.67) { // Below 60fps
            pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 0.5)
          }
          
          scrollSamples = []
        }
      }
      lastScrollTime = now
    }, { passive: true })

    // Monitor animation performance
    let animationFrameTimes: number[] = []
    
    function measureAnimationFrame() {
      const startTime = performance.now()
      
      requestAnimationFrame(() => {
        const frameTime = performance.now() - startTime
        animationFrameTimes.push(frameTime)
        
        if (animationFrameTimes.length > 60) { // Check every second
          const avgFrameTime = animationFrameTimes.reduce((a, b) => a + b) / animationFrameTimes.length
          
          if (avgFrameTime > 16.67) { // Below 60fps
            pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 1)
          }
          
          animationFrameTimes = []
        }
        
        measureAnimationFrame()
      })
    }
    
    measureAnimationFrame()
  }

  /**
   * Observe performance entries
   */
  function observePerformanceEntry(entryType: string, callback: (entry: PerformanceEntry) => void): void {
    if (!('PerformanceObserver' in window)) return

    try {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(callback)
      })
      
      observer.observe({ entryTypes: [entryType] })
    } catch (error) {
      console.warn(`Failed to observe ${entryType}:`, error)
    }
  }

  /**
   * Record performance metric
   */
  function recordMetric(metric: string, value: number): void {
    const entry: PerformanceEntry = {
      timestamp: Date.now(),
      metric,
      value,
      url: window.location.href,
      userAgent: navigator.userAgent,
      connectionType: getConnectionType(),
      deviceMemory: getDeviceMemory(),
      hardwareConcurrency: navigator.hardwareConcurrency
    }

    performanceEntries.value.push(entry)
    reportingQueue.value.push(entry)

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`Performance metric - ${metric}: ${value.toFixed(2)}`)
    }
  }

  /**
   * Check performance budget
   */
  function checkBudget(budgetKey: keyof PerformanceBudgets, value: number): void {
    const budget = budgets[budgetKey]
    
    if (value > budget) {
      console.warn(`Performance budget exceeded for ${budgetKey}: ${value.toFixed(2)} > ${budget}`)
      
      // Update user comfort score for budget violations
      pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 5)
      
      // Record budget violation
      recordMetric(`budget-violation-${budgetKey}`, value - budget)
    }
  }

  /**
   * Setup performance budget alerts
   */
  function setupPerformanceBudgetAlerts(): void {
    // Monitor bundle size
    const scripts = document.querySelectorAll('script[src]')
    let totalBundleSize = 0
    
    scripts.forEach(script => {
      if (script.src.includes('.js')) {
        fetch(script.src, { method: 'HEAD' }).then(response => {
          const contentLength = response.headers.get('Content-Length')
          if (contentLength) {
            totalBundleSize += parseInt(contentLength) / 1024 // Convert to KB
            checkBudget('bundleSize', totalBundleSize)
          }
        }).catch(() => {
          // Ignore errors for bundle size checking
        })
      }
    })
  }

  /**
   * Setup real user monitoring
   */
  function setupRealUserMonitoring(): void {
    // Capture page visibility changes
    document.addEventListener('visibilitychange', () => {
      recordMetric('visibility-change', document.hidden ? 0 : 1)
    })

    // Capture page unload
    window.addEventListener('beforeunload', () => {
      // Send any remaining performance data
      sendPerformanceData()
    })

    // Capture errors
    window.addEventListener('error', (event) => {
      recordMetric('javascript-error', 1)
      pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 3)
    })

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      recordMetric('promise-rejection', 1)
      pregnancyMetrics.value.userComfortScore = Math.max(0, pregnancyMetrics.value.userComfortScore - 2)
    })
  }

  /**
   * Start periodic reporting
   */
  function startReporting(): void {
    reportingIntervalId = setInterval(() => {
      if (reportingQueue.value.length > 0) {
        sendPerformanceData()
      }
    }, reportingInterval)
  }

  /**
   * Send performance data to analytics endpoint
   */
  async function sendPerformanceData(): Promise<void> {
    if (reportingQueue.value.length === 0) return

    try {
      const data = [...reportingQueue.value]
      reportingQueue.value = []

      // Use sendBeacon if available for better reliability
      if ('sendBeacon' in navigator) {
        navigator.sendBeacon('/api/v1/analytics/performance', JSON.stringify({
          entries: data,
          coreWebVitals: coreWebVitals.value,
          pregnancyMetrics: pregnancyMetrics.value
        }))
      } else {
        // Fallback to fetch
        fetch('/api/v1/analytics/performance', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            entries: data,
            coreWebVitals: coreWebVitals.value,
            pregnancyMetrics: pregnancyMetrics.value
          })
        }).catch(error => {
          console.warn('Failed to send performance data:', error)
        })
      }
    } catch (error) {
      console.warn('Failed to send performance data:', error)
    }
  }

  /**
   * Get connection type
   */
  function getConnectionType(): string | undefined {
    const connection = (navigator as any).connection
    return connection?.effectiveType
  }

  /**
   * Get device memory
   */
  function getDeviceMemory(): number | undefined {
    return (navigator as any).deviceMemory
  }

  /**
   * Cleanup monitoring
   */
  function cleanup(): void {
    if (performanceObserver) {
      performanceObserver.disconnect()
    }
    
    if (intersectionObserver) {
      intersectionObserver.disconnect()
    }
    
    if (reportingIntervalId) {
      clearInterval(reportingIntervalId)
    }
    
    // Send final performance data
    sendPerformanceData()
    
    isMonitoring.value = false
  }

  // Computed properties
  const performanceSummary = computed(() => ({
    coreWebVitals: coreWebVitals.value,
    pregnancyMetrics: pregnancyMetrics.value,
    overallScore: calculateOverallScore(),
    budgetStatus: getBudgetStatus()
  }))

  const calculateOverallScore = (): number => {
    const vitals = coreWebVitals.value
    let score = 100

    // Deduct points for poor Core Web Vitals
    if (vitals.lcp && vitals.lcp > budgets.largestContentfulPaint) score -= 20
    if (vitals.fid && vitals.fid > budgets.firstInputDelay) score -= 15
    if (vitals.cls && vitals.cls > budgets.cumulativeLayoutShift) score -= 15
    if (vitals.fcp && vitals.fcp > budgets.firstContentfulPaint) score -= 10

    // Factor in user comfort score
    score = Math.min(score, pregnancyMetrics.value.userComfortScore)

    return Math.max(0, score)
  }

  const getBudgetStatus = () => {
    const vitals = coreWebVitals.value
    return {
      fcp: vitals.fcp ? vitals.fcp <= budgets.firstContentfulPaint : null,
      lcp: vitals.lcp ? vitals.lcp <= budgets.largestContentfulPaint : null,
      fid: vitals.fid ? vitals.fid <= budgets.firstInputDelay : null,
      cls: vitals.cls ? vitals.cls <= budgets.cumulativeLayoutShift : null,
      tti: vitals.tti ? vitals.tti <= budgets.timeToInteractive : null
    }
  }

  // Initialize on mount
  onMounted(() => {
    // Delay initialization to avoid impacting initial page load
    setTimeout(() => {
      initializeMonitoring()
    }, 1000)
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // State
    coreWebVitals: readonly(coreWebVitals),
    pregnancyMetrics: readonly(pregnancyMetrics),
    performanceEntries: readonly(performanceEntries),
    isMonitoring: readonly(isMonitoring),

    // Computed
    performanceSummary,

    // Methods
    recordMetric,
    sendPerformanceData,
    cleanup,

    // Config
    budgets,
    sampleRate,
    enableRealUserMonitoring,
    enableCoreWebVitals,
    enablePregnancyMetrics
  }
}