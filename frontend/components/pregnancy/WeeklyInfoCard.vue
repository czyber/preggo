<template>
  <BaseCard variant="calming" class="p-6">
    <h3 class="text-lg font-primary font-semibold text-gray-800 mb-4">
      This Week
    </h3>
    <div class="space-y-3">
      <div class="flex items-start space-x-3">
        <div class="w-2 h-2 bg-muted-lavender rounded-full mt-2 flex-shrink-0"></div>
        <div>
          <p class="text-sm font-medium text-gray-800">Common Changes</p>
          <p class="text-xs text-gray-600 font-secondary">{{ commonChanges }}</p>
        </div>
      </div>
      <div class="flex items-start space-x-3">
        <div class="w-2 h-2 bg-muted-lavender rounded-full mt-2 flex-shrink-0"></div>
        <div>
          <p class="text-sm font-medium text-gray-800">Tips</p>
          <p class="text-xs text-gray-600 font-secondary">{{ weeklyTips }}</p>
        </div>
      </div>
      <div v-if="symptoms.length > 0" class="flex items-start space-x-3">
        <div class="w-2 h-2 bg-muted-lavender rounded-full mt-2 flex-shrink-0"></div>
        <div>
          <p class="text-sm font-medium text-gray-800">Common Symptoms</p>
          <p class="text-xs text-gray-600 font-secondary">{{ symptoms.join(', ') }}</p>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
interface Props {
  currentWeek?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  currentWeek: null
})

// Static data for weekly information (could be dynamic in the future)
const weeklyData = {
  1: {
    changes: 'Missed period, possible implantation',
    tips: 'Start taking prenatal vitamins, avoid alcohol',
    symptoms: ['Missed period', 'Mild cramping']
  },
  4: {
    changes: 'Hormone levels rising, early pregnancy signs',
    tips: 'Schedule first prenatal appointment, eat healthy',
    symptoms: ['Morning sickness', 'Breast tenderness', 'Fatigue']
  },
  8: {
    changes: 'Growing uterus, morning sickness peaks',
    tips: 'Stay hydrated, eat small frequent meals',
    symptoms: ['Nausea', 'Food aversions', 'Frequent urination']
  },
  12: {
    changes: 'Morning sickness may ease, energy returns',
    tips: 'Consider sharing pregnancy news, continue prenatal care',
    symptoms: ['Less nausea', 'Increased energy']
  },
  16: {
    changes: 'Baby bump showing, possible movement',
    tips: 'Start maternity clothes shopping, pelvic floor exercises',
    symptoms: ['Round ligament pain', 'Increased appetite']
  },
  20: {
    changes: 'Anatomy scan, baby movements felt',
    tips: 'Take maternity photos, baby-proof planning',
    symptoms: ['Back pain', 'Leg cramps', 'Heartburn']
  },
  24: {
    changes: 'Growing belly, possible glucose test',
    tips: 'Monitor blood sugar, comfortable shoes',
    symptoms: ['Swelling', 'Stretch marks', 'Shortness of breath']
  },
  28: {
    changes: 'Third trimester begins, regular checkups',
    tips: 'Start childbirth classes, hospital bag prep',
    symptoms: ['Braxton Hicks', 'Difficulty sleeping']
  },
  32: {
    changes: 'Baby gaining weight, frequent appointments',
    tips: 'Practice breathing exercises, rest when possible',
    symptoms: ['Increased fatigue', 'Pelvic pressure']
  },
  36: {
    changes: 'Baby dropping, preparing for labor',
    tips: 'Finalize birth plan, pack hospital bag',
    symptoms: ['Pelvic pressure', 'Frequent urination']
  },
  39: {
    changes: 'Increased appetite, possible braxton hicks',
    tips: 'Practice breathing exercises, stay hydrated',
    symptoms: ['Braxton Hicks', 'Pelvic pressure', 'Restlessness']
  },
  40: {
    changes: 'Ready for labor, cervix may dilate',
    tips: 'Stay calm, monitor contractions, rest',
    symptoms: ['Contractions', 'Water breaking', 'Nesting instinct']
  }
}

const getCurrentWeekInfo = (week: number) => {
  // Find the closest week data
  const availableWeeks = Object.keys(weeklyData).map(Number).sort((a, b) => a - b)
  let closestWeek = availableWeeks[0]
  
  for (const availableWeek of availableWeeks) {
    if (week >= availableWeek) {
      closestWeek = availableWeek
    } else {
      break
    }
  }
  
  return weeklyData[closestWeek as keyof typeof weeklyData]
}

const commonChanges = computed(() => {
  if (!props.currentWeek) return 'Your body is adapting to pregnancy'
  const data = getCurrentWeekInfo(props.currentWeek)
  return data?.changes || 'Your body is adapting to pregnancy'
})

const weeklyTips = computed(() => {
  if (!props.currentWeek) return 'Take care of yourself and stay healthy'
  const data = getCurrentWeekInfo(props.currentWeek)
  return data?.tips || 'Take care of yourself and stay healthy'
})

const symptoms = computed(() => {
  if (!props.currentWeek) return []
  const data = getCurrentWeekInfo(props.currentWeek)
  return data?.symptoms || []
})
</script>