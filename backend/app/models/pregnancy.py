from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime, date
import uuid
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PregnancyStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class BabyGender(str, Enum):
    BOY = "boy"
    GIRL = "girl"
    UNKNOWN = "unknown"
    SURPRISE = "surprise"


class BabyInfo(SQLModel):
    """Information about expected baby(ies)"""
    name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[BabyGender] = None
    estimated_weight: Optional[float] = None  # in grams
    notes: Optional[str] = None


class PregnancyDetails(SQLModel):
    """Detailed pregnancy information"""
    due_date: date
    conception_date: Optional[date] = None
    current_week: int = Field(ge=0, le=42)
    current_day: int = Field(ge=0, le=6)
    trimester: int = Field(ge=1, le=3)
    is_multiple: bool = False
    expected_babies: List[BabyInfo] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW


class PregnancyPreferences(SQLModel):
    """Pregnancy-specific preferences"""
    share_weekly_updates: bool = True
    auto_generate_milestones: bool = True
    include_health_data: bool = False
    allow_family_contributions: bool = True
    default_photo_sharing: str = "immediate"  # family group level
    reminder_frequency: str = "weekly"


class Pregnancy(SQLModel, table=True):
    """Main pregnancy model"""
    __tablename__ = "pregnancies"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID primary key"
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="Primary pregnant person")
    partner_ids: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Partners/spouses user IDs"
    )
    
    # Pregnancy details stored as JSONB
    pregnancy_details: PregnancyDetails = Field(
        sa_column=Column(JSON),
        description="Detailed pregnancy information"
    )
    
    # Preferences stored as JSONB
    preferences: PregnancyPreferences = Field(
        default_factory=PregnancyPreferences,
        sa_column=Column(JSON),
        description="Pregnancy-specific preferences"
    )
    
    # Status and metadata
    status: PregnancyStatus = PregnancyStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class WeeklyUpdate(SQLModel, table=True):
    """Weekly pregnancy development information"""
    __tablename__ = "weekly_updates"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Reference to pregnancy
    pregnancy_id: str = Field(foreign_key="pregnancies.id")
    
    # Week information
    week: int = Field(ge=0, le=42, description="Pregnancy week number")
    
    # Development information
    baby_development: str = Field(description="Baby development description")
    maternal_changes: str = Field(description="Maternal changes description")
    
    # Tips and recommendations stored as JSON arrays
    tips: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Pregnancy tips for the week"
    )
    common_symptoms: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Common symptoms for the week"
    )
    appointment_recommendations: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Recommended appointments for the week"
    )
    
    # Baby size information
    baby_size_length: Optional[float] = Field(default=None, description="Baby length in cm")
    baby_size_weight: Optional[float] = Field(default=None, description="Baby weight in grams")
    baby_size_comparison: Optional[str] = Field(default=None, description="Size comparison (e.g., 'size of a blueberry')")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }