import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Types for baby development data
export interface BabyDevelopmentMilestone {
  id: string
  week: number
  day?: number
  title: string
  description: string
  category: 'physical' | 'cognitive' | 'sensory' | 'motor'
  importance: 'low' | 'medium' | 'high'
}

export interface BabyWeekData {
  week: number
  icon: string
  size: string
  weight: string
  length: number // in cm
  milestones: string[]
  description: string
  babyHighlights: string[]
  momHighlights: string[]
  medicalNotes?: string[]
  developmentFocus: string[]
}

export interface DevelopmentStats {
  totalMilestones: number
  completedMilestones: number
  currentTrimester: number
  daysPregnant: number
  progressPercentage: number
}

export const useBabyDevelopmentStore = defineStore('babyDevelopment', () => {
  // State
  const developmentData = ref<Map<number, BabyWeekData>>(new Map())
  const milestones = ref<BabyDevelopmentMilestone[]>([])
  const currentWeek = ref<number>(1)
  const currentDay = ref<number>(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetched = ref<Date | null>(null)
  
  // Cache duration (24 hours)
  const CACHE_DURATION = 24 * 60 * 60 * 1000

  // Static comprehensive development data
  const staticDevelopmentData: Record<number, BabyWeekData> = {
    1: {
      week: 1,
      icon: '🌱',
      size: 'Poppy seed',
      weight: '< 1g',
      length: 0.1,
      milestones: ['Neural tube forms', 'Heart begins to develop', 'Basic body structure emerges'],
      description: 'Your baby is just beginning to form! The neural tube, which will become the brain and spinal cord, is developing. Though tiny, rapid cell division is creating the foundation for your baby\'s entire body.',
      babyHighlights: ['Rapid cell division creating basic body structure', 'Neural tube development begins', 'Primitive streak appears'],
      momHighlights: ['You might not know you\'re pregnant yet', 'Take prenatal vitamins with folic acid', 'Maintain healthy lifestyle'],
      developmentFocus: ['Neural development', 'Cell differentiation', 'Implantation']
    },
    4: {
      week: 4,
      icon: '🌾',
      size: 'Sesame seed',
      weight: '< 1g',
      length: 0.2,
      milestones: ['Limb buds appear', 'Heart starts beating', 'Neural tube closes'],
      description: 'Your baby\'s heart has started beating! Though still microscopic, tiny limb buds that will become arms and legs are beginning to form. The neural tube is closing to form the brain and spinal cord.',
      babyHighlights: ['Heart begins to beat at around 100-110 bpm', 'Arms and legs start forming as tiny buds', 'Brain divides into three sections'],
      momHighlights: ['Morning sickness may begin', 'Breast tenderness', 'First missed period'],
      developmentFocus: ['Cardiovascular system', 'Limb formation', 'Brain development']
    },
    6: {
      week: 6,
      icon: '🫛',
      size: 'Sweet pea',
      weight: '2g',
      length: 0.4,
      milestones: ['Brain hemispheres form', 'Jaw and facial features develop', 'Heart chambers form'],
      description: 'Your baby is growing rapidly! The brain is developing distinct hemispheres, and facial features are beginning to take shape. The heart is becoming more sophisticated with distinct chambers.',
      babyHighlights: ['Brain hemispheres clearly visible', 'Facial features beginning to form', 'Heart developing four chambers'],
      momHighlights: ['Morning sickness may intensify', 'Fatigue is common', 'First prenatal appointment'],
      developmentFocus: ['Brain hemisphere development', 'Facial formation', 'Heart chamber development']
    },
    8: {
      week: 8,
      icon: '🫐',
      size: 'Blueberry',
      weight: '4g',
      length: 1.6,
      milestones: ['Brain waves detectable', 'Fingers and toes form', 'Major organs developing'],
      description: 'This is an incredible week - your baby\'s brain waves can now be detected! Tiny fingers and toes are forming, and all major organs are beginning to develop. Your baby is officially transitioning from embryo to fetus.',
      babyHighlights: ['First brain waves detectable', 'Individual fingers and toes forming', 'All major organs present in basic form'],
      momHighlights: ['End of first trimester approaching', 'Prenatal testing may be discussed', 'Symptoms may be strongest'],
      developmentFocus: ['Neurological activity', 'Digit formation', 'Organ system development']
    },
    10: {
      week: 10,
      icon: '🍇',
      size: 'Grape',
      weight: '8g',
      length: 2.3,
      milestones: ['Webbed fingers separate', 'Eyelids form', 'External ears develop'],
      description: 'Your baby is looking more human! The webbing between fingers is disappearing, eyelids are forming, and external ears are developing. All vital organs are now present and continuing to mature.',
      babyHighlights: ['Fingers no longer webbed', 'Eyelids covering developing eyes', 'External ear structures forming'],
      momHighlights: ['Doppler may detect heartbeat', 'Nausea may start to improve', 'Energy levels may increase'],
      developmentFocus: ['Fine motor development', 'Sensory organ formation', 'Facial feature refinement']
    },
    12: {
      week: 12,
      icon: '🍋',
      size: 'Lime',
      weight: '18g',
      length: 5.4,
      milestones: ['All organs present', 'Can make fists', 'Reflexes developing'],
      description: 'Congratulations - you\'ve reached a major milestone! All of your baby\'s major organs are now present and many are beginning to function. Your baby can make tiny fists and is developing reflexes.',
      babyHighlights: ['All major organs formed and some functioning', 'Can make fists and move fingers', 'Reflexes like sucking beginning'],
      momHighlights: ['End of first trimester', 'Morning sickness may improve', 'First trimester screening available'],
      developmentFocus: ['Organ maturation', 'Reflex development', 'Motor skill foundation']
    },
    16: {
      week: 16,
      icon: '🥑',
      size: 'Avocado',
      weight: '85g',
      length: 11.6,
      milestones: ['Can hear sounds', 'Develops unique fingerprints', 'Skeleton hardening'],
      description: 'Your baby can now hear! Sound waves can penetrate your womb, and your baby is developing their unique fingerprints. The skeleton is changing from soft cartilage to bone.',
      babyHighlights: ['Can hear sounds from outside the womb', 'Unique fingerprints developing', 'Skeleton beginning to harden'],
      momHighlights: ['Anatomy scan coming up', 'May feel first movements', 'Energy levels often improve'],
      developmentFocus: ['Auditory development', 'Skeletal ossification', 'Sensory system maturation']
    },
    20: {
      week: 20,
      icon: '🍌',
      size: 'Banana',
      weight: '240g',
      length: 16.4,
      milestones: ['Can suck thumb', 'Hair and nails grow', 'Taste buds develop'],
      description: 'Congratulations - you\'re halfway there! Your baby can now suck their thumb and is developing taste buds. Hair and nails are growing, and you may start feeling more definite movements.',
      babyHighlights: ['Can suck thumb and swallow', 'Hair growing on head', 'Taste buds developing'],
      momHighlights: ['Anatomy scan scheduled', 'Baby movements becoming stronger', 'May discover baby\'s sex'],
      developmentFocus: ['Gustatory system', 'Fine motor skills', 'Behavioral patterns']
    },
    24: {
      week: 24,
      icon: '🌽',
      size: 'Corn cob',
      weight: '540g',
      length: 21,
      milestones: ['Lungs developing', 'Taste buds form', 'Hearing improves'],
      description: 'This is a significant week for viability! Your baby\'s lungs are developing rapidly, and they\'re producing surfactant, which helps the lungs inflate. Hearing is much more sensitive now.',
      babyHighlights: ['Lungs producing surfactant', 'Can distinguish different sounds', 'Taste buds fully formed'],
      momHighlights: ['Viability milestone reached', 'Glucose screening test', 'Baby movements very noticeable'],
      developmentFocus: ['Respiratory system', 'Auditory refinement', 'Survival milestone']
    },
    28: {
      week: 28,
      icon: '🥥',
      size: 'Coconut',
      weight: '1kg',
      length: 25,
      milestones: ['Eyes can open', 'Brain tissue increases', 'Can distinguish sounds'],
      description: 'Your baby\'s eyes can now open and close! Brain development is accelerating rapidly, and your baby can distinguish between different sounds, including your voice.',
      babyHighlights: ['Eyes can open and blink', 'Rapid brain tissue development', 'Can recognize your voice'],
      momHighlights: ['Third trimester begins', 'More frequent prenatal visits', 'May experience heartburn'],
      developmentFocus: ['Visual development', 'Neurological acceleration', 'Sensory integration']
    },
    32: {
      week: 32,
      icon: '🥭',
      size: 'Mango',
      weight: '1.6kg',
      length: 28,
      milestones: ['Bones hardening', 'Practices breathing', 'Immune system developing'],
      description: 'Your baby is practicing breathing by inhaling and exhaling amniotic fluid! Bones are hardening (except the skull, which remains soft for delivery), and the immune system is developing.',
      babyHighlights: ['Practicing breathing movements', 'Bones hardening except skull', 'Immune system getting stronger'],
      momHighlights: ['Baby shower time', 'Braxton Hicks contractions may begin', 'Preparing nursery'],
      developmentFocus: ['Respiratory preparation', 'Skeletal maturation', 'Immune development']
    },
    36: {
      week: 36,
      icon: '🎃',
      size: 'Small pumpkin',
      weight: '2.4kg',
      length: 32,
      milestones: ['Immune system develops', 'Gains weight rapidly', 'Skull bones soft'],
      description: 'Your baby is gaining weight rapidly and the immune system is developing strongly. The skull bones remain soft and separated to make delivery easier.',
      babyHighlights: ['Gaining about 200g per week', 'Strong immune system developing', 'Skull bones remain flexible'],
      momHighlights: ['Baby considered full-term soon', 'Weekly doctor visits begin', 'Hospital bag preparation'],
      developmentFocus: ['Weight gain', 'Immune maturation', 'Birth preparation']
    },
    40: {
      week: 40,
      icon: '🍉',
      size: 'Watermelon',
      weight: '3.2kg',
      length: 50,
      milestones: ['Fully developed', 'Ready for birth', 'Perfect timing for delivery'],
      description: 'Your baby is fully developed and ready to meet you! They have everything needed to thrive outside the womb. Most babies are born around this time, though anywhere from 37-42 weeks is considered full-term.',
      babyHighlights: ['All organ systems fully mature', 'Strong bones and muscles', 'Ready for independent life'],
      momHighlights: ['Labor may begin any day', 'Frequent doctor visits', 'Hospital bag ready'],
      developmentFocus: ['Complete maturation', 'Birth readiness', 'Final preparations']
    }
  }

  // Computed properties
  const pregnancyDay = computed(() => (currentWeek.value * 7) + currentDay.value)
  
  const trimester = computed(() => {
    const week = currentWeek.value
    if (week <= 12) return 1
    if (week <= 26) return 2
    return 3
  })

  const progressPercentage = computed(() => {
    const totalDays = 280 // 40 weeks
    return Math.min((pregnancyDay.value / totalDays) * 100, 100)
  })

  const currentWeekData = computed(() => {
    return getWeekData(currentWeek.value)
  })

  const developmentStats = computed((): DevelopmentStats => ({
    totalMilestones: milestones.value.length,
    completedMilestones: milestones.value.filter(m => m.week <= currentWeek.value).length,
    currentTrimester: trimester.value,
    daysPregnant: pregnancyDay.value,
    progressPercentage: progressPercentage.value
  }))

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    return Date.now() - lastFetched.value.getTime() < CACHE_DURATION
  })

  // Actions
  function getWeekData(week: number): BabyWeekData | null {
    // First check cached data
    if (developmentData.value.has(week)) {
      return developmentData.value.get(week) || null
    }

    // Fall back to static data
    const staticData = staticDevelopmentData[week]
    if (staticData) {
      developmentData.value.set(week, staticData)
      return staticData
    }

    // Find closest available data
    const availableWeeks = Object.keys(staticDevelopmentData).map(Number).sort((a, b) => a - b)
    let closestWeek = availableWeeks[0]
    
    for (const availableWeek of availableWeeks) {
      if (week >= availableWeek) {
        closestWeek = availableWeek
      } else {
        break
      }
    }
    
    const closestData = staticDevelopmentData[closestWeek]
    if (closestData) {
      // Create a modified version for the requested week
      const modifiedData = {
        ...closestData,
        week,
        description: `Development data approximated from week ${closestWeek}. ${closestData.description}`
      }
      developmentData.value.set(week, modifiedData)
      return modifiedData
    }

    return null
  }

  async function fetchDevelopmentData(week?: number): Promise<void> {
    loading.value = true
    error.value = null

    try {
      if (week) {
        // Fetch specific week from API
        try {
          const response = await $fetch(`/api/v1/baby-development/by-week/${week}`)
          
          // Convert API response to our format
          if (response && response.length > 0) {
            const apiData = response[0] // Get first day of the week as representative
            const weekData: BabyWeekData = {
              week,
              icon: getWeekIcon(week),
              size: apiData.baby_size_comparison,
              weight: `${apiData.baby_weight_grams}g`,
              length: apiData.baby_length_cm,
              milestones: apiData.development_highlights || [],
              description: apiData.detailed_description,
              babyHighlights: apiData.development_highlights || [],
              momHighlights: [apiData.mother_changes],
              medicalNotes: apiData.medical_milestones || [],
              developmentFocus: apiData.symptoms_to_expect || []
            }
            developmentData.value.set(week, weekData)
            return
          }
        } catch (apiError) {
          console.warn('API fetch failed, falling back to static data:', apiError)
        }

        // Fallback to static data
        const data = getWeekData(week)
        if (!data) {
          throw new Error(`No development data available for week ${week}`)
        }
      } else {
        // Load all static data into cache first
        Object.entries(staticDevelopmentData).forEach(([weekStr, data]) => {
          const weekNum = parseInt(weekStr)
          developmentData.value.set(weekNum, data)
        })
      }

      lastFetched.value = new Date()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch development data'
      console.error('Error fetching development data:', err)
    } finally {
      loading.value = false
    }
  }

  function getWeekIcon(week: number): string {
    // Simple icon mapping based on size progression
    if (week <= 4) return '🌱'
    if (week <= 8) return '🫐'
    if (week <= 12) return '🍋'
    if (week <= 16) return '🥑'
    if (week <= 20) return '🍌'
    if (week <= 24) return '🌽'
    if (week <= 28) return '🥥'
    if (week <= 32) return '🥭'
    if (week <= 36) return '🎃'
    return '🍉'
  }

  async function fetchWeekRange(startWeek: number, endWeek: number): Promise<BabyWeekData[]> {
    loading.value = true
    error.value = null

    try {
      const weekData: BabyWeekData[] = []
      
      for (let week = startWeek; week <= endWeek; week++) {
        const data = getWeekData(week)
        if (data) {
          weekData.push(data)
        }
      }

      return weekData
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch week range data'
      console.error('Error fetching week range:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  function setCurrentWeek(week: number, day: number = 0): void {
    if (week >= 1 && week <= 42) {
      currentWeek.value = week
      currentDay.value = Math.max(0, Math.min(day, 6))
    }
  }

  function updateFromPregnancyDay(day: number): void {
    const week = Math.floor(day / 7)
    const dayOfWeek = day % 7
    setCurrentWeek(Math.max(1, week), dayOfWeek)
  }

  function getMilestonesByWeek(week: number): BabyDevelopmentMilestone[] {
    return milestones.value.filter(milestone => milestone.week === week)
  }

  function getMilestonesByCategory(category: BabyDevelopmentMilestone['category']): BabyDevelopmentMilestone[] {
    return milestones.value.filter(milestone => milestone.category === category)
  }

  function clearCache(): void {
    developmentData.value.clear()
    lastFetched.value = null
  }

  function reset(): void {
    developmentData.value.clear()
    milestones.value = []
    currentWeek.value = 1
    currentDay.value = 0
    loading.value = false
    error.value = null
    lastFetched.value = null
  }

  // Auto-fetch data on store initialization if needed
  if (!isCacheValid.value) {
    fetchDevelopmentData()
  }

  return {
    // State
    developmentData: readonly(developmentData),
    milestones: readonly(milestones),
    currentWeek: readonly(currentWeek),
    currentDay: readonly(currentDay),
    loading: readonly(loading),
    error: readonly(error),
    
    // Computed
    pregnancyDay,
    trimester,
    progressPercentage,
    currentWeekData,
    developmentStats,
    isCacheValid,
    
    // Actions
    getWeekData,
    fetchDevelopmentData,
    fetchWeekRange,
    setCurrentWeek,
    updateFromPregnancyDay,
    getMilestonesByWeek,
    getMilestonesByCategory,
    clearCache,
    reset
  }
})