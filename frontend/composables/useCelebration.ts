import { ref, reactive, toRefs } from 'vue'

type PostType = 'belly_photo' | 'milestone' | 'weekly_update' | 'celebration' | 'symptom_share' | 'ultrasound' | 'appointment' | 'memory' | 'preparation' | 'announcement' | 'question'

interface CelebrationOptions {
  title?: string
  subtitle?: string
  duration?: number
  postType?: PostType
}

interface CelebrationState {
  show: boolean
  message: {
    title: string
    subtitle: string
  }
  sparkles: Array<{
    id: number
    style: string
    delay: number
  }>
}

const celebrationState = reactive<CelebrationState>({
  show: false,
  message: {
    title: '',
    subtitle: ''
  },
  sparkles: []
})

export const useCelebration = () => {
  const getCelebrationMessage = (postType?: PostType) => {
    const messages = {
      'belly_photo': {
        title: 'Beautiful bump shared! 📸',
        subtitle: 'Your family will love seeing your journey'
      },
      'milestone': {
        title: 'Special milestone shared! ⭐',
        subtitle: 'What a wonderful moment to remember'
      },
      'weekly_update': {
        title: 'Weekly update shared! 📅',
        subtitle: 'Keeping your family close to your journey'
      },
      'celebration': {
        title: 'Celebration shared! 🎉',
        subtitle: 'Your joy is contagious!'
      },
      'symptom_share': {
        title: 'Update shared! 💕',
        subtitle: 'Your family cares about how you feel'
      },
      'ultrasound': {
        title: 'Amazing photo shared! 🤱',
        subtitle: 'Baby\'s first family portrait!'
      },
      'appointment': {
        title: 'Appointment update shared! 🩺',
        subtitle: 'Keeping everyone in the loop'
      },
      'memory': {
        title: 'Sweet memory shared! 💭',
        subtitle: 'These moments are precious'
      },
      'preparation': {
        title: 'Progress shared! 🛍️',
        subtitle: 'Getting ready together as a family'
      }
    } as const

    return messages[postType as keyof typeof messages] || {
      title: 'Moment shared! 💕',
      subtitle: 'Your family will love this update'
    }
  }

  const generateSparkles = () => {
    const sparkles = []
    for (let i = 0; i < 8; i++) {
      const angle = (i * 45) + Math.random() * 20 - 10 // Random variation
      const distance = 60 + Math.random() * 20 // Random distance
      const x = Math.cos(angle * Math.PI / 180) * distance
      const y = Math.sin(angle * Math.PI / 180) * distance
      
      sparkles.push({
        id: i,
        style: `left: calc(50% + ${x}px); top: calc(50% + ${y}px);`,
        delay: i * 0.1 + Math.random() * 0.2
      })
    }
    return sparkles
  }

  let originalBodyStyle = ''
  let originalHtmlStyle = ''

  const celebrate = (options: CelebrationOptions = {}) => {
    if (celebrationState.show) return // Prevent multiple celebrations

    const message = options.title && options.subtitle 
      ? { title: options.title, subtitle: options.subtitle }
      : getCelebrationMessage(options.postType)

    celebrationState.message = message
    celebrationState.sparkles = generateSparkles()
    celebrationState.show = true

    // Disable body and html scroll (client-side only)
    if (process.client && document?.body && document?.documentElement) {
      // Store original styles
      originalBodyStyle = document.body.style.overflow
      originalHtmlStyle = document.documentElement.style.overflow
      
      // Prevent scroll on both body and html
      document.body.style.overflow = 'hidden'
      document.documentElement.style.overflow = 'hidden'
      
      // Also add a class to prevent scroll behaviors
      document.body.classList.add('celebration-active')
    }

    // Auto-hide after duration
    const duration = options.duration || 2500
    setTimeout(() => {
      celebrationState.show = false
      // Re-enable body scroll
      if (process.client && document?.body && document?.documentElement) {
        document.body.style.overflow = originalBodyStyle
        document.documentElement.style.overflow = originalHtmlStyle
        document.body.classList.remove('celebration-active')
      }
    }, duration)
  }

  return {
    ...toRefs(celebrationState),
    celebrate
  }
}