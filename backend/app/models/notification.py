from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime
import uuid
from enum import Enum


class PregnancyNotificationType(str, Enum):
    # Week Progress
    NEW_WEEK = "new_week"
    MILESTONE_DUE = "milestone_due"
    WEEK_SUMMARY = "week_summary"
    
    # Family Sharing
    NEW_FAMILY_POST = "new_family_post"
    POST_REACTION = "post_reaction"
    COMMENT_ON_POST = "comment_on_post"
    FAMILY_MEMBER_JOINED = "family_member_joined"
    MENTION_IN_POST = "mention_in_post"
    
    # Health & Appointments
    APPOINTMENT_REMINDER = "appointment_reminder"
    SYMPTOM_CHECK_IN = "symptom_check_in"
    WEIGHT_TRACKING_REMINDER = "weight_tracking_reminder"
    
    # Special Moments
    MILESTONE_CELEBRATION = "milestone_celebration"
    MEMORY_BOOK_UPDATE = "memory_book_update"
    WEEKLY_PHOTO_REMINDER = "weekly_photo_reminder"
    
    # Family Engagement
    FAMILY_QUESTION = "family_question"
    SUPPORT_MESSAGE = "support_message"
    CELEBRATION_INVITE = "celebration_invite"


class NotificationCategory(str, Enum):
    PREGNANCY_PROGRESS = "pregnancy_progress"
    FAMILY_ACTIVITY = "family_activity"
    HEALTH_REMINDERS = "health_reminders"
    SPECIAL_MOMENTS = "special_moments"
    SYSTEM_UPDATES = "system_updates"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryMethod(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationFrequency(str, Enum):
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class NotificationData(SQLModel):
    """Additional data for notifications"""
    post_id: Optional[str] = None
    milestone_id: Optional[str] = None
    week: Optional[int] = None
    author_name: Optional[str] = None
    group_name: Optional[str] = None
    action_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None


class PregnancyNotification(SQLModel, table=True):
    """Pregnancy-focused notifications"""
    __tablename__ = "pregnancy_notifications"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="User receiving the notification")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Notification details
    type: PregnancyNotificationType = Field(description="Type of notification")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    
    # Notification metadata
    priority: NotificationPriority = NotificationPriority.MEDIUM
    category: NotificationCategory = Field(description="Notification category")
    
    # Additional data stored as JSONB
    data: NotificationData = Field(
        default_factory=NotificationData,
        sa_column=Column(JSON),
        description="Additional notification data"
    )
    
    # Delivery settings
    delivery_methods: List[DeliveryMethod] = Field(
        default_factory=lambda: [DeliveryMethod.IN_APP],
        sa_column=Column(JSON),
        description="How notification should be delivered"
    )
    
    # Scheduling and delivery
    scheduled_for: Optional[datetime] = Field(default=None, description="When to send notification")
    sent_at: Optional[datetime] = Field(default=None, description="When notification was sent")
    read_at: Optional[datetime] = Field(default=None, description="When notification was read")
    action_taken: Optional[str] = Field(default=None, description="Action taken by user")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CategoryPreference(SQLModel):
    """Preference settings for notification categories"""
    category: NotificationCategory
    enabled: bool = True
    methods: List[DeliveryMethod] = Field(default_factory=lambda: [DeliveryMethod.IN_APP])
    frequency: NotificationFrequency = NotificationFrequency.IMMEDIATE


class DeliverySchedule(SQLModel):
    """When notifications should be delivered"""
    quiet_hours_start: str = "22:00"  # HH:MM format
    quiet_hours_end: str = "07:00"    # HH:MM format
    weekend_delivery: bool = True
    time_zone: str = "UTC"


class FamilyNotificationSettings(SQLModel):
    """Family-specific notification preferences"""
    new_member_notifications: bool = True
    every_post_notification: bool = False
    only_important_posts: bool = True
    milestone_notifications: bool = True
    comment_notifications: bool = True
    reaction_notifications: bool = False


class QuietHours(SQLModel):
    """Quiet hours configuration"""
    enabled: bool = True
    start_time: str = "22:00"  # HH:MM format
    end_time: str = "07:00"    # HH:MM format
    days_of_week: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])  # 0 = Monday


class NotificationPreferences(SQLModel, table=True):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", unique=True, description="User these preferences belong to")
    
    # Category preferences stored as JSONB
    categories: List[CategoryPreference] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Preferences by notification category"
    )
    
    # Delivery schedule stored as JSONB
    delivery_schedule: DeliverySchedule = Field(
        default_factory=DeliverySchedule,
        sa_column=Column(JSON),
        description="When notifications should be delivered"
    )
    
    # Family notification settings stored as JSONB
    family_settings: FamilyNotificationSettings = Field(
        default_factory=FamilyNotificationSettings,
        sa_column=Column(JSON),
        description="Family-specific notification preferences"
    )
    
    # Quiet hours stored as JSONB
    quiet_hours: QuietHours = Field(
        default_factory=QuietHours,
        sa_column=Column(JSON),
        description="Quiet hours configuration"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FamilyMessage(SQLModel, table=True):
    """Messages between family members"""
    __tablename__ = "family_messages"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    sender_id: str = Field(foreign_key="users.id", description="Message sender")
    
    # Message details
    recipient_type: str = Field(description="individual, group, or all_family")
    recipients: List[str] = Field(
        sa_column=Column(JSON),
        description="User IDs or group IDs of recipients"
    )
    subject: Optional[str] = Field(default=None, description="Message subject")
    message: str = Field(description="Message content")
    
    # Attachments and references
    related_post_id: Optional[str] = Field(default=None, foreign_key="posts.id", description="Related post")
    priority: str = Field(default="normal", description="normal or high")
    
    # Read tracking
    read_by: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Read receipts with user_id and read_at timestamp"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }