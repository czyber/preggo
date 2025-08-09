import { ref } from 'vue'

interface GestureConfig {
  swipeThreshold?: number
  doubleTapWindow?: number
  longPressDelay?: number
  pregnancyAdaptations?: boolean
}

interface SwipeGesture {
  direction: 'left' | 'right' | 'up' | 'down'
  distance: number
  velocity: number
  startPoint: { x: number, y: number }
  endPoint: { x: number, y: number }
}

interface TapGesture {
  point: { x: number, y: number }
  timestamp: number
}

interface LongPressGesture {
  point: { x: number, y: number }
  duration: number
}

export const useGestureRecognition = (config: GestureConfig = {}) => {
  const {
    swipeThreshold = 50,
    doubleTapWindow = 300,
    longPressDelay = 600,
    pregnancyAdaptations = true
  } = config

  // Pregnancy adaptations - make gestures more forgiving
  const adaptedSwipeThreshold = pregnancyAdaptations ? swipeThreshold * 0.8 : swipeThreshold
  const adaptedDoubleTapWindow = pregnancyAdaptations ? doubleTapWindow * 1.5 : doubleTapWindow
  const adaptedLongPressDelay = pregnancyAdaptations ? longPressDelay * 1.2 : longPressDelay

  // Gesture state
  const isGestureActive = ref(false)
  const gestureType = ref<'swipe' | 'tap' | 'longpress' | null>(null)
  
  // Touch tracking
  let touchStartTime = 0
  let touchStartPoint = { x: 0, y: 0 }
  let lastTapTime = 0
  let lastTapPoint = { x: 0, y: 0 }
  let longPressTimer: NodeJS.Timeout | null = null

  /**
   * Recognize swipe gestures with pregnancy-friendly adaptations
   */
  function recognizeSwipe(
    startEvent: TouchEvent | MouseEvent,
    endEvent: TouchEvent | MouseEvent,
    onSwipe: (gesture: SwipeGesture) => void
  ): boolean {
    const startPoint = getEventPoint(startEvent)
    const endPoint = getEventPoint(endEvent)
    
    const deltaX = endPoint.x - startPoint.x
    const deltaY = endPoint.y - startPoint.y
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    
    // Check if swipe meets threshold
    if (distance < adaptedSwipeThreshold) return false
    
    // Determine primary direction
    const absDeltaX = Math.abs(deltaX)
    const absDeltaY = Math.abs(deltaY)
    
    // For pregnancy apps, we primarily care about horizontal swipes
    if (absDeltaX < absDeltaY) return false // Vertical movement, likely scrolling
    
    const direction = deltaX > 0 ? 'right' : 'left'
    const velocity = distance / (Date.now() - touchStartTime)
    
    const gesture: SwipeGesture = {
      direction,
      distance,
      velocity,
      startPoint,
      endPoint
    }
    
    onSwipe(gesture)
    return true
  }

  /**
   * Recognize double tap with extended window for pregnancy users
   */
  function recognizeDoubleTap(
    event: TouchEvent | MouseEvent,
    onDoubleTap: (gesture: TapGesture) => void
  ): boolean {
    const currentTime = Date.now()
    const currentPoint = getEventPoint(event)
    
    // Check if this is within the double tap window
    const timeDiff = currentTime - lastTapTime
    const pointDistance = Math.sqrt(
      Math.pow(currentPoint.x - lastTapPoint.x, 2) + 
      Math.pow(currentPoint.y - lastTapPoint.y, 2)
    )
    
    if (timeDiff <= adaptedDoubleTapWindow && pointDistance <= 50) {
      const gesture: TapGesture = {
        point: currentPoint,
        timestamp: currentTime
      }
      
      onDoubleTap(gesture)
      
      // Reset to prevent triple taps
      lastTapTime = 0
      lastTapPoint = { x: 0, y: 0 }
      return true
    }
    
    // Store this tap for potential double tap
    lastTapTime = currentTime
    lastTapPoint = currentPoint
    return false
  }

  /**
   * Recognize long press with pregnancy-adapted timing
   */
  function recognizeLongPress(
    startEvent: TouchEvent | MouseEvent,
    onLongPress: (gesture: LongPressGesture) => void,
    onLongPressStart?: () => void
  ): () => void {
    const startPoint = getEventPoint(startEvent)
    const startTime = Date.now()
    
    // Start visual feedback if provided
    if (onLongPressStart) {
      setTimeout(onLongPressStart, adaptedLongPressDelay * 0.3)
    }
    
    longPressTimer = setTimeout(() => {
      const gesture: LongPressGesture = {
        point: startPoint,
        duration: adaptedLongPressDelay
      }
      
      onLongPress(gesture)
    }, adaptedLongPressDelay)
    
    // Return cleanup function
    return () => {
      if (longPressTimer) {
        clearTimeout(longPressTimer)
        longPressTimer = null
      }
    }
  }

  /**
   * Initialize gesture recognition on an element
   */
  function initializeGestures(
    element: HTMLElement,
    handlers: {
      onSwipeLeft?: (gesture: SwipeGesture) => void
      onSwipeRight?: (gesture: SwipeGesture) => void
      onDoubleTap?: (gesture: TapGesture) => void
      onLongPress?: (gesture: LongPressGesture) => void
      onLongPressStart?: () => void
    }
  ) {
    let cleanupLongPress: (() => void) | null = null
    let touchMoved = false
    
    const handleTouchStart = (event: TouchEvent) => {
      touchStartTime = Date.now()
      touchStartPoint = getEventPoint(event)
      touchMoved = false
      isGestureActive.value = true
      
      // Start long press detection
      if (handlers.onLongPress) {
        cleanupLongPress = recognizeLongPress(
          event,
          handlers.onLongPress,
          handlers.onLongPressStart
        )
      }
    }
    
    const handleTouchMove = (event: TouchEvent) => {
      const currentPoint = getEventPoint(event)
      const distance = Math.sqrt(
        Math.pow(currentPoint.x - touchStartPoint.x, 2) + 
        Math.pow(currentPoint.y - touchStartPoint.y, 2)
      )
      
      if (distance > 10) {
        touchMoved = true
        // Cancel long press if user moves too much
        if (cleanupLongPress) {
          cleanupLongPress()
          cleanupLongPress = null
        }
      }
    }
    
    const handleTouchEnd = (event: TouchEvent) => {
      const endTime = Date.now()
      const touchDuration = endTime - touchStartTime
      
      // Cancel long press
      if (cleanupLongPress) {
        cleanupLongPress()
        cleanupLongPress = null
      }
      
      if (!touchMoved) {
        // Handle tap gestures
        if (touchDuration < 200) {
          // Quick tap - check for double tap
          if (handlers.onDoubleTap) {
            recognizeDoubleTap(event, handlers.onDoubleTap)
          }
        }
      } else {
        // Handle swipe gestures
        const swipeHandler = (gesture: SwipeGesture) => {
          if (gesture.direction === 'left' && handlers.onSwipeLeft) {
            handlers.onSwipeLeft(gesture)
          } else if (gesture.direction === 'right' && handlers.onSwipeRight) {
            handlers.onSwipeRight(gesture)
          }
        }
        
        recognizeSwipe(
          { touches: [{ clientX: touchStartPoint.x, clientY: touchStartPoint.y }] } as any,
          event,
          swipeHandler
        )
      }
      
      isGestureActive.value = false
      gestureType.value = null
    }
    
    // Add event listeners
    element.addEventListener('touchstart', handleTouchStart, { passive: false })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })
    element.addEventListener('touchend', handleTouchEnd, { passive: false })
    
    // Return cleanup function
    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
      element.removeEventListener('touchend', handleTouchEnd)
      
      if (cleanupLongPress) {
        cleanupLongPress()
      }
    }
  }

  /**
   * Get point coordinates from touch or mouse event
   */
  function getEventPoint(event: TouchEvent | MouseEvent): { x: number, y: number } {
    if ('touches' in event && event.touches.length > 0) {
      return {
        x: event.touches[0].clientX,
        y: event.touches[0].clientY
      }
    } else if ('clientX' in event) {
      return {
        x: event.clientX,
        y: event.clientY
      }
    }
    return { x: 0, y: 0 }
  }

  /**
   * Check if device supports touch
   */
  const isTouchDevice = () => {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0
  }

  /**
   * Get recommended gesture instructions based on device
   */
  const getGestureInstructions = () => {
    if (isTouchDevice()) {
      return {
        love: 'Double tap or swipe right to send love',
        memory: 'Swipe left to add to memories',
        longPress: 'Hold for more options'
      }
    } else {
      return {
        love: 'Double click to send love',
        memory: 'Click the bookmark icon to add to memories',
        longPress: 'Right click for more options'
      }
    }
  }

  return {
    // State
    isGestureActive,
    gestureType,
    
    // Methods
    recognizeSwipe,
    recognizeDoubleTap,
    recognizeLongPress,
    initializeGestures,
    isTouchDevice,
    getGestureInstructions,
    
    // Config
    adaptedSwipeThreshold,
    adaptedDoubleTapWindow,
    adaptedLongPressDelay
  }
}