"""
Family management endpoints for groups, members, and invitations.

This module provides endpoints for:
- Creating and managing family groups
- Managing family members and their permissions
- Sending and managing invitations
- Emergency contact management
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.supabase import get_current_active_user
from app.services.family_service import (
    family_group_service, family_member_service, 
    family_invitation_service, emergency_contact_service
)
from app.services.pregnancy_service import pregnancy_service
from app.db.session import get_session
from app.schemas.family import (
    FamilyGroupCreate, FamilyGroupUpdate, FamilyGroupResponse,
    FamilyMemberCreate, FamilyMemberUpdate, FamilyMemberResponse,
    FamilyInvitationCreate, FamilyInvitationUpdate, FamilyInvitationResponse,
    FamilyInvitationLinkCreate, FamilyInvitationLinkResponse, FamilyInvitationDetailsResponse,
    EmergencyContactCreate, EmergencyContactResponse
)
from app.models.family import InvitationStatus

router = APIRouter(prefix="/family", tags=["family"])


# Family Groups
@router.post("/groups", response_model=FamilyGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_family_group(
    group_data: FamilyGroupCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new family group for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, group_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create the group
        group_record = group_data.dict()
        created_group = await family_group_service.create_group(session, group_record)
        
        if not created_group:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create family group"
            )
        
        return FamilyGroupResponse.from_orm(created_group)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family group: {str(e)}"
        )


@router.get("/groups/{pregnancy_id}", response_model=List[FamilyGroupResponse])
async def get_pregnancy_groups(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all family groups for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        groups = await family_group_service.get_pregnancy_groups(session, pregnancy_id)
        return [FamilyGroupResponse.from_orm(group) for group in groups]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family groups: {str(e)}"
        )


@router.get("/groups/single/{group_id}", response_model=FamilyGroupResponse)
async def get_family_group(
    group_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get a specific family group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        group = await family_group_service.get_by_id(session, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family group not found"
            )
        
        return FamilyGroupResponse.from_orm(group)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family group: {str(e)}"
        )


@router.put("/groups/{group_id}", response_model=FamilyGroupResponse)
async def update_family_group(
    group_id: str,
    group_update: FamilyGroupUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a family group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        # Update group
        update_data = group_update.dict(exclude_unset=True)
        updated_group = await family_group_service.update_group(session, group_id, update_data)
        
        if not updated_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family group not found"
            )
        
        return FamilyGroupResponse.from_orm(updated_group)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update family group: {str(e)}"
        )


@router.delete("/groups/{group_id}")
async def delete_family_group(
    group_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete a family group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        group = await family_group_service.get_by_id(session, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family group not found"
            )
        
        await family_group_service.delete(session, group)
        return {"message": "Family group deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete family group: {str(e)}"
        )


# Family Members
@router.post("/members", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_family_member(
    member_data: FamilyMemberCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add a new family member to a group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, member_data.group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        # Add member
        member_record = member_data.dict()
        member_record["invited_by"] = user_id
        
        created_member = await family_member_service.add_member(session, member_record)
        
        if not created_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add family member - member may already exist in group"
            )
        
        return FamilyMemberResponse.from_orm(created_member)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add family member: {str(e)}"
        )


@router.get("/members/{group_id}", response_model=List[FamilyMemberResponse])
async def get_group_members(
    group_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all members of a family group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        members = await family_member_service.get_group_members(session, group_id)
        return [FamilyMemberResponse.from_orm(member) for member in members]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group members: {str(e)}"
        )


@router.get("/{pregnancy_id}/members", response_model=List[FamilyMemberResponse])
async def get_pregnancy_family_members(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all family members across all groups for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get all family groups for this pregnancy
        groups = await family_group_service.get_pregnancy_groups(session, pregnancy_id)
        
        # Get all members from all groups
        all_members = []
        for group in groups:
            members = await family_member_service.get_group_members(session, group.id)
            all_members.extend(members)
        
        # Remove duplicates (same user might be in multiple groups)
        unique_members = {}
        for member in all_members:
            if member.user_id not in unique_members:
                unique_members[member.user_id] = member
        
        return [FamilyMemberResponse.from_orm(member) for member in unique_members.values()]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pregnancy family members: {str(e)}"
        )


@router.put("/members/{member_id}", response_model=FamilyMemberResponse)
async def update_family_member(
    member_id: str,
    member_update: FamilyMemberUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a family member."""
    try:
        user_id = current_user["sub"]
        
        # Get member to check access
        member = await family_member_service.get_by_id(session, member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found"
            )
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, member.group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        # Update member
        update_data = member_update.dict(exclude_unset=True)
        updated_member = await family_member_service.update_member(session, member_id, update_data)
        
        if not updated_member:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update family member"
            )
        
        return FamilyMemberResponse.from_orm(updated_member)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update family member: {str(e)}"
        )


