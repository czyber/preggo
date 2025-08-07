/**
 * Vue Composables for Pregnancy-Themed Animations
 * 
 * Provides reactive animation utilities with emotional context
 * and accessibility support for the pregnancy tracking app.
 */

import { ref, onMounted, onUnmounted, nextTick, type Ref } from 'vue'
import { 
  scrollAnimator, 
  celebrationAnimator, 
  respectsReducedMotion,
  createGentleAnimation,
  applyEmotionalAnimation,
  getEmotionalTiming,
  type ANIMATION_PRESETS 
} from '@/utils/animations'

// === SCROLL ANIMATIONS COMPOSABLE ===

export const useScrollAnimation = () => {
  const elementsToAnimate = ref<Set<HTMLElement>>(new Set())
  
  const observeElement = (element: any, options?: {
    animation?: string
    delay?: number
    duration?: number
    supportive?: boolean
  }) => {
    if (!element) return
    
    // Get the actual DOM element (handle Vue refs and component instances)
    let domElement: HTMLElement | null = null
    
    if (element.$el) {
      // Vue component instance
      domElement = element.$el
    } else if (element instanceof HTMLElement || element instanceof Element) {
      // Already a DOM element
      domElement = element as HTMLElement
    } else if (element.value) {
      // Vue ref
      domElement = element.value
    } else {
      domElement = element
    }
    
    if (!domElement || typeof domElement.setAttribute !== 'function') {
      console.warn('observeElement: Invalid element provided', element)
      return
    }
    
    // Set animation attributes
    if (options?.animation) {
      domElement.setAttribute('data-animation', options.animation)
    }
    if (options?.delay) {
      domElement.setAttribute('data-delay', options.delay.toString())
    }
    if (options?.duration) {
      domElement.setAttribute('data-duration', options.duration.toString())
    }
    if (options?.supportive) {
      domElement.setAttribute('data-supportive', 'true')
    }
    
    // Add to observer
    scrollAnimator.observe(domElement)
    elementsToAnimate.value.add(domElement)
  }
  
  const unobserveElement = (element: HTMLElement) => {
    if (!element) return
    
    scrollAnimator.unobserve(element)
    elementsToAnimate.value.delete(element)
  }
  
  const animateOnScroll = (elements: HTMLElement[], staggerDelay: number = 100) => {
    elements.forEach((element, index) => {
      observeElement(element, {
        animation: 'fadeInUp',
        delay: index * staggerDelay,
        supportive: true
      })
    })
  }
  
  onUnmounted(() => {
    elementsToAnimate.value.forEach(element => {
      scrollAnimator.unobserve(element)
    })
    elementsToAnimate.value.clear()
  })
  
  return {
    observeElement,
    unobserveElement,
    animateOnScroll
  }
}

// === CELEBRATION ANIMATIONS COMPOSABLE ===

export const useCelebrationAnimation = () => {
  const isAnimating = ref(false)
  const animationQueue = ref<Array<() => void>>([])
  
  const celebrateSparkles = (container?: HTMLElement, count: number = 8) => {
    createGentleAnimation(() => {
      celebrationAnimator.createSparkles(count, container)
    })
  }
  
  const celebrateHearts = (container?: HTMLElement, count: number = 4) => {
    createGentleAnimation(() => {
      celebrationAnimator.createFloatingHearts(count, container)
    })
  }
  
  const celebrateConfetti = (container?: HTMLElement, count: number = 12) => {
    createGentleAnimation(() => {
      celebrationAnimator.createConfetti(count, container)
    })
  }
  
  const celebrateMilestone = async (container?: HTMLElement) => {
    if (isAnimating.value) {
      animationQueue.value.push(() => celebrateMilestone(container))
      return
    }
    
    isAnimating.value = true
    
    createGentleAnimation(() => {
      celebrationAnimator.celebrateMilestone(container)
    })
    
    // Mark as done after animation completes
    setTimeout(() => {
      isAnimating.value = false
      
      // Process next in queue
      const nextAnimation = animationQueue.value.shift()
      if (nextAnimation) {
        nextAnimation()
      }
    }, 2000)
  }
  
  const celebrateReaction = (element: HTMLElement, reactionType: string) => {
    const emotionMap: Record<string, 'excited' | 'supportive' | 'celebratory'> = {
      love: 'supportive',
      excited: 'excited',
      care: 'supportive',
      support: 'supportive',
      beautiful: 'celebratory',
      funny: 'excited',
      praying: 'supportive',
      proud: 'celebratory',
      grateful: 'supportive'
    }
    
    const emotion = emotionMap[reactionType] || 'supportive'
    
    createGentleAnimation(() => {
      applyEmotionalAnimation(element, emotion, 'reactionSelect')
      
      // Add special class for animation
      element.classList.add('animate-celebration-bounce')
      
      setTimeout(() => {
        element.classList.remove('animate-celebration-bounce')
      }, 600)
    })
  }
  
  return {
    isAnimating: readonly(isAnimating),
    celebrateSparkles,
    celebrateHearts,
    celebrateConfetti,
    celebrateMilestone,
    celebrateReaction
  }
}

