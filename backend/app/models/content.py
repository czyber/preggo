from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User


class PostType(str, Enum):
    MILESTONE = "milestone"         # Major pregnancy milestones
    WEEKLY_UPDATE = "weekly_update"  # Regular pregnancy updates
    BELLY_PHOTO = "belly_photo"     # Progress photos
    ULTRASOUND = "ultrasound"       # Ultrasound images
    APPOINTMENT = "appointment"      # Appointment updates
    SYMPTOM_SHARE = "symptom_share"  # How I'm feeling
    CELEBRATION = "celebration"      # Happy moments
    QUESTION = "question"           # Ask family for advice
    ANNOUNCEMENT = "announcement"    # Big news
    MEMORY = "memory"               # Special memories
    PREPARATION = "preparation"      # Getting ready updates


class MoodType(str, Enum):
    EXCITED = "excited"
    NERVOUS = "nervous"
    HAPPY = "happy"
    TIRED = "tired"
    EMOTIONAL = "emotional"
    GRATEFUL = "grateful"
    UNCOMFORTABLE = "uncomfortable"
    PEACEFUL = "peaceful"


class VisibilityLevel(str, Enum):
    PRIVATE = "private"           # Only me
    PARTNER_ONLY = "partner_only"  # Me + partners
    IMMEDIATE = "immediate"       # Immediate family group
    EXTENDED = "extended"         # Extended family group
    FRIENDS = "friends"           # Friends group
    ALL_FAMILY = "all_family"     # All family groups
    CUSTOM = "custom"             # Custom selection


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ReactionType(str, Enum):
    """Enhanced pregnancy-specific reactions with 9 types"""
    # Primary reactions (core pregnancy emotions)
    LOVE = "love"           # ❤️ - General love and support
    EXCITED = "excited"     # 😍 - Excitement for milestones/moments
    SUPPORTIVE = "supportive"  # 🤗 - Caring, nurturing, being there
    STRONG = "strong"       # 💪 - Strength, encouragement, "you got this"
    BLESSED = "blessed"     # ✨ - Beautiful moments, feeling blessed
    
    # Additional reactions (extended emotions)
    HAPPY = "happy"         # 😂 - Joy, laughter, funny moments
    GRATEFUL = "grateful"   # 🙏 - Gratitude, prayers, thankfulness
    CELEBRATING = "celebrating"  # 🎉 - Celebrating achievements/milestones
    AMAZED = "amazed"       # 🌟 - Wonder, awe, amazement at development
    
    # Legacy mappings (for backwards compatibility)
    CARE = "supportive"     # Map old 'care' to 'supportive'
    SUPPORT = "strong"      # Map old 'support' to 'strong' 
    BEAUTIFUL = "blessed"   # Map old 'beautiful' to 'blessed'
    FUNNY = "happy"         # Map old 'funny' to 'happy'
    PRAYING = "grateful"    # Map old 'praying' to 'grateful'


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class PostContent(SQLModel):
    """Content structure for posts"""
    title: Optional[str] = None
    text: Optional[str] = None
    milestone_id: Optional[str] = None  # Milestone ID if related
    week: Optional[int] = None          # Pregnancy week
    mood: Optional[MoodType] = None
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class PostPrivacy(SQLModel):
    """Privacy settings for posts"""
    visibility: VisibilityLevel = VisibilityLevel.IMMEDIATE
    allowed_groups: List[str] = Field(default_factory=list)    # Which family groups can see
    allowed_members: Optional[List[str]] = None               # Specific members (override groups)
    allow_comments: bool = True
    allow_reactions: bool = True
    allow_downloads: bool = False    # For photos/videos
    hide_from_timeline: bool = False  # Don't show in main timeline


class MediaMetadata(SQLModel):
    """Metadata for media items"""
    width: Optional[int] = None
    height: Optional[int] = None
    device: Optional[str] = None
    camera: Optional[str] = None
    pregnancy_week: Optional[int] = None
    is_ultrasound: bool = False
    is_belly_photo: bool = False


