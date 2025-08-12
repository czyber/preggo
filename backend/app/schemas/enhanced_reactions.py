"""
Enhanced Reactions Schemas for pregnancy-specific reactions with intensity.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from app.schemas.feed import PregnancyReactionType


class OptimisticReactionRequest(BaseModel):
    """Request schema for optimistic reactions with sub-50ms target."""
    post_id: Optional[str] = Field(None, description="Post ID (required if not comment)")
    comment_id: Optional[str] = Field(None, description="Comment ID (required if not post)")
    reaction_type: PregnancyReactionType = Field(description="Type of reaction")
    intensity: int = Field(default=2, ge=1, le=3, description="Reaction intensity (1-3)")
    custom_message: Optional[str] = Field(None, max_length=200, description="Personal note with reaction")
    is_milestone_reaction: bool = Field(default=False, description="Special milestone recognition")
    client_id: str = Field(description="Client-generated UUID for deduplication")
    client_timestamp: datetime = Field(description="Client timestamp for latency calculation")
    
    @validator('post_id', 'comment_id')
    def validate_target(cls, v, values):
        """Ensure either post_id or comment_id is provided, but not both."""
        if 'post_id' in values and 'comment_id' in values:
            if values['post_id'] and v:
                raise ValueError('Cannot specify both post_id and comment_id')
            if not values['post_id'] and not v:
                raise ValueError('Must specify either post_id or comment_id')
        return v


class StandardReactionRequest(BaseModel):
    """Request schema for standard reactions with full validation."""
    post_id: Optional[str] = Field(None, description="Post ID (required if not comment)")
    comment_id: Optional[str] = Field(None, description="Comment ID (required if not post)")
    reaction_type: PregnancyReactionType = Field(description="Type of reaction")
    intensity: int = Field(default=2, ge=1, le=3, description="Reaction intensity (1-3)")
    custom_message: Optional[str] = Field(None, max_length=200, description="Personal note with reaction")
    is_milestone_reaction: bool = Field(default=False, description="Special milestone recognition")


class OptimisticReactionResponse(BaseModel):
    """Response schema for optimistic reactions with performance metrics."""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="ID of the reaction")
    reaction_type: str = Field(description="Type of reaction added")
    intensity: int = Field(description="Reaction intensity level")
    family_warmth_delta: float = Field(description="Change in family warmth score")
    updated_counts: Dict[str, int] = Field(description="Updated reaction counts by type")
    total_family_warmth: float = Field(description="Total family warmth score")
    client_dedup_id: str = Field(description="Client ID for deduplication")
    performance: Dict[str, Any] = Field(description="Performance metrics")
    server_timestamp: str = Field(description="Server processing timestamp")


class StandardReactionResponse(BaseModel):
    """Response schema for standard reactions."""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="ID of the reaction")
    reaction_summary: Dict[str, Any] = Field(description="Complete reaction summary")
    message: str = Field(description="Success message")


class EnhancedReactionSummary(BaseModel):
    """Comprehensive reaction summary with family warmth data."""
    total_count: int = Field(description="Total number of reactions")
    reaction_counts: Dict[str, int] = Field(description="Count by reaction type")
    intensity_breakdown: Dict[str, Dict[str, int]] = Field(description="Intensity breakdown by type")
    average_intensities: Dict[str, float] = Field(description="Average intensity per reaction type")
    total_family_warmth: float = Field(description="Total family warmth contribution")
    milestone_reaction_count: int = Field(description="Number of milestone reactions")
    top_reactions: List[Dict[str, Any]] = Field(description="Top 3 reaction types")
    user_reaction: Optional[Dict[str, Any]] = Field(None, description="Current user's reaction")
    generated_at: str = Field(description="When summary was generated")


class ReactionTypeInfo(BaseModel):
    """Information about available reaction types."""
    value: str = Field(description="Reaction type value")
    display_name: str = Field(description="Display name")
    emoji: str = Field(description="Emoji representation")
    description: str = Field(description="Reaction description")
    category: str = Field(description="Reaction category (primary/additional)")
    family_warmth_base: float = Field(description="Base family warmth value")


class IntensityLevelInfo(BaseModel):
    """Information about intensity levels."""
    level: int = Field(description="Intensity level (1-3)")
    display_name: str = Field(description="Display name")
    multiplier: float = Field(description="Family warmth multiplier")
    description: str = Field(description="Level description")


class AvailableReactionTypes(BaseModel):
    """Complete information about available reaction types and intensity."""
    reaction_types: List[ReactionTypeInfo] = Field(description="All available reaction types")
    intensity_levels: List[IntensityLevelInfo] = Field(description="Available intensity levels")
    milestone_bonus: Dict[str, float] = Field(description="Milestone bonus multipliers")


class FamilyReactionInsights(BaseModel):
    """Family-wide reaction insights for analytics."""
    total_reactions: int = Field(description="Total reactions in period")
    family_reactions: int = Field(description="Reactions from family members")
    family_participation_rate: float = Field(description="Family member participation rate")
    total_family_warmth: float = Field(description="Total family warmth generated")
    average_intensity: float = Field(description="Average reaction intensity")
    milestone_celebrations: int = Field(description="Number of milestone celebrations")
    reaction_distribution: Dict[str, Dict[str, Any]] = Field(description="Distribution by reaction type")
    most_supportive_members: List[Dict[str, Any]] = Field(description="Most supportive family members")
    engagement_trends: List[Dict[str, Any]] = Field(description="Engagement trend data")


class ReactionRemovalResponse(BaseModel):
    """Response for reaction removal."""
    success: bool = Field(description="Whether removal was successful")
    updated_summary: Dict[str, Any] = Field(description="Updated reaction summary")
    message: str = Field(description="Success message")