// === REACTION ANIMATIONS COMPOSABLE ===

export const useReactionAnimation = () => {
  const animateReactionButton = (element: HTMLElement, isSelected: boolean) => {
    createGentleAnimation(() => {
      if (isSelected) {
        element.classList.add('animate-celebration-bounce', 'hover-celebration')
      } else {
        element.classList.remove('animate-celebration-bounce', 'hover-celebration')
        element.classList.add('hover-reaction')
      }
    })
  }
  
  const animateReactionCounter = (element: HTMLElement, increment: boolean = true) => {
    createGentleAnimation(() => {
      element.classList.add('counter-animate')
      
      if (increment) {
        // Briefly show a +1 indicator
        const indicator = document.createElement('span')
        indicator.textContent = '+1'
        indicator.className = 'absolute -top-2 -right-2 text-xs text-soft-pink animate-fadeInUp'
        indicator.style.cssText = 'pointer-events: none; z-index: 10;'
        
        element.style.position = 'relative'
        element.appendChild(indicator)
        
        setTimeout(() => {
          if (indicator.parentNode) {
            indicator.parentNode.removeChild(indicator)
          }
        }, 1000)
      }
      
      setTimeout(() => {
        element.classList.remove('counter-animate')
      }, 400)
    })
  }
  
  const animateReactionPicker = (pickerElement: HTMLElement, isOpening: boolean) => {
    createGentleAnimation(() => {
      if (isOpening) {
        pickerElement.classList.add('reaction-picker-enter')
      }
    })
  }
  
  const animateReactionOption = (optionElement: HTMLElement, isHovering: boolean) => {
    createGentleAnimation(() => {
      if (isHovering) {
        optionElement.classList.add('reaction-option-hover')
      } else {
        optionElement.classList.remove('reaction-option-hover')
      }
    })
  }
  
  return {
    animateReactionButton,
    animateReactionCounter,
    animateReactionPicker,
    animateReactionOption
  }
}

// === GENTLE TRANSITIONS COMPOSABLE ===

export const useGentleTransitions = () => {
  const createGentleHover = (element: any, type: 'lift' | 'glow' | 'celebration' = 'lift') => {
    // Get the actual DOM element (handle Vue refs and component instances)
    let domElement: HTMLElement | null = null
    
    if (element?.$el) {
      // Vue component instance
      domElement = element.$el
    } else if (element instanceof HTMLElement || element instanceof Element) {
      // Already a DOM element
      domElement = element as HTMLElement
    } else if (element?.value) {
      // Vue ref
      domElement = element.value
    } else {
      domElement = element
    }
    
    if (!domElement || !domElement.classList) {
      console.warn('createGentleHover: Invalid element provided', element)
      return
    }
    
    const classMap = {
      lift: 'hover-gentle-lift',
      glow: 'hover-supportive-glow',
      celebration: 'hover-celebration'
    }
    
    createGentleAnimation(() => {
      domElement!.classList.add(classMap[type])
    })
  }
  
  const animateElementIn = (
    element: HTMLElement, 
    animation: 'fadeInUp' | 'fadeInScale' | 'slideInLeft' | 'slideInRight' = 'fadeInUp',
    emotion: 'calm' | 'excited' | 'supportive' | 'celebratory' = 'supportive'
  ) => {
    createGentleAnimation(() => {
      element.classList.add('animate-in', `animate-${animation}`, `emotion-${emotion}`)
    })
  }
  
  const pulseElement = (element: HTMLElement, type: 'gentle' | 'supportive' | 'warm' = 'gentle') => {
    const classMap = {
      gentle: 'animate-gentle-pulse',
      supportive: 'animate-supportive',
      warm: 'animate-warm-pulse'
    }
    
    createGentleAnimation(() => {
      element.classList.add(classMap[type])
      
      // Auto-remove after a few cycles
      setTimeout(() => {
        element.classList.remove(classMap[type])
      }, 6000)
    })
  }
  
  const shakeElement = (element: HTMLElement, type: 'gentle' | 'wiggle' = 'gentle') => {
    const classMap = {
      gentle: 'animate-gentle-shake',
      wiggle: 'animate-gentle-wiggle'
    }
    
    createGentleAnimation(() => {
      element.classList.add(classMap[type])
      
      setTimeout(() => {
        element.classList.remove(classMap[type])
      }, type === 'gentle' ? 500 : 1000)
    })
  }
  
  const glowElement = (element: HTMLElement, duration: number = 3000) => {
    createGentleAnimation(() => {
      element.classList.add('animate-milestone-glow')
      
      setTimeout(() => {
        element.classList.remove('animate-milestone-glow')
      }, duration)
    })
  }
  
  return {
    createGentleHover,
    animateElementIn,
    pulseElement,
    shakeElement,
    glowElement
  }
}


