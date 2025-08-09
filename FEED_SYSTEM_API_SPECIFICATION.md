# Feed System API Technical Specification

## Executive Summary

This document provides comprehensive technical specifications for the enhanced feed system overhaul of the Preggo pregnancy tracking application. The system leverages the existing FastAPI backend with sophisticated endpoints for family feed, reactions, celebrations, and real-time engagement features.

## Table of Contents

1. [Enhanced API Endpoints](#enhanced-api-endpoints)
2. [Real-time Features](#real-time-features)
3. [Reaction System](#reaction-system)
4. [Comment Threading](#comment-threading)
5. [Feed Performance](#feed-performance)
6. [Data Models](#data-models)
7. [Authentication & Permissions](#authentication--permissions)
8. [Error Handling](#error-handling)
9. [API Examples](#api-examples)

---

## Enhanced API Endpoints

### 1. Family Feed Endpoint (Enhanced)

**Endpoint:** `GET /api/v1/feed/family/{pregnancy_id}`

**Current Implementation Enhanced:**
```python
@router.get("/family/{pregnancy_id}/enhanced", response_model=EnhancedFeedResponse)
async def get_enhanced_family_feed(
    pregnancy_id: str,
    response: Response,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter_type: FeedFilterType = Query(FeedFilterType.ALL),
    sort_by: FeedSortType = Query(FeedSortType.CHRONOLOGICAL),
    
    # Enhanced parameters
    real_time_updates: bool = Query(True, description="Include real-time update metadata"),
    include_warmth_scores: bool = Query(True, description="Include family warmth calculations"),
    include_memory_suggestions: bool = Query(True, description="Include memory book auto-curation"),
    include_celebration_triggers: bool = Query(True, description="Include celebration opportunities"),
    personalization_level: str = Query("standard", regex="^(minimal|standard|detailed)$"),
    
    # Real-time sync parameters
    last_sync_timestamp: Optional[str] = Query(None, description="Last client sync timestamp"),
    client_session_id: str = Query(..., description="Unique client session for real-time updates"),
    
    # Advanced filtering
    mood_filter: Optional[List[MoodType]] = Query(None, description="Filter by post moods"),
    author_filter: Optional[List[str]] = Query(None, description="Filter by specific authors"),
    engagement_threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum engagement score"),
    
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
```

**Enhanced Response Model:**
```python
class EnhancedFeedResponse(BaseModel):
    posts: List[EnrichedPost]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None
    
    # Real-time features
    real_time_metadata: RealTimeMetadata
    sync_token: str  # For optimistic updates
    feed_generation_time: datetime
    
    # Enhanced context
    pregnancy_context: PregnancyContextEnhanced
    family_warmth_summary: FamilyWarmthSummary
    celebration_opportunities: List[CelebrationOpportunity]
    memory_book_suggestions: List[MemoryBookSuggestion]
    
    # Performance metrics
    feed_metadata: FeedMetadataEnhanced
    cache_info: CacheInfo
```

### 2. Real-time Feed Updates

**Endpoint:** `GET /api/v1/feed/family/{pregnancy_id}/updates`

```python
@router.get("/family/{pregnancy_id}/updates", response_model=FeedUpdatesResponse)
async def get_feed_updates(
    pregnancy_id: str,
    since_timestamp: str = Query(..., description="ISO timestamp of last update"),
    update_types: List[FeedUpdateType] = Query(default=["all"], description="Types of updates to include"),
    client_session_id: str = Query(..., description="Client session identifier"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get incremental feed updates since last sync for real-time updates.
    
    Update Types:
    - new_posts: New posts added to feed
    - reactions: New reactions on existing posts
    - comments: New comments on existing posts
    - celebrations: New celebrations triggered
    - family_warmth: Updated warmth scores
    - system_updates: System-generated content
    """
```

### 3. Story Card Feed (New)

**Endpoint:** `GET /api/v1/feed/story-cards/{pregnancy_id}`

```python
@router.get("/story-cards/{pregnancy_id}/enhanced", response_model=StoryCardFeedResponse)
async def get_enhanced_story_card_feed(
    pregnancy_id: str,
    limit: int = Query(15, ge=5, le=30),
    card_types: Optional[List[StoryCardType]] = Query(None, description="Specific card types to include"),
    personalization_context: Optional[str] = Query(None, description="Additional personalization context"),
    include_interactive_elements: bool = Query(True, description="Include interactive prompts and CTAs"),
    user_id: str = Query(..., description="User ID for personalization"),
    session: Session = Depends(get_session)
):
    """
    Enhanced story card feed with advanced personalization and interactive elements.
    
    Story Card Types:
    - baby_development: Weekly baby development cards
    - user_moment: User-generated content cards
    - pregnancy_tip: Personalized tips and advice
    - family_warmth_summary: Family engagement summaries
    - milestone_celebration: Milestone celebration cards
    - memory_prompt: Memory book prompts
    - interactive_poll: Interactive family polls
    - health_reminder: Health and appointment reminders
    """
```

### 4. Integrated Content Feed (Enhanced)

**Endpoint:** `GET /api/v1/feed/integrated/{pregnancy_id}/v2`

```python
@router.get("/integrated/{pregnancy_id}/v2", response_model=IntegratedFeedResponseV2)
async def get_integrated_feed_v2(
    pregnancy_id: str,
    limit: int = Query(20, ge=5, le=50),
    
    # Content integration options
    content_mix_ratio: Optional[str] = Query("balanced", regex="^(user_heavy|content_heavy|balanced)$"),
    include_educational_content: bool = Query(True),
    include_emotional_support: bool = Query(True),
    include_milestone_content: bool = Query(True),
    
    # Advanced personalization
    emotional_state: Optional[str] = Query(None, description="Current emotional state for content personalization"),
    time_of_day_optimization: bool = Query(True, description="Optimize content for current time"),
    cultural_preferences: Optional[Dict[str, Any]] = Query(None, description="Cultural content preferences"),
    
    # Family context
    family_engagement_level: Optional[str] = Query(None, description="Current family engagement level"),
    recent_family_activity: Optional[str] = Query(None, description="Recent family activity context"),
    
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
```

---

## Real-time Features

### 1. WebSocket Connections

**Endpoint:** `WS /ws/feed/{pregnancy_id}`

```python
@router.websocket("/ws/feed/{pregnancy_id}")
async def websocket_feed_updates(
    websocket: WebSocket,
    pregnancy_id: str,
    user_id: str = Query(...),
    session_id: str = Query(...),
    session: Session = Depends(get_session)
):
    """
    WebSocket endpoint for real-time feed updates.
    
    Message Types (Client -> Server):
    - subscribe: Subscribe to specific update types
    - unsubscribe: Unsubscribe from update types
    - heartbeat: Keep connection alive
    - sync_request: Request full sync
    - optimistic_update: Send optimistic update for immediate UI response
    
    Message Types (Server -> Client):
    - new_post: New post added to feed
    - reaction_update: Reaction counts updated
    - comment_update: New comment added
    - celebration_triggered: Celebration event
    - warmth_update: Family warmth score updated
    - sync_complete: Full sync completed
    - error: Error occurred
    """
```

**WebSocket Message Schema:**
```python
class WebSocketMessage(BaseModel):
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    session_id: str
    user_id: str

class FeedUpdateMessage(WebSocketMessage):
    class Config:
        schema_extra = {
            "example": {
                "message_type": "new_post",
                "payload": {
                    "post": {
                        "id": "post_123",
                        "author_id": "user_456",
                        "type": "milestone",
                        "content": {...},
                        "warmth_score": 0.85
                    }
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "session_id": "session_789",
                "user_id": "user_123"
            }
        }
```

### 2. Server-Sent Events (SSE)

**Endpoint:** `GET /api/v1/feed/sse/{pregnancy_id}`

```python
@router.get("/feed/sse/{pregnancy_id}")
async def feed_sse_endpoint(
    request: Request,
    pregnancy_id: str,
    user_id: str = Query(...),
    update_types: List[str] = Query(default=["all"]),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Server-Sent Events endpoint for real-time feed updates.
    Less resource-intensive alternative to WebSockets.
    
    Event Types:
    - feed-update: New feed content available
    - reaction-update: Reaction counts changed
    - celebration: Celebration triggered
    - warmth-update: Family warmth score updated
    - milestone: Milestone reached
    - system-notification: System message
    """
    
    async def event_generator():
        while True:
            # Check for new updates
            updates = await get_feed_updates_since_last_check(
                session, pregnancy_id, user_id, last_check_time
            )
            
            for update in updates:
                yield {
                    "event": update.event_type,
                    "data": json.dumps(update.payload),
                    "id": update.id,
                    "retry": 1000
                }
            
            await asyncio.sleep(1)  # Poll every second
    
    return EventSourceResponse(event_generator())
```

---

## Reaction System

### 1. Enhanced Reaction Endpoints

**Add/Update Reaction (Enhanced):**
```python
@router.post("/reactions/v2", response_model=ReactionResponseV2)
async def add_reaction_v2(
    reaction_request: EnhancedReactionRequest,
    optimistic_update: bool = Query(False, description="Handle as optimistic update"),
    client_session_id: str = Query(..., description="Client session for optimistic updates"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
```

**Enhanced Reaction Request Model:**
```python
class EnhancedReactionRequest(BaseModel):
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    reaction_type: PregnancyReactionType
    
    # Enhanced features
    reaction_intensity: Optional[float] = Field(default=1.0, ge=0.1, le=2.0, description="Reaction intensity multiplier")
    custom_message: Optional[str] = Field(default=None, max_length=200, description="Optional custom message with reaction")
    reaction_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for reaction")
    
    # Real-time features
    is_optimistic: bool = Field(default=False, description="Whether this is an optimistic update")
    client_temp_id: Optional[str] = Field(default=None, description="Client-generated temporary ID")
    
    # Celebration triggers
    trigger_celebration: bool = Field(default=True, description="Whether to trigger celebration if applicable")
    family_notification: bool = Field(default=True, description="Whether to notify family members")

class PregnancyReactionTypeV2(str, Enum):
    # Existing reactions
    LOVE = "love"           # ❤️
    EXCITED = "excited"     # 😍
    CARE = "care"           # 🤗
    SUPPORT = "support"     # 💪
    BEAUTIFUL = "beautiful"  # ✨
    FUNNY = "funny"         # 😂
    PRAYING = "praying"     # 🙏
    PROUD = "proud"         # 🏆
    GRATEFUL = "grateful"   # 🙏✨
    
    # Enhanced reactions for pregnancy context
    EMOTIONAL = "emotional" # 😭 Happy tears
    AMAZED = "amazed"      # 😲 Amazing moment
    HOPEFUL = "hopeful"    # 🌟 Hope and optimism
    BLESSED = "blessed"    # 🙌 Feeling blessed
    STRONG = "strong"      # 💪 Strength and resilience
    PEACEFUL = "peaceful"  # ☮️ Peace and calm
    ANTICIPATION = "anticipation" # ⏰ Looking forward
```

### 2. Reaction Analytics

**Endpoint:** `GET /api/v1/reactions/analytics/{pregnancy_id}`

```python
@router.get("/reactions/analytics/{pregnancy_id}", response_model=ReactionAnalyticsResponse)
async def get_reaction_analytics(
    pregnancy_id: str,
    time_period: str = Query("7d", regex="^(1d|7d|30d|90d|all)$"),
    include_family_breakdown: bool = Query(True),
    include_reaction_patterns: bool = Query(True),
    include_emotional_insights: bool = Query(True),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Advanced reaction analytics for pregnancy feed.
    
    Returns:
    - Reaction trends over time
    - Most popular reaction types
    - Family member engagement patterns
    - Emotional sentiment analysis
    - Celebration trigger statistics
    """
```

### 3. Bulk Reaction Operations

**Endpoint:** `POST /api/v1/reactions/bulk`

```python
@router.post("/reactions/bulk", response_model=BulkReactionResponse)
async def handle_bulk_reactions(
    bulk_request: BulkReactionRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Handle multiple reaction operations in a single request.
    Useful for optimistic updates and offline synchronization.
    """

class BulkReactionRequest(BaseModel):
    operations: List[ReactionOperation]
    session_id: str
    sync_token: Optional[str] = None

class ReactionOperation(BaseModel):
    operation_type: str  # "add", "update", "remove"
    target_id: str  # post_id or comment_id
    target_type: str  # "post" or "comment"
    reaction_type: Optional[PregnancyReactionTypeV2] = None
    client_temp_id: Optional[str] = None
    timestamp: datetime
```

---

## Comment Threading

### 1. Enhanced Comment System

**Add Comment (Enhanced):**
```python
@router.post("/comments/v2", response_model=CommentResponseV2)
async def add_comment_v2(
    comment_request: EnhancedCommentRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
```

**Enhanced Comment Models:**
```python
class EnhancedCommentRequest(BaseModel):
    post_id: str
    content: str = Field(min_length=1, max_length=2000)
    parent_id: Optional[str] = None  # For threaded replies
    
    # Enhanced features
    mentions: List[str] = Field(default_factory=list, description="User IDs mentioned in comment")
    reply_to_user: Optional[str] = Field(default=None, description="Specific user being replied to")
    comment_type: CommentType = Field(default=CommentType.STANDARD)
    
    # Rich content
    attachments: List[CommentAttachment] = Field(default_factory=list)
    formatting: Optional[CommentFormatting] = Field(default=None)
    
    # Context
    emotional_context: Optional[str] = Field(default=None)
    is_private_to_author: bool = Field(default=False, description="Only visible to post author")
    is_family_only: bool = Field(default=True, description="Only visible to family members")

class CommentType(str, Enum):
    STANDARD = "standard"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    SUPPORT = "support"
    CELEBRATION = "celebration"
    PRIVATE_NOTE = "private_note"

class CommentAttachment(BaseModel):
    type: str  # "image", "gif", "sticker"
    url: str
    metadata: Optional[Dict[str, Any]] = None

class CommentFormatting(BaseModel):
    has_bold: bool = False
    has_italic: bool = False
    has_links: bool = False
    mentions_formatted: List[Dict[str, str]] = Field(default_factory=list)
```

### 2. Threaded Comments Endpoint

**Endpoint:** `GET /api/v1/comments/thread/{post_id}`

```python
@router.get("/comments/thread/{post_id}", response_model=ThreadedCommentsResponse)
async def get_threaded_comments(
    post_id: str,
    max_depth: int = Query(3, ge=1, le=5, description="Maximum thread depth"),
    sort_by: CommentSortType = Query(CommentSortType.CHRONOLOGICAL),
    include_private: bool = Query(False, description="Include private comments if user has access"),
    include_reactions: bool = Query(True, description="Include reaction counts on comments"),
    page_size: int = Query(20, ge=5, le=100),
    page: int = Query(1, ge=1),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get threaded comments with nested replies.
    
    Response includes:
    - Hierarchical comment structure
    - Reaction counts for each comment
    - User permissions for each comment
    - Reply counts and pagination
    - Real-time update metadata
    """

class CommentSortType(str, Enum):
    CHRONOLOGICAL = "chronological"  # Oldest first
    REVERSE_CHRONOLOGICAL = "reverse_chronological"  # Newest first
    MOST_REACTIONS = "most_reactions"  # Most reacted first
    FAMILY_PRIORITY = "family_priority"  # Family members first

class ThreadedComment(BaseModel):
    id: str
    post_id: str
    user_id: str
    author: UserBasicInfo
    
    content: str
    formatted_content: str
    mentions: List[UserMention]
    attachments: List[CommentAttachment]
    
    parent_id: Optional[str] = None
    thread_level: int = 0
    reply_count: int = 0
    replies: List["ThreadedComment"] = Field(default_factory=list)
    
    # Engagement
    reaction_summary: CommentReactionSummary
    user_can_reply: bool
    user_can_edit: bool
    user_can_delete: bool
    
    # Metadata
    edited: bool = False
    is_private: bool = False
    is_family_only: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

ThreadedComment.update_forward_refs()  # For self-referencing model
```

### 3. Comment Notifications

**Endpoint:** `POST /api/v1/comments/notifications/mark-read`

```python
@router.post("/comments/notifications/mark-read")
async def mark_comment_notifications_read(
    notification_request: CommentNotificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Mark comment notifications as read."""

class CommentNotificationRequest(BaseModel):
    comment_ids: Optional[List[str]] = None  # Specific comments
    post_id: Optional[str] = None  # All comments on post
    mark_all: bool = False  # All comment notifications
    notification_types: List[str] = Field(default_factory=lambda: ["mention", "reply", "reaction"])
```

---

## Feed Performance

### 1. Advanced Caching Strategy

**Cache Configuration:**
```python
class FeedCacheConfig:
    # Cache keys and TTL
    FAMILY_FEED_TTL = 300  # 5 minutes
    PERSONAL_TIMELINE_TTL = 180  # 3 minutes
    STORY_CARDS_TTL = 600  # 10 minutes
    REACTION_COUNTS_TTL = 60  # 1 minute
    COMMENT_THREADS_TTL = 240  # 4 minutes
    
    # Cache strategies
    @staticmethod
    def get_feed_cache_key(pregnancy_id: str, user_id: str, params: FeedRequest) -> str:
        param_hash = hashlib.md5(str(sorted(params.dict().items())).encode()).hexdigest()[:8]
        return f"feed:family:{pregnancy_id}:{user_id}:{param_hash}"
    
    @staticmethod
    def get_story_cards_cache_key(pregnancy_id: str, user_id: str, limit: int) -> str:
        return f"story_cards:{pregnancy_id}:{user_id}:{limit}"
```

**Cache Invalidation:**
```python
@router.post("/cache/invalidate", include_in_schema=False)
async def invalidate_feed_cache(
    invalidation_request: CacheInvalidationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Manual cache invalidation for feed data.
    Triggered by:
    - New posts
    - Reactions added/removed
    - Comments added
    - Family warmth score updates
    - Celebration triggers
    """

class CacheInvalidationRequest(BaseModel):
    pregnancy_id: str
    invalidation_types: List[str]  # ["feed", "story_cards", "reactions", "comments"]
    affected_user_ids: Optional[List[str]] = None
    cascade_to_family: bool = True
```

### 2. Database Optimization

**Optimized Feed Query:**
```python
async def build_optimized_feed_query(
    session: Session,
    pregnancy_id: str,
    user_id: str,
    params: FeedRequest
) -> Select:
    """
    Build optimized query with proper indexes and joins.
    
    Optimization techniques:
    - Selective column loading
    - Proper index usage
    - Join optimization
    - Query result caching
    - Connection pooling
    """
    
    # Base query with selective loading
    base_query = select(
        Post.id,
        Post.author_id,
        Post.type,
        Post.content,
        Post.family_warmth_score,
        Post.reaction_count,
        Post.comment_count,
        Post.created_at,
        Post.updated_at,
        # Selective content loading based on request parameters
        case(
            (params.include_reactions == True, Post.reaction_count),
            else_=literal_column("0")
        ).label("reaction_count_conditional"),
        # Join author info if needed
        case(
            (params.include_reactions == True, User.display_name),
            else_=literal_column("''")
        ).label("author_name")
    ).select_from(
        Post.join(User, Post.author_id == User.id, isouter=not params.include_reactions)
    )
    
    # Apply filters with index hints
    base_query = base_query.where(
        and_(
            Post.pregnancy_id == pregnancy_id,
            Post.status == PostStatus.PUBLISHED,
            Post.deleted_at.is_(None)
        )
    )
    
    return base_query
```

### 3. Pagination & Infinite Scroll

**Enhanced Pagination:**
```python
@router.get("/family/{pregnancy_id}/paginated", response_model=PaginatedFeedResponse)
async def get_paginated_feed(
    pregnancy_id: str,
    # Cursor-based pagination
    cursor: Optional[str] = Query(None, description="Cursor for next page"),
    limit: int = Query(20, ge=5, le=100),
    
    # Offset-based pagination (legacy support)
    offset: Optional[int] = Query(None, ge=0),
    
    # Direction for cursor pagination
    direction: str = Query("forward", regex="^(forward|backward)$"),
    
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Enhanced pagination supporting both cursor-based and offset-based pagination.
    
    Cursor-based pagination provides:
    - Consistent results during real-time updates
    - Better performance for large datasets
    - No duplicate items during infinite scroll
    - Stable pagination even with new content
    """

class PaginatedFeedResponse(BaseModel):
    posts: List[EnrichedPost]
    
    # Cursor pagination
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_next: bool = False
    has_prev: bool = False
    
    # Legacy offset pagination
    total_count: Optional[int] = None
    next_offset: Optional[int] = None
    
    # Metadata
    page_info: PageInfo

class PageInfo(BaseModel):
    page_size: int
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    pagination_type: str  # "cursor" or "offset"
    estimated_total: Optional[int] = None
```

### 4. Performance Monitoring

**Performance Metrics Endpoint:**
```python
@router.get("/performance/metrics", response_model=FeedPerformanceMetrics)
async def get_feed_performance_metrics(
    pregnancy_id: Optional[str] = Query(None),
    time_window: str = Query("1h", regex="^(5m|1h|24h|7d)$"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get feed performance metrics for monitoring and optimization.
    
    Metrics include:
    - Query execution times
    - Cache hit rates
    - Error rates
    - User engagement patterns
    - System resource usage
    """

class FeedPerformanceMetrics(BaseModel):
    query_performance: QueryPerformanceStats
    cache_performance: CachePerformanceStats
    engagement_metrics: EngagementMetrics
    error_rates: ErrorRateStats
    resource_usage: ResourceUsageStats

class QueryPerformanceStats(BaseModel):
    avg_query_time_ms: float
    p95_query_time_ms: float
    p99_query_time_ms: float
    slow_queries_count: int
    total_queries: int

class CachePerformanceStats(BaseModel):
    hit_rate: float
    miss_rate: float
    eviction_rate: float
    memory_usage_mb: float
    avg_key_ttl: float
```

---

## Data Models

### 1. Enhanced Post Model

```python
class EnhancedPost(Post):
    """Enhanced post model with additional computed fields for feed display."""
    
    # Computed fields
    engagement_score: float = Field(description="Calculated engagement score")
    trending_score: float = Field(description="Trending algorithm score")
    family_warmth_breakdown: FamilyWarmthBreakdown = Field(description="Detailed warmth analysis")
    
    # Real-time features
    live_reaction_count: int = Field(description="Real-time reaction count")
    live_comment_count: int = Field(description="Real-time comment count")
    last_activity_at: datetime = Field(description="Last engagement activity")
    
    # Memory book integration
    memory_book_auto_curated: bool = Field(description="Auto-curated for memory book")
    memory_book_user_saved: bool = Field(description="Manually saved by user")
    memory_book_family_nominated: bool = Field(description="Nominated by family members")
    
    # Celebration data
    celebration_status: CelebrationStatus = Field(description="Current celebration status")
    celebration_participants: List[CelebrationParticipant] = Field(default_factory=list)
    
    # AI-generated insights
    ai_emotional_analysis: Optional[EmotionalAnalysis] = Field(default=None)
    ai_content_suggestions: List[ContentSuggestion] = Field(default_factory=list)

class FamilyWarmthBreakdown(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    reaction_warmth: float = Field(ge=0.0, le=1.0)
    comment_warmth: float = Field(ge=0.0, le=1.0)
    engagement_velocity: float = Field(ge=0.0, le=1.0)
    family_participation_rate: float = Field(ge=0.0, le=1.0)
    emotional_resonance: float = Field(ge=0.0, le=1.0)

class CelebrationStatus(str, Enum):
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

class CelebrationParticipant(BaseModel):
    user_id: str
    user_name: str
    participation_type: str  # "reaction", "comment", "share"
    timestamp: datetime

class EmotionalAnalysis(BaseModel):
    primary_emotion: str
    emotional_intensity: float = Field(ge=0.0, le=1.0)
    emotional_tags: List[str] = Field(default_factory=list)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    family_resonance_prediction: float = Field(ge=0.0, le=1.0)
```

### 2. Enhanced Reaction Model

```python
class EnhancedReaction(Reaction):
    """Enhanced reaction model with additional context and metadata."""
    
    # Enhanced context
    reaction_intensity: float = Field(default=1.0, ge=0.1, le=2.0)
    custom_message: Optional[str] = Field(default=None, max_length=200)
    reaction_context: Optional[Dict[str, Any]] = Field(default=None)
    
    # Real-time features
    client_temp_id: Optional[str] = Field(default=None)
    optimistic_update: bool = Field(default=False)
    sync_status: SyncStatus = Field(default=SyncStatus.SYNCED)
    
    # Celebration triggers
    triggered_celebration: bool = Field(default=False)
    celebration_id: Optional[str] = Field(default=None)
    
    # Family context
    family_member_info: Optional[FamilyMemberInfo] = Field(default=None)
    relationship_to_author: Optional[str] = Field(default=None)
    
    # Analytics
    reaction_source: ReactionSource = Field(default=ReactionSource.MANUAL)
    device_context: Optional[DeviceContext] = Field(default=None)

class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"

class ReactionSource(str, Enum):
    MANUAL = "manual"
    QUICK_REACT = "quick_react"
    AUTO_SUGGEST = "auto_suggest"
    CELEBRATION = "celebration"

class DeviceContext(BaseModel):
    device_type: str  # "mobile", "tablet", "desktop"
    app_version: str
    platform: str  # "ios", "android", "web"
    user_agent: Optional[str] = None
```

### 3. Comment Threading Models

```python
class CommentThread(BaseModel):
    """Hierarchical comment thread structure."""
    
    root_comment: ThreadedComment
    reply_tree: Dict[str, List[ThreadedComment]] = Field(default_factory=dict)
    thread_stats: ThreadStats
    
    # Thread management
    max_depth_reached: bool = Field(default=False)
    collapsed_replies: List[str] = Field(default_factory=list)
    thread_participants: List[ThreadParticipant] = Field(default_factory=list)
    
    # Real-time features
    live_reply_count: int = Field(default=0)
    active_typists: List[str] = Field(default_factory=list)
    last_activity: Optional[datetime] = Field(default=None)

class ThreadStats(BaseModel):
    total_replies: int = 0
    max_depth: int = 0
    participant_count: int = 0
    reaction_count: int = 0
    most_reacted_reply_id: Optional[str] = None

class ThreadParticipant(BaseModel):
    user_id: str
    user_name: str
    reply_count: int = 0
    last_activity: datetime
    relationship_to_op: Optional[str] = None  # Original poster
```

---

## Authentication & Permissions

### 1. Enhanced Permission System

```python
class FeedPermissionChecker:
    """Enhanced permission checking for feed operations."""
    
    @staticmethod
    async def check_feed_access(
        session: Session,
        user_id: str,
        pregnancy_id: str,
        access_level: FeedAccessLevel = FeedAccessLevel.READ
    ) -> PermissionResult:
        """
        Check user access to pregnancy feed with granular permissions.
        
        Access Levels:
        - READ: View feed content
        - REACT: Add reactions to posts
        - COMMENT: Add comments to posts
        - POST: Create new posts
        - MODERATE: Moderate family content
        - ADMIN: Full administrative access
        """
        
        permission_result = PermissionResult()
        
        # Check basic pregnancy access
        if await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            permission_result.access_level = FeedAccessLevel.ADMIN
            permission_result.can_read = True
            permission_result.can_react = True
            permission_result.can_comment = True
            permission_result.can_post = True
            permission_result.can_moderate = True
        else:
            # Check family member status
            family_membership = await family_member_service.get_user_membership(
                session, user_id, pregnancy_id
            )
            
            if family_membership:
                permission_result = await _calculate_family_permissions(
                    session, family_membership, access_level
                )
            else:
                permission_result.access_denied = True
                permission_result.reason = "No access to this pregnancy feed"
        
        return permission_result

class FeedAccessLevel(str, Enum):
    READ = "read"
    REACT = "react"
    COMMENT = "comment"
    POST = "post"
    MODERATE = "moderate"
    ADMIN = "admin"

class PermissionResult(BaseModel):
    access_denied: bool = False
    reason: Optional[str] = None
    
    access_level: FeedAccessLevel = FeedAccessLevel.READ
    can_read: bool = False
    can_react: bool = False
    can_comment: bool = False
    can_post: bool = False
    can_moderate: bool = False
    
    # Granular permissions
    can_see_private_posts: bool = False
    can_access_analytics: bool = False
    can_trigger_celebrations: bool = False
    can_manage_memory_book: bool = False
    
    # Rate limiting
    reaction_rate_limit: int = 100  # per hour
    comment_rate_limit: int = 50    # per hour
    post_rate_limit: int = 10       # per hour
```

### 2. Content Privacy & Visibility

```python
class ContentVisibilityChecker:
    """Check content visibility based on privacy settings."""
    
    @staticmethod
    async def can_user_see_post(
        session: Session,
        user_id: str,
        post: Post,
        pregnancy_id: str
    ) -> VisibilityResult:
        """
        Determine if user can see a specific post based on privacy settings.
        """
        
        visibility_result = VisibilityResult()
        
        # Check post privacy settings
        privacy = post.privacy
        
        if privacy.visibility == VisibilityLevel.PRIVATE:
            # Only post author can see private posts
            visibility_result.can_see = (user_id == post.author_id)
        elif privacy.visibility == VisibilityLevel.PARTNER_ONLY:
            # Post author + partners
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            visibility_result.can_see = (
                user_id == post.author_id or
                user_id in pregnancy.partner_ids
            )
        elif privacy.visibility == VisibilityLevel.CUSTOM:
            # Custom visibility list
            if privacy.allowed_members:
                visibility_result.can_see = user_id in privacy.allowed_members
            elif privacy.allowed_groups:
                user_groups = await family_member_service.get_user_group_memberships(
                    session, user_id, pregnancy_id
                )
                user_group_ids = [group.id for group in user_groups]
                visibility_result.can_see = bool(
                    set(privacy.allowed_groups) & set(user_group_ids)
                )
        else:
            # Check family group access
            visibility_result.can_see = await family_member_service.user_has_family_access(
                session, user_id, pregnancy_id, privacy.visibility
            )
        
        # Apply additional restrictions
        if visibility_result.can_see:
            visibility_result.can_react = privacy.allow_reactions
            visibility_result.can_comment = privacy.allow_comments
            visibility_result.can_download = privacy.allow_downloads
        
        return visibility_result

class VisibilityResult(BaseModel):
    can_see: bool = False
    can_react: bool = False
    can_comment: bool = False
    can_download: bool = False
    
    restriction_reason: Optional[str] = None
    partial_access: bool = False  # Can see post but not all features
```

### 3. Rate Limiting

```python
class FeedRateLimiter:
    """Rate limiting for feed operations to prevent abuse."""
    
    @staticmethod
    async def check_rate_limit(
        redis_client,
        user_id: str,
        operation_type: str,
        pregnancy_id: Optional[str] = None
    ) -> RateLimitResult:
        """
        Check rate limits for feed operations.
        
        Rate Limits:
        - Reactions: 100/hour, 10/minute
        - Comments: 50/hour, 5/minute  
        - Posts: 10/hour, 2/minute
        - API calls: 1000/hour, 100/minute
        """
        
        # Define rate limits by operation type
        limits = {
            "reaction": {"hour": 100, "minute": 10},
            "comment": {"hour": 50, "minute": 5},
            "post": {"hour": 10, "minute": 2},
            "api_call": {"hour": 1000, "minute": 100}
        }
        
        if operation_type not in limits:
            return RateLimitResult(allowed=True)
        
        # Check both hourly and minute limits
        for window, limit in limits[operation_type].items():
            key = f"rate_limit:{operation_type}:{user_id}:{window}"
            if pregnancy_id:
                key += f":{pregnancy_id}"
            
            current_count = await redis_client.get(key) or 0
            
            if int(current_count) >= limit:
                return RateLimitResult(
                    allowed=False,
                    reason=f"Rate limit exceeded: {limit} {operation_type}s per {window}",
                    retry_after=await _calculate_retry_after(redis_client, key, window)
                )
        
        return RateLimitResult(allowed=True)
    
    @staticmethod
    async def increment_rate_limit(
        redis_client,
        user_id: str,
        operation_type: str,
        pregnancy_id: Optional[str] = None
    ):
        """Increment rate limit counters after successful operation."""
        
        for window in ["hour", "minute"]:
            key = f"rate_limit:{operation_type}:{user_id}:{window}"
            if pregnancy_id:
                key += f":{pregnancy_id}"
            
            ttl = 3600 if window == "hour" else 60
            
            await redis_client.incr(key)
            await redis_client.expire(key, ttl)

class RateLimitResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    retry_after: Optional[int] = None  # seconds
    current_usage: Optional[int] = None
    limit: Optional[int] = None
```

---

## Error Handling

### 1. Comprehensive Error Responses

```python
class FeedErrorHandler:
    """Centralized error handling for feed operations."""
    
    @staticmethod
    def handle_feed_error(error: Exception, context: Dict[str, Any]) -> HTTPException:
        """Convert internal errors to appropriate HTTP responses."""
        
        error_mapping = {
            PregnancyNotFoundError: {
                "status_code": 404,
                "detail": "Pregnancy not found",
                "error_code": "PREGNANCY_NOT_FOUND"
            },
            InsufficientPermissionsError: {
                "status_code": 403,
                "detail": "Insufficient permissions for this operation",
                "error_code": "INSUFFICIENT_PERMISSIONS"
            },
            RateLimitExceededError: {
                "status_code": 429,
                "detail": "Rate limit exceeded. Please try again later.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            },
            InvalidFeedParametersError: {
                "status_code": 400,
                "detail": "Invalid feed parameters provided",
                "error_code": "INVALID_PARAMETERS"
            },
            DatabaseConnectionError: {
                "status_code": 503,
                "detail": "Service temporarily unavailable",
                "error_code": "SERVICE_UNAVAILABLE"
            },
            CacheConnectionError: {
                "status_code": 200,  # Degrade gracefully
                "detail": "Feed loaded successfully (cached data unavailable)",
                "error_code": "CACHE_UNAVAILABLE",
                "warning": True
            }
        }
        
        error_type = type(error)
        if error_type in error_mapping:
            error_info = error_mapping[error_type]
            
            # Add context information
            error_details = {
                "error_code": error_info["error_code"],
                "message": error_info["detail"],
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": context.get("request_id")
            }
            
            # Add specific error information
            if hasattr(error, 'additional_info'):
                error_details["additional_info"] = error.additional_info
            
            if error_info.get("warning"):
                # For non-critical errors, return success with warning
                return {"warning": True, "details": error_details}
            else:
                raise HTTPException(
                    status_code=error_info["status_code"],
                    detail=error_details
                )
        else:
            # Unknown error - log and return generic error
            logger.error(f"Unknown feed error: {error}", extra=context)
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                    "request_id": context.get("request_id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

class FeedErrorResponse(BaseModel):
    """Standardized error response for feed operations."""
    
    error_code: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None
    
    # Error details
    field_errors: Optional[Dict[str, List[str]]] = None
    validation_errors: Optional[List[ValidationError]] = None
    
    # Recovery suggestions
    suggested_actions: Optional[List[str]] = None
    retry_after: Optional[int] = None
    
    # Support information
    support_reference: Optional[str] = None
    documentation_links: Optional[List[str]] = None

# Custom Exception Classes
class PregnancyNotFoundError(Exception):
    pass

class InsufficientPermissionsError(Exception):
    def __init__(self, message: str, required_permission: str = None):
        self.message = message
        self.required_permission = required_permission
        super().__init__(message)

class RateLimitExceededError(Exception):
    def __init__(self, message: str, retry_after: int = None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

class InvalidFeedParametersError(Exception):
    def __init__(self, message: str, invalid_fields: List[str] = None):
        self.message = message
        self.invalid_fields = invalid_fields or []
        super().__init__(message)
```

### 2. Graceful Degradation

```python
class FeedGracefulDegradation:
    """Handle service degradation gracefully when components fail."""
    
    @staticmethod
    async def get_feed_with_fallback(
        session: Session,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest,
        services_status: Dict[str, bool]
    ) -> FeedResponse:
        """
        Get feed with fallback strategies when services are unavailable.
        
        Fallback strategies:
        - Cache unavailable: Serve from database only
        - Real-time features unavailable: Serve static content
        - Analytics unavailable: Skip engagement calculations
        - Content service unavailable: Show user posts only
        """
        
        response_warnings = []
        
        try:
            # Try full feed first
            if all(services_status.values()):
                return await feed_service.get_family_feed(
                    session, user_id, pregnancy_id, feed_request
                )
            
            # Fallback: Basic feed without enhanced features
            basic_posts = await feed_service.get_basic_posts(
                session, user_id, pregnancy_id, feed_request
            )
            
            # Add available enhancements
            enhanced_posts = []
            for post in basic_posts:
                enhanced_post = EnrichedPost(**post.dict())
                
                # Add reactions if service available
                if services_status.get("reaction_service", False):
                    try:
                        enhanced_post.reaction_summary = await reaction_service.get_post_reaction_summary(
                            session, post.id
                        )
                    except Exception:
                        response_warnings.append("Reaction data unavailable")
                
                # Add comments if service available
                if services_status.get("comment_service", False):
                    try:
                        enhanced_post.comment_preview = await comment_service.get_post_comment_preview(
                            session, post.id
                        )
                    except Exception:
                        response_warnings.append("Comment data unavailable")
                
                enhanced_posts.append(enhanced_post)
            
            return FeedResponse(
                posts=enhanced_posts,
                total_count=len(enhanced_posts),
                has_more=False,
                warnings=response_warnings,
                degraded_mode=True
            )
            
        except Exception as e:
            # Ultimate fallback: Cached response if available
            cached_response = await cache_service.get_cached_feed(
                user_id, pregnancy_id, "fallback"
            )
            
            if cached_response:
                cached_response.warnings = ["Serving cached data due to service issues"]
                cached_response.degraded_mode = True
                return cached_response
            else:
                raise FeedServiceUnavailableError(
                    "Feed service temporarily unavailable"
                )

class FeedServiceUnavailableError(Exception):
    pass
```

### 3. Request Validation

```python
class FeedRequestValidator:
    """Comprehensive request validation for feed endpoints."""
    
    @staticmethod
    def validate_feed_request(request: FeedRequest) -> ValidationResult:
        """Validate feed request parameters."""
        
        validation_result = ValidationResult()
        
        # Validate pagination parameters
        if request.limit < 1 or request.limit > 100:
            validation_result.add_error(
                "limit", "Limit must be between 1 and 100"
            )
        
        if request.offset < 0:
            validation_result.add_error(
                "offset", "Offset must be non-negative"
            )
        
        # Validate since timestamp
        if request.since:
            if request.since > datetime.utcnow():
                validation_result.add_error(
                    "since", "Since timestamp cannot be in the future"
                )
            
            # Don't allow very old timestamps (performance)
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            if request.since < six_months_ago:
                validation_result.add_error(
                    "since", "Since timestamp cannot be older than 6 months"
                )
        
        # Validate filter combinations
        if request.filter_type == FeedFilterType.TRENDING and request.since:
            validation_result.add_error(
                "filter_type", "Trending filter cannot be used with since parameter"
            )
        
        return validation_result
    
    @staticmethod
    def validate_reaction_request(request: EnhancedReactionRequest) -> ValidationResult:
        """Validate reaction request parameters."""
        
        validation_result = ValidationResult()
        
        # Either post_id or comment_id must be provided
        if not request.post_id and not request.comment_id:
            validation_result.add_error(
                "target", "Either post_id or comment_id must be provided"
            )
        
        if request.post_id and request.comment_id:
            validation_result.add_error(
                "target", "Cannot react to both post and comment simultaneously"
            )
        
        # Validate reaction intensity
        if request.reaction_intensity and (
            request.reaction_intensity < 0.1 or request.reaction_intensity > 2.0
        ):
            validation_result.add_error(
                "reaction_intensity", "Reaction intensity must be between 0.1 and 2.0"
            )
        
        # Validate custom message length
        if request.custom_message and len(request.custom_message) > 200:
            validation_result.add_error(
                "custom_message", "Custom message cannot exceed 200 characters"
            )
        
        return validation_result

class ValidationResult:
    def __init__(self):
        self.is_valid = True
        self.errors: Dict[str, List[str]] = {}
        self.warnings: List[str] = []
    
    def add_error(self, field: str, message: str):
        self.is_valid = False
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def to_exception(self) -> HTTPException:
        if not self.is_valid:
            return HTTPException(
                status_code=422,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "field_errors": self.errors,
                    "warnings": self.warnings
                }
            )
        return None
```

---

## API Examples

### 1. Enhanced Family Feed

**Request:**
```bash
curl -X GET "https://api.preggo.app/v1/feed/family/12345/enhanced" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -G \
  -d "limit=20" \
  -d "offset=0" \
  -d "filter_type=all" \
  -d "sort_by=chronological" \
  -d "real_time_updates=true" \
  -d "include_warmth_scores=true" \
  -d "include_celebration_triggers=true" \
  -d "personalization_level=standard" \
  -d "client_session_id=sess_789" \
  -d "last_sync_timestamp=2024-01-15T10:00:00Z"
```

**Response:**
```json
{
  "posts": [
    {
      "id": "post_123",
      "author_id": "user_456",
      "pregnancy_id": "preg_789",
      "type": "milestone",
      "content": {
        "title": "20 Week Anatomy Scan! 💕",
        "text": "Everything looks perfect! Baby is measuring right on track and we found out we're having a little girl! 👶🏽💗",
        "week": 20,
        "mood": "excited",
        "tags": ["ultrasound", "anatomy_scan", "baby_girl"]
      },
      "privacy": {
        "visibility": "immediate",
        "allow_comments": true,
        "allow_reactions": true
      },
      
      // Enhanced fields
      "family_warmth_score": 0.92,
      "family_warmth_breakdown": {
        "overall_score": 0.92,
        "reaction_warmth": 0.95,
        "comment_warmth": 0.88,
        "engagement_velocity": 0.94,
        "family_participation_rate": 0.89,
        "emotional_resonance": 0.93
      },
      
      "reaction_summary": {
        "total_count": 18,
        "reaction_counts": {
          "love": 8,
          "excited": 6,
          "beautiful": 3,
          "grateful": 1
        },
        "user_reaction": "love",
        "recent_reactors": ["user_111", "user_222", "user_333"]
      },
      
      "comment_preview": {
        "total_count": 7,
        "recent_comments": [
          {
            "id": "comment_444",
            "author_name": "Grandma Sarah",
            "content": "Oh my goodness! I can't wait to meet my granddaughter! 👶🏽💕",
            "created_at": "2024-01-15T10:45:00Z"
          }
        ],
        "has_user_commented": false
      },
      
      "engagement_stats": {
        "family_member_reactions": 15,
        "family_member_comments": 6,
        "family_member_views": 24,
        "needs_family_response": false,
        "celebration_worthy": true,
        "engagement_score": 87.5
      },
      
      "pregnancy_context": {
        "current_week": 20,
        "trimester": 2,
        "days_since_post": 0,
        "is_milestone_week": true,
        "baby_development": "Baby's anatomy is fully formed and clearly visible on ultrasound"
      },
      
      // Memory book integration
      "memory_book_eligible": true,
      "memory_book_priority": 0.95,
      "memory_book_auto_curated": true,
      
      // Celebration data
      "celebration_trigger_data": {
        "celebration_type": "milestone_reached",
        "milestone_name": "Anatomy Scan",
        "auto_message": "🎉 Congratulations on your 20-week anatomy scan!"
      },
      
      "celebration_status": "active",
      "celebration_participants": [
        {
          "user_id": "user_111",
          "user_name": "Mom",
          "participation_type": "reaction",
          "timestamp": "2024-01-15T10:30:00Z"
        }
      ],
      
      "is_trending": true,
      "requires_attention": false,
      "created_at": "2024-01-15T10:15:00Z",
      "updated_at": "2024-01-15T10:47:00Z"
    }
  ],
  
  "total_count": 156,
  "has_more": true,
  "next_offset": 20,
  
  // Real-time metadata
  "real_time_metadata": {
    "sync_token": "sync_abc123",
    "last_update_check": "2024-01-15T10:50:00Z",
    "pending_updates": 2,
    "websocket_available": true
  },
  
  "feed_generation_time": "2024-01-15T10:50:15Z",
  
  // Enhanced context
  "pregnancy_context": {
    "current_week": 20,
    "trimester": 2,
    "days_until_due": 140,
    "next_milestone": {
      "name": "Viability Milestone",
      "week": 24,
      "days_away": 28
    }
  },
  
  "family_warmth_summary": {
    "overall_family_engagement": 0.89,
    "most_active_family_members": ["user_111", "user_222"],
    "recent_celebration_count": 3,
    "warmth_trend": "increasing"
  },
  
  "celebration_opportunities": [
    {
      "type": "milestone_upcoming",
      "title": "Viability Milestone Coming Up!",
      "description": "Your baby will reach the viability milestone in 4 weeks",
      "suggested_action": "Start planning a celebration post"
    }
  ],
  
  "memory_book_suggestions": [
    {
      "post_id": "post_123",
      "suggestion_type": "auto_curate",
      "reason": "High family engagement milestone post",
      "confidence": 0.95
    }
  ],
  
  // Performance metadata
  "feed_metadata": {
    "query_time_ms": 145,
    "cache_hit": true,
    "total_query_count": 3,
    "personalization_applied": true
  },
  
  "cache_info": {
    "cached": true,
    "cache_age_seconds": 67,
    "cache_expires_in": 233
  }
}
```

### 2. Real-time WebSocket Updates

**WebSocket Connection:**
```javascript
const ws = new WebSocket('wss://api.preggo.app/ws/feed/preg_789?user_id=user_123&session_id=sess_789');

// Subscribe to specific update types
ws.send(JSON.stringify({
  message_type: 'subscribe',
  payload: {
    update_types: ['new_post', 'reactions', 'celebrations', 'family_warmth']
  },
  timestamp: new Date().toISOString(),
  session_id: 'sess_789',
  user_id: 'user_123'
}));

// Handle incoming updates
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  switch(message.message_type) {
    case 'new_post':
      updateFeedWithNewPost(message.payload.post);
      break;
      
    case 'reaction_update':
      updateReactionCounts(message.payload.post_id, message.payload.updated_counts);
      break;
      
    case 'celebration_triggered':
      showCelebration(message.payload.celebration);
      break;
      
    case 'warmth_update':
      updateWarmthScore(message.payload.post_id, message.payload.new_score);
      break;
  }
};
```

**WebSocket Message Examples:**

New Post Update:
```json
{
  "message_type": "new_post",
  "payload": {
    "post": {
      "id": "post_124",
      "author_id": "user_456",
      "type": "belly_photo",
      "content": {
        "title": "20 weeks bump! 🤰🏽",
        "text": "Growing baby girl is making her presence known! 💗",
        "week": 20
      },
      "family_warmth_score": 0.0,
      "created_at": "2024-01-15T11:00:00Z"
    },
    "insert_position": 0
  },
  "timestamp": "2024-01-15T11:00:00Z",
  "session_id": "sess_789",
  "user_id": "user_123"
}
```

Reaction Update:
```json
{
  "message_type": "reaction_update",
  "payload": {
    "post_id": "post_123",
    "updated_counts": {
      "love": 9,
      "excited": 6,
      "beautiful": 3,
      "grateful": 1
    },
    "new_reaction": {
      "user_id": "user_555",
      "user_name": "Uncle Mike",
      "reaction_type": "love"
    },
    "total_count": 19
  },
  "timestamp": "2024-01-15T11:05:00Z",
  "session_id": "sess_789",
  "user_id": "user_123"
}
```

### 3. Enhanced Reaction System

**Add Reaction with Context:**
```bash
curl -X POST "https://api.preggo.app/v1/feed/reactions/v2" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "post_123",
    "reaction_type": "excited",
    "reaction_intensity": 1.5,
    "custom_message": "This is so exciting! Can'\''t wait to meet her! 👶🏽💕",
    "reaction_context": {
      "celebration_trigger": true,
      "first_reaction_to_milestone": false
    },
    "trigger_celebration": true,
    "family_notification": true,
    "client_session_id": "sess_789"
  }'
```

**Response:**
```json
{
  "success": true,
  "reaction_id": "react_789",
  "updated_counts": {
    "love": 8,
    "excited": 7,
    "beautiful": 3,
    "grateful": 1
  },
  "total_count": 19,
  
  // Enhanced response data
  "celebration_triggered": {
    "celebration_id": "celeb_456",
    "celebration_type": "milestone_excitement",
    "message": "The family is so excited about your 20-week milestone! 🎉"
  },
  
  "family_warmth_impact": {
    "previous_score": 0.92,
    "new_score": 0.94,
    "warmth_increase": 0.02
  },
  
  "real_time_updates": {
    "websocket_sent": true,
    "family_notifications_sent": 5
  },
  
  "memory_book_impact": {
    "priority_increased": true,
    "new_priority": 0.97,
    "auto_curation_triggered": true
  },
  
  "message": "Reaction added successfully with celebration triggered!"
}
```

### 4. Threaded Comments

**Get Comment Thread:**
```bash
curl -X GET "https://api.preggo.app/v1/feed/comments/thread/post_123" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -G \
  -d "max_depth=3" \
  -d "sort_by=chronological" \
  -d "include_reactions=true" \
  -d "page_size=20" \
  -d "page=1"
```

**Response:**
```json
{
  "post_id": "post_123",
  "comment_threads": [
    {
      "root_comment": {
        "id": "comment_444",
        "post_id": "post_123",
        "user_id": "user_111",
        "author": {
          "id": "user_111",
          "name": "Grandma Sarah",
          "relationship": "grandmother"
        },
        
        "content": "Oh my goodness! I can't wait to meet my granddaughter! 👶🏽💕",
        "formatted_content": "Oh my goodness! I can't wait to meet my granddaughter! 👶🏽💕",
        "mentions": [],
        "attachments": [],
        
        "parent_id": null,
        "thread_level": 0,
        "reply_count": 2,
        "replies": [
          {
            "id": "comment_445",
            "user_id": "user_456",
            "author": {
              "id": "user_456",
              "name": "Emma",
              "relationship": "mother"
            },
            
            "content": "She's going to be so loved! ❤️ Can't wait for you to hold her, Mom!",
            "parent_id": "comment_444",
            "thread_level": 1,
            "reply_count": 1,
            
            "replies": [
              {
                "id": "comment_446",
                "user_id": "user_111",
                "author": {
                  "id": "user_111",
                  "name": "Grandma Sarah"
                },
                
                "content": "@Emma I'm already planning all the books I'm going to read to her! 📚✨",
                "mentions": [
                  {
                    "user_id": "user_456",
                    "user_name": "Emma",
                    "mention_text": "@Emma"
                  }
                ],
                "parent_id": "comment_445",
                "thread_level": 2,
                "reply_count": 0,
                "replies": [],
                
                "reaction_summary": {
                  "total_count": 3,
                  "reaction_counts": {
                    "love": 2,
                    "excited": 1
                  },
                  "user_reaction": null
                },
                
                "user_can_reply": true,
                "user_can_edit": false,
                "user_can_delete": false,
                "created_at": "2024-01-15T11:30:00Z"
              }
            ],
            
            "reaction_summary": {
              "total_count": 5,
              "reaction_counts": {
                "love": 4,
                "care": 1
              },
              "user_reaction": null
            },
            
            "created_at": "2024-01-15T11:00:00Z"
          }
        ],
        
        "reaction_summary": {
          "total_count": 8,
          "reaction_counts": {
            "love": 6,
            "excited": 2
          },
          "user_reaction": null
        },
        
        "user_can_reply": true,
        "user_can_edit": false,
        "user_can_delete": false,
        "created_at": "2024-01-15T10:45:00Z"
      },
      
      "thread_stats": {
        "total_replies": 2,
        "max_depth": 2,
        "participant_count": 2,
        "reaction_count": 16,
        "most_reacted_reply_id": "comment_445"
      },
      
      "live_reply_count": 2,
      "active_typists": [],
      "last_activity": "2024-01-15T11:30:00Z"
    }
  ],
  
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_threads": 1,
    "total_comments": 8,
    "has_next": false
  },
  
  "real_time_info": {
    "websocket_available": true,
    "live_updates_enabled": true,
    "typing_indicators_enabled": true
  }
}
```

### 5. Story Card Feed

**Request:**
```bash
curl -X GET "https://api.preggo.app/v1/feed/story-cards/preg_789/enhanced" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -G \
  -d "limit=15" \
  -d "user_id=user_123" \
  -d "card_types=baby_development,user_moment,pregnancy_tip" \
  -d "include_interactive_elements=true"
```

**Response:**
```json
{
  "pregnancy_id": "preg_789",
  "story_cards": [
    {
      "id": "weekly_development_20",
      "type": "baby_development",
      "priority": 10,
      
      "content": {
        "title": "Week 20: Your Baby This Week",
        "subtitle": "Your baby is the size of a banana! 🍌",
        "amazing_fact": "Your baby's sense of hearing is developing rapidly - they can hear your voice!",
        "connection_moment": "Try talking or singing to your baby. They're listening to you! 🎵",
        "size_comparison": "About 6.5 inches long (crown to rump)",
        "size_comparison_image": "/images/size-comparisons/banana.png",
        "major_developments": [
          "Anatomy scan can reveal baby's sex",
          "Baby's hearing is developing",
          "Eyebrows and hair are growing",
          "Baby can suck their thumb"
        ],
        "what_baby_can_do": "Your baby can now hear sounds from outside the womb and may respond to music or your voice!"
      },
      
      "pregnancy_context": {
        "week_number": 20,
        "trimester": 2,
        "is_development_highlight": true
      },
      
      "interaction_prompts": {
        "share_with_family": {
          "enabled": true,
          "prompt_text": "Share this exciting development with your family!",
          "suggested_message": "Baby can hear us now! 👂🏽💕"
        },
        "save_to_memory": {
          "enabled": true,
          "prompt_text": "Save this milestone to your memory book"
        },
        "start_conversation": {
          "enabled": true,
          "prompt_text": "Start a family conversation about baby's development",
          "suggested_topics": [
            "What songs should we sing to baby?",
            "Who's voice do you think baby will recognize first?",
            "Any family lullabies to share?"
          ]
        }
      },
      
      "visual_elements": {
        "background_gradient": ["#ff9a8b", "#fecfef"],
        "icon": "👂🏽",
        "illustration_url": "/illustrations/baby-hearing.svg"
      },
      
      "generated_at": "2024-01-15T10:50:00Z"
    },
    
    {
      "id": "post_123",
      "type": "user_moment",
      "priority": 9.2,
      
      "content": {
        "title": "Anatomy Scan Success! 💕",
        "text": "Everything looks perfect! Baby is measuring right on track and we found out we're having a little girl!",
        "mood": "excited",
        "post_type": "milestone",
        "tags": ["ultrasound", "anatomy_scan", "baby_girl"]
      },
      
      "family_warmth": {
        "score": 0.92,
        "visualization": "hearts_growing",
        "family_engagement_preview": "18 reactions from 8 family members"
      },
      
      "memory_book": {
        "eligible": true,
        "priority": 0.95,
        "auto_curated": true,
        "reason": "High-engagement milestone moment"
      },
      
      "celebration_status": {
        "active": true,
        "participants": 8,
        "celebration_message": "🎉 The whole family is celebrating your 20-week milestone!"
      },
      
      "interaction_prompts": {
        "view_full_post": {
          "enabled": true,
          "engagement_preview": "7 comments • 18 reactions"
        },
        "add_to_memory_book": {
          "enabled": true,
          "auto_suggested": true
        }
      },
      
      "created_at": "2024-01-15T10:15:00Z"
    },
    
    {
      "id": "tip_bonding_20",
      "type": "pregnancy_tip",
      "priority": 7.8,
      
      "content": {
        "title": "Bonding Through Sound",
        "subtitle": "Connect with your baby through voice and music",
        "text": "Now that your baby can hear, this is a perfect time to start building that connection. Try reading aloud, singing lullabies, or playing gentle music. Your baby is already learning to recognize your voice!",
        "tip_type": "emotional_support",
        "reading_time": 2,
        "featured_image": "/images/tips/pregnancy-bonding.jpg"
      },
      
      "personalization_context": {
        "personalization_score": 0.85,
        "reason": "Based on current week and family interaction patterns"
      },
      
      "interaction_prompts": {
        "mark_helpful": {
          "enabled": true,
          "prompt_text": "Was this tip helpful?"
        },
        "save_to_memory": {
          "enabled": true,
          "prompt_text": "Save this bonding idea"
        },
        "share_with_family": {
          "enabled": true,
          "suggested_message": "Let's all start talking to our little one! 🗣️💕"
        },
        "try_it_now": {
          "enabled": true,
          "action": "open_voice_recorder",
          "prompt_text": "Record a message for baby"
        }
      },
      
      "related_actions": [
        {
          "type": "create_post",
          "prompt": "Share a voice recording for baby",
          "template": "voice_message_to_baby"
        }
      ]
    }
  ],
  
  "total_count": 12,
  "current_week": 20,
  "card_types_included": ["baby_development", "user_moment", "pregnancy_tip"],
  
  "personalization_info": {
    "cards_personalized": 8,
    "personalization_factors": [
      "pregnancy_week",
      "family_engagement_patterns", 
      "previous_interactions",
      "milestone_proximity"
    ]
  },
  
  "interaction_summary": {
    "total_interactive_elements": 15,
    "conversation_starters": 4,
    "memory_book_opportunities": 6,
    "family_sharing_suggestions": 8
  },
  
  "generated_at": "2024-01-15T10:50:00Z"
}
```

---

## Implementation Notes

### Development Priority

1. **Phase 1: Core Enhanced Endpoints**
   - Enhanced family feed with real-time metadata
   - Improved reaction system with context
   - Basic WebSocket implementation

2. **Phase 2: Real-time Features**
   - Full WebSocket support
   - Server-Sent Events
   - Optimistic updates

3. **Phase 3: Advanced Features**
   - Comment threading
   - Story card enhancements  
   - Advanced caching

4. **Phase 4: Analytics & Optimization**
   - Performance monitoring
   - Advanced analytics
   - Machine learning insights

### Technology Stack Considerations

- **Real-time**: WebSocket with Redis for pub/sub
- **Caching**: Redis with intelligent invalidation
- **Database**: PostgreSQL with optimized indexes
- **Background Tasks**: Celery for async processing
- **Monitoring**: Prometheus + Grafana

### Security Considerations

- Rate limiting per endpoint and user
- Input validation on all requests
- CORS properly configured for WebSocket connections
- Audit logging for sensitive operations
- Data encryption for sensitive content

This specification provides a comprehensive foundation for implementing the enhanced feed system while maintaining backward compatibility with existing client applications.