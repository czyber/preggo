"""
User service for database operations using SQLModel sessions.

This service handles all user-related database operations using proper SQLModel sessions
instead of direct Supabase client calls.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from app.models.user import User
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    """Service for user-related database operations."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """Get a user by email address."""
        try:
            statement = select(User).where(User.email == email)
            result = session.exec(statement).first()
            return result
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def create_user(self, session: Session, user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user with proper validation."""
        try:
            # Check if user already exists
            existing_user = await self.get_by_email(session, user_data.get("email"))
            if existing_user:
                logger.warning(f"User with email {user_data.get('email')} already exists")
                return existing_user
            
            # Create new user
            db_user = await self.create(session, user_data)
            return db_user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def update_user(self, session: Session, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """Update an existing user."""
        try:
            db_user = await self.get_by_id(session, user_id)
            if not db_user:
                logger.warning(f"User with ID {user_id} not found")
                return None
            
            # Update timestamp
            from datetime import datetime
            user_data["updated_at"] = datetime.utcnow()
            
            updated_user = await self.update(session, db_user, user_data)
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def update_last_login(self, session: Session, user_id: str) -> Optional[User]:
        """Update user's last login timestamp."""
        try:
            from datetime import datetime
            return await self.update_user(session, user_id, {"last_login": datetime.utcnow()})
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return None
    
    async def verify_email(self, session: Session, user_id: str) -> Optional[User]:
        """Mark user's email as verified."""
        try:
            return await self.update_user(session, user_id, {"email_verified": True})
        except Exception as e:
            logger.error(f"Error verifying email for user {user_id}: {e}")
            return None
    
    async def deactivate_user(self, session: Session, user_id: str) -> Optional[User]:
        """Deactivate a user account."""
        try:
            return await self.update_user(session, user_id, {"is_active": False})
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return None
    
    async def activate_user(self, session: Session, user_id: str) -> Optional[User]:
        """Activate a user account."""
        try:
            return await self.update_user(session, user_id, {"is_active": True})
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            return None
    
    async def get_active_users(self, session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        try:
            statement = select(User).where(User.is_active == True).offset(skip).limit(limit)
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []


# Global service instance
user_service = UserService()