@router.delete("/members/{member_id}")
async def remove_family_member(
    member_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove a family member from a group."""
    try:
        user_id = current_user["sub"]
        
        # Get member to check access
        member = await family_member_service.get_by_id(session, member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found"
            )
        
        # Check access to group  
        if not await family_group_service.user_can_access_group(session, user_id, member.group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        success = await family_member_service.remove_member(session, member_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove family member"
            )
        
        return {"message": "Family member removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove family member: {str(e)}"
        )


# Family Invitations
@router.post("/invitations", response_model=FamilyInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_family_invitation(
    invitation_data: FamilyInvitationCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new family invitation."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, invitation_data.group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        # Create invitation
        invitation_record = invitation_data.dict()
        invitation_record["invited_by"] = user_id
        
        created_invitation = await family_invitation_service.create_invitation(session, invitation_record)
        
        if not created_invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create family invitation"
            )
        
        return FamilyInvitationResponse.from_orm(created_invitation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family invitation: {str(e)}"
        )


@router.get("/invitations/{group_id}", response_model=List[FamilyInvitationResponse])
async def get_group_invitations(
    group_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all invitations for a family group."""
    try:
        user_id = current_user["sub"]
        
        # Check access to group
        if not await family_group_service.user_can_access_group(session, user_id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this family group"
            )
        
        invitations = await family_invitation_service.get_group_invitations(session, group_id)
        return [FamilyInvitationResponse.from_orm(invitation) for invitation in invitations]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group invitations: {str(e)}"
        )


@router.put("/invitations/{invitation_id}/accept", response_model=FamilyMemberResponse)
async def accept_family_invitation(
    invitation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Accept a family invitation."""
    try:
        user_id = current_user["sub"]
        
        # Accept invitation and create member
        member = await family_invitation_service.accept_invitation(session, invitation_id, user_id)
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to accept invitation - invitation may be expired or invalid"
            )
        
        return FamilyMemberResponse.from_orm(member)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept family invitation: {str(e)}"
        )


@router.put("/invitations/{invitation_id}", response_model=FamilyInvitationResponse)
async def update_invitation_status(
    invitation_id: str,
    status_update: FamilyInvitationUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update invitation status (decline, revoke, etc)."""
    try:
        user_id = current_user["sub"]
        
        # Get invitation to check access
        invitation = await family_invitation_service.get_by_id(session, invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Check access to group (only group members or inviter can update)
        can_access = await family_group_service.user_can_access_group(session, user_id, invitation.group_id)
        if not can_access and invitation.invited_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this invitation"
            )
        
        # Update status
        updated_invitation = await family_invitation_service.update_invitation_status(
            session, invitation_id, status_update.status
        )
        
        if not updated_invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update invitation status"
            )
        
        return FamilyInvitationResponse.from_orm(updated_invitation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update invitation status: {str(e)}"
        )


