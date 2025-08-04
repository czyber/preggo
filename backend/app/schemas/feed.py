from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.models.content import ReactionType
from app.schemas.content import PostResponse


class PregnancyReactionType(str, Enum):
    """Extended reaction types specific to pregnancy content"""
    LOVE = "love"           # ❤️ General love and support
    EXCITED = "excited"     # 😍 Excitement for milestones
    CARE = "care"           # 🤗 Caring and nurturing
    SUPPORT = "support"     # 💪 Strength and encouragement
    BEAUTIFUL = "beautiful"  # ✨ Beautiful moments/photos
    FUNNY = "funny"         # 😂 Funny pregnancy moments
    PRAYING = "praying"     # 🙏 Prayers and well wishes
    PROUD = "proud"         # 🏆 Pride in achievements
    GRATEFUL = "grateful"   # 🙏✨ Gratitude and thankfulness


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


class FeedRequest(BaseModel):
    """Request parameters for feed queries"""
    limit: int = Field(default=20, ge=1, le=100, description="Number of posts to return")
    offset: int = Field(default=0, ge=0, description="Number of posts to skip")
    filter_type: FeedFilterType = Field(default=FeedFilterType.ALL, description="Type of content to show")
    sort_by: FeedSortType = Field(default=FeedSortType.CHRONOLOGICAL, description="How to sort the feed")
    include_reactions: bool = Field(default=True, description="Include reaction counts and types")
    include_comments: bool = Field(default=True, description="Include comment previews")
    include_media: bool = Field(default=True, description="Include media metadata")
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


class FeedResponse(BaseModel):
    """Response for feed queries"""
    posts: List[EnrichedPost] = Field(description="Feed posts with enriched data")
    total_count: int = Field(description="Total number of posts available")
    has_more: bool = Field(description="Whether there are more posts to load")
    next_offset: Optional[int] = Field(default=None, description="Offset for next page")
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


class ReactionResponse(BaseModel):
    """Response for reaction operations"""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="ID of the reaction")
    updated_counts: Dict[ReactionType, int] = Field(description="Updated reaction counts")
    message: Optional[str] = Field(default=None, description="Success/error message")


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