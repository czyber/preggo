"""
Base service class for database operations using SQLModel sessions.

This module provides a base service class that all other services should inherit from.
It ensures proper session management and consistent error handling.
"""

from typing import Optional, List, Generic, TypeVar, Type, Any, Dict
from sqlmodel import Session, select, delete
from app.db.session import get_session
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

# Generic type for SQLModel models
ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Base service class for database operations using SQLModel sessions.
    
    All service classes should inherit from this to ensure:
    - Proper session management
    - Consistent error handling
    - Standard CRUD operations
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(self, session: Session, id: Any) -> Optional[ModelType]:
        """Get a record by ID."""
        try:
            statement = select(self.model).where(self.model.id == id)
            result = session.exec(statement).first()
            return result
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            return None
    
    async def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            statement = select(self.model).offset(skip).limit(limit)
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            return []
    
    async def create(self, session: Session, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_in)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            session.rollback()
            return None
    
    async def update(self, session: Session, db_obj: ModelType, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update an existing record."""
        try:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            session.rollback()
            return None
    
    async def delete(self, session: Session, id: Any) -> bool:
        """Delete a record by ID."""
        try:
            statement = delete(self.model).where(self.model.id == id)
            result = session.exec(statement)
            session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            session.rollback()
            return False
    
    async def exists(self, session: Session, id: Any) -> bool:
        """Check if a record exists by ID."""
        try:
            statement = select(self.model).where(self.model.id == id)
            result = session.exec(statement).first()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if {self.model.__name__} exists with ID {id}: {e}")
            return False


def get_session_dependency():
    """Dependency to get database session."""
    return Depends(get_session)