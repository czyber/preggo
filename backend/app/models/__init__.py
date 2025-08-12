# Database models

# Import all models for Alembic to detect them
from .user import User, UserPreferences, NotificationSettings, DefaultPrivacyLevel, SharingDefaults
from .pregnancy import Pregnancy, PregnancyDetails, BabyInfo, WeeklyUpdate, RiskLevel, PregnancyStatus, BabyGender, PregnancyPreferences
from .baby_development import BabyDevelopment, TrimesterType
from .family import (
    FamilyGroup, FamilyMember, FamilyInvitation, EmergencyContact,
    GroupType, RelationshipType, MemberRole, MemberPermission, MemberStatus, InvitationStatus,
    GroupPermissions, GroupSettings, MemberPreferences
)
from .content import (
    Post, PostContent, PostPrivacy, MediaItem, MediaMetadata, Comment, Reaction, PostView, PostShare, FeedActivity,
    PostType, MoodType, VisibilityLevel, PostStatus, ReactionType, MediaType
)
from .milestone import (
    Milestone, Appointment, ImportantDate, WeeklyChecklist, AppointmentResult,
    MilestoneType, AppointmentType
)
from .memory import (
    MemoryBook, MemoryChapter, MemoryContent, FamilyTimeline, TimelineEntry,
    MemoryBookStatus, MemoryContentType, TimelineEntryType, TimelineImportance,
    MemoryBookTheme, MemoryBookFormat, MemoryBookCover, TimeframeFilter, MemoryBookSettings
)
from .notification import (
    PregnancyNotification, NotificationPreferences, FamilyMessage,
    PregnancyNotificationType, NotificationCategory, NotificationPriority, DeliveryMethod,
    NotificationFrequency, NotificationData, CategoryPreference, DeliverySchedule,
    FamilyNotificationSettings, QuietHours
)
from .health import (
    PregnancyHealth, HealthAlert, SymptomTracking, WeightEntry, MoodEntry,
    EnergyLevel, SymptomFrequency, SymptomTrend, WeightTrend, WeightRange,
    WeightTracking, SymptomSummary, MoodTracking, SleepSummary, UpcomingAppointment,
    HealthSnapshot, HealthSharingSettings
)
from .circle_patterns import (
    CirclePattern, UserCirclePattern, CirclePatternUsage, PatternSuggestion,
    PatternSuggestionSource, PatternConfiguration, UserPatternPreferences, SuggestionContext,
    SYSTEM_DEFAULT_PATTERNS
)

# Keep the existing imports
from .item import Item
from .log import Log
