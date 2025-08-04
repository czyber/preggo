/**
 * Animation Utilities for Pregnancy Tracking App
 * 
 * Provides reusable animation presets and utilities with pregnancy-themed timing
 * and emotion-aware animation behavior that feels warm, supportive, and celebratory.
 */

// Animation timing curves optimized for pregnancy app feel
export const TIMING_CURVES = {
  // Gentle, organic timing for supportive interactions
  gentle: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  
  // More pronounced for celebrations and milestones
  celebration: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  
  // Smooth for hover states and micro-interactions
  smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
  
  // Bouncy for playful interactions
  bouncy: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
  
  // Calming for soothing transitions
  calming: 'cubic-bezier(0.25, 0.1, 0.25, 1)'
} as const

// Duration presets based on emotional context
export const DURATIONS = {
  // Quick micro-interactions
  quick: 150,
  
  // Standard interactions
  normal: 250,
  
  // Gentle, supportive transitions
  gentle: 400,
  
  // Celebrations and milestones
  celebration: 600,
  
  // Calming, soothing animations
  soothing: 800,
  
  // Long ceremonial animations
  ceremonial: 1200
} as const

// Animation presets for different emotional contexts
export const ANIMATION_PRESETS = {
  // Gentle hover effect for supportive elements
  gentleHover: {
    duration: DURATIONS.gentle,
    timingFunction: TIMING_CURVES.gentle,
    transform: 'translateY(-2px) scale(1.02)',
    boxShadow: '0 8px 25px rgba(248, 187, 208, 0.15)',
    filter: 'brightness(1.05)'
  },
  
  // Celebration bounce for milestones
  celebrationBounce: {
    duration: DURATIONS.celebration,
    timingFunction: TIMING_CURVES.celebration,
    transform: 'scale(1.05)',
    filter: 'brightness(1.1) saturate(1.2)'
  },
  
  // Gentle pulse for attention
  gentlePulse: {
    duration: DURATIONS.soothing,
    timingFunction: TIMING_CURVES.calming,
    transform: 'scale(1.02)',
    opacity: '0.9'
  },
  
  // Sparkle effect for celebrations
  sparkle: {
    duration: DURATIONS.celebration,
    timingFunction: TIMING_CURVES.bouncy,
    transform: 'rotate(15deg) scale(1.2)',
    filter: 'brightness(1.5) hue-rotate(15deg)'
  },
  
  // Floating heart animation
  floatingHeart: {
    duration: DURATIONS.ceremonial,
    timingFunction: TIMING_CURVES.gentle,
    transform: 'translateY(-20px) rotate(5deg) scale(1.1)',
    opacity: '0.8'
  },
  
  // Supportive glow effect
  supportiveGlow: {
    duration: DURATIONS.gentle,
    timingFunction: TIMING_CURVES.smooth,
    boxShadow: '0 0 20px rgba(178, 223, 219, 0.4)',
    borderColor: 'rgba(178, 223, 219, 0.6)'
  },
  
  // Reaction selection animation
  reactionSelect: {
    duration: DURATIONS.normal,
    timingFunction: TIMING_CURVES.bouncy,
    transform: 'scale(1.15)',
    backgroundColor: 'rgba(248, 187, 208, 0.2)',
    borderColor: 'rgba(248, 187, 208, 0.5)'
  }
} as const

// Intersection Observer utilities for scroll-triggered animations
export class PregnancyScrollAnimator {
  private observer: IntersectionObserver | null = null
  private animatedElements = new Set<Element>()
  
  constructor(
    private options: IntersectionObserverInit = {
      threshold: 0.1,
      rootMargin: '50px 0px -50px 0px'
    }
  ) {
    this.initializeObserver()
  }
  
