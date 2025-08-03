from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.memory import (
    MemoryBookStatus, MemoryContentType, TimelineEntryType, TimelineImportance,
    MemoryBookTheme, MemoryBookCover, TimeframeFilter, MemoryBookSettings
)


class MemoryBookBase(BaseModel):
    """Base memory book schema"""
    title: str
    description: Optional[str] = None
    cover: Optional[MemoryBookCover] = None
    settings: Optional[MemoryBookSettings] = None
    contributors: List[str] = []


class MemoryBookCreate(MemoryBookBase):
    """Schema for creating memory book"""
    pregnancy_id: str


class MemoryBookUpdate(BaseModel):
    """Schema for updating memory book"""
    title: Optional[str] = None
    description: Optional[str] = None
    cover: Optional[MemoryBookCover] = None
    settings: Optional[MemoryBookSettings] = None
    contributors: Optional[List[str]] = None
    status: Optional[MemoryBookStatus] = None


class MemoryBookResponse(MemoryBookBase):
    """Schema for memory book responses"""
    id: str
    pregnancy_id: str
    status: MemoryBookStatus
    generated_pdf_url: Optional[str]
    generated_web_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemoryChapterBase(BaseModel):
    """Base memory chapter schema"""
    title: str
    description: Optional[str] = None
    order: int
    timeframe: Optional[TimeframeFilter] = None
    auto_generated: bool = True


class MemoryChapterCreate(MemoryChapterBase):
    """Schema for creating memory chapter"""
    memory_book_id: str


class MemoryChapterUpdate(BaseModel):
    """Schema for updating memory chapter"""
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    timeframe: Optional[TimeframeFilter] = None


class MemoryChapterResponse(MemoryChapterBase):
    """Schema for memory chapter responses"""
    id: str
    memory_book_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemoryContentBase(BaseModel):
    """Base memory content schema"""
    type: MemoryContentType
    source_id: Optional[str] = None
    custom_text: Optional[str] = None
    order: int


class MemoryContentCreate(MemoryContentBase):
    """Schema for creating memory content"""
    memory_chapter_id: str
    included_by: str


class MemoryContentResponse(MemoryContentBase):
    """Schema for memory content responses"""
    id: str
    memory_chapter_id: str
    included_by: str
    included_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyTimelineBase(BaseModel):
    """Base family timeline schema"""
    grouped_by: str = "week"
    privacy_level: str = "all_family"


class FamilyTimelineCreate(FamilyTimelineBase):
    """Schema for creating family timeline"""
    pregnancy_id: str


class FamilyTimelineResponse(FamilyTimelineBase):
    """Schema for family timeline responses"""
    id: str
    pregnancy_id: str
    generated_at: datetime
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimelineEntryBase(BaseModel):
    """Base timeline entry schema"""
    type: TimelineEntryType
    entry_date: datetime
    week: int
    title: str
    summary: Optional[str] = None
    thumbnail: Optional[str] = None
    importance: TimelineImportance = TimelineImportance.MEDIUM


class TimelineEntryCreate(TimelineEntryBase):
    """Schema for creating timeline entry"""
    family_timeline_id: str
    post_id: Optional[str] = None
    milestone_id: Optional[str] = None


class TimelineEntryResponse(TimelineEntryBase):
    """Schema for timeline entry responses"""
    id: str
    family_timeline_id: str
    post_id: Optional[str]
    milestone_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True