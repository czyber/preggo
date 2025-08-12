from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime
import uuid
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.pregnancy import Pregnancy
    from app.models.content import Post, PostType
    from app.models.family import GroupType


class PatternSuggestionSource(str, Enum):
    """Source types for pattern suggestions"""
    CONTENT_ANALYSIS = "content_analysis"
    HISTORICAL_PATTERN = "historical_pattern"
    POST_TYPE = "post_type"
    TIME_CONTEXT = "time_context"
    USER_BEHAVIOR = "user_behavior"
    AI_RECOMMENDATION = "ai_recommendation"


class PatternConfiguration(SQLModel):
    """Configuration data for circle patterns"""
    # Groups that should be included when using this pattern
    included_groups: List[str] = Field(default_factory=list, description="GroupType enum values")
    
    # Specific visibility level if different from groups
    visibility_level: Optional[str] = Field(default=None, description="VisibilityLevel enum value")
    
    # Privacy settings for posts using this pattern
    allow_comments: bool = Field(default=True)
    allow_reactions: bool = Field(default=True)
    allow_downloads: bool = Field(default=False)
    
    # Suggested post types for this pattern
    suggested_for: List[str] = Field(default_factory=list, description="PostType enum values")
    
    # Auto-inclusion rules
    auto_include_new_content: bool = Field(default=False)
    notify_members_on_use: bool = Field(default=True)


class UserPatternPreferences(SQLModel):
    """User-specific preferences for a circle pattern"""
    # Custom name override
    custom_name: Optional[str] = Field(default=None)
    custom_icon: Optional[str] = Field(default=None)
    custom_description: Optional[str] = Field(default=None)
    
    # Usage preferences
    is_favorite: bool = Field(default=False)
    is_enabled: bool = Field(default=True)
    sort_order: int = Field(default=0)
    
    # Notification preferences for this pattern
    notify_on_suggestions: bool = Field(default=True)
    auto_select_for_types: List[str] = Field(default_factory=list, description="PostType enum values")


class SuggestionContext(SQLModel):
    """Context data for pattern suggestions"""
    # Content analysis results
    content_keywords: List[str] = Field(default_factory=list)
    detected_mood: Optional[str] = Field(default=None)
    pregnancy_week: Optional[int] = Field(default=None)
    
    # Historical data
    similar_posts_count: int = Field(default=0)
    user_pattern_history: Dict[str, int] = Field(default_factory=dict)
    
    # Timing context
    time_of_day: Optional[str] = Field(default=None)
    day_of_week: Optional[str] = Field(default=None)
    
    # Engagement predictions
    predicted_engagement: Optional[float] = Field(default=None)
    expected_reach: Optional[int] = Field(default=None)


class CirclePattern(SQLModel, table=True):
    """Core circle patterns that define sharing combinations"""
    __tablename__ = "circle_patterns"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Pattern identification
    name: str = Field(description="Pattern name (e.g., 'Just Us', 'Close Family')")
    icon: str = Field(description="Emoji or icon identifier")
    description: str = Field(description="Description of who sees content with this pattern")
    
    # Pattern type and source
    is_system_default: bool = Field(default=False, description="Whether this is a system-provided pattern")
    is_global: bool = Field(default=False, description="Whether this pattern is available to all users")
    created_by: Optional[str] = Field(default=None, foreign_key="users.id", description="User who created this pattern")
    
    # Pattern configuration stored as JSONB
    configuration: PatternConfiguration = Field(
        default_factory=PatternConfiguration,
        sa_column=Column(JSON),
        description="Pattern configuration and rules"
    )
    
    # Usage statistics (denormalized for performance)
    total_usage_count: int = Field(default=0, description="Total times this pattern has been used")
    unique_users_count: int = Field(default=0, description="Number of unique users who have used this pattern")
    average_engagement: float = Field(default=0.0, description="Average engagement rate for posts using this pattern")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCirclePattern(SQLModel, table=True):
    """User-specific circle pattern preferences and customizations"""
    __tablename__ = "user_circle_patterns"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="User who owns this pattern preference")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    pattern_id: str = Field(foreign_key="circle_patterns.id", description="Base circle pattern")
    
    # User customizations stored as JSONB
    preferences: UserPatternPreferences = Field(
        default_factory=UserPatternPreferences,
        sa_column=Column(JSON),
        description="User-specific pattern preferences"
    )
    
    # Pattern override configuration (if user customized the pattern)
    custom_configuration: Optional[PatternConfiguration] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Custom configuration overrides"
    )
    
    # Usage statistics for this user
    usage_count: int = Field(default=0, description="How many times user has used this pattern")
    last_used_at: Optional[datetime] = Field(default=None, description="When pattern was last used")
    average_engagement: float = Field(default=0.0, description="User's average engagement with this pattern")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CirclePatternUsage(SQLModel, table=True):
    """Analytics and learning data for circle pattern usage"""
    __tablename__ = "circle_pattern_usage"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="User who used the pattern")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    pattern_id: str = Field(foreign_key="circle_patterns.id", description="Pattern that was used")
    post_id: str = Field(foreign_key="posts.id", description="Post that used this pattern")
    
    # Usage context
    post_type: str = Field(description="Type of post that used this pattern")
    was_suggested: bool = Field(default=False, description="Whether this pattern was AI-suggested")
    suggestion_confidence: Optional[float] = Field(default=None, description="AI suggestion confidence if applicable")
    user_modified: bool = Field(default=False, description="Whether user modified the suggested pattern")
    
    # Engagement results (populated after post goes live)
    final_reach: Optional[int] = Field(default=None, description="Final number of family members who saw the post")
    engagement_rate: Optional[float] = Field(default=None, description="Engagement rate for this usage")
    reaction_count: Optional[int] = Field(default=None, description="Number of reactions received")
    comment_count: Optional[int] = Field(default=None, description="Number of comments received")
    
    # Learning data stored as JSONB
    context_data: Optional[SuggestionContext] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Context data for learning algorithms"
    )
    
    # Timestamps
    used_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PatternSuggestion(SQLModel, table=True):
    """AI-generated pattern suggestions for posts"""
    __tablename__ = "pattern_suggestions"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="User receiving the suggestion")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    pattern_id: str = Field(foreign_key="circle_patterns.id", description="Suggested pattern")
    post_id: Optional[str] = Field(default=None, foreign_key="posts.id", description="Post this suggestion was for")
    
    # Suggestion details
    confidence_score: float = Field(ge=0.0, le=1.0, description="AI confidence in this suggestion (0-1)")
    reasoning: str = Field(description="Human-readable explanation for the suggestion")
    source: PatternSuggestionSource = Field(description="What algorithm/data source generated this suggestion")
    
    # Suggestion context stored as JSONB
    context: SuggestionContext = Field(
        default_factory=SuggestionContext,
        sa_column=Column(JSON),
        description="Context data that led to this suggestion"
    )
    
    # User response tracking
    was_shown: bool = Field(default=False, description="Whether this suggestion was shown to the user")
    was_accepted: Optional[bool] = Field(default=None, description="Whether user accepted the suggestion")
    user_feedback: Optional[str] = Field(default=None, description="User feedback on the suggestion")
    
    # Performance tracking
    shown_at: Optional[datetime] = Field(default=None, description="When suggestion was shown to user")
    responded_at: Optional[datetime] = Field(default=None, description="When user responded to suggestion")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Create system default patterns as constants for seeding
SYSTEM_DEFAULT_PATTERNS = [
    {
        "id": "just-us",
        "name": "Just Us",
        "icon": "💕",
        "description": "You and your partner",
        "is_system_default": True,
        "is_global": True,
        "configuration": PatternConfiguration(
            included_groups=[],
            visibility_level="PARTNER_ONLY",
            suggested_for=["SYMPTOM_SHARE", "PREPARATION"],
            allow_comments=True,
            allow_reactions=True,
            allow_downloads=False
        )
    },
    {
        "id": "close-family", 
        "name": "Close Family",
        "icon": "👨‍👩‍👧‍👦",
        "description": "Parents, siblings, and partner",
        "is_system_default": True,
        "is_global": True,
        "configuration": PatternConfiguration(
            included_groups=["IMMEDIATE_FAMILY"],
            visibility_level="IMMEDIATE",
            suggested_for=["ULTRASOUND", "MILESTONE"],
            allow_comments=True,
            allow_reactions=True,
            allow_downloads=False
        )
    },
    {
        "id": "everyone",
        "name": "Everyone", 
        "icon": "🌟",
        "description": "All your family and friends",
        "is_system_default": True,
        "is_global": True,
        "configuration": PatternConfiguration(
            included_groups=["IMMEDIATE_FAMILY", "EXTENDED_FAMILY", "FRIENDS"],
            visibility_level="ALL_FAMILY",
            suggested_for=["ANNOUNCEMENT", "CELEBRATION"],
            allow_comments=True,
            allow_reactions=True,
            allow_downloads=False
        )
    },
    {
        "id": "grandparents",
        "name": "Grandparents Circle",
        "icon": "👴👵", 
        "description": "Extended family including grandparents",
        "is_system_default": True,
        "is_global": True,
        "configuration": PatternConfiguration(
            included_groups=["IMMEDIATE_FAMILY", "EXTENDED_FAMILY"],
            visibility_level="EXTENDED",
            suggested_for=["WEEKLY_UPDATE", "BELLY_PHOTO"],
            allow_comments=True,
            allow_reactions=True,
            allow_downloads=False
        )
    },
    {
        "id": "friends-support",
        "name": "Friend Support",
        "icon": "🤗",
        "description": "Close friends and support network", 
        "is_system_default": True,
        "is_global": True,
        "configuration": PatternConfiguration(
            included_groups=["FRIENDS", "SUPPORT_CIRCLE"],
            visibility_level="FRIENDS",
            suggested_for=["QUESTION", "MEMORY"],
            allow_comments=True,
            allow_reactions=True,
            allow_downloads=False
        )
    }
]