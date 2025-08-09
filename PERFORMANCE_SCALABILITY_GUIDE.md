# Performance & Scalability Implementation Guide
## Feed System Overhaul for Family Engagement

### Executive Summary

This guide provides detailed implementation strategies to achieve **< 200ms perceived response times** for the Preggo family feed system while supporting high-engagement family sharing. The focus is on immediate user responses through optimistic updates, comprehensive caching, and real-time performance optimization.

### Current Architecture Analysis

Based on the existing codebase:
- **Backend**: FastAPI with PostgreSQL, basic ETag caching (2-5 minutes)
- **Frontend**: Nuxt.js with Vue 3, Pinia state management, component-level animations
- **API**: RESTful endpoints with type-safe OpenAPI integration
- **Feed Types**: Family feed, personal timeline, story cards, integrated content

---

## 1. Immediate Response Strategy (< 200ms Perceived)

### 1.1 Optimistic Updates Implementation

**Frontend State Management Enhancement**

```typescript
// stores/feed.ts - Enhanced with optimistic updates
export const useFeedStore = defineStore('feed', () => {
  const posts = ref<Post[]>([])
  const optimisticUpdates = ref<Map<string, OptimisticUpdate>>(new Map())
  
  // Optimistic reaction update
  const addReactionOptimistic = async (postId: string, reactionType: string) => {
    const tempId = `temp-${Date.now()}`
    const currentPost = posts.value.find(p => p.id === postId)
    
    if (currentPost) {
      // Immediate UI update (< 16ms)
      const optimisticReaction = {
        id: tempId,
        postId,
        userId: useAuthStore().user?.id,
        type: reactionType,
        timestamp: new Date().toISOString(),
        isOptimistic: true
      }
      
      // Update local state immediately
      currentPost.reactions = [...currentPost.reactions, optimisticReaction]
      currentPost.reactionCounts[reactionType] = (currentPost.reactionCounts[reactionType] || 0) + 1
      
      // Store optimistic update for rollback
      optimisticUpdates.value.set(tempId, {
        type: 'reaction',
        postId,
        tempId,
        originalState: structuredClone(currentPost),
        timestamp: Date.now()
      })
      
      try {
        // Background API call
        const result = await api.addPostReaction(postId, { reaction_type: reactionType })
        
        if (result.data) {
          // Replace optimistic update with real data
          const realReactionId = result.data.reaction_id
          currentPost.reactions = currentPost.reactions.map(r => 
            r.id === tempId ? { ...r, id: realReactionId, isOptimistic: false } : r
          )
          optimisticUpdates.value.delete(tempId)
        } else {
          throw new Error('API response invalid')
        }
      } catch (error) {
        // Rollback on failure
        rollbackOptimisticUpdate(tempId)
        showErrorToast('Failed to add reaction')
      }
    }
  }
  
  const rollbackOptimisticUpdate = (tempId: string) => {
    const update = optimisticUpdates.value.get(tempId)
    if (update && update.type === 'reaction') {
      const post = posts.value.find(p => p.id === update.postId)
      if (post && update.originalState) {
        Object.assign(post, update.originalState)
      }
    }
    optimisticUpdates.value.delete(tempId)
  }
  
  return { addReactionOptimistic, rollbackOptimisticUpdate }
})
```

**Optimistic Post Creation**

```typescript
// stores/feed.ts - Optimistic post creation
const createPostOptimistic = async (postData: CreatePostRequest) => {
  const tempId = `temp-post-${Date.now()}`
  const optimisticPost = {
    ...postData,
    id: tempId,
    createdAt: new Date().toISOString(),
    isOptimistic: true,
    reactions: [],
    comments: [],
    reactionCounts: {},
    status: 'pending' as const
  }
  
  // Add to feed immediately
  posts.value.unshift(optimisticPost)
  
  // Store for rollback
  optimisticUpdates.value.set(tempId, {
    type: 'post',
    tempId,
    timestamp: Date.now()
  })
  
  try {
    const result = await api.createPost(postData)
    if (result.data) {
      // Replace optimistic post with real post
      const index = posts.value.findIndex(p => p.id === tempId)
      if (index !== -1) {
        posts.value[index] = { ...result.data, isOptimistic: false }
      }
    }
  } catch (error) {
    // Remove failed post
    posts.value = posts.value.filter(p => p.id !== tempId)
    showErrorToast('Failed to create post')
  }
}
```

### 1.2 Local State Management

**Enhanced Pinia Store with Local Persistence**

```typescript
// stores/feed.ts - Local persistence
import { useStorage } from '@vueuse/core'

export const useFeedStore = defineStore('feed', () => {
  // Persist critical feed data locally
  const cachedPosts = useStorage('feed-cache', [] as Post[], localStorage, {
    serializer: {
      read: (v) => v ? JSON.parse(v) : [],
      write: (v) => JSON.stringify(v)
    }
  })
  
  const cachedTimestamp = useStorage('feed-cache-timestamp', 0, localStorage)
  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
  
  const loadFromCache = () => {
    const now = Date.now()
    if (cachedTimestamp.value && (now - cachedTimestamp.value) < CACHE_DURATION) {
      posts.value = [...cachedPosts.value]
      return true
    }
    return false
  }
  
  const saveToCache = () => {
    cachedPosts.value = posts.value.filter(p => !p.isOptimistic)
    cachedTimestamp.value = Date.now()
  }
  
  return { loadFromCache, saveToCache }
})
```

### 1.3 Rollback Mechanisms

**Comprehensive Error Recovery**

```typescript
// composables/useOptimisticUpdates.ts
export const useOptimisticUpdates = () => {
  const rollbackQueue = ref<RollbackOperation[]>([])
  
  const scheduleRollback = (operation: RollbackOperation, delay = 10000) => {
    rollbackQueue.value.push(operation)
    
    setTimeout(() => {
      if (rollbackQueue.value.includes(operation)) {
        executeRollback(operation)
        rollbackQueue.value = rollbackQueue.value.filter(op => op !== operation)
      }
    }, delay)
  }
  
  const executeRollback = (operation: RollbackOperation) => {
    switch (operation.type) {
      case 'reaction':
        const feedStore = useFeedStore()
        feedStore.rollbackOptimisticUpdate(operation.tempId)
        break
      case 'post':
        // Remove failed post
        break
      case 'comment':
        // Remove failed comment
        break
    }
  }
  
  return { scheduleRollback, executeRollback }
}
```

---

## 2. Caching Architecture (Multi-Level)

### 2.1 Redis Implementation (Backend)

**Redis Setup and Configuration**

```python
# backend/app/core/cache.py
import redis.asyncio as redis
from typing import Optional, Any, Union
import json
import pickle
from datetime import timedelta
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.json_redis = redis.from_url(redis_url, decode_responses=True)
    
    async def get(self, key: str, use_json: bool = True) -> Optional[Any]:
        """Get cached value"""
        client = self.json_redis if use_json else self.redis
        try:
            value = await client.get(f"preggo:{key}")
            if value is None:
                return None
            
            if use_json:
                return json.loads(value) if isinstance(value, str) else value
            else:
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300, use_json: bool = True) -> bool:
        """Set cached value with TTL"""
        client = self.json_redis if use_json else self.redis
        try:
            serialized = json.dumps(value, default=str) if use_json else pickle.dumps(value)
            await client.setex(f"preggo:{key}", ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def invalidate(self, pattern: str) -> int:
        """Invalidate cache keys by pattern"""
        keys = await self.json_redis.keys(f"preggo:{pattern}")
        if keys:
            return await self.json_redis.delete(*keys)
        return 0
    
    def generate_cache_key(self, *args) -> str:
        """Generate consistent cache key"""
        key_data = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_data.encode()).hexdigest()[:16]

# Initialize cache manager
cache_manager = CacheManager(settings.REDIS_URL)
```

**Feed Caching Implementation**

```python
# backend/app/services/feed_cache_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class FeedCacheService:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.FEED_TTL = 300  # 5 minutes
        self.USER_FEED_TTL = 180  # 3 minutes
        self.TRENDING_TTL = 900  # 15 minutes
        
    async def get_family_feed(
        self, 
        user_id: str, 
        pregnancy_id: str, 
        filter_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached family feed"""
        cache_key = self.cache.generate_cache_key(
            "family_feed", user_id, pregnancy_id, 
            filter_params.get("filter_type", "all"),
            filter_params.get("sort_by", "chronological"),
            filter_params.get("limit", 20),
            filter_params.get("offset", 0)
        )
        
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            # Check if data is still fresh enough
            cache_time = datetime.fromisoformat(cached_data.get("cached_at", ""))
            if (datetime.utcnow() - cache_time).seconds < self.FEED_TTL:
                return cached_data
        
        return None
    
    async def set_family_feed(
        self,
        user_id: str,
        pregnancy_id: str,
        filter_params: Dict[str, Any],
        feed_data: Dict[str, Any]
    ) -> bool:
        """Cache family feed data"""
        cache_key = self.cache.generate_cache_key(
            "family_feed", user_id, pregnancy_id,
            filter_params.get("filter_type", "all"),
            filter_params.get("sort_by", "chronological"),
            filter_params.get("limit", 20),
            filter_params.get("offset", 0)
        )
        
        # Add cache metadata
        cache_data = {
            **feed_data,
            "cached_at": datetime.utcnow().isoformat(),
            "cache_version": "1.0"
        }
        
        return await self.cache.set(cache_key, cache_data, self.FEED_TTL)
    
    async def invalidate_pregnancy_feed(self, pregnancy_id: str) -> int:
        """Invalidate all feed caches for a pregnancy"""
        patterns = [
            f"family_feed*{pregnancy_id}*",
            f"personal_timeline*{pregnancy_id}*",
            f"story_cards*{pregnancy_id}*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += await self.cache.invalidate(pattern)
        
        return total_invalidated

# Initialize service
feed_cache_service = FeedCacheService(cache_manager)
```

