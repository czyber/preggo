# Database Schema Documentation

## Overview

This document outlines the complete database schema for the Preggo pregnancy tracking application. The schema is designed for PostgreSQL/Supabase and includes comprehensive models for pregnancy tracking, family sharing, content management, and health monitoring.

## Migration Information

- **Migration File**: `54584cc27ecc_create_complete_pregnancy_tracking_.py`
- **Created**: August 3, 2025
- **Purpose**: Initial schema creation for all pregnancy tracking features
- **Tables Created**: 32 tables covering all aspects of the application

## Core Database Principles

### Primary Keys
- All tables use UUID primary keys for better scalability and security
- UUIDs are generated using Python's `uuid.uuid4()` function

### JSON Storage
- Complex nested data is stored as JSONB columns for flexibility
- Examples: user preferences, pregnancy details, notification settings

### Timestamps
- All tables include `created_at` and `updated_at` timestamps
- Timestamps are stored in UTC and managed automatically

### Foreign Keys
- Proper referential integrity with foreign key constraints
- Cascading deletes where appropriate

## Schema Organization

### 1. Core User Models

#### users
- **Purpose**: Main user accounts
- **Key Fields**: 
  - `id` (UUID, PK)
  - `email` (unique, indexed)
  - `first_name`, `last_name`
  - `profile_image` (URL)
  - `timezone`
  - `preferences` (JSONB)
- **Relationships**: One-to-many with pregnancies, posts, etc.

#### notification_preferences
- **Purpose**: User notification settings
- **Key Fields**:
  - `user_id` (FK to users, unique)
  - `categories` (JSONB array)
  - `delivery_schedule` (JSONB)
  - `family_settings` (JSONB)
- **Relationships**: One-to-one with users

### 2. Pregnancy Core Models

#### pregnancies
- **Purpose**: Main pregnancy records
- **Key Fields**:
  - `id` (UUID, PK)
  - `user_id` (FK to users)
  - `partner_ids` (JSONB array)
  - `pregnancy_details` (JSONB)
  - `preferences` (JSONB)
  - `status` (enum: active, completed, archived)
- **Relationships**: Central hub - connects to all other pregnancy-related data

#### weekly_updates
- **Purpose**: Week-by-week pregnancy information
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `week` (0-42)
  - `baby_development`, `maternal_changes`
  - `tips`, `common_symptoms` (JSONB arrays)
  - Baby size information

### 3. Family & Sharing Models

#### family_groups
- **Purpose**: Organize family members into groups (immediate, extended, friends)
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `name`, `type` (enum)
  - `permissions`, `custom_settings` (JSONB)

#### family_members
- **Purpose**: Individual family members within groups
- **Key Fields**:
  - `user_id` (FK to users)
  - `pregnancy_id` (FK to pregnancies)
  - `group_id` (FK to family_groups)
  - `relationship` (enum), `role` (enum)
  - `permissions` (JSONB array)
  - `status` (enum)

#### family_invitations
- **Purpose**: Manage invitations to join family groups
- **Key Fields**:
  - `email`, `relationship`, `role`
  - `expires_at`, `status`
  - `message` (optional personal message)

#### emergency_contacts
- **Purpose**: Emergency contact information
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `name`, `relationship`
  - `phone_primary`, `phone_secondary`, `email`
  - `priority` (1-10), permissions

### 4. Content & Social Models

#### posts
- **Purpose**: Main content sharing (updates, photos, milestones)
- **Key Fields**:
  - `author_id` (FK to users)
  - `pregnancy_id` (FK to pregnancies)
  - `type` (enum: milestone, weekly_update, belly_photo, etc.)
  - `content` (JSONB)
  - `privacy` (JSONB)
  - Engagement counters (denormalized for performance)

#### media_items
- **Purpose**: Photos, videos, audio files
- **Key Fields**:
  - `type` (enum: image, video, audio)
  - `url`, `thumbnail_url`, `filename`, `size`
  - `post_id` (FK to posts)
  - `media_metadata` (JSONB) - Note: renamed from 'metadata' to avoid SQLModel conflicts

#### comments
- **Purpose**: Comments on posts
- **Key Fields**:
  - `post_id` (FK to posts)
  - `user_id` (FK to users)
  - `parent_id` (FK to comments, for threaded replies)
  - `content`, `mentions` (JSONB array)

#### reactions
- **Purpose**: Emoji reactions to posts and comments
- **Key Fields**:
  - `user_id` (FK to users)
  - `post_id` or `comment_id` (FK, mutually exclusive)
  - `type` (enum: love, excited, care, support, etc.)

#### post_views, post_shares
- **Purpose**: Analytics and sharing tracking
- **Key Fields**: User, post, timestamp, additional metadata

### 5. Milestone & Health Models

#### milestones
- **Purpose**: Pregnancy milestones (first heartbeat, gender reveal, etc.)
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `type` (enum), `week`, `title`, `description`
  - `completed`, `completed_at`
  - `celebration_post_id` (FK to posts)
  - `shared_with` (JSONB array)

#### appointments
- **Purpose**: Medical appointments
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `type` (enum), `title`
  - `appointment_date` (renamed from 'date' to avoid conflicts)
  - `provider`, `location`
  - `results` (JSONB array of AppointmentResult objects)
  - Family sharing settings

#### important_dates, weekly_checklists
- **Purpose**: Timeline management and task tracking

### 6. Health Tracking Models

#### pregnancy_health
- **Purpose**: Main health tracking record per pregnancy
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies, unique)
  - `current_metrics` (JSONB - HealthSnapshot)
  - `sharing` (JSONB - HealthSharingSettings)
  - `alerts` (JSONB array)

#### symptom_tracking, weight_entries, mood_entries
- **Purpose**: Detailed health data tracking
- **Key Fields**: Pregnancy ID, week, date, specific measurements

#### health_alerts
- **Purpose**: Health warnings and reminders
- **Key Fields**: Type, severity, acknowledgment status

### 7. Memory & Timeline Models

#### memory_books
- **Purpose**: Generated memory books for pregnancies
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `title`, `cover` (JSONB), `settings` (JSONB)
  - `contributors` (JSONB array of user IDs)
  - `status` (enum: draft, generating, ready, shared)

#### memory_chapters, memory_content
- **Purpose**: Organize memory book content
- **Key Fields**: Book/chapter hierarchy, content types, ordering

#### family_timelines, timeline_entries
- **Purpose**: Generated family timelines
- **Key Fields**: 
  - Timeline entries with `entry_date` (renamed from 'date')
  - Entry types, importance levels

### 8. Notification Models

#### pregnancy_notifications
- **Purpose**: All notifications in the system
- **Key Fields**:
  - `user_id` (FK to users)
  - `pregnancy_id` (FK to pregnancies)
  - `type` (enum - comprehensive notification types)
  - `category`, `priority`
  - `data` (JSONB - additional context)
  - Delivery and read tracking

#### family_messages
- **Purpose**: Direct messages between family members
- **Key Fields**:
  - `pregnancy_id` (FK to pregnancies)
  - `sender_id` (FK to users)
  - `recipients` (JSONB array)
  - `read_by` (JSONB array with timestamps)

## Key Design Decisions

### 1. Field Name Conflicts Resolution
Several fields were renamed to avoid Python/SQLModel reserved word conflicts:
- `metadata` → `media_metadata` (in MediaItem)
- `date` → `appointment_date` (in Appointment)
- `date` → `event_date` (in ImportantDate)
- `date` → `entry_date` (in TimelineEntry)

### 2. JSONB Usage
Extensive use of JSONB for flexible data storage:
- User preferences and settings
- Pregnancy details with nested baby information
- Post content and privacy settings
- Health metrics and sharing preferences
- Notification data and preferences

### 3. Enum Usage
Comprehensive enums for consistency:
- User roles and permissions
- Content types and visibility levels
- Health tracking categories
- Notification types and priorities

### 4. Relationship Patterns
- **One-to-Many**: User → Pregnancies, Pregnancy → Posts
- **Many-to-Many**: Users ↔ Family Groups (via family_members)
- **Self-Referencing**: Comments (threaded replies)
- **Polymorphic**: Reactions (posts or comments)

## Performance Considerations

### Indexes
- Email index on users table
- Name index on items table (existing)
- Foreign key indexes automatically created
- Additional indexes may be needed based on query patterns

### Denormalization
- Engagement counters on posts (reaction_count, comment_count, view_count)
- Avoids expensive COUNT queries on related tables

### JSON Query Optimization
- PostgreSQL JSONB supports efficient querying
- GIN indexes can be added for frequently queried JSON paths

## Supabase-Specific Features

### Row Level Security (RLS)
Ready for RLS policies:
- User-based access control
- Pregnancy-based data isolation
- Family group permissions

### Realtime Subscriptions
Tables suitable for realtime:
- posts (new family updates)
- comments and reactions (engagement)
- pregnancy_notifications (live notifications)
- family_messages (chat functionality)

### Storage Integration
- Media items reference Supabase Storage URLs
- Structured for automatic cleanup of unused files

## Migration Instructions

1. **Environment Setup**: Ensure DATABASE_URL points to your Supabase PostgreSQL database
2. **Run Migration**: `alembic upgrade head`
3. **Verify Creation**: Check Supabase dashboard for all 32 tables
4. **Enable RLS**: Set up Row Level Security policies as needed
5. **Enable Realtime**: Configure realtime subscriptions for relevant tables

## Data Integrity

### Constraints
- NOT NULL constraints on essential fields
- Check constraints on enum values
- Foreign key constraints for referential integrity
- Unique constraints where appropriate

### Cascading
- Designed for safe cascading deletes
- Orphaned records are prevented through proper FK relationships

## Future Considerations

### Scaling
- UUID primary keys support horizontal scaling
- JSONB allows schema evolution without migrations
- Partitioning potential for large datasets

### Extensions
- Schema supports easy addition of new features
- Modular design allows independent feature development
- Versioning support through migration system

This schema provides a robust foundation for the Preggo pregnancy tracking application, supporting all features outlined in the PROJECT_OUTLINE.md while maintaining flexibility for future enhancements.