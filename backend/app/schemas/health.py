from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from app.models.health import (
    EnergyLevel, SymptomFrequency, SymptomTrend,
    HealthSnapshot, HealthSharingSettings
)


class PregnancyHealthBase(BaseModel):
    """Base pregnancy health schema"""
    current_metrics: HealthSnapshot
    sharing: Optional[HealthSharingSettings] = None
    alerts: List[str] = []


class PregnancyHealthCreate(PregnancyHealthBase):
    """Schema for creating pregnancy health record"""
    pregnancy_id: str


class PregnancyHealthUpdate(BaseModel):
    """Schema for updating pregnancy health"""
    current_metrics: Optional[HealthSnapshot] = None
    sharing: Optional[HealthSharingSettings] = None
    alerts: Optional[List[str]] = None


class PregnancyHealthResponse(PregnancyHealthBase):
    """Schema for pregnancy health responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthAlertBase(BaseModel):
    """Base health alert schema"""
    type: str
    title: str
    message: str
    severity: str
    is_active: bool = True


class HealthAlertCreate(HealthAlertBase):
    """Schema for creating health alert"""
    pregnancy_health_id: str


class HealthAlertUpdate(BaseModel):
    """Schema for updating health alert"""
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class HealthAlertResponse(HealthAlertBase):
    """Schema for health alert responses"""
    id: str
    pregnancy_health_id: str
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    resolved: bool
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SymptomTrackingBase(BaseModel):
    """Base symptom tracking schema"""
    symptom_name: str
    severity: int
    frequency: SymptomFrequency
    week: int
    date_recorded: date
    notes: Optional[str] = None
    triggers: List[str] = []
    relief_methods: List[str] = []


class SymptomTrackingCreate(SymptomTrackingBase):
    """Schema for creating symptom tracking entry"""
    pregnancy_id: str


class SymptomTrackingResponse(SymptomTrackingBase):
    """Schema for symptom tracking responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeightEntryBase(BaseModel):
    """Base weight entry schema"""
    weight: float
    unit: str = "kg"
    week: int
    date_recorded: date
    notes: Optional[str] = None


class WeightEntryCreate(WeightEntryBase):
    """Schema for creating weight entry"""
    pregnancy_id: str
    recorded_by: str


class WeightEntryResponse(WeightEntryBase):
    """Schema for weight entry responses"""
    id: str
    pregnancy_id: str
    recorded_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MoodEntryBase(BaseModel):
    """Base mood entry schema"""
    mood: str
    mood_score: int
    week: int
    date_recorded: date
    notes: Optional[str] = None
    factors: List[str] = []


class MoodEntryCreate(MoodEntryBase):
    """Schema for creating mood entry"""
    pregnancy_id: str


class MoodEntryResponse(MoodEntryBase):
    """Schema for mood entry responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True