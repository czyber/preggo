from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.notification import (
    PregnancyNotificationType, NotificationCategory, NotificationPriority,
    DeliveryMethod, NotificationData, CategoryPreference, DeliverySchedule,
    FamilyNotificationSettings, QuietHours
)


class PregnancyNotificationBase(BaseModel):
    """Base pregnancy notification schema"""
    type: PregnancyNotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    category: NotificationCategory
    data: Optional[NotificationData] = None
    delivery_methods: List[DeliveryMethod] = []
    scheduled_for: Optional[datetime] = None


class PregnancyNotificationCreate(PregnancyNotificationBase):
    """Schema for creating pregnancy notification"""
    user_id: str
    pregnancy_id: str


class PregnancyNotificationUpdate(BaseModel):
    """Schema for updating notification"""
    read_at: Optional[datetime] = None
    action_taken: Optional[str] = None


class PregnancyNotificationResponse(PregnancyNotificationBase):
    """Schema for pregnancy notification responses"""
    id: str
    user_id: str
    pregnancy_id: str
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    action_taken: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferencesBase(BaseModel):
    """Base notification preferences schema"""
    categories: List[CategoryPreference] = []
    delivery_schedule: Optional[DeliverySchedule] = None
    family_settings: Optional[FamilyNotificationSettings] = None
    quiet_hours: Optional[QuietHours] = None


class NotificationPreferencesCreate(NotificationPreferencesBase):
    """Schema for creating notification preferences"""
    user_id: str


class NotificationPreferencesUpdate(NotificationPreferencesBase):
    """Schema for updating notification preferences"""
    pass


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Schema for notification preferences responses"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyMessageBase(BaseModel):
    """Base family message schema"""
    recipient_type: str
    recipients: List[str]
    subject: Optional[str] = None
    message: str
    related_post_id: Optional[str] = None
    priority: str = "normal"


class FamilyMessageCreate(FamilyMessageBase):
    """Schema for creating family message"""
    pregnancy_id: str
    sender_id: str


class FamilyMessageResponse(FamilyMessageBase):
    """Schema for family message responses"""
    id: str
    pregnancy_id: str
    sender_id: str
    read_by: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True