"""
Pregnancy service for database operations using SQLModel sessions.

This service handles all pregnancy-related database operations using proper SQLModel sessions
instead of direct Supabase client calls.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from app.models.pregnancy import Pregnancy, PregnancyStatus, WeeklyUpdate
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class PregnancyService(BaseService[Pregnancy]):
    """Service for pregnancy-related database operations."""
    
    def __init__(self):
        super().__init__(Pregnancy)
    
    async def get_user_pregnancies(
        self, 
        session: Session, 
        user_id: str, 
        status: Optional[PregnancyStatus] = None
    ) -> List[Pregnancy]:
        """Get all pregnancies for a user, optionally filtered by status."""
        try:
            statement = select(Pregnancy).where(Pregnancy.user_id == user_id)
            
            if status:
                statement = statement.where(Pregnancy.status == status)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting pregnancies for user {user_id}: {e}")
            return []
    
    async def get_active_pregnancies(self, session: Session, user_id: str) -> List[Pregnancy]:
        """Get all active pregnancies for a user."""
        return await self.get_user_pregnancies(session, user_id, PregnancyStatus.ACTIVE)
    
    async def create_pregnancy(self, session: Session, pregnancy_data: Dict[str, Any]) -> Optional[Pregnancy]:
        """Create a new pregnancy with proper validation."""
        try:
            # Ensure status is set
            if "status" not in pregnancy_data:
                pregnancy_data["status"] = PregnancyStatus.ACTIVE
            
            # Create new pregnancy
            db_pregnancy = await self.create(session, pregnancy_data)
            return db_pregnancy
        except Exception as e:
            logger.error(f"Error creating pregnancy: {e}")
            return None
    
    async def update_pregnancy(
        self, 
        session: Session, 
        pregnancy_id: str, 
        pregnancy_data: Dict[str, Any]
    ) -> Optional[Pregnancy]:
        """Update an existing pregnancy."""
        try:
            db_pregnancy = await self.get_by_id(session, pregnancy_id)
            if not db_pregnancy:
                logger.warning(f"Pregnancy with ID {pregnancy_id} not found")
                return None
            
            # Update timestamp
            from datetime import datetime
            pregnancy_data["updated_at"] = datetime.utcnow()
            
            updated_pregnancy = await self.update(session, db_pregnancy, pregnancy_data)
            return updated_pregnancy
        except Exception as e:
            logger.error(f"Error updating pregnancy {pregnancy_id}: {e}")
            return None
    
    async def user_owns_pregnancy(self, session: Session, user_id: str, pregnancy_id: str) -> bool:
        """Check if a user owns a specific pregnancy."""
        try:
            statement = select(Pregnancy).where(
                Pregnancy.id == pregnancy_id,
                Pregnancy.user_id == user_id
            )
            result = session.exec(statement).first()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking pregnancy ownership: {e}")
            return False
    
    async def archive_pregnancy(self, session: Session, pregnancy_id: str) -> Optional[Pregnancy]:
        """Archive a pregnancy."""
        try:
            return await self.update_pregnancy(
                session, 
                pregnancy_id, 
                {"status": PregnancyStatus.ARCHIVED}
            )
        except Exception as e:
            logger.error(f"Error archiving pregnancy {pregnancy_id}: {e}")
            return None
    
    async def complete_pregnancy(self, session: Session, pregnancy_id: str) -> Optional[Pregnancy]:
        """Mark a pregnancy as completed."""
        try:
            return await self.update_pregnancy(
                session, 
                pregnancy_id, 
                {"status": PregnancyStatus.COMPLETED}
            )
        except Exception as e:
            logger.error(f"Error completing pregnancy {pregnancy_id}: {e}")
            return None
    
    async def add_partner(self, session: Session, pregnancy_id: str, partner_id: str) -> Optional[Pregnancy]:
        """Add a partner to a pregnancy."""
        try:
            db_pregnancy = await self.get_by_id(session, pregnancy_id)
            if not db_pregnancy:
                return None
            
            # Add partner if not already in the list
            current_partners = db_pregnancy.partner_ids or []
            if partner_id not in current_partners:
                current_partners.append(partner_id)
                
                updated_pregnancy = await self.update_pregnancy(
                    session,
                    pregnancy_id,
                    {"partner_ids": current_partners}
                )
                return updated_pregnancy
            
            return db_pregnancy
        except Exception as e:
            logger.error(f"Error adding partner to pregnancy {pregnancy_id}: {e}")
            return None
    
    async def remove_partner(self, session: Session, pregnancy_id: str, partner_id: str) -> Optional[Pregnancy]:
        """Remove a partner from a pregnancy."""
        try:
            db_pregnancy = await self.get_by_id(session, pregnancy_id)
            if not db_pregnancy:
                return None
            
            # Remove partner if in the list
            current_partners = db_pregnancy.partner_ids or []
            if partner_id in current_partners:
                current_partners.remove(partner_id)
                
                updated_pregnancy = await self.update_pregnancy(
                    session,
                    pregnancy_id,
                    {"partner_ids": current_partners}
                )
                return updated_pregnancy
            
            return db_pregnancy
        except Exception as e:
            logger.error(f"Error removing partner from pregnancy {pregnancy_id}: {e}")
            return None


class WeeklyUpdateService(BaseService[WeeklyUpdate]):
    """Service for weekly update-related database operations."""
    
    def __init__(self):
        super().__init__(WeeklyUpdate)
    
    async def get_pregnancy_weekly_updates(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> List[WeeklyUpdate]:
        """Get all weekly updates for a pregnancy."""
        try:
            statement = select(WeeklyUpdate).where(
                WeeklyUpdate.pregnancy_id == pregnancy_id
            ).order_by(WeeklyUpdate.week)
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting weekly updates for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_weekly_update_by_week(
        self, 
        session: Session, 
        pregnancy_id: str, 
        week: int
    ) -> Optional[WeeklyUpdate]:
        """Get a specific week's update for a pregnancy."""
        try:
            statement = select(WeeklyUpdate).where(
                WeeklyUpdate.pregnancy_id == pregnancy_id,
                WeeklyUpdate.week == week
            )
            result = session.exec(statement).first()
            return result
        except Exception as e:
            logger.error(f"Error getting week {week} update for pregnancy {pregnancy_id}: {e}")
            return None


# Global service instances
pregnancy_service = PregnancyService()
weekly_update_service = WeeklyUpdateService()