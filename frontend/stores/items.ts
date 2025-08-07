import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { components } from '@/types/api'

// Type aliases for cleaner code
type Item = components['schemas']['ItemRead']
type ItemCreate = components['schemas']['ItemCreate']
type ItemUpdate = components['schemas']['ItemUpdate']

export const useItemsStore = defineStore('items', () => {
  // State as refs
  const items = ref<Item[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed properties as computed()
  const getItemById = computed(() => (id: number) => {
    return items.value.find(item => item.id === id)
  })
  
  const activeItems = computed(() => {
    return items.value.filter(item => item.is_active)
  })
  
  const inactiveItems = computed(() => {
    return items.value.filter(item => !item.is_active)
  })

  // Actions as functions
  async function fetchItems() {
    loading.value = true
    error.value = null
    
    try {
      const api = useApi()
      const { data, error: apiError } = await api.getItems()
      
      if (apiError) {
        throw new Error(`Failed to fetch items: ${apiError}`)
      }
      
      items.value = data || []
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching items:', err)
    } finally {
      loading.value = false
    }
  }

  async function createItem(itemData: ItemCreate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.createItem(itemData)
      
      if (apiError) {
        throw new Error(`Failed to create item: ${apiError}`)
      }
      
      if (data) {
        items.value.push(data)
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error creating item:', err)
      throw err
    }
  }

  async function updateItem(itemId: number, itemData: ItemUpdate) {
    try {
      const api = useApi()
      const { data, error: apiError } = await api.updateItem(itemId, itemData)
      
      if (apiError) {
        throw new Error(`Failed to update item: ${apiError}`)
      }
      
      if (data) {
        const index = items.value.findIndex(item => item.id === itemId)
        if (index !== -1) {
          items.value[index] = data
        }
      }
      
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error updating item:', err)
      throw err
    }
  }

  async function deleteItem(itemId: number) {
    try {
      const api = useApi()
      const { error: apiError } = await api.deleteItem(itemId)
      
      if (apiError) {
        throw new Error(`Failed to delete item: ${apiError}`)
      }
      
      items.value = items.value.filter(item => item.id !== itemId)
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error deleting item:', err)
      throw err
    }
  }

  function reset() {
    items.value = []
    loading.value = false
    error.value = null
  }

  // Return all state, computed properties, and functions
  return {
    // State
    items,
    loading,
    error,
    
    // Computed
    getItemById,
    activeItems,
    inactiveItems,
    
    // Actions
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    reset
  }
})