### 2.2 Enhanced Backend Caching

**Feed Endpoint with Comprehensive Caching**

```python
# backend/app/api/endpoints/feed.py - Enhanced caching
from fastapi import Header

@router.get("/family/{pregnancy_id}")
async def get_family_feed(
    pregnancy_id: str,
    response: Response,
    if_none_match: Optional[str] = Header(None),
    # ... other parameters
):
    user_id = current_user["sub"]
    
    # Check cache first
    cached_feed = await feed_cache_service.get_family_feed(
        user_id, pregnancy_id, {
            "filter_type": filter_type,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset
        }
    )
    
    if cached_feed:
        # Generate ETag
        etag = _generate_etag(cached_feed, user_id)
        
        # Check if client has current version
        if if_none_match == etag:
            return Response(status_code=304)
        
        # Set cache headers
        response.headers.update({
            "Cache-Control": "private, max-age=180, stale-while-revalidate=60",
            "ETag": etag,
            "X-Cache": "HIT"
        })
        
        return cached_feed["data"]
    
    # Generate fresh feed
    feed_response = await feed_service.get_family_feed(
        session, user_id, pregnancy_id, feed_request
    )
    
    # Cache the response
    await feed_cache_service.set_family_feed(
        user_id, pregnancy_id,
        {
            "filter_type": filter_type,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset
        },
        {"data": feed_response}
    )
    
    # Set response headers
    etag = _generate_etag(feed_response, user_id)
    response.headers.update({
        "Cache-Control": "private, max-age=180, stale-while-revalidate=60",
        "ETag": etag,
        "X-Cache": "MISS"
    })
    
    return feed_response
```

### 2.3 CDN Integration

**Cloudflare/AWS CloudFront Configuration**

```yaml
# cloudflare-workers/feed-cache.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    
    // Cache static feed content
    if (url.pathname.startsWith('/api/v1/feed/')) {
      const cacheKey = new Request(url.toString(), request)
      const cache = caches.default
      
      // Check cache first
      let response = await cache.match(cacheKey)
      
      if (!response) {
        // Fetch from origin
        response = await fetch(request)
        
        // Cache successful responses
        if (response.status === 200) {
          const headers = new Headers(response.headers)
          headers.set('Cache-Control', 'public, max-age=120, stale-while-revalidate=300')
          headers.set('X-Edge-Cache', 'MISS')
          
          const cachedResponse = new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers
          })
          
          await cache.put(cacheKey, cachedResponse.clone())
          return cachedResponse
        }
      } else {
        // Add cache hit header
        const headers = new Headers(response.headers)
        headers.set('X-Edge-Cache', 'HIT')
        response = new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers
        })
      }
      
      return response
    }
    
    return fetch(request)
  }
}
```

### 2.4 Browser Caching Strategy

**Service Worker Implementation**

```javascript
// frontend/public/sw.js
const CACHE_NAME = 'preggo-feed-v1'
const FEED_CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)
  
  // Cache feed API responses
  if (url.pathname.includes('/api/v1/feed/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache => {
        return cache.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            const cacheTime = new Date(cachedResponse.headers.get('sw-cache-time'))
            const now = new Date()
            
            // Return cached version if still fresh
            if ((now - cacheTime) < FEED_CACHE_DURATION) {
              return cachedResponse
            }
          }
          
          // Fetch fresh data
          return fetch(event.request).then(response => {
            if (response.status === 200) {
              const responseClone = response.clone()
              const headers = new Headers(responseClone.headers)
              headers.set('sw-cache-time', new Date().toISOString())
              
              const cachedResponse = new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers
              })
              
              cache.put(event.request, cachedResponse)
            }
            
            return response
          })
        })
      })
    )
  }
})
```

---

## 3. Real-time Performance Optimization

### 3.1 WebSocket Implementation

**Backend WebSocket Manager**

```python
# backend/app/websocket/feed_websocket.py
from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

class FeedWebSocketManager:
    def __init__(self):
        self.pregnancy_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, pregnancy_id: str):
        await websocket.accept()
        
        # Add to pregnancy group
        if pregnancy_id not in self.pregnancy_connections:
            self.pregnancy_connections[pregnancy_id] = set()
        self.pregnancy_connections[pregnancy_id].add(websocket)
        
        # Track user connection
        self.user_connections[user_id] = websocket
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "pregnancy_id": pregnancy_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def disconnect(self, websocket: WebSocket, user_id: str, pregnancy_id: str):
        # Remove from pregnancy group
        if pregnancy_id in self.pregnancy_connections:
            self.pregnancy_connections[pregnancy_id].discard(websocket)
            if not self.pregnancy_connections[pregnancy_id]:
                del self.pregnancy_connections[pregnancy_id]
        
        # Remove user connection
        self.user_connections.pop(user_id, None)
    
    async def broadcast_to_pregnancy(self, pregnancy_id: str, message: dict):
        if pregnancy_id in self.pregnancy_connections:
            disconnected = []
            
            for websocket in self.pregnancy_connections[pregnancy_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.pregnancy_connections[pregnancy_id].discard(ws)
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except:
                del self.user_connections[user_id]

ws_manager = FeedWebSocketManager()

# WebSocket endpoint
@app.websocket("/ws/feed/{pregnancy_id}")
async def websocket_feed(websocket: WebSocket, pregnancy_id: str, token: str):
    # Authenticate user
    user_data = await authenticate_websocket_token(token)
    if not user_data:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    user_id = user_data["sub"]
    
    try:
        await ws_manager.connect(websocket, user_id, pregnancy_id)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_json()
            await handle_websocket_message(data, user_id, pregnancy_id)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(websocket, user_id, pregnancy_id)
```

**Frontend WebSocket Integration**

