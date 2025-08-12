"""
Threaded Comments Schemas for enhanced comment functionality.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CreateCommentRequest(BaseModel):
    """Request schema for creating threaded comments."""
    post_id: str = Field(description="ID of the post to comment on")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for threaded replies")
    content: str = Field(min_length=1, max_length=2000, description="Comment content")
    mentions: Optional[List[str]] = Field(None, description="List of user IDs to mention")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class UpdateCommentRequest(BaseModel):
    """Request schema for updating comments."""
    content: str = Field(min_length=1, max_length=2000, description="Updated comment content")
    preserve_mentions: bool = Field(default=True, description="Whether to preserve existing mentions")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class MentionInfo(BaseModel):
    """Information about mentioned users."""
    user_id: str = Field(description="Mentioned user ID")
    display_name: str = Field(description="Display name of mentioned user")


class AuthorInfo(BaseModel):
    """Comment author information."""
    id: str = Field(description="Author user ID")
    display_name: str = Field(description="Author display name")
    avatar_url: Optional[str] = Field(None, description="Author avatar URL")


class EditHistoryEntry(BaseModel):
    """Edit history entry for comments."""
    previous_content: str = Field(description="Previous comment content")
    edited_at: str = Field(description="When edit was made")
    edited_by: str = Field(description="User ID who made the edit")


class TypingIndicatorInfo(BaseModel):
    """Typing indicator information."""
    is_someone_typing: bool = Field(description="Whether someone is typing")
    typing_user: Optional[AuthorInfo] = Field(None, description="User who is typing")
    typing_since: Optional[str] = Field(None, description="When typing started")


class CommentReactions(BaseModel):
    """Comment reaction information."""
    total_count: int = Field(description="Total reaction count")
    reaction_counts: Dict[str, int] = Field(description="Counts by reaction type")
    user_reaction: Optional[Dict[str, Any]] = Field(None, description="Current user's reaction")


class ThreadedCommentResponse(BaseModel):
    """Response schema for threaded comments."""
    id: str = Field(description="Comment ID")
    content: str = Field(description="Comment content")
    author: AuthorInfo = Field(description="Comment author information")
    post_id: Optional[str] = Field(None, description="Post ID (for root comments)")
    parent_id: Optional[str] = Field(None, description="Parent comment ID")
    thread_depth: int = Field(description="Depth in comment thread (0-5)")
    thread_path: str = Field(description="Thread path (e.g., '1.2.3')")
    reply_count: int = Field(default=0, description="Number of direct replies")
    total_descendant_count: int = Field(default=0, description="Total descendants in thread")
    mentions: List[MentionInfo] = Field(default_factory=list, description="Mentioned users")
    edited: bool = Field(default=False, description="Whether comment was edited")
    edit_history: Optional[List[EditHistoryEntry]] = Field(None, description="Edit history")
    reactions: Optional[CommentReactions] = Field(None, description="Reaction information")
    typing_indicator: Optional[TypingIndicatorInfo] = Field(None, description="Typing indicator info")
    family_warmth: float = Field(description="Family warmth contribution")
    can_accept_replies: bool = Field(description="Whether comment can accept replies")
    replies: List["ThreadedCommentResponse"] = Field(default_factory=list, description="Nested replies")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


class CreateCommentResponse(BaseModel):
    """Response schema for comment creation."""
    success: bool = Field(description="Whether creation was successful")
    comment: ThreadedCommentResponse = Field(description="Created comment with thread info")
    message: str = Field(description="Success message")


class UpdateCommentResponse(BaseModel):
    """Response schema for comment updates."""
    success: bool = Field(description="Whether update was successful")
    comment: Dict[str, Any] = Field(description="Updated comment data")
    message: str = Field(description="Success message")


class ThreadStatistics(BaseModel):
    """Statistics about comment threads."""
    total_comments: int = Field(description="Total number of comments")
    root_comments: int = Field(description="Number of root comments")
    max_depth_used: int = Field(description="Maximum thread depth used")
    threads_with_replies: int = Field(description="Number of threads with replies")
    total_mentions: int = Field(description="Total mentions across all comments")


class ThreadedCommentsResponse(BaseModel):
    """Response schema for getting threaded comments."""
    comments: List[ThreadedCommentResponse] = Field(description="Root comments with nested replies")
    total_count: int = Field(description="Total comment count")
    thread_structure: Dict[str, Any] = Field(description="Comment tree structure")
    thread_statistics: ThreadStatistics = Field(description="Thread statistics")
    generated_at: str = Field(description="Response generation timestamp")


class TypingIndicatorRequest(BaseModel):
    """Request schema for typing indicators."""
    post_id: Optional[str] = Field(None, description="Post ID (for root comments)")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID (for replies)")
    is_typing: bool = Field(default=True, description="Whether user is typing")
    
    @validator('post_id', 'parent_comment_id')
    def validate_target(cls, v, values):
        """Ensure either post_id or parent_comment_id is provided."""
        if 'post_id' in values and 'parent_comment_id' in values:
            if not values.get('post_id') and not v:
                raise ValueError('Must specify either post_id or parent_comment_id')
        return v


class TypingIndicatorResponse(BaseModel):
    """Response schema for typing indicators."""
    success: bool = Field(description="Whether typing indicator was set")
    is_typing: bool = Field(description="Current typing state")
    message: str = Field(description="Status message")


class MentionSuggestion(BaseModel):
    """Mention suggestion for auto-complete."""
    user_id: str = Field(description="User ID")
    username: str = Field(description="Username for @mention")
    display_name: str = Field(description="Display name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    relationship: str = Field(description="Relationship to pregnancy")
    match_score: float = Field(description="Match score for query")


class MentionSuggestionsResponse(BaseModel):
    """Response schema for mention suggestions."""
    suggestions: List[MentionSuggestion] = Field(description="Mention suggestions")
    query: str = Field(description="Search query used")
    total_count: int = Field(description="Number of suggestions returned")


class CommentReactionRequest(BaseModel):
    """Request schema for commenting reactions."""
    reaction_type: str = Field(description="Type of reaction (subset of main reactions)")
    intensity: int = Field(default=2, ge=1, le=3, description="Reaction intensity")
    custom_message: Optional[str] = Field(None, max_length=200, description="Optional message")


class CommentReactionResponse(BaseModel):
    """Response schema for comment reactions."""
    success: bool = Field(description="Whether reaction was successful")
    reaction_id: str = Field(description="Reaction ID")
    reaction_summary: Dict[str, Any] = Field(description="Updated reaction summary")
    message: str = Field(description="Success message")


class CommentDeletionResponse(BaseModel):
    """Response schema for comment deletion."""
    success: bool = Field(description="Whether deletion was successful")
    message: str = Field(description="Status message")


# Update forward references for recursive model
ThreadedCommentResponse.model_rebuild()