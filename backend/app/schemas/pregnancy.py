from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from app.models.pregnancy import PregnancyDetails, PregnancyPreferences, PregnancyStatus, BabyInfo


class PregnancyBase(BaseModel):
    """Base pregnancy schema"""
    pregnancy_details: PregnancyDetails
    preferences: Optional[PregnancyPreferences] = None


class PregnancyCreate(PregnancyBase):
    """Schema for creating a new pregnancy"""
    partner_ids: Optional[List[str]] = None


class PregnancyUpdate(BaseModel):
    """Schema for updating pregnancy information"""
    partner_ids: Optional[List[str]] = None
    pregnancy_details: Optional[PregnancyDetails] = None
    preferences: Optional[PregnancyPreferences] = None
    status: Optional[PregnancyStatus] = None


class PregnancyResponse(PregnancyBase):
    """Schema for pregnancy responses"""
    id: str
    user_id: str
    partner_ids: List[str]
    status: PregnancyStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyUpdateBase(BaseModel):
    """Base weekly update schema"""
    week: int
    baby_development: str
    maternal_changes: str
    tips: List[str] = []
    common_symptoms: List[str] = []
    appointment_recommendations: Optional[List[str]] = None
    baby_size_length: Optional[float] = None
    baby_size_weight: Optional[float] = None
    baby_size_comparison: Optional[str] = None


class WeeklyUpdateCreate(WeeklyUpdateBase):
    """Schema for creating weekly updates"""
    pregnancy_id: str


class WeeklyUpdateResponse(WeeklyUpdateBase):
    """Schema for weekly update responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True