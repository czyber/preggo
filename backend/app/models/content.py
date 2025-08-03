from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime
import uuid
from enum import Enum


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
    LOVE = "love"           # ❤️
    EXCITED = "excited"     # 😍
    CARE = "care"           # 🤗
    SUPPORT = "support"     # 💪
    BEAUTIFUL = "beautiful"  # ✨
    FUNNY = "funny"         # 😂
    PRAYING = "praying"     # 🙏


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
    
    # Engagement counters (denormalized for performance)
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
    """Reactions to posts and comments"""
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
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Ensure a user can only have one reaction per post/comment
        table_args = [
            {"extend_existing": True}
        ]


class Comment(SQLModel, table=True):
    """Comments on posts"""
    __tablename__ = "comments"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: str = Field(foreign_key="posts.id", description="Post being commented on")
    user_id: str = Field(foreign_key="users.id", description="Comment author")
    parent_id: Optional[str] = Field(default=None, foreign_key="comments.id", description="Parent comment for threaded replies")
    
    # Comment content
    content: str = Field(description="Comment text content")
    mentions: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User IDs mentioned in comment"
    )
    
    # Comment metadata
    edited: bool = Field(default=False, description="Whether comment has been edited")
    reaction_count: int = Field(default=0, description="Number of reactions to this comment")
    reply_count: int = Field(default=0, description="Number of replies to this comment")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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