class MediaItem(SQLModel, table=True):
    """Media items (photos, videos, audio) attached to posts"""
    __tablename__ = "media_items"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Media information
    type: MediaType = Field(description="Type of media")
    url: str = Field(description="URL to media file")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail URL for videos/large images")
    filename: str = Field(description="Original filename")
    size: int = Field(description="File size in bytes")
    duration: Optional[int] = Field(default=None, description="Duration in seconds for video/audio")
    
    # Media details
    caption: Optional[str] = Field(default=None, description="Media caption")
    taken_at: Optional[datetime] = Field(default=None, description="When media was captured")
    location: Optional[str] = Field(default=None, description="Where media was taken")
    order: int = Field(default=0, description="Order within post")
    
    # Metadata stored as JSONB
    media_metadata: MediaMetadata = Field(
        default_factory=MediaMetadata,
        sa_column=Column(JSON),
        description="Media metadata"
    )
    
    # References
    post_id: Optional[str] = Field(default=None, foreign_key="posts.id", description="Associated post")
    uploaded_by: str = Field(foreign_key="users.id", description="User who uploaded this media")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    """Main posts table for pregnancy updates and family sharing"""
    __tablename__ = "posts"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    author_id: str = Field(foreign_key="users.id", description="Post author")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Post information
    type: PostType = Field(description="Type of post")
    
    # Content stored as JSONB
    content: PostContent = Field(
        default_factory=PostContent,
        sa_column=Column(JSON),
        description="Post content and metadata"
    )
    
    # Privacy settings stored as JSONB
    privacy: PostPrivacy = Field(
        default_factory=PostPrivacy,
        sa_column=Column(JSON),
        description="Privacy and sharing settings"
    )
    
    # Post status and scheduling
    status: PostStatus = PostStatus.PUBLISHED
    scheduled_for: Optional[datetime] = Field(default=None, description="When to publish scheduled post")
    
    # Circle pattern tracking
    circle_pattern_id: Optional[str] = Field(default=None, foreign_key="circle_patterns.id", description="Circle pattern used for this post")
    pattern_was_suggested: bool = Field(default=False, description="Whether the pattern was AI-suggested")

    # Engagement counters (denormalized for performance)
    # ENHANCED FEATURES FOR OVERHAUL
    # Content integration with pregnancy content system
    integrated_content_id: Optional[str] = Field(
        default=None,
        foreign_key="pregnancy_content.id",
        description="Associated pregnancy content if post was inspired by content"
    )

    # Family warmth score (replacing traditional engagement metrics)
    family_warmth_score: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Calculated family warmth score"
    )

    # Memory book integration
    memory_book_eligible: bool = Field(
        default=False,
        description="Whether this post is eligible for memory book"
    )
    memory_book_priority: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Priority score for memory book inclusion"
    )

    # Celebration and milestone integration
    celebration_trigger_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Data for triggering celebrations or milestone recognition"
    )

    # Emotional intelligence and context
    emotional_context: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Detected emotional context for intelligent responses"
    )

    # Enhanced performance optimizations for Instagram-like feed
    reaction_summary: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Cached reaction counts by type for performance"
    )
    last_family_interaction: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last family member interaction"
    )
    trending_score: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Calculated trending score for feed prioritization"
    )

    # Traditional engagement counters (kept for gradual transition)
    reaction_count: int = Field(default=0, description="Total reaction count")
    comment_count: int = Field(default=0, description="Total comment count")
    view_count: int = Field(default=0, description="Total view count")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Reaction(SQLModel, table=True):
    """Reactions to posts and comments with Instagram-like enhancements"""
    __tablename__ = "reactions"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    user_id: str = Field(foreign_key="users.id", description="User who reacted")
    post_id: Optional[str] = Field(default=None, foreign_key="posts.id", description="Post being reacted to")
    comment_id: Optional[str] = Field(default=None, foreign_key="comments.id", description="Comment being reacted to")
    
    # Reaction details
    type: ReactionType = Field(description="Type of reaction")
    
    # ENHANCED FEATURES FOR INSTAGRAM-LIKE OVERHAUL
    intensity: int = Field(default=1, ge=1, le=3, description="Reaction strength (1-3)")
    custom_message: Optional[str] = Field(default=None, max_length=200, description="Personal note with reaction")
    is_milestone_reaction: bool = Field(default=False, description="Special milestone recognition")
    family_warmth_contribution: float = Field(default=0.0, ge=0.0, le=1.0, description="Contribution to family warmth score")

    # Client-side deduplication for optimistic updates
    client_id: Optional[str] = Field(default=None, description="Client-side ID for deduplication")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Ensure a user can only have one reaction per post/comment
        table_args = [
            {"extend_existing": True}
        ]


