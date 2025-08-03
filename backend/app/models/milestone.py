from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime, date
import uuid
from enum import Enum


class MilestoneType(str, Enum):
    FIRST_HEARTBEAT = "first_heartbeat"
    FIRST_MOVEMENT = "first_movement"
    GENDER_REVEAL = "gender_reveal"
    BABY_SHOWER = "baby_shower"
    NURSERY_COMPLETE = "nursery_complete"
    HOSPITAL_BAG_PACKED = "hospital_bag_packed"
    MATERNITY_PHOTOS = "maternity_photos"
    NAME_CHOSEN = "name_chosen"
    FIRST_KICK = "first_kick"
    CUSTOM = "custom"


class AppointmentType(str, Enum):
    ROUTINE_CHECKUP = "routine_checkup"
    ULTRASOUND = "ultrasound"
    GLUCOSE_TEST = "glucose_test"
    SPECIALIST = "specialist"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"


class Milestone(SQLModel, table=True):
    """Pregnancy milestones and special moments"""
    __tablename__ = "milestones"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Milestone information
    type: MilestoneType = Field(description="Type of milestone")
    week: int = Field(ge=0, le=42, description="Pregnancy week when milestone occurs/occurred")
    title: str = Field(description="Milestone title")
    description: str = Field(description="Milestone description")
    
    # Status
    is_default: bool = Field(default=False, description="System vs custom milestone")
    completed: bool = Field(default=False, description="Whether milestone has been completed")
    completed_at: Optional[datetime] = Field(default=None, description="When milestone was completed")
    
    # Sharing and celebration
    celebration_post_id: Optional[str] = Field(
        default=None, 
        foreign_key="posts.id", 
        description="Post ID if shared as celebration"
    )
    shared_with: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Family group IDs this milestone is shared with"
    )
    
    # Additional content
    notes: Optional[str] = Field(default=None, description="Personal notes about milestone")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AppointmentResult(SQLModel):
    """Individual test results from appointments"""
    type: str = Field(description="Type of test/measurement")
    value: str = Field(description="Test result value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    is_normal: bool = Field(description="Whether result is within normal range")
    notes: Optional[str] = Field(default=None, description="Additional notes about result")


class Appointment(SQLModel, table=True):
    """Medical appointments during pregnancy"""
    __tablename__ = "appointments"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Appointment information
    type: AppointmentType = Field(description="Type of appointment")
    title: str = Field(description="Appointment title")
    appointment_date: datetime = Field(description="Appointment date and time")
    provider: str = Field(description="Healthcare provider name")
    location: Optional[str] = Field(default=None, description="Appointment location")
    
    # Appointment content
    notes: Optional[str] = Field(default=None, description="Personal notes about appointment")
    
    # Results stored as JSONB array
    results: List[AppointmentResult] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Test results and measurements from appointment"
    )
    
    # Family sharing
    share_with_family: bool = Field(default=False, description="Whether to share with family")
    shared_summary: Optional[str] = Field(
        default=None, 
        description="Summary to share with family (if different from notes)"
    )
    
    # Status tracking
    completed: bool = Field(default=False, description="Whether appointment has occurred")
    cancelled: bool = Field(default=False, description="Whether appointment was cancelled")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImportantDate(SQLModel, table=True):
    """Important dates in pregnancy timeline"""
    __tablename__ = "important_dates"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Date information
    event_date: date = Field(description="The important date")
    title: str = Field(description="Title of the important date")
    description: Optional[str] = Field(default=None, description="Description of what this date represents")
    category: str = Field(description="Category like 'appointment', 'milestone', 'preparation'")
    
    # Display and reminder settings
    is_reminder: bool = Field(default=False, description="Whether to send reminders")
    reminder_days_before: Optional[int] = Field(default=None, description="Days before to remind")
    
    # Sharing
    share_with_family: bool = Field(default=False, description="Share this date with family")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class WeeklyChecklist(SQLModel, table=True):
    """Weekly pregnancy checklists and tasks"""
    __tablename__ = "weekly_checklists"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Checklist item information
    week: int = Field(ge=0, le=42, description="Pregnancy week")
    task: str = Field(description="Task description")
    category: str = Field(description="Category: health, preparation, appointments, education")
    priority: str = Field(description="Priority: low, medium, high")
    
    # Status
    completed: bool = Field(default=False, description="Whether task is completed")
    completed_at: Optional[datetime] = Field(default=None, description="When task was completed")
    notes: Optional[str] = Field(default=None, description="Notes about completing the task")
    
    # Sharing
    share_with_family: bool = Field(default=False, description="Share completion with family")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }