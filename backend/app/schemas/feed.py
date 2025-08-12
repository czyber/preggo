from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import base64
import json

from app.models.content import ReactionType
from app.schemas.content import PostResponse


class PregnancyReactionType(str, Enum):
    """Enhanced pregnancy-specific reactions matching the 9 core types"""
    # Primary reactions (core pregnancy emotions)
    LOVE = "love"           # ❤️ General love and support
    EXCITED = "excited"     # 😍 Excitement for milestones/moments
    SUPPORTIVE = "supportive"  # 🤗 Caring, nurturing, being there
    STRONG = "strong"       # 💪 Strength, encouragement, "you got this"
    BLESSED = "blessed"     # ✨ Beautiful moments, feeling blessed
    
    # Additional reactions (extended emotions)
    HAPPY = "happy"         # 😂 Joy, laughter, funny moments
    GRATEFUL = "grateful"   # 🙏 Gratitude, prayers, thankfulness
    CELEBRATING = "celebrating"  # 🎉 Celebrating achievements/milestones
    AMAZED = "amazed"       # 🌟 Wonder, awe, amazement at development


class FeedFilterType(str, Enum):
    """Available feed filter types"""
    ALL = "all"
    MILESTONES = "milestones"
    PHOTOS = "photos"
    UPDATES = "updates"
    CELEBRATIONS = "celebrations"
    QUESTIONS = "questions"
    RECENT = "recent"
    TRENDING = "trending"


class FeedSortType(str, Enum):
    """Feed sorting options"""
    CHRONOLOGICAL = "chronological"    # Most recent first
    ENGAGEMENT = "engagement"          # Most engaging first
    FAMILY_PRIORITY = "family_priority"  # Family member priority
    MILESTONE_FIRST = "milestone_first"  # Milestone posts first


class FeedCursor(BaseModel):
    """Cursor for pagination in Instagram-like feed"""
    timestamp: datetime = Field(description="Timestamp of the last item")
    id: str = Field(description="ID of the last item for tie-breaking")
    score: Optional[float] = Field(default=None, description="Score of the last item (for ranking-based feeds)")
    
    def encode(self) -> str:
        """Encode cursor to base64 string for URL safety"""
        cursor_data = {
            "timestamp": self.timestamp.isoformat(),
            "id": self.id,
            "score": self.score
        }
        cursor_json = json.dumps(cursor_data, sort_keys=True)
        return base64.b64encode(cursor_json.encode()).decode()
    
    @classmethod
    def decode(cls, cursor_str: str) -> "FeedCursor":
        """Decode cursor from base64 string"""
        try:
            cursor_json = base64.b64decode(cursor_str.encode()).decode()
            cursor_data = json.loads(cursor_json)
            return cls(
                timestamp=datetime.fromisoformat(cursor_data["timestamp"]),
                id=cursor_data["id"],
                score=cursor_data.get("score")
            )
        except Exception as e:
            raise ValueError(f"Invalid cursor format: {e}")


class FeedRequest(BaseModel):
    """Enhanced request parameters for Instagram-like feed queries"""
    limit: int = Field(default=20, ge=1, le=50, description="Number of posts to return (reduced max for performance)")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination (replaces offset)")
    offset: Optional[int] = Field(default=0, ge=0, description="Offset for personal timeline pagination (legacy)")
    filter_type: FeedFilterType = Field(default=FeedFilterType.ALL, description="Type of content to show")
    sort_by: FeedSortType = Field(default=FeedSortType.CHRONOLOGICAL, description="How to sort the feed")
    include_reactions: bool = Field(default=True, description="Include reaction counts and types")
    include_comments: bool = Field(default=True, description="Include comment previews")
    include_media: bool = Field(default=True, description="Include media metadata")
    include_content: bool = Field(default=False, description="Include integrated pregnancy content")
    include_warmth: bool = Field(default=True, description="Include family warmth visualizations")
    real_time: bool = Field(default=False, description="Enable real-time updates via WebSocket upgrade")
    since: Optional[datetime] = Field(default=None, description="Only show posts after this timestamp")


class ReactionSummary(BaseModel):
    """Summary of reactions on a post"""
    total_count: int = Field(description="Total number of reactions")
    reaction_counts: Dict[ReactionType, int] = Field(description="Count by reaction type")
    user_reaction: Optional[ReactionType] = Field(default=None, description="Current user's reaction")
    recent_reactors: List[str] = Field(description="User IDs of recent reactors")


class CommentPreview(BaseModel):
    """Preview of comments for feed display"""
    total_count: int = Field(description="Total number of comments")
    recent_comments: List[Dict[str, Any]] = Field(description="Recent comment previews")
    has_user_commented: bool = Field(description="Whether current user has commented")


class PregnancyContext(BaseModel):
    """Pregnancy-specific context for posts"""
    current_week: Optional[int] = Field(default=None, description="Current pregnancy week")
    trimester: Optional[int] = Field(default=None, description="Current trimester (1, 2, or 3)")
    days_since_post: int = Field(description="Days since post was created")
    is_milestone_week: bool = Field(default=False, description="Whether this is a milestone week")
    baby_development: Optional[str] = Field(default=None, description="Baby development info for this week")


class FamilyEngagementStats(BaseModel):
    """Family engagement statistics for posts"""
    family_member_reactions: int = Field(description="Reactions from family members")
    family_member_comments: int = Field(description="Comments from family members")
    family_member_views: int = Field(description="Views from family members")
    needs_family_response: bool = Field(default=False, description="Post is asking for family input")
    celebration_worthy: bool = Field(default=False, description="Post should be celebrated")
    engagement_score: float = Field(description="Overall engagement score (0-100)")


