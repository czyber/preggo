from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from app.models.milestone import MilestoneType, AppointmentType, AppointmentResult


class MilestoneBase(BaseModel):
    """Base milestone schema"""
    type: MilestoneType
    week: int
    title: str
    description: str
    is_default: bool = False
    notes: Optional[str] = None
    shared_with: List[str] = []


class MilestoneCreate(MilestoneBase):
    """Schema for creating a milestone"""
    pregnancy_id: str


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    notes: Optional[str] = None
    shared_with: Optional[List[str]] = None


class MilestoneResponse(MilestoneBase):
    """Schema for milestone responses"""
    id: str
    pregnancy_id: str
    completed: bool
    completed_at: Optional[datetime]
    celebration_post_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    """Base appointment schema"""
    type: AppointmentType
    title: str
    appointment_date: datetime
    provider: str
    location: Optional[str] = None
    notes: Optional[str] = None
    share_with_family: bool = False
    shared_summary: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    pregnancy_id: str


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    type: Optional[AppointmentType] = None
    title: Optional[str] = None
    appointment_date: Optional[datetime] = None
    provider: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    results: Optional[List[AppointmentResult]] = None
    share_with_family: Optional[bool] = None
    shared_summary: Optional[str] = None
    completed: Optional[bool] = None
    cancelled: Optional[bool] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment responses"""
    id: str
    pregnancy_id: str
    results: List[AppointmentResult]
    completed: bool
    cancelled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportantDateBase(BaseModel):
    """Base important date schema"""
    event_date: date
    title: str
    description: Optional[str] = None
    category: str
    is_reminder: bool = False
    reminder_days_before: Optional[int] = None
    share_with_family: bool = False


class ImportantDateCreate(ImportantDateBase):
    """Schema for creating important date"""
    pregnancy_id: str


class ImportantDateResponse(ImportantDateBase):
    """Schema for important date responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyChecklistBase(BaseModel):
    """Base weekly checklist schema"""
    week: int
    task: str
    category: str
    priority: str
    share_with_family: bool = False


class WeeklyChecklistCreate(WeeklyChecklistBase):
    """Schema for creating weekly checklist item"""
    pregnancy_id: str


class WeeklyChecklistUpdate(BaseModel):
    """Schema for updating checklist item"""
    completed: Optional[bool] = None
    notes: Optional[str] = None


class WeeklyChecklistResponse(WeeklyChecklistBase):
    """Schema for weekly checklist responses"""
    id: str
    pregnancy_id: str
    completed: bool
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True