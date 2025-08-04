"""
WebSocket event schemas for real-time family interactions and celebrations.

This module defines the event types and data structures for WebSocket communication
between the backend and frontend, enabling live family interactions during pregnancy tracking.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.schemas.content import ReactionType
from app.schemas.milestone import MilestoneType


class WebSocketEventType(str, Enum):
    """Types of WebSocket events for pregnancy tracking app"""
    
    # Connection events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_ERROR = "connection_error"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    
    # Feed events
    NEW_POST = "new_post"
    POST_UPDATED = "post_updated"
    POST_DELETED = "post_deleted"
    
    # Interaction events
    NEW_REACTION = "new_reaction"
    REACTION_REMOVED = "reaction_removed"
    NEW_COMMENT = "new_comment"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    
    # Milestone and celebration events
    MILESTONE_ACHIEVED = "milestone_achieved"
    CELEBRATION_STARTED = "celebration_started"
    CELEBRATION_JOINED = "celebration_joined"
    CELEBRATION_ENDED = "celebration_ended"
    
    # Family activity events
    FAMILY_MEMBER_ONLINE = "family_member_online"
    FAMILY_MEMBER_OFFLINE = "family_member_offline"
    TYPING_STARTED = "typing_started"
    TYPING_STOPPED = "typing_stopped"
    
    # System events
    SYSTEM_NOTIFICATION = "system_notification"
    ERROR = "error"


class ConnectionStatus(str, Enum):
    """WebSocket connection status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class UserPresence(BaseModel):
    """User presence information for family members"""
    user_id: str = Field(description="User ID")
    display_name: str = Field(description="Display name")
    profile_image: Optional[str] = Field(default=None, description="Profile image URL")
    status: str = Field(description="Online status")
    last_seen: datetime = Field(description="Last seen timestamp")
    is_typing: bool = Field(default=False, description="Is currently typing")


