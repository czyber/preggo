"""
Enhanced content models for Preggo app overhaul.
This module contains the additional content system models including:
- Baby development content with creative size comparisons
- User content preferences and personalization
- Family warmth system (replacing traditional engagement metrics)  
- Memory book system for automatic curation and family collaboration
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column
from datetime import datetime
import uuid
from enum import Enum


class BabyDevelopmentContent(SQLModel, table=True):
    """Specific baby development information with creative comparisons"""
    __tablename__ = "baby_development_content"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Week targeting
    week_number: int = Field(ge=1, le=42, description="Pregnancy week")
    
    # Size information
    length_mm: Optional[float] = Field(default=None, description="Baby length in millimeters")
    weight_grams: Optional[float] = Field(default=None, description="Baby weight in grams")
    
    # Creative size comparisons (moving beyond fruits)
    size_comparison: str = Field(description="Creative size comparison")
    size_comparison_category: str = Field(
        description="Category of comparison (everyday_object, food, household_item)"
    )
    alternative_comparisons: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Alternative size comparisons for variety"
    )
    
    # Development highlights
    major_developments: List[str] = Field(
        sa_column=Column(JSON),
        description="Key developments happening this week"
    )
    sensory_developments: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="What baby can sense/experience"
    )
    body_system_developments: Dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Development by body system (brain, heart, lungs, etc.)"
    )
    
    # Connection and bonding information
    amazing_fact: str = Field(description="Wonder-inducing development fact")
    connection_moment: str = Field(description="How parents can connect with this development")
    what_baby_can_do: str = Field(description="Baby's capabilities at this stage")
    
    # Family engagement suggestions
    bonding_activities: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Activities families can do based on development"
    )
    conversation_starters: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Ways to involve family in discussing development"
    )
    
    # Visual content
    illustration_url: Optional[str] = Field(
        default=None,
        description="URL to development illustration"
    )
    size_comparison_image: Optional[str] = Field(
        default=None,
        description="URL to size comparison image"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentDeliveryMethod(str, Enum):
    """How content is delivered to users"""
    FEED_INTEGRATION = "feed_integration"
    PUSH_NOTIFICATION = "push_notification"
    EMAIL_DIGEST = "email_digest"
    ON_DEMAND = "on_demand"
    MILESTONE_TRIGGER = "milestone_trigger"


class UserContentPreferences(SQLModel, table=True):
    """User preferences for content personalization"""
    __tablename__ = "user_content_preferences"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # User and pregnancy context
    user_id: str = Field(foreign_key="users.id", description="User ID")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Content delivery preferences
    content_frequency: str = Field(
        default="daily",
        description="How often to receive content (daily, weekly, minimal)"
    )
    preferred_delivery_time: str = Field(
        default="09:00",
        description="Preferred time for content delivery (HH:MM)"
    )
    delivery_methods: List[ContentDeliveryMethod] = Field(
        default_factory=lambda: [ContentDeliveryMethod.FEED_INTEGRATION],
        sa_column=Column(JSON),
        description="Preferred delivery methods"
    )
    
    # Content preferences
    preferred_categories: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Preferred content category IDs"
    )
    blocked_categories: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Categories user doesn't want to see"
    )
    
    # Personalization settings
    detail_level: str = Field(
        default="standard",
        description="Preferred content detail level (minimal, standard, detailed)"
    )
    emotional_tone: str = Field(
        default="warm",
        description="Preferred emotional tone (clinical, warm, casual)"
    )
    medical_info_level: str = Field(
        default="balanced",
        description="Medical information preference (minimal, balanced, comprehensive)"
    )
    
    # Cultural and personal context
    cultural_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Cultural adaptations and preferences"
    )
    language_preference: str = Field(
        default="en",
        description="Preferred language for content"
    )
    
    # Family involvement preferences
    family_sharing_level: str = Field(
        default="moderate",
        description="How much to encourage family sharing (minimal, moderate, high)"
    )
    partner_involvement_level: str = Field(
        default="high",
        description="Level of partner-focused content (low, moderate, high)"
    )
    
    # Learning and adaptation
    interaction_patterns: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Learned patterns from user interactions"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentDeliveryLog(SQLModel, table=True):
    """Track content delivery and engagement"""
    __tablename__ = "content_delivery_log"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    user_id: str = Field(foreign_key="users.id", description="User who received content")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    content_id: str = Field(foreign_key="pregnancy_content.id", description="Delivered content")
    
    # Delivery details
    delivery_method: ContentDeliveryMethod = Field(description="How content was delivered")
    delivery_context: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Context when content was delivered (mood, time, etc.)"
    )
    
    # Engagement tracking
    delivered_at: datetime = Field(default_factory=datetime.utcnow)
    first_viewed_at: Optional[datetime] = Field(default=None)
    last_viewed_at: Optional[datetime] = Field(default=None)
    total_view_time_seconds: int = Field(default=0)
    view_count: int = Field(default=0)
    
    # User feedback
    reaction: Optional[str] = Field(
        default=None,
        description="User reaction (helpful, not_helpful, saved, shared)"
    )
    rating: Optional[int] = Field(
        default=None,
        ge=1, le=5,
        description="User rating if provided"
    )
    feedback_text: Optional[str] = Field(
        default=None,
        description="User feedback text"
    )
    
    # Action tracking
    shared_with_family: bool = Field(default=False)
    added_to_memory_book: bool = Field(default=False)
    triggered_follow_up: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# FAMILY WARMTH SYSTEM (REPLACING ENGAGEMENT METRICS)
# =============================================================================

class FamilyWarmthType(str, Enum):
    """Types of family warmth interactions"""
    EMOTIONAL_SUPPORT = "emotional_support"  # Comments with care/encouragement
    CELEBRATION = "celebration"  # Celebrating milestones/achievements
    PRACTICAL_HELP = "practical_help"  # Offering help or resources
    MEMORY_SHARING = "memory_sharing"  # Contributing to memories
    ANTICIPATION = "anticipation"  # Excitement for future moments
    REASSURANCE = "reassurance"  # Providing comfort during concerns
    INCLUSION = "inclusion"  # Including extended family/friends


class FamilyWarmthScore(SQLModel):
    """Calculated warmth score components"""
    immediate_family_score: float = Field(default=0.0, description="Immediate family warmth (0-1)")
    extended_family_score: float = Field(default=0.0, description="Extended family warmth (0-1)")
    recent_engagement_score: float = Field(default=0.0, description="Recent activity warmth (0-1)")
    emotional_support_score: float = Field(default=0.0, description="Quality of emotional support (0-1)")
    overall_warmth_score: float = Field(default=0.0, description="Composite warmth score (0-1)")
    warmth_trend: str = Field(default="stable", description="Trend: increasing, stable, decreasing")


class FamilyInteraction(SQLModel, table=True):
    """Track family interactions for warmth calculation"""
    __tablename__ = "family_interactions"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: Optional[str] = Field(
        default=None,
        foreign_key="posts.id",
        description="Associated post"
    )
    pregnancy_id: str = Field(
        foreign_key="pregnancies.id",
        description="Associated pregnancy"
    )
    user_id: str = Field(
        foreign_key="users.id",
        description="User who interacted"
    )
    
    # Interaction details
    interaction_type: FamilyWarmthType = Field(description="Type of warm interaction")
    interaction_content: str = Field(description="Content of interaction (comment text, etc.)")
    
    # Context and analysis
    emotional_sentiment: Optional[str] = Field(
        default=None,
        description="Detected sentiment (positive, supportive, celebratory, etc.)"
    )
    warmth_intensity: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Intensity of warmth in this interaction"
    )
    
    # Family relationship context
    relationship_to_pregnant_person: str = Field(
        description="Relationship (partner, mother, sister, friend, etc.)"
    )
    family_group_level: str = Field(
        description="Family group (immediate, extended, friends)"
    )
    
    # Timing and recency
    interaction_at: datetime = Field(default_factory=datetime.utcnow)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FamilyWarmthCalculation(SQLModel, table=True):
    """Calculated family warmth scores for posts/pregnancies"""
    __tablename__ = "family_warmth_calculations"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    post_id: Optional[str] = Field(
        default=None,
        foreign_key="posts.id",
        description="Associated post (for post-level warmth)"
    )
    pregnancy_id: str = Field(
        foreign_key="pregnancies.id",
        description="Associated pregnancy (for overall warmth)"
    )
    
    # Calculated scores
    warmth_scores: FamilyWarmthScore = Field(
        sa_column=Column(JSON),
        description="Detailed warmth score breakdown"
    )
    
    # Calculation metadata
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    total_interactions: int = Field(default=0)
    active_family_members: int = Field(default=0)
    calculation_period_days: int = Field(default=7, description="Period analyzed for calculation")
    
    # Insights for family
    warmth_insights: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Generated insights about family support patterns"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MEMORY BOOK SYSTEM
# =============================================================================

class MemoryType(str, Enum):
    """Types of memories in the memory book"""
    MILESTONE_MOMENT = "milestone_moment"
    WEEKLY_HIGHLIGHT = "weekly_highlight"
    FAMILY_CONTRIBUTION = "family_contribution"
    ULTRASOUND_MEMORY = "ultrasound_memory"
    BELLY_PHOTO_SERIES = "belly_photo_series"
    PREPARATION_MEMORY = "preparation_memory"
    EMOTIONAL_MOMENT = "emotional_moment"
    CELEBRATION_MEMORY = "celebration_memory"
    SURPRISE_MOMENT = "surprise_moment"
    AUTO_CURATED = "auto_curated"


class MemoryBookItem(SQLModel, table=True):
    """Individual items in the pregnancy memory book"""
    __tablename__ = "memory_book_items"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    pregnancy_id: str = Field(
        foreign_key="pregnancies.id",
        description="Associated pregnancy"
    )
    source_post_id: Optional[str] = Field(
        default=None,
        foreign_key="posts.id",
        description="Source post if memory comes from a post"
    )
    created_by_user_id: str = Field(
        foreign_key="users.id",
        description="User who created or triggered this memory"
    )
    
    # Memory details
    memory_type: MemoryType = Field(description="Type of memory")
    title: str = Field(description="Memory title")
    description: str = Field(description="Memory description")
    
    # Content
    content: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Memory content (text, images, etc.)"
    )
    media_items: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Associated media item IDs"
    )
    
    # Context
    pregnancy_week: Optional[int] = Field(
        default=None,
        ge=1, le=42,
        description="Pregnancy week when memory occurred"
    )
    memory_date: datetime = Field(
        description="When the memory occurred (not when it was created)"
    )
    
    # Family collaboration
    family_contributions: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Family member contributions to this memory"
    )
    collaborative: bool = Field(
        default=False,
        description="Whether family members can contribute to this memory"
    )
    
    # Curation and automation
    auto_generated: bool = Field(
        default=False,
        description="Whether this memory was auto-curated"
    )
    curation_score: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="AI curation confidence score"
    )
    curation_reasons: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Why this was selected as a memory"
    )
    
    # Organization
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Memory tags for organization"
    )
    is_favorite: bool = Field(default=False)
    is_private: bool = Field(default=False, description="Private to pregnant person only")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryCollection(SQLModel, table=True):
    """Collections of related memories"""
    __tablename__ = "memory_collections"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    pregnancy_id: str = Field(
        foreign_key="pregnancies.id",
        description="Associated pregnancy"
    )
    created_by_user_id: str = Field(
        foreign_key="users.id",
        description="User who created this collection"
    )
    
    # Collection details
    title: str = Field(description="Collection title")
    description: Optional[str] = Field(default=None, description="Collection description")
    collection_type: str = Field(description="Type: weekly, monthly, trimester, milestone, custom")
    
    # Collection content
    memory_item_ids: List[str] = Field(
        sa_column=Column(JSON),
        description="Memory item IDs in this collection"
    )
    
    # Time period
    start_week: Optional[int] = Field(default=None, ge=1, le=42)
    end_week: Optional[int] = Field(default=None, ge=1, le=42)
    
    # Sharing and collaboration
    is_shared: bool = Field(default=False)
    shared_with: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User IDs this collection is shared with"
    )
    
    # Auto-generation
    auto_generated: bool = Field(default=False)
    generation_schedule: Optional[str] = Field(
        default=None,
        description="Schedule for auto-generating (weekly, monthly, etc.)"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FamilyMemoryContribution(SQLModel, table=True):
    """Family member contributions to memories"""
    __tablename__ = "family_memory_contributions"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # References
    memory_item_id: str = Field(
        foreign_key="memory_book_items.id",
        description="Memory being contributed to"
    )
    contributor_user_id: str = Field(
        foreign_key="users.id",
        description="Family member making contribution"
    )
    
    # Contribution details
    contribution_type: str = Field(
        description="Type: comment, photo, story, reaction, well_wish"
    )
    content: str = Field(description="Contribution content")
    
    # Media attachments
    media_items: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Media items attached to contribution"
    )
    
    # Relationship context
    relationship_to_pregnant_person: str = Field(
        description="Contributor's relationship"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# ENHANCED POST MODELS (EXTENDING EXISTING CONTENT MODELS)
# =============================================================================

class PregnancyContext(SQLModel):
    """Pregnancy context for posts and content"""
    week_number: int = Field(ge=1, le=42)
    trimester: int = Field(ge=1, le=3)
    is_milestone_week: bool = False
    development_highlight: Optional[str] = None
    size_comparison: Optional[str] = None
    preparation_focus: Optional[str] = None


class EmotionalContext(SQLModel):
    """Emotional context for intelligent content delivery"""
    detected_mood: Optional[str] = None  # anxious, excited, tired, grateful, etc.
    support_level_needed: int = Field(default=1, ge=1, le=5)  # 1-5 scale
    celebration_worthy: bool = False
    family_response_suggested: bool = False
    emotional_intensity: float = Field(default=0.5, ge=0.0, le=1.0)


class CelebrationData(SQLModel):
    """Data for milestone and achievement celebrations"""
    celebration_type: str  # milestone, achievement, surprise, family_moment
    celebration_message: str
    suggested_family_actions: List[str] = Field(default_factory=list)
    celebration_media: List[str] = Field(default_factory=list)
    involves_extended_family: bool = False


class MemoryBookData(SQLModel):
    """Data for memory book integration"""
    auto_save_eligible: bool = False
    memory_priority: float = Field(default=0.0, ge=0.0, le=1.0)
    memory_categories: List[str] = Field(default_factory=list)
    family_collaboration_suggested: bool = False
    memory_prompt: Optional[str] = None