class Comment(SQLModel, table=True):
    """Enhanced comments on posts with threading support up to 5 levels deep"""
    __tablename__ = "comments"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: str = Field(foreign_key="posts.id", description="Post being commented on")
    user_id: str = Field(foreign_key="users.id", description="Comment author")
    parent_id: Optional[str] = Field(default=None, foreign_key="comments.id", description="Parent comment for threaded replies")
    
    # Threading support
    thread_depth: int = Field(default=0, ge=0, le=5, description="Depth in comment thread (0-5, 0 = root)")
    thread_path: str = Field(default="", description="Path from root comment (e.g., '1.2.3')")
    root_comment_id: Optional[str] = Field(default=None, foreign_key="comments.id", description="Root comment of this thread")
    
    # Comment content
    content: str = Field(max_length=2000, description="Comment text content (max 2000 chars)")
    mentions: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User IDs mentioned in comment (@mentions)"
    )
    mention_names: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Display names of mentioned users for frontend display"
    )
    
    # Enhanced comment features
    edited: bool = Field(default=False, description="Whether comment has been edited")
    edit_history: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Edit history for transparency"
    )
    
    # Engagement metrics
    reaction_count: int = Field(default=0, description="Number of reactions to this comment")
    reply_count: int = Field(default=0, description="Number of direct replies to this comment")
    total_descendant_count: int = Field(default=0, description="Total number of descendants in thread")
    
    # Real-time features
    is_typing_reply: bool = Field(default=False, description="Whether someone is currently typing a reply")
    last_typing_user: Optional[str] = Field(default=None, description="User ID of last person typing a reply")
    last_typing_at: Optional[datetime] = Field(default=None, description="When last typing activity occurred")
    
    # Performance and caching
    reaction_summary: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Cached reaction counts by type for performance"
    )
    
    # Family warmth integration
    family_warmth_contribution: float = Field(
        default=0.0, 
        ge=0.0, le=1.0,
        description="Contribution to overall family warmth score"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="comments")
    
    def get_next_thread_path(self, parent_reply_count: int) -> str:
        """Generate thread path for a new reply"""
        if self.thread_depth == 0:
            return str(parent_reply_count + 1)
        else:
            return f"{self.thread_path}.{parent_reply_count + 1}"
    
    def can_accept_replies(self) -> bool:
        """Check if comment can accept replies based on depth limit"""
        return self.thread_depth < 5


class PostView(SQLModel, table=True):
    """Track post views for analytics"""
    __tablename__ = "post_views"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: str = Field(foreign_key="posts.id", description="Post that was viewed")
    user_id: str = Field(foreign_key="users.id", description="User who viewed the post")
    
    # View details
    viewed_at: datetime = Field(default_factory=datetime.utcnow)
    time_spent: Optional[int] = Field(default=None, description="Time spent viewing in seconds")
    source: str = Field(default="timeline", description="How user accessed post (timeline, notification, direct_link)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PostShare(SQLModel, table=True):
    """Track post shares within the family network"""
    __tablename__ = "post_shares"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: str = Field(foreign_key="posts.id", description="Post that was shared")
    shared_by: str = Field(foreign_key="users.id", description="User who shared the post")
    
    # Share details
    shared_with: List[str] = Field(
        sa_column=Column(JSON),
        description="Group IDs or user IDs shared with"
    )
    message: Optional[str] = Field(default=None, description="Message included with share")
    method: str = Field(default="internal", description="How post was shared (internal, email, link)")
    
    # Timestamps
    shared_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FeedActivity(SQLModel, table=True):
    """Real-time activity tracking for Instagram-like feed features"""
    __tablename__ = "feed_activities"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )

    # References
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Pregnancy this activity relates to")
    user_id: str = Field(foreign_key="users.id", description="User who performed the activity")

    # Activity details
    activity_type: str = Field(description="Type of activity (reaction, comment, view, share, post_create)")
    target_id: str = Field(description="ID of target (post_id, comment_id, etc.)")
    target_type: str = Field(description="Type of target (post, comment, etc.)")

    # Activity data stored as JSONB for flexibility
    activity_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Detailed activity data (reaction_type, comment_text, etc.)"
    )

    # Real-time broadcasting control
    broadcast_to_family: bool = Field(default=True, description="Whether to broadcast this activity to family members")
    broadcast_priority: int = Field(default=1, ge=1, le=5, description="Broadcasting priority (1=low, 5=urgent)")

    # Performance tracking
    client_timestamp: Optional[datetime] = Field(default=None, description="Client-side timestamp for latency calculation")
    processed_at: Optional[datetime] = Field(default=None, description="When activity was processed by background jobs")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# ENHANCED CONTENT SYSTEM FOR PREGGO APP OVERHAUL
# =============================================================================

class ContentType(str, Enum):
    """Types of pregnancy content"""
    WEEKLY_TIP = "weekly_tip"
    BABY_DEVELOPMENT = "baby_development"
    HEALTH_WELLNESS = "health_wellness"
    EMOTIONAL_SUPPORT = "emotional_support"
    PREPARATION = "preparation"
    PARTNER_FAMILY = "partner_family"
    MILESTONE_CELEBRATION = "milestone_celebration"
    SELF_CARE = "self_care"
    LOOKING_AHEAD = "looking_ahead"
    SYMPTOM_SUPPORT = "symptom_support"
    DECISION_SUPPORT = "decision_support"


class ContentDeliveryMethod(str, Enum):
    """How content is delivered to users"""
    FEED_INTEGRATION = "feed_integration"
    PUSH_NOTIFICATION = "push_notification"
    EMAIL_DIGEST = "email_digest"
    ON_DEMAND = "on_demand"
    MILESTONE_TRIGGER = "milestone_trigger"


