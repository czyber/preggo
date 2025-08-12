from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column, Relationship
from datetime import datetime, date
import uuid
from enum import Enum


class GroupType(str, Enum):
    IMMEDIATE_FAMILY = "immediate_family"  # Parents, siblings
    EXTENDED_FAMILY = "extended_family"    # Grandparents, aunts, uncles
    FRIENDS = "friends"                    # Close friends
    SUPPORT_CIRCLE = "support_circle"      # Support group, mentors


class RelationshipType(str, Enum):
    PARTNER = "partner"
    MOTHER = "mother"
    FATHER = "father"
    SISTER = "sister"
    BROTHER = "brother"
    MOTHER_IN_LAW = "mother_in_law"
    FATHER_IN_LAW = "father_in_law"
    GRANDMOTHER = "grandmother"
    GRANDFATHER = "grandfather"
    AUNT = "aunt"
    UNCLE = "uncle"
    FRIEND = "friend"
    MENTOR = "mentor"
    OTHER = "other"


class MemberRole(str, Enum):
    ADMIN = "admin"           # Can manage group, invite others
    CONTRIBUTOR = "contributor"  # Can post, comment, react
    VIEWER = "viewer"         # Can only view and react


class MemberPermission(str, Enum):
    VIEW_POSTS = "view_posts"
    CREATE_POSTS = "create_posts"
    COMMENT = "comment"
    REACT = "react"
    VIEW_MILESTONES = "view_milestones"
    VIEW_APPOINTMENTS = "view_appointments"
    VIEW_PHOTOS = "view_photos"
    DOWNLOAD_PHOTOS = "download_photos"
    RECEIVE_UPDATES = "receive_updates"
    INVITE_OTHERS = "invite_others"


class MemberStatus(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    PENDING = "pending"
    INACTIVE = "inactive"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class GroupPermissions(SQLModel):
    """Permissions for a family group"""
    allow_posts: bool = True
    allow_comments: bool = True
    allow_reactions: bool = True
    allow_photo_uploads: bool = True
    allow_milestone_sharing: bool = True
    require_approval_for_posts: bool = False


class GroupSettings(SQLModel):
    """Custom settings for a family group"""
    notification_frequency: str = "immediate"  # immediate, daily, weekly
    auto_include_new_content: bool = True
    allow_member_invites: bool = False  # Only admins can invite by default
    content_moderation: bool = False


class MemberPreferences(SQLModel):
    """Individual member preferences within a family group"""
    notification_enabled: bool = True
    email_updates: bool = True
    push_notifications: bool = True
    weekly_digest: bool = True
    milestone_alerts: bool = True


class FamilyGroup(SQLModel, table=True):
    """Family groups for organizing pregnancy sharing"""
    __tablename__ = "family_groups"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Reference to pregnancy
    pregnancy_id: str = Field(foreign_key="pregnancies.id")
    
    # Group information
    name: str = Field(description="Group name (e.g., 'Immediate Family')")
    description: Optional[str] = Field(default=None, description="Group description")
    type: GroupType = Field(description="Type of family group")
    
    # Group settings stored as JSONB
    permissions: GroupPermissions = Field(
        default_factory=GroupPermissions,
        sa_column=Column(JSON),
        description="Group permissions and rules"
    )
    custom_settings: GroupSettings = Field(
        default_factory=GroupSettings,
        sa_column=Column(JSON),
        description="Custom group settings"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FamilyMember(SQLModel, table=True):
    """Individual family members within groups"""
    __tablename__ = "family_members"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    user_id: str = Field(foreign_key="users.id", description="User ID of family member")
    pregnancy_id: str = Field(foreign_key="pregnancies.id", description="Associated pregnancy")
    group_id: str = Field(foreign_key="family_groups.id", description="Family group")
    
    # Member information
    relationship: RelationshipType = Field(description="Relationship to pregnant person")
    custom_title: Optional[str] = Field(default=None, description="Custom title like 'Grandma Mary'")
    role: MemberRole = Field(description="Member role and permissions level")
    
    # Permissions stored as JSON array
    permissions: List[MemberPermission] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Specific permissions for this member"
    )
    
    # Member preferences
    preferences: MemberPreferences = Field(
        default_factory=MemberPreferences,
        sa_column=Column(JSON),
        description="Member's notification and interaction preferences"
    )
    
    # Status and metadata
    status: MemberStatus = MemberStatus.ACTIVE
    invited_by: str = Field(foreign_key="users.id", description="User who invited this member")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FamilyInvitation(SQLModel, table=True):
    """Invitations to join family groups"""
    __tablename__ = "family_invitations"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Relationships
    pregnancy_id: str = Field(foreign_key="pregnancies.id")
    group_id: str = Field(foreign_key="family_groups.id")
    invited_by: str = Field(foreign_key="users.id", description="User who sent the invitation")
    
    # Invitation details
    email: Optional[str] = Field(default=None, description="Email address of invitee (optional for link invites)")
    relationship: RelationshipType = Field(description="Expected relationship")
    custom_title: Optional[str] = Field(default=None, description="Custom title for invitee")
    role: MemberRole = Field(description="Intended role for invitee")
    message: Optional[str] = Field(default=None, description="Personal message with invitation")
    
    # Token-based invite support
    token: Optional[str] = Field(default=None, index=True, unique=True, description="Secure token for invite links")
    
    # Status and timing
    status: InvitationStatus = InvitationStatus.PENDING
    expires_at: datetime = Field(description="When invitation expires")
    accepted_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmergencyContact(SQLModel, table=True):
    """Emergency contacts for pregnancy"""
    __tablename__ = "emergency_contacts"
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4())
    )
    
    # Reference to pregnancy
    pregnancy_id: str = Field(foreign_key="pregnancies.id")
    
    # Contact information
    name: str = Field(description="Emergency contact name")
    relationship: str = Field(description="Relationship to pregnant person")
    phone_primary: str = Field(description="Primary phone number")
    phone_secondary: Optional[str] = Field(default=None, description="Secondary phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    
    # Priority and access
    priority: int = Field(ge=1, le=10, description="Contact priority (1 = highest)")
    can_view_all_updates: bool = Field(default=False, description="Can view all pregnancy updates")
    notify_on_emergency: bool = Field(default=True, description="Notify in case of emergency")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


