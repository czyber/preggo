from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.models.baby_development import TrimesterType


class BabyDevelopmentBase(BaseModel):
    """Base baby development schema"""
    day_of_pregnancy: int = Field(ge=1, le=310, description="Day of pregnancy (1-310)")
    baby_size_comparison: str = Field(max_length=200, description="Size comparison")
    baby_length_cm: Optional[float] = Field(None, ge=0, description="Baby length in centimeters")
    baby_weight_grams: Optional[float] = Field(None, ge=0, description="Baby weight in grams")
    title: str = Field(max_length=300, description="Catchy daily title")
    brief_description: str = Field(max_length=500, description="Brief description for cards")
    detailed_description: str = Field(description="Comprehensive development information")
    development_highlights: List[str] = Field(default_factory=list, description="Key developments")
    symptoms_to_expect: List[str] = Field(default_factory=list, description="Common symptoms")
    medical_milestones: List[str] = Field(default_factory=list, description="Medical checkpoints")
    mother_changes: str = Field(description="Changes in mother's body")
    tips_and_advice: str = Field(description="Helpful tips for this stage")
    emotional_notes: str = Field(description="Emotional/psychological aspects")
    partner_tips: str = Field(description="Advice for partners")
    fun_fact: str = Field(max_length=1000, description="Interesting trivia")
    
    @validator('development_highlights', 'symptoms_to_expect', 'medical_milestones')
    def validate_list_items(cls, v):
        """Ensure list items are non-empty strings"""
        if v:
            return [item.strip() for item in v if item and item.strip()]
        return []


class BabyDevelopmentCreate(BabyDevelopmentBase):
    """Schema for creating baby development records"""
    content_version: str = Field(default="1.0", description="Content version")
    is_active: bool = Field(default=True, description="Whether record is active")


class BabyDevelopmentUpdate(BaseModel):
    """Schema for updating baby development records"""
    baby_size_comparison: Optional[str] = Field(None, max_length=200)
    baby_length_cm: Optional[float] = Field(None, ge=0)
    baby_weight_grams: Optional[float] = Field(None, ge=0)
    title: Optional[str] = Field(None, max_length=300)
    brief_description: Optional[str] = Field(None, max_length=500)
    detailed_description: Optional[str] = None
    development_highlights: Optional[List[str]] = None
    symptoms_to_expect: Optional[List[str]] = None
    medical_milestones: Optional[List[str]] = None
    mother_changes: Optional[str] = None
    tips_and_advice: Optional[str] = None
    emotional_notes: Optional[str] = None
    partner_tips: Optional[str] = None
    fun_fact: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    content_version: Optional[str] = None
    
    @validator('development_highlights', 'symptoms_to_expect', 'medical_milestones')
    def validate_list_items(cls, v):
        """Ensure list items are non-empty strings"""
        if v is not None:
            return [item.strip() for item in v if item and item.strip()]
        return v


class BabyDevelopmentResponse(BabyDevelopmentBase):
    """Schema for baby development responses"""
    id: str
    week_number: int = Field(description="Calculated week number")
    trimester: TrimesterType = Field(description="Calculated trimester")
    is_active: bool
    content_version: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BabyDevelopmentSummary(BaseModel):
    """Lightweight schema for listing baby developments"""
    id: str
    day_of_pregnancy: int
    week_number: int
    trimester: TrimesterType
    title: str
    brief_description: str
    baby_size_comparison: str
    baby_length_cm: Optional[float]
    baby_weight_grams: Optional[float]
    is_active: bool
    
    class Config:
        from_attributes = True


class BabyDevelopmentByWeek(BaseModel):
    """Schema for grouping developments by week"""
    week_number: int
    trimester: TrimesterType
    developments: List[BabyDevelopmentSummary]
    
    
class BabyDevelopmentByTrimester(BaseModel):
    """Schema for grouping developments by trimester"""
    trimester: TrimesterType
    weeks: List[BabyDevelopmentByWeek]


class BabyDevelopmentStats(BaseModel):
    """Statistics about baby development data"""
    total_days: int
    days_per_trimester: dict[int, int]
    weeks_covered: int
    last_updated: Optional[datetime]
    active_records: int
    inactive_records: int


class BabyDevelopmentSearch(BaseModel):
    """Schema for searching baby development records"""
    week_number: Optional[int] = Field(None, ge=1, le=45)
    trimester: Optional[TrimesterType] = None
    day_range_start: Optional[int] = Field(None, ge=1, le=310)
    day_range_end: Optional[int] = Field(None, ge=1, le=310)
    search_text: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    
    @validator('day_range_end')
    def validate_day_range(cls, v, values):
        """Ensure end date is after start date"""
        if v is not None and 'day_range_start' in values and values['day_range_start'] is not None:
            if v < values['day_range_start']:
                raise ValueError('day_range_end must be greater than or equal to day_range_start')
        return v