class EnrichedPost(PostResponse):
    """Enhanced post with additional context for feed display"""
    author: Optional[Dict[str, Any]] = Field(default=None, description="Author information")
    pregnancy_context: Optional[PregnancyContext] = Field(default=None, description="Pregnancy-specific context")
    reaction_summary: Optional[ReactionSummary] = Field(default=None, description="Reaction summary")
    comment_preview: Optional[CommentPreview] = Field(default=None, description="Comment preview")
    engagement_stats: Optional[FamilyEngagementStats] = Field(default=None, description="Family engagement metrics")
    media_items: List[Dict[str, Any]] = Field(default_factory=list, description="Associated media items")
    is_trending: bool = Field(default=False, description="Whether post is trending in family")
    is_pinned: bool = Field(default=False, description="Whether post is pinned by family")
    requires_attention: bool = Field(default=False, description="Whether post needs family attention")


class FamilyContext(BaseModel):
    """Family context information for Instagram-like feed"""
    active_members: int = Field(description="Number of active family members")
    recent_interactions: int = Field(description="Recent interactions count")
    warmth_score: float = Field(description="Overall family warmth score")
    celebration_count: int = Field(default=0, description="Number of recent celebrations")
    

class FeedResponse(BaseModel):
    """Enhanced response for Instagram-like feed queries"""
    posts: List[EnrichedPost] = Field(description="Feed posts with enriched data")
    cursor: Optional[Dict[str, Any]] = Field(default=None, description="Cursor information for pagination")
    family_context: Optional[FamilyContext] = Field(default=None, description="Family engagement context")
    real_time_token: Optional[str] = Field(default=None, description="WebSocket token for real-time updates")
    feed_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional feed metadata")
    pregnancy_summary: Optional[Dict[str, Any]] = Field(default=None, description="Current pregnancy summary")


class PersonalTimelineResponse(BaseModel):
    """Response for personal timeline queries"""
    posts: List[EnrichedPost] = Field(description="Personal timeline posts")
    milestones_coming_up: List[Dict[str, Any]] = Field(description="Upcoming pregnancy milestones")
    weekly_progress: Optional[Dict[str, Any]] = Field(default=None, description="Current week progress")
    total_count: int = Field(description="Total number of posts")
    has_more: bool = Field(description="Whether there are more posts")


class ReactionRequest(BaseModel):
    """Request to add/update a reaction"""
    post_id: Optional[str] = Field(default=None, description="Post ID (if reacting to post)")
    comment_id: Optional[str] = Field(default=None, description="Comment ID (if reacting to comment)")
    reaction_type: PregnancyReactionType = Field(description="Type of reaction")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional reaction context")


class OptimisticReactionRequest(BaseModel):
    """Enhanced request for optimistic reactions with sub-50ms response target"""
    post_id: str = Field(description="Post ID (required for optimistic reactions)")
    reaction_type: PregnancyReactionType = Field(description="Type of reaction")
    intensity: int = Field(default=2, ge=1, le=3, description="Reaction intensity (1-3)")
    client_id: str = Field(description="Client-generated UUID for deduplication")
    timestamp: datetime = Field(description="Client timestamp for latency calculation")
    custom_message: Optional[str] = Field(default=None, max_length=200, description="Personal note with reaction")
    is_milestone_reaction: bool = Field(default=False, description="Special milestone recognition")


class ReactionResponse(BaseModel):
    """Response for reaction operations"""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="ID of the reaction")
    updated_counts: Dict[ReactionType, int] = Field(description="Updated reaction counts")
    message: Optional[str] = Field(default=None, description="Success/error message")


class OptimisticReactionResponse(BaseModel):
    """Enhanced response for optimistic reactions with performance metrics"""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="ID of the reaction")
    optimistic: bool = Field(default=True, description="Whether this is an optimistic response")
    updated_counts: Dict[str, int] = Field(description="Updated reaction counts by type")
    family_warmth_delta: float = Field(description="Change in family warmth score")
    latency_ms: Optional[float] = Field(default=None, description="Server processing latency")
    client_dedup_id: str = Field(description="Client ID for deduplication")
    broadcast_queued: bool = Field(default=True, description="Whether real-time broadcast is queued")


class FeedFiltersResponse(BaseModel):
    """Available feed filters and their counts"""
    available_filters: List[Dict[str, Any]] = Field(description="Available filter types with counts")
    active_pregnancies: List[Dict[str, Any]] = Field(description="Active pregnancies user can access")
    family_groups: List[Dict[str, Any]] = Field(description="Family groups user belongs to")
    suggested_filters: List[str] = Field(description="Suggested filters based on recent activity")


class CelebrationPost(BaseModel):
    """Special celebration post data"""
    post_id: str = Field(description="ID of the post being celebrated")
    celebration_type: str = Field(description="Type of celebration (milestone, achievement, etc.)")
    family_reactions: List[Dict[str, Any]] = Field(description="Family member reactions")
    celebration_message: Optional[str] = Field(default=None, description="Auto-generated celebration message")
    is_new: bool = Field(default=True, description="Whether this is a new celebration")


class FeedAnalytics(BaseModel):
    """Analytics data for feed performance"""
    total_family_engagement: int = Field(description="Total family engagement this week")
    trending_posts: List[str] = Field(description="Post IDs that are trending")
    engagement_by_type: Dict[str, int] = Field(description="Engagement counts by post type")
    family_activity_score: float = Field(description="Overall family activity score")
    suggestions: List[str] = Field(description="Suggestions to improve engagement")