class WebSocketMessage(BaseModel):
    """Base WebSocket message structure"""
    event_type: WebSocketEventType = Field(description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    user_id: Optional[str] = Field(default=None, description="User who triggered the event")
    pregnancy_id: Optional[str] = Field(default=None, description="Associated pregnancy ID")
    room_id: str = Field(description="Room/channel ID (usually pregnancy-{id})")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")


class ConnectionEvent(BaseModel):
    """Connection establishment event data"""
    user_id: str = Field(description="Connected user ID")
    display_name: str = Field(description="User display name")
    rooms: List[str] = Field(description="Rooms user has joined")
    permissions: List[str] = Field(description="User permissions in rooms")


class PostEvent(BaseModel):
    """Post-related event data"""
    post_id: str = Field(description="Post ID")
    post_type: str = Field(description="Type of post")
    title: Optional[str] = Field(default=None, description="Post title")
    content: Optional[str] = Field(default=None, description="Post content")
    author_id: str = Field(description="Post author user ID")
    author_name: str = Field(description="Post author display name")
    created_at: datetime = Field(description="Post creation timestamp")
    privacy_level: str = Field(description="Post privacy level")
    has_media: bool = Field(default=False, description="Post has media attachments")
    is_milestone: bool = Field(default=False, description="Post is milestone-related")


class ReactionEvent(BaseModel):
    """Reaction event data"""
    post_id: str = Field(description="Post ID")
    reaction_type: ReactionType = Field(description="Type of reaction")
    user_id: str = Field(description="User who reacted")
    user_name: str = Field(description="User display name")
    total_reactions: int = Field(description="Total reaction count for post")
    reaction_counts: Dict[str, int] = Field(description="Count by reaction type")


class CommentEvent(BaseModel):
    """Comment event data"""
    comment_id: str = Field(description="Comment ID")
    post_id: str = Field(description="Post ID")
    content: str = Field(description="Comment content")
    author_id: str = Field(description="Comment author user ID")
    author_name: str = Field(description="Comment author display name")
    created_at: datetime = Field(description="Comment creation timestamp")
    parent_comment_id: Optional[str] = Field(default=None, description="Parent comment ID for replies")
    total_comments: int = Field(description="Total comment count for post")


class MilestoneEvent(BaseModel):
    """Milestone achievement event data"""
    milestone_id: str = Field(description="Milestone ID")
    milestone_type: MilestoneType = Field(description="Type of milestone")
    title: str = Field(description="Milestone title")
    description: str = Field(description="Milestone description")
    week: int = Field(description="Pregnancy week")
    achieved_at: datetime = Field(description="Achievement timestamp")
    celebration_worthy: bool = Field(description="Should trigger celebration")
    custom_message: Optional[str] = Field(default=None, description="Custom celebration message")


class CelebrationEvent(BaseModel):
    """Celebration event data"""
    celebration_id: str = Field(description="Celebration ID")
    milestone_id: Optional[str] = Field(default=None, description="Associated milestone ID")
    post_id: Optional[str] = Field(default=None, description="Associated post ID")
    title: str = Field(description="Celebration title")
    message: str = Field(description="Celebration message")
    started_by: str = Field(description="User who started celebration")
    participants: List[UserPresence] = Field(description="Celebration participants")
    duration_minutes: int = Field(default=10, description="Celebration duration")
    celebration_type: str = Field(description="Type of celebration")


class FamilyActivityEvent(BaseModel):
    """Family member activity event data"""
    user_id: str = Field(description="User ID")
    display_name: str = Field(description="User display name")
    activity_type: str = Field(description="Type of activity")
    target_id: Optional[str] = Field(default=None, description="Target post/comment ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional activity data")


class SystemNotificationEvent(BaseModel):
    """System notification event data"""
    notification_id: str = Field(description="Notification ID")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    level: str = Field(description="Notification level (info, warning, error)")
    action_url: Optional[str] = Field(default=None, description="Optional action URL")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")


class ErrorEvent(BaseModel):
    """Error event data"""
    error_code: str = Field(description="Error code")
    error_message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class WebSocketResponse(BaseModel):
    """WebSocket response message structure"""
    success: bool = Field(description="Whether the operation was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[ErrorEvent] = Field(default=None, description="Error information if applicable")


class RoomInfo(BaseModel):
    """Information about a WebSocket room"""
    room_id: str = Field(description="Room identifier")
    pregnancy_id: str = Field(description="Associated pregnancy ID")
    name: str = Field(description="Room display name")
    member_count: int = Field(description="Number of active members")
    permissions: List[str] = Field(description="Required permissions for room access")
    created_at: datetime = Field(description="Room creation timestamp")


class ConnectionInfo(BaseModel):
    """Client connection information"""
    connection_id: str = Field(description="Unique connection identifier")
    user_id: str = Field(description="Connected user ID")
    rooms: List[str] = Field(description="Rooms user has joined")
    connected_at: datetime = Field(description="Connection timestamp")
    last_activity: datetime = Field(description="Last activity timestamp")
    permissions: List[str] = Field(description="User permissions across all rooms")


# Helper functions for creating specific event messages
def create_websocket_message(
    event_type: WebSocketEventType,
    room_id: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    pregnancy_id: Optional[str] = None
) -> WebSocketMessage:
    """Helper to create a WebSocket message"""
    return WebSocketMessage(
        event_type=event_type,
        user_id=user_id,
        pregnancy_id=pregnancy_id,
        room_id=room_id,
        data=data
    )


def create_post_event_message(
    event_type: WebSocketEventType,
    room_id: str,
    post_data: PostEvent,
    user_id: str,
    pregnancy_id: str
) -> WebSocketMessage:
    """Helper to create post-related event messages"""
    return create_websocket_message(
        event_type=event_type,
        room_id=room_id,
        data=post_data.dict(),
        user_id=user_id,
        pregnancy_id=pregnancy_id
    )


def create_reaction_event_message(
    event_type: WebSocketEventType,
    room_id: str,
    reaction_data: ReactionEvent,
    user_id: str,
    pregnancy_id: str
) -> WebSocketMessage:
    """Helper to create reaction event messages"""
    return create_websocket_message(
        event_type=event_type,
        room_id=room_id,
        data=reaction_data.dict(),
        user_id=user_id,
        pregnancy_id=pregnancy_id
    )


def create_milestone_event_message(
    room_id: str,
    milestone_data: MilestoneEvent,
    user_id: str,
    pregnancy_id: str
) -> WebSocketMessage:
    """Helper to create milestone achievement messages"""
    return create_websocket_message(
        event_type=WebSocketEventType.MILESTONE_ACHIEVED,
        room_id=room_id,
        data=milestone_data.dict(),
        user_id=user_id,
        pregnancy_id=pregnancy_id
    )


def create_celebration_event_message(
    event_type: WebSocketEventType,
    room_id: str,
    celebration_data: CelebrationEvent,
    user_id: str,
    pregnancy_id: str
) -> WebSocketMessage:
    """Helper to create celebration event messages"""
    return create_websocket_message(
        event_type=event_type,
        room_id=room_id,
        data=celebration_data.dict(),
        user_id=user_id,
        pregnancy_id=pregnancy_id
    )