# Link-based Invitations
@router.post("/invitations/generate-link", response_model=FamilyInvitationLinkResponse, status_code=status.HTTP_201_CREATED)
async def generate_invite_link(
    link_data: FamilyInvitationLinkCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Generate a shareable invite link for family members."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, link_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get or create default family group for this pregnancy
        # First check if there's an existing group
        groups = await family_group_service.get_pregnancy_groups(session, link_data.pregnancy_id)
        
        if not groups:
            # Create a default group
            from app.models.family import GroupType, GroupPermissions, GroupSettings
            default_group_data = {
                "name": "Family",
                "description": "Default family group",
                "type": GroupType.IMMEDIATE_FAMILY,
                "pregnancy_id": link_data.pregnancy_id,
                "permissions": GroupPermissions().dict(),
                "custom_settings": GroupSettings().dict()
            }
            group = await family_group_service.create_group(session, default_group_data)
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create default family group"
                )
        else:
            # Use the first existing group
            group = groups[0]
        
        # Create the link invitation
        from app.models.family import MemberRole
        invitation_data = {
            "pregnancy_id": link_data.pregnancy_id,
            "group_id": group.id,
            "relationship": link_data.relationship,
            "custom_title": link_data.custom_title,
            "role": MemberRole.CONTRIBUTOR,  # Default role for link invites
            "message": link_data.message,
            "invited_by": user_id
        }
        
        invitation = await family_invitation_service.create_link_invitation(session, invitation_data)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create invite link"
            )
        
        # Generate the full URL (you might want to make this configurable)
        base_url = "https://app.com"  # This should come from config
        invite_url = f"{base_url}/invite/{invitation.token}"
        
        return FamilyInvitationLinkResponse(
            url=invite_url,
            token=invitation.token,
            expires_at=invitation.expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invite link: {str(e)}"
        )


@router.get("/invitations/details/{token}", response_model=FamilyInvitationDetailsResponse)
async def get_invite_details(
    token: str,
    session: Session = Depends(get_session)
):
    """Get invitation details by token for displaying on invite landing page."""
    try:
        invitation = await family_invitation_service.get_invitation_by_token(session, token)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Check if invitation is expired
        from datetime import datetime
        if invitation.expires_at < datetime.utcnow():
            # Update status to expired
            await family_invitation_service.update_invitation_status(
                session, invitation.id, InvitationStatus.EXPIRED
            )
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Invitation has expired"
            )
        
        # Check if invitation is still pending
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=f"Invitation has already been {invitation.status.value}"
            )
        
        # Get inviter information
        from app.models.user import User
        inviter = session.get(User, invitation.invited_by)
        if not inviter:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Inviter information not found"
            )
        
        # Get pregnancy details for context
        from app.models.pregnancy import Pregnancy
        pregnancy = session.get(Pregnancy, invitation.pregnancy_id)
        pregnancy_details = None
        if pregnancy and pregnancy.pregnancy_details:
            # Only include safe, non-sensitive pregnancy details
            pregnancy_details = {
                "due_date": pregnancy.pregnancy_details.get("due_date"),
                "current_week": pregnancy.pregnancy_details.get("current_week"),
                "baby_name": pregnancy.pregnancy_details.get("baby_name")
            }
        
        return FamilyInvitationDetailsResponse(
            id=invitation.id,
            pregnancy_id=invitation.pregnancy_id,
            relationship=invitation.relationship,
            custom_title=invitation.custom_title,
            message=invitation.message,
            expires_at=invitation.expires_at,
            status=invitation.status,
            inviter_name=f"{inviter.first_name} {inviter.last_name}",
            inviter_email=inviter.email,
            pregnancy_details=pregnancy_details,
            created_at=invitation.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invitation details: {str(e)}"
        )


