from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.content import (
    PostType, PostStatus, ReactionType, MediaType, PostContent, PostPrivacy,
    MediaMetadata, VisibilityLevel
)


class MediaItemBase(BaseModel):
    """Base media item schema"""
    type: MediaType
    url: str
    thumbnail_url: Optional[str] = None
    filename: str
    size: int
    duration: Optional[int] = None
    caption: Optional[str] = None
    taken_at: Optional[datetime] = None
    location: Optional[str] = None
    order: int = 0
    media_metadata: Optional[MediaMetadata] = None


class MediaItemCreate(MediaItemBase):
    """Schema for creating media item"""
    uploaded_by: str
    post_id: Optional[str] = None


class MediaItemResponse(MediaItemBase):
    """Schema for media item responses"""
    id: str
    post_id: Optional[str]
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """Base post schema"""
    type: PostType
    content: PostContent
    privacy: Optional[PostPrivacy] = None
    scheduled_for: Optional[datetime] = None


class PostCreate(PostBase):
    """Schema for creating a post"""
    author_id: str
    pregnancy_id: str


class PostUpdate(BaseModel):
    """Schema for updating a post"""
    type: Optional[PostType] = None
    content: Optional[PostContent] = None
    privacy: Optional[PostPrivacy] = None
    status: Optional[PostStatus] = None
    scheduled_for: Optional[datetime] = None


class PostResponse(PostBase):
    """Schema for post responses"""
    id: str
    author_id: str
    pregnancy_id: str
    status: PostStatus
    reaction_count: int
    comment_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReactionBase(BaseModel):
    """Base reaction schema"""
    type: ReactionType


class ReactionCreate(ReactionBase):
    """Schema for creating a reaction"""
    user_id: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None


class ReactionResponse(ReactionBase):
    """Schema for reaction responses"""
    id: str
    user_id: str
    post_id: Optional[str]
    comment_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    """Base comment schema"""
    content: str
    mentions: List[str] = []


class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    post_id: str
    user_id: str
    parent_id: Optional[str] = None


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: Optional[str] = None


class CommentResponse(CommentBase):
    """Schema for comment responses"""
    id: str
    post_id: str
    user_id: str
    parent_id: Optional[str]
    edited: bool
    reaction_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostViewCreate(BaseModel):
    """Schema for creating a post view"""
    post_id: str
    user_id: str
    time_spent: Optional[int] = None
    source: str = "timeline"


class PostShareCreate(BaseModel):
    """Schema for creating a post share"""
    post_id: str
    shared_by: str
    shared_with: List[str]
    message: Optional[str] = None
    method: str = "internal"