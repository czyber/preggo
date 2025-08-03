import { defineStore } from 'pinia'
import type { components } from '~/types/api'

// Type aliases for cleaner code
type Item = components['schemas']['ItemRead']
type ItemCreate = components['schemas']['ItemCreate']
type ItemUpdate = components['schemas']['ItemUpdate']

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [] as Item[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    getItemById: (state) => (id: number) => {
      return state.items.find(item => item.id === id)
    },
    
    activeItems: (state) => {
      return state.items.filter(item => item.is_active)
    },
    
    inactiveItems: (state) => {
      return state.items.filter(item => !item.is_active)
    },
  },

  actions: {
    async fetchItems() {
      this.loading = true
      this.error = null
      
      try {
        const api = useApi()
        const { data, error } = await api.getItems()
        
        if (error) {
          throw new Error(`Failed to fetch items: ${error}`)
        }
        
        this.items = data || []
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error fetching items:', err)
      } finally {
        this.loading = false
      }
    },

    async createItem(itemData: ItemCreate) {
      try {
        const api = useApi()
        const { data, error } = await api.createItem(itemData)
        
        if (error) {
          throw new Error(`Failed to create item: ${error}`)
        }
        
        if (data) {
          this.items.push(data)
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error creating item:', err)
        throw err
      }
    },

    async updateItem(itemId: number, itemData: ItemUpdate) {
      try {
        const api = useApi()
        const { data, error } = await api.updateItem(itemId, itemData)
        
        if (error) {
          throw new Error(`Failed to update item: ${error}`)
        }
        
        if (data) {
          const index = this.items.findIndex(item => item.id === itemId)
          if (index !== -1) {
            this.items[index] = data
          }
        }
        
        return data
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error updating item:', err)
        throw err
      }
    },

    async deleteItem(itemId: number) {
      try {
        const api = useApi()
        const { error } = await api.deleteItem(itemId)
        
        if (error) {
          throw new Error(`Failed to delete item: ${error}`)
        }
        
        this.items = this.items.filter(item => item.id !== itemId)
        
        return true
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Unknown error'
        console.error('Error deleting item:', err)
        throw err
      }
    },

    reset() {
      this.items = []
      this.loading = false
      this.error = null
    }
  }
})