@router.post("/invitations/{token}/accept", response_model=FamilyMemberResponse)
async def accept_invite_by_token(
    token: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Accept a family invitation using the token from the invite link."""
    try:
        user_id = current_user["sub"]
        
        # Accept invitation and create member
        member = await family_invitation_service.accept_invitation_by_token(
            session, token, user_id
        )
        
        if not member:
            # Get the invitation to provide more specific error messages
            invitation = await family_invitation_service.get_invitation_by_token(session, token)
            
            if not invitation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found"
                )
            
            if invitation.status != InvitationStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Invitation has already been {invitation.status.value}"
                )
            
            from datetime import datetime
            if invitation.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="Invitation has expired"
                )
            
            # Check if user is already a member
            from app.models.family import FamilyMember
            existing_member = session.exec(
                select(FamilyMember).where(
                    FamilyMember.user_id == user_id,
                    FamilyMember.group_id == invitation.group_id
                )
            ).first()
            
            if existing_member:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You are already a member of this family group"
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to accept invitation"
            )
        
        return FamilyMemberResponse.from_orm(member)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept family invitation: {str(e)}"
        )


@router.post("/invitations/{invite_id}/resend", response_model=FamilyInvitationLinkResponse)
async def resend_invitation(
    invite_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Resend an invitation by generating a new token/link and updating expiry date."""
    try:
        user_id = current_user["sub"]
        
        # Get the invitation
        invitation = await family_invitation_service.get_by_id(session, invite_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Check if user has access to this invitation (must be the inviter or own the pregnancy)
        can_resend = False
        if invitation.invited_by == user_id:
            can_resend = True
        else:
            # Check if user owns the pregnancy
            if await pregnancy_service.user_owns_pregnancy(session, user_id, invitation.pregnancy_id):
                can_resend = True
        
        if not can_resend:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to resend this invitation"
            )
        
        # Resend the invitation
        updated_invitation = await family_invitation_service.resend_invitation(
            session, invite_id
        )
        
        if not updated_invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resend invitation"
            )
        
        # Generate response based on invitation type
        if updated_invitation.token:
            # Link-based invitation
            base_url = "https://app.com"  # This should come from config
            invite_url = f"{base_url}/invite/{updated_invitation.token}"
            
            return FamilyInvitationLinkResponse(
                url=invite_url,
                token=updated_invitation.token,
                expires_at=updated_invitation.expires_at
            )
        else:
            # Email-based invitation - return empty URL but updated expiry
            return FamilyInvitationLinkResponse(
                url="",  # No URL for email-based invites
                token="",
                expires_at=updated_invitation.expires_at
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend invitation: {str(e)}"
        )


# Emergency Contacts
@router.post("/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new emergency contact."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, contact_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create contact
        contact_record = contact_data.dict()
        created_contact = await emergency_contact_service.create_contact(session, contact_record)
        
        if not created_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create emergency contact"
            )
        
        return EmergencyContactResponse.from_orm(created_contact)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create emergency contact: {str(e)}"
        )


@router.get("/emergency-contacts/{pregnancy_id}", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all emergency contacts for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        contacts = await emergency_contact_service.get_pregnancy_contacts(session, pregnancy_id)
        return [EmergencyContactResponse.from_orm(contact) for contact in contacts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get emergency contacts: {str(e)}"
        )


@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: str,
    contact_data: EmergencyContactCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update an emergency contact."""
    try:
        user_id = current_user["sub"]
        
        # Get contact to check access
        contact = await emergency_contact_service.get_by_id(session, contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, contact.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Update contact
        update_data = contact_data.dict(exclude={"pregnancy_id"})  # Don't allow changing pregnancy_id
        updated_contact = await emergency_contact_service.update_contact(session, contact_id, update_data)
        
        if not updated_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update emergency contact"
            )
        
        return EmergencyContactResponse.from_orm(updated_contact)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update emergency contact: {str(e)}"
        )


@router.delete("/emergency-contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete an emergency contact."""
    try:
        user_id = current_user["sub"]
        
        # Get contact to check access
        contact = await emergency_contact_service.get_by_id(session, contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, contact.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        await emergency_contact_service.delete(session, contact)
        return {"message": "Emergency contact deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete emergency contact: {str(e)}"
        )
