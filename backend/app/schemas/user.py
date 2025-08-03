from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserPreferences, DefaultPrivacyLevel


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    timezone: str = "UTC"


class UserCreate(UserBase):
    """Schema for creating a new user"""
    preferences: Optional[UserPreferences] = None


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: str
    preferences: UserPreferences
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user information for family sharing"""
    id: str
    first_name: str
    last_name: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True