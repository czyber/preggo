// Preggo App Service Worker - Pregnancy-focused offline experience
// Optimized for maternal health content and family engagement

const CACHE_NAME = 'preggo-app-v1'
const RUNTIME_CACHE = 'preggo-runtime-v1'
const IMAGES_CACHE = 'preggo-images-v1'
const API_CACHE = 'preggo-api-v1'
const CONTENT_CACHE = 'preggo-content-v1'

// Critical assets for offline functionality
const CRITICAL_ASSETS = [
  '/',
  '/family-feed',
  '/manifest.json',
  '/css/main.css',
  '/js/app.js',
  '/fonts/Inter-Regular.woff2',
  '/fonts/Poppins-Regular.woff2',
  // Pregnancy-specific offline content
  '/offline-pregnancy-tips.json',
  '/emergency-pregnancy-info.json'
]

// Pregnancy week content that should be cached
const PREGNANCY_CONTENT_PATTERNS = [
  /\/api\/v1\/content\/weekly\/\d+/,
  /\/api\/v1\/pregnancies\/[^\/]+$/,
  /\/api\/v1\/feed\/personal\/[^\/]+$/
]

// API endpoints to cache for offline access
const CACHEABLE_API_PATTERNS = [
  /\/api\/v1\/auth\/me$/,
  /\/api\/v1\/pregnancies\//,
  /\/api\/v1\/content\//,
  /\/api\/v1\/feed\//
]

// Network-first patterns (always try network first)
const NETWORK_FIRST_PATTERNS = [
  /\/api\/v1\/posts$/,
  /\/api\/v1\/feed\/family/,
  /\/api\/v1\/.*\/reactions$/,
  /\/api\/v1\/.*\/comments$/
]

// Image optimization patterns
const IMAGE_PATTERNS = [
  /\.(jpg|jpeg|png|gif|webp|avif|svg)$/i,
  /\/storage\/.*\.(jpg|jpeg|png|gif|webp|avif)$/i
]

// Install event - cache critical assets
self.addEventListener('install', (event) => {
  console.log('Preggo SW: Installing service worker')
  
  event.waitUntil(
    Promise.all([
      // Cache critical assets
      caches.open(CACHE_NAME).then(cache => {
        console.log('Preggo SW: Caching critical assets')
        return cache.addAll(CRITICAL_ASSETS.map(url => new Request(url, { credentials: 'same-origin' })))
      }),
      
      // Pre-cache essential pregnancy content
      cacheEssentialPregnancyContent(),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Preggo SW: Activating service worker')
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName.startsWith('preggo-') && !isCurrentCache(cacheName))
            .map(cacheName => {
              console.log('Preggo SW: Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            })
        )
      }),
      
      // Claim all clients
      self.clients.claim()
    ])
  )
})

// Fetch event - handle all network requests
self.addEventListener('fetch', (event) => {
  const { request } = event
  const { url, method } = request
  
  // Only handle GET requests
  if (method !== 'GET') return
  
  // Handle different types of requests
  if (isApiRequest(url)) {
    event.respondWith(handleApiRequest(request))
  } else if (isImageRequest(url)) {
    event.respondWith(handleImageRequest(request))
  } else if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request))
  } else {
    event.respondWith(handlePageRequest(request))
  }
})

// Handle API requests with pregnancy-aware caching
async function handleApiRequest(request) {
  const url = request.url
  
  try {
    // Network-first for real-time data
    if (isNetworkFirst(url)) {
      return await handleNetworkFirst(request, API_CACHE)
    }
    
    // Cache-first for pregnancy content
    if (isPregnancyContent(url)) {
      return await handleCacheFirst(request, CONTENT_CACHE, { maxAge: 24 * 60 * 60 * 1000 }) // 24 hours
    }
    
    // Stale-while-revalidate for user data
    return await handleStaleWhileRevalidate(request, API_CACHE)
    
  } catch (error) {
    console.error('Preggo SW: API request failed:', error)
    return handleOfflineResponse(request)
  }
}

