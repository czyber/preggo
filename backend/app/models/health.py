from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime, date
import uuid
from enum import Enum


class EnergyLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SymptomFrequency(str, Enum):
    RARE = "rare"
    OCCASIONAL = "occasional"
    FREQUENT = "frequent"
    DAILY = "daily"


class SymptomTrend(str, Enum):
    BETTER = "better"
    SAME = "same"
    WORSE = "worse"


class WeightTrend(str, Enum):
    NORMAL = "normal"
    FAST = "fast"
    SLOW = "slow"


class WeightRange(SQLModel):
    """Recommended weight gain range"""
    min_gain: float  # minimum recommended gain in kg/lbs
    max_gain: float  # maximum recommended gain in kg/lbs
    unit: str = "kg"  # kg or lbs


class WeightTracking(SQLModel):
    """Weight tracking information"""
    current: float
    starting_weight: float
    total_gain: float
    weekly_gain: float
    recommended_range: WeightRange
    trend: WeightTrend = WeightTrend.NORMAL


class SymptomSummary(SQLModel):
    """Summary of pregnancy symptoms"""
    symptom: str
    frequency: SymptomFrequency
    severity: int = Field(ge=1, le=5, description="Severity from 1-5")
    trending: SymptomTrend = SymptomTrend.SAME
    last_reported: datetime


class MoodTracking(SQLModel):
    """Mood tracking information"""
    current_mood: str
    mood_score: int = Field(ge=1, le=10, description="Mood score from 1-10")
    notes: Optional[str] = None
    last_updated: datetime


class SleepSummary(SQLModel):
    """Sleep tracking summary"""
    average_hours: float
    quality_score: int = Field(ge=1, le=10, description="Sleep quality from 1-10")
    common_issues: List[str] = Field(default_factory=list)
    last_updated: datetime


class UpcomingAppointment(SQLModel):
    """Summary of upcoming appointments"""
    appointment_id: str
    type: str
    appointment_date: datetime
    provider: str
    days_until: int


class HealthSnapshot(SQLModel):
    """Current health snapshot"""
    week: int = Field(ge=0, le=42)
    weight: WeightTracking
    symptoms: List[SymptomSummary] = Field(default_factory=list)
    mood: MoodTracking
    energy: EnergyLevel = EnergyLevel.NORMAL
    sleep: SleepSummary
    appointments: List[UpcomingAppointment] = Field(default_factory=list)
    last_updated: datetime


class HealthSharingSettings(SQLModel):
    """Health data sharing preferences"""
    share_weight_with_partner: bool = True
    share_symptom_summary_with_family: bool = False
    share_mood_with_support_circle: bool = False
    share_appointment_updates: bool = True
    auto_share_milestones: bool = True
    emergency_contacts_can_view_all: bool = False


class PregnancyHealth(SQLModel, table=True):
    """Pregnancy health tracking and metrics"""
    __tablename__ = "pregnancy_health"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", unique=True, description="Associated pregnancy")
    
    # Current health snapshot stored as JSONB
    current_metrics: HealthSnapshot = Field(
        sa_column=Column(JSON),
        description="Current health metrics and status"
    )
    
    # Sharing preferences stored as JSONB
    sharing: HealthSharingSettings = Field(
        default_factory=HealthSharingSettings,
        sa_column=Column(JSON),
        description="Health data sharing preferences"
    )
    
    # Health alerts and flags
    alerts: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Active health alerts and reminders"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthAlert(SQLModel, table=True):
    """Health alerts and reminders"""
    __tablename__ = "health_alerts"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_health_id: str = Field(foreign_key="pregnancy_health.id", description="Associated health record")
    
    # Alert details
    type: str = Field(description="Type of alert (weight_gain, symptom_severity, appointment_overdue)")
    title: str = Field(description="Alert title")
    message: str = Field(description="Alert message")
    severity: str = Field(description="low, medium, high, critical")
    
    # Alert status
    is_active: bool = Field(default=True, description="Whether alert is still active")
    acknowledged: bool = Field(default=False, description="Whether user has acknowledged alert")
    acknowledged_at: Optional[datetime] = Field(default=None)
    
    # Resolution
    resolved: bool = Field(default=False, description="Whether issue has been resolved")
    resolved_at: Optional[datetime] = Field(default=None)
    resolution_notes: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SymptomTracking(SQLModel, table=True):
    """Individual symptom tracking entries"""
    __tablename__ = "symptom_tracking"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Symptom details
    symptom_name: str = Field(description="Name of the symptom")
    severity: int = Field(ge=1, le=5, description="Severity from 1-5")
    frequency: SymptomFrequency = Field(description="How often symptom occurs")
    
    # Tracking information
    week: int = Field(ge=0, le=42, description="Pregnancy week when symptom was recorded")
    date_recorded: date = Field(description="Date symptom was recorded")
    notes: Optional[str] = Field(default=None, description="Additional notes about symptom")
    
    # Related factors
    triggers: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Potential triggers for the symptom"
    )
    relief_methods: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Methods that helped relieve the symptom"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class WeightEntry(SQLModel, table=True):
    """Individual weight tracking entries"""
    __tablename__ = "weight_entries"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Weight information
    weight: float = Field(description="Weight measurement")
    unit: str = Field(default="kg", description="Unit of measurement (kg or lbs)")
    week: int = Field(ge=0, le=42, description="Pregnancy week")
    date_recorded: date = Field(description="Date weight was recorded")
    
    # Additional metadata
    notes: Optional[str] = Field(default=None, description="Notes about weight measurement")
    recorded_by: str = Field(foreign_key="users.id", description="Who recorded this weight")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class MoodEntry(SQLModel, table=True):
    """Individual mood tracking entries"""
    __tablename__ = "mood_entries"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Mood information
    mood: str = Field(description="Mood description")
    mood_score: int = Field(ge=1, le=10, description="Mood score from 1-10")
    week: int = Field(ge=0, le=42, description="Pregnancy week")
    date_recorded: date = Field(description="Date mood was recorded")
    
    # Additional context
    notes: Optional[str] = Field(default=None, description="Notes about mood")
    factors: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Factors that influenced mood"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }