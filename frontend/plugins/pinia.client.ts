import { createPinia, setActivePinia } from 'pinia'

export default defineNuxtPlugin(() => {
  const nuxtApp = useNuxtApp()
  
  // Ensure we have an active Pinia instance
  if (!nuxtApp.$pinia) {
    const pinia = createPinia()
    nuxtApp.vueApp.use(pinia)
    setActivePinia(pinia)
  } else {
    setActivePinia(nuxtApp.$pinia)
  }
})