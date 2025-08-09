from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Index
from datetime import datetime
import uuid
from enum import Enum


class TrimesterType(int, Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3


class BabyDevelopment(SQLModel, table=True):
    """Daily baby development information for pregnancy tracking"""
    __tablename__ = "baby_development"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID primary key"
    )
    
    # Core day tracking fields
    day_of_pregnancy: int = Field(
        ge=1, 
        le=310,  # Full term (280 days) + extra month for safety
        unique=True,
        index=True,
        description="Day of pregnancy (1-310)"
    )
    week_number: int = Field(
        ge=1,
        le=45,
        index=True,
        description="Week of pregnancy calculated from day (1-45)"
    )
    trimester: TrimesterType = Field(
        index=True,
        description="Trimester number (1-3)"
    )
    
    # Baby size and measurements
    baby_size_comparison: str = Field(
        max_length=200,
        description="Size comparison (e.g., 'poppy seed', 'blueberry', 'watermelon')"
    )
    baby_length_cm: Optional[float] = Field(
        default=None,
        ge=0,
        description="Approximate baby length in centimeters"
    )
    baby_weight_grams: Optional[float] = Field(
        default=None,
        ge=0,
        description="Approximate baby weight in grams"
    )
    
    # Content fields
    title: str = Field(
        max_length=300,
        description="Catchy daily title for the development stage"
    )
    brief_description: str = Field(
        max_length=500,
        description="1-2 sentences for card display"
    )
    detailed_description: str = Field(
        description="Comprehensive information for expanded view"
    )
    
    # JSON fields for structured data
    development_highlights: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Array of key developmental milestones for this day"
    )
    symptoms_to_expect: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Array of common symptoms the mother might experience"
    )
    medical_milestones: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Array of important medical checkpoints or milestones"
    )
    
    # Text fields for detailed information
    mother_changes: str = Field(
        description="What's happening to the mother's body at this stage"
    )
    tips_and_advice: str = Field(
        description="Helpful tips and advice for this stage of pregnancy"
    )
    emotional_notes: str = Field(
        description="Emotional and psychological aspects of this pregnancy stage"
    )
    partner_tips: str = Field(
        description="Advice and tips specifically for partners"
    )
    
    # Fun and engaging content
    fun_fact: str = Field(
        max_length=1000,
        description="Interesting trivia about baby development at this stage"
    )
    
    # Metadata
    is_active: bool = Field(default=True, description="Whether this record is active")
    content_version: str = Field(default="1.0", description="Version of the content")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Create indexes for efficient querying
    __table_args__ = (
        Index('ix_baby_development_day', 'day_of_pregnancy'),
        Index('ix_baby_development_week', 'week_number'),
        Index('ix_baby_development_trimester', 'trimester'),
        Index('ix_baby_development_active', 'is_active'),
        Index('ix_baby_development_week_trimester', 'week_number', 'trimester'),
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def __init__(self, **data):
        # Auto-calculate week_number and trimester from day_of_pregnancy before calling super()
        if 'day_of_pregnancy' in data and data['day_of_pregnancy']:
            day = data['day_of_pregnancy']
            data['week_number'] = ((day - 1) // 7) + 1
            
            if data['week_number'] <= 12:
                data['trimester'] = TrimesterType.FIRST
            elif data['week_number'] <= 27:
                data['trimester'] = TrimesterType.SECOND
            else:
                data['trimester'] = TrimesterType.THIRD
        
        super().__init__(**data)