  private initializeObserver() {
    if (typeof window === 'undefined') return
    
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
          this.animatedElements.add(entry.target)
          this.animateElement(entry.target)
        }
      })
    }, this.options)
  }
  
  private animateElement(element: Element) {
    const animationType = element.getAttribute('data-animation') || 'fadeInUp'
    const delay = parseInt(element.getAttribute('data-delay') || '0', 10)
    const duration = parseInt(element.getAttribute('data-duration') || '400', 10)
    
    setTimeout(() => {
      element.classList.add('animate-in', `animate-${animationType}`)
      
      // Add supportive message class for certain elements
      if (element.getAttribute('data-supportive') === 'true') {
        element.classList.add('animate-supportive')
      }
    }, delay)
  }
  
  observe(element: Element) {
    if (this.observer) {
      this.observer.observe(element)
    }
  }
  
  unobserve(element: Element) {
    if (this.observer) {
      this.observer.unobserve(element)
      this.animatedElements.delete(element)
    }
  }
  
  disconnect() {
    if (this.observer) {
      this.observer.disconnect()
      this.animatedElements.clear()
    }
  }
}

// Celebration animation generator
export class CelebrationAnimator {
  private container: HTMLElement | null = null
  
  constructor(containerSelector?: string) {
    if (typeof window !== 'undefined') {
      this.container = containerSelector 
        ? document.querySelector(containerSelector)
        : document.body
    }
  }
  
  // Create sparkle elements for celebration
  createSparkles(count: number = 12, containerElement?: HTMLElement): HTMLElement[] {
    const sparkles: HTMLElement[] = []
    const container = containerElement || this.container
    
    if (!container) return sparkles
    
    for (let i = 0; i < count; i++) {
      const sparkle = document.createElement('div')
      sparkle.className = 'celebration-sparkle'
      sparkle.innerHTML = '✨'
      
      // Random positioning
      const angle = (360 / count) * i + Math.random() * 30 - 15
      const distance = 60 + Math.random() * 40
      const x = Math.cos(angle * Math.PI / 180) * distance
      const y = Math.sin(angle * Math.PI / 180) * distance
      
      sparkle.style.cssText = `
        position: absolute;
        left: calc(50% + ${x}px);
        top: calc(50% + ${y}px);
        font-size: 16px;
        animation: sparkle-celebration ${800 + Math.random() * 400}ms ease-out forwards;
        animation-delay: ${i * 50}ms;
        pointer-events: none;
        z-index: 1000;
      `
      
      container.appendChild(sparkle)
      sparkles.push(sparkle)
      
      // Clean up after animation
      setTimeout(() => {
        if (sparkle.parentNode) {
          sparkle.parentNode.removeChild(sparkle)
        }
      }, 1500)
    }
    
    return sparkles
  }
  
  // Create floating hearts
  createFloatingHearts(count: number = 6, containerElement?: HTMLElement): HTMLElement[] {
    const hearts: HTMLElement[] = []
    const container = containerElement || this.container
    
    if (!container) return hearts
    
    const heartEmojis = ['❤️', '💕', '💖', '💗', '💝']
    
    for (let i = 0; i < count; i++) {
      const heart = document.createElement('div')
      heart.className = 'celebration-heart'
      heart.innerHTML = heartEmojis[Math.floor(Math.random() * heartEmojis.length)]
      
      // Random starting position
      const startX = Math.random() * 100
      const drift = (Math.random() - 0.5) * 50
      
      heart.style.cssText = `
        position: absolute;
        left: ${startX}%;
        bottom: -20px;
        font-size: ${14 + Math.random() * 8}px;
        animation: heart-float ${2000 + Math.random() * 1000}ms ease-out forwards;
        animation-delay: ${i * 200}ms;
        pointer-events: none;
        z-index: 1000;
        --drift: ${drift}px;
      `
      
      container.appendChild(heart)
      hearts.push(heart)
      
      // Clean up after animation
      setTimeout(() => {
        if (heart.parentNode) {
          heart.parentNode.removeChild(heart)
        }
      }, 3500)
    }
    
    return hearts
  }
  
