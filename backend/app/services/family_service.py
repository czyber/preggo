"""
Family service for database operations using SQLModel sessions.

This service handles all family-related database operations for groups,
members, invitations, and emergency contacts.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timedelta
import secrets
import string
from app.models.family import (
    FamilyGroup, FamilyMember, FamilyInvitation, EmergencyContact,
    MemberStatus, InvitationStatus
)
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class FamilyGroupService(BaseService[FamilyGroup]):
    """Service for family group-related database operations."""
    
    def __init__(self):
        super().__init__(FamilyGroup)
    
    async def get_pregnancy_groups(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> List[FamilyGroup]:
        """Get all family groups for a pregnancy."""
        try:
            statement = select(FamilyGroup).where(
                FamilyGroup.pregnancy_id == pregnancy_id
            )
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting groups for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_group(
        self, 
        session: Session, 
        group_data: Dict[str, Any]
    ) -> Optional[FamilyGroup]:
        """Create a new family group."""
        try:
            return await self.create(session, group_data)
        except Exception as e:
            logger.error(f"Error creating family group: {e}")
            return None
    
    async def update_group(
        self, 
        session: Session, 
        group_id: str, 
        group_data: Dict[str, Any]
    ) -> Optional[FamilyGroup]:
        """Update an existing family group."""
        try:
            db_group = await self.get_by_id(session, group_id)
            if not db_group:
                return None
            
            group_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_group, group_data)
        except Exception as e:
            logger.error(f"Error updating family group {group_id}: {e}")
            return None
    
    async def user_can_access_group(
        self, 
        session: Session, 
        user_id: str, 
        group_id: str
    ) -> bool:
        """Check if user has access to a family group."""
        try:
            # Check if user is member of the group
            statement = select(FamilyMember).where(
                FamilyMember.user_id == user_id,
                FamilyMember.group_id == group_id,
                FamilyMember.status == MemberStatus.ACTIVE
            )
            member = session.exec(statement).first()
            
            if member:
                return True
            
            # Check if user owns the pregnancy
            group = await self.get_by_id(session, group_id)
            if group:
                from app.services.pregnancy_service import pregnancy_service
                return await pregnancy_service.user_owns_pregnancy(
                    session, user_id, group.pregnancy_id
                )
            
            return False
        except Exception as e:
            logger.error(f"Error checking group access: {e}")
            return False


class FamilyMemberService(BaseService[FamilyMember]):
    """Service for family member-related database operations."""
    
    def __init__(self):
        super().__init__(FamilyMember)
    
    async def get_group_members(
        self, 
        session: Session, 
        group_id: str,
        status: Optional[MemberStatus] = None
    ) -> List[FamilyMember]:
        """Get all members of a family group."""
        try:
            statement = select(FamilyMember).where(
                FamilyMember.group_id == group_id
            )
            
            if status:
                statement = statement.where(FamilyMember.status == status)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting members for group {group_id}: {e}")
            return []
    
    async def get_user_memberships(
        self, 
        session: Session, 
        user_id: str,
        pregnancy_id: Optional[str] = None
    ) -> List[FamilyMember]:
        """Get all family memberships for a user."""
        try:
            statement = select(FamilyMember).where(
                FamilyMember.user_id == user_id
            )
            
            if pregnancy_id:
                statement = statement.where(FamilyMember.pregnancy_id == pregnancy_id)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting memberships for user {user_id}: {e}")
            return []
    
    async def add_member(
        self, 
        session: Session, 
        member_data: Dict[str, Any]
    ) -> Optional[FamilyMember]:
        """Add a new family member."""
        try:
            # Check if member already exists
            existing = session.exec(
                select(FamilyMember).where(
                    FamilyMember.user_id == member_data["user_id"],
                    FamilyMember.group_id == member_data["group_id"]
                )
            ).first()
            
            if existing:
                logger.warning(f"Member already exists in group")
                return None
            
            member_data["status"] = MemberStatus.ACTIVE
            member_data["joined_at"] = datetime.utcnow()
            
            return await self.create(session, member_data)
        except Exception as e:
            logger.error(f"Error adding family member: {e}")
            return None
    
    async def update_member(
        self, 
        session: Session, 
        member_id: str, 
        member_data: Dict[str, Any]
    ) -> Optional[FamilyMember]:
        """Update a family member."""
        try:
            db_member = await self.get_by_id(session, member_id)
            if not db_member:
                return None
            
            member_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_member, member_data)
        except Exception as e:
            logger.error(f"Error updating family member {member_id}: {e}")
            return None
    
    async def remove_member(
        self, 
        session: Session, 
        member_id: str
    ) -> bool:
        """Remove a family member."""
        try:
            db_member = await self.get_by_id(session, member_id)
            if not db_member:
                return False
            
            await self.delete(session, db_member)
            return True
        except Exception as e:
            logger.error(f"Error removing family member {member_id}: {e}")
            return False
    
    async def get_pregnancy_members(
        self, 
        session: Session, 
        pregnancy_id: str,
        status: Optional[MemberStatus] = None
    ) -> List[FamilyMember]:
        """Get all family members for a pregnancy."""
        try:
            statement = select(FamilyMember).where(
                FamilyMember.pregnancy_id == pregnancy_id
            )
            
            if status:
                statement = statement.where(FamilyMember.status == status)
            else:
                # Default to active members
                statement = statement.where(FamilyMember.status == MemberStatus.ACTIVE)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting members for pregnancy {pregnancy_id}: {e}")
            return []


class FamilyInvitationService(BaseService[FamilyInvitation]):
    """Service for family invitation-related database operations."""
    
    def __init__(self):
        super().__init__(FamilyInvitation)
    
    async def get_group_invitations(
        self, 
        session: Session, 
        group_id: str,
        status: Optional[InvitationStatus] = None
    ) -> List[FamilyInvitation]:
        """Get all invitations for a family group."""
        try:
            statement = select(FamilyInvitation).where(
                FamilyInvitation.group_id == group_id
            )
            
            if status:
                statement = statement.where(FamilyInvitation.status == status)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting invitations for group {group_id}: {e}")
            return []
    
    async def create_invitation(
        self, 
        session: Session, 
        invitation_data: Dict[str, Any]
    ) -> Optional[FamilyInvitation]:
        """Create a new family invitation."""
        try:
            # Set expiry date (7 days from now)
            invitation_data["expires_at"] = datetime.utcnow() + timedelta(days=7)
            invitation_data["status"] = InvitationStatus.PENDING
            
            return await self.create(session, invitation_data)
        except Exception as e:
            logger.error(f"Error creating family invitation: {e}")
            return None
    
    async def accept_invitation(
        self, 
        session: Session, 
        invitation_id: str,
        accepting_user_id: str
    ) -> Optional[FamilyMember]:
        """Accept a family invitation and create member."""
        try:
            invitation = await self.get_by_id(session, invitation_id)
            if not invitation:
                return None
            
            if invitation.status != InvitationStatus.PENDING:
                logger.warning(f"Invitation {invitation_id} is not pending")
                return None
            
            if invitation.expires_at < datetime.utcnow():
                logger.warning(f"Invitation {invitation_id} has expired")
                await self.update_invitation_status(
                    session, invitation_id, InvitationStatus.EXPIRED
                )
                return None
            
            # Create family member
            member_data = {
                "user_id": accepting_user_id,
                "pregnancy_id": invitation.pregnancy_id,
                "group_id": invitation.group_id,
                "relationship": invitation.relationship,
                "custom_title": invitation.custom_title,
                "role": invitation.role,
                "invited_by": invitation.invited_by
            }
            
            member = await family_member_service.add_member(session, member_data)
            
            if member:
                # Update invitation status
                await self.update_invitation_status(
                    session, invitation_id, InvitationStatus.ACCEPTED
                )
                
                # Update accepted_at timestamp
                invitation_update = {"accepted_at": datetime.utcnow()}
                await self.update(session, invitation, invitation_update)
            
            return member
        except Exception as e:
            logger.error(f"Error accepting invitation {invitation_id}: {e}")
            return None
    
    async def update_invitation_status(
        self, 
        session: Session, 
        invitation_id: str, 
        status: InvitationStatus
    ) -> Optional[FamilyInvitation]:
        """Update invitation status."""
        try:
            invitation = await self.get_by_id(session, invitation_id)
            if not invitation:
                return None
            
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            return await self.update(session, invitation, update_data)
        except Exception as e:
            logger.error(f"Error updating invitation status {invitation_id}: {e}")
            return None
    
    async def cleanup_expired_invitations(self, session: Session) -> int:
        """Clean up expired invitations."""
        try:
            statement = select(FamilyInvitation).where(
                FamilyInvitation.status == InvitationStatus.PENDING,
                FamilyInvitation.expires_at < datetime.utcnow()
            )
            expired_invitations = session.exec(statement).all()
            
            count = 0
            for invitation in expired_invitations:
                await self.update_invitation_status(
                    session, invitation.id, InvitationStatus.EXPIRED
                )
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error cleaning up expired invitations: {e}")
            return 0
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def create_link_invitation(
        self, 
        session: Session, 
        invitation_data: Dict[str, Any]
    ) -> Optional[FamilyInvitation]:
        """Create a new link-based family invitation with token."""
        try:
            # Generate unique token
            max_attempts = 10
            for _ in range(max_attempts):
                token = self.generate_secure_token()
                
                # Check if token already exists
                existing = session.exec(
                    select(FamilyInvitation).where(FamilyInvitation.token == token)
                ).first()
                
                if not existing:
                    break
            else:
                logger.error("Failed to generate unique token after maximum attempts")
                return None
            
            # Set token and expiry
            invitation_data["token"] = token
            invitation_data["expires_at"] = datetime.utcnow() + timedelta(days=7)
            invitation_data["status"] = InvitationStatus.PENDING
            
            # Email is optional for link invites
            if "email" not in invitation_data:
                invitation_data["email"] = None
            
            return await self.create(session, invitation_data)
        except Exception as e:
            logger.error(f"Error creating link invitation: {e}")
            return None
    
    async def get_invitation_by_token(
        self, 
        session: Session, 
        token: str
    ) -> Optional[FamilyInvitation]:
        """Get invitation by token."""
        try:
            statement = select(FamilyInvitation).where(
                FamilyInvitation.token == token
            )
            return session.exec(statement).first()
        except Exception as e:
            logger.error(f"Error getting invitation by token: {e}")
            return None
    
    async def accept_invitation_by_token(
        self, 
        session: Session, 
        token: str,
        accepting_user_id: str
    ) -> Optional[FamilyMember]:
        """Accept a family invitation using token and create member."""
        try:
            invitation = await self.get_invitation_by_token(session, token)
            if not invitation:
                logger.warning(f"Invitation with token {token} not found")
                return None
            
            if invitation.status != InvitationStatus.PENDING:
                logger.warning(f"Invitation {invitation.id} is not pending")
                return None
            
            if invitation.expires_at < datetime.utcnow():
                logger.warning(f"Invitation {invitation.id} has expired")
                await self.update_invitation_status(
                    session, invitation.id, InvitationStatus.EXPIRED
                )
                return None
            
            # Check if user is already a member of this group
            existing_member = session.exec(
                select(FamilyMember).where(
                    FamilyMember.user_id == accepting_user_id,
                    FamilyMember.group_id == invitation.group_id
                )
            ).first()
            
            if existing_member:
                logger.warning(f"User {accepting_user_id} is already a member of group {invitation.group_id}")
                return None
            
            # Create family member
            member_data = {
                "user_id": accepting_user_id,
                "pregnancy_id": invitation.pregnancy_id,
                "group_id": invitation.group_id,
                "relationship": invitation.relationship,
                "custom_title": invitation.custom_title,
                "role": invitation.role,
                "invited_by": invitation.invited_by
            }
            
            member = await family_member_service.add_member(session, member_data)
            
            if member:
                # Update invitation status
                await self.update_invitation_status(
                    session, invitation.id, InvitationStatus.ACCEPTED
                )
                
                # Update accepted_at timestamp
                invitation_update = {"accepted_at": datetime.utcnow()}
                await self.update(session, invitation, invitation_update)
            
            return member
        except Exception as e:
            logger.error(f"Error accepting invitation by token {token}: {e}")
            return None
    
    async def resend_invitation(
        self, 
        session: Session, 
        invitation_id: str
    ) -> Optional[FamilyInvitation]:
        """Resend an invitation by generating a new token and extending expiry."""
        try:
            invitation = await self.get_by_id(session, invitation_id)
            if not invitation:
                return None
            
            # Generate new token if it's a link invitation
            if invitation.token:
                # Generate new unique token
                max_attempts = 10
                for _ in range(max_attempts):
                    new_token = self.generate_secure_token()
                    
                    # Check if token already exists
                    existing = session.exec(
                        select(FamilyInvitation).where(
                            FamilyInvitation.token == new_token,
                            FamilyInvitation.id != invitation_id
                        )
                    ).first()
                    
                    if not existing:
                        break
                else:
                    logger.error("Failed to generate unique token for resend")
                    return None
                
                # Update invitation with new token and expiry
                update_data = {
                    "token": new_token,
                    "expires_at": datetime.utcnow() + timedelta(days=7),
                    "status": InvitationStatus.PENDING,
                    "updated_at": datetime.utcnow()
                }
            else:
                # For email-based invitations, just extend expiry
                update_data = {
                    "expires_at": datetime.utcnow() + timedelta(days=7),
                    "status": InvitationStatus.PENDING,
                    "updated_at": datetime.utcnow()
                }
            
            return await self.update(session, invitation, update_data)
        except Exception as e:
            logger.error(f"Error resending invitation {invitation_id}: {e}")
            return None


class EmergencyContactService(BaseService[EmergencyContact]):
    """Service for emergency contact-related database operations."""
    
    def __init__(self):
        super().__init__(EmergencyContact)
    
    async def get_pregnancy_contacts(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> List[EmergencyContact]:
        """Get all emergency contacts for a pregnancy."""
        try:
            statement = select(EmergencyContact).where(
                EmergencyContact.pregnancy_id == pregnancy_id
            ).order_by(EmergencyContact.priority)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting emergency contacts for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_contact(
        self, 
        session: Session, 
        contact_data: Dict[str, Any]
    ) -> Optional[EmergencyContact]:
        """Create a new emergency contact."""
        try:
            return await self.create(session, contact_data)
        except Exception as e:
            logger.error(f"Error creating emergency contact: {e}")
            return None
    
    async def update_contact(
        self, 
        session: Session, 
        contact_id: str, 
        contact_data: Dict[str, Any]
    ) -> Optional[EmergencyContact]:
        """Update an emergency contact."""
        try:
            db_contact = await self.get_by_id(session, contact_id)
            if not db_contact:
                return None
            
            contact_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_contact, contact_data)
        except Exception as e:
            logger.error(f"Error updating emergency contact {contact_id}: {e}")
            return None


# Global service instances
family_group_service = FamilyGroupService()
family_member_service = FamilyMemberService()
family_invitation_service = FamilyInvitationService()
emergency_contact_service = EmergencyContactService()
