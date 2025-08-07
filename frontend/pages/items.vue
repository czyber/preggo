<template>
  <div class="px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Items</h1>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
      >
        Create Item
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="itemsStore.loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading items...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="itemsStore.error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
      <p class="text-red-800">Error: {{ itemsStore.error }}</p>
      <button
        @click="itemsStore.fetchItems()"
        class="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
      >
        Retry
      </button>
    </div>

    <!-- Items grid -->
    <div v-else-if="itemsStore.items.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="item in itemsStore.items"
        :key="item.id"
        class="bg-white p-6 rounded-lg shadow-sm border"
      >
        <h3 class="text-lg font-semibold mb-2">{{ item.name }}</h3>
        <p class="text-gray-600 mb-4">{{ item.description || 'No description' }}</p>
        <div class="flex justify-between items-center">
          <span
            :class="[
              'px-2 py-1 text-xs rounded',
              item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ item.is_active ? 'Active' : 'Inactive' }}
          </span>
          <div class="flex space-x-2">
            <button
              @click="editItem(item)"
              class="text-blue-600 hover:text-blue-800 text-sm"
            >
              Edit
            </button>
            <button
              @click="deleteItem(item.id)"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600 mb-4">No items found</p>
      <button
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
      >
        Create your first item
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingItem" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4">
          {{ editingItem ? 'Edit Item' : 'Create New Item' }}
        </h2>
        
        <form @submit.prevent="submitForm">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Name
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              v-model="formData.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
          
          <div class="mb-6">
            <label class="flex items-center">
              <input
                v-model="formData.is_active"
                type="checkbox"
                class="mr-2"
              />
              <span class="text-sm text-gray-700">Active</span>
            </label>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="cancelForm"
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {{ submitting ? 'Saving...' : (editingItem ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useItemsStore } from "@/stores/items"

const itemsStore = useItemsStore()

// Modal state
const showCreateModal = ref(false)
const editingItem = ref(null)
const submitting = ref(false)

// Form data
const formData = ref({
  name: '',
  description: '',
  is_active: true
})

// Load items on mount
onMounted(() => {
  itemsStore.fetchItems()
})

// Form handling
const submitForm = async () => {
  submitting.value = true
  
  try {
    if (editingItem.value) {
      await itemsStore.updateItem(editingItem.value.id, formData.value)
    } else {
      await itemsStore.createItem(formData.value)
    }
    cancelForm()
  } catch (error) {
    console.error('Error submitting form:', error)
  } finally {
    submitting.value = false
  }
}

const cancelForm = () => {
  showCreateModal.value = false
  editingItem.value = null
  formData.value = {
    name: '',
    description: '',
    is_active: true
  }
}

const editItem = (item) => {
  editingItem.value = item
  formData.value = {
    name: item.name,
    description: item.description || '',
    is_active: item.is_active
  }
}

const deleteItem = async (itemId) => {
  if (confirm('Are you sure you want to delete this item?')) {
    await itemsStore.deleteItem(itemId)
  }
}
</script>
