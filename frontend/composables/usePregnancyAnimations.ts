import { ref, nextTick } from 'vue'

interface AnimationConfig {
  duration?: number
  intensity?: number
  color?: 'soft-pink' | 'gentle-mint' | 'muted-lavender' | 'warm'
  easing?: string
  respectReducedMotion?: boolean
}

interface HeartParticle {
  id: string
  x: number
  y: number
  velocity: { x: number, y: number }
  life: number
  maxLife: number
  size: number
  opacity: number
  color: string
}

interface SparkleParticle {
  id: string
  x: number
  y: number
  rotation: number
  scale: number
  life: number
  maxLife: number
  color: string
}

export const usePregnancyAnimations = () => {
  // Respect user's motion preferences
  const prefersReducedMotion = ref(
    typeof window !== 'undefined' && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )

  // Active animations tracking
  const activeAnimations = ref<Map<string, Animation>>(new Map())

  /**
   * Create gentle heart animation for love interactions
   */
  function gentleHeartAnimation(
    element: HTMLElement,
    config: AnimationConfig = {}
  ): Promise<void> {
    const {
      duration = 2000,
      intensity = 0.8,
      color = 'soft-pink',
      respectReducedMotion = true
    } = config

    if (respectReducedMotion && prefersReducedMotion.value) {
      // Fallback to subtle opacity animation
      return simpleHeartFeedback(element)
    }

    return new Promise((resolve) => {
      // Create heart particles
      const particleCount = Math.floor(intensity * 5) + 2
      const particles: HeartParticle[] = []
      
      const rect = element.getBoundingClientRect()
      const centerX = rect.width / 2
      const centerY = rect.height / 2

      // Generate heart particles
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          id: `heart-${i}-${Date.now()}`,
          x: centerX + (Math.random() - 0.5) * 20,
          y: centerY + (Math.random() - 0.5) * 20,
          velocity: {
            x: (Math.random() - 0.5) * 60,
            y: -Math.random() * 80 - 20
          },
          life: 0,
          maxLife: duration * 0.8 + Math.random() * duration * 0.4,
          size: 12 + Math.random() * 8,
          opacity: 0.9,
          color: getColorValue(color)
        })
      }

      // Create animation container
      const container = createAnimationContainer(element, 'heart-animation')
      
      // Animate particles
      let startTime = Date.now()
      const animate = () => {
        const currentTime = Date.now()
        const elapsed = currentTime - startTime

        // Clear container
        container.innerHTML = ''

        let aliveParticles = 0
        particles.forEach(particle => {
          particle.life = elapsed
          
          if (particle.life < particle.maxLife) {
            aliveParticles++
            
            // Update position
            particle.x += particle.velocity.x * 0.016 // 60fps
            particle.y += particle.velocity.y * 0.016
            
            // Apply gravity
            particle.velocity.y += 120 * 0.016
            
            // Update opacity
            const lifeRatio = particle.life / particle.maxLife
            particle.opacity = Math.max(0, 1 - lifeRatio * lifeRatio)
            
            // Create heart element
            const heart = document.createElement('div')
            heart.innerHTML = '💕'
            heart.style.position = 'absolute'
            heart.style.left = `${particle.x}px`
            heart.style.top = `${particle.y}px`
            heart.style.fontSize = `${particle.size}px`
            heart.style.opacity = particle.opacity.toString()
            heart.style.pointerEvents = 'none'
            heart.style.userSelect = 'none'
            heart.style.transform = 'translate(-50%, -50%)'
            heart.style.filter = `hue-rotate(${color === 'gentle-mint' ? '120deg' : '0deg'})`
            
            container.appendChild(heart)
          }
        })

        if (aliveParticles > 0) {
          requestAnimationFrame(animate)
        } else {
          container.remove()
          resolve()
        }
      }

      requestAnimationFrame(animate)
    })
  }

  /**
   * Create soft bookmark animation for memory interactions
   */
  function softBookmarkAnimation(
    element: HTMLElement,
    config: AnimationConfig = {}
  ): Promise<void> {
    const {
      duration = 1500,
      intensity = 0.6,
      color = 'muted-lavender',
      respectReducedMotion = true
    } = config

    if (respectReducedMotion && prefersReducedMotion.value) {
      return simpleBookmarkFeedback(element)
    }

    return new Promise((resolve) => {
      // Create bookmark float animation
      const bookmark = document.createElement('div')
      bookmark.innerHTML = '🔖'
      bookmark.style.position = 'absolute'
      bookmark.style.top = '10px'
      bookmark.style.right = '10px'
      bookmark.style.fontSize = '24px'
      bookmark.style.pointerEvents = 'none'
      bookmark.style.zIndex = '10'
      bookmark.style.transform = 'scale(0) rotate(-10deg)'
      bookmark.style.filter = `hue-rotate(${color === 'gentle-mint' ? '60deg' : '0deg'})`
      
      element.style.position = 'relative'
      element.appendChild(bookmark)

      // Animate bookmark appearance
      const animation = bookmark.animate([
        { 
          transform: 'scale(0) rotate(-10deg)', 
          opacity: 0 
        },
        { 
          transform: 'scale(1.2) rotate(-5deg)', 
          opacity: 1,
          offset: 0.3
        },
        { 
          transform: 'scale(1) rotate(-3deg)', 
          opacity: 0.9,
          offset: 0.7
        },
        { 
          transform: 'scale(1) rotate(-3deg)', 
          opacity: 0 
        }
      ], {
        duration,
        easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
      })

      animation.onfinish = () => {
        bookmark.remove()
        resolve()
      }
    })
  }

  /**
   * Create warm glow effect for special moments
   */
  function warmGlowEffect(
    element: HTMLElement,
    config: AnimationConfig = {}
  ): Promise<void> {
    const {
      duration = 3000,
      intensity = 0.4,
      color = 'soft-pink',
      respectReducedMotion = true
    } = config

    if (respectReducedMotion && prefersReducedMotion.value) {
      return Promise.resolve()
    }

    return new Promise((resolve) => {
      const originalBoxShadow = element.style.boxShadow
      const glowColor = getColorValue(color)
      
      const keyframes = [
        { boxShadow: originalBoxShadow || 'none' },
        { boxShadow: `0 0 20px ${glowColor}40, 0 0 40px ${glowColor}20` },
        { boxShadow: originalBoxShadow || 'none' }
      ]

      const animation = element.animate(keyframes, {
        duration,
        easing: 'ease-in-out',
        iterations: 1
      })

      activeAnimations.value.set(element.id || `glow-${Date.now()}`, animation)

      animation.onfinish = () => {
        element.style.boxShadow = originalBoxShadow
        activeAnimations.value.delete(element.id || `glow-${Date.now()}`)
        resolve()
      }
    })
  }

  /**
   * Create sparkle effect for celebrations
   */
  function celebrationSparkles(
    element: HTMLElement,
    count: number = 6,
    config: AnimationConfig = {}
  ): Promise<void> {
    const {
      duration = 2500,
      color = 'gentle-mint',
      respectReducedMotion = true
    } = config

    if (respectReducedMotion && prefersReducedMotion.value) {
      return Promise.resolve()
    }

    return new Promise((resolve) => {
      const container = createAnimationContainer(element, 'sparkles-animation')
      const sparkles: SparkleParticle[] = []
      
      const rect = element.getBoundingClientRect()
      
      // Generate sparkles
      for (let i = 0; i < count; i++) {
        sparkles.push({
          id: `sparkle-${i}-${Date.now()}`,
          x: Math.random() * rect.width,
          y: Math.random() * rect.height,
          rotation: Math.random() * 360,
          scale: 0.5 + Math.random() * 0.8,
          life: 0,
          maxLife: duration * 0.6 + Math.random() * duration * 0.4,
          color: getColorValue(color)
        })
      }

      let startTime = Date.now()
      const animate = () => {
        const elapsed = Date.now() - startTime
        container.innerHTML = ''

        let aliveSparkles = 0
        sparkles.forEach(sparkle => {
          sparkle.life = elapsed
          
          if (sparkle.life < sparkle.maxLife) {
            aliveSparkles++
            
            const lifeRatio = sparkle.life / sparkle.maxLife
            const opacity = Math.sin(lifeRatio * Math.PI)
            
            sparkle.rotation += 2
            
            const sparkleEl = document.createElement('div')
            sparkleEl.innerHTML = '✨'
            sparkleEl.style.position = 'absolute'
            sparkleEl.style.left = `${sparkle.x}px`
            sparkleEl.style.top = `${sparkle.y}px`
            sparkleEl.style.transform = `translate(-50%, -50%) scale(${sparkle.scale}) rotate(${sparkle.rotation}deg)`
            sparkleEl.style.opacity = opacity.toString()
            sparkleEl.style.pointerEvents = 'none'
            sparkleEl.style.fontSize = '16px'
            sparkleEl.style.filter = `hue-rotate(${color === 'soft-pink' ? '0deg' : '120deg'})`
            
            container.appendChild(sparkleEl)
          }
        })

        if (aliveSparkles > 0) {
          requestAnimationFrame(animate)
        } else {
          container.remove()
          resolve()
        }
      }

      requestAnimationFrame(animate)
    })
  }

  /**
   * Create gentle entrance animation for story cards
   */
  function gentleEntrance(
    element: HTMLElement,
    delay: number = 0,
    config: AnimationConfig = {}
  ): Promise<void> {
    const {
      duration = 600,
      respectReducedMotion = true
    } = config

    if (respectReducedMotion && prefersReducedMotion.value) {
      element.style.opacity = '1'
      return Promise.resolve()
    }

    return new Promise((resolve) => {
      setTimeout(() => {
        const animation = element.animate([
          { 
            opacity: 0, 
            transform: 'translateY(20px) scale(0.95)',
            filter: 'blur(1px)'
          },
          { 
            opacity: 1, 
            transform: 'translateY(0) scale(1)',
            filter: 'blur(0px)'
          }
        ], {
          duration,
          easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          fill: 'forwards'
        })

        animation.onfinish = () => {
          element.style.opacity = '1'
          element.style.transform = 'none'
          resolve()
        }
      }, delay)
    })
  }

  // Utility functions
  function createAnimationContainer(parent: HTMLElement, className: string): HTMLElement {
    const container = document.createElement('div')
    container.className = className
    container.style.position = 'absolute'
    container.style.top = '0'
    container.style.left = '0'
    container.style.width = '100%'
    container.style.height = '100%'
    container.style.pointerEvents = 'none'
    container.style.overflow = 'hidden'
    container.style.zIndex = '5'
    
    parent.style.position = 'relative'
    parent.appendChild(container)
    
    return container
  }

  function getColorValue(color: string): string {
    const colors = {
      'soft-pink': '#F8BBD0',
      'gentle-mint': '#B2DFDB',
      'muted-lavender': '#E1BEE7',
      'warm': '#FFF3E0'
    }
    return colors[color as keyof typeof colors] || colors['soft-pink']
  }

  async function simpleHeartFeedback(element: HTMLElement): Promise<void> {
    const animation = element.animate([
      { transform: 'scale(1)', filter: 'brightness(1)' },
      { transform: 'scale(1.02)', filter: 'brightness(1.1)' },
      { transform: 'scale(1)', filter: 'brightness(1)' }
    ], {
      duration: 200,
      easing: 'ease-out'
    })

    return new Promise(resolve => {
      animation.onfinish = () => resolve()
    })
  }

  async function simpleBookmarkFeedback(element: HTMLElement): Promise<void> {
    const animation = element.animate([
      { opacity: 1 },
      { opacity: 0.8 },
      { opacity: 1 }
    ], {
      duration: 300,
      easing: 'ease-in-out'
    })

    return new Promise(resolve => {
      animation.onfinish = () => resolve()
    })
  }

  /**
   * Cancel all active animations
   */
  function cancelAllAnimations(): void {
    activeAnimations.value.forEach(animation => {
      animation.cancel()
    })
    activeAnimations.value.clear()
  }

  /**
   * Update reduced motion preference
   */
  function updateMotionPreference(): void {
    if (typeof window !== 'undefined') {
      prefersReducedMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    }
  }

  return {
    // Animation methods
    gentleHeartAnimation,
    softBookmarkAnimation,
    warmGlowEffect,
    celebrationSparkles,
    gentleEntrance,

    // Utility methods
    cancelAllAnimations,
    updateMotionPreference,

    // State
    prefersReducedMotion,
    activeAnimations
  }
}