  // Create confetti burst
  createConfetti(count: number = 20, containerElement?: HTMLElement): HTMLElement[] {
    const confetti: HTMLElement[] = []
    const container = containerElement || this.container
    
    if (!container) return confetti
    
    const colors = ['#F8BBD0', '#E1BEE7', '#B2DFDB', '#FFCDD2', '#BBDEFB']
    const shapes = ['▪', '▫', '●', '◆', '♦']
    
    for (let i = 0; i < count; i++) {
      const piece = document.createElement('div')
      piece.className = 'celebration-confetti'
      piece.innerHTML = shapes[Math.floor(Math.random() * shapes.length)]
      
      const color = colors[Math.floor(Math.random() * colors.length)]
      const size = 8 + Math.random() * 6
      const angle = Math.random() * 360
      const distance = 100 + Math.random() * 150
      const x = Math.cos(angle * Math.PI / 180) * distance
      const y = Math.sin(angle * Math.PI / 180) * distance
      
      piece.style.cssText = `
        position: absolute;
        left: calc(50% + ${x}px);
        top: calc(50% + ${y}px);
        color: ${color};
        font-size: ${size}px;
        animation: confetti-burst ${1000 + Math.random() * 500}ms ease-out forwards;
        animation-delay: ${Math.random() * 200}ms;
        pointer-events: none;
        z-index: 1000;
        transform: rotate(${Math.random() * 360}deg);
      `
      
      container.appendChild(piece)
      confetti.push(piece)
      
      // Clean up after animation
      setTimeout(() => {
        if (piece.parentNode) {
          piece.parentNode.removeChild(piece)
        }
      }, 2000)
    }
    
    return confetti
  }
  
  // Celebration combo effect
  celebrateMilestone(containerElement?: HTMLElement) {
    this.createSparkles(8, containerElement)
    setTimeout(() => this.createFloatingHearts(4, containerElement), 200)
    setTimeout(() => this.createConfetti(12, containerElement), 400)
  }
}

// Emotion-aware animation timing
export const getEmotionalTiming = (emotion: 'calm' | 'excited' | 'supportive' | 'celebratory') => {
  const timings = {
    calm: {
      duration: DURATIONS.soothing,
      curve: TIMING_CURVES.calming,
      delay: 100
    },
    excited: {
      duration: DURATIONS.normal,
      curve: TIMING_CURVES.bouncy,
      delay: 50
    },
    supportive: {
      duration: DURATIONS.gentle,
      curve: TIMING_CURVES.gentle,
      delay: 80
    },
    celebratory: {
      duration: DURATIONS.celebration,
      curve: TIMING_CURVES.celebration,
      delay: 30
    }
  }
  
  return timings[emotion]
}

// Utility function to apply animation with emotion context
export const applyEmotionalAnimation = (
  element: HTMLElement, 
  emotion: 'calm' | 'excited' | 'supportive' | 'celebratory',
  animationType: keyof typeof ANIMATION_PRESETS
) => {
  const timing = getEmotionalTiming(emotion)
  const preset = ANIMATION_PRESETS[animationType]
  
  const style = `
    transition-duration: ${timing.duration}ms;
    transition-timing-function: ${timing.curve};
    transition-delay: ${timing.delay}ms;
  `
  
  element.style.cssText += style
  
  // Apply the animation preset
  Object.entries(preset).forEach(([property, value]) => {
    if (property !== 'duration' && property !== 'timingFunction') {
      const cssProperty = property.replace(/([A-Z])/g, '-$1').toLowerCase()
      element.style.setProperty(cssProperty, value as string)
    }
  })
}

// Utility to check for reduced motion preference
export const respectsReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return true
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// Create gentle animation with reduced motion support
export const createGentleAnimation = (
  callback: () => void,
  fallbackCallback?: () => void
) => {
  if (respectsReducedMotion() && fallbackCallback) {
    fallbackCallback()
  } else {
    callback()
  }
}

// Export singleton instances for common use
export const scrollAnimator = new PregnancyScrollAnimator()
export const celebrationAnimator = new CelebrationAnimator()