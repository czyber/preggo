/**
 * WebSocket composable for real-time feed updates
 * Instagram-like real-time reactions, comments, and notifications
 */

import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useToast } from './useToast'

interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
  enableCompression: boolean
  pregnancyOptimizations: boolean
  enableHaptics: boolean
}

interface WebSocketMessage {
  type: string
  payload: any
  timestamp: number
  id?: string
}

interface ConnectionStats {
  connectedAt?: Date
  reconnectAttempts: number
  messagesReceived: number
  messagesSent: number
  latency: number
  isStable: boolean
}

type MessageHandler = (message: WebSocketMessage) => void
type ConnectionHandler = (connected: boolean) => void

export function useWebSocket(config: Partial<WebSocketConfig> = {}) {
  const {
    url = process.env.NUXT_PUBLIC_WS_URL || 'ws://localhost:8001/ws',
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    enableCompression = true,
    pregnancyOptimizations = true,
    enableHaptics = true
  } = config

  const toast = useToast()

  // Connection state
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionError = ref<string | null>(null)
  const lastPongReceived = ref<number>(0)

  // Statistics
  const stats = reactive<ConnectionStats>({
    reconnectAttempts: 0,
    messagesReceived: 0,
    messagesSent: 0,
    latency: 0,
    isStable: false
  })

  // Event handlers
  const messageHandlers = new Map<string, Set<MessageHandler>>()
  const connectionHandlers = new Set<ConnectionHandler>()

  // Timers
  let reconnectTimer: number | null = null
  let heartbeatTimer: number | null = null
  let latencyTimer: number | null = null

  /**
   * Connect to WebSocket with pregnancy-optimized settings
   */
  function connect(): Promise<void> {
    if (socket.value?.readyState === WebSocket.OPEN) {
      return Promise.resolve()
    }

    if (isConnecting.value) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        isConnecting.value = true
        connectionError.value = null

        // Create WebSocket connection
        const wsUrl = new URL(url)
        if (enableCompression) {
          wsUrl.searchParams.set('compression', 'true')
        }
        if (pregnancyOptimizations) {
          wsUrl.searchParams.set('pregnancy-mode', 'true')
        }

        socket.value = new WebSocket(wsUrl.toString())

        // Connection opened
        socket.value.onopen = () => {
          isConnected.value = true
          isConnecting.value = false
          stats.connectedAt = new Date()
          stats.reconnectAttempts = 0
          
          // Start heartbeat
          startHeartbeat()
          
          // Notify handlers
          connectionHandlers.forEach(handler => handler(true))
          
          // Provide gentle connection feedback
          if (pregnancyOptimizations && enableHaptics && 'vibrate' in navigator) {
            navigator.vibrate([15, 5, 15]) // Connected pattern
          }
          
          resolve()
        }

        // Message received
        socket.value.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            handleIncomingMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        // Connection closed
        socket.value.onclose = (event) => {
          isConnected.value = false
          isConnecting.value = false
          stopHeartbeat()
          
          // Notify handlers
          connectionHandlers.forEach(handler => handler(false))
          
          // Auto-reconnect if not a clean close
          if (!event.wasClean && stats.reconnectAttempts < maxReconnectAttempts) {
            scheduleReconnect()
          }
        }

        // Connection error
        socket.value.onerror = (error) => {
          console.error('WebSocket error:', error)
          connectionError.value = 'Connection error occurred'
          isConnecting.value = false
          
          reject(error)
        }

      } catch (error) {
        isConnecting.value = false
        connectionError.value = 'Failed to establish connection'
        reject(error)
      }
    })
  }

  /**
   * Disconnect from WebSocket
   */
  function disconnect(): void {
    if (socket.value) {
      socket.value.close(1000, 'Normal closure')
      socket.value = null
    }
    
    stopHeartbeat()
    clearReconnectTimer()
    
    isConnected.value = false
    isConnecting.value = false
    connectionError.value = null
  }

  /**
   * Send message to WebSocket
   */
  function send(type: string, payload: any, id?: string): boolean {
    if (!isConnected.value || !socket.value) {
      console.warn('Cannot send message: WebSocket not connected')
      return false
    }

    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: Date.now(),
      ...(id && { id })
    }

    try {
      socket.value.send(JSON.stringify(message))
      stats.messagesSent++
      return true
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      return false
    }
  }

  /**
   * Handle incoming messages with pregnancy-optimized processing
   */
  function handleIncomingMessage(message: WebSocketMessage): void {
    stats.messagesReceived++

    // Handle special message types
    switch (message.type) {
      case 'pong':
        handlePong(message)
        break
      case 'heartbeat':
        lastPongReceived.value = Date.now()
        break
      case 'reaction':
        handleRealtimeReaction(message)
        break
      case 'comment':
        handleRealtimeComment(message)
        break
      case 'milestone':
        handleMilestoneNotification(message)
        break
      default:
        // Forward to registered handlers
        const handlers = messageHandlers.get(message.type)
        if (handlers) {
          handlers.forEach(handler => {
            try {
              handler(message)
            } catch (error) {
              console.error('Message handler error:', error)
            }
          })
        }
        break
    }
  }

  /**
   * Handle real-time reaction with pregnancy-friendly feedback
   */
  function handleRealtimeReaction(message: WebSocketMessage): void {
    const { postId, reactionType, userId, userDisplayName } = message.payload

    // Provide gentle haptic feedback
    if (pregnancyOptimizations && enableHaptics && 'vibrate' in navigator) {
      navigator.vibrate([10]) // Gentle pulse for reactions
    }

    // Show pregnancy-friendly toast for milestone posts
    if (message.payload.isMilestone && pregnancyOptimizations) {
      const reactionEmoji = getReactionEmoji(reactionType)
      toast.add({
        title: 'Family love received',
        description: `${userDisplayName} sent ${reactionEmoji} to your special moment`,
        type: 'success',
        duration: 3000
      })
    }

    // Forward to reaction handlers
    const handlers = messageHandlers.get('reaction')
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }
  }

  /**
   * Handle real-time comments
   */
  function handleRealtimeComment(message: WebSocketMessage): void {
    const { postId, comment, userId, userDisplayName } = message.payload

    // Provide gentle haptic feedback
    if (pregnancyOptimizations && enableHaptics && 'vibrate' in navigator) {
      navigator.vibrate([15, 5, 10]) // Comment pattern
    }

    // Show pregnancy-friendly toast
    if (pregnancyOptimizations) {
      toast.add({
        title: 'New family message',
        description: `${userDisplayName} commented on your post`,
        type: 'info',
        duration: 4000
      })
    }

    // Forward to comment handlers
    const handlers = messageHandlers.get('comment')
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }
  }

  /**
   * Handle milestone notifications with special care
   */
  function handleMilestoneNotification(message: WebSocketMessage): void {
    const { milestone, week, description } = message.payload

    // Special vibration pattern for milestones
    if (pregnancyOptimizations && enableHaptics && 'vibrate' in navigator) {
      navigator.vibrate([25, 10, 25, 10, 50]) // Celebration pattern
    }

    // Show beautiful milestone toast
    toast.add({
      title: '✨ Milestone Moment',
      description: `Week ${week}: ${description}`,
      type: 'success',
      duration: 8000
    })

    // Forward to milestone handlers
    const handlers = messageHandlers.get('milestone')
    if (handlers) {
      handlers.forEach(handler => handler(message))
    }
  }

  /**
   * Handle pong response for latency calculation
   */
  function handlePong(message: WebSocketMessage): void {
    if (latencyTimer && message.payload.pingTimestamp) {
      const latency = Date.now() - message.payload.pingTimestamp
      stats.latency = latency
      stats.isStable = latency < 200 // Consider stable if under 200ms
      
      clearTimeout(latencyTimer)
      latencyTimer = null
    }
    lastPongReceived.value = Date.now()
  }

  /**
   * Start heartbeat to keep connection alive
   */
  function startHeartbeat(): void {
    stopHeartbeat()
    
    heartbeatTimer = window.setInterval(() => {
      if (isConnected.value) {
        const pingTimestamp = Date.now()
        
        // Start latency measurement
        latencyTimer = window.setTimeout(() => {
          stats.isStable = false // Connection seems unstable
        }, 5000)
        
        send('ping', { pingTimestamp })
        
        // Check if we missed too many pongs
        if (lastPongReceived.value > 0 && 
            Date.now() - lastPongReceived.value > heartbeatInterval * 2) {
          console.warn('WebSocket appears to be unresponsive, reconnecting...')
          socket.value?.close()
        }
      }
    }, heartbeatInterval)
  }

  /**
   * Stop heartbeat timer
   */
  function stopHeartbeat(): void {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (latencyTimer) {
      clearTimeout(latencyTimer)
      latencyTimer = null
    }
  }

  /**
   * Schedule reconnection with pregnancy-optimized backoff
   */
  function scheduleReconnect(): void {
    if (stats.reconnectAttempts >= maxReconnectAttempts) {
      connectionError.value = 'Maximum reconnection attempts reached'
      if (pregnancyOptimizations) {
        toast.add({
          title: 'Connection taking a break',
          description: "We'll try reconnecting again in a moment. Your content is safe.",
          type: 'info',
          duration: 6000
        })
      }
      return
    }

    clearReconnectTimer()
    
    // Progressive backoff with pregnancy adaptations
    const baseDelay = pregnancyOptimizations ? reconnectInterval * 0.8 : reconnectInterval
    const delay = baseDelay * Math.pow(1.5, stats.reconnectAttempts)
    
    reconnectTimer = window.setTimeout(() => {
      stats.reconnectAttempts++
      connect().catch(() => {
        scheduleReconnect()
      })
    }, delay)
  }

  /**
   * Clear reconnect timer
   */
  function clearReconnectTimer(): void {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  /**
   * Register message handler
   */
  function onMessage(type: string, handler: MessageHandler): () => void {
    if (!messageHandlers.has(type)) {
      messageHandlers.set(type, new Set())
    }
    
    messageHandlers.get(type)!.add(handler)
    
    // Return unsubscribe function
    return () => {
      const handlers = messageHandlers.get(type)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          messageHandlers.delete(type)
        }
      }
    }
  }

  /**
   * Register connection handler
   */
  function onConnection(handler: ConnectionHandler): () => void {
    connectionHandlers.add(handler)
    
    return () => {
      connectionHandlers.delete(handler)
    }
  }

  /**
   * Get emoji for reaction type
   */
  function getReactionEmoji(reactionType: string): string {
    const emojiMap: Record<string, string> = {
      love: '❤️',
      excited: '😍',
      care: '🤗',
      support: '💪',
      beautiful: '✨',
      funny: '😂',
      praying: '🙏',
      proud: '🏆',
      grateful: '🙏✨'
    }
    return emojiMap[reactionType] || '❤️'
  }

  // Computed properties
  const connectionStatus = computed(() => {
    if (isConnected.value) return 'connected'
    if (isConnecting.value) return 'connecting'
    if (connectionError.value) return 'error'
    return 'disconnected'
  })

  const isHealthy = computed(() => {
    return isConnected.value && stats.isStable && stats.latency < 300
  })

  // Lifecycle
  onMounted(() => {
    // Auto-connect on mount
    connect().catch(console.error)
  })

  onUnmounted(() => {
    // Clean disconnect on unmount
    disconnect()
    messageHandlers.clear()
    connectionHandlers.clear()
  })

  return {
    // State
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    connectionError: readonly(connectionError),
    stats: readonly(stats),
    
    // Computed
    connectionStatus,
    isHealthy,
    
    // Methods
    connect,
    disconnect,
    send,
    onMessage,
    onConnection
  }
}