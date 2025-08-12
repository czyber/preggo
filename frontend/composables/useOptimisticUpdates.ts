/**
 * Optimistic updates composable for immediate UI feedback
 * Provides Instagram-like immediate response with rollback capability
 */

import { ref, reactive } from 'vue'
import { useToast } from './useToast'

interface OptimisticOperation<T = any> {
  id: string
  type: 'add' | 'update' | 'remove'
  data: T
  originalData?: T
  timestamp: number
  retries: number
  maxRetries: number
  rollbackFn?: () => void
}

interface OptimisticConfig {
  maxRetries: number
  retryDelay: number
  timeoutMs: number
  enableHapticFeedback: boolean
  pregnancyAdaptations: boolean
}

export function useOptimisticUpdates<T = any>(config: Partial<OptimisticConfig> = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    timeoutMs = 5000,
    enableHapticFeedback = true,
    pregnancyAdaptations = true
  } = config

  const toast = useToast()
  
  // State
  const pendingOperations = ref<Map<string, OptimisticOperation<T>>>(new Map())
  const failedOperations = ref<Set<string>>(new Set())
  const isProcessing = ref(false)

  // Statistics for pregnancy-focused UX
  const stats = reactive({
    totalOperations: 0,
    successfulOperations: 0,
    failedOperations: 0,
    averageLatency: 0,
    userSatisfactionScore: 100 // Start optimistic
  })

  /**
   * Apply optimistic update with immediate UI feedback
   */
  function applyOptimistic<TData = T>(
    id: string,
    type: 'add' | 'update' | 'remove',
    data: TData,
    originalData?: TData,
    rollbackFn?: () => void
  ): string {
    const operationId = `${id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    const operation: OptimisticOperation<TData> = {
      id: operationId,
      type,
      data,
      originalData,
      timestamp: Date.now(),
      retries: 0,
      maxRetries,
      rollbackFn
    }

    pendingOperations.value.set(operationId, operation as OptimisticOperation<T>)
    stats.totalOperations++

    // Provide immediate haptic feedback for supported devices
    if (enableHapticFeedback && 'vibrate' in navigator) {
      // Gentle vibration pattern for pregnancy-friendly experience
      if (pregnancyAdaptations) {
        navigator.vibrate([10]) // Single gentle pulse
      } else {
        navigator.vibrate([25, 10, 25]) // Confirmation pattern
      }
    }

    return operationId
  }

  /**
   * Commit optimistic update after successful server response
   */
  function commitOptimistic(
    operationId: string,
    serverData?: T
  ): boolean {
    const operation = pendingOperations.value.get(operationId)
    if (!operation) {
      console.warn('Attempted to commit unknown operation:', operationId)
      return false
    }

    // Update with server data if provided
    if (serverData) {
      operation.data = serverData
    }

    pendingOperations.value.delete(operationId)
    failedOperations.value.delete(operationId)
    
    stats.successfulOperations++
    updateLatencyStats(operation.timestamp)
    updateSatisfactionScore(true)

    // Provide success feedback
    if (enableHapticFeedback && 'vibrate' in navigator && pregnancyAdaptations) {
      navigator.vibrate([15, 5, 10]) // Success pattern
    }

    return true
  }

  /**
   * Rollback optimistic update on failure
   */
  function rollbackOptimistic(
    operationId: string,
    error?: Error,
    showUserMessage: boolean = true
  ): boolean {
    const operation = pendingOperations.value.get(operationId)
    if (!operation) {
      console.warn('Attempted to rollback unknown operation:', operationId)
      return false
    }

    // Execute rollback function if provided
    if (operation.rollbackFn) {
      try {
        operation.rollbackFn()
      } catch (rollbackError) {
        console.error('Rollback function failed:', rollbackError)
      }
    }

    pendingOperations.value.delete(operationId)
    failedOperations.value.add(operationId)
    
    stats.failedOperations++
    updateSatisfactionScore(false)

    // Show user-friendly error message
    if (showUserMessage) {
      const message = getPregnancyFriendlyErrorMessage(operation.type, error)
      if (pregnancyAdaptations) {
        toast.add({
          title: 'Gentle retry needed',
          description: message,
          type: 'warning',
          duration: 4000
        })
      } else {
        toast.add({
          title: 'Action failed',
          description: message,
          type: 'error',
          duration: 3000
        })
      }
    }

    // Provide error feedback
    if (enableHapticFeedback && 'vibrate' in navigator) {
      if (pregnancyAdaptations) {
        navigator.vibrate([20]) // Single gentle notification
      } else {
        navigator.vibrate([50, 25, 50]) // Error pattern
      }
    }

    return true
  }

  /**
   * Retry failed optimistic update
   */
  async function retryOptimistic(
    operationId: string,
    retryFn: () => Promise<T>
  ): Promise<boolean> {
    const operation = pendingOperations.value.get(operationId)
    if (!operation) {
      return false
    }

    if (operation.retries >= operation.maxRetries) {
      rollbackOptimistic(operationId, new Error('Max retries exceeded'), true)
      return false
    }

    operation.retries++
    
    try {
      isProcessing.value = true
      
      // Progressive delay for retries (pregnancy-adapted)
      const delay = pregnancyAdaptations 
        ? retryDelay * operation.retries * 0.8 // Shorter delays for comfort
        : retryDelay * operation.retries
      
      await new Promise(resolve => setTimeout(resolve, delay))
      
      const result = await retryFn()
      commitOptimistic(operationId, result)
      
      return true
    } catch (error) {
      console.warn(`Retry ${operation.retries} failed for operation ${operationId}:`, error)
      
      if (operation.retries >= operation.maxRetries) {
        rollbackOptimistic(operationId, error as Error, true)
        return false
      }
      
      // Schedule another retry
      setTimeout(() => retryOptimistic(operationId, retryFn), delay)
      return false
    } finally {
      isProcessing.value = false
    }
  }

  /**
   * Auto-rollback operations that exceed timeout
   */
  function setupAutoRollback(operationId: string): void {
    setTimeout(() => {
      const operation = pendingOperations.value.get(operationId)
      if (operation) {
        rollbackOptimistic(
          operationId,
          new Error('Operation timed out'),
          pregnancyAdaptations // Only show message if pregnancy adaptations are enabled
        )
      }
    }, timeoutMs)
  }

  /**
   * Get pregnancy-friendly error messages
   */
  function getPregnancyFriendlyErrorMessage(
    type: 'add' | 'update' | 'remove',
    error?: Error
  ): string {
    if (!pregnancyAdaptations) {
      switch (type) {
        case 'add': return 'Failed to add item'
        case 'update': return 'Failed to update item'
        case 'remove': return 'Failed to remove item'
        default: return 'Operation failed'
      }
    }

    // Pregnancy-friendly messages
    const networkIssue = error?.message?.includes('network') || 
                        error?.message?.includes('fetch') ||
                        error?.message?.includes('timeout')

    if (networkIssue) {
      return "Connection seems a bit slow right now. We'll keep trying gently."
    }

    switch (type) {
      case 'add':
        return "Your beautiful moment is taking a bit longer to save. We'll try again shortly."
      case 'update':
        return "Your update is taking its time. We'll make sure it gets through."
      case 'remove':
        return "Having a little trouble with that change. We'll sort it out soon."
      default:
        return "Everything's okay, just taking a moment longer than expected."
    }
  }

  /**
   * Update latency statistics
   */
  function updateLatencyStats(startTime: number): void {
    const latency = Date.now() - startTime
    const currentAvg = stats.averageLatency
    const totalSuccessful = stats.successfulOperations
    
    stats.averageLatency = (currentAvg * (totalSuccessful - 1) + latency) / totalSuccessful
  }

  /**
   * Update user satisfaction score based on success/failure
   */
  function updateSatisfactionScore(success: boolean): void {
    const total = stats.totalOperations
    const successful = stats.successfulOperations
    const successRate = successful / total
    
    // Calculate satisfaction score (pregnancy-weighted)
    if (pregnancyAdaptations) {
      // More forgiving scoring for pregnancy users
      stats.userSatisfactionScore = Math.max(70, Math.min(100, successRate * 110))
    } else {
      stats.userSatisfactionScore = Math.max(0, Math.min(100, successRate * 100))
    }
  }

  /**
   * Batch multiple optimistic operations
   */
  function batchOptimistic<TData = T>(
    operations: Array<{
      id: string
      type: 'add' | 'update' | 'remove'
      data: TData
      originalData?: TData
      rollbackFn?: () => void
    }>
  ): string[] {
    const operationIds: string[] = []
    
    operations.forEach(op => {
      const operationId = applyOptimistic(
        op.id,
        op.type,
        op.data,
        op.originalData,
        op.rollbackFn
      )
      operationIds.push(operationId)
    })

    return operationIds
  }

  /**
   * Check if operation is pending
   */
  function isPending(operationId: string): boolean {
    return pendingOperations.value.has(operationId)
  }

  /**
   * Check if operation failed
   */
  function hasFailed(operationId: string): boolean {
    return failedOperations.value.has(operationId)
  }

  /**
   * Clear all failed operations
   */
  function clearFailedOperations(): void {
    failedOperations.value.clear()
  }

  /**
   * Get pending operations count
   */
  const pendingCount = computed(() => pendingOperations.value.size)
  
  /**
   * Get failed operations count
   */
  const failedCount = computed(() => failedOperations.value.size)

  /**
   * Check if any operations are in progress
   */
  const hasActiveOperations = computed(() => 
    pendingOperations.value.size > 0 || isProcessing.value
  )

  /**
   * Cleanup all pending operations
   */
  function cleanup(): void {
    // Rollback all pending operations
    Array.from(pendingOperations.value.keys()).forEach(operationId => {
      rollbackOptimistic(operationId, new Error('Component unmounted'), false)
    })
    
    pendingOperations.value.clear()
    failedOperations.value.clear()
    
    // Reset stats
    Object.assign(stats, {
      totalOperations: 0,
      successfulOperations: 0,
      failedOperations: 0,
      averageLatency: 0,
      userSatisfactionScore: 100
    })
  }

  return {
    // State
    pendingOperations: readonly(pendingOperations),
    failedOperations: readonly(failedOperations),
    isProcessing: readonly(isProcessing),
    stats: readonly(stats),
    
    // Computed
    pendingCount,
    failedCount,
    hasActiveOperations,
    
    // Methods
    applyOptimistic,
    commitOptimistic,
    rollbackOptimistic,
    retryOptimistic,
    batchOptimistic,
    isPending,
    hasFailed,
    clearFailedOperations,
    setupAutoRollback,
    cleanup
  }
}