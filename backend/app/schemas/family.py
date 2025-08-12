from typing import Optional, List
from pydantic import BaseModel, EmailStr
from typing import Union
from datetime import datetime
from app.models.family import (
    GroupType, RelationshipType, MemberRole, MemberPermission, MemberStatus,
    InvitationStatus, GroupPermissions, GroupSettings, MemberPreferences
)


class FamilyGroupBase(BaseModel):
    """Base family group schema"""
    name: str
    description: Optional[str] = None
    type: GroupType
    permissions: Optional[GroupPermissions] = None
    custom_settings: Optional[GroupSettings] = None


class FamilyGroupCreate(FamilyGroupBase):
    """Schema for creating a family group"""
    pregnancy_id: str


class FamilyGroupUpdate(BaseModel):
    """Schema for updating family group"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[GroupPermissions] = None
    custom_settings: Optional[GroupSettings] = None


class FamilyGroupResponse(FamilyGroupBase):
    """Schema for family group responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyMemberBase(BaseModel):
    """Base family member schema"""
    relationship: RelationshipType
    custom_title: Optional[str] = None
    role: MemberRole
    permissions: List[MemberPermission] = []
    preferences: Optional[MemberPreferences] = None


class FamilyMemberCreate(FamilyMemberBase):
    """Schema for adding family member"""
    user_id: str
    pregnancy_id: str
    group_id: str


class FamilyMemberUpdate(BaseModel):
    """Schema for updating family member"""
    relationship: Optional[RelationshipType] = None
    custom_title: Optional[str] = None
    role: Optional[MemberRole] = None
    permissions: Optional[List[MemberPermission]] = None
    preferences: Optional[MemberPreferences] = None
    status: Optional[MemberStatus] = None


class FamilyMemberResponse(FamilyMemberBase):
    """Schema for family member responses"""
    id: str
    user_id: str
    pregnancy_id: str
    group_id: str
    status: MemberStatus
    invited_by: str
    joined_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FamilyInvitationBase(BaseModel):
    """Base family invitation schema"""
    email: Optional[EmailStr] = None  # Optional for link-based invites
    relationship: RelationshipType
    custom_title: Optional[str] = None
    role: MemberRole
    message: Optional[str] = None


class FamilyInvitationCreate(FamilyInvitationBase):
    """Schema for creating family invitation"""
    pregnancy_id: str
    group_id: str


class FamilyInvitationUpdate(BaseModel):
    """Schema for updating invitation status"""
    status: InvitationStatus


class FamilyInvitationLinkCreate(BaseModel):
    """Schema for creating link-based family invitation"""
    pregnancy_id: str
    relationship: RelationshipType
    custom_title: Optional[str] = None
    message: Optional[str] = None


class FamilyInvitationLinkResponse(BaseModel):
    """Schema for link invitation generation response"""
    url: str
    token: str
    expires_at: datetime


class FamilyInvitationDetailsResponse(BaseModel):
    """Schema for invitation details from token"""
    id: str
    pregnancy_id: str
    relationship: RelationshipType
    custom_title: Optional[str] = None
    message: Optional[str] = None
    expires_at: datetime
    status: InvitationStatus
    # Inviter information
    inviter_name: str
    inviter_email: str
    # Pregnancy information for context
    pregnancy_details: Optional[dict] = None
    created_at: datetime


class FamilyInvitationResponse(FamilyInvitationBase):
    """Schema for family invitation responses"""
    id: str
    pregnancy_id: str
    group_id: str
    invited_by: str
    status: InvitationStatus
    expires_at: datetime
    accepted_at: Optional[datetime]
    token: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmergencyContactBase(BaseModel):
    """Base emergency contact schema"""
    name: str
    relationship: str
    phone_primary: str
    phone_secondary: Optional[str] = None
    email: Optional[str] = None
    priority: int = 1
    can_view_all_updates: bool = False
    notify_on_emergency: bool = True


class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating emergency contact"""
    pregnancy_id: str


class EmergencyContactResponse(EmergencyContactBase):
    """Schema for emergency contact responses"""
    id: str
    pregnancy_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