// Handle image requests with optimization
async function handleImageRequest(request) {
  const cache = await caches.open(IMAGES_CACHE)
  
  try {
    // Try cache first for images
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Fetch and cache
    const response = await fetch(request)
    if (response.ok) {
      // Only cache successful responses
      cache.put(request, response.clone())
    }
    return response
    
  } catch (error) {
    console.error('Preggo SW: Image request failed:', error)
    // Return pregnancy-themed placeholder
    return getPregnancyPlaceholder(request.url)
  }
}

// Handle static assets
async function handleStaticAsset(request) {
  return await handleCacheFirst(request, CACHE_NAME)
}

// Handle page requests
async function handlePageRequest(request) {
  try {
    // Try network first for pages
    const networkResponse = await fetch(request)
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
    
  } catch (error) {
    // Try cache
    const cache = await caches.open(RUNTIME_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return getOfflinePage()
    }
    
    throw error
  }
}

// Network-first strategy
async function handleNetworkFirst(request, cacheName, options = {}) {
  const cache = await caches.open(cacheName)
  
  try {
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      // Cache with TTL if specified
      if (options.maxAge) {
        const responseToCache = networkResponse.clone()
        responseToCache.headers.set('sw-cache-timestamp', Date.now().toString())
        cache.put(request, responseToCache)
      } else {
        cache.put(request, networkResponse.clone())
      }
    }
    
    return networkResponse
    
  } catch (error) {
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      // Check TTL if specified
      if (options.maxAge) {
        const timestamp = cachedResponse.headers.get('sw-cache-timestamp')
        if (timestamp && (Date.now() - parseInt(timestamp)) > options.maxAge) {
          cache.delete(request)
          throw error
        }
      }
      return cachedResponse
    }
    
    throw error
  }
}

// Cache-first strategy
async function handleCacheFirst(request, cacheName, options = {}) {
  const cache = await caches.open(cacheName)
  const cachedResponse = await cache.match(request)
  
  if (cachedResponse) {
    // Check TTL if specified
    if (options.maxAge) {
      const timestamp = cachedResponse.headers.get('sw-cache-timestamp')
      if (timestamp && (Date.now() - parseInt(timestamp)) > options.maxAge) {
        cache.delete(request)
      } else {
        return cachedResponse
      }
    } else {
      return cachedResponse
    }
  }
  
  try {
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone()
      if (options.maxAge) {
        responseToCache.headers.set('sw-cache-timestamp', Date.now().toString())
      }
      cache.put(request, responseToCache)
    }
    
    return networkResponse
    
  } catch (error) {
    if (cachedResponse) return cachedResponse
    throw error
  }
}

// Stale-while-revalidate strategy
async function handleStaleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cachedResponse = await cache.match(request)
  
  // Fetch in background
  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone())
    }
    return response
  }).catch(() => {
    // Network failed, return cached if available
    return cachedResponse
  })
  
  // Return cached immediately if available
  return cachedResponse || fetchPromise
}

