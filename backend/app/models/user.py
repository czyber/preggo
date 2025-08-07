from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime
import uuid
from enum import Enum
import json

if TYPE_CHECKING:
    from app.models.content import Comment


class NotificationSettings(SQLModel):
    """Notification preferences"""
    push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    weekly_updates: bool = True
    milestone_reminders: bool = True
    family_activity: bool = True
    appointment_reminders: bool = True
    quiet_hours_start: Optional[str] = "22:00"  # HH:MM format
    quiet_hours_end: Optional[str] = "07:00"


class DefaultPrivacyLevel(str, Enum):
    PRIVATE = "private"
    PARTNER_ONLY = "partner_only"
    IMMEDIATE = "immediate"
    EXTENDED = "extended"
    FRIENDS = "friends"
    ALL_FAMILY = "all_family"


class SharingDefaults(SQLModel):
    """Default sharing preferences for new posts"""
    default_visibility: DefaultPrivacyLevel = DefaultPrivacyLevel.IMMEDIATE
    allow_comments: bool = True
    allow_reactions: bool = True
    allow_downloads: bool = False
    auto_share_milestones: bool = True
    auto_share_weekly_photos: bool = False


class UserPreferences(SQLModel):
    """User preferences and settings"""
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy: DefaultPrivacyLevel = DefaultPrivacyLevel.IMMEDIATE
    language: str = "en"
    measurement_unit: str = "metric"  # 'metric' | 'imperial'
    sharing_defaults: SharingDefaults = Field(default_factory=SharingDefaults)


class User(SQLModel, table=True):
    """Main user model for the pregnancy tracking app"""
    __tablename__ = "users"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID primary key"
    )
    email: str = Field(unique=True, index=True, description="User's email address")
    first_name: str = Field(description="User's first name")
    last_name: str = Field(description="User's last name")
    profile_image: Optional[str] = Field(default=None, description="URL to profile image")
    timezone: str = Field(default="UTC", description="User's timezone")
    
    # Store preferences as JSONB
    preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        sa_column=Column(JSON),
        description="User preferences and settings"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional fields for user status
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    
    # Relationships
    comments: List["Comment"] = Relationship(back_populates="author")
    
    class Config:
        # Enable JSON encoding for Pydantic models
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }