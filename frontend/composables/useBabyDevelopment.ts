import { computed, ref, readonly } from 'vue'
import { useBabyDevelopmentStore, type BabyWeekData, type DevelopmentStats } from '~/stores/babyDevelopment'
import { usePregnancyStore } from '~/stores/pregnancy'

export interface DevelopmentInsight {
  title: string
  description: string
  category: 'milestone' | 'health' | 'preparation' | 'development'
  priority: 'low' | 'medium' | 'high'
  week: number
}

export interface SizeComparison {
  item: string
  icon: string
  description: string
  visualSize: {
    width: string
    height: string
    scale: number
  }
}

export interface TrimesterInfo {
  number: 1 | 2 | 3
  name: string
  description: string
  keyMilestones: string[]
  commonSymptoms: string[]
  colorScheme: {
    primary: string
    secondary: string
    gradient: string
    text: string
  }
  weekRange: {
    start: number
    end: number
  }
}

/**
 * Composable for baby development functionality
 * Provides reactive data, calculations, and helper functions for baby development tracking
 */
export const useBabyDevelopment = () => {
  const developmentStore = useBabyDevelopmentStore()
  const pregnancyStore = usePregnancyStore()
  
  // Loading state for async operations
  const isLoading = ref(false)
  
  // Computed properties
  const currentPregnancyWeek = computed(() => {
    return pregnancyStore.currentWeek || developmentStore.currentWeek
  })
  
  const currentPregnancyDay = computed(() => {
    if (pregnancyStore.currentPregnancy?.pregnancy_details) {
      return pregnancyStore.currentPregnancy.pregnancy_details.current_day || 0
    }
    return developmentStore.currentDay
  })
  
  const pregnancyDay = computed(() => {
    return developmentStore.pregnancyDay
  })
  
  const currentWeekData = computed((): BabyWeekData | null => {
    return developmentStore.getWeekData(currentPregnancyWeek.value)
  })
  
  const trimesterInfo = computed((): TrimesterInfo => {
    const trimester = developmentStore.trimester
    
    const trimesterData: Record<number, TrimesterInfo> = {
      1: {
        number: 1,
        name: 'First Trimester',
        description: 'The foundation period where all major organs develop and early pregnancy symptoms are strongest.',
        keyMilestones: ['Neural tube formation', 'Heart begins beating', 'All major organs form', 'Fingers and toes develop'],
        commonSymptoms: ['Morning sickness', 'Fatigue', 'Breast tenderness', 'Food aversions'],
        colorScheme: {
          primary: '#f472b6',
          secondary: '#fbcfe8',
          gradient: 'from-rose-400 via-pink-500 to-rose-600',
          text: 'text-rose-600'
        },
        weekRange: { start: 1, end: 12 }
      },
      2: {
        number: 2,
        name: 'Second Trimester',
        description: 'The "golden period" with increased energy, visible baby bump, and feeling first movements.',
        keyMilestones: ['Baby can hear sounds', 'Taste buds develop', 'Hair and nails grow', 'Anatomy scan'],
        commonSymptoms: ['Increased energy', 'Baby movements', 'Growing belly', 'Improved mood'],
        colorScheme: {
          primary: '#a855f7',
          secondary: '#ddd6fe',
          gradient: 'from-purple-400 via-violet-500 to-purple-600',
          text: 'text-purple-600'
        },
        weekRange: { start: 13, end: 26 }
      },
      3: {
        number: 3,
        name: 'Third Trimester',
        description: 'The final stretch where baby gains weight rapidly and prepares for birth.',
        keyMilestones: ['Eyes can open', 'Lungs mature', 'Brain development accelerates', 'Baby gains weight'],
        commonSymptoms: ['Back pain', 'Frequent urination', 'Braxton Hicks', 'Shortness of breath'],
        colorScheme: {
          primary: '#3b82f6',
          secondary: '#bfdbfe',
          gradient: 'from-blue-400 via-indigo-500 to-blue-600',
          text: 'text-blue-600'
        },
        weekRange: { start: 27, end: 40 }
      }
    }
    
    return trimesterData[trimester] || trimesterData[1]
  })
  
  const developmentStats = computed((): DevelopmentStats => {
    return developmentStore.developmentStats
  })
  
  const sizeComparison = computed((): SizeComparison => {
    const weekData = currentWeekData.value
    
    if (!weekData) {
      return {
        item: 'Growing beautifully',
        icon: '👶',
        description: 'Your baby is developing perfectly',
        visualSize: { width: '20px', height: '20px', scale: 1 }
      }
    }
    
    const week = currentPregnancyWeek.value
    const baseSize = Math.min(20 + (week * 1.5), 80)
    const scale = Math.min(0.5 + (week * 0.02), 2)
    
    return {
      item: weekData.size,
      icon: weekData.icon,
      description: `Your baby is about the size of a ${weekData.size.toLowerCase()}`,
      visualSize: {
        width: `${baseSize}px`,
        height: `${baseSize}px`,
        scale
      }
    }
  })
  
  // Helper functions
  const formatWeekDay = (week: number, day: number = 0): string => {
    if (day === 0) return `Week ${week}`
    return `Week ${week}, Day ${day + 1}`
  }
  
  const getWeekProgress = (week: number): number => {
    return Math.min((week / 40) * 100, 100)
  }
  
  const getDaysUntilDue = (): number => {
    const totalDays = 280 // 40 weeks
    return Math.max(0, totalDays - pregnancyDay.value)
  }
  
  const getWeeksUntilDue = (): number => {
    return Math.max(0, 40 - currentPregnancyWeek.value)
  }
  
  const isViabilityReached = (): boolean => {
    return currentPregnancyWeek.value >= 24
  }
  
  const isFullTerm = (): boolean => {
    return currentPregnancyWeek.value >= 37
  }
  
  const getDevelopmentInsights = (week: number): DevelopmentInsight[] => {
    const weekData = developmentStore.getWeekData(week)
    if (!weekData) return []
    
    const insights: DevelopmentInsight[] = []
    
    // Add milestone insights
    weekData.milestones.forEach((milestone, index) => {
      insights.push({
        title: milestone,
        description: `This important development milestone shows your baby's growth is progressing beautifully.`,
        category: 'milestone',
        priority: index === 0 ? 'high' : 'medium',
        week
      })
    })
    
    // Add development focus insights
    weekData.developmentFocus?.forEach(focus => {
      insights.push({
        title: `${focus} Development`,
        description: `This week focuses on ${focus.toLowerCase()}, a crucial aspect of your baby's growth.`,
        category: 'development',
        priority: 'medium',
        week
      })
    })
    
    return insights
  }
  
  const getTrimesterMilestones = (trimester: 1 | 2 | 3): string[] => {
    const info = trimesterInfo.value
    if (info.number === trimester) {
      return info.keyMilestones
    }
    return []
  }
  
  const calculatePregnancyProgress = (): { 
    percentage: number
    daysCompleted: number
    totalDays: number
    weeksCompleted: number
    totalWeeks: number
  } => {
    const totalDays = 280
    const totalWeeks = 40
    const daysCompleted = pregnancyDay.value
    const weeksCompleted = currentPregnancyWeek.value
    const percentage = Math.min((daysCompleted / totalDays) * 100, 100)
    
    return {
      percentage,
      daysCompleted,
      totalDays,
      weeksCompleted,
      totalWeeks
    }
  }
  
  // API integration functions
  const fetchWeekData = async (week: number): Promise<BabyWeekData | null> => {
    isLoading.value = true
    try {
      await developmentStore.fetchDevelopmentData(week)
      return developmentStore.getWeekData(week)
    } catch (error) {
      console.error('Error fetching week data:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchWeekRange = async (startWeek: number, endWeek: number): Promise<BabyWeekData[]> => {
    isLoading.value = true
    try {
      return await developmentStore.fetchWeekRange(startWeek, endWeek)
    } catch (error) {
      console.error('Error fetching week range:', error)
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  const updateCurrentWeek = (week: number, day: number = 0): void => {
    developmentStore.setCurrentWeek(week, day)
  }
  
  const syncWithPregnancyData = (): void => {
    if (pregnancyStore.currentPregnancy?.pregnancy_details) {
      const { current_week, current_day } = pregnancyStore.currentPregnancy.pregnancy_details
      if (current_week) {
        developmentStore.setCurrentWeek(current_week, current_day || 0)
      }
    }
  }
  
  // Data formatting helpers
  const formatMilestone = (milestone: string, week: number): { 
    text: string
    importance: 'low' | 'medium' | 'high'
    category: string
  } => {
    const importanceKeywords = {
      high: ['heart', 'brain', 'neural', 'organ', 'viable', 'mature'],
      medium: ['hear', 'move', 'grow', 'develop', 'form'],
      low: ['hair', 'nail', 'thumb']
    }
    
    const text = milestone.toLowerCase()
    let importance: 'low' | 'medium' | 'high' = 'low'
    
    for (const [level, keywords] of Object.entries(importanceKeywords)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        importance = level as 'low' | 'medium' | 'high'
        break
      }
    }
    
    // Determine category
    let category = 'general'
    if (text.includes('brain') || text.includes('neural')) category = 'neurological'
    else if (text.includes('heart') || text.includes('lung')) category = 'vital'
    else if (text.includes('move') || text.includes('kick')) category = 'motor'
    else if (text.includes('hear') || text.includes('see')) category = 'sensory'
    
    return {
      text: milestone,
      importance,
      category
    }
  }
  
  const getRecommendations = (week: number): string[] => {
    const recommendations: Record<number, string[]> = {
      4: ['Take prenatal vitamins', 'Schedule first prenatal appointment', 'Avoid alcohol and smoking'],
      8: ['Discuss prenatal testing options', 'Stay hydrated', 'Get plenty of rest'],
      12: ['Consider sharing the news', 'Start pregnancy journaling', 'Continue healthy diet'],
      16: ['Schedule anatomy scan', 'Start thinking about baby names', 'Consider maternity clothes'],
      20: ['Enjoy the anatomy scan', 'Start feeling for movements', 'Take maternity photos'],
      24: ['Begin monitoring baby movements', 'Take glucose screening test', 'Start birth classes'],
      28: ['Monitor blood pressure', 'Count fetal movements daily', 'Prepare nursery'],
      32: ['Pack hospital bag', 'Install car seat', 'Prepare for maternity leave'],
      36: ['Weekly doctor visits', 'Watch for labor signs', 'Rest and prepare'],
      40: ['Stay alert for labor signs', 'Keep hospital bag ready', 'Rest when possible']
    }
    
    // Find the closest week with recommendations
    const availableWeeks = Object.keys(recommendations).map(Number).sort((a, b) => Math.abs(week - a) - Math.abs(week - b))
    const closestWeek = availableWeeks[0]
    
    return recommendations[closestWeek] || ['Continue healthy pregnancy habits', 'Stay in touch with your healthcare provider']
  }
  
  return {
    // Reactive data
    currentPregnancyWeek,
    currentPregnancyDay,
    pregnancyDay,
    currentWeekData,
    trimesterInfo,
    developmentStats,
    sizeComparison,
    isLoading: readonly(isLoading),
    
    // Helper functions
    formatWeekDay,
    getWeekProgress,
    getDaysUntilDue,
    getWeeksUntilDue,
    isViabilityReached,
    isFullTerm,
    getDevelopmentInsights,
    getTrimesterMilestones,
    calculatePregnancyProgress,
    
    // API functions
    fetchWeekData,
    fetchWeekRange,
    updateCurrentWeek,
    syncWithPregnancyData,
    
    // Data formatting
    formatMilestone,
    getRecommendations,
    
    // Store access
    store: developmentStore
  }
}