class MedicalReviewStatus(str, Enum):
    """Medical review status for health content"""
    PENDING = "pending"
    APPROVED = "approved"
    REQUIRES_REVISION = "requires_revision"
    REJECTED = "rejected"
    EXPIRED = "expired"  # Needs re-review due to guideline changes


class PersonalizationContext(SQLModel):
    """Context for personalizing content delivery"""
    pregnancy_week: int = Field(ge=1, le=42)
    trimester: int = Field(ge=1, le=3)
    is_high_risk: bool = False
    is_multiple_pregnancy: bool = False
    first_time_parent: bool = True
    preferred_detail_level: str = "standard"  # minimal, standard, detailed
    cultural_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    emotional_state: Optional[str] = None  # anxious, excited, tired, etc.
    time_of_day: Optional[str] = None  # morning, afternoon, evening


class ContentCategory(SQLModel, table=True):
    """Categories for organizing pregnancy content"""
    __tablename__ = "content_categories"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = Field(max_length=100, description="Category name")
    slug: str = Field(max_length=100, unique=True, description="URL-friendly category identifier")
    description: Optional[str] = Field(default=None, description="Category description")
    icon_name: Optional[str] = Field(default=None, max_length=50, description="Icon identifier")
    color_hex: Optional[str] = Field(default=None, max_length=7, description="Category color")
    sort_order: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Whether category is active")

    # Metadata
    parent_category_id: Optional[str] = Field(
        default=None,
        foreign_key="content_categories.id",
        description="Parent category for hierarchical organization"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PregnancyContent(SQLModel, table=True):
    """Comprehensive pregnancy content system"""
    __tablename__ = "pregnancy_content"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )

    # Content classification
    category_id: Optional[str] = Field(
        default=None,
        foreign_key="content_categories.id",
        description="Content category"
    )
    content_type: ContentType = Field(description="Type of content")

    # Content targeting
    week_number: Optional[int] = Field(
        default=None,
        ge=1, le=42,
        description="Target pregnancy week (null for cross-week content)"
    )
    trimester: Optional[int] = Field(
        default=None,
        ge=1, le=3,
        description="Target trimester (null for all trimesters)"
    )

    # Content details
    title: str = Field(max_length=200, description="Content title")
    subtitle: Optional[str] = Field(default=None, max_length=300, description="Content subtitle")
    content_body: str = Field(description="Main content body in Markdown")
    content_summary: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Brief summary for cards and notifications"
    )

    # Content metadata
    reading_time_minutes: Optional[int] = Field(
        default=None,
        description="Estimated reading time"
    )
    priority: int = Field(default=0, description="Content priority (higher numbers = higher priority)")
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Content tags for filtering and search"
    )

    # Media and resources
    featured_image: Optional[str] = Field(default=None, description="Featured image URL")
    media_urls: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Associated media files (images, videos, audio)"
    )
    external_links: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="External resource links"
    )

    # Personalization rules
    personalization_rules: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Rules for content personalization and delivery"
    )
    target_audience: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Target audience tags (first_time_parent, high_risk, etc.)"
    )

    # Medical review and quality assurance
    medical_review_status: MedicalReviewStatus = Field(
        default=MedicalReviewStatus.PENDING,
        description="Medical review status"
    )
    medical_reviewer_id: Optional[str] = Field(
        default=None,
        foreign_key="users.id",
        description="Healthcare provider who reviewed content"
    )
    reviewed_at: Optional[datetime] = Field(
        default=None,
        description="When content was medically reviewed"
    )
    review_notes: Optional[str] = Field(
        default=None,
        description="Medical reviewer notes"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When content needs re-review"
    )

    # Content delivery
    delivery_methods: List[ContentDeliveryMethod] = Field(
        default_factory=lambda: [ContentDeliveryMethod.FEED_INTEGRATION],
        sa_column=Column(JSON),
        description="How this content can be delivered"
    )
    optimal_delivery_time: Optional[str] = Field(
        default=None,
        description="Optimal time of day for delivery (HH:MM)"
    )

    # Status and versioning
    is_active: bool = Field(default=True, description="Whether content is active")
    version: int = Field(default=1, description="Content version number")
    parent_content_id: Optional[str] = Field(
        default=None,
        foreign_key="pregnancy_content.id",
        description="Parent content if this is a revision"
    )

    # Analytics and engagement
    view_count: int = Field(default=0, description="Number of times content was viewed")
    helpful_count: int = Field(default=0, description="Number of 'helpful' reactions")
    not_helpful_count: int = Field(default=0, description="Number of 'not helpful' reactions")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(
        default=None,
        description="When content was published"
    )