// === FEED-SPECIFIC ANIMATIONS COMPOSABLE ===

export const useFeedAnimations = () => {
  const animatePostEntry = (element: any) => {
    // Get the actual DOM element (handle Vue refs and component instances)
    let domElement: HTMLElement | null = null
    
    if (element?.$el) {
      // Vue component instance
      domElement = element.$el
    } else if (element instanceof HTMLElement || element instanceof Element) {
      // Already a DOM element
      domElement = element as HTMLElement
    } else if (element?.value) {
      // Vue ref
      domElement = element.value
    } else {
      domElement = element
    }
    
    if (!domElement || !domElement.classList) {
      console.warn('animatePostEntry: Invalid element provided', element)
      return
    }
    
    createGentleAnimation(() => {
      domElement!.classList.add('feed-post-enter')
    })
  }
  
  const animatePostCelebration = (element: any) => {
    // Get the actual DOM element (handle Vue refs and component instances)
    let domElement: HTMLElement | null = null
    
    if (element?.$el) {
      // Vue component instance
      domElement = element.$el
    } else if (element instanceof HTMLElement || element instanceof Element) {
      // Already a DOM element
      domElement = element as HTMLElement
    } else if (element?.value) {
      // Vue ref
      domElement = element.value
    } else {
      domElement = element
    }
    
    if (!domElement || !domElement.classList) {
      console.warn('animatePostCelebration: Invalid element provided', element)
      return
    }
    
    createGentleAnimation(() => {
      domElement!.classList.add('feed-post-celebration')
      
      setTimeout(() => {
        domElement!.classList.remove('feed-post-celebration')
      }, 600)
    })
  }
  
  const animateTimelineItem = (itemElement: HTMLElement, index: number = 0) => {
    createGentleAnimation(() => {
      itemElement.style.animationDelay = `${index * 100}ms`
      itemElement.classList.add('timeline-item-enter')
    })
  }
  
  const animateEngagementUpdate = (engagementElement: HTMLElement) => {
    createGentleAnimation(() => {
      engagementElement.classList.add('engagement-reaction-increment')
      
      setTimeout(() => {
        engagementElement.classList.remove('engagement-reaction-increment')
      }, 400)
    })
  }
  
  return {
    animatePostEntry,
    animatePostCelebration,
    animateTimelineItem,
    animateEngagementUpdate
  }
}

// === LOADING ANIMATIONS COMPOSABLE ===

export const useLoadingAnimations = () => {
  const isLoading = ref(false)
  
  const showHeartsLoader = (container: HTMLElement) => {
    isLoading.value = true
    
    const loader = document.createElement('div')
    loader.className = 'loading-hearts'
    loader.setAttribute('aria-label', 'Loading...')
    
    container.appendChild(loader)
    
    return () => {
      if (loader.parentNode) {
        loader.parentNode.removeChild(loader)
      }
      isLoading.value = false
    }
  }
  
  const showDotsLoader = (container: HTMLElement) => {
    isLoading.value = true
    
    const loader = document.createElement('div')
    loader.className = 'loading-dots'
    loader.setAttribute('aria-label', 'Loading...')
    loader.innerHTML = '<span></span><span></span><span></span>'
    
    container.appendChild(loader)
    
    return () => {
      if (loader.parentNode) {
        loader.parentNode.removeChild(loader)
      }
      isLoading.value = false
    }
  }
  
  return {
    isLoading: readonly(isLoading),
    showHeartsLoader,
    showDotsLoader
  }
}

// === ACCESSIBILITY-AWARE ANIMATION COMPOSABLE ===

export const useAccessibleAnimations = () => {
  const reducedMotion = ref(respectsReducedMotion())
  
  // Update preference if user changes system setting
  onMounted(() => {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      const updatePreference = () => {
        reducedMotion.value = mediaQuery.matches
      }
      
      mediaQuery.addEventListener('change', updatePreference)
      
      onUnmounted(() => {
        mediaQuery.removeEventListener('change', updatePreference)
      })
    }
  })
  
  const animateWithRespect = (
    element: HTMLElement,
    fullAnimation: () => void,
    reducedAnimation?: () => void
  ) => {
    if (reducedMotion.value && reducedAnimation) {
      reducedAnimation()
    } else if (!reducedMotion.value) {
      fullAnimation()
    }
  }
  
  const addAriaLiveRegion = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (typeof document === 'undefined') return
    
    const region = document.createElement('div')
    region.setAttribute('aria-live', priority)
    region.setAttribute('aria-atomic', 'true')
    region.className = 'sr-only'
    region.textContent = message
    
    document.body.appendChild(region)
    
    // Clean up after announcement
    setTimeout(() => {
      if (region.parentNode) {
        region.parentNode.removeChild(region)
      }
    }, 1000)
  }
  
  return {
    reducedMotion: readonly(reducedMotion),
    animateWithRespect,
    addAriaLiveRegion
  }
}