```typescript
// composables/useWebSocket.ts
export const useWebSocket = (pregnancyId: string) => {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  
  const connect = () => {
    const auth = useAuth()
    const token = auth.session.value?.access_token
    
    if (!token) return
    
    const wsUrl = `wss://api.preggo.app/ws/feed/${pregnancyId}?token=${token}`
    socket.value = new WebSocket(wsUrl)
    
    socket.value.onopen = () => {
      isConnected.value = true
      reconnectAttempts.value = 0
      console.log('WebSocket connected')
    }
    
    socket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleRealtimeUpdate(data)
      } catch (error) {
        console.error('WebSocket message parsing error:', error)
      }
    }
    
    socket.value.onclose = () => {
      isConnected.value = false
      
      // Attempt reconnection
      if (reconnectAttempts.value < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.value++
          connect()
        }, Math.pow(2, reconnectAttempts.value) * 1000) // Exponential backoff
      }
    }
    
    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  const handleRealtimeUpdate = (data: any) => {
    const feedStore = useFeedStore()
    
    switch (data.type) {
      case 'new_post':
        feedStore.addPostRealtime(data.post)
        break
      case 'post_reaction':
        feedStore.updatePostReaction(data.post_id, data.reaction)
        break
      case 'post_comment':
        feedStore.addCommentRealtime(data.post_id, data.comment)
        break
      case 'celebration':
        feedStore.addCelebration(data.celebration)
        break
    }
  }
  
  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      isConnected.value = false
    }
  }
  
  return { connect, disconnect, isConnected }
}
```

### 3.2 Connection Management

**Connection Pooling and Health Monitoring**

```typescript
// composables/useConnectionManager.ts
export const useConnectionManager = () => {
  const connections = ref<Map<string, WebSocket>>(new Map())
  const healthChecks = ref<Map<string, NodeJS.Timeout>>(new Map())
  
  const createConnection = (pregnancyId: string) => {
    // Reuse existing connection if healthy
    const existing = connections.value.get(pregnancyId)
    if (existing && existing.readyState === WebSocket.OPEN) {
      return existing
    }
    
    // Create new connection
    const ws = useWebSocket(pregnancyId)
    ws.connect()
    connections.value.set(pregnancyId, ws.socket.value!)
    
    // Set up health check
    const healthCheck = setInterval(() => {
      if (ws.socket.value?.readyState === WebSocket.OPEN) {
        ws.socket.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
    
    healthChecks.value.set(pregnancyId, healthCheck)
    
    return ws.socket.value
  }
  
  const closeConnection = (pregnancyId: string) => {
    const connection = connections.value.get(pregnancyId)
    if (connection) {
      connection.close()
      connections.value.delete(pregnancyId)
    }
    
    const healthCheck = healthChecks.value.get(pregnancyId)
    if (healthCheck) {
      clearInterval(healthCheck)
      healthChecks.value.delete(pregnancyId)
    }
  }
  
  return { createConnection, closeConnection }
}
```

---

## 4. Database Optimization

### 4.1 Query Optimization

**Optimized Feed Queries**

```python
# backend/app/services/optimized_feed_service.py
from sqlmodel import select, func
from sqlalchemy.orm import selectinload, joinedload

class OptimizedFeedService:
    async def get_family_feed_optimized(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Post]:
        """Optimized feed query with minimal N+1 problems"""
        
        # Single query with strategic joins and eager loading
        query = (
            select(Post)
            .options(
                # Eagerly load related data to avoid N+1
                selectinload(Post.reactions),
                selectinload(Post.comments).selectinload(Comment.author),
                joinedload(Post.author),
                selectinload(Post.media),
            )
            .where(Post.pregnancy_id == pregnancy_id)
            .where(Post.status == PostStatus.PUBLISHED)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        # Execute query
        result = await session.exec(query)
        posts = result.unique().all()
        
        return posts
    
    async def get_feed_with_engagement_scores(
        self,
        session: Session,
        pregnancy_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get feed with pre-calculated engagement scores"""
        
        # Use CTE for engagement calculation
        engagement_cte = (
            select(
                Post.id.label('post_id'),
                func.count(Reaction.id).label('reaction_count'),
                func.count(Comment.id).label('comment_count'),
                (func.count(Reaction.id) * 2 + func.count(Comment.id) * 5).label('engagement_score')
            )
            .select_from(Post)
            .outerjoin(Reaction, Reaction.post_id == Post.id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .where(Post.pregnancy_id == pregnancy_id)
            .group_by(Post.id)
        ).cte('engagement')
        
        # Main query with engagement scores
        query = (
            select(
                Post,
                engagement_cte.c.reaction_count,
                engagement_cte.c.comment_count,
                engagement_cte.c.engagement_score
            )
            .select_from(Post)
            .join(engagement_cte, engagement_cte.c.post_id == Post.id)
            .options(
                selectinload(Post.reactions),
                selectinload(Post.media),
                joinedload(Post.author)
            )
            .order_by(engagement_cte.c.engagement_score.desc(), Post.created_at.desc())
            .limit(limit)
        )
        
        result = await session.exec(query)
        return result.all()
```

### 4.2 Strategic Indexing

**Database Index Creation**

```sql
-- backend/alembic/versions/add_performance_indexes.sql

-- Feed performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_pregnancy_created 
ON posts (pregnancy_id, created_at DESC) 
WHERE status = 'published';

-- Compound index for filtered feeds
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_pregnancy_type_created 
ON posts (pregnancy_id, type, created_at DESC) 
WHERE status = 'published';

-- Reaction aggregation index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reactions_post_type 
ON reactions (post_id, type);

-- Comment threading index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comments_post_parent 
ON comments (post_id, parent_id, created_at);

-- Family member access index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_family_members_pregnancy_user 
ON family_members (pregnancy_id, user_id, status) 
WHERE status = 'active';

-- Media loading index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_media_post_order 
ON media_items (post_id, order_index);

-- Engagement calculation indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_views_post_date 
ON post_views (post_id, viewed_at);

-- Trending posts index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_trending_score 
ON posts (pregnancy_id, family_warmth_score DESC, created_at DESC) 
WHERE status = 'published' AND created_at > NOW() - INTERVAL '7 days';

-- Weekly content index for story cards
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pregnancy_week_content 
ON posts (pregnancy_id, content->>'week', created_at DESC) 
WHERE content->>'week' IS NOT NULL;
```

### 4.3 Connection Pooling

**Enhanced Database Configuration**

```python
# backend/app/db/session.py - Enhanced connection pooling
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool

class DatabaseManager:
    def __init__(self, database_url: str):
        # Enhanced connection pool configuration
        self.engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,  # Core connections
            max_overflow=30,  # Additional connections
            pool_timeout=30,  # Connection timeout
            pool_recycle=3600,  # Recycle connections every hour
            pool_pre_ping=True,  # Validate connections
            # Performance optimizations
            echo=False,  # Disable SQL logging in production
            future=True,
            # Connection-specific settings
            connect_args={
                "server_settings": {
                    "jit": "off",  # Disable JIT for predictable performance
                    "application_name": "preggo-api",
                }
            }
        )
    
    async def get_session(self) -> AsyncSession:
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            try:
                yield session
            finally:
                await session.close()

# Optimized session dependency
async def get_optimized_session() -> AsyncSession:
    """Optimized database session with performance settings"""
    db_manager = DatabaseManager(settings.DATABASE_URL)
    async with db_manager.get_session() as session:
        # Set session-level optimizations
        await session.execute(text("SET statement_timeout = '30s'"))
        await session.execute(text("SET lock_timeout = '10s'"))
        await session.execute(text("SET idle_in_transaction_session_timeout = '60s'"))
        yield session
```

---

## 5. Frontend Performance

### 5.1 Virtual Scrolling Implementation

**Virtual Timeline Component**

```vue
<!-- components/feed/VirtualFeedTimeline.vue -->
<template>
  <div ref="container" class="virtual-timeline" @scroll="handleScroll">
    <!-- Visible area -->
    <div 
      class="timeline-content"
      :style="{ height: totalHeight + 'px', paddingTop: offsetY + 'px' }"
    >
      <!-- Rendered items -->
      <FeedPostCard
        v-for="(post, index) in visiblePosts"
        :key="post.id"
        :post="post"
        :style="{ height: itemHeight + 'px' }"
        :data-index="startIndex + index"
        @mounted="onItemMounted"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  posts: Post[]
  itemHeight?: number
  visibleCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  itemHeight: 200,
  visibleCount: 10
})

const container = ref<HTMLElement>()
const scrollTop = ref(0)
const containerHeight = ref(0)

// Virtual scrolling calculations
const startIndex = computed(() => Math.floor(scrollTop.value / props.itemHeight))
const endIndex = computed(() => 
  Math.min(
    startIndex.value + props.visibleCount + 2, // Buffer
    props.posts.length
  )
)

const visiblePosts = computed(() => 
  props.posts.slice(startIndex.value, endIndex.value)
)

const totalHeight = computed(() => props.posts.length * props.itemHeight)
const offsetY = computed(() => startIndex.value * props.itemHeight)

// Performance-optimized scroll handler
let ticking = false
const handleScroll = (event: Event) => {
  if (!ticking) {
    requestAnimationFrame(() => {
      const target = event.target as HTMLElement
      scrollTop.value = target.scrollTop
      ticking = false
    })
    ticking = true
  }
}

// Intersection Observer for precise item heights
const itemObserver = ref<IntersectionObserver>()
const itemHeights = ref<Map<number, number>>(new Map())

const onItemMounted = (index: number, height: number) => {
  itemHeights.value.set(index, height)
}

onMounted(() => {
  if (container.value) {
    containerHeight.value = container.value.clientHeight
    
    // Observe container size changes
    const resizeObserver = new ResizeObserver((entries) => {
      containerHeight.value = entries[0].contentRect.height
    })
    resizeObserver.observe(container.value)
  }
})
</script>
```

### 5.2 Progressive Loading

**Progressive Image Loading Component**

```vue
<!-- components/ui/ProgressiveImage.vue -->
<template>
  <div class="progressive-image" :class="{ loaded: imageLoaded }">
    <!-- Low quality placeholder -->
    <img
      v-if="placeholder"
      :src="placeholder"
      :alt="alt"
      class="placeholder"
      loading="eager"
    />
    
    <!-- Progressive image -->
    <img
      ref="imageRef"
      :src="currentSrc"
      :alt="alt"
      :loading="loading"
      class="main-image"
      @load="onLoad"
      @error="onError"
    />
    
    <!-- Loading state -->
    <div v-if="!imageLoaded" class="loading-overlay">
      <div class="spinner" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  src: string
  placeholder?: string
  alt: string
  loading?: 'lazy' | 'eager'
  sizes?: string
  srcset?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: 'lazy'
})

const imageRef = ref<HTMLImageElement>()
const imageLoaded = ref(false)
const imageError = ref(false)
const currentSrc = ref('')

// Progressive loading strategy
const loadImage = () => {
  // Start with low-quality version
  if (props.placeholder) {
    currentSrc.value = props.placeholder
  }
  
  // Load high-quality version
  const highQualityImage = new Image()
  
  highQualityImage.onload = () => {
    currentSrc.value = props.src
    imageLoaded.value = true
  }
  
  highQualityImage.onerror = () => {
    imageError.value = true
  }
  
  // Set srcset if provided
  if (props.srcset) {
    highQualityImage.srcset = props.srcset
  }
  if (props.sizes) {
    highQualityImage.sizes = props.sizes
  }
  
  highQualityImage.src = props.src
}

const onLoad = () => {
  imageLoaded.value = true
}

const onError = () => {
  imageError.value = true
}

// Intersection Observer for lazy loading
const observer = ref<IntersectionObserver>()

onMounted(() => {
  if (props.loading === 'lazy' && imageRef.value) {
    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            observer.value?.unobserve(entry.target)
          }
        })
      },
      { rootMargin: '50px' }
    )
    observer.value.observe(imageRef.value)
  } else {
    loadImage()
  }
})

onUnmounted(() => {
  observer.value?.disconnect()
})
</script>

<style scoped>
.progressive-image {
  position: relative;
  overflow: hidden;
}

.placeholder {
  position: absolute;
  inset: 0;
  filter: blur(5px);
  transform: scale(1.1);
  transition: opacity 0.3s ease;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.loaded .main-image {
  opacity: 1;
}

.loaded .placeholder {
  opacity: 0;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg) }
}
</style>
```

### 5.3 Code Splitting

**Route-based Code Splitting**

```typescript
// nuxt.config.ts - Enhanced performance configuration
export default defineNuxtConfig({
  // Code splitting optimization
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            // Feed-specific chunk
            'feed': [
              '~/components/feed/FeedTimeline.vue',
              '~/components/feed/FeedPostCard.vue',
              '~/stores/feed.ts'
            ],
            // Pregnancy content chunk
            'pregnancy': [
              '~/components/pregnancy/BabyDevelopmentCard.vue',
              '~/stores/pregnancy.ts'
            ],
            // Family management chunk
            'family': [
              '~/components/family/FamilyMember.vue',
              '~/stores/family.ts'
            ],
            // UI components chunk
            'ui': [
              '~/components/ui/BaseCard.vue',
              '~/components/ui/BaseButton.vue'
            ]
          }
        }
      }
    },
    ssr: {
      noExternal: ['@vueuse/core'] // Prevent SSR issues
    }
  },
  
  // Route-based splitting
  router: {
    options: {
      scrollBehaviorType: 'smooth'
    }
  },
  
  // Performance optimizations
  nitro: {
    compressPublicAssets: true,
    minify: true
  },
  
  // Image optimization
  image: {
    domains: ['supabase.co'],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      '2xl': 1536
    },
    formats: ['webp', 'avif', 'jpeg'],
    quality: 85
  }
})
```

**Dynamic Import Strategy**

```typescript
// composables/useDynamicImports.ts
export const useDynamicImports = () => {
  const loadedComponents = ref<Map<string, any>>(new Map())
  
  const loadComponent = async (componentName: string) => {
    if (loadedComponents.value.has(componentName)) {
      return loadedComponents.value.get(componentName)
    }
    
    let component
    
    try {
      switch (componentName) {
        case 'FeedPostCard':
          component = await import('~/components/feed/FeedPostCard.vue')
          break
        case 'BabyDevelopmentCard':
          component = await import('~/components/pregnancy/BabyDevelopmentCard.vue')
          break
        case 'FamilyWarmth':
          component = await import('~/components/feed/FamilyWarmth.vue')
          break
        default:
          throw new Error(`Unknown component: ${componentName}`)
      }
      
      loadedComponents.value.set(componentName, component.default)
      return component.default
    } catch (error) {
      console.error(`Failed to load component ${componentName}:`, error)
      return null
    }
  }
  
  const preloadComponents = async (componentNames: string[]) => {
    await Promise.all(componentNames.map(name => loadComponent(name)))
  }
  
  return { loadComponent, preloadComponents }
}
```

---

## 6. CDN & Asset Optimization

### 6.1 Image Optimization Pipeline

**Automatic Image Processing**

```python
# backend/app/services/image_optimization_service.py
from PIL import Image, ImageOps
import io
import asyncio
from typing import Tuple, List

class ImageOptimizationService:
    def __init__(self):
        self.SIZES = [
            (150, 150),  # Thumbnail
            (400, 400),  # Small
            (800, 800),  # Medium
            (1200, 1200),  # Large
        ]
        self.FORMATS = ['webp', 'avif', 'jpeg']
        self.QUALITY = 85
    
    async def process_uploaded_image(
        self, 
        image_data: bytes, 
        filename: str
    ) -> List[Dict[str, Any]]:
        """Process uploaded image into multiple formats and sizes"""
        
        # Open and orient image
        image = Image.open(io.BytesIO(image_data))
        image = ImageOps.exif_transpose(image)  # Fix orientation
        
        # Generate variants
        variants = []
        
        for size in self.SIZES:
            # Resize maintaining aspect ratio
            resized = image.copy()
            resized.thumbnail(size, Image.LANCZOS)
            
            for format_type in self.FORMATS:
                optimized_data = await self._optimize_image(resized, format_type)
                
                # Generate filename
                size_name = f"{size[0]}x{size[1]}"
                variant_filename = f"{filename}_{size_name}.{format_type}"
                
                variants.append({
                    'filename': variant_filename,
                    'data': optimized_data,
                    'format': format_type,
                    'width': resized.width,
                    'height': resized.height,
                    'size_bytes': len(optimized_data)
                })
        
        return variants
    
    async def _optimize_image(self, image: Image.Image, format_type: str) -> bytes:
        """Optimize image for specific format"""
        output = io.BytesIO()
        
        if format_type == 'webp':
            image.save(output, 'WEBP', quality=self.QUALITY, optimize=True)
        elif format_type == 'avif':
            image.save(output, 'AVIF', quality=self.QUALITY)
        elif format_type == 'jpeg':
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(output, 'JPEG', quality=self.QUALITY, optimize=True)
        
        return output.getvalue()
    
    def generate_srcset(self, base_url: str, filename_base: str) -> dict:
        """Generate responsive srcset for different formats"""
        return {
            'webp': self._build_srcset(base_url, filename_base, 'webp'),
            'avif': self._build_srcset(base_url, filename_base, 'avif'),
            'jpeg': self._build_srcset(base_url, filename_base, 'jpeg')
        }
    
    def _build_srcset(self, base_url: str, filename_base: str, format_type: str) -> str:
        """Build srcset string for a format"""
        srcset_parts = []
        for width, height in self.SIZES:
            url = f"{base_url}/{filename_base}_{width}x{height}.{format_type}"
            srcset_parts.append(f"{url} {width}w")
        return ", ".join(srcset_parts)

image_optimizer = ImageOptimizationService()
```

### 6.2 Lazy Loading Strategy

**Advanced Lazy Loading with Intersection Observer**

```typescript
// composables/useAdvancedLazyLoading.ts
export const useAdvancedLazyLoading = () => {
  const observers = ref<Map<string, IntersectionObserver>>(new Map())
  const loadedImages = ref<Set<string>>(new Set())
  
  const createObserver = (
    rootMargin = '50px',
    threshold = 0.1
  ): IntersectionObserver => {
    return new IntersectionObserver((entries) => {
      entries.forEach(async (entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          const src = img.dataset.src
          
          if (src && !loadedImages.value.has(src)) {
            await loadImageWithFallback(img, src)
            loadedImages.value.add(src)
          }
          
          // Unobserve after loading
          entry.target.classList.remove('lazy')
          observers.value.get('default')?.unobserve(entry.target)
        }
      })
    }, { rootMargin, threshold })
  }
  
  const loadImageWithFallback = async (
    img: HTMLImageElement, 
    src: string
  ): Promise<void> => {
    return new Promise((resolve) => {
      const image = new Image()
      
      image.onload = () => {
        img.src = src
        img.classList.add('loaded')
        resolve()
      }
      
      image.onerror = () => {
        // Try fallback format
        const fallbackSrc = src.replace('.webp', '.jpeg').replace('.avif', '.jpeg')
        if (fallbackSrc !== src) {
          const fallbackImage = new Image()
          fallbackImage.onload = () => {
            img.src = fallbackSrc
            img.classList.add('loaded')
            resolve()
          }
          fallbackImage.onerror = () => {
            // Use placeholder
            img.src = '/images/placeholder.svg'
            img.classList.add('error')
            resolve()
          }
          fallbackImage.src = fallbackSrc
        } else {
          img.src = '/images/placeholder.svg'
          img.classList.add('error')
          resolve()
        }
      }
      
      image.src = src
    })
  }
  
  const observeImage = (element: HTMLImageElement, observerKey = 'default') => {
    if (!observers.value.has(observerKey)) {
      observers.value.set(observerKey, createObserver())
    }
    
    observers.value.get(observerKey)?.observe(element)
  }
  
  const unobserveAll = () => {
    observers.value.forEach(observer => observer.disconnect())
    observers.value.clear()
  }
  
  return { observeImage, unobserveAll, loadedImages }
}
```

### 6.3 Prefetching Strategy

**Intelligent Content Prefetching**

```typescript
// composables/usePrefetching.ts
export const usePrefetching = () => {
  const prefetchQueue = ref<Set<string>>(new Set())
  const prefetchedData = ref<Map<string, any>>(new Map())
  
  const prefetchFeedContent = async (pregnancyId: string, page = 2) => {
    const cacheKey = `feed-${pregnancyId}-${page}`
    
    if (prefetchQueue.value.has(cacheKey) || prefetchedData.value.has(cacheKey)) {
      return
    }
    
    prefetchQueue.value.add(cacheKey)
    
    try {
      // Prefetch next page of feed content
      const api = useApi()
      const response = await api.getFamilyFeed(pregnancyId, {
        limit: 20,
        offset: (page - 1) * 20
      })
      
      if (response.data) {
        prefetchedData.value.set(cacheKey, response.data)
        
        // Prefetch images for the posts
        await prefetchPostImages(response.data.posts)
      }
    } catch (error) {
      console.error('Prefetch failed:', error)
    } finally {
      prefetchQueue.value.delete(cacheKey)
    }
  }
  
  const prefetchPostImages = async (posts: Post[]) => {
    const imageUrls: string[] = []
    
    posts.forEach(post => {
      post.media?.forEach(media => {
        if (media.type === 'image' && media.thumbnailUrl) {
          imageUrls.push(media.thumbnailUrl)
        }
      })
    })
    
    // Limit concurrent prefetches
    const chunks = chunkArray(imageUrls, 3)
    for (const chunk of chunks) {
      await Promise.all(chunk.map(url => prefetchImage(url)))
      // Small delay between chunks to avoid overwhelming
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
  
  const prefetchImage = (url: string): Promise<void> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => resolve()
      img.onerror = () => resolve() // Don't fail on image errors
      img.src = url
    })
  }
  
  const getPrefetchedData = (cacheKey: string) => {
    return prefetchedData.value.get(cacheKey)
  }
  
  const chunkArray = <T>(array: T[], size: number): T[][] => {
    const chunks: T[][] = []
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size))
    }
    return chunks
  }
  
  return { 
    prefetchFeedContent, 
    prefetchPostImages, 
    getPrefetchedData 
  }
}
```

---

## 7. Monitoring & Analytics

### 7.1 Performance Metrics

**Comprehensive Performance Monitoring**

```typescript
// composables/usePerformanceMonitoring.ts
export const usePerformanceMonitoring = () => {
  const metrics = ref<PerformanceMetric[]>([])
  const thresholds = {
    feedLoadTime: 200,
    imageLoadTime: 1000,
    apiResponseTime: 300,
    timeToInteractive: 500
  }
  
  const recordMetric = (name: string, value: number, metadata?: any) => {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      metadata,
      isWarning: value > getThreshold(name),
      isCritical: value > getThreshold(name) * 2
    }
    
    metrics.value.push(metric)
    
    // Send to analytics if critical
    if (metric.isCritical) {
      sendPerformanceAlert(metric)
    }
    
    // Limit stored metrics
    if (metrics.value.length > 100) {
      metrics.value = metrics.value.slice(-100)
    }
  }
  
  const measureFeedLoadTime = async (pregnancyId: string) => {
    const startTime = performance.now()
    
    try {
      const feedStore = useFeedStore()
      await feedStore.fetchFeed(pregnancyId)
      
      const loadTime = performance.now() - startTime
      recordMetric('feedLoadTime', loadTime, { pregnancyId })
      
      return loadTime
    } catch (error) {
      const errorTime = performance.now() - startTime
      recordMetric('feedLoadError', errorTime, { pregnancyId, error: error.message })
      throw error
    }
  }
  
  const measureImageLoadTime = (imageUrl: string): Promise<number> => {
    return new Promise((resolve) => {
      const startTime = performance.now()
      const img = new Image()
      
      const finishMeasurement = () => {
        const loadTime = performance.now() - startTime
        recordMetric('imageLoadTime', loadTime, { imageUrl })
        resolve(loadTime)
      }
      
      img.onload = finishMeasurement
      img.onerror = finishMeasurement
      img.src = imageUrl
    })
  }
  
  const measureApiCall = async <T>(
    apiCall: () => Promise<T>,
    endpoint: string
  ): Promise<T> => {
    const startTime = performance.now()
    
    try {
      const result = await apiCall()
      const responseTime = performance.now() - startTime
      
      recordMetric('apiResponseTime', responseTime, { endpoint, success: true })
      return result
    } catch (error) {
      const errorTime = performance.now() - startTime
      recordMetric('apiResponseTime', errorTime, { 
        endpoint, 
        success: false, 
        error: error.message 
      })
      throw error
    }
  }
  
  const getThreshold = (metricName: string): number => {
    return thresholds[metricName as keyof typeof thresholds] || 1000
  }
  
  const sendPerformanceAlert = async (metric: PerformanceMetric) => {
    try {
      await fetch('/api/v1/analytics/performance-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric,
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('Failed to send performance alert:', error)
    }
  }
  
  const getMetricsSummary = () => {
    const summary = {
      totalMetrics: metrics.value.length,
      warnings: metrics.value.filter(m => m.isWarning).length,
      criticals: metrics.value.filter(m => m.isCritical).length,
      averageLoadTime: 0,
      slowestOperation: null as PerformanceMetric | null
    }
    
    if (metrics.value.length > 0) {
      summary.averageLoadTime = metrics.value.reduce((sum, m) => sum + m.value, 0) / metrics.value.length
      summary.slowestOperation = metrics.value.reduce((slowest, current) => 
        current.value > (slowest?.value || 0) ? current : slowest
      )
    }
    
    return summary
  }
  
  return {
    recordMetric,
    measureFeedLoadTime,
    measureImageLoadTime,
    measureApiCall,
    getMetricsSummary,
    metrics: readonly(metrics)
  }
}

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
  metadata?: any
  isWarning: boolean
  isCritical: boolean
}
```

### 7.2 Error Tracking

**Comprehensive Error Monitoring**

```python
# backend/app/monitoring/error_tracker.py
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import json

class ErrorTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_counts = {}
        self.critical_errors = []
    
    async def track_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: str = "error",
        user_id: Optional[str] = None
    ):
        """Track and log application errors"""
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "severity": severity,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT
        }
        
        # Count error occurrences
        error_key = f"{error_data['error_type']}:{error_data['context'].get('endpoint', 'unknown')}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log based on severity
        if severity == "critical":
            self.logger.critical(json.dumps(error_data))
            self.critical_errors.append(error_data)
            await self._send_alert(error_data)
        elif severity == "error":
            self.logger.error(json.dumps(error_data))
        else:
            self.logger.warning(json.dumps(error_data))
        
        # Store in database for analysis
        await self._store_error(error_data)
    
    async def track_performance_issue(
        self,
        operation: str,
        duration: float,
        threshold: float,
        context: Dict[str, Any]
    ):
        """Track performance issues"""
        
        if duration > threshold:
            severity = "critical" if duration > threshold * 2 else "warning"
            
            perf_data = {
                "type": "performance_issue",
                "operation": operation,
                "duration_ms": duration,
                "threshold_ms": threshold,
                "severity": severity,
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.warning(json.dumps(perf_data))
            
            if severity == "critical":
                await self._send_alert(perf_data)
    
    async def _send_alert(self, error_data: Dict[str, Any]):
        """Send alert for critical errors"""
        # Implement alerting logic (Slack, email, etc.)
        pass
    
    async def _store_error(self, error_data: Dict[str, Any]):
        """Store error in database for analysis"""
        # Implement database storage
        pass
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring dashboard"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "unique_error_types": len(self.error_counts),
            "critical_errors": len(self.critical_errors),
            "most_common_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

error_tracker = ErrorTracker()
```

### 7.3 User Engagement Analytics

**Feed Engagement Tracking**

```typescript
// composables/useEngagementAnalytics.ts
export const useEngagementAnalytics = () => {
  const sessionData = ref({
    startTime: Date.now(),
    interactions: [] as EngagementEvent[],
    viewedPosts: new Set<string>(),
    scrollDepth: 0,
    timeSpentOnPosts: new Map<string, number>()
  })
  
  const trackPostView = (postId: string, metadata?: any) => {
    if (!sessionData.value.viewedPosts.has(postId)) {
      sessionData.value.viewedPosts.add(postId)
      
      const event: EngagementEvent = {
        type: 'post_view',
        postId,
        timestamp: Date.now(),
        metadata
      }
      
      sessionData.value.interactions.push(event)
      
      // Start timing for this post
      sessionData.value.timeSpentOnPosts.set(postId, Date.now())
    }
  }
  
  const trackPostInteraction = (
    type: 'reaction' | 'comment' | 'share',
    postId: string,
    metadata?: any
  ) => {
    const event: EngagementEvent = {
      type: `post_${type}`,
      postId,
      timestamp: Date.now(),
      metadata
    }
    
    sessionData.value.interactions.push(event)
    
    // Send high-value interactions immediately
    if (['reaction', 'comment', 'share'].includes(type)) {
      sendEngagementEvent(event)
    }
  }
  
  const trackScrollDepth = (depth: number) => {
    if (depth > sessionData.value.scrollDepth) {
      sessionData.value.scrollDepth = depth
    }
  }
  
  const trackPostReadTime = (postId: string) => {
    const startTime = sessionData.value.timeSpentOnPosts.get(postId)
    if (startTime) {
      const readTime = Date.now() - startTime
      
      const event: EngagementEvent = {
        type: 'post_read_time',
        postId,
        timestamp: Date.now(),
        metadata: { readTime }
      }
      
      sessionData.value.interactions.push(event)
    }
  }
  
  const sendEngagementEvent = async (event: EngagementEvent) => {
    try {
      await fetch('/api/v1/analytics/engagement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event,
          sessionId: getSessionId(),
          userAgent: navigator.userAgent,
          timestamp: Date.now()
        })
      })
    } catch (error) {
      console.error('Failed to send engagement event:', error)
    }
  }
  
  const getSessionSummary = () => {
    const sessionDuration = Date.now() - sessionData.value.startTime
    
    return {
      sessionDuration,
      totalInteractions: sessionData.value.interactions.length,
      uniquePostsViewed: sessionData.value.viewedPosts.size,
      maxScrollDepth: sessionData.value.scrollDepth,
      interactionTypes: countInteractionTypes(),
      avgTimePerPost: calculateAvgTimePerPost()
    }
  }
  
  const countInteractionTypes = () => {
    return sessionData.value.interactions.reduce((counts, event) => {
      counts[event.type] = (counts[event.type] || 0) + 1
      return counts
    }, {} as Record<string, number>)
  }
  
  const calculateAvgTimePerPost = () => {
    const readTimes = sessionData.value.interactions
      .filter(e => e.type === 'post_read_time')
      .map(e => e.metadata?.readTime || 0)
    
    return readTimes.length > 0 
      ? readTimes.reduce((sum, time) => sum + time, 0) / readTimes.length
      : 0
  }
  
  const getSessionId = () => {
    let sessionId = sessionStorage.getItem('analytics-session-id')
    if (!sessionId) {
      sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('analytics-session-id', sessionId)
    }
    return sessionId
  }
  
  // Send session summary on page unload
  onBeforeUnmount(() => {
    const summary = getSessionSummary()
    navigator.sendBeacon('/api/v1/analytics/session-summary', JSON.stringify(summary))
  })
  
  return {
    trackPostView,
    trackPostInteraction,
    trackScrollDepth,
    trackPostReadTime,
    getSessionSummary
  }
}

interface EngagementEvent {
  type: string
  postId: string
  timestamp: number
  metadata?: any
}
```

---

## 8. Scaling Strategy

### 8.1 Horizontal Scaling

**Load Balancer Configuration (Nginx)**

```nginx
# nginx/load-balancer.conf
upstream preggo_backend {
    least_conn;
    server backend-1:8000 weight=3 max_fails=3 fail_timeout=30s;
    server backend-2:8000 weight=3 max_fails=3 fail_timeout=30s;
    server backend-3:8000 weight=2 max_fails=3 fail_timeout=30s;  # Smaller instance
    
    # Health checks
    keepalive 32;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

upstream preggo_websocket {
    ip_hash;  # Sticky sessions for WebSocket
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 80;
    server_name api.preggo.app;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=feed:10m rate=30r/s;  # Higher limit for feed
    
    # API routes
    location /api/v1/feed/ {
        limit_req zone=feed burst=20 nodelay;
        proxy_pass http://preggo_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Caching for feed endpoints
        proxy_cache feed_cache;
        proxy_cache_valid 200 2m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        add_header X-Cache-Status $upstream_cache_status;
    }
    
    # WebSocket routes
    location /ws/ {
        proxy_pass http://preggo_websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
    
    # Other API routes
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://preggo_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Cache configuration
proxy_cache_path /var/cache/nginx/feed levels=1:2 keys_zone=feed_cache:10m max_size=100m inactive=60m;
```

### 8.2 Database Sharding

**Pregnancy-based Sharding Strategy**

```python
# backend/app/db/sharding.py
from typing import List, Dict, Any
import hashlib
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

class ShardManager:
    def __init__(self, shard_configs: List[Dict[str, str]]):
        self.shards = {}
        self.shard_count = len(shard_configs)
        
        for i, config in enumerate(shard_configs):
            engine = create_async_engine(
                config["database_url"],
                pool_size=10,
                max_overflow=15,
                pool_recycle=3600
            )
            self.shards[f"shard_{i}"] = engine
    
    def get_shard_for_pregnancy(self, pregnancy_id: str) -> AsyncEngine:
        """Determine which shard to use for a pregnancy"""
        # Use consistent hashing based on pregnancy ID
        hash_value = int(hashlib.md5(pregnancy_id.encode()).hexdigest(), 16)
        shard_index = hash_value % self.shard_count
        return self.shards[f"shard_{shard_index}"]
    
    def get_shard_for_user(self, user_id: str) -> AsyncEngine:
        """Determine shard for user-specific queries"""
        # For user queries, we might need to query multiple shards
        # or use a separate user mapping table
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        shard_index = hash_value % self.shard_count
        return self.shards[f"shard_{shard_index}"]
    
    async def execute_on_all_shards(self, query_func):
        """Execute a query on all shards (for cross-shard operations)"""
        results = []
        for shard_name, engine in self.shards.items():
            try:
                result = await query_func(engine)
                results.append(result)
            except Exception as e:
                logger.error(f"Query failed on {shard_name}: {e}")
        return results

# Enhanced feed service with sharding
class ShardedFeedService:
    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager
    
    async def get_family_feed_sharded(
        self,
        user_id: str,
        pregnancy_id: str,
        request: FeedRequest
    ) -> FeedResponse:
        """Get family feed from appropriate shard"""
        
        # Get the shard for this pregnancy
        shard_engine = self.shard_manager.get_shard_for_pregnancy(pregnancy_id)
        
        # Create session for this shard
        async with AsyncSession(shard_engine) as session:
            # Execute feed query on the correct shard
            posts = await self._get_posts_for_pregnancy(
                session, pregnancy_id, request
            )
            
            return FeedResponse(
                posts=posts,
                total_count=len(posts),
                has_more=len(posts) == request.limit
            )
    
    async def get_user_cross_shard_feed(
        self,
        user_id: str
    ) -> List[Post]:
        """Get posts across all pregnancies user has access to (cross-shard)"""
        
        # First, get user's pregnancy memberships
        user_pregnancies = await self._get_user_pregnancies(user_id)
        
        # Group pregnancies by shard
        pregnancy_by_shard = {}
        for pregnancy_id in user_pregnancies:
            shard_engine = self.shard_manager.get_shard_for_pregnancy(pregnancy_id)
            shard_key = id(shard_engine)
            if shard_key not in pregnancy_by_shard:
                pregnancy_by_shard[shard_key] = {"engine": shard_engine, "pregnancies": []}
            pregnancy_by_shard[shard_key]["pregnancies"].append(pregnancy_id)
        
        # Query each shard
        all_posts = []
        for shard_data in pregnancy_by_shard.values():
            async with AsyncSession(shard_data["engine"]) as session:
                shard_posts = await self._get_posts_for_pregnancies(
                    session, shard_data["pregnancies"]
                )
                all_posts.extend(shard_posts)
        
        # Sort and limit results
        all_posts.sort(key=lambda p: p.created_at, reverse=True)
        return all_posts[:50]  # Limit cross-shard results
```

### 8.3 Caching Scalability

**Redis Cluster Configuration**

```python
# backend/app/cache/redis_cluster.py
import redis.cluster
from typing import Dict, Any, Optional, List
import json
import asyncio

class RedisClusterManager:
    def __init__(self, cluster_nodes: List[Dict[str, Any]]):
        # Redis Cluster setup for horizontal scaling
        self.cluster = redis.cluster.RedisCluster(
            startup_nodes=cluster_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            health_check_interval=30,
            retry_on_timeout=True
        )
        
        # Cache configuration by data type
        self.cache_configs = {
            "feed": {"ttl": 300, "prefix": "feed:"},      # 5 minutes
            "posts": {"ttl": 600, "prefix": "post:"},     # 10 minutes
            "users": {"ttl": 1800, "prefix": "user:"},    # 30 minutes
            "pregnancy": {"ttl": 3600, "prefix": "preg:"} # 1 hour
        }
    
    async def get_feed_cache(
        self,
        pregnancy_id: str,
        user_id: str,
        cache_key_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached feed data with intelligent key generation"""
        
        # Generate consistent cache key
        key_parts = [
            pregnancy_id,
            user_id,
            cache_key_params.get("filter_type", "all"),
            cache_key_params.get("sort_by", "recent"),
            str(cache_key_params.get("limit", 20)),
            str(cache_key_params.get("offset", 0))
        ]
        
        cache_key = f"feed:{'::'.join(key_parts)}"
        
        try:
            cached_data = await asyncio.to_thread(self.cluster.get, cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache read error for key {cache_key}: {e}")
        
        return None
    
    async def set_feed_cache(
        self,
        pregnancy_id: str,
        user_id: str,
        cache_key_params: Dict[str, Any],
        data: Dict[str, Any],
        ttl_override: Optional[int] = None
    ) -> bool:
        """Set feed cache with automatic expiration"""
        
        key_parts = [
            pregnancy_id,
            user_id,
            cache_key_params.get("filter_type", "all"),
            cache_key_params.get("sort_by", "recent"),
            str(cache_key_params.get("limit", 20)),
            str(cache_key_params.get("offset", 0))
        ]
        
        cache_key = f"feed:{'::'.join(key_parts)}"
        ttl = ttl_override or self.cache_configs["feed"]["ttl"]
        
        try:
            # Add cache metadata
            cache_data = {
                "data": data,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "version": "1.0"
            }
            
            await asyncio.to_thread(
                self.cluster.setex,
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )
            return True
            
        except Exception as e:
            logger.error(f"Cache write error for key {cache_key}: {e}")
            return False
    
    async def invalidate_pregnancy_caches(self, pregnancy_id: str) -> int:
        """Invalidate all caches related to a pregnancy"""
        
        patterns = [
            f"feed::{pregnancy_id}::*",
            f"post::{pregnancy_id}::*",
            f"celebration::{pregnancy_id}::*"
        ]
        
        total_deleted = 0
        
        for pattern in patterns:
            try:
                # Scan for keys matching pattern
                keys = []
                for key in self.cluster.scan_iter(match=pattern):
                    keys.append(key)
                
                # Delete in batches
                if keys:
                    batch_size = 100
                    for i in range(0, len(keys), batch_size):
                        batch = keys[i:i + batch_size]
                        deleted = await asyncio.to_thread(self.cluster.delete, *batch)
                        total_deleted += deleted
                        
            except Exception as e:
                logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
        
        return total_deleted
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache cluster statistics"""
        try:
            info = await asyncio.to_thread(self.cluster.info)
            return {
                "connected_nodes": len(self.cluster.get_nodes()),
                "total_memory_used": sum(
                    int(node_info.get("used_memory", 0)) 
                    for node_info in info.values()
                ),
                "total_keys": sum(
                    int(node_info.get("db0", {}).get("keys", 0))
                    for node_info in info.values()
                ),
                "hit_ratio": self._calculate_hit_ratio(info)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def _calculate_hit_ratio(self, cluster_info: Dict[str, Any]) -> float:
        """Calculate overall cache hit ratio across cluster"""
        total_hits = sum(
            int(node_info.get("keyspace_hits", 0))
            for node_info in cluster_info.values()
        )
        total_misses = sum(
            int(node_info.get("keyspace_misses", 0))
            for node_info in cluster_info.values()
        )
        
        if total_hits + total_misses > 0:
            return total_hits / (total_hits + total_misses)
        return 0.0

# Initialize cluster manager
redis_cluster = RedisClusterManager([
    {"host": "redis-node-1", "port": 7000},
    {"host": "redis-node-2", "port": 7001},
    {"host": "redis-node-3", "port": 7002},
])
```

---

## 9. Offline Support

### 9.1 Service Worker Implementation

**Comprehensive Offline Strategy**

```javascript
// frontend/public/sw.js
const CACHE_VERSION = 'preggo-v1.2.0'
const STATIC_CACHE = `${CACHE_VERSION}-static`
const API_CACHE = `${CACHE_VERSION}-api`
const IMAGE_CACHE = `${CACHE_VERSION}-images`

// Cache strategies by resource type
const CACHE_STRATEGIES = {
  static: 'cache-first',
  api: 'network-first', 
  images: 'cache-first',
  feed: 'stale-while-revalidate'
}

// Resources to cache immediately
const STATIC_RESOURCES = [
  '/',
  '/offline',
  '/manifest.json',
  '/css/animations.css',
  '/js/app.js'
]

// Install event - cache static resources
self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => 
        cache.addAll(STATIC_RESOURCES)
      ),
      caches.open(API_CACHE),
      caches.open(IMAGE_CACHE)
    ]).then(() => {
      console.log('Service worker installed and caches initialized')
      return self.skipWaiting()
    })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => !cacheName.startsWith(CACHE_VERSION))
          .map(cacheName => caches.delete(cacheName))
      )
    }).then(() => {
      console.log('Service worker activated and old caches cleaned')
      return self.clients.claim()
    })
  )
})

// Fetch event - handle requests based on strategy
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(event.request))
  }
  // Handle image requests
  else if (isImageRequest(event.request)) {
    event.respondWith(handleImageRequest(event.request))
  }
  // Handle static resources
  else {
    event.respondWith(handleStaticRequest(event.request))
  }
})

// API request handler with offline support
async function handleApiRequest(request) {
  const url = new URL(request.url)
  const cacheName = API_CACHE
  
  // Feed endpoints use stale-while-revalidate
  if (url.pathname.includes('/feed/')) {
    return staleWhileRevalidate(request, cacheName)
  }
  
  // Other API endpoints use network-first
  return networkFirst(request, cacheName)
}

// Network-first strategy
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request.clone())
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('Network request failed, trying cache:', error)
    
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline fallback
    return createOfflineResponse(request)
  }
}

// Stale-while-revalidate strategy for feed
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cachedResponse = await cache.match(request)
  
  // Revalidate in background
  const networkPromise = fetch(request.clone()).then(response => {
    if (response.ok) {
      cache.put(request, response.clone())
    }
    return response
  }).catch(error => {
    console.log('Background revalidation failed:', error)
  })
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse
  }
  
  // Wait for network if no cache
  try {
    return await networkPromise
  } catch (error) {
    return createOfflineResponse(request)
  }
}

// Image request handler
async function handleImageRequest(request) {
  const cache = await caches.open(IMAGE_CACHE)
  const cachedImage = await cache.match(request)
  
  if (cachedImage) {
    return cachedImage
  }
  
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    // Return placeholder image
    return caches.match('/images/placeholder.svg')
  }
}

// Static request handler
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request)
  
  if (cachedResponse) {
    return cachedResponse
  }
  
  try {
    const networkResponse = await fetch(request)
    const cache = await caches.open(STATIC_CACHE)
    cache.put(request, networkResponse.clone())
    return networkResponse
  } catch (error) {
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline')
    }
    throw error
  }
}

// Create offline response
function createOfflineResponse(request) {
  const url = new URL(request.url)
  
  if (url.pathname.includes('/api/v1/feed/')) {
    return new Response(JSON.stringify({
      offline: true,
      posts: [],
      message: 'You are offline. Showing cached content.'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
  
  return new Response('You are offline', { status: 503 })
}

// Utility functions
function isImageRequest(request) {
  return request.destination === 'image' || 
         /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(new URL(request.url).pathname)
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-posts') {
    event.waitUntil(syncOfflinePosts())
  } else if (event.tag === 'sync-reactions') {
    event.waitUntil(syncOfflineReactions())
  }
})

// Sync offline posts when back online
async function syncOfflinePosts() {
  const offlinePosts = await getStoredOfflineData('offline-posts')
  
  for (const post of offlinePosts) {
    try {
      await fetch('/api/v1/posts/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(post.data)
      })
      
      // Remove from offline storage on success
      await removeOfflineData('offline-posts', post.id)
      
    } catch (error) {
      console.log('Failed to sync post:', error)
      // Keep in offline storage for next sync
    }
  }
}

// Sync offline reactions when back online
async function syncOfflineReactions() {
  const offlineReactions = await getStoredOfflineData('offline-reactions')
  
  for (const reaction of offlineReactions) {
    try {
      await fetch('/api/v1/feed/reactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reaction.data)
      })
      
      await removeOfflineData('offline-reactions', reaction.id)
      
    } catch (error) {
      console.log('Failed to sync reaction:', error)
    }
  }
}

// IndexedDB helpers for offline data
async function getStoredOfflineData(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('preggo-offline', 1)
    
    request.onsuccess = event => {
      const db = event.target.result
      const transaction = db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const getAllRequest = store.getAll()
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result)
      getAllRequest.onerror = () => reject(getAllRequest.error)
    }
    
    request.onerror = () => reject(request.error)
  })
}

async function removeOfflineData(storeName, id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('preggo-offline', 1)
    
    request.onsuccess = event => {
      const db = event.target.result
      const transaction = db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const deleteRequest = store.delete(id)
      
      deleteRequest.onsuccess = () => resolve()
      deleteRequest.onerror = () => reject(deleteRequest.error)
    }
  })
}
```

### 9.2 Offline Queue Management

**Offline Action Queue**

```typescript
// composables/useOfflineQueue.ts
export const useOfflineQueue = () => {
  const queue = ref<OfflineAction[]>([])
  const isOnline = ref(navigator.onLine)
  const syncInProgress = ref(false)
  
  // Listen for online/offline events
  onMounted(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    // Load pending actions from storage
    loadQueueFromStorage()
  })
  
  onUnmounted(() => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  })
  
  const addToQueue = async (action: OfflineAction) => {
    action.id = `offline-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    action.timestamp = Date.now()
    action.status = 'pending'
    
    queue.value.push(action)
    await saveQueueToStorage()
    
    // If online, try to sync immediately
    if (isOnline.value && !syncInProgress.value) {
      await syncQueue()
    }
  }
  
  const addPostToQueue = async (postData: CreatePostRequest) => {
    await addToQueue({
      type: 'create_post',
      data: postData,
      endpoint: '/api/v1/posts/',
      method: 'POST'
    })
  }
  
  const addReactionToQueue = async (postId: string, reactionType: string) => {
    await addToQueue({
      type: 'add_reaction',
      data: { post_id: postId, reaction_type: reactionType },
      endpoint: '/api/v1/feed/reactions',
      method: 'POST'
    })
  }
  
  const syncQueue = async () => {
    if (!isOnline.value || syncInProgress.value) return
    
    syncInProgress.value = true
    const pendingActions = queue.value.filter(action => action.status === 'pending')
    
    console.log(`Syncing ${pendingActions.length} offline actions`)
    
    for (const action of pendingActions) {
      try {
        const response = await fetch(action.endpoint, {
          method: action.method,
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${useAuth().session.value?.access_token}`
          },
          body: JSON.stringify(action.data)
        })
        
        if (response.ok) {
          action.status = 'completed'
          action.syncedAt = Date.now()
          
          // Handle successful sync
          await handleSuccessfulSync(action, await response.json())
        } else {
          action.status = 'failed'
          action.error = `HTTP ${response.status}: ${response.statusText}`
        }
      } catch (error) {
        action.status = 'failed'
        action.error = error.message
        console.error('Failed to sync action:', error)
      }
    }
    
    // Clean up completed actions
    queue.value = queue.value.filter(action => action.status !== 'completed')
    await saveQueueToStorage()
    
    syncInProgress.value = false
  }
  
  const handleSuccessfulSync = async (action: OfflineAction, response: any) => {
    switch (action.type) {
      case 'create_post':
        // Update optimistic post with real data
        const feedStore = useFeedStore()
        feedStore.replaceOptimisticPost(action.id!, response)
        break
        
      case 'add_reaction':
        // Update reaction counts
        feedStore.updateReactionCounts(action.data.post_id, response.updated_counts)
        break
    }
  }
  
  const handleOnline = async () => {
    isOnline.value = true
    console.log('Connection restored - syncing offline actions')
    
    // Register background sync if supported
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      const registration = await navigator.serviceWorker.ready
      await registration.sync.register('sync-offline-actions')
    } else {
      // Fallback to immediate sync
      await syncQueue()
    }
  }
  
  const handleOffline = () => {
    isOnline.value = false
    console.log('Connection lost - queuing actions for later sync')
  }
  
  const saveQueueToStorage = async () => {
    try {
      await localforage.setItem('offline-queue', queue.value)
    } catch (error) {
      console.error('Failed to save offline queue:', error)
    }
  }
  
  const loadQueueFromStorage = async () => {
    try {
      const stored = await localforage.getItem<OfflineAction[]>('offline-queue')
      if (stored) {
        queue.value = stored
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error)
    }
  }
  
  const clearQueue = async () => {
    queue.value = []
    await saveQueueToStorage()
  }
  
  const getQueueStats = () => {
    const total = queue.value.length
    const pending = queue.value.filter(a => a.status === 'pending').length
    const failed = queue.value.filter(a => a.status === 'failed').length
    
    return { total, pending, failed }
  }
  
  return {
    queue: readonly(queue),
    isOnline: readonly(isOnline),
    syncInProgress: readonly(syncInProgress),
    addPostToQueue,
    addReactionToQueue,
    syncQueue,
    clearQueue,
    getQueueStats
  }
}

interface OfflineAction {
  id?: string
  type: 'create_post' | 'add_reaction' | 'add_comment' | 'upload_media'
  data: any
  endpoint: string
  method: 'POST' | 'PUT' | 'DELETE'
  timestamp?: number
  status?: 'pending' | 'completed' | 'failed'
  error?: string
  syncedAt?: number
}
```

### 9.3 Sync Strategies

**Intelligent Sync Management**

```typescript
// composables/useSyncStrategies.ts
export const useSyncStrategies = () => {
  const syncQueue = ref<SyncItem[]>([])
  const syncStatus = ref<'idle' | 'syncing' | 'failed'>('idle')
  
  const SYNC_STRATEGIES = {
    immediate: ['reactions', 'views'],      // Sync immediately when online
    batched: ['comments', 'shares'],        // Batch sync every 30 seconds
    deferred: ['analytics', 'logs']         // Sync during idle time
  }
  
  const addToSyncQueue = (item: SyncItem) => {
    const strategy = getSyncStrategy(item.type)
    item.strategy = strategy
    item.priority = getSyncPriority(item.type)
    
    syncQueue.value.push(item)
    
    if (strategy === 'immediate' && navigator.onLine) {
      syncImmediate(item)
    }
  }
  
  const syncImmediate = async (item: SyncItem) => {
    try {
      await executeSyncItem(item)
      removeSyncItem(item.id)
    } catch (error) {
      item.retryCount = (item.retryCount || 0) + 1
      item.lastError = error.message
      
      if (item.retryCount >= 3) {
        item.status = 'failed'
      } else {
        // Exponential backoff retry
        setTimeout(() => syncImmediate(item), Math.pow(2, item.retryCount) * 1000)
      }
    }
  }
  
  const syncBatched = async () => {
    const batchedItems = syncQueue.value.filter(
      item => item.strategy === 'batched' && item.status === 'pending'
    )
    
    if (batchedItems.length === 0) return
    
    // Group by endpoint for efficient batching
    const groupedItems = batchedItems.reduce((groups, item) => {
      const key = `${item.endpoint}-${item.method}`
      if (!groups[key]) groups[key] = []
      groups[key].push(item)
      return groups
    }, {} as Record<string, SyncItem[]>)
    
    for (const [key, items] of Object.entries(groupedItems)) {
      try {
        await syncItemBatch(items)
        items.forEach(item => removeSyncItem(item.id))
      } catch (error) {
        items.forEach(item => {
          item.retryCount = (item.retryCount || 0) + 1
          item.lastError = error.message
          if (item.retryCount >= 3) {
            item.status = 'failed'
          }
        })
      }
    }
  }
  
  const syncDeferred = async () => {
    // Only sync during browser idle time
    if ('requestIdleCallback' in window) {
      requestIdleCallback(async () => {
        const deferredItems = syncQueue.value.filter(
          item => item.strategy === 'deferred' && item.status === 'pending'
        )
        
        for (const item of deferredItems.slice(0, 5)) { // Limit to 5 per idle period
          try {
            await executeSyncItem(item)
            removeSyncItem(item.id)
          } catch (error) {
            // Deferred items fail silently
            item.status = 'failed'
          }
        }
      })
    }
  }
  
  const executeSyncItem = async (item: SyncItem): Promise<any> => {
    const response = await fetch(item.endpoint, {
      method: item.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${useAuth().session.value?.access_token}`
      },
      body: item.data ? JSON.stringify(item.data) : undefined
    })
    
    if (!response.ok) {
      throw new Error(`Sync failed: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }
  
  const syncItemBatch = async (items: SyncItem[]): Promise<any> => {
    // Create batch request payload
    const batchPayload = {
      requests: items.map(item => ({
        id: item.id,
        method: item.method,
        endpoint: item.endpoint,
        data: item.data
      }))
    }
    
    const response = await fetch('/api/v1/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${useAuth().session.value?.access_token}`
      },
      body: JSON.stringify(batchPayload)
    })
    
    if (!response.ok) {
      throw new Error(`Batch sync failed: ${response.status}`)
    }
    
    return response.json()
  }
  
  const getSyncStrategy = (itemType: string): 'immediate' | 'batched' | 'deferred' => {
    for (const [strategy, types] of Object.entries(SYNC_STRATEGIES)) {
      if (types.includes(itemType)) {
        return strategy as any
      }
    }
    return 'batched' // Default strategy
  }
  
  const getSyncPriority = (itemType: string): number => {
    const priorities = {
      reactions: 10,
      comments: 8,
      views: 6,
      shares: 5,
      analytics: 2,
      logs: 1
    }
    return priorities[itemType as keyof typeof priorities] || 5
  }
  
  const removeSyncItem = (id: string) => {
    const index = syncQueue.value.findIndex(item => item.id === id)
    if (index > -1) {
      syncQueue.value.splice(index, 1)
    }
  }
  
  // Set up periodic syncing
  onMounted(() => {
    // Batched sync every 30 seconds
    setInterval(syncBatched, 30000)
    
    // Deferred sync every 2 minutes
    setInterval(syncDeferred, 120000)
    
    // Listen for online events
    window.addEventListener('online', () => {
      console.log('Back online - syncing pending items')
      syncBatched()
    })
  })
  
  return {
    addToSyncQueue,
    syncQueue: readonly(syncQueue),
    syncStatus: readonly(syncStatus)
  }
}

interface SyncItem {
  id: string
  type: string
  endpoint: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  strategy?: 'immediate' | 'batched' | 'deferred'
  priority?: number
  status?: 'pending' | 'completed' | 'failed'
  retryCount?: number
  lastError?: string
  createdAt: number
}
```

---

## Implementation Timeline & Monitoring

### Phase 1: Immediate Response (Week 1-2)
- Implement optimistic updates for reactions and comments
- Set up local state persistence
- Add rollback mechanisms
- Target: < 100ms perceived response for interactions

### Phase 2: Caching Layer (Week 3-4)
- Deploy Redis cluster for backend caching
- Implement browser-level caching with service workers
- Set up CDN integration
- Target: < 200ms for cached feed loads

### Phase 3: Real-time & Database (Week 5-6)
- Implement WebSocket connections for live updates
- Optimize database queries and add strategic indexes
- Set up connection pooling
- Target: < 300ms for fresh data loads

### Phase 4: Scaling & Offline (Week 7-8)
- Implement horizontal scaling with load balancing
- Add offline support with sync capabilities
- Complete monitoring and analytics implementation
- Target: < 200ms at scale, full offline functionality

### Success Metrics
- **Perceived Response Time**: < 200ms for 95% of user interactions
- **Actual Load Time**: < 500ms for feed data
- **Cache Hit Rate**: > 80% for frequently accessed content
- **Error Rate**: < 0.1% for critical operations
- **Offline Success Rate**: > 95% sync success when back online

This comprehensive implementation guide provides the technical foundation to achieve sub-200ms perceived response times while scaling to support high-engagement family sharing. The multi-layered approach ensures both immediate user satisfaction and robust system performance under load.