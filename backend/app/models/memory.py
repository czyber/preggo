from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime, date
import uuid
from enum import Enum


class MemoryBookStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SHARED = "shared"


class MemoryContentType(str, Enum):
    POST = "post"
    PHOTO = "photo"
    MILESTONE = "milestone"
    QUOTE = "quote"
    TEXT = "text"


class TimelineEntryType(str, Enum):
    POST = "post"
    MILESTONE = "milestone"
    APPOINTMENT = "appointment"
    WEEK_CHANGE = "week_change"


class TimelineImportance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MemoryBookTheme(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    PLAYFUL = "playful"
    ELEGANT = "elegant"


class MemoryBookFormat(str, Enum):
    DIGITAL = "digital"
    PRINT = "print"
    BOTH = "both"


class MemoryBookCover(SQLModel):
    """Cover design for memory book"""
    background_image: Optional[str] = None
    title: str = "Our Pregnancy Journey"
    subtitle: Optional[str] = None
    theme_color: str = "#f8bbd9"  # Default pink
    font_family: str = "serif"


class TimeframeFilter(SQLModel):
    """Timeframe specification for memory content"""
    start_week: Optional[int] = None
    end_week: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_all: bool = False


class MemoryBookSettings(SQLModel):
    """Settings for memory book generation and sharing"""
    theme: MemoryBookTheme = MemoryBookTheme.CLASSIC
    include_private_posts: bool = False
    include_comments: bool = True
    include_all_photos: bool = False
    auto_include_milestones: bool = True
    family_contributions: bool = True
    format: MemoryBookFormat = MemoryBookFormat.DIGITAL


class MemoryBook(SQLModel, table=True):
    """Digital memory books for pregnancy journey"""
    __tablename__ = "memory_books"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Book information
    title: str = Field(description="Memory book title")
    description: Optional[str] = Field(default=None, description="Book description")
    
    # Cover design stored as JSONB
    cover: MemoryBookCover = Field(
        default_factory=MemoryBookCover,
        sa_column=Column(JSON),
        description="Cover design and layout"
    )
    
    # Settings stored as JSONB
    settings: MemoryBookSettings = Field(
        default_factory=MemoryBookSettings,
        sa_column=Column(JSON),
        description="Book generation and sharing settings"
    )
    
    # Contributors and permissions
    contributors: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="User IDs who can add content to this book"
    )
    
    # Status
    status: MemoryBookStatus = MemoryBookStatus.DRAFT
    
    # Generated files
    generated_pdf_url: Optional[str] = Field(default=None, description="URL to generated PDF")
    generated_web_url: Optional[str] = Field(default=None, description="URL to web version")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class MemoryChapter(SQLModel, table=True):
    """Chapters within memory books"""
    __tablename__ = "memory_chapters"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    memory_book_id: str = Field(foreign_key="memory_books.id", description="Parent memory book")
    
    # Chapter information
    title: str = Field(description="Chapter title")
    description: Optional[str] = Field(default=None, description="Chapter description")
    order: int = Field(description="Chapter order within book")
    
    # Content filtering stored as JSONB
    timeframe: TimeframeFilter = Field(
        default_factory=TimeframeFilter,
        sa_column=Column(JSON),
        description="Timeframe filter for content inclusion"
    )
    
    # Generation settings
    auto_generated: bool = Field(default=True, description="Whether chapter content is auto-generated")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryContent(SQLModel, table=True):
    """Individual content items within memory chapters"""
    __tablename__ = "memory_content"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    memory_chapter_id: str = Field(foreign_key="memory_chapters.id", description="Parent chapter")
    
    # Content information
    type: MemoryContentType = Field(description="Type of memory content")
    source_id: Optional[str] = Field(default=None, description="Source post ID, photo ID, etc.")
    custom_text: Optional[str] = Field(default=None, description="Custom text content")
    order: int = Field(description="Order within chapter")
    
    # Metadata
    included_by: str = Field(foreign_key="users.id", description="User who included this content")
    included_at: datetime = Field(default_factory=datetime.utcnow, description="When content was included")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FamilyTimeline(SQLModel, table=True):
    """Generated family timeline for pregnancies"""
    __tablename__ = "family_timelines"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    
    # Timeline settings
    grouped_by: str = Field(default="week", description="Grouping: week, month, milestone")
    
    # Privacy and access
    privacy_level: str = Field(default="all_family", description="Who can view this timeline")
    
    # Generation metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TimelineEntry(SQLModel, table=True):
    """Individual entries in family timelines"""
    __tablename__ = "timeline_entries"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    family_timeline_id: str = Field(foreign_key="family_timelines.id", description="Parent timeline")
    
    # Entry information
    type: TimelineEntryType = Field(description="Type of timeline entry")
    entry_date: datetime = Field(description="Date of the entry")
    week: int = Field(ge=0, le=42, description="Pregnancy week")
    title: str = Field(description="Entry title")
    summary: Optional[str] = Field(default=None, description="Entry summary")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail image URL")
    
    # Source references
    post_id: Optional[str] = Field(default=None, foreign_key="posts.id", description="Associated post")
    milestone_id: Optional[str] = Field(default=None, foreign_key="milestones.id", description="Associated milestone")
    
    # Importance and display
    importance: TimelineImportance = TimelineImportance.MEDIUM
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }