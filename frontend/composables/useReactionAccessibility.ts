/**
 * Accessibility-focused composable for pregnancy reaction system
 * 
 * Provides screen reader support, keyboard navigation, and inclusive design
 * for family-centered pregnancy reaction interactions.
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAccessibleAnimations } from './useAnimations'

interface FamilyReactor {
  id: string
  name: string
  relationship?: string
  avatar_url?: string
  reaction_type: string
  reacted_at: string
}

export const useReactionAccessibility = () => {
  const { addAriaLiveRegion, reducedMotion } = useAccessibleAnimations()

  // Accessibility state
  const screenReaderAnnouncements = ref<string[]>([])
  const keyboardFocusIndex = ref(-1)
  const isHighContrastMode = ref(false)

  // Pregnancy-specific reaction labels for screen readers
  const pregnancyReactionLabels: Record<string, { 
    label: string
    description: string
    familyContext: string
  }> = {
    love: {
      label: 'Love reaction',
      description: 'Show love and warm support for this pregnancy moment',
      familyContext: 'Your family is sending love and support'
    },
    excited: {
      label: 'Excited reaction',
      description: 'Share excitement about this pregnancy journey milestone',
      familyContext: 'Your family is excited to celebrate with you'
    },
    care: {
      label: 'Care reaction',
      description: 'Send caring thoughts and emotional support',
      familyContext: 'Your family is wrapping you in caring thoughts'
    },
    support: {
      label: 'Support reaction',
      description: 'Show encouragement and strength for the pregnancy journey',
      familyContext: 'Your family is standing strong beside you'
    },
    beautiful: {
      label: 'Beautiful reaction',
      description: 'Celebrate the beauty of this pregnancy moment',
      familyContext: 'Your family finds this moment precious and beautiful'
    },
    funny: {
      label: 'Funny reaction',
      description: 'Share joy and smiles about this moment',
      familyContext: 'Your family is smiling and laughing with you'
    },
    praying: {
      label: 'Praying reaction',
      description: 'Send prayers and blessings for the pregnancy journey',
      familyContext: 'Your family is offering prayers and blessings'
    },
    proud: {
      label: 'Proud reaction',
      description: 'Express pride and admiration for this pregnancy milestone',
      familyContext: 'Your family is bursting with pride for you'
    },
    grateful: {
      label: 'Grateful reaction',
      description: 'Show gratitude for sharing this pregnancy journey moment',
      familyContext: 'Your family is grateful to be part of your journey'
    }
  }

  // Relationship labels for screen readers
  const relationshipLabels: Record<string, string> = {
    partner: 'your partner',
    mom: 'your mom',
    dad: 'your dad',
    grandma: 'grandma',
    grandpa: 'grandpa',
    sister: 'your sister',
    brother: 'your brother',
    'best-friend': 'your best friend',
    friend: 'your friend',
    aunt: 'your aunt',
    uncle: 'your uncle',
    cousin: 'your cousin',
    'mother-in-law': 'your mother-in-law',
    'father-in-law': 'your father-in-law'
  }

  // Computed properties
  const hasHighContrast = computed(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-contrast: high)').matches
  })

  const prefersDarkMode = computed(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  // Methods
  function announceReactionAdd(reactionType: string, familyContext?: FamilyReactor[]) {
    const reaction = pregnancyReactionLabels[reactionType]
    if (!reaction) return

    let announcement = `You added a ${reaction.label} to this pregnancy post. `
    
    if (familyContext && familyContext.length > 0) {
      const familyNames = familyContext.slice(0, 3).map(reactor => {
        const relationship = relationshipLabels[reactor.relationship || '']
        return relationship || reactor.name
      })
      
      if (familyNames.length === 1) {
        announcement += `${familyNames[0]} has also reacted to this post.`
      } else if (familyNames.length === 2) {
        announcement += `${familyNames[0]} and ${familyNames[1]} have also reacted to this post.`
      } else {
        announcement += `${familyNames[0]}, ${familyNames[1]} and ${familyContext.length - 2} others have also reacted to this post.`
      }
    }

    addAriaLiveRegion(announcement, 'polite')
    screenReaderAnnouncements.value.push(announcement)
  }

  function announceReactionRemove(reactionType: string) {
    const reaction = pregnancyReactionLabels[reactionType]
    if (!reaction) return

    const announcement = `You removed your ${reaction.label} from this pregnancy post.`
    addAriaLiveRegion(announcement, 'polite')
    screenReaderAnnouncements.value.push(announcement)
  }

  function announceFamilyReaction(reactor: FamilyReactor, reactionType: string, isNew: boolean = true) {
    const reaction = pregnancyReactionLabels[reactionType]
    const relationship = relationshipLabels[reactor.relationship || ''] || reactor.name
    
    if (!reaction) return

    const announcement = isNew
      ? `${relationship} just added a ${reaction.label} to your pregnancy post. ${reaction.familyContext}.`
      : `${relationship} has added a ${reaction.label} to your pregnancy post.`

    addAriaLiveRegion(announcement, 'polite')
    screenReaderAnnouncements.value.push(announcement)
  }

  function announceMilestoneCelebration(reactionCount: number, reactionType?: string) {
    let announcement = `Milestone reached! Your pregnancy post now has ${reactionCount} family reactions. `
    
    if (reactionType) {
      const reaction = pregnancyReactionLabels[reactionType]
      announcement += `Your family is celebrating with ${reaction?.familyContext || 'love and support'}.`
    } else {
      announcement += 'Your family is celebrating this special moment with you.'
    }

    addAriaLiveRegion(announcement, 'assertive')
    screenReaderAnnouncements.value.push(announcement)
  }

  function announceFamilyContext(reactors: FamilyReactor[], totalCount: number) {
    if (reactors.length === 0) return

    const specialFamily = reactors.filter(r => 
      ['partner', 'mom', 'dad', 'grandma', 'grandpa'].includes(r.relationship || '')
    )

    let announcement = `Your pregnancy post has ${totalCount} family reactions. `

    if (specialFamily.length > 0) {
      const relationships = specialFamily.slice(0, 2).map(r => 
        relationshipLabels[r.relationship || ''] || r.name
      )
      
      if (relationships.length === 1) {
        announcement += `${relationships[0]} has shared a special reaction.`
      } else {
        announcement += `${relationships.join(' and ')} have shared special reactions.`
      }
    } else {
      const names = reactors.slice(0, 3).map(r => r.name)
      if (names.length === 1) {
        announcement += `${names[0]} has reacted.`
      } else if (names.length === 2) {
        announcement += `${names[0]} and ${names[1]} have reacted.`
      } else {
        announcement += `${names[0]}, ${names[1]} and others have reacted.`
      }
    }

    addAriaLiveRegion(announcement, 'polite')
  }

  function getReactionAriaLabel(reactionType: string, isSelected: boolean, count?: number): string {
    const reaction = pregnancyReactionLabels[reactionType]
    if (!reaction) return `${reactionType} reaction`

    let label = reaction.label
    if (count && count > 0) {
      label += `, ${count} ${count === 1 ? 'person has' : 'people have'} reacted`
    }
    
    if (isSelected) {
      label += ', currently selected'
    }
    
    label += `. ${reaction.description}`
    
    return label
  }

  function getReactionPickerAriaLabel(totalReactions: number): string {
    if (totalReactions === 0) {
      return 'Add a reaction to share your feelings about this pregnancy moment with your family'
    }
    
    return `React to this pregnancy post. ${totalReactions} family ${totalReactions === 1 ? 'member has' : 'members have'} already reacted. Press space or enter to open reaction picker.`
  }

  function getFamilyAvatarAriaLabel(reactor: FamilyReactor): string {
    const relationship = relationshipLabels[reactor.relationship || ''] || reactor.name
    const reaction = pregnancyReactionLabels[reactor.reaction_type]?.label || 'reaction'
    const timeAgo = getRelativeTimeDescription(reactor.reacted_at)
    
    return `${relationship} added a ${reaction} ${timeAgo}`
  }

  function getRelativeTimeDescription(timestamp: string): string {
    const now = new Date()
    const reactedAt = new Date(timestamp)
    const diffInMinutes = Math.floor((now.getTime() - reactedAt.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'just now'
    if (diffInMinutes < 60) return `${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`
    if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60)
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`
    }
    
    const days = Math.floor(diffInMinutes / 1440)
    return `${days} ${days === 1 ? 'day' : 'days'} ago`
  }

  function handleKeyboardNavigation(event: KeyboardEvent, availableReactions: string[]) {
    const { key } = event
    
    switch (key) {
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault()
        keyboardFocusIndex.value = Math.min(
          keyboardFocusIndex.value + 1,
          availableReactions.length - 1
        )
        break
        
      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault()
        keyboardFocusIndex.value = Math.max(keyboardFocusIndex.value - 1, 0)
        break
        
      case 'Home':
        event.preventDefault()
        keyboardFocusIndex.value = 0
        break
        
      case 'End':
        event.preventDefault()
        keyboardFocusIndex.value = availableReactions.length - 1
        break
        
      case 'Escape':
        event.preventDefault()
        keyboardFocusIndex.value = -1
        return 'close'
        
      case 'Enter':
      case ' ':
        event.preventDefault()
        if (keyboardFocusIndex.value >= 0) {
          return availableReactions[keyboardFocusIndex.value]
        }
        break
    }
    
    return null
  }

  function setupAccessibilityFeatures() {
    // Check for high contrast mode
    if (typeof window !== 'undefined') {
      const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
      isHighContrastMode.value = highContrastQuery.matches
      
      const updateHighContrast = () => {
        isHighContrastMode.value = highContrastQuery.matches
      }
      
      highContrastQuery.addEventListener('change', updateHighContrast)
      
      // Cleanup function
      return () => {
        highContrastQuery.removeEventListener('change', updateHighContrast)
      }
    }
  }

  function getAccessibilityCSS(): Record<string, any> {
    return {
      // High contrast mode adjustments
      ...(hasHighContrast.value && {
        '--reaction-border-color': '#000000',
        '--reaction-bg-color': '#ffffff',
        '--reaction-text-color': '#000000',
        '--focus-outline-color': '#0000ff'
      }),
      
      // Reduced motion adjustments
      ...(reducedMotion.value && {
        '--animation-duration': '0.01s',
        '--transition-duration': '0.01s'
      })
    }
  }

  function createKeyboardHelpText(): string {
    return [
      'Keyboard navigation:',
      'Arrow keys: Navigate between reactions',
      'Enter or Space: Select reaction',
      'Escape: Close reaction picker',
      'Home: Go to first reaction',
      'End: Go to last reaction'
    ].join(' ')
  }

  // Lifecycle
  let cleanupAccessibility: (() => void) | undefined

  onMounted(() => {
    cleanupAccessibility = setupAccessibilityFeatures()
  })

  onUnmounted(() => {
    if (cleanupAccessibility) {
      cleanupAccessibility()
    }
  })

  return {
    // State
    screenReaderAnnouncements: readonly(screenReaderAnnouncements),
    keyboardFocusIndex: readonly(keyboardFocusIndex),
    isHighContrastMode: readonly(isHighContrastMode),
    hasHighContrast,
    prefersDarkMode,
    
    // Announcement methods
    announceReactionAdd,
    announceReactionRemove,
    announceFamilyReaction,
    announceMilestoneCelebration,
    announceFamilyContext,
    
    // ARIA label methods
    getReactionAriaLabel,
    getReactionPickerAriaLabel,
    getFamilyAvatarAriaLabel,
    getRelativeTimeDescription,
    
    // Keyboard navigation
    handleKeyboardNavigation,
    
    // Accessibility utilities
    getAccessibilityCSS,
    createKeyboardHelpText,
    pregnancyReactionLabels,
    relationshipLabels
  }
}

// Individual accessibility helpers that can be used independently
export const reactionAccessibilityHelpers = {
  // Focus management
  manageFocus(element: HTMLElement, shouldFocus: boolean = true) {
    if (shouldFocus && element) {
      element.focus()
      element.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  },

  // Screen reader text creation
  createScreenReaderText(text: string): HTMLElement {
    const srElement = document.createElement('span')
    srElement.className = 'sr-only'
    srElement.textContent = text
    srElement.setAttribute('aria-live', 'polite')
    return srElement
  },

  // Enhanced tooltip accessibility
  createAccessibleTooltip(triggerId: string, content: string): string {
    const tooltipId = `tooltip-${triggerId}-${Date.now()}`
    
    // Add to DOM for screen readers
    if (typeof document !== 'undefined') {
      const tooltip = document.createElement('div')
      tooltip.id = tooltipId
      tooltip.className = 'sr-only'
      tooltip.textContent = content
      tooltip.setAttribute('role', 'tooltip')
      document.body.appendChild(tooltip)
      
      // Cleanup after 5 seconds
      setTimeout(() => {
        if (tooltip.parentNode) {
          tooltip.parentNode.removeChild(tooltip)
        }
      }, 5000)
    }
    
    return tooltipId
  },

  // Color contrast helpers
  ensureColorContrast(foreground: string, background: string): boolean {
    // Simple contrast check - in production, use a proper contrast calculation library
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-contrast: high)').matches) {
      return true // Browser will handle high contrast
    }
    return true // Placeholder - implement actual contrast checking
  }
}