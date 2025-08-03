"""
Milestone service for database operations using SQLModel sessions.

This service handles all milestone-related database operations including milestones,
appointments, important dates, and weekly checklists.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, date
from app.models.milestone import (
    Milestone, Appointment, ImportantDate, WeeklyChecklist,
    MilestoneType, AppointmentType
)
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class MilestoneService(BaseService[Milestone]):
    """Service for milestone-related database operations."""
    
    def __init__(self):
        super().__init__(Milestone)
    
    async def get_pregnancy_milestones(
        self, 
        session: Session, 
        pregnancy_id: str,
        completed: Optional[bool] = None
    ) -> List[Milestone]:
        """Get all milestones for a pregnancy."""
        try:
            statement = select(Milestone).where(
                Milestone.pregnancy_id == pregnancy_id
            )
            
            if completed is not None:
                statement = statement.where(Milestone.completed == completed)
            
            statement = statement.order_by(Milestone.week.asc(), Milestone.created_at.asc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting milestones for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_milestones_by_week(
        self, 
        session: Session, 
        pregnancy_id: str,
        week: int
    ) -> List[Milestone]:
        """Get milestones for a specific pregnancy week."""
        try:
            statement = select(Milestone).where(
                Milestone.pregnancy_id == pregnancy_id,
                Milestone.week == week
            ).order_by(Milestone.created_at.asc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting week {week} milestones for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_milestone(
        self, 
        session: Session, 
        milestone_data: Dict[str, Any]
    ) -> Optional[Milestone]:
        """Create a new milestone."""
        try:
            return await self.create(session, milestone_data)
        except Exception as e:
            logger.error(f"Error creating milestone: {e}")
            return None
    
    async def update_milestone(
        self, 
        session: Session, 
        milestone_id: str, 
        milestone_data: Dict[str, Any]
    ) -> Optional[Milestone]:
        """Update an existing milestone."""
        try:
            db_milestone = await self.get_by_id(session, milestone_id)
            if not db_milestone:
                return None
            
            milestone_data["updated_at"] = datetime.utcnow()
            
            # If marking as completed, set completed_at timestamp
            if milestone_data.get("completed") and not db_milestone.completed:
                milestone_data["completed_at"] = datetime.utcnow()
            
            return await self.update(session, db_milestone, milestone_data)
        except Exception as e:
            logger.error(f"Error updating milestone {milestone_id}: {e}")
            return None
    
    async def complete_milestone(
        self, 
        session: Session, 
        milestone_id: str,
        celebration_post_id: Optional[str] = None
    ) -> Optional[Milestone]:
        """Mark a milestone as completed."""
        try:
            update_data = {
                "completed": True,
                "completed_at": datetime.utcnow()
            }
            
            if celebration_post_id:
                update_data["celebration_post_id"] = celebration_post_id
            
            return await self.update_milestone(session, milestone_id, update_data)
        except Exception as e:
            logger.error(f"Error completing milestone {milestone_id}: {e}")
            return None
    
    async def get_upcoming_milestones(
        self, 
        session: Session, 
        pregnancy_id: str,
        current_week: int,
        weeks_ahead: int = 4
    ) -> List[Milestone]:
        """Get upcoming milestones within a specified number of weeks."""
        try:
            statement = select(Milestone).where(
                Milestone.pregnancy_id == pregnancy_id,
                Milestone.completed == False,
                Milestone.week >= current_week,
                Milestone.week <= current_week + weeks_ahead
            ).order_by(Milestone.week.asc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting upcoming milestones: {e}")
            return []
    
    async def create_default_milestones(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> List[Milestone]:
        """Create default milestones for a new pregnancy."""
        try:
            default_milestones = [
                {
                    "pregnancy_id": pregnancy_id,
                    "type": MilestoneType.FIRST_HEARTBEAT,
                    "week": 6,
                    "title": "First Heartbeat",
                    "description": "Hearing your baby's heartbeat for the first time",
                    "is_default": True
                },
                {
                    "pregnancy_id": pregnancy_id,
                    "type": MilestoneType.FIRST_MOVEMENT,
                    "week": 18,
                    "title": "First Movement (Quickening)",
                    "description": "Feeling your baby move for the first time",
                    "is_default": True
                },
                {
                    "pregnancy_id": pregnancy_id,
                    "type": MilestoneType.GENDER_REVEAL,
                    "week": 20,
                    "title": "Gender Reveal",
                    "description": "Finding out if you're having a boy or girl",
                    "is_default": True
                },
                {
                    "pregnancy_id": pregnancy_id,
                    "type": MilestoneType.BABY_SHOWER,
                    "week": 32,
                    "title": "Baby Shower",
                    "description": "Celebrating your upcoming arrival with family and friends",
                    "is_default": True
                },
                {
                    "pregnancy_id": pregnancy_id,
                    "type": MilestoneType.HOSPITAL_BAG_PACKED,
                    "week": 36,
                    "title": "Hospital Bag Packed",
                    "description": "Getting ready for the big day",
                    "is_default": True
                }
            ]
            
            created_milestones = []
            for milestone_data in default_milestones:
                milestone = await self.create_milestone(session, milestone_data)
                if milestone:
                    created_milestones.append(milestone)
            
            return created_milestones
        except Exception as e:
            logger.error(f"Error creating default milestones: {e}")
            return []


class AppointmentService(BaseService[Appointment]):
    """Service for appointment-related database operations."""
    
    def __init__(self):
        super().__init__(Appointment)
    
    async def get_pregnancy_appointments(
        self, 
        session: Session, 
        pregnancy_id: str,
        completed: Optional[bool] = None,
        future_only: bool = False
    ) -> List[Appointment]:
        """Get appointments for a pregnancy."""
        try:
            statement = select(Appointment).where(
                Appointment.pregnancy_id == pregnancy_id
            )
            
            if completed is not None:
                statement = statement.where(Appointment.completed == completed)
            
            if future_only:
                statement = statement.where(
                    Appointment.appointment_date >= datetime.utcnow()
                )
            
            statement = statement.order_by(Appointment.appointment_date.asc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting appointments for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_upcoming_appointments(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_ahead: int = 30
    ) -> List[Appointment]:
        """Get upcoming appointments within specified days."""
        try:
            from datetime import timedelta
            end_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            statement = select(Appointment).where(
                Appointment.pregnancy_id == pregnancy_id,
                Appointment.completed == False,
                Appointment.cancelled == False,
                Appointment.appointment_date >= datetime.utcnow(),
                Appointment.appointment_date <= end_date
            ).order_by(Appointment.appointment_date.asc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting upcoming appointments: {e}")
            return []
    
    async def create_appointment(
        self, 
        session: Session, 
        appointment_data: Dict[str, Any]
    ) -> Optional[Appointment]:
        """Create a new appointment."""
        try:
            return await self.create(session, appointment_data)
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None
    
    async def update_appointment(
        self, 
        session: Session, 
        appointment_id: str, 
        appointment_data: Dict[str, Any]
    ) -> Optional[Appointment]:
        """Update an existing appointment."""
        try:
            db_appointment = await self.get_by_id(session, appointment_id)
            if not db_appointment:
                return None
            
            appointment_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_appointment, appointment_data)
        except Exception as e:
            logger.error(f"Error updating appointment {appointment_id}: {e}")
            return None
    
    async def complete_appointment(
        self, 
        session: Session, 
        appointment_id: str,
        results: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Appointment]:
        """Mark an appointment as completed."""
        try:
            update_data = {
                "completed": True
            }
            
            if results:
                update_data["results"] = results
            
            return await self.update_appointment(session, appointment_id, update_data)
        except Exception as e:
            logger.error(f"Error completing appointment {appointment_id}: {e}")
            return None


class ImportantDateService(BaseService[ImportantDate]):
    """Service for important date-related database operations."""
    
    def __init__(self):
        super().__init__(ImportantDate)
    
    async def get_pregnancy_dates(
        self, 
        session: Session, 
        pregnancy_id: str,
        category: Optional[str] = None
    ) -> List[ImportantDate]:
        """Get important dates for a pregnancy."""
        try:
            statement = select(ImportantDate).where(
                ImportantDate.pregnancy_id == pregnancy_id
            )
            
            if category:
                statement = statement.where(ImportantDate.category == category)
            
            statement = statement.order_by(ImportantDate.event_date.asc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting important dates for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_upcoming_dates(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_ahead: int = 30
    ) -> List[ImportantDate]:
        """Get upcoming important dates."""
        try:
            from datetime import timedelta
            end_date = date.today() + timedelta(days=days_ahead)
            
            statement = select(ImportantDate).where(
                ImportantDate.pregnancy_id == pregnancy_id,
                ImportantDate.event_date >= date.today(),
                ImportantDate.event_date <= end_date
            ).order_by(ImportantDate.event_date.asc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting upcoming important dates: {e}")
            return []
    
    async def create_important_date(
        self, 
        session: Session, 
        date_data: Dict[str, Any]
    ) -> Optional[ImportantDate]:
        """Create a new important date."""
        try:
            return await self.create(session, date_data)
        except Exception as e:
            logger.error(f"Error creating important date: {e}")
            return None
    
    async def update_important_date(
        self, 
        session: Session, 
        date_id: str, 
        date_data: Dict[str, Any]
    ) -> Optional[ImportantDate]:
        """Update an important date."""
        try:
            db_date = await self.get_by_id(session, date_id)
            if not db_date:
                return None
            
            date_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_date, date_data)
        except Exception as e:
            logger.error(f"Error updating important date {date_id}: {e}")
            return None


class WeeklyChecklistService(BaseService[WeeklyChecklist]):
    """Service for weekly checklist-related database operations."""
    
    def __init__(self):
        super().__init__(WeeklyChecklist)
    
    async def get_pregnancy_checklists(
        self, 
        session: Session, 
        pregnancy_id: str,
        week: Optional[int] = None,
        completed: Optional[bool] = None
    ) -> List[WeeklyChecklist]:
        """Get checklist items for a pregnancy."""
        try:
            statement = select(WeeklyChecklist).where(
                WeeklyChecklist.pregnancy_id == pregnancy_id
            )
            
            if week is not None:
                statement = statement.where(WeeklyChecklist.week == week)
            
            if completed is not None:
                statement = statement.where(WeeklyChecklist.completed == completed)
            
            statement = statement.order_by(
                WeeklyChecklist.week.asc(), 
                WeeklyChecklist.priority.desc(),
                WeeklyChecklist.created_at.asc()
            )
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting checklists for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_checklist_item(
        self, 
        session: Session, 
        checklist_data: Dict[str, Any]
    ) -> Optional[WeeklyChecklist]:
        """Create a new checklist item."""
        try:
            return await self.create(session, checklist_data)
        except Exception as e:
            logger.error(f"Error creating checklist item: {e}")
            return None
    
    async def update_checklist_item(
        self, 
        session: Session, 
        checklist_id: str, 
        checklist_data: Dict[str, Any]
    ) -> Optional[WeeklyChecklist]:
        """Update a checklist item."""
        try:
            db_checklist = await self.get_by_id(session, checklist_id)
            if not db_checklist:
                return None
            
            checklist_data["updated_at"] = datetime.utcnow()
            
            # If marking as completed, set completed_at timestamp
            if checklist_data.get("completed") and not db_checklist.completed:
                checklist_data["completed_at"] = datetime.utcnow()
            
            return await self.update(session, db_checklist, checklist_data)
        except Exception as e:
            logger.error(f"Error updating checklist item {checklist_id}: {e}")
            return None
    
    async def complete_checklist_item(
        self, 
        session: Session, 
        checklist_id: str,
        notes: Optional[str] = None
    ) -> Optional[WeeklyChecklist]:
        """Mark a checklist item as completed."""
        try:
            update_data = {
                "completed": True,
                "completed_at": datetime.utcnow()
            }
            
            if notes:
                update_data["notes"] = notes
            
            return await self.update_checklist_item(session, checklist_id, update_data)
        except Exception as e:
            logger.error(f"Error completing checklist item {checklist_id}: {e}")
            return None
    
    async def create_default_checklists(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> List[WeeklyChecklist]:
        """Create default weekly checklist items for a pregnancy."""
        try:
            default_items = [
                # Early pregnancy
                {"week": 4, "task": "Schedule first prenatal appointment", "category": "health", "priority": "high"},
                {"week": 6, "task": "Start taking prenatal vitamins", "category": "health", "priority": "high"},
                {"week": 8, "task": "Research pregnancy nutrition", "category": "education", "priority": "medium"},
                
                # First trimester
                {"week": 12, "task": "Consider sharing pregnancy news", "category": "preparation", "priority": "medium"},
                {"week": 12, "task": "Schedule genetic screening tests", "category": "health", "priority": "medium"},
                
                # Second trimester
                {"week": 16, "task": "Schedule anatomy scan", "category": "health", "priority": "high"},
                {"week": 20, "task": "Start thinking about nursery", "category": "preparation", "priority": "medium"},
                {"week": 24, "task": "Take glucose screening test", "category": "health", "priority": "high"},
                
                # Third trimester
                {"week": 28, "task": "Start childbirth classes", "category": "education", "priority": "high"},
                {"week": 32, "task": "Plan baby shower", "category": "preparation", "priority": "medium"},
                {"week": 35, "task": "Pack hospital bag", "category": "preparation", "priority": "high"},
                {"week": 36, "task": "Install car seat", "category": "preparation", "priority": "high"},
                {"week": 38, "task": "Final preparations for baby", "category": "preparation", "priority": "high"}
            ]
            
            created_items = []
            for item_data in default_items:
                item_data["pregnancy_id"] = pregnancy_id
                item = await self.create_checklist_item(session, item_data)
                if item:
                    created_items.append(item)
            
            return created_items
        except Exception as e:
            logger.error(f"Error creating default checklists: {e}")
            return []


# Global service instances
milestone_service = MilestoneService()
appointment_service = AppointmentService()
important_date_service = ImportantDateService()
weekly_checklist_service = WeeklyChecklistService()