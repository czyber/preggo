<template>
  <BaseCard variant="supportive" class="p-6">
    <h3 class="text-lg font-primary font-semibold text-gray-800 mb-4">
      Quick Actions
    </h3>
    <div class="space-y-2">
      <BaseButton 
        variant="outline" 
        size="sm" 
        class="w-full justify-start"
        @click="$emit('logSymptoms')"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Log Symptoms
      </BaseButton>
      <BaseButton 
        variant="outline" 
        size="sm" 
        class="w-full justify-start"
        @click="$emit('addPhoto')"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
        </svg>
        Add Photo
      </BaseButton>
      <BaseButton 
        variant="outline" 
        size="sm" 
        class="w-full justify-start"
        @click="$emit('scheduleAppointment')"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        Schedule Appointment
      </BaseButton>
      <BaseButton 
        variant="outline" 
        size="sm" 
        class="w-full justify-start"
        @click="$emit('trackWeight')"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        Track Weight
      </BaseButton>
      <BaseButton 
        variant="outline" 
        size="sm" 
        class="w-full justify-start text-soft-pink border-soft-pink/30 hover:bg-soft-pink/10"
        @click="$emit('viewFamilyFeed')"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
        Family Feed
      </BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
defineEmits<{
  logSymptoms: []
  addPhoto: []
  scheduleAppointment: []
  trackWeight: []
  viewFamilyFeed: []
}>()
</script>