// Pre-cache essential pregnancy content
async function cacheEssentialPregnancyContent() {
  const contentCache = await caches.open(CONTENT_CACHE)
  
  const essentialContent = [
    // Emergency pregnancy information
    {
      url: '/api/v1/content/emergency-pregnancy-info',
      data: {
        emergencyContacts: [
          { type: 'Emergency', number: '911', description: 'Life-threatening emergency' },
          { type: 'Maternal Emergency', number: '1-800-MATERNAL', description: 'Pregnancy-related emergency' }
        ],
        warningsSigns: [
          'Severe headache with blurred vision',
          'Severe abdominal pain',
          'Heavy bleeding',
          'Persistent vomiting',
          'High fever (>101°F)',
          'Decreased fetal movement'
        ],
        comfortMeasures: [
          'Rest and hydration',
          'Gentle breathing exercises',
          'Comfortable positioning',
          'Contact healthcare provider'
        ]
      }
    },
    
    // Basic pregnancy tips for offline access
    {
      url: '/api/v1/content/offline-tips',
      data: {
        generalTips: [
          'Stay hydrated - aim for 8-10 glasses of water daily',
          'Take prenatal vitamins as recommended',
          'Get adequate rest - listen to your body',
          'Eat small, frequent meals to help with nausea',
          'Practice gentle exercises like walking or prenatal yoga',
          'Track baby movements after 20 weeks'
        ],
        nutritionTips: [
          'Include protein in every meal',
          'Choose whole grains over refined',
          'Eat plenty of fruits and vegetables',
          'Include calcium-rich foods',
          'Limit caffeine and avoid alcohol',
          'Take folic acid supplements'
        ]
      }
    }
  ]
  
  // Cache essential content
  for (const content of essentialContent) {
    const response = new Response(JSON.stringify(content.data), {
      headers: {
        'Content-Type': 'application/json',
        'sw-cache-timestamp': Date.now().toString()
      }
    })
    await contentCache.put(content.url, response)
  }
}

// Utility functions
function isCurrentCache(cacheName) {
  return [CACHE_NAME, RUNTIME_CACHE, IMAGES_CACHE, API_CACHE, CONTENT_CACHE].includes(cacheName)
}

function isApiRequest(url) {
  return url.includes('/api/v1/')
}

function isImageRequest(url) {
  return IMAGE_PATTERNS.some(pattern => pattern.test(url))
}

function isStaticAsset(url) {
  return /\.(js|css|woff2?|json)$/i.test(url)
}

function isNetworkFirst(url) {
  return NETWORK_FIRST_PATTERNS.some(pattern => pattern.test(url))
}

function isPregnancyContent(url) {
  return PREGNANCY_CONTENT_PATTERNS.some(pattern => pattern.test(url))
}

// Handle offline responses
function handleOfflineResponse(request) {
  const url = request.url
  
  if (url.includes('/api/v1/content/')) {
    // Return cached pregnancy tips for content requests
    return caches.open(CONTENT_CACHE).then(cache => {
      return cache.match('/api/v1/content/offline-tips')
    })
  }
  
  if (url.includes('/api/v1/')) {
    // Return offline API response
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'You are currently offline. Some features may not be available.',
      pregnancyTip: 'Remember to stay hydrated and rest when needed.'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
  
  return new Response('Offline', { status: 503 })
}

// Get pregnancy-themed placeholder for failed images
function getPregnancyPlaceholder(imageUrl) {
  // Generate SVG placeholder with pregnancy theme
  const svg = `
    <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#FFF3E0;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#F8BBD0;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#grad)"/>
      <text x="50%" y="45%" text-anchor="middle" font-family="system-ui" font-size="48" fill="rgba(0,0,0,0.1)">👶</text>
      <text x="50%" y="65%" text-anchor="middle" font-family="system-ui" font-size="14" fill="rgba(0,0,0,0.3)">Image temporarily unavailable</text>
      <text x="50%" y="80%" text-anchor="middle" font-family="system-ui" font-size="12" fill="rgba(0,0,0,0.2)">Will load when connection returns</text>
    </svg>
  `
  
  return new Response(svg, {
    headers: { 'Content-Type': 'image/svg+xml' }
  })
}

// Get offline page
function getOfflinePage() {
  const offlineHTML = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Offline - Preggo</title>
      <style>
        body {
          font-family: system-ui, -apple-system, sans-serif;
          background: linear-gradient(135deg, #FFF3E0, #F8BBD0);
          margin: 0;
          padding: 2rem;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #333;
        }
        .container {
          text-align: center;
          background: white;
          padding: 2rem;
          border-radius: 16px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          max-width: 400px;
          width: 100%;
        }
        .icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        h1 {
          color: #E91E63;
          margin-bottom: 1rem;
        }
        p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 1.5rem;
        }
        .tips {
          background: #FFF3E0;
          padding: 1rem;
          border-radius: 8px;
          margin-top: 1.5rem;
          text-align: left;
        }
        .tips h3 {
          margin-top: 0;
          color: #FF6F00;
        }
        .tips ul {
          margin: 0.5rem 0;
          padding-left: 1.5rem;
        }
        .tips li {
          margin: 0.5rem 0;
          color: #666;
        }
        button {
          background: #E91E63;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 1rem;
          cursor: pointer;
          margin-top: 1rem;
        }
        button:hover {
          background: #C2185B;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">👶💕</div>
        <h1>You're Currently Offline</h1>
        <p>Don't worry - your pregnancy journey continues even when you're offline. Here are some gentle reminders while you wait for your connection to return.</p>
        
        <div class="tips">
          <h3>Gentle Reminders</h3>
          <ul>
            <li>Stay hydrated with plenty of water</li>
            <li>Take deep breaths and rest if needed</li>
            <li>Listen to your body and take breaks</li>
            <li>Remember to take your prenatal vitamins</li>
            <li>Try gentle stretching or meditation</li>
          </ul>
        </div>
        
        <button onclick="location.reload()">Try Again</button>
      </div>
    </body>
    </html>
  `
  
  return new Response(offlineHTML, {
    headers: { 'Content-Type': 'text/html' }
  })
}

// Handle background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'pregnancy-data-sync') {
    event.waitUntil(syncPregnancyData())
  }
  
  if (event.tag === 'family-reactions-sync') {
    event.waitUntil(syncFamilyReactions())
  }
})

// Sync pregnancy data when back online
async function syncPregnancyData() {
  console.log('Preggo SW: Syncing pregnancy data')
  
  try {
    // Get pending pregnancy updates from IndexedDB or cache
    const pendingUpdates = await getPendingUpdates('pregnancy-updates')
    
    for (const update of pendingUpdates) {
      try {
        const response = await fetch(update.url, {
          method: update.method,
          headers: update.headers,
          body: update.body
        })
        
        if (response.ok) {
          await removePendingUpdate('pregnancy-updates', update.id)
        }
      } catch (error) {
        console.error('Preggo SW: Failed to sync update:', error)
      }
    }
  } catch (error) {
    console.error('Preggo SW: Pregnancy data sync failed:', error)
  }
}

// Sync family reactions when back online
async function syncFamilyReactions() {
  console.log('Preggo SW: Syncing family reactions')
  
  try {
    const pendingReactions = await getPendingUpdates('family-reactions')
    
    for (const reaction of pendingReactions) {
      try {
        const response = await fetch(reaction.url, {
          method: reaction.method,
          headers: reaction.headers,
          body: reaction.body
        })
        
        if (response.ok) {
          await removePendingUpdate('family-reactions', reaction.id)
        }
      } catch (error) {
        console.error('Preggo SW: Failed to sync reaction:', error)
      }
    }
  } catch (error) {
    console.error('Preggo SW: Family reactions sync failed:', error)
  }
}

// Helper functions for background sync
async function getPendingUpdates(storeName) {
  // This would typically use IndexedDB to store pending updates
  // For now, return empty array as placeholder
  return []
}

async function removePendingUpdate(storeName, updateId) {
  // This would remove the update from IndexedDB
  console.log(`Removing pending update ${updateId} from ${storeName}`)
}

// Handle push notifications for pregnancy updates
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json()
    
    const options = {
      body: data.body,
      icon: '/icon-192.png',
      badge: '/badge-72.png',
      tag: data.tag || 'pregnancy-update',
      data: data.data || {},
      actions: data.actions || [],
      requireInteraction: data.urgent || false,
      silent: data.silent || false
    }
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    )
  }
})

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  const urlToOpen = event.notification.data.url || '/'
  
  event.waitUntil(
    clients.matchAll().then(clientList => {
      // Check if app is already open
      for (const client of clientList) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus()
        }
      }
      
      // Open new window/tab
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen)
      }
    })
  )
})

console.log('Preggo SW: